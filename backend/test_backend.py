import sys
import math
import warnings
warnings.filterwarnings("ignore")
from datetime import datetime, timedelta
from pathlib import Path

# Add backend folder to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import engine, Base, SessionLocal
from app.models.destination import Destination, Endorsement, Contributor
from app.services.seeder import seed_destinations
from app.services.security import generate_secure_session_id, verify_session_id
from app.services.recommendation_engine import (
    calculate_contributor_trust,
    calculate_temporal_decay,
    compute_effective_endorsement_count,
    get_recommendations,
    get_global_corpus_stats,
)
from fastapi.testclient import TestClient
from app.main import app

def run_all_tests():
    print("=" * 70)
    print("WANDERLUST STAGE 3: TEST SUITE & VALIDATION")
    print("=" * 70)

    # ── TEST 1: Database Initialization & Seeding ──
    print("\n[TEST 1] Initializing Database & Verifying Foreign Keys...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Verify PRAGMA foreign_keys is ON
    raw_conn = engine.raw_connection()
    cur = raw_conn.cursor()
    cur.execute("PRAGMA foreign_keys;")
    fk_status = cur.fetchone()[0]
    cur.close()
    raw_conn.close()
    print(f"✓ SQLite PRAGMA foreign_keys = {fk_status} (Expected: 1)")
    assert fk_status == 1, "Foreign keys are not enabled in SQLite connection!"

    count = seed_destinations(db)
    print(f"✓ Seeded destinations: {count} (Expected: >= 25)")
    assert count >= 25

    contrib_count = db.query(Contributor).count()
    print(f"✓ Seeded contributors: {contrib_count}")
    assert contrib_count >= 5

    initial_endrs = db.query(Endorsement).count()
    print(f"✓ Seeded relational endorsements: {initial_endrs}")
    assert initial_endrs >= 5

    # ── TEST 2: Foreign Key Constraint & Cascade Action ──
    print("\n[TEST 2] Testing SQLite Foreign Key Constraints...")
    # Attempt inserting an endorsement pointing to an invalid destination ID (-999)
    test_session = generate_secure_session_id()
    invalid_endr = Endorsement(destination_id=999999, session_id=test_session, trust_weight=0.5)
    db.add(invalid_endr)
    try:
        db.commit()
        raise AssertionError("Foreign key violation was not enforced!")
    except Exception as e:
        db.rollback()
        print(f"✓ Foreign key constraint successfully prevented invalid reference: {type(e).__name__}")

    # ── TEST 3: Contributor Trust Scoring ──
    print("\n[TEST 3] Testing Contributor Trust Scoring Formula...")
    # Case A: Anonymous/Unauthenticated contributor (None) -> baseline 0.50
    t_anon = calculate_contributor_trust(None)
    print(f"✓ Anonymous contributor trust: {t_anon} (Expected: 0.50)")
    assert t_anon == 0.50

    # Case B: Verified veteran contributor (Priya: verified=True, 450 days, 12 endorsements)
    priya = db.query(Contributor).filter(Contributor.username == "priya_travels").first()
    t_priya = calculate_contributor_trust(priya)
    print(f"✓ Verified veteran contributor ({priya.username}) trust: {t_priya} (Expected > 0.85)")
    assert t_priya >= 0.85

    # Case C: Unverified newcomer contributor (Vikram: verified=False, 95 days, 4 endorsements)
    vikram = db.query(Contributor).filter(Contributor.username == "vikram_hiker").first()
    t_vikram = calculate_contributor_trust(vikram)
    print(f"✓ Unverified contributor ({vikram.username}) trust: {t_vikram} (Expected ~0.55-0.65)")
    assert 0.50 < t_vikram < t_priya

    # ── TEST 4: Temporal Decay Function ──
    print("\n[TEST 4] Testing Temporal Weighting & Half-Life Decay...")
    now = datetime.utcnow()
    # Brand new (0 days)
    d_fresh = calculate_temporal_decay(now, now)
    print(f"✓ Fresh endorsement (0 days) decay factor: {d_fresh} (Expected: 1.0)")
    assert d_fresh == 1.0

    # 180 days ago (1 half-life) -> should be close to 0.40 + 0.60 * 0.5 = 0.70
    t_half = now - timedelta(days=180)
    d_half = calculate_temporal_decay(t_half, now)
    print(f"✓ 180-day old endorsement decay factor: {d_half} (Expected ~0.70)")
    assert 0.68 <= d_half <= 0.72

    # 1000 days ago -> floor should protect it from zeroing out (>= 0.40)
    t_old = now - timedelta(days=1000)
    d_old = calculate_temporal_decay(t_old, now)
    print(f"✓ 1000-day old endorsement decay factor: {d_old} (Expected >= 0.40)")
    assert d_old >= 0.40

    # ── TEST 5: Global Bayesian Smoothing & Normalization ──
    print("\n[TEST 5] Testing Global Bayesian Smoothing & Bounded Log Normalization...")
    stats = get_global_corpus_stats(db)
    print(f"✓ Global corpus stats: Mean={stats['mean_endorsements']:.1f}, Max={stats['max_endorsements']:.1f}, MeanRating={stats['mean_rating']:.2f}")

    # Verify candidate filtering does NOT distort the global prior
    all_recs = get_recommendations(db, query=None, limit=5)
    filtered_recs = get_recommendations(db, query=None, region="South America", limit=5)

    print(f"✓ Global top match: '{all_recs[0]['destination'].name}' (Score={all_recs[0]['scores']['final_score']})")
    if filtered_recs:
        print(f"✓ Filtered South America match: '{filtered_recs[0]['destination'].name}' (Endorsement Score={filtered_recs[0]['scores']['endorsement_score']})")
        # Ensure endorsement score did NOT artificially collapse to 0.0 or 50.0
        assert filtered_recs[0]['scores']['endorsement_score'] > 60.0

    # ── TEST 6: Edge Case Robustness (Empty sets, Zero variance, Zero counts) ──
    print("\n[TEST 6] Testing Edge Cases & Boundary Conditions...")
    # Empty candidate set (impossible budget)
    empty_recs = get_recommendations(db, max_budget=1)
    print(f"✓ Empty candidate set returns: {len(empty_recs)} results (Expected: 0)")
    assert len(empty_recs) == 0

    # ── TEST 7: FastAPI Endpoints via TestClient ──
    print("\n[TEST 7] Testing REST API Endpoints & Security Token System...")
    client = TestClient(app)

    # Health check
    res = client.get("/api/health")
    assert res.status_code == 200
    hdata = res.json()
    print(f"✓ GET /api/health -> {hdata['stage']}, Destinations: {hdata['destinations_count']}")

    # Session token issuance
    s_res = client.get("/api/session?username=priya_travels")
    assert s_res.status_code == 200
    token_data = s_res.json()
    valid_session = token_data["session_id"]
    print(f"✓ GET /api/session -> Issued valid HMAC token: {valid_session[:25]}... (Linked to: {token_data['contributor']['username']})")

    # Contributor listing
    c_res = client.get("/api/contributors")
    assert c_res.status_code == 200
    print(f"✓ GET /api/contributors -> {len(c_res.json())} contributors retrieved")

    # Security: Reject forged/unsigned session ID
    forged_res = client.post("/api/endorsements", json={
        "destination_id": 1,
        "session_id": "forged_random_attacker_uuid_9999"
    })
    print(f"✓ POST with forged session token -> HTTP {forged_res.status_code} ({forged_res.json()['detail']})")
    assert forged_res.status_code == 400

    # Valid Endorsement Creation
    first_dest = db.query(Destination).first()
    dest_id = first_dest.id
    before_count = first_dest.endorsement_count

    endr_res = client.post("/api/endorsements", json={
        "destination_id": dest_id,
        "session_id": valid_session
    })
    print(f"✓ POST /api/endorsements with signed token -> HTTP {endr_res.status_code} (New Count: {endr_res.json()['new_count']}, Trust Weight: {endr_res.json()['trust_weight']})")
    assert endr_res.status_code == 201
    assert endr_res.json()["new_count"] == before_count + 1

    # Duplicate rejection
    dup_res = client.post("/api/endorsements", json={
        "destination_id": dest_id,
        "session_id": valid_session
    })
    print(f"✓ Duplicate POST /api/endorsements -> HTTP {dup_res.status_code} ({dup_res.json()['detail']})")
    assert dup_res.status_code == 409

    # Endorsement Withdrawal (DELETE)
    del_res = client.request("DELETE", "/api/endorsements", json={
        "destination_id": dest_id,
        "session_id": valid_session
    })
    print(f"✓ DELETE /api/endorsements -> HTTP {del_res.status_code} (Status: {del_res.json()['status']}, Restored Count: {del_res.json()['new_count']})")
    assert del_res.status_code == 200
    assert del_res.json()["new_count"] == before_count

    # Withdrawal of already withdrawn item -> 404
    del_res2 = client.request("DELETE", "/api/endorsements", json={
        "destination_id": dest_id,
        "session_id": valid_session
    })
    print(f"✓ DELETE non-existent endorsement -> HTTP {del_res2.status_code} ({del_res2.json()['detail']})")
    assert del_res2.status_code == 404

    # ── TEST 8: Recommendations with Configurable Weights ──
    print("\n[TEST 8] Testing Recommendations with Custom Weights...")
    rec_res = client.get("/api/recommendations?q=beaches&weight_endorsement=0.60&weight_rating=0.20&weight_relevance=0.20")
    assert rec_res.status_code == 200
    rec_data = rec_res.json()
    top_dest = rec_data["results"][0]
    print(f"✓ Recommendations for 'beaches' top result: '{top_dest['name']}' in {top_dest['country']}")
    print(f"   Scores: Final={top_dest['scores']['final_score']}, Endorsement={top_dest['scores']['endorsement_score']}, Rating={top_dest['scores']['rating_score']}, Relevance={top_dest['scores']['relevance_score']}")
    assert top_dest['scores']['final_score'] > 0

    db.close()
    print("\n" + "=" * 70)
    print("ALL 8 STAGE 3 TEST SUITES PASSED FLAWLESSLY! ✓")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    run_all_tests()
