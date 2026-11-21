from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import engine, Base, get_db, SessionLocal, migrate_sqlite_destination_metadata
from .models.destination import Destination, Contributor, Endorsement
from .services.seeder import seed_destinations
from .routes.destinations import router as destinations_router
from .routes.endorsements import router as endorsements_router
from .routes.recommendations import router as recommendations_router
from .routes.auth import router as auth_router
from .routes.catalog_admin import router as catalog_admin_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup: Create SQLite tables and seed initial destinations & contributors ──
    Base.metadata.create_all(bind=engine)
    migrate_sqlite_destination_metadata()
    db = SessionLocal()
    try:
        count = seed_destinations(db)
        contrib_count = db.query(Contributor).count()
        endr_count = db.query(Endorsement).count()
        print(f"[Wanderlust Stage 3] Database initialized: {count} destinations, {contrib_count} contributors, {endr_count} relational endorsements.")
    finally:
        db.close()
    yield
    # ── Shutdown ──

app = FastAPI(
    title="Wanderlust Trust-Aware API",
    description="Stage 3: Trust-Aware, Endorsement-Based Recommendation Engine for Wanderlust",
    version="3.0.0",
    lifespan=lifespan,
)

# ── CORS configuration for React frontend ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ── Include API routes ──
app.include_router(destinations_router, prefix="/api")
app.include_router(endorsements_router, prefix="/api")
app.include_router(recommendations_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(catalog_admin_router, prefix="/api")

@app.get("/api/health", tags=["system"])
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint returning system status, destination count, and trust statistics.
    """
    dest_count = db.query(Destination).count()
    contrib_count = db.query(Contributor).count()
    endr_count = db.query(Endorsement).count()
    return {
        "status": "ok",
        "stage": "Stage 3 — Trust-Aware Recommendation Engine",
        "destinations_count": dest_count,
        "contributors_count": contrib_count,
        "relational_endorsements_count": endr_count,
        "security_mode": "HMAC-SHA256 signed session identity",
        "note": "Ratings and baseline endorsements are demonstration data; dynamic endorsements are trust-weighted."
    }
