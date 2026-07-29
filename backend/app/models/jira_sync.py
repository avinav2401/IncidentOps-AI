"""Jira sync ORM model."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class JiraSync(Base):
    __tablename__ = "jira_sync"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    incident_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True, index=True
    )
    issue_key: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="synced")
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(UTC),
    )
    project_key: Mapped[str] = mapped_column(String(20), nullable=False, default="OPS")
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "issue_key": self.issue_key,
            "status": self.status,
            "synced_at": self.synced_at.isoformat() if self.synced_at else None,
            "project_key": self.project_key,
            "summary": self.summary,
        }

    def __repr__(self) -> str:
        return f"<JiraSync {self.issue_key!r} status={self.status!r}>"
