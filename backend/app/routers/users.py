"""Users router — manage workspace users and invitations."""

from __future__ import annotations

import uuid
from typing import List

from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user, require_role
from app.models.user import User
from app.schemas.auth import UserRead
from app.services.auth_service import get_password_hash

router = APIRouter(tags=["Users"], prefix="/users")

class InviteRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: str = Field(..., min_length=3, max_length=320)
    role: str = Field(..., min_length=2, max_length=40)

@router.get("", response_model=List[UserRead], summary="List users in workspace")
def list_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> List[UserRead]:
    if not current_user.workspace_id:
        # If user is not in a workspace, return just themself
        return [
            UserRead(
                id=current_user.id,
                name=current_user.name,
                email=current_user.email,
                role=current_user.role,
                avatar_initials=current_user.avatar_initials,
            )
        ]
        
    users = db.query(User).filter(User.workspace_id == current_user.workspace_id).all()
    return [
        UserRead(
            id=u.id,
            name=u.name,
            email=u.email,
            role=u.role,
            avatar_initials=u.avatar_initials,
        ) for u in users
    ]

@router.post("/invite", response_model=UserRead, summary="Invite a user to the workspace")
def invite_user(
    req: InviteRequest, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role("admin", "owner"))
) -> UserRead:
    if not current_user.workspace_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You must belong to a workspace to invite users")
        
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")

    avatar_initials = "".join([part[0].upper() for part in req.name.split() if part])[:2]
    
    # Default password for invited users is "demo123" (since there is no email integration yet)
    new_user = User(
        id=str(uuid.uuid4()),
        workspace_id=current_user.workspace_id,
        name=req.name,
        email=req.email,
        hashed_password=get_password_hash("demo123"),
        role=req.role,
        avatar_initials=avatar_initials,
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserRead(
        id=new_user.id,
        name=new_user.name,
        email=new_user.email,
        role=new_user.role,
        avatar_initials=new_user.avatar_initials,
    )
