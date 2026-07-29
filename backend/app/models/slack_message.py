"""Slack message ORM model."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SlackMessage(Base):
    __tablename__ = "slack_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    incident_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True, index=True
    )
    channel: Mapped[str] = mapped_column(String(100), nullable=False, default="#incidentops-test")
    message: Mapped[str] = mapped_column(Text, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(UTC),
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="delivered")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "channel": self.channel,
            "message": self.message,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "status": self.status,
        }

    def __repr__(self) -> str:
        return f"<SlackMessage channel={self.channel!r} status={self.status!r}>"
