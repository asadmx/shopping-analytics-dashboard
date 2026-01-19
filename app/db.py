import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Always load .env from the project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_PATH)


def get_engine():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError(
            f"DATABASE_URL is not set. Expected it in {ENV_PATH}."
        )

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    if db_url.startswith("postgresql://") and "+psycopg" not in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

    return create_engine(db_url, pool_pre_ping=True)


def run_sql(sql: str, params: dict | None = None):
    eng = get_engine()
    with eng.connect() as conn:
        result = conn.execute(text(sql), params or {})
        return result
