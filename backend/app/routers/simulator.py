"""Simulator router — triggers mock incidents and auto-starts the AI pipeline."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.agents.orchestrator import run_pipeline
from app.database import get_db
from app.middleware.auth import require_role
from app.models.user import User
from app.services.simulator import inject_payment_service_crash

router = APIRouter(tags=["Simulator"])


@router.post("/simulator/trigger", summary="Trigger a chaotic incident")
def trigger_incident(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("owner", "admin", "incident_commander")),
) -> dict[str, Any]:
    incident = inject_payment_service_crash(db, user.workspace_id, user.name)

    # Auto-trigger the AI pipeline (Step 3: AI starts automatically)
    background_tasks.add_task(run_pipeline, incident["id"])

    return {
        "message": "Simulated incident injected. AI pipeline started automatically.",
        "incident": incident,
    }
