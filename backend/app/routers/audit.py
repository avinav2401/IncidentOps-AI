"""Audit log router."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services import incident_service as svc

router = APIRouter(tags=["Audit"])


@router.get("/audit-logs", summary="Read the audit trail")
def audit_logs(
    incident_id: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=250),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> dict[str, Any]:
    rows = svc.audit_logs(db, incident_id=incident_id, limit=limit)
    return {"items": rows, "total": len(rows)}
