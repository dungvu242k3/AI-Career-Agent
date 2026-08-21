"""CareerPilot AI — FastAPI Application Entry Point."""

from contextlib import asynccontextmanager
from pathlib import Path
import sys

# Add workspace root to Python path so 'ai' package is always resolvable
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

import asyncio

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware

from be.api.v1.cv_router import router as cv_router
from be.api.v1.ats_router import router as ats_router
from be.api.v1.chat_router import router as chat_router
from be.api.v1.interview_router import router as interview_router
from be.api.v1.ai_jobs_router import router as ai_jobs_router
from be.config import get_settings
from be.db.database import check_database_ready, close_db, init_db
from be.core.redis_client import check_redis_ready, close_redis_client
from be.observability import RequestContextMiddleware, configure_logging, request_metrics
from be.telemetry import configure_api_telemetry, shutdown_telemetry


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware enforcing OWASP-recommended HTTP security headers."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup & shutdown events."""
    settings = get_settings()
    settings.validate_production_settings()

    # Ensure data and upload directories exist
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)

    # Initialize Database (PostgreSQL / SQLite)
    await init_db()

    yield

    # Graceful shutdown of connection pools
    await close_db()
    await close_redis_client()
    shutdown_telemetry()


def create_app() -> FastAPI:
    """FastAPI Application Factory."""
    settings = get_settings()
    configure_logging(production=settings.is_production)

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        debug=settings.debug,
        description="CareerPilot AI — Next-Gen AI Career Agent & Automation Suite",
        lifespan=lifespan,
    )
    configure_api_telemetry(app)

    # Security Headers Middleware
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestContextMiddleware)

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=[
            "Content-Disposition",
            "X-Estimated-ATS-Score",
            "X-Estimated-Word-Count",
            "X-Critic-Score",
            "X-Critic-Approved",
            "X-Reflection-Iterations",
        ],
    )

    # Mount API Routers
    app.include_router(
        cv_router,
        prefix=f"{settings.api_prefix}/cv",
        tags=["CV Ingestion & Preview"],
    )
    app.include_router(
        ats_router,
        prefix=f"{settings.api_prefix}/ats",
        tags=["ATS Studio & STAR Rewriter"],
    )
    app.include_router(
        chat_router,
        prefix=f"{settings.api_prefix}",
        tags=["Chat & Job Search"],
    )
    app.include_router(
        interview_router,
        prefix=f"{settings.api_prefix}",
        tags=["Mock Interview Arena"],
    )
    app.include_router(ai_jobs_router, prefix=settings.api_prefix)

    @app.get("/health/live", tags=["Monitoring"])
    async def liveness_check():
        return {"status": "ok", "app": settings.app_name, "version": "0.1.0"}

    @app.get("/health/ready", tags=["Monitoring"])
    async def readiness_check():
        async def bounded(check):
            try:
                return await asyncio.wait_for(check(), timeout=1.0)
            except Exception:
                return False

        checks = {
            "database": await bounded(check_database_ready),
            "redis": await bounded(check_redis_ready),
        }
        ready = all(checks.values())
        return JSONResponse(
            status_code=200 if ready else 503,
            content={
                "status": "ready" if ready else "not_ready",
                "app": settings.app_name,
                "checks": checks,
            },
        )

    @app.get("/metrics", include_in_schema=False, tags=["Monitoring"])
    async def metrics():
        return PlainTextResponse(
            request_metrics.prometheus_text(),
            media_type="text/plain; version=0.0.4",
        )

    @app.get("/health", tags=["Monitoring"])
    async def health_check():
        """Legacy liveness endpoint kept for existing probes and clients."""
        return await liveness_check()

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("be.main:app", host="0.0.0.0", port=8000, reload=True)
