"""Database setup — Async SQLite with aiosqlite for candidate profiles, uploads, and analyses."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
import aiosqlite

from be.config import get_settings

CREATE_TABLES_SQL = """
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


@asynccontextmanager
async def get_db_connection() -> AsyncGenerator[aiosqlite.Connection, None]:
    """Context manager for SQLite connections with WAL mode and foreign keys enabled."""
    db_path = get_settings().db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(str(db_path)) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        yield db


async def init_db() -> None:
    """Initialize database schema, tables, and indexes."""
    async with get_db_connection() as db:
        await db.executescript(CREATE_TABLES_SQL)
        await db.commit()


async def save_candidate(profile_json: str, full_name: str, email: str | None, title: str) -> int:
    """Save candidate profile and return the new ID."""
    async with get_db_connection() as db:
        cursor = await db.execute(
            "INSERT INTO candidates (full_name, email, title, profile_json) VALUES (?, ?, ?, ?)",
            (full_name, email, title, profile_json),
        )
        await db.commit()
        return int(cursor.lastrowid)


async def update_candidate(candidate_id: int, profile_json: str, full_name: str, email: str | None, title: str) -> bool:
    """Update candidate profile if edited by user on Preview Card."""
    async with get_db_connection() as db:
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


async def get_candidate(candidate_id: int) -> dict | None:
    """Get candidate record by ID."""
    async with get_db_connection() as db:
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
    async with get_db_connection() as db:
        cursor = await db.execute(
            "INSERT INTO uploads (candidate_id, filename, file_path, checksum, raw_text) VALUES (?, ?, ?, ?, ?)",
            (candidate_id, filename, file_path, checksum, raw_text),
        )
        await db.commit()
        return int(cursor.lastrowid)


async def get_upload_by_checksum(checksum: str) -> dict | None:
    """Find existing upload by SHA256 checksum to avoid redundant extraction."""
    async with get_db_connection() as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM uploads WHERE checksum = ? ORDER BY created_at DESC LIMIT 1",
            (checksum,),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def save_analysis(candidate_id: int, ats_score: int, ats_grade: str, report_json: str) -> int:
    """Save analysis report."""
    async with get_db_connection() as db:
        cursor = await db.execute(
            "INSERT INTO analyses (candidate_id, ats_score, ats_grade, report_json) VALUES (?, ?, ?, ?)",
            (candidate_id, ats_score, ats_grade, report_json),
        )
        await db.commit()
        return int(cursor.lastrowid)


async def get_analysis(candidate_id: int) -> dict | None:
    """Get latest analysis report for a candidate."""
    async with get_db_connection() as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM analyses WHERE candidate_id = ? ORDER BY created_at DESC LIMIT 1",
            (candidate_id,),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None
