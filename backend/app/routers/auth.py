"""Authentication router — token management and user profile."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import UserRead
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter(tags=["Authentication"])


@router.get("/me", response_model=UserRead, summary="Current user profile")
def me(user: User = Depends(get_current_user)) -> UserRead:
    return UserRead(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        avatar_initials=user.avatar_initials,
    )
