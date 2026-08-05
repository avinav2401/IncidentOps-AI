"""JWT authentication and role-based access control middleware.

Usage in routers::

    from app.middleware.auth import get_current_user, require_role

    @router.get("/protected")
    def protected(user = Depends(get_current_user)):
        ...

    @router.post("/admin-only")
    def admin_only(user = Depends(require_role("admin"))):
        ...

In **demo mode** (``DEMO_MODE=true``), the middleware also accepts the
legacy base64 demo tokens produced by the previous implementation so the
UI can work without a real login flow during development.
"""

from __future__ import annotations

import base64
from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.services.auth_service import decode_access_token

_bearer = HTTPBearer(auto_error=False)


def _try_demo_token(token: str, db: Session) -> User | None:
    """Attempt to decode the old-style base64 demo token.

    Format: ``incidentops-demo:<user_id>:<timestamp>`` (URL-safe base64,
    padding may be stripped).
    """
    if not settings.demo_mode:
        return None
    try:
        padded = token + "=" * (4 - len(token) % 4)
        decoded = base64.urlsafe_b64decode(padded).decode("utf-8")
        if not decoded.startswith("incidentops-demo:"):
            return None
        parts = decoded.split(":")
        user_id = parts[1]
        return db.query(User).filter(User.id == user_id).first()
    except Exception:
        return None


async def get_current_user(
    token_query: str | None = None,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the current user from the ``Authorization: Bearer <token>``
    header or ``?token=`` query parameter (for SSE). In demo mode,
    requests without a token are served as the default incident commander."""

    token = token_query
    if credentials and credentials.credentials:
        token = credentials.credentials

    if token:

        # Try real JWT first.
        payload = decode_access_token(token)
        if payload:
            user = db.query(User).filter(User.id == payload.get("sub")).first()
            if user:
                return user

        # Fallback: legacy demo token.
        demo_user = _try_demo_token(token, db)
        if demo_user:
            return demo_user

    # In demo mode, allow unauthenticated requests as the default user.
    if settings.demo_mode:
        default = db.query(User).filter(User.role == "incident_commander").first()
        if default:
            return default

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid authentication token.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def require_role(*allowed_roles: str) -> Callable:
    """Return a FastAPI dependency that ensures the user has one of the
    specified roles.

    Example::

        @router.post("/admin")
        def admin(user = Depends(require_role("admin", "incident_commander"))):
            ...
    """

    async def _check(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role}' is not authorized for this action.",
            )
        return user

    return _check
