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
    from app.config import settings

    channel = settings.slack_channel or "#incidents-critical"
    message_text = f"✅ Incident Resolved\nService: {service}\nRoot Cause: {root_cause}\nResolution: {resolution}\nDuration: {duration}"

    if settings.slack_webhook_url or (settings.slack_bot_token and settings.slack_channel):
        try:
            from app.services.output_handlers.slack import SlackWebhookHandler

            handler = SlackWebhookHandler()
            await handler.post_result(
                {},
                message_text,
                success=True,
                agent_name="IncidentOps AI",
            )
        except Exception:
            pass

    msg = SlackMessage(
        id=f"slack_{_uid()}",
        incident_id=incident_id,
        channel=channel,
        message=message_text,
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

    import httpx

    from app.config import settings

    project_key = settings.jira_project_key or "INC"
    issue_key = f"{project_key}-{random.randint(1000, 9999)}"
    summary = f"Bug — {root_cause} | Priority: Critical | Assign: Backend Team"

    if settings.jira_base_url and settings.jira_email and settings.jira_api_token and settings.jira_project_key:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                auth = (settings.jira_email, settings.jira_api_token)
                payload = {
                    "fields": {
                        "project": {"key": settings.jira_project_key},
                        "summary": summary,
                        "description": f"Service: {service}\nRoot Cause: {root_cause}",
                        "issuetype": {"name": "Bug"},
                    }
                }
                resp = await client.post(
                    f"{settings.jira_base_url.rstrip('/')}/rest/api/2/issue",
                    json=payload,
                    auth=auth,
                )
                if resp.status_code == 201:
                    data = resp.json()
                    issue_key = data.get("key", issue_key)
        except Exception:
            pass

    sync = JiraSync(
        id=f"jira_sync_{_uid()}",
        incident_id=incident_id,
        issue_key=issue_key,
        status="synced",
        synced_at=_utcnow(),
        project_key=project_key,
        summary=summary,
    )
    db.add(sync)
    db.commit()
    return sync.to_dict()
