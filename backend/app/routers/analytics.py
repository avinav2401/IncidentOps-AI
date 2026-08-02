"""Analytics router."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services.analytics_service import compute_analytics

router = APIRouter(tags=["Analytics"])


@router.get("/analytics", summary="Incident operations analytics")
def analytics(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> dict[str, Any]:
    return compute_analytics(db, _user.workspace_id)
