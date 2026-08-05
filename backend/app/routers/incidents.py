"""Incident CRUD and lifecycle router."""

from __future__ import annotations

import random
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.agents.knowledge_base import kb
from app.agents.orchestrator import run_pipeline
from app.agents.post_approval_pipeline import run_post_approval_pipeline
from app.database import get_db
from app.middleware.auth import require_role
from app.models.user import User
from app.schemas.incident import (
    ApprovalRequest,
    CommentRequest,
    IncidentCreate,
    IncidentDetail,
    IncidentListResponse,
    IncidentLogRead,
    IncidentRead,
    IncidentState,
    IncidentUpdate,
    ResolutionRequest,
)
from app.services import incident_service as svc

router = APIRouter(tags=["Incidents"])


def _not_found(incident_id: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' was not found.")


@router.get("/incidents", response_model=IncidentListResponse, summary="List incidents")
def list_incidents(
    status_filter: str | None = Query(default=None, alias="status"),
    severity: str | None = Query(default=None),
    service: str | None = Query(default=None),
    q: str | None = Query(default=None, max_length=180),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _user: User = Depends(
        require_role("owner", "admin", "auditor", "incident_commander", "responder", "sme", "observer", "external_stakeholder")
    ),
) -> IncidentListResponse:
    rows, total = svc.list_incidents(db, _user.workspace_id, status_filter, severity, service, q, limit, offset)
    incidents = [IncidentRead.model_validate(row) for row in rows]
    return IncidentListResponse(items=incidents, incidents=incidents, total=total, limit=limit, offset=offset)


@router.post("/incidents", response_model=IncidentRead, status_code=status.HTTP_201_CREATED, summary="Create an incident")
def create_incident(
    payload: IncidentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("owner", "admin", "incident_commander", "automation")),
) -> IncidentRead:
    return IncidentRead.model_validate(svc.create_incident(db, user.workspace_id, payload, user.name))


@router.post("/simulate", response_model=IncidentRead, status_code=status.HTTP_201_CREATED, summary="Simulate a chaos event")
def simulate_incident(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("owner", "admin", "incident_commander", "automation")),
) -> IncidentRead:
    services = ["Payment Service", "API Gateway", "Database", "Redis Cache", "Inventory System", "Notification Service"]
    issues = [
        ("Memory Leak", "OOM (Out of Memory) errors detected causing CrashLoopBackOff.", "P1", 12500),
        ("High Latency", "API requests timing out after 30s.", "P2", 4500),
        ("Connection Refused", "Database connections failing.", "P1", 15000),
        ("Replication Lag", "Read replicas falling behind primary.", "P3", 1200),
        ("CPU Spikes", "Service consuming 100% CPU.", "P2", 3000),
    ]

    svc_name = random.choice(services)
    issue_title, desc, severity, users = random.choice(issues)

    payload = IncidentCreate(
        title=f"[{svc_name}] {issue_title}",
        description=f"Automated chaos engineering simulation: {desc} Affecting critical paths.",
        service=svc_name,
        severity=severity,
        status=IncidentState.OPEN,
        affected_users=users,
        tags=["simulated", "chaos"],
        source="Chaos Simulator",
    )
    return IncidentRead.model_validate(svc.create_incident(db, user.workspace_id, payload, "Simulator"))


@router.get("/incidents/{incident_id}", response_model=IncidentDetail, summary="Get incident detail")
def get_incident(
    incident_id: str,
    db: Session = Depends(get_db),
    _user: User = Depends(
        require_role("owner", "admin", "auditor", "incident_commander", "responder", "sme", "observer", "external_stakeholder")
    ),
) -> IncidentDetail:
    detail = svc.get_detail(db, _user.workspace_id, incident_id)
    if not detail:
        raise _not_found(incident_id)
    return IncidentDetail.model_validate(detail)


@router.patch("/incidents/{incident_id}", response_model=IncidentRead, summary="Update an incident")
def update_incident(
    incident_id: str,
    payload: IncidentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("owner", "admin", "incident_commander", "automation")),
) -> IncidentRead:
    incident = svc.update_incident(db, user.workspace_id, incident_id, payload, user.name)
    if not incident:
        raise _not_found(incident_id)
    return IncidentRead.model_validate(incident)


