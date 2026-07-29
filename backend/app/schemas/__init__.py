"""Schema package — split for maintainability but re-exported for
backward compatibility with ``from app.schemas import ...``."""

from app.schemas.analytics import AnalyticsOverview
from app.schemas.auth import LoginRequest, LoginResponse, UserRead
from app.schemas.incident import (
    AIRecommendationRead,
    ApprovalRequest,
    AuditLogRead,
    IncidentCreate,
    IncidentDetail,
    IncidentListResponse,
    IncidentLogRead,
    IncidentRead,
    IncidentUpdate,
    ResolutionRequest,
)
from app.schemas.integrations import IntegrationTestRequest

# Legacy aliases so existing test_api.py continues to work.
User = UserRead
IncidentLog = IncidentLogRead
AuditLog = AuditLogRead
AIRecommendation = AIRecommendationRead

__all__ = [
    "LoginRequest",
    "LoginResponse",
    "User",
    "UserRead",
    "IncidentCreate",
    "IncidentUpdate",
    "IncidentRead",
    "IncidentDetail",
    "IncidentListResponse",
    "IncidentLog",
    "IncidentLogRead",
    "AuditLog",
    "AuditLogRead",
    "AIRecommendation",
    "AIRecommendationRead",
    "ApprovalRequest",
    "ResolutionRequest",
    "IntegrationTestRequest",
    "AnalyticsOverview",
]
