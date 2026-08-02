"""Authentication router — token management and user profile."""

from __future__ import annotations

import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, SignupRequest, UserRead
from app.services.auth_service import create_access_token, get_password_hash, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=LoginResponse, summary="Register a new user")
def signup(req: SignupRequest, db: Session = Depends(get_db)) -> LoginResponse:
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user_id = str(uuid.uuid4())
    avatar_initials = "".join([part[0].upper() for part in req.name.split() if part])[:2]

    new_user = User(
        id=user_id,
        name=req.name,
        email=req.email,
        hashed_password=get_password_hash(req.password),
        role="responder",
        avatar_initials=avatar_initials,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": new_user.id, "email": new_user.email, "role": new_user.role})

    return LoginResponse(
        access_token=token,
        user=UserRead(
            id=new_user.id,
            name=new_user.name,
            email=new_user.email,
            role=new_user.role,
            avatar_initials=new_user.avatar_initials,
        ),
    )


@router.post("/login", response_model=LoginResponse, summary="Login endpoint")
def login(req: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Fallback for demo users that don't have hashed passwords, or check proper hash
    if req.password == "demo123" and user.hashed_password == "":
        pass  # Allow demo login for seeded users
    elif not user.hashed_password or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role, "exp": int(time.time()) + 28800})

    return LoginResponse(
        access_token=token,
        user=UserRead(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            avatar_initials=user.avatar_initials,
        ),
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
