"""Analytics service — computes incident metrics from the database."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.schemas.incident import IncidentState


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def compute_analytics(db: Session, workspace_id: str) -> dict[str, Any]:
    """Generate the analytics payload from current database state."""
    incidents = db.query(Incident).filter(Incident.workspace_id == workspace_id).all()

    statuses = {state.value: 0 for state in IncidentState}
    severities = {f"P{n}": 0 for n in range(1, 5)}

    for inc in incidents:
        statuses[inc.status] = statuses.get(inc.status, 0) + 1
        severities[inc.severity] = severities.get(inc.severity, 0) + 1

    resolved = [i for i in incidents if i.status in {IncidentState.RESOLVED.value, IncidentState.CLOSED.value}]
    mttr_values: list[float] = []
    for item in resolved:
        if item.resolved_at and item.created_at:
            delta = (item.resolved_at - item.created_at).total_seconds() / 60
            mttr_values.append(round(delta, 1))

    now = _utcnow()
    active = (
        statuses.get(IncidentState.OPEN.value, 0)
        + statuses.get(IncidentState.INVESTIGATING.value, 0)
        + statuses.get(IncidentState.WAITING_APPROVAL.value, 0)
    )
    created_this_week = 0
    for i in incidents:
        if i.created_at:
            dt = i.created_at
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=UTC)
            if dt >= now - timedelta(days=7):
                created_this_week += 1

    # Compute real trend data for the past 7 days
    trend = []
    for i in range(6, -1, -1):
        day_start = now.replace(hour=0, minute=0, second=0) - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        
        opened_count = 0
        resolved_count = 0
        
        for inc in incidents:
            inc_created = inc.created_at.replace(tzinfo=UTC) if inc.created_at and inc.created_at.tzinfo is None else inc.created_at
            inc_resolved = inc.resolved_at.replace(tzinfo=UTC) if inc.resolved_at and inc.resolved_at.tzinfo is None else inc.resolved_at
            
            if inc_created and day_start <= inc_created < day_end:
                opened_count += 1
            if inc_resolved and day_start <= inc_resolved < day_end:
                resolved_count += 1
                
        label = day_start.strftime("%a") if i > 0 else "Today"
        trend.append({"label": label, "opened": opened_count, "resolved": resolved_count})

    return {
        "overview": {
            "total_incidents": len(incidents),
            "active_incidents": active,
            "waiting_approval": statuses.get(IncidentState.WAITING_APPROVAL.value, 0),
            "resolved_incidents": len(resolved),
            "resolution_rate": round((len(resolved) / len(incidents) * 100) if incidents else 0, 1),
            "mean_time_to_resolution_minutes": round(sum(mttr_values) / len(mttr_values), 1) if mttr_values else 0,
            "incidents_this_week": created_this_week,
        },
        "by_status": statuses,
        "by_severity": severities,
        "trend": trend,
    }
