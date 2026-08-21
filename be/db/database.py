"""Database setup — High-performance Async PostgreSQL (asyncpg) with Native JSONB and SQLite fallback."""

import json
import logging
from typing import Any
import aiosqlite
import asyncpg
import uuid6

from be.config import get_settings
from be.db.migrations import (
    apply_postgres_migrations,
    apply_sqlite_migrations,
    get_postgres_schema_version,
    get_sqlite_schema_version,
    validate_schema_version,
)

logger = logging.getLogger(__name__)

# Global connection pool for PostgreSQL
_pg_pool: asyncpg.Pool | None = None

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
        except Exception as e:
            logger.warning(
                "Could not connect to PostgreSQL: %s", e
            )
            if settings.is_production:
                raise RuntimeError("PostgreSQL is unavailable; refusing SQLite fallback in production") from e
        else:
            try:
                async with _pg_pool.acquire() as conn:
                    if settings.is_production:
                        version = await get_postgres_schema_version(conn)
                        validate_schema_version(version)
                    else:
                        version = await apply_postgres_migrations(conn)
                logger.info("Connected to PostgreSQL successfully; schema_version=%s", version)
                return
            except Exception:
                await close_db()
                raise

    # SQLite fallback
    db_path = settings.db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(str(db_path)) as db:
        if settings.is_production:
            version = await get_sqlite_schema_version(db)
            validate_schema_version(version)
        else:
            version = await apply_sqlite_migrations(db)
    logger.info("Using SQLite database at %s; schema_version=%s", db_path, version)


async def close_db() -> None:
    """Close active database connection pool."""
    global _pg_pool
    if _pg_pool is not None:
        await _pg_pool.close()
        _pg_pool = None


async def check_database_ready() -> bool:
    """Return whether the configured database accepts a trivial read query."""
    try:
        if _pg_pool is not None:
            async with _pg_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True

        settings = get_settings()
        async with aiosqlite.connect(str(settings.db_path)) as db:
            cursor = await db.execute("SELECT 1")
            await cursor.fetchone()
        return True
    except Exception:
        logger.warning("Database readiness check failed")
        return False


async def save_candidate(
    profile_json: str,
    full_name: str,
    email: str | None,
    title: str,
    owner_user_id: int,
    candidate_id: str | None = None,
) -> str:
    """Save candidate profile with time-ordered UUIDv7 and return ID string."""
    cid = candidate_id or str(uuid6.uuid7())
    global _pg_pool
    if _pg_pool is not None:
        async with _pg_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO candidates (id, owner_user_id, full_name, email, title, profile_json)
                VALUES ($1::uuid, $2, $3, $4, $5, $6::jsonb)
                RETURNING id
                """,
                cid, owner_user_id, full_name, email, title, profile_json,
            )
            return str(row["id"])

    # SQLite fallback
    settings = get_settings()
    async with aiosqlite.connect(str(settings.db_path)) as db:
        await db.execute(
            "INSERT INTO candidates (id, owner_user_id, full_name, email, title, profile_json) VALUES (?, ?, ?, ?, ?, ?)",
            (cid, owner_user_id, full_name, email, title, profile_json),
        )
        await db.commit()
        return cid


async def update_candidate(
    candidate_id: str,
    profile_json: str,
    full_name: str,
    email: str | None,
    title: str,
    owner_user_id: int,
) -> bool:
    """Update candidate profile."""
    global _pg_pool
    if _pg_pool is not None:
        async with _pg_pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE candidates 
                SET profile_json = $1::jsonb, full_name = $2, email = $3, title = $4, updated_at = CURRENT_TIMESTAMP
                WHERE id = $5::uuid AND owner_user_id = $6
                """,
                profile_json,
                full_name,
                email,
                title,
                candidate_id, owner_user_id,
            )
            return result.endswith("1")

    # SQLite fallback
    settings = get_settings()
    async with aiosqlite.connect(str(settings.db_path)) as db:
        cursor = await db.execute(
            """
            UPDATE candidates 
            SET profile_json = ?, full_name = ?, email = ?, title = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND owner_user_id = ?
            """,
            (profile_json, full_name, email, title, str(candidate_id), owner_user_id),
        )
        await db.commit()
        return cursor.rowcount > 0


