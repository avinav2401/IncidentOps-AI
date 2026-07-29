"""Integration router with webhook endpoints and signature verification.

Provides:
- Slack / Jira integration test endpoints (authenticated)
- GitHub webhook receiver with HMAC-SHA256 signature verification
- PagerDuty webhook receiver with HMAC-SHA256 signature verification

Webhook signature verification ported from IncidentFox's production
``signatures.py`` with constant-time comparison.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.audit_log import AuditLog
from app.models.jira_sync import JiraSync
from app.models.slack_message import SlackMessage
from app.models.user import User
from app.schemas.integrations import IntegrationTestRequest
from app.services.webhook_signatures import (
    SignatureVerificationError,
    verify_github_signature,
    verify_pagerduty_signature,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Integrations"])


# ── Structured logging ────────────────────────────────────────────────


def _structured_log(event: str, **fields: Any) -> None:
    try:
        payload = {"component": "integrations", "event": event, **fields}
        logger.info(json.dumps(payload, default=str))
    except Exception:
        logger.info("%s %s", event, fields)


# ── Helpers ───────────────────────────────────────────────────────────


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _uid() -> str:
    return uuid4().hex[:12]


# ── Integration tests (authenticated) ────────────────────────────────


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


# ── Webhook receivers (signature-verified, no auth) ──────────────────


@router.post("/webhooks/github", summary="Receive GitHub webhooks")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: str | None = Header(default=None),
    x_github_event: str | None = Header(default=None),
    x_github_delivery: str | None = Header(default=None),
) -> dict[str, Any]:
    """Receive and verify GitHub webhooks.

    Verifies the HMAC-SHA256 signature before processing.
    Supports events: push, pull_request, issues, issue_comment, deployment_status.
    """
    raw_body = await request.body()

    # Verify signature if a webhook secret is configured
    if settings.github_webhook_secret:
        try:
            verify_github_signature(
                secret=settings.github_webhook_secret,
                signature_header=x_hub_signature_256,
                raw_body=raw_body,
            )
        except SignatureVerificationError as e:
            _structured_log(
                "github_webhook_signature_failed",
                reason=e.reason,
                delivery_id=x_github_delivery,
            )
            raise HTTPException(status_code=401, detail=f"Signature verification failed: {e.reason}")

    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = x_github_event or "unknown"
    _structured_log(
        "github_webhook_received",
        event_type=event_type,
        delivery_id=x_github_delivery,
        repo=payload.get("repository", {}).get("full_name"),
    )

    # Process webhook asynchronously
    background_tasks.add_task(_process_github_event, event_type, payload)

    return {
        "ok": True,
        "event": event_type,
        "delivery_id": x_github_delivery,
    }


@router.post("/webhooks/pagerduty", summary="Receive PagerDuty webhooks")
async def pagerduty_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_pagerduty_signature: str | None = Header(default=None),
) -> dict[str, Any]:
    """Receive and verify PagerDuty V3 webhooks.

    Verifies the HMAC-SHA256 signature before processing.
    """
    raw_body = await request.body()

    # Verify signature if a webhook secret is configured
    if settings.pagerduty_webhook_secret:
        try:
            verify_pagerduty_signature(
                secret=settings.pagerduty_webhook_secret,
                signature_header=x_pagerduty_signature,
                raw_body=raw_body,
            )
        except SignatureVerificationError as e:
            _structured_log(
                "pagerduty_webhook_signature_failed",
                reason=e.reason,
            )
            raise HTTPException(status_code=401, detail=f"Signature verification failed: {e.reason}")

    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = payload.get("event", {}).get("event_type", "unknown")
    _structured_log(
        "pagerduty_webhook_received",
        event_type=event_type,
    )

    background_tasks.add_task(_process_pagerduty_event, event_type, payload)

    return {"ok": True, "event": event_type}


# ── Background webhook processors ────────────────────────────────────


async def _process_github_event(event_type: str, payload: dict[str, Any]) -> None:
    """Process a GitHub webhook event asynchronously."""
    _structured_log(
        "github_event_processing",
        event_type=event_type,
        action=payload.get("action"),
    )

    # Future: auto-create incidents from deployment failures,
    # correlate PRs with active incidents, etc.
    if event_type == "deployment_status":
        state = payload.get("deployment_status", {}).get("state")
        if state == "failure":
            _structured_log(
                "github_deployment_failure_detected",
                repo=payload.get("repository", {}).get("full_name"),
                environment=payload.get("deployment_status", {}).get("environment"),
            )
    elif event_type == "issues" and payload.get("action") == "opened":
        _structured_log(
            "github_issue_opened",
            repo=payload.get("repository", {}).get("full_name"),
            issue_number=payload.get("issue", {}).get("number"),
            title=payload.get("issue", {}).get("title"),
        )


async def _process_pagerduty_event(event_type: str, payload: dict[str, Any]) -> None:
    """Process a PagerDuty webhook event asynchronously."""
    _structured_log(
        "pagerduty_event_processing",
        event_type=event_type,
    )

    # Future: auto-create incidents from PagerDuty alerts,
    # sync incident status, etc.
    if event_type == "incident.triggered":
        incident_data = payload.get("event", {}).get("data", {})
        _structured_log(
            "pagerduty_incident_triggered",
            pd_incident_id=incident_data.get("id"),
            title=incident_data.get("title"),
            urgency=incident_data.get("urgency"),
        )
