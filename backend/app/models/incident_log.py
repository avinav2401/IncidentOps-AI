"""Incident log / timeline event ORM model."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class IncidentLog(Base):
    __tablename__ = "incident_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    incident_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(60), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    actor: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )
    # Metadata stored as JSON text for SQLite compat.
    metadata_raw: Mapped[str] = mapped_column("metadata", Text, nullable=False, default="{}")

    @property
    def metadata_dict(self) -> dict:
        try:
            return json.loads(self.metadata_raw) if self.metadata_raw else {}
        except json.JSONDecodeError:
            return {}

    @metadata_dict.setter
    def metadata_dict(self, value: dict) -> None:
        self.metadata_raw = json.dumps(value) if value else "{}"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "event_type": self.event_type,
            "message": self.message,
            "actor": self.actor,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "metadata": self.metadata_dict,
        }

    def __repr__(self) -> str:
        return f"<IncidentLog {self.event_type!r} incident={self.incident_id!r}>"