async def get_candidate(candidate_id: str, owner_user_id: int) -> dict[str, Any] | None:
    """Get candidate record by UUIDv7 string ID."""
    global _pg_pool
    if _pg_pool is not None:
        async with _pg_pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM candidates WHERE id = $1::uuid AND owner_user_id = $2", candidate_id, owner_user_id)
            if not row:
                return None
            record = dict(row)
            if isinstance(record.get("profile_json"), dict):
                record["profile_json"] = json.dumps(record["profile_json"])
            if record.get("id"):
                record["id"] = str(record["id"])
            return record

    # SQLite fallback
    settings = get_settings()
    async with aiosqlite.connect(str(settings.db_path)) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM candidates WHERE id = ? AND owner_user_id = ?", (str(candidate_id), owner_user_id))
        row = await cursor.fetchone()
        if not row:
            return None
        rec = dict(row)
        if rec.get("id"):
            rec["id"] = str(rec["id"])
        return rec


async def save_upload(
    filename: str,
    file_path: str,
    raw_text: str,
    owner_user_id: int,
    checksum: str | None = None,
    candidate_id: str | None = None,
) -> int:
    """Save upload record with checksum."""
    global _pg_pool
    if _pg_pool is not None:
        async with _pg_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO uploads (candidate_id, owner_user_id, filename, file_path, checksum, raw_text)
                VALUES ($1::uuid, $2, $3, $4, $5, $6)
                RETURNING id
                """,
                candidate_id, owner_user_id, filename, file_path, checksum, raw_text,
            )
            return int(row["id"])

    # SQLite fallback
    settings = get_settings()
    async with aiosqlite.connect(str(settings.db_path)) as db:
        cursor = await db.execute(
            "INSERT INTO uploads (candidate_id, owner_user_id, filename, file_path, checksum, raw_text) VALUES (?, ?, ?, ?, ?, ?)",
            (str(candidate_id) if candidate_id else None, owner_user_id, filename, file_path, checksum, raw_text),
        )
        await db.commit()
        return int(cursor.lastrowid)


async def save_candidate_and_upload_idempotently(
    *,
    profile_json: str,
    full_name: str,
    email: str | None,
    title: str,
    owner_user_id: int,
    filename: str,
    file_path: str,
    raw_text: str,
    checksum: str,
) -> tuple[str, bool]:
    """Atomically create a candidate/upload pair or return the existing pair.

    The advisory lock is per owner and content hash, so retries and concurrent
    uploads cannot create two candidate records for the same user document.
    """
    candidate_id = str(uuid6.uuid7())
    global _pg_pool
    if _pg_pool is not None:
        async with _pg_pool.acquire() as conn:
            async with conn.transaction():
                lock_key = f"candidate-upload:{owner_user_id}:{checksum}"
                await conn.execute("SELECT pg_advisory_xact_lock(hashtextextended($1, 0))", lock_key)
                existing = await conn.fetchrow(
                    "SELECT candidate_id FROM uploads WHERE owner_user_id = $1 AND checksum = $2 ORDER BY id DESC LIMIT 1",
                    owner_user_id,
                    checksum,
                )
                if existing and existing["candidate_id"]:
                    return str(existing["candidate_id"]), True
                await conn.execute(
                    """INSERT INTO candidates (id, owner_user_id, full_name, email, title, profile_json)
                       VALUES ($1::uuid, $2, $3, $4, $5, $6::jsonb)""",
                    candidate_id, owner_user_id, full_name, email, title, profile_json,
                )
                await conn.execute(
                    """INSERT INTO uploads (candidate_id, owner_user_id, filename, file_path, checksum, raw_text)
                       VALUES ($1::uuid, $2, $3, $4, $5, $6)""",
                    candidate_id, owner_user_id, filename, file_path, checksum, raw_text,
                )
                return candidate_id, False

    settings = get_settings()
    async with aiosqlite.connect(str(settings.db_path)) as db:
        await db.execute("BEGIN IMMEDIATE")
        existing = await db.execute(
            "SELECT candidate_id FROM uploads WHERE owner_user_id = ? AND checksum = ? ORDER BY id DESC LIMIT 1",
            (owner_user_id, checksum),
        )
        row = await existing.fetchone()
        if row and row[0]:
            await db.commit()
            return str(row[0]), True
        await db.execute(
            "INSERT INTO candidates (id, owner_user_id, full_name, email, title, profile_json) VALUES (?, ?, ?, ?, ?, ?)",
            (candidate_id, owner_user_id, full_name, email, title, profile_json),
        )
        await db.execute(
            "INSERT INTO uploads (candidate_id, owner_user_id, filename, file_path, checksum, raw_text) VALUES (?, ?, ?, ?, ?, ?)",
            (candidate_id, owner_user_id, filename, file_path, checksum, raw_text),
        )
        await db.commit()
        return candidate_id, False


async def get_upload_by_checksum(checksum: str, owner_user_id: int) -> dict[str, Any] | None:
    """Find existing upload by SHA256 checksum."""
    global _pg_pool
    if _pg_pool is not None:
        async with _pg_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM uploads WHERE checksum = $1 AND owner_user_id = $2 ORDER BY created_at DESC LIMIT 1",
                checksum, owner_user_id,
            )
            if not row:
                return None
            rec = dict(row)
            if rec.get("candidate_id"):
                rec["candidate_id"] = str(rec["candidate_id"])
            return rec

    # SQLite fallback
    settings = get_settings()
    async with aiosqlite.connect(str(settings.db_path)) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM uploads WHERE checksum = ? AND owner_user_id = ? ORDER BY created_at DESC LIMIT 1",
            (checksum, owner_user_id),
        )
        row = await cursor.fetchone()
        if not row:
            return None
        rec = dict(row)
        if rec.get("candidate_id"):
            rec["candidate_id"] = str(rec["candidate_id"])
        return rec


async def save_analysis(candidate_id: str, ats_score: int, ats_grade: str, report_json: str, owner_user_id: int) -> int:
    """Save analysis report."""
    global _pg_pool
    if _pg_pool is not None:
        async with _pg_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO analyses (candidate_id, owner_user_id, ats_score, ats_grade, report_json)
                VALUES ($1::uuid, $2, $3, $4, $5::jsonb)
                RETURNING id
                """,
                candidate_id, owner_user_id, ats_score, ats_grade, report_json,
            )
            return int(row["id"])

    # SQLite fallback
    settings = get_settings()
    async with aiosqlite.connect(str(settings.db_path)) as db:
        cursor = await db.execute(
            "INSERT INTO analyses (candidate_id, owner_user_id, ats_score, ats_grade, report_json) VALUES (?, ?, ?, ?, ?)",
            (str(candidate_id), owner_user_id, ats_score, ats_grade, report_json),
        )
        await db.commit()
        return int(cursor.lastrowid)


