"""Integration test router (Slack / Jira safe adapters)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.audit_log import AuditLog
from app.models.jira_sync import JiraSync
from app.models.slack_message import SlackMessage
from app.models.user import User
from app.schemas.integrations import IntegrationTestRequest

router = APIRouter(tags=["Integrations"])


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _uid() -> str:
    return uuid4().hex[:12]


@router.post("/slack/test", summary="Test Slack integration")
def test_slack(
    payload: IntegrationTestRequest,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> dict[str, Any]:
    msg = SlackMessage(
        id=f"slack_{_uid()}",
        incident_id=None,
        channel=payload.channel or "#incidentops-test",
        message=payload.message or "IncidentOps AI Slack connection test succeeded.",
        sent_at=_utcnow(),
        status="delivered",
    )
    db.add(msg)
    audit = AuditLog(
        id=f"audit_{_uid()}",
        entity_type="integration",
        entity_id=msg.id,
        action="slack.tested",
        actor=payload.actor,
        message=f"Sent Slack test message to {msg.channel}.",
        created_at=_utcnow(),
    )
    db.add(audit)
    db.commit()
    return {
        "ok": True,
        "connected": True,
        "message": "Slack test message delivered.",
        "slack_message": msg.to_dict(),
    }


@router.post("/jira/test", summary="Test Jira integration")
def test_jira(
    payload: IntegrationTestRequest,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> dict[str, Any]:
    project = (payload.project_key or "OPS").upper()
    count = db.query(JiraSync).count()
    sync = JiraSync(
        id=f"jira_sync_{_uid()}",
        incident_id=None,
        issue_key=f"{project}-{180 + count + 1}",
        status="synced",
        synced_at=_utcnow(),
        project_key=project,
        summary=payload.message or "IncidentOps AI Jira connection test",
    )
    db.add(sync)
    audit = AuditLog(
        id=f"audit_{_uid()}",
        entity_type="integration",
        entity_id=sync.id,
        action="jira.tested",
        actor=payload.actor,
        message=f"Created Jira test issue {sync.issue_key}.",
        created_at=_utcnow(),
    )
    db.add(audit)
    db.commit()
    return {
        "ok": True,
        "connected": True,
        "message": "Jira test issue created.",
        "jira_sync": sync.to_dict(),
    }
