"""Agent status ORM model."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AgentStatus(Base):
    __tablename__ = "agent_status"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    purpose: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="healthy")
    last_heartbeat: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(UTC),
    )
    active_incidents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    success_rate: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "purpose": self.purpose,
            "status": self.status,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "active_incidents": self.active_incidents,
            "success_rate": self.success_rate,
        }

    def __repr__(self) -> str:
        return f"<AgentStatus {self.name!r} status={self.status!r}>"
