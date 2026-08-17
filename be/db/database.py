"""Database setup — SQLite with aiosqlite for async operations."""

import aiosqlite
from pathlib import Path

DB_PATH = Path("./data/careerpilot.db")

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT,
    title TEXT,
    profile_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id INTEGER NOT NULL,
    ats_score INTEGER NOT NULL,
    ats_grade TEXT NOT NULL,
    report_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
);

CREATE TABLE IF NOT EXISTS uploads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id INTEGER,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    raw_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
);
"""


async def init_db():
    """Initialize database and create tables if they don't exist."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(str(DB_PATH)) as db:
        await db.executescript(CREATE_TABLES_SQL)
        await db.commit()


async def get_db() -> aiosqlite.Connection:
    """Get a database connection."""
    return await aiosqlite.connect(str(DB_PATH))


async def save_candidate(profile_json: str, full_name: str, email: str | None, title: str) -> int:
    """Save candidate profile and return the new ID."""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        cursor = await db.execute(
            "INSERT INTO candidates (full_name, email, title, profile_json) VALUES (?, ?, ?, ?)",
            (full_name, email, title, profile_json),
        )
        await db.commit()
        return cursor.lastrowid


async def save_analysis(candidate_id: int, ats_score: int, ats_grade: str, report_json: str) -> int:
    """Save analysis report and return the new ID."""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        cursor = await db.execute(
            "INSERT INTO analyses (candidate_id, ats_score, ats_grade, report_json) VALUES (?, ?, ?, ?)",
            (candidate_id, ats_score, ats_grade, report_json),
        )
        await db.commit()
        return cursor.lastrowid


async def save_upload(filename: str, file_path: str, raw_text: str, candidate_id: int | None = None) -> int:
    """Save upload record and return the new ID."""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        cursor = await db.execute(
            "INSERT INTO uploads (candidate_id, filename, file_path, raw_text) VALUES (?, ?, ?, ?)",
            (candidate_id, filename, file_path, raw_text),
        )
        await db.commit()
        return cursor.lastrowid


async def get_candidate(candidate_id: int) -> dict | None:
    """Get candidate by ID."""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_analysis(candidate_id: int) -> dict | None:
    """Get latest analysis for a candidate."""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM analyses WHERE candidate_id = ? ORDER BY created_at DESC LIMIT 1",
            (candidate_id,),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None
