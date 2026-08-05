"""Authentication-related Pydantic schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class UserRead(BaseModel):
    """Public user representation (no password)."""

    id: str
    name: str
    email: str
    role: str
    avatar_initials: str


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=256)


class SignupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=6, max_length=256)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserRead


class TokenPayload(BaseModel):
    """Internal model for decoded JWT claims."""

    sub: str  # user id
    email: str
    role: str
    exp: int | None = None
