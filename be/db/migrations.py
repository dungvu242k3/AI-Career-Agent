"""Versioned database migrations for CareerPilot AI.

The application must not silently change production schema as a side effect of
starting a web process.  This small runner keeps the current async PostgreSQL
and SQLite support while making schema changes explicit, ordered, transactional
and repeatable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable

import aiosqlite


class MigrationError(RuntimeError):
    """Raised when the database cannot be moved to the supported schema."""


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    postgres: Callable[[Any], Awaitable[None]]
    sqlite: Callable[[aiosqlite.Connection], Awaitable[None]]


SCHEMA_MIGRATIONS_SQL = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""

SCHEMA_MIGRATIONS_SQLITE = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""


async def _postgres_baseline(conn: Any) -> None:
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS candidates (
            id UUID PRIMARY KEY,
            full_name VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            title VARCHAR(255),
            profile_json JSONB NOT NULL,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS uploads (
            id SERIAL PRIMARY KEY,
            candidate_id UUID REFERENCES candidates(id) ON DELETE SET NULL,
            filename VARCHAR(255) NOT NULL,
            file_path TEXT NOT NULL,
            checksum VARCHAR(64),
            raw_text TEXT,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS analyses (
            id SERIAL PRIMARY KEY,
            candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
            ats_score INTEGER NOT NULL,
            ats_grade VARCHAR(10) NOT NULL,
            report_json JSONB NOT NULL,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    await conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_uploads_checksum ON uploads(checksum)"
    )
    await conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_candidates_email ON candidates(email)"
    )
    await conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_candidates_profile_gin ON candidates USING GIN (profile_json)"
    )
    await conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_analyses_report_gin ON analyses USING GIN (report_json)"
    )


async def _postgres_ownership_and_ai_jobs(conn: Any) -> None:
    for table in ("candidates", "uploads", "analyses"):
        await conn.execute(
            f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS owner_user_id BIGINT"
        )
        await conn.execute(
            f"UPDATE {table} SET owner_user_id = 0 WHERE owner_user_id IS NULL"
        )
        await conn.execute(
            f"ALTER TABLE {table} ALTER COLUMN owner_user_id SET NOT NULL"
        )

    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS ai_jobs (
            id UUID PRIMARY KEY,
            owner_user_id BIGINT NOT NULL,
            operation VARCHAR(40) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'queued',
            progress INTEGER NOT NULL DEFAULT 0,
            idempotency_key VARCHAR(128),
            payload_json JSONB NOT NULL,
            result_json JSONB,
            error_code VARCHAR(64),
            trace_id VARCHAR(64),
            model_version VARCHAR(128) NOT NULL DEFAULT 'routing-v1',
            prompt_version VARCHAR(64) NOT NULL DEFAULT 'grounded-v1',
            attempts INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # These clauses make the migration safe for an intermediate development
    # schema that created ai_jobs before the versioned runner existed.
    ai_job_columns = (
        ("owner_user_id", "BIGINT"),
        ("operation", "VARCHAR(40) NOT NULL DEFAULT 'unknown'"),
        ("status", "VARCHAR(20) NOT NULL DEFAULT 'queued'"),
        ("progress", "INTEGER NOT NULL DEFAULT 0"),
        ("idempotency_key", "VARCHAR(128)"),
        ("payload_json", "JSONB NOT NULL DEFAULT '{}'::jsonb"),
        ("result_json", "JSONB"),
        ("error_code", "VARCHAR(64)"),
        ("trace_id", "VARCHAR(64)"),
        ("model_version", "VARCHAR(128) NOT NULL DEFAULT 'routing-v1'"),
        ("prompt_version", "VARCHAR(64) NOT NULL DEFAULT 'grounded-v1'"),
        ("attempts", "INTEGER NOT NULL DEFAULT 0"),
        ("created_at", "TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP"),
        ("updated_at", "TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP"),
    )
    for column, definition in ai_job_columns:
        await conn.execute(
            f"ALTER TABLE ai_jobs ADD COLUMN IF NOT EXISTS {column} {definition}"
        )
    await conn.execute(
        "UPDATE ai_jobs SET owner_user_id = 0 WHERE owner_user_id IS NULL"
    )
    await conn.execute("ALTER TABLE ai_jobs ALTER COLUMN owner_user_id SET NOT NULL")

    await conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_uploads_owner_checksum ON uploads(owner_user_id, checksum)"
    )
    await conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_uploads_owner_path ON uploads(owner_user_id, file_path)"
    )
    await conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_candidates_owner ON candidates(owner_user_id)"
    )
    await conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_analyses_owner_candidate ON analyses(owner_user_id, candidate_id)"
    )
    await conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_ai_jobs_owner_created ON ai_jobs(owner_user_id, created_at DESC)"
    )
    await conn.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_ai_jobs_owner_operation_idempotency
        ON ai_jobs(owner_user_id, operation, idempotency_key)
        WHERE idempotency_key IS NOT NULL
        """
    )


