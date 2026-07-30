"""Simulator router — triggers mock incidents and auto-starts the AI pipeline."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.agents.orchestrator import run_pipeline
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services.simulator import inject_payment_service_crash

router = APIRouter(tags=["Simulator"])


@router.post("/simulator/trigger", summary="Trigger the Payment Service Crash scenario")
def trigger_simulation(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    incident = inject_payment_service_crash(db, user.name)

    # Auto-trigger the AI pipeline (Step 3: AI starts automatically)
    background_tasks.add_task(run_pipeline, incident["id"])

    return {
        "message": "Simulated incident injected. AI pipeline started automatically.",
        "incident": incident,
    }
