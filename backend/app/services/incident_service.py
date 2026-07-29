"""Incident lifecycle service — all database operations for incidents."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.incident import Incident
from app.models.incident_log import IncidentLog
from app.models.recommendation import AIRecommendation
from app.schemas.incident import (
    ApprovalRequest,
    IncidentCreate,
    IncidentState,
    IncidentUpdate,
    ResolutionRequest,
)


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def _uid() -> str:
    return uuid4().hex[:12]


def _add_log(
    db: Session,
    incident_id: str,
    event_type: str,
    message: str,
    actor: str,
    metadata: dict[str, Any] | None = None,
) -> IncidentLog:
    log = IncidentLog(
        id=f"log_{_uid()}",
        incident_id=incident_id,
        event_type=event_type,
        message=message,
        actor=actor,
    )
    log.metadata_dict = metadata or {}
    db.add(log)
    return log


def _add_audit(
    db: Session,
    entity_type: str,
    entity_id: str,
    action: str,
    actor: str,
    message: str,
    metadata: dict[str, Any] | None = None,
) -> AuditLog:
    audit = AuditLog(
        id=f"audit_{_uid()}",
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        actor=actor,
        message=message,
    )
    audit.metadata_dict = metadata or {}
    db.add(audit)
    return audit


# ── List / Read ────────────────────────────────────────────────────────


def list_incidents(
    db: Session,
    status: str | None = None,
    severity: str | None = None,
    service: str | None = None,
    query: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[dict[str, Any]], int]:
    q = db.query(Incident)
    if status:
        q = q.filter(Incident.status.ilike(status))
    if severity:
        q = q.filter(Incident.severity.ilike(severity))
    if service:
        q = q.filter(Incident.service.ilike(service))
    if query:
        needle = f"%{query}%"
        q = q.filter(
            Incident.title.ilike(needle)
            | Incident.description.ilike(needle)
            | Incident.tags_raw.ilike(needle)
        )
    total = q.count()
    rows = q.order_by(Incident.created_at.desc()).offset(offset).limit(limit).all()
    return [r.to_dict() for r in rows], total


def get_incident(db: Session, incident_id: str) -> dict[str, Any] | None:
    row = db.query(Incident).filter(
        (Incident.id == incident_id) | (Incident.incident_number == incident_id)
    ).first()
    return row.to_dict() if row else None


def get_detail(db: Session, incident_id: str) -> dict[str, Any] | None:
    incident = db.query(Incident).filter(
        (Incident.id == incident_id) | (Incident.incident_number == incident_id)
    ).first()
    if not incident:
        return None
    real_id = incident.id
    logs = (
        db.query(IncidentLog)
        .filter(IncidentLog.incident_id == real_id)
        .order_by(IncidentLog.created_at)
        .all()
    )
    audits = (
        db.query(AuditLog)
        .filter(
            (AuditLog.entity_id == real_id)
            | (AuditLog.metadata_raw.contains(real_id))
        )
        .order_by(AuditLog.created_at.desc())
        .all()
    )
    recommendations = (
        db.query(AIRecommendation)
        .filter(AIRecommendation.incident_id == real_id)
        .order_by(AIRecommendation.created_at.desc())
        .all()
    )
    base = incident.to_dict()
    log_dicts = [log.to_dict() for log in logs]
    return {
        **base,
        "incident": base,
        "incident_logs": log_dicts,
        "logs": log_dicts,
        "audit_logs": [a.to_dict() for a in audits],
        "ai_recommendations": [r.to_dict() for r in recommendations],
    }


# ── Create ─────────────────────────────────────────────────────────────


def create_incident(db: Session, request: IncidentCreate, actor: str = "Maya Chen") -> dict[str, Any]:
    now = _utcnow()
    count = db.query(Incident).count()
    incident = Incident(
        id=f"inc_{_uid()}",
        incident_number=f"INC-{now.year}-{count + 38:03d}",
        title=request.title,
        description=request.description,
        service=request.service,
        severity=request.severity.value if hasattr(request.severity, "value") else request.severity,
        status=request.status.value if hasattr(request.status, "value") else request.status,
        owner=request.owner,
        source=request.source,
        affected_users=request.affected_users,
        created_at=now,
        updated_at=now,
        resolved_at=now if request.status in {IncidentState.RESOLVED, IncidentState.CLOSED} else None,
        resolution_summary=None,
    )
    incident.tags = request.tags
    db.add(incident)
    _add_log(db, incident.id, "incident_created", f"{incident.incident_number} was created.", actor, {"source": incident.source})
    _add_audit(db, "incident", incident.id, "incident.created", actor, f"Created {incident.incident_number}.", {"severity": incident.severity})
    db.commit()
    db.refresh(incident)
    return incident.to_dict()


# ── Update ─────────────────────────────────────────────────────────────


def update_incident(
    db: Session, incident_id: str, request: IncidentUpdate, actor: str = "Maya Chen"
) -> dict[str, Any] | None:
    incident = db.query(Incident).filter(
        (Incident.id == incident_id) | (Incident.incident_number == incident_id)
    ).first()
    if not incident:
        return None
    real_id = incident.id
    changes = request.model_dump(exclude_unset=True, mode="json")
    if not changes:
        return incident.to_dict()
    previous_status = incident.status
    for key, value in changes.items():
        if key == "tags":
            incident.tags = value
        else:
            setattr(incident, key, value)
    incident.updated_at = _utcnow()
    if changes.get("status") in {IncidentState.RESOLVED.value, IncidentState.CLOSED.value} and not incident.resolved_at:
        incident.resolved_at = incident.updated_at
    _add_log(db, real_id, "incident_updated", "Incident fields were updated.", actor, {"fields": sorted(changes)})
    if "status" in changes and changes["status"] != previous_status:
        _add_log(db, real_id, "status_changed", f"Status changed from {previous_status} to {changes['status']}.", actor)
    _add_audit(db, "incident", real_id, "incident.updated", actor, f"Updated {incident.incident_number}.", {"fields": sorted(changes)})
    db.commit()
    db.refresh(incident)
    return incident.to_dict()


# ── Approve ────────────────────────────────────────────────────────────


def approve(db: Session, incident_id: str, request: ApprovalRequest) -> tuple[dict, dict] | None:
    incident = db.query(Incident).filter(
        (Incident.id == incident_id) | (Incident.incident_number == incident_id)
    ).first()
    if not incident:
        return None
    real_id = incident.id
    recommendations = (
        db.query(AIRecommendation)
        .filter(AIRecommendation.incident_id == real_id)
        .all()
    )
    recommendation = None
    if request.recommendation_id:
        recommendation = next((r for r in recommendations if r.id == request.recommendation_id), None)
    else:
        recommendation = next((r for r in recommendations if r.status in {"pending_approval", "ready_for_review"}), None)
    if not recommendation:
        recommendation = AIRecommendation(
            id=f"rec_{_uid()}",
            incident_id=real_id,
            title="Operator approval recorded",
            rationale="Approval was recorded without a linked AI recommendation.",
            confidence=100,
            risk="Low",
            status="pending_approval",
        )
        recommendation.proposed_actions = []
        db.add(recommendation)
    now = _utcnow()
    old_status = incident.status
    if request.decision == "approve":
        recommendation.status = "approved"
        recommendation.approved_at = now
        recommendation.approved_by = request.actor
        if incident.status == IncidentState.WAITING_APPROVAL.value:
            incident.status = IncidentState.INVESTIGATING.value
        message = f"Approved recommendation: {recommendation.title}."
        action = "recommendation.approved"
    else:
        recommendation.status = "rejected"
        if incident.status == IncidentState.WAITING_APPROVAL.value:
            incident.status = IncidentState.INVESTIGATING.value
        message = f"Rejected recommendation: {recommendation.title}."
        action = "recommendation.rejected"
    incident.updated_at = now
    meta = {"recommendation_id": recommendation.id, "decision": request.decision}
    if request.note:
        meta["note"] = request.note
    _add_log(db, real_id, "approval_recorded", message, request.actor, meta)
    if incident.status != old_status:
        _add_log(db, real_id, "status_changed", f"Status changed from {old_status} to {incident.status}.", request.actor)
    _add_audit(db, "recommendation", recommendation.id, action, request.actor, message, {"incident_id": real_id, **meta})
    db.commit()
    db.refresh(incident)
    db.refresh(recommendation)
    return incident.to_dict(), recommendation.to_dict()


# ── Resolve ────────────────────────────────────────────────────────────


def resolve(db: Session, incident_id: str, request: ResolutionRequest) -> dict[str, Any] | None:
    incident = db.query(Incident).filter(
        (Incident.id == incident_id) | (Incident.incident_number == incident_id)
    ).first()
    if not incident:
        return None
    real_id = incident.id
    now = _utcnow()
    previous_status = incident.status
    incident.status = IncidentState.RESOLVED.value
    incident.updated_at = now
    incident.resolved_at = now
    incident.resolution_summary = request.summary
    _add_log(db, real_id, "incident_resolved", "Incident marked resolved after operator confirmation.", request.actor, {"summary": request.summary})
    if previous_status != IncidentState.RESOLVED.value:
        _add_log(db, real_id, "status_changed", f"Status changed from {previous_status} to Resolved.", request.actor)
    _add_audit(db, "incident", real_id, "incident.resolved", request.actor, f"Resolved {incident.incident_number}.", {"summary": request.summary})
    db.commit()
    db.refresh(incident)
    return incident.to_dict()


# ── Delete ─────────────────────────────────────────────────────────────


def delete_incident(db: Session, incident_id: str, actor: str = "Maya Chen") -> bool:
    incident = db.query(Incident).filter(
        (Incident.id == incident_id) | (Incident.incident_number == incident_id)
    ).first()
    if not incident:
        return False
    _add_audit(db, "incident", incident.id, "incident.deleted", actor, f"Deleted {incident.incident_number}.")
    db.delete(incident)
    db.commit()
    return True


# ── Logs ───────────────────────────────────────────────────────────────


def get_incident_logs(db: Session, incident_id: str) -> list[dict[str, Any]] | None:
    incident = db.query(Incident).filter(
        (Incident.id == incident_id) | (Incident.incident_number == incident_id)
    ).first()
    if not incident:
        return None
    real_id = incident.id
    logs = (
        db.query(IncidentLog)
        .filter(IncidentLog.incident_id == real_id)
        .order_by(IncidentLog.created_at)
        .all()
    )
    return [log.to_dict() for log in logs]


# ── Audit ──────────────────────────────────────────────────────────────


def audit_logs(
    db: Session, incident_id: str | None = None, limit: int = 100
) -> list[dict[str, Any]]:
    q = db.query(AuditLog)
    if incident_id:
        q = q.filter(
            (AuditLog.entity_id == incident_id)
            | (AuditLog.metadata_raw.contains(incident_id))
        )
    rows = q.order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [r.to_dict() for r in rows]