async def _sqlite_columns(db: aiosqlite.Connection, table: str) -> set[str]:
    cursor = await db.execute(f'PRAGMA table_info("{table}")')
    return {row[1] for row in await cursor.fetchall()}


async def _sqlite_add_column_if_missing(
    db: aiosqlite.Connection,
    table: str,
    column: str,
    definition: str,
) -> None:
    if column not in await _sqlite_columns(db, table):
        await db.execute(f'ALTER TABLE "{table}" ADD COLUMN "{column}" {definition}')


async def _sqlite_baseline(db: aiosqlite.Connection) -> None:
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS candidates (
            id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT,
            title TEXT,
            profile_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id TEXT,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            checksum TEXT,
            raw_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE SET NULL
        )
        """
    )
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id TEXT NOT NULL,
            ats_score INTEGER NOT NULL,
            ats_grade TEXT NOT NULL,
            report_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
        )
        """
    )
    await db.execute(
        "CREATE INDEX IF NOT EXISTS idx_uploads_checksum ON uploads(checksum)"
    )
    await db.execute(
        "CREATE INDEX IF NOT EXISTS idx_candidates_email ON candidates(email)"
    )


async def _sqlite_ownership_and_ai_jobs(db: aiosqlite.Connection) -> None:
    for table in ("candidates", "uploads", "analyses"):
        await _sqlite_add_column_if_missing(
            db, table, "owner_user_id", "INTEGER NOT NULL DEFAULT 0"
        )
        await db.execute(
            f'UPDATE "{table}" SET owner_user_id = 0 WHERE owner_user_id IS NULL'
        )

    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS ai_jobs (
            id TEXT PRIMARY KEY,
            owner_user_id INTEGER NOT NULL,
            operation TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'queued',
            progress INTEGER NOT NULL DEFAULT 0,
            idempotency_key TEXT,
            payload_json TEXT NOT NULL,
            result_json TEXT,
            error_code TEXT,
            trace_id TEXT,
            model_version TEXT NOT NULL DEFAULT 'routing-v1',
            prompt_version TEXT NOT NULL DEFAULT 'grounded-v1',
            attempts INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    for column, definition in (
        ("owner_user_id", "INTEGER NOT NULL DEFAULT 0"),
        ("operation", "TEXT NOT NULL DEFAULT 'unknown'"),
        ("status", "TEXT NOT NULL DEFAULT 'queued'"),
        ("progress", "INTEGER NOT NULL DEFAULT 0"),
        ("idempotency_key", "TEXT"),
        ("payload_json", "TEXT NOT NULL DEFAULT '{}'"),
        ("result_json", "TEXT"),
        ("error_code", "TEXT"),
        ("trace_id", "TEXT"),
        ("model_version", "TEXT NOT NULL DEFAULT 'routing-v1'"),
        ("prompt_version", "TEXT NOT NULL DEFAULT 'grounded-v1'"),
        ("attempts", "INTEGER NOT NULL DEFAULT 0"),
        ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
        ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
    ):
        await _sqlite_add_column_if_missing(db, "ai_jobs", column, definition)
    await db.execute("UPDATE ai_jobs SET owner_user_id = 0 WHERE owner_user_id IS NULL")

    await db.execute(
        "CREATE INDEX IF NOT EXISTS idx_uploads_owner_checksum ON uploads(owner_user_id, checksum)"
    )
    await db.execute(
        "CREATE INDEX IF NOT EXISTS idx_uploads_owner_path ON uploads(owner_user_id, file_path)"
    )
    await db.execute(
        "CREATE INDEX IF NOT EXISTS idx_candidates_owner ON candidates(owner_user_id)"
    )
    await db.execute(
        "CREATE INDEX IF NOT EXISTS idx_analyses_owner_candidate ON analyses(owner_user_id, candidate_id)"
    )
    await db.execute(
        "CREATE INDEX IF NOT EXISTS idx_ai_jobs_owner_created ON ai_jobs(owner_user_id, created_at DESC)"
    )
    await db.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_ai_jobs_owner_operation_idempotency
        ON ai_jobs(owner_user_id, operation, idempotency_key)
        """
    )


MIGRATIONS = (
    Migration(1, "baseline_schema", _postgres_baseline, _sqlite_baseline),
    Migration(
        2,
        "ownership_and_ai_jobs",
        _postgres_ownership_and_ai_jobs,
        _sqlite_ownership_and_ai_jobs,
    ),
)
CURRENT_SCHEMA_VERSION = MIGRATIONS[-1].version


async def get_postgres_schema_version(conn: Any) -> int:
    """Read the schema version without creating or changing any database object."""
    exists = await conn.fetchval("SELECT to_regclass('public.schema_migrations')")
    if exists is None:
        return 0
    return int(
        await conn.fetchval("SELECT COALESCE(MAX(version), 0) FROM schema_migrations")
    )


async def get_sqlite_schema_version(db: aiosqlite.Connection) -> int:
    """Read the schema version without creating or changing any database object."""
    cursor = await db.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'schema_migrations'"
    )
    if await cursor.fetchone() is None:
        return 0
    cursor = await db.execute("SELECT COALESCE(MAX(version), 0) FROM schema_migrations")
    row = await cursor.fetchone()
    return int(row[0])


def validate_schema_version(version: int) -> None:
    """Reject an old or future schema before the application serves traffic."""
    if version > CURRENT_SCHEMA_VERSION:
        raise MigrationError(
            f"Database schema version {version} is newer than application version "
            f"{CURRENT_SCHEMA_VERSION}"
        )
    if version < CURRENT_SCHEMA_VERSION:
        raise MigrationError(
            f"Database schema version {version} is behind required version "
            f"{CURRENT_SCHEMA_VERSION}; run the migration command before startup"
        )


async def apply_postgres_migrations(conn: Any) -> int:
    """Apply all pending PostgreSQL migrations under a transaction lock."""
    async with conn.transaction():
        await conn.execute(
            "SELECT pg_advisory_xact_lock(hashtext('careerpilot:schema'))"
        )
        await conn.execute(SCHEMA_MIGRATIONS_SQL)
        rows = await conn.fetch(
            "SELECT version FROM schema_migrations ORDER BY version"
        )
        applied = {int(row["version"]) for row in rows}
        _validate_applied_versions(applied)
        for migration in MIGRATIONS:
            if migration.version in applied:
                continue
            await migration.postgres(conn)
            await conn.execute(
                "INSERT INTO schema_migrations(version, name) VALUES($1, $2)",
                migration.version,
                migration.name,
            )
            applied.add(migration.version)
    return max(applied, default=0)


async def apply_sqlite_migrations(db: aiosqlite.Connection) -> int:
    """Apply all pending SQLite migrations under an immediate transaction."""
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    await db.execute("BEGIN IMMEDIATE")
    try:
        await db.execute(SCHEMA_MIGRATIONS_SQLITE)
        cursor = await db.execute(
            "SELECT version FROM schema_migrations ORDER BY version"
        )
        applied = {int(row[0]) for row in await cursor.fetchall()}
        _validate_applied_versions(applied)
        for migration in MIGRATIONS:
            if migration.version in applied:
                continue
            await migration.sqlite(db)
            await db.execute(
                "INSERT INTO schema_migrations(version, name) VALUES(?, ?)",
                (migration.version, migration.name),
            )
            applied.add(migration.version)
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    return max(applied, default=0)


def _validate_applied_versions(applied: set[int]) -> None:
    unknown = applied - {migration.version for migration in MIGRATIONS}
    if unknown:
        raise MigrationError(
            "Database schema is newer than this application: "
            + ", ".join(str(version) for version in sorted(unknown))
        )
