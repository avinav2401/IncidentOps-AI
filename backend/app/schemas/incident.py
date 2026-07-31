"""Incident-related Pydantic schemas."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class IncidentState(str, Enum):
    OPEN = "Open"
    INVESTIGATING = "Investigating"
    WAITING_APPROVAL = "Waiting Approval"
    EXECUTING = "Executing"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


class Severity(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


# ── Write schemas ──────────────────────────────────────────────────────


class IncidentCreate(BaseModel):
    title: str = Field(min_length=4, max_length=180)
    description: str = Field(min_length=8, max_length=4_000)
    service: str = Field(min_length=2, max_length=100)
    severity: Severity = Severity.P2
    status: IncidentState = IncidentState.OPEN
    owner: str | None = Field(default=None, max_length=120)
    source: str = Field(default="Manual", max_length=80)
    affected_users: int = Field(default=0, ge=0)
    tags: list[str] = Field(default_factory=list, max_length=12)


class IncidentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=4, max_length=180)
    description: str | None = Field(default=None, min_length=8, max_length=4_000)
    service: str | None = Field(default=None, min_length=2, max_length=100)
    severity: Severity | None = None
    status: IncidentState | None = None
    owner: str | None = Field(default=None, max_length=120)
    affected_users: int | None = Field(default=None, ge=0)
    tags: list[str] | None = Field(default=None, max_length=12)

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, value: Any) -> Any:
        if not isinstance(value, str):
            return value
        normalized = " ".join(value.replace("_", " ").split()).casefold()
        for state in IncidentState:
            if state.value.casefold() == normalized:
                return state.value
        return value


# ── Read schemas ───────────────────────────────────────────────────────


class IncidentRead(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: str
    incident_number: str
    title: str
    description: str
    service: str
    severity: Severity
    status: IncidentState
    owner: str | None = None
    source: str
    affected_users: int = 0
    tags: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None = None
    resolution_summary: str | None = None


class IncidentLogRead(BaseModel):
    id: str
    incident_id: str
    event_type: str
    message: str
    actor: str
    created_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class AuditLogRead(BaseModel):
    id: str
    entity_type: str
    entity_id: str
    action: str
    actor: str
    message: str
    created_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class AIRecommendationRead(BaseModel):
    id: str
    incident_id: str
    title: str
    rationale: str
    confidence: int = Field(ge=0, le=100)
    risk: str
    status: str
    proposed_actions: list[str] = Field(default_factory=list)
    evidence_chain: list[dict[str, Any]] = Field(default_factory=list)
    similar_incidents: list[str] = Field(default_factory=list)
    created_at: datetime
    approved_at: datetime | None = None
    approved_by: str | None = None


class IncidentDetail(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    incident: IncidentRead
    incident_logs: list[IncidentLogRead] = Field(default_factory=list)
    logs: list[IncidentLogRead] = Field(default_factory=list)
    audit_logs: list[AuditLogRead] = Field(default_factory=list)
    ai_recommendations: list[AIRecommendationRead] = Field(default_factory=list)


class IncidentListResponse(BaseModel):
    items: list[IncidentRead]
    # ``incidents`` is deliberately duplicated for lightweight dashboard clients.
    incidents: list[IncidentRead]
    total: int
    limit: int
    offset: int


# ── Action schemas ─────────────────────────────────────────────────────


class ApprovalRequest(BaseModel):
    recommendation_id: str | None = None
    decision: str = Field(default="approve", pattern="^(approve|reject)$")
    note: str | None = Field(default=None, max_length=1_000)
    actor: str = Field(default="Maya Chen", max_length=120)


class ResolutionRequest(BaseModel):
    summary: str = Field(
        default="Mitigation completed and service health has returned to normal.",
        min_length=8,
        max_length=4_000,
    )
    actor: str = Field(default="Maya Chen", max_length=120)

class CommentRequest(BaseModel):
    content: str = Field(min_length=1, max_length=4_000)
    actor: str = Field(default="Maya Chen", max_length=120)
