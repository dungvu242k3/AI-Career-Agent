"""Database setup — High-performance Async PostgreSQL (asyncpg) with Native JSONB and SQLite fallback."""

import json
import logging
from typing import Any
import aiosqlite
import asyncpg

from be.config import get_settings

logger = logging.getLogger(__name__)

# Global connection pool for PostgreSQL
_pg_pool: asyncpg.Pool | None = None

# --- PostgreSQL DDL with Native JSONB and GIN Indexing ---
PG_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS candidates (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    title VARCHAR(255),
    profile_json JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS uploads (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidates(id) ON DELETE SET NULL,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    checksum VARCHAR(64),
    raw_text TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analyses (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    ats_score INTEGER NOT NULL,
    ats_grade VARCHAR(10) NOT NULL,
    report_json JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_uploads_checksum ON uploads(checksum);
CREATE INDEX IF NOT EXISTS idx_candidates_email ON candidates(email);
CREATE INDEX IF NOT EXISTS idx_candidates_profile_gin ON candidates USING GIN (profile_json);
CREATE INDEX IF NOT EXISTS idx_analyses_report_gin ON analyses USING GIN (report_json);
"""

# --- SQLite Fallback DDL ---
SQLITE_TABLES_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT,
    title TEXT,
    profile_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS uploads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id INTEGER,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    checksum TEXT,
    raw_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id INTEGER NOT NULL,
    ats_score INTEGER NOT NULL,
    ats_grade TEXT NOT NULL,
    report_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_uploads_checksum ON uploads(checksum);
CREATE INDEX IF NOT EXISTS idx_candidates_email ON candidates(email);
"""


def is_postgres() -> bool:
    """Check if configured DATABASE_URL is PostgreSQL."""
    db_url = get_settings().database_url.lower()
    return db_url.startswith("postgres") or db_url.startswith("postgresql")


def _get_clean_pg_url(db_url: str) -> str:
    """Normalize SQLAlchemy-style postgresql+asyncpg:// to asyncpg standard postgresql://."""
    if "+asyncpg" in db_url:
        return db_url.replace("+asyncpg", "")
    return db_url


async def init_db() -> None:
    """Initialize database tables and indexes."""
    settings = get_settings()

    if is_postgres():
        global _pg_pool
        clean_url = _get_clean_pg_url(settings.database_url)
        try:
            _pg_pool = await asyncpg.create_pool(clean_url, min_size=2, max_size=10)
            async with _pg_pool.acquire() as conn:
                await conn.execute(PG_TABLES_SQL)
            logger.info("Connected to PostgreSQL successfully.")
            return
        except Exception as e:
            logger.warning(
                "Could not connect to PostgreSQL (%s). Falling back to local SQLite.", e
            )

    # SQLite fallback
    db_path = settings.db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(str(db_path)) as db:
        await db.executescript(SQLITE_TABLES_SQL)
        await db.commit()
    logger.info("Using SQLite database at %s", db_path)


async def close_db() -> None:
    """Close active database connection pool."""
    global _pg_pool
    if _pg_pool is not None:
        await _pg_pool.close()
        _pg_pool = None


async def save_candidate(profile_json: str, full_name: str, email: str | None, title: str) -> int:
    """Save candidate profile and return new ID."""
    global _pg_pool
    if _pg_pool is not None:
        async with _pg_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO candidates (full_name, email, title, profile_json) 
                VALUES ($1, $2, $3, $4::jsonb) 
                RETURNING id
                """,
                full_name,
                email,
                title,
                profile_json,
            )
            return int(row["id"])

    # SQLite fallback
    settings = get_settings()
    async with aiosqlite.connect(str(settings.db_path)) as db:
        cursor = await db.execute(
            "INSERT INTO candidates (full_name, email, title, profile_json) VALUES (?, ?, ?, ?)",
            (full_name, email, title, profile_json),
        )
        await db.commit()
        return int(cursor.lastrowid)


async def update_candidate(candidate_id: int, profile_json: str, full_name: str, email: str | None, title: str) -> bool:
    """Update candidate profile."""
    global _pg_pool
    if _pg_pool is not None:
        async with _pg_pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE candidates 
                SET profile_json = $1::jsonb, full_name = $2, email = $3, title = $4, updated_at = CURRENT_TIMESTAMP
                WHERE id = $5
                """,
                profile_json,
                full_name,
                email,
                title,
                candidate_id,
            )
            return result.endswith("1")

    # SQLite fallback
    settings = get_settings()
    async with aiosqlite.connect(str(settings.db_path)) as db:
        cursor = await db.execute(
            """
            UPDATE candidates 
            SET profile_json = ?, full_name = ?, email = ?, title = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (profile_json, full_name, email, title, candidate_id),
        )
        await db.commit()
        return cursor.rowcount > 0


async def get_candidate(candidate_id: int) -> dict[str, Any] | None:
    """Get candidate record by ID."""
    global _pg_pool
    if _pg_pool is not None:
        async with _pg_pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM candidates WHERE id = $1", candidate_id)
            if not row:
                return None
            record = dict(row)
            if isinstance(record.get("profile_json"), dict):
                record["profile_json"] = json.dumps(record["profile_json"])
            return record

    # SQLite fallback
    settings = get_settings()
    async with aiosqlite.connect(str(settings.db_path)) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def save_upload(
    filename: str,
    file_path: str,
    raw_text: str,
    checksum: str | None = None,
    candidate_id: int | None = None,
) -> int:
    """Save upload record with checksum."""
    global _pg_pool
    if _pg_pool is not None:
        async with _pg_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO uploads (candidate_id, filename, file_path, checksum, raw_text) 
                VALUES ($1, $2, $3, $4, $5) 
                RETURNING id
                """,
                candidate_id,
                filename,
                file_path,
                checksum,
                raw_text,
            )
            return int(row["id"])

    # SQLite fallback
    settings = get_settings()
    async with aiosqlite.connect(str(settings.db_path)) as db:
        cursor = await db.execute(
            "INSERT INTO uploads (candidate_id, filename, file_path, checksum, raw_text) VALUES (?, ?, ?, ?, ?)",
            (candidate_id, filename, file_path, checksum, raw_text),
        )
        await db.commit()
        return int(cursor.lastrowid)


async def get_upload_by_checksum(checksum: str) -> dict[str, Any] | None:
    """Find existing upload by SHA256 checksum."""
    global _pg_pool
    if _pg_pool is not None:
        async with _pg_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM uploads WHERE checksum = $1 ORDER BY created_at DESC LIMIT 1",
                checksum,
            )
            return dict(row) if row else None

    # SQLite fallback
    settings = get_settings()
    async with aiosqlite.connect(str(settings.db_path)) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM uploads WHERE checksum = ? ORDER BY created_at DESC LIMIT 1",
            (checksum,),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def save_analysis(candidate_id: int, ats_score: int, ats_grade: str, report_json: str) -> int:
    """Save analysis report."""
    global _pg_pool
    if _pg_pool is not None:
        async with _pg_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO analyses (candidate_id, ats_score, ats_grade, report_json) 
                VALUES ($1, $2, $3, $4::jsonb) 
                RETURNING id
                """,
                candidate_id,
                ats_score,
                ats_grade,
                report_json,
            )
            return int(row["id"])

    # SQLite fallback
    settings = get_settings()
    async with aiosqlite.connect(str(settings.db_path)) as db:
        cursor = await db.execute(
            "INSERT INTO analyses (candidate_id, ats_score, ats_grade, report_json) VALUES (?, ?, ?, ?)",
            (candidate_id, ats_score, ats_grade, report_json),
        )
        await db.commit()
        return int(cursor.lastrowid)


async def get_analysis(candidate_id: int) -> dict[str, Any] | None:
    """Get latest analysis report for a candidate."""
    global _pg_pool
    if _pg_pool is not None:
        async with _pg_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM analyses WHERE candidate_id = $1 ORDER BY created_at DESC LIMIT 1",
                candidate_id,
            )
            if not row:
                return None
            record = dict(row)
            if isinstance(record.get("report_json"), dict):
                record["report_json"] = json.dumps(record["report_json"])
            return record

    # SQLite fallback
    settings = get_settings()
    async with aiosqlite.connect(str(settings.db_path)) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM analyses WHERE candidate_id = ? ORDER BY created_at DESC LIMIT 1",
            (candidate_id,),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None
