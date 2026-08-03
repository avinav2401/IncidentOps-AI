"""Service ORM model — represents a monitored service in a workspace."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Service(Base):
    __tablename__ = "services"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    owner_team: Mapped[str] = mapped_column(String(200), nullable=False, default="Unassigned")
    repository: Mapped[str] = mapped_column(String(300), nullable=True)
    language: Mapped[str] = mapped_column(String(60), nullable=True)
    environment: Mapped[str] = mapped_column(String(40), nullable=False, default="Production")
    critical_level: Mapped[str] = mapped_column(String(20), nullable=False, default="High")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="healthy", index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    dependencies: Mapped[str] = mapped_column(Text, nullable=False, default="[]")  # JSON string of service names
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(UTC),
    )

    def to_dict(self) -> dict:
        import json

        try:
            deps = json.loads(self.dependencies) if self.dependencies else []
        except Exception:
            deps = []

        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "name": self.name,
            "owner_team": self.owner_team,
            "repository": self.repository,
            "language": self.language,
            "environment": self.environment,
            "critical_level": self.critical_level,
            "status": self.status,
            "description": self.description,
            "dependencies": deps,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<Service {self.name!r} status={self.status!r}>"
