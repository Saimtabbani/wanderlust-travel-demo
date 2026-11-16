from pathlib import Path
import os
import shutil
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database file stored in backend/wanderlust.db. Vercel functions have
# a read-only application bundle, so the demo copies the seeded database to
# the function's temporary directory for the lifetime of a warm instance.
BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_DB_PATH = BASE_DIR / "wanderlust.db"
if os.getenv("VERCEL"):
    runtime_db = Path("/tmp") / "wanderlust.db"
    if not runtime_db.exists() and SOURCE_DB_PATH.exists():
        shutil.copy2(SOURCE_DB_PATH, runtime_db)
    DB_PATH = runtime_db
else:
    DB_PATH = SOURCE_DB_PATH
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite in multi-threaded FastAPI
    echo=False
)

# ── SQLite Foreign Key Enforcement ──
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Ensure SQLite enforces foreign key constraints and cascade actions on every connection.
    By default, SQLite disables foreign keys.
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency that provides a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

