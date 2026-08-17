"""CareerPilot AI — FastAPI Application Entry Point"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from api.v1.cv_router import router as cv_router
from db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    # Ensure data directories exist
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path("./data").mkdir(parents=True, exist_ok=True)

    # Initialize database
    await init_db()

    yield


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="AI-powered career automation agent",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(cv_router, prefix=f"{settings.api_prefix}/cv", tags=["CV"])

    @app.get("/health")
    async def health_check():
        return {"status": "ok", "app": settings.app_name}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
