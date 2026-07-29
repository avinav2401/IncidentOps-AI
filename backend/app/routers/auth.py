"""Authentication router — token management and user profile."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import base64
import time

from app.database import get_db
from app.schemas.auth import UserRead, LoginRequest, LoginResponse
from app.middleware.auth import get_current_user
from app.models.user import User
from app.config import settings

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=LoginResponse, summary="Demo login endpoint")
def login(req: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    if not settings.demo_mode:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Login only available in demo mode (use Supabase).")
    
    user = db.query(User).filter(User.email == req.email).first()
    if not user or req.password != "demo123":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    # Generate legacy demo token
    raw_token = f"incidentops-demo:{user.id}:{int(time.time())}"
    encoded = base64.urlsafe_b64encode(raw_token.encode()).decode().rstrip("=")
    
    return LoginResponse(
        access_token=encoded,
        user=UserRead(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            avatar_initials=user.avatar_initials,
        )
    )

@router.get("/me", response_model=UserRead, summary="Current user profile")
def me(user: User = Depends(get_current_user)) -> UserRead:
    return UserRead(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        avatar_initials=user.avatar_initials,
    )
