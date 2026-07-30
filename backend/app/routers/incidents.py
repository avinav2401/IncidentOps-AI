"""Incident CRUD and lifecycle router."""

from __future__ import annotations

import logging

from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.agents.orchestrator import run_pipeline
from app.agents.post_approval_pipeline import run_post_approval_pipeline
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.incident import (
    ApprovalRequest,
    IncidentCreate,
    IncidentDetail,
    IncidentListResponse,
    IncidentLogRead,
    IncidentRead,
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
    _user: User = Depends(get_current_user),
) -> IncidentListResponse:
    rows, total = svc.list_incidents(db, status_filter, severity, service, q, limit, offset)
    incidents = [IncidentRead.model_validate(row) for row in rows]
    return IncidentListResponse(items=incidents, incidents=incidents, total=total, limit=limit, offset=offset)


@router.post("/incidents", response_model=IncidentRead, status_code=status.HTTP_201_CREATED, summary="Create an incident")
def create_incident(
    payload: IncidentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> IncidentRead:
    return IncidentRead.model_validate(svc.create_incident(db, payload, user.name))


@router.get("/incidents/{incident_id}", response_model=IncidentDetail, summary="Get incident detail")
def get_incident(
    incident_id: str,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> IncidentDetail:
    detail = svc.get_detail(db, incident_id)
    if not detail:
        raise _not_found(incident_id)
    return IncidentDetail.model_validate(detail)


@router.patch("/incidents/{incident_id}", response_model=IncidentRead, summary="Update an incident")
def update_incident(
    incident_id: str,
    payload: IncidentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> IncidentRead:
    incident = svc.update_incident(db, incident_id, payload, user.name)
    if not incident:
        raise _not_found(incident_id)
    return IncidentRead.model_validate(incident)


@router.delete("/incidents/{incident_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an incident")
def delete_incident(
    incident_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Response:
    if not svc.delete_incident(db, incident_id, user.name):
        raise _not_found(incident_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/incidents/{incident_id}/logs", response_model=list[IncidentLogRead], summary="Get incident timeline")
def get_incident_logs(
    incident_id: str,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> list[IncidentLogRead]:
    logs = svc.get_incident_logs(db, incident_id)
    if logs is None:
        raise _not_found(incident_id)
    return [IncidentLogRead.model_validate(item) for item in logs]


@router.post("/incidents/{incident_id}/approve", summary="Record a recommendation decision")
def approve_incident(
    incident_id: str,
    payload: ApprovalRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> dict[str, Any]:
    result = svc.approve(db, incident_id, payload)
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
    _user: User = Depends(get_current_user),
) -> IncidentRead:
    incident = svc.resolve(db, incident_id, payload)
    if not incident:
        raise _not_found(incident_id)
    return IncidentRead.model_validate(incident)


@router.post("/incidents/{incident_id}/analyze", summary="Trigger AI analysis pipeline")
async def trigger_ai_analysis(
    incident_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> dict[str, Any]:
    incident = svc.get_detail(db, incident_id)
    if not incident:
        raise _not_found(incident_id)

    background_tasks.add_task(run_pipeline, incident["id"])
    return {"message": "AI analysis started."}


@router.get("/incidents/{incident_id}/notifications", summary="Get Slack and Jira notifications for an incident")
def get_notifications(
    incident_id: str,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> dict[str, Any]:
    result = svc.get_notifications(db, incident_id)
    if result is None:
        raise _not_found(incident_id)
    return result

