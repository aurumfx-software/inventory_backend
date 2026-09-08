import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Ensure environment variables from backend/.env are loaded
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(env_path)

POSTGRES_USER = os.getenv("POSTGRES_USER", "")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "")
POSTGRES_DB = os.getenv("POSTGRES_DB", "")

# Read DATABASE_URL directly from .env or construct from .env environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

import time

# Engine setup with connection pool optimization for DigitalOcean Managed PostgreSQL
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=15,
    pool_recycle=60,
    pool_timeout=3
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency for obtaining a SQLAlchemy session in API routes."""
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

_db_online_cache = {"status": True, "time": 0}

def check_db_connection() -> bool:
    """Check if connection to PostgreSQL database is alive (cached for 10 seconds)."""
    now = time.time()
    if now - _db_online_cache["time"] < 10:
        return _db_online_cache["status"]

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        _db_online_cache["status"] = True
        _db_online_cache["time"] = now
        return True
    except Exception as e:
        _db_online_cache["status"] = False
        _db_online_cache["time"] = now
        print(f"[DB WARN] Could not connect to PostgreSQL ({POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}): {e}")
        return False

