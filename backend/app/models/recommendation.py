"""AI recommendation ORM model."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    incident_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    risk: Mapped[str] = mapped_column(String(20), nullable=False, default="Low")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending_approval")
    # Proposed actions stored as JSON array text.
    proposed_actions_raw: Mapped[str] = mapped_column("proposed_actions", Text, nullable=False, default="[]")
    evidence_chain_raw: Mapped[str | None] = mapped_column("evidence_chain", Text, nullable=True)
    similar_incidents_raw: Mapped[str | None] = mapped_column("similar_incidents", Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(UTC),
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(120), nullable=True)

    @property
    def proposed_actions(self) -> list[str]:
        try:
            return json.loads(self.proposed_actions_raw) if self.proposed_actions_raw else []
        except json.JSONDecodeError:
            return []

    @proposed_actions.setter
    def proposed_actions(self, value: list[str]) -> None:
        self.proposed_actions_raw = json.dumps(value) if value else "[]"

    @property
    def evidence_chain(self) -> list[dict]:
        try:
            return json.loads(self.evidence_chain_raw) if self.evidence_chain_raw else []
        except json.JSONDecodeError:
            return []

    @evidence_chain.setter
    def evidence_chain(self, value: list[dict]) -> None:
        self.evidence_chain_raw = json.dumps(value) if value else "[]"

    @property
    def similar_incidents(self) -> list[str]:
        try:
            return json.loads(self.similar_incidents_raw) if self.similar_incidents_raw else []
        except json.JSONDecodeError:
            return []

    @similar_incidents.setter
    def similar_incidents(self, value: list[str]) -> None:
        self.similar_incidents_raw = json.dumps(value) if value else "[]"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "title": self.title,
            "rationale": self.rationale,
            "confidence": self.confidence,
            "risk": self.risk,
            "status": self.status,
            "proposed_actions": self.proposed_actions,
            "evidence_chain": self.evidence_chain,
            "similar_incidents": self.similar_incidents,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "approved_by": self.approved_by,
        }

    def __repr__(self) -> str:
        return f"<AIRecommendation {self.title!r} status={self.status!r}>"
