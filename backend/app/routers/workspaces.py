"""Workspace router — manage organizations."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceRead

router = APIRouter(tags=["Workspaces"], prefix="/workspaces")


@router.post("", response_model=WorkspaceRead, summary="Create a new workspace")
def create_workspace(req: WorkspaceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> WorkspaceRead:
    if current_user.workspace_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already belongs to a workspace")

    # Basic slug generation
    slug = req.name.lower().replace(" ", "-") + "-" + str(uuid.uuid4())[:8]

    new_workspace = Workspace(
        id=str(uuid.uuid4()), name=req.name, slug=slug, industry=req.industry, company_size=req.company_size, owner_id=current_user.id
    )
    db.add(new_workspace)

    # Link user to the new workspace
    current_user.workspace_id = new_workspace.id

    db.commit()
    db.refresh(new_workspace)

    return WorkspaceRead(
        id=new_workspace.id,
        name=new_workspace.name,
        slug=new_workspace.slug,
        industry=new_workspace.industry,
        company_size=new_workspace.company_size,
        owner_id=new_workspace.owner_id,
        created_at=new_workspace.created_at.isoformat() if new_workspace.created_at else None,
    )


@router.get("/current", response_model=WorkspaceRead, summary="Get current workspace")
def get_current_workspace(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> WorkspaceRead:
    if not current_user.workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    workspace = db.query(Workspace).filter(Workspace.id == current_user.workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    return WorkspaceRead(
        id=workspace.id,
        name=workspace.name,
        slug=workspace.slug,
        industry=workspace.industry,
        company_size=workspace.company_size,
        owner_id=workspace.owner_id,
        created_at=workspace.created_at.isoformat() if workspace.created_at else None,
    )
