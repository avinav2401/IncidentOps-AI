"""Authentication service — JWT verification."""

from __future__ import annotations

from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User


def decode_access_token(token: str) -> dict | None:
    """Decode and verify a Supabase JWT. Returns the claims dict or ``None``."""
    try:
        # Supabase uses HS256 and validates the token using the SUPABASE_JWT_SECRET
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"verify_aud": False},
        )
        return payload
    except JWTError:
        return None


def get_user_by_id(db: Session, user_id: str) -> User | None:
    """Fetch a user by primary key."""
    return db.query(User).filter(User.id == user_id).first()