async def get_analysis(candidate_id: str, owner_user_id: int) -> dict[str, Any] | None:
    """Get latest analysis report for a candidate."""
    global _pg_pool
    if _pg_pool is not None:
        async with _pg_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM analyses WHERE candidate_id = $1::uuid AND owner_user_id = $2 ORDER BY created_at DESC LIMIT 1",
                candidate_id, owner_user_id,
            )
            if not row:
                return None
            record = dict(row)
            if isinstance(record.get("report_json"), dict):
                record["report_json"] = json.dumps(record["report_json"])
            if record.get("candidate_id"):
                record["candidate_id"] = str(record["candidate_id"])
            return record

    # SQLite fallback
    settings = get_settings()
    async with aiosqlite.connect(str(settings.db_path)) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM analyses WHERE candidate_id = ? AND owner_user_id = ? ORDER BY created_at DESC LIMIT 1",
            (str(candidate_id), owner_user_id),
        )
        row = await cursor.fetchone()
        if not row:
            return None
        rec = dict(row)
        if rec.get("candidate_id"):
            rec["candidate_id"] = str(rec["candidate_id"])
        return rec


async def get_candidate_analyses(candidate_id: str, owner_user_id: int, limit: int = 20) -> list[dict[str, Any]]:
    """Get all past analyses for a candidate."""
    global _pg_pool
    if _pg_pool is not None:
        async with _pg_pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM analyses WHERE candidate_id = $1::uuid AND owner_user_id = $2 ORDER BY created_at DESC LIMIT $3",
                candidate_id, owner_user_id, limit,
            )
            records = []
            for r in rows:
                rec = dict(r)
                if isinstance(rec.get("report_json"), dict):
                    rec["report_json"] = json.dumps(rec["report_json"])
                if rec.get("created_at"):
                    rec["created_at"] = str(rec["created_at"])
                if rec.get("candidate_id"):
                    rec["candidate_id"] = str(rec["candidate_id"])
                records.append(rec)
            return records

    # SQLite fallback
    settings = get_settings()
    async with aiosqlite.connect(str(settings.db_path)) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM analyses WHERE candidate_id = ? AND owner_user_id = ? ORDER BY created_at DESC LIMIT ?",
            (str(candidate_id), owner_user_id, limit),
        )
        rows = await cursor.fetchall()
        records = []
        for r in rows:
            rec = dict(r)
            if rec.get("created_at"):
                rec["created_at"] = str(rec["created_at"])
            if rec.get("candidate_id"):
                rec["candidate_id"] = str(rec["candidate_id"])
            records.append(rec)
        return records


