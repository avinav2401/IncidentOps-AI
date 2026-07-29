"""Agent status router."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.agent_status import AgentStatus
from app.models.user import User

router = APIRouter(tags=["Agents"])


@router.get("/agents/status", summary="AI agent fleet health")
def agent_status(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> dict[str, Any]:
    agents = db.query(AgentStatus).all()
    agent_dicts = [a.to_dict() for a in agents]
    healthy = sum(1 for a in agent_dicts if a["status"] == "healthy")
    return {
        "agents": agent_dicts,
        "total": len(agent_dicts),
        "healthy": healthy,
        "attention_required": len(agent_dicts) - healthy,
    }
