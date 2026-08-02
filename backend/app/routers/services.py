"""Services router — manage workspace services."""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.service import Service

router = APIRouter(tags=["Services"], prefix="/services")

class ServiceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    owner_team: str = Field(..., min_length=1, max_length=200)
    repository: str | None = None
    language: str | None = None
    environment: str = "Production"
    critical_level: str = "High"
    description: str | None = None

@router.post("", summary="Create a new service")
def create_service(req: ServiceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.workspace_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User must belong to a workspace to add a service")

    new_service = Service(
        id=str(uuid.uuid4()),
        workspace_id=current_user.workspace_id,
        name=req.name,
        owner_team=req.owner_team,
        repository=req.repository,
        language=req.language,
        environment=req.environment,
        critical_level=req.critical_level,
        description=req.description,
    )
    db.add(new_service)
    db.commit()
    db.refresh(new_service)

    return new_service.to_dict()

@router.get("", summary="List all services in workspace")
def list_services(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.workspace_id:
        return []
    services = db.query(Service).filter(Service.workspace_id == current_user.workspace_id).all()
    return [s.to_dict() for s in services]
