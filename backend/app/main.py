"""FastAPI application for the IncidentOps AI backend.

The application factory builds the app with modular routers, CORS
middleware, and automatic database setup (table creation + seed data).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.routers import agents, analytics, audit, auth, chat, incidents, integrations, knowledge, reports, stream, users
from app.seed import seed_database


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Startup: create tables and seed data.  Shutdown: dispose engine."""
    # Import models so they are registered with Base.metadata.
    import app.models  # noqa: F401

    try:
        Base.metadata.create_all(bind=engine)

        # Seed demo data on first run.
        db = SessionLocal()
        try:
            seed_database(db)
        finally:
            db.close()
    except Exception:
        # During testing, the production engine may not be available.
        # This is expected — tests override get_db with their own engine.
        pass

    yield

    try:
        engine.dispose()
    except Exception:
        pass


def create_app() -> FastAPI:
    """Build the FastAPI application with all routers and middleware."""
    application = FastAPI(
        title="IncidentOps AI API",
        version="1.0.0",
        description="A self-contained, audit-friendly incident response API with AI-assisted operations.",
        lifespan=lifespan,
    )

    # CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check (always public).
    @application.get("/health", tags=["Health"])
    @application.get("/api/v1/health", tags=["Health"], include_in_schema=False)
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "incidentops-ai-api", "mode": "demo" if settings.demo_mode else "production"}

    @application.get("/", include_in_schema=False)
    def root(request: Request) -> dict[str, str]:
        base = str(request.base_url).rstrip("/")
        return {"service": "IncidentOps AI API", "docs": f"{base}/docs", "health": f"{base}/health"}

    # Mount all routers — both versioned (/api/v1/...) and unversioned for
    # backward compatibility with the demo frontend.
    from app.routers import services, simulator, workspaces

    all_routers = [
        auth.router,
        workspaces.router,
        services.router,
        incidents.router,
        analytics.router,
        agents.router,
        audit.router,
        chat.router,
        integrations.router,
        knowledge.router,
        reports.router,
        stream.router,
        simulator.router,
        users.router,
    ]
    for router in all_routers:
        application.include_router(router, prefix="/api/v1")
        application.include_router(router, include_in_schema=False)

    return application


app = create_app()
