"""Communicator Agent — Slack & Jira integration.

Creates mock Slack messages and Jira tickets for resolved incidents,
saving them as real DB records so the frontend can display them.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.jira_sync import JiraSync
from app.models.slack_message import SlackMessage


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def _uid() -> str:
    return uuid.uuid4().hex[:12]


async def send_slack_notification(
    db: Session,
    incident_id: str,
    service: str,
    root_cause: str,
    resolution: str,
    duration: str,
) -> dict:
    """Create a Slack notification record for the resolved incident."""
    msg = SlackMessage(
        id=f"slack_{_uid()}",
        incident_id=incident_id,
        channel="#incidents-critical",
        message=(f"✅ Incident Resolved\nService: {service}\nRoot Cause: {root_cause}\nResolution: {resolution}\nDuration: {duration}"),
        sent_at=_utcnow(),
        status="delivered",
    )
    db.add(msg)
    db.commit()
    return msg.to_dict()


async def create_jira_ticket(
    db: Session,
    incident_id: str,
    root_cause: str,
    service: str,
) -> dict:
    """Create a Jira ticket record for the post-incident bug."""
    import random

    issue_id = random.randint(1000, 9999)
    sync = JiraSync(
        id=f"jira_sync_{_uid()}",
        incident_id=incident_id,
        issue_key=f"INC-{issue_id}",
        status="synced",
        synced_at=_utcnow(),
        project_key="INC",
        summary=f"Bug — {root_cause} | Priority: Critical | Assign: Backend Team",
    )
    db.add(sync)
    db.commit()
    return sync.to_dict()
