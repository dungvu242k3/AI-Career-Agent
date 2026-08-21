import asyncio

from be import config as config_module
from be.db import database


def test_ai_job_idempotency_is_atomic_for_concurrent_requests(monkeypatch, tmp_path):
    database_path = tmp_path / "ai-jobs.db"
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///./unused.db")
    monkeypatch.setenv("DB_PATH", str(database_path))
    config_module.get_settings.cache_clear()
    database._pg_pool = None

    async def run_test():
        await database.init_db()
        jobs = await asyncio.gather(
            *[
                database.create_ai_job(
                    owner_user_id=7,
                    operation="cv-generation",
                    idempotency_key="same-request",
                    payload={"candidate_id": "candidate-1"},
                )
                for _ in range(8)
            ]
        )
        ids = {job[0]["id"] for job in jobs}
        assert len(ids) == 1
        assert sum(1 for _, duplicate in jobs if not duplicate) == 1

        claimed = await database.claim_ai_job(next(iter(ids)))
        assert claimed is not None
        assert (await database.claim_ai_job(next(iter(ids)))) is None
        assert await database.complete_ai_job(claimed["id"], {"storage_key": "private.pdf"})
        saved = await database.get_ai_job(claimed["id"], owner_user_id=7)
        assert saved and saved["status"] == "succeeded"
        assert await database.get_ai_job(claimed["id"], owner_user_id=8) is None

    try:
        asyncio.run(run_test())
    finally:
        config_module.get_settings.cache_clear()
