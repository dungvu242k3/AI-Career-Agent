import asyncio
import logging
from be.workers.celery_app import celery_app
from ai.pipeline import get_default_ingestion_pipeline

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def process_cv_async(self, file_path: str, candidate_id: str, raw_text: str):
    """Background task to process CV via LLM with retries on failure."""
    logger.info(f"Starting async CV processing for candidate {candidate_id}")

    # Celery tasks are synchronous. Use asyncio.run() (Python 3.12-safe)
    # instead of deprecated asyncio.get_event_loop().
    try:
        pipeline = get_default_ingestion_pipeline()

        async def _run_extraction():
            # Since raw_text is already extracted by Parser, call extractor directly.
            profile = await pipeline.primary_extractor.extract_profile(raw_text)
            return profile.model_dump()

        result = asyncio.run(_run_extraction())

        # After extraction, update DB and notify via WebSocket.
        logger.info(f"Successfully processed CV for candidate {candidate_id}")
        return result

    except Exception as exc:
        logger.error(f"Task failed for candidate {candidate_id}: {exc}")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

