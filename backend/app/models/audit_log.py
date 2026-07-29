"""Audit log ORM model."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(60), nullable=False)
    actor: Mapped[str] = mapped_column(String(120), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )
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
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "action": self.action,
            "actor": self.actor,
            "message": self.message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "metadata": self.metadata_dict,
        }

    def __repr__(self) -> str:
        return f"<AuditLog {self.action!r} entity={self.entity_id!r}>"
