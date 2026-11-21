"""Run repeatable offline ranking checks against the versioned query fixture.

Usage: py backend/evaluate_recommendations.py
The output is a dated JSON artefact. It is a development/reproducibility check,
not evidence of user preference or publication-quality model performance.
"""
import json
import math
from datetime import datetime, timezone
from pathlib import Path

from app.database import Base, SessionLocal, engine
from app.services.recommendation_engine import get_recommendations
from app.services.seeder import seed_destinations

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "evaluation" / "queries.v1.json"
OUTPUT = ROOT / "evaluation" / "latest-results.json"


def reciprocal_rank(names, relevant):
    for rank, name in enumerate(names, start=1):
        if name in relevant:
            return 1 / rank
    return 0.0


def ndcg_at_k(names, relevant, k=10):
    gains = [1 if name in relevant else 0 for name in names[:k]]
    dcg = sum(gain / math.log2(index + 2) for index, gain in enumerate(gains))
    ideal = sum(1 / math.log2(index + 2) for index in range(min(k, len(relevant))))
    return dcg / ideal if ideal else 0.0


def main():
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_destinations(db)
        rows = []
        for item in fixture["queries"]:
            ranked = get_recommendations(db, query=item["query"], limit=10)
            names = [result["destination"].name for result in ranked]
            relevant = set(item["relevant"])
            rows.append({
                "id": item["id"],
                "query": item["query"],
                "ranking": names,
                "mrr": round(reciprocal_rank(names, relevant), 4),
                "ndcg_at_10": round(ndcg_at_k(names, relevant), 4),
            })
        artifact = {
            "fixture": fixture["dataset_version"],
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "method": "Current Wanderlust weighted ranker over a human-labelled fixture.",
            "limitations": "No held-out users, behavioural logs, statistical significance tests, or external baseline are included.",
            "results": rows,
            "mean_mrr": round(sum(row["mrr"] for row in rows) / len(rows), 4),
            "mean_ndcg_at_10": round(sum(row["ndcg_at_10"] for row in rows) / len(rows), 4),
        }
        OUTPUT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(artifact, indent=2))
    finally:
        db.close()


if __name__ == "__main__":
    main()
