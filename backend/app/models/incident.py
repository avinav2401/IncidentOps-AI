"""Incident ORM model."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    incident_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    service: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(4), nullable=False, default="P2", index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="Open", index=True)
    owner: Mapped[str | None] = mapped_column(String(120), nullable=True)
    source: Mapped[str] = mapped_column(String(80), nullable=False, default="Manual")
    affected_users: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Tags stored as comma-separated string for SQLite compat; ARRAY for Postgres.
    tags_raw: Mapped[str] = mapped_column("tags", Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    @property
    def tags(self) -> list[str]:
        """Deserialize tags from the stored comma-separated string."""
        if not self.tags_raw:
            return []
        return [t.strip() for t in self.tags_raw.split(",") if t.strip()]

    @tags.setter
    def tags(self, value: list[str]) -> None:
        self.tags_raw = ",".join(value) if value else ""

    def to_dict(self) -> dict:
        """Convenience serializer for API responses."""
        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "incident_number": self.incident_number,
            "title": self.title,
            "description": self.description,
            "service": self.service,
            "severity": self.severity,
            "status": self.status,
            "owner": self.owner,
            "source": self.source,
            "affected_users": self.affected_users,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolution_summary": self.resolution_summary,
        }

    def __repr__(self) -> str:
        return f"<Incident {self.incident_number!r} status={self.status!r}>"
