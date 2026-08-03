"""Simulator router — triggers diverse incident scenarios and auto-starts the AI pipeline.

Endpoints:
- POST /simulator/trigger          → Random scenario (or specific by index)
- GET  /simulator/scenarios        → List all available scenarios
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.orm import Session

from app.agents.orchestrator import run_pipeline, store_scenario_data
from app.database import get_db
from app.middleware.auth import require_role
from app.models.user import User
from app.services.simulator import inject_random_incident, inject_scenario_by_index, list_scenarios

router = APIRouter(tags=["Simulator"])


@router.get("/simulator/scenarios", summary="List available incident scenarios")
def get_scenarios() -> list[dict[str, Any]]:
    """Return a summary of all available chaos scenarios the simulator can inject."""
    return list_scenarios()


@router.post("/simulator/trigger", summary="Trigger a chaotic incident")
def trigger_incident(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("owner", "admin", "incident_commander")),
    scenario_index: int | None = Query(default=None, description="Specific scenario index (0-9). Omit for random."),
) -> dict[str, Any]:
    """Inject a simulated incident and auto-start the AI investigation pipeline.

    Pass ``scenario_index`` to pick a specific scenario, or omit it for a random one.
    """
    if scenario_index is not None:
        incident = inject_scenario_by_index(db, user.workspace_id, user.name, scenario_index)
    else:
        incident = inject_random_incident(db, user.workspace_id, user.name)

    # Cache scenario evidence for the orchestrator to use
    scenario_evidence = incident.pop("_scenario", None)
    if scenario_evidence:
        store_scenario_data(incident["id"], scenario_evidence)

    # Auto-trigger the AI pipeline
    background_tasks.add_task(run_pipeline, incident["id"])

    return {
        "message": f"Simulated incident injected: {incident['title']}. AI pipeline started.",
        "incident": incident,
    }