@router.delete("/incidents/{incident_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an incident")
def delete_incident(
    incident_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("owner", "admin")),
) -> Response:
    if not svc.delete_incident(db, user.workspace_id, incident_id, user.name):
        raise _not_found(incident_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/incidents/{incident_id}/logs", response_model=list[IncidentLogRead], summary="Get incident timeline")
def get_incident_logs(
    incident_id: str,
    db: Session = Depends(get_db),
    _user: User = Depends(
        require_role("owner", "admin", "auditor", "incident_commander", "responder", "sme", "observer", "external_stakeholder")
    ),
) -> list[IncidentLogRead]:
    logs = svc.get_incident_logs(db, _user.workspace_id, incident_id)
    if logs is None:
        raise _not_found(incident_id)
    return [IncidentLogRead.model_validate(item) for item in logs]


@router.post("/incidents/{incident_id}/approve", summary="Record a recommendation decision")
def approve_incident(
    incident_id: str,
    payload: ApprovalRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role("owner", "admin", "incident_commander", "automation")),
) -> dict[str, Any]:
    payload.actor = _user.name
    result = svc.approve(db, _user.workspace_id, incident_id, payload)
    if not result:
        raise _not_found(incident_id)
    incident, recommendation = result
    past_tense = "approved" if payload.decision == "approve" else "rejected"

    # On approval, kick off the post-approval pipeline (execute → verify → notify → resolve)
    if payload.decision == "approve":
        background_tasks.add_task(
            run_post_approval_pipeline,
            incident["id"],
            recommendation.get("title", "Apply fix"),
            recommendation.get("rationale", "Unknown root cause"),
        )

    return {
        "message": f"Recommendation {past_tense} successfully.",
        "incident": IncidentRead.model_validate(incident),
        "recommendation": recommendation,
    }


@router.post("/incidents/{incident_id}/resolve", response_model=IncidentRead, summary="Resolve an incident")
def resolve_incident(
    incident_id: str,
    payload: ResolutionRequest,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role("owner", "admin", "incident_commander", "automation")),
) -> IncidentRead:
    payload.actor = _user.name
    incident = svc.resolve(db, _user.workspace_id, incident_id, payload)
    if not incident:
        raise _not_found(incident_id)

    detail = svc.get_detail(db, _user.workspace_id, incident_id)
    recs = detail.get("ai_recommendations", []) if detail else []
    rec = recs[0] if recs else {}

    incident_dict = {
        "incident_number": incident.get("incident_number"),
        "service": incident.get("service"),
        "severity": incident.get("severity"),
        "owner": incident.get("owner"),
        "description": incident.get("description"),
    }
    kb.index_resolved_incident(incident_dict, rec)

    return IncidentRead.model_validate(incident)


@router.post("/incidents/{incident_id}/comments", response_model=IncidentLogRead, summary="Add a comment to an incident")
def add_comment(
    incident_id: str,
    payload: CommentRequest,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role("owner", "admin", "incident_commander", "responder", "sme", "automation")),
) -> IncidentLogRead:
    payload.actor = _user.name
    log = svc.add_comment(db, _user.workspace_id, incident_id, payload.content, payload.actor)
    if not log:
        raise _not_found(incident_id)
    return IncidentLogRead.model_validate(log)


@router.post("/incidents/{incident_id}/analyze", summary="Trigger AI analysis pipeline")
async def trigger_ai_analysis(
    incident_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role("owner", "admin", "incident_commander", "responder", "sme", "automation")),
) -> dict[str, Any]:
    incident = svc.get_detail(db, _user.workspace_id, incident_id)
    if not incident:
        raise _not_found(incident_id)

    background_tasks.add_task(run_pipeline, incident["id"])
    return {"message": "AI analysis started."}


@router.get("/incidents/{incident_id}/notifications", summary="Get Slack and Jira notifications for an incident")
def get_notifications(
    incident_id: str,
    db: Session = Depends(get_db),
    _user: User = Depends(
        require_role("owner", "admin", "auditor", "incident_commander", "responder", "sme", "observer", "external_stakeholder")
    ),
) -> dict[str, Any]:
    result = svc.get_notifications(db, _user.workspace_id, incident_id)
    if result is None:
        raise _not_found(incident_id)
    return result
