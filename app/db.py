import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# ------------------------------------------------------
# Load .env from project root (works locally + on Render)
# ------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_PATH)


def get_engine():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError(
            f"DATABASE_URL is not set. Expected it in {ENV_PATH}."
        )

    # Normalize old postgres:// URLs
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    # Force psycopg v3 driver
    if db_url.startswith("postgresql://") and "+psycopg" not in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

    # Supabase requires SSL
    if "sslmode=" not in db_url:
        join_char = "&" if "?" in db_url else "?"
        db_url = db_url + f"{join_char}sslmode=require"

    return create_engine(
        db_url,
        pool_pre_ping=True,
        pool_size=3,
        max_overflow=2,
        pool_recycle=300,
        connect_args={"connect_timeout": 10},
    )


def run_sql(sql: str, params: dict | None = None):
    eng = get_engine()
    with eng.connect() as conn:
        result = conn.execute(text(sql), params or {})
        return result
