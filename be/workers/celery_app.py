import os
from celery import Celery

# Default to local redis if not specified in environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "ai_career_agent",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["be.workers.ai_task_worker"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Ho_Chi_Minh",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300, # 5 minutes max per task
)
