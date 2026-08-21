"""Explicit production database migration command.

Run from the repository root with the production environment loaded:

    python -m be.db.migrate

The web application only validates the schema version in production; it does
not perform DDL during startup.
"""

from __future__ import annotations

import asyncio

import aiosqlite
import asyncpg

from be.config import get_settings
from be.db.database import _get_clean_pg_url, is_postgres
from be.db.migrations import apply_postgres_migrations, apply_sqlite_migrations


async def migrate() -> int:
    settings = get_settings()
    if is_postgres():
        conn = await asyncpg.connect(_get_clean_pg_url(settings.database_url))
        try:
            return await apply_postgres_migrations(conn)
        finally:
            await conn.close()

    async with aiosqlite.connect(str(settings.db_path)) as db:
        return await apply_sqlite_migrations(db)


def main() -> None:
    version = asyncio.run(migrate())
    print(f"Database migrated successfully to schema_version={version}")


if __name__ == "__main__":
    main()
