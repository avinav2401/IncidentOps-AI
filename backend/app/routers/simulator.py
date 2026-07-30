from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Any

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services.simulator import inject_payment_service_crash

router = APIRouter(tags=["Simulator"])

@router.post("/simulator/trigger", summary="Trigger the Payment Service Crash scenario")
def trigger_simulation(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    incident = inject_payment_service_crash(db, user.name)
    return {
        "message": "Simulated incident injected successfully.",
        "incident": incident
    }