def _normalize_ai_job(record: Any) -> dict[str, Any]:
    """Normalize JSON/UUID/timestamp differences between PostgreSQL and SQLite."""
    job = dict(record)
    job["id"] = str(job["id"])
    for key in ("payload_json", "result_json"):
        if isinstance(job.get(key), str):
            job[key] = json.loads(job[key])
    for key in ("created_at", "updated_at"):
        if job.get(key) is not None:
            job[key] = str(job[key])
    return job


async def create_ai_job(
    *,
    owner_user_id: int,
    operation: str,
    payload: dict[str, Any],
    idempotency_key: str | None = None,
    model_version: str = "routing-v1",
    prompt_version: str = "grounded-v1",
) -> tuple[dict[str, Any], bool]:
    """Create a queued AI job once, or return the owner's idempotent job."""
    job_id = str(uuid6.uuid7())
    payload_json = json.dumps(payload, ensure_ascii=False)
    global _pg_pool
    if _pg_pool is not None:
        async with _pg_pool.acquire() as conn:
            async with conn.transaction():
                if idempotency_key:
                    existing = await conn.fetchrow(
                        """SELECT * FROM ai_jobs WHERE owner_user_id = $1 AND operation = $2
                           AND idempotency_key = $3 ORDER BY created_at DESC LIMIT 1""",
                        owner_user_id, operation, idempotency_key,
                    )
                    if existing:
                        return _normalize_ai_job(existing), True
                row = await conn.fetchrow(
                    """INSERT INTO ai_jobs (id, owner_user_id, operation, idempotency_key, payload_json, model_version, prompt_version)
                       VALUES ($1::uuid, $2, $3, $4, $5::jsonb, $6, $7)
                       ON CONFLICT DO NOTHING
                       RETURNING *""",
                    job_id, owner_user_id, operation, idempotency_key, payload_json, model_version, prompt_version,
                )
                if row:
                    return _normalize_ai_job(row), False
                # A concurrent request inserted the same idempotency key
                # after the initial read. Return its durable job instead of
                # surfacing a unique-index exception to the client.
                existing = await conn.fetchrow(
                    """SELECT * FROM ai_jobs WHERE owner_user_id = $1 AND operation = $2
                       AND idempotency_key = $3 ORDER BY created_at DESC LIMIT 1""",
                    owner_user_id, operation, idempotency_key,
                )
                if existing:
                    return _normalize_ai_job(existing), True
                raise RuntimeError("AI job insertion was not persisted")

    settings = get_settings()
    async with aiosqlite.connect(str(settings.db_path)) as db:
        db.row_factory = aiosqlite.Row
        await db.execute("BEGIN IMMEDIATE")
        if idempotency_key:
            cursor = await db.execute(
                """SELECT * FROM ai_jobs WHERE owner_user_id = ? AND operation = ?
                   AND idempotency_key = ? ORDER BY created_at DESC LIMIT 1""",
                (owner_user_id, operation, idempotency_key),
            )
            existing = await cursor.fetchone()
            if existing:
                await db.commit()
                return _normalize_ai_job(existing), True
        await db.execute(
            """INSERT INTO ai_jobs (id, owner_user_id, operation, idempotency_key, payload_json, model_version, prompt_version)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (job_id, owner_user_id, operation, idempotency_key, payload_json, model_version, prompt_version),
        )
        cursor = await db.execute("SELECT * FROM ai_jobs WHERE id = ?", (job_id,))
        row = await cursor.fetchone()
        await db.commit()
        return _normalize_ai_job(row), False


async def get_ai_job(job_id: str, owner_user_id: int | None = None) -> dict[str, Any] | None:
    """Fetch a job, optionally scoped to the authenticated owner."""
    global _pg_pool
    if _pg_pool is not None:
        async with _pg_pool.acquire() as conn:
            if owner_user_id is None:
                row = await conn.fetchrow("SELECT * FROM ai_jobs WHERE id = $1::uuid", job_id)
            else:
                row = await conn.fetchrow(
                    "SELECT * FROM ai_jobs WHERE id = $1::uuid AND owner_user_id = $2", job_id, owner_user_id
                )
            return _normalize_ai_job(row) if row else None

    settings = get_settings()
    async with aiosqlite.connect(str(settings.db_path)) as db:
        db.row_factory = aiosqlite.Row
        if owner_user_id is None:
            cursor = await db.execute("SELECT * FROM ai_jobs WHERE id = ?", (job_id,))
        else:
            cursor = await db.execute("SELECT * FROM ai_jobs WHERE id = ? AND owner_user_id = ?", (job_id, owner_user_id))
        row = await cursor.fetchone()
        return _normalize_ai_job(row) if row else None


async def list_queued_ai_job_ids(limit: int = 100) -> list[str]:
    """Return only durable identifiers for safe broker reconciliation."""
    safe_limit = max(1, min(limit, 1_000))
    global _pg_pool
    if _pg_pool is not None:
        async with _pg_pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id FROM ai_jobs WHERE status = 'queued' ORDER BY created_at ASC LIMIT $1",
                safe_limit,
            )
            return [str(row["id"]) for row in rows]
    settings = get_settings()
    async with aiosqlite.connect(str(settings.db_path)) as db:
        cursor = await db.execute(
            "SELECT id FROM ai_jobs WHERE status = 'queued' ORDER BY created_at ASC LIMIT ?", (safe_limit,)
        )
        return [str(row[0]) for row in await cursor.fetchall()]


async def claim_ai_job(job_id: str) -> dict[str, Any] | None:
    """Atomically move a queued job to running; duplicate workers get None."""
    global _pg_pool
    if _pg_pool is not None:
        async with _pg_pool.acquire() as conn:
            row = await conn.fetchrow(
                """UPDATE ai_jobs SET status = 'running', progress = 10, attempts = attempts + 1,
                   updated_at = CURRENT_TIMESTAMP WHERE id = $1::uuid AND status = 'queued' RETURNING *""",
                job_id,
            )
            return _normalize_ai_job(row) if row else None

    settings = get_settings()
    async with aiosqlite.connect(str(settings.db_path)) as db:
        db.row_factory = aiosqlite.Row
        await db.execute("BEGIN IMMEDIATE")
        cursor = await db.execute("SELECT * FROM ai_jobs WHERE id = ? AND status = 'queued'", (job_id,))
        row = await cursor.fetchone()
        if not row:
            await db.commit()
            return None
        await db.execute(
            """UPDATE ai_jobs SET status = 'running', progress = 10, attempts = attempts + 1,
               updated_at = CURRENT_TIMESTAMP WHERE id = ?""",
            (job_id,),
        )
        cursor = await db.execute("SELECT * FROM ai_jobs WHERE id = ?", (job_id,))
        claimed = await cursor.fetchone()
        await db.commit()
        return _normalize_ai_job(claimed)


async def complete_ai_job(job_id: str, result: dict[str, Any], trace_id: str | None = None) -> bool:
    """Persist success only from the worker currently holding the job."""
    result_json = json.dumps(result, ensure_ascii=False)
    global _pg_pool
    if _pg_pool is not None:
        async with _pg_pool.acquire() as conn:
            status = await conn.execute(
                """UPDATE ai_jobs SET status = 'succeeded', progress = 100, result_json = $2::jsonb,
                   trace_id = $3, error_code = NULL, updated_at = CURRENT_TIMESTAMP
                   WHERE id = $1::uuid AND status = 'running'""",
                job_id, result_json, trace_id,
            )
            return status.endswith("1")
    settings = get_settings()
    async with aiosqlite.connect(str(settings.db_path)) as db:
        cursor = await db.execute(
            """UPDATE ai_jobs SET status = 'succeeded', progress = 100, result_json = ?, trace_id = ?,
               error_code = NULL, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND status = 'running'""",
            (result_json, trace_id, job_id),
        )
        await db.commit()
        return cursor.rowcount == 1


async def requeue_ai_job(job_id: str, error_code: str) -> bool:
    """Release a retryable running job back to the queue without losing its id."""
    global _pg_pool
    if _pg_pool is not None:
        async with _pg_pool.acquire() as conn:
            status = await conn.execute(
                """UPDATE ai_jobs SET status = 'queued', progress = 0, error_code = $2,
                   updated_at = CURRENT_TIMESTAMP WHERE id = $1::uuid AND status = 'running'""",
                job_id, error_code,
            )
            return status.endswith("1")
    settings = get_settings()
    async with aiosqlite.connect(str(settings.db_path)) as db:
        cursor = await db.execute(
            """UPDATE ai_jobs SET status = 'queued', progress = 0, error_code = ?,
               updated_at = CURRENT_TIMESTAMP WHERE id = ? AND status = 'running'""",
            (error_code, job_id),
        )
        await db.commit()
        return cursor.rowcount == 1


async def fail_ai_job(job_id: str, error_code: str, trace_id: str | None = None) -> bool:
    """Mark the terminal failure state without storing raw provider exceptions."""
    global _pg_pool
    if _pg_pool is not None:
        async with _pg_pool.acquire() as conn:
            status = await conn.execute(
                """UPDATE ai_jobs SET status = 'failed', error_code = $2, trace_id = $3,
                   updated_at = CURRENT_TIMESTAMP WHERE id = $1::uuid AND status = 'running'""",
                job_id, error_code, trace_id,
            )
            return status.endswith("1")
    settings = get_settings()
    async with aiosqlite.connect(str(settings.db_path)) as db:
        cursor = await db.execute(
            """UPDATE ai_jobs SET status = 'failed', error_code = ?, trace_id = ?,
               updated_at = CURRENT_TIMESTAMP WHERE id = ? AND status = 'running'""",
            (error_code, trace_id, job_id),
        )
        await db.commit()
        return cursor.rowcount == 1

