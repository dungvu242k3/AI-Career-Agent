"""CareerPilot AI — FastAPI Application Entry Point."""

from contextlib import asynccontextmanager
from pathlib import Path
import sys

# Add workspace root to Python path so 'ai' package is always resolvable
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from be.api.v1.cv_router import router as cv_router
from be.api.v1.ats_router import router as ats_router
from be.config import get_settings
from be.db.database import init_db, close_db


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

    # Ensure data and upload directories exist
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)

    # Initialize Database (PostgreSQL / SQLite)
    await init_db()

    yield

    # Graceful shutdown of connection pools
    await close_db()


def create_app() -> FastAPI:
    """FastAPI Application Factory."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        debug=settings.debug,
        description="CareerPilot AI — Next-Gen AI Career Agent & Automation Suite",
        lifespan=lifespan,
    )

    # Security Headers Middleware
    app.add_middleware(SecurityHeadersMiddleware)

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
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

    @app.get("/health", tags=["Monitoring"])
    async def health_check():
        return {"status": "ok", "app": settings.app_name, "version": "0.1.0"}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("be.main:app", host="0.0.0.0", port=8000, reload=True)
