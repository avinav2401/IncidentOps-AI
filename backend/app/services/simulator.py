from sqlalchemy.orm import Session

from app.schemas.incident import IncidentCreate, IncidentState
from app.services.incident_service import create_incident


def inject_payment_service_crash(db: Session, workspace_id: str, actor: str) -> dict:
    payload = IncidentCreate(
        title="Payment Service Down",
        description="CPU 99%, Memory 98%, 500 Errors, Latency 12s",
        service="Payment Service",
        severity="P1",
        status=IncidentState.INVESTIGATING,
        owner=actor,
        source="Monitor Agent",
        affected_users=15000,
        tags=["payment", "critical", "simulated"],
    )
    return create_incident(db, workspace_id, payload, actor)
