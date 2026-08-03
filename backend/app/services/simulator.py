"""Simulator service — injects realistic incidents from the scenario library.

Each trigger picks a random scenario from the library (or a specific one
by index), creates a real incident record, and attaches the scenario's
evidence data so the AI agents receive varied, realistic signals.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.schemas.incident import IncidentCreate, IncidentState
from app.services.incident_service import create_incident
from app.services.scenarios import SCENARIOS, Scenario, get_random_scenario, get_scenario_by_index


def _inject_scenario(db: Session, workspace_id: str, actor: str, scenario: Scenario) -> dict:
    """Create an incident from a Scenario dataclass and return its dict."""
    payload = IncidentCreate(
        title=scenario.title,
        description=scenario.description,
        service=scenario.service,
        severity=scenario.severity,
        status=IncidentState.INVESTIGATING,
        owner=actor,
        source="Monitor Agent",
        affected_users=scenario.affected_users,
        tags=scenario.tags,
    )
    incident = create_incident(db, workspace_id, payload, actor)

    # Attach scenario evidence to the incident dict so the orchestrator
    # can pass it to the agents instead of relying on hardcoded mocks.
    incident["_scenario"] = {
        "logs": scenario.logs,
        "metrics": scenario.metrics,
        "monitor_status": scenario.monitor_status,
        "monitor_details": scenario.monitor_details,
        "recent_commits": scenario.recent_commits,
        "knowledge_context": scenario.knowledge_context,
    }
    return incident


def inject_random_incident(db: Session, workspace_id: str, actor: str) -> dict:
    """Inject a random incident scenario."""
    return _inject_scenario(db, workspace_id, actor, get_random_scenario())


def inject_scenario_by_index(db: Session, workspace_id: str, actor: str, index: int) -> dict:
    """Inject a specific incident scenario by its index (0-based)."""
    return _inject_scenario(db, workspace_id, actor, get_scenario_by_index(index))


def inject_payment_service_crash(db: Session, workspace_id: str, actor: str) -> dict:
    """Legacy entrypoint — injects the Payment API Timeout scenario (index 0)."""
    return inject_scenario_by_index(db, workspace_id, actor, 0)


def list_scenarios() -> list[dict]:
    """Return a summary of all available scenarios for the frontend."""
    return [
        {
            "index": i,
            "title": s.title,
            "service": s.service,
            "severity": s.severity,
            "description": s.description,
            "tags": s.tags,
        }
        for i, s in enumerate(SCENARIOS)
    ]
