from __future__ import annotations

import aiosqlite
import pytest

from be.db.migrations import MigrationError, apply_sqlite_migrations


async def _table_columns(db: aiosqlite.Connection, table: str) -> set[str]:
    cursor = await db.execute(f'PRAGMA table_info("{table}")')
    return {row[1] for row in await cursor.fetchall()}


async def _fetchone(db: aiosqlite.Connection, query: str, parameters=()):
    cursor = await db.execute(query, parameters)
    return await cursor.fetchone()


@pytest.mark.asyncio
async def test_fresh_sqlite_database_reaches_current_schema(tmp_path):
    database_path = tmp_path / "fresh.db"
    async with aiosqlite.connect(database_path) as db:
        assert await apply_sqlite_migrations(db) == 2

        migrations = await db.execute_fetchall(
            "SELECT version, name FROM schema_migrations ORDER BY version"
        )
        assert migrations == [
            (1, "baseline_schema"),
            (2, "ownership_and_ai_jobs"),
        ]
        assert "owner_user_id" in await _table_columns(db, "candidates")
        assert "owner_user_id" in await _table_columns(db, "uploads")
        assert "owner_user_id" in await _table_columns(db, "analyses")
        assert "prompt_version" in await _table_columns(db, "ai_jobs")

        # A second startup must not rerun or duplicate migrations.
        assert await apply_sqlite_migrations(db) == 2
        count = await _fetchone(db, "SELECT COUNT(*) FROM schema_migrations")
        assert count[0] == 2


@pytest.mark.asyncio
async def test_legacy_sqlite_schema_is_upgraded_without_losing_rows(tmp_path):
    database_path = tmp_path / "legacy.db"
    candidate_id = "legacy-candidate"
    async with aiosqlite.connect(database_path) as db:
        await db.executescript(
            """
            CREATE TABLE candidates (
                id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                email TEXT,
                title TEXT,
                profile_json TEXT NOT NULL
            );
            CREATE TABLE uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id TEXT,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                checksum TEXT,
                raw_text TEXT
            );
            CREATE TABLE analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id TEXT NOT NULL,
                ats_score INTEGER NOT NULL,
                ats_grade TEXT NOT NULL,
                report_json TEXT NOT NULL
            );
            INSERT INTO candidates(id, full_name, profile_json)
            VALUES ('legacy-candidate', 'Legacy User', '{}');
            INSERT INTO uploads(candidate_id, filename, file_path)
            VALUES ('legacy-candidate', 'cv.pdf', 'legacy/cv.pdf');
            INSERT INTO analyses(candidate_id, ats_score, ats_grade, report_json)
            VALUES ('legacy-candidate', 80, 'B', '{}');
            """
        )
        await db.commit()

        assert await apply_sqlite_migrations(db) == 2
        candidate = await _fetchone(
            db,
            "SELECT full_name, owner_user_id FROM candidates WHERE id = ?",
            (candidate_id,),
        )
        upload = await _fetchone(
            db,
            "SELECT owner_user_id FROM uploads WHERE candidate_id = ?",
            (candidate_id,),
        )
        analysis = await _fetchone(
            db,
            "SELECT owner_user_id FROM analyses WHERE candidate_id = ?",
            (candidate_id,),
        )
        assert candidate == ("Legacy User", 0)
        assert upload == (0,)
        assert analysis == (0,)


@pytest.mark.asyncio
async def test_unknown_schema_version_is_rejected(tmp_path):
    database_path = tmp_path / "future.db"
    async with aiosqlite.connect(database_path) as db:
        await db.execute(
            "CREATE TABLE schema_migrations (version INTEGER PRIMARY KEY, name TEXT NOT NULL)"
        )
        await db.execute(
            "INSERT INTO schema_migrations(version, name) VALUES(99, 'future')"
        )
        await db.commit()

        with pytest.raises(MigrationError, match="newer than this application"):
            await apply_sqlite_migrations(db)
