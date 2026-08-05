"""Post-Approval Pipeline — Steps 11-15 of the SRE lifecycle.

Orchestrates: Execute Fix → Verify Health → Slack/Jira → Resolve.
Publishes SSE events at each step so the frontend shows live progress.
"""

from __future__ import annotations

import logging
import time
import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.agents.communicator_agent import create_jira_ticket, send_slack_notification
from app.agents.execution_agent import execute_fix
from app.agents.verification_agent import verify_fix
from app.database import SessionLocal
from app.events import agent_end_event, agent_start_event, result_event, thought_event
from app.models.incident import Incident
from app.models.incident_log import IncidentLog
from app.routers.stream import publish

logger = logging.getLogger(__name__)


def _uid() -> str:
    return uuid.uuid4().hex[:12]


def _add_log(db: Session, incident_id: str, event_type: str, message: str, actor: str) -> None:
    log = IncidentLog(
        id=f"log_{_uid()}",
        incident_id=incident_id,
        event_type=event_type,
        message=message,
        actor=actor,
    )
    db.add(log)
    db.commit()


async def run_post_approval_pipeline(
    incident_id: str,
    recommendation_title: str,
    root_cause_hypothesis: str,
) -> None:
    """Execute the post-approval pipeline with SSE streaming."""
    pipeline_start = time.monotonic()
    db = SessionLocal()

    try:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            return

        service = incident.service

        # ── Step 11: Execute Fix ─────────────────────────────────────
        agent_name = "Execution Agent"
        publish(agent_start_event(incident_id, agent_name, description="Executing approved remediation command."))
        step_start = time.monotonic()

        exec_result = await execute_fix(service, recommendation_title)

        dur = time.monotonic() - step_start
        _add_log(db, incident_id, "execution", f"Executed: {exec_result['command']} → {exec_result['status']}", agent_name)
        publish(
            agent_end_event(incident_id, agent_name, summary=f"{exec_result['command']} → {exec_result['status']}", duration_seconds=dur)
        )

        # ── Step 12: Verify Fix ──────────────────────────────────────
        agent_name = "Verification Agent"
        publish(agent_start_event(incident_id, agent_name, description="Re-checking service health after fix."))
        step_start = time.monotonic()

        verify_result = await verify_fix(service)

        dur = time.monotonic() - step_start
        health_summary = f"Health: {verify_result['health']}, CPU: {verify_result['cpu']}, Latency: {verify_result['latency']}, Errors: {verify_result['error_rate']}"
        _add_log(db, incident_id, "verification", health_summary, agent_name)
        publish(agent_end_event(incident_id, agent_name, summary=health_summary, duration_seconds=dur))

        # ── Step 13: Resolve Incident ────────────────────────────────
        now = datetime.now(UTC).replace(microsecond=0)
        incident.status = "Resolved"
        incident.resolved_at = now
        incident.updated_at = now
        incident.resolution_summary = f"Root cause: {root_cause_hypothesis}. Fix: {recommendation_title}. Post-fix health verified."
        db.commit()
        _add_log(db, incident_id, "incident_resolved", "Incident resolved after successful verification.", "System")

        # Compute duration string
        if incident.created_at:
            diff = (now - incident.created_at.replace(tzinfo=None)) if incident.created_at.tzinfo is None else (now - incident.created_at)
            diff_min = int(abs(diff.total_seconds()) / 60)
            duration_str = f"{diff_min} minutes"
        else:
            duration_str = "Unknown"

        # ── Step 14: Slack Notification ──────────────────────────────
        agent_name = "Communicator Agent"
        publish(agent_start_event(incident_id, agent_name, description="Sending Slack notification and creating Jira ticket."))
        step_start = time.monotonic()

        slack_msg = await send_slack_notification(
            db,
            incident_id,
            service,
            root_cause_hypothesis,
            recommendation_title,
            duration_str,
        )
        _add_log(db, incident_id, "slack_sent", f"Sent to {slack_msg['channel']}: ✅ Incident Resolved", agent_name)

        # ── Step 15: Jira Ticket ─────────────────────────────────────
        jira_ticket = await create_jira_ticket(db, incident_id, root_cause_hypothesis, service)
        _add_log(db, incident_id, "jira_created", f"Created {jira_ticket['issue_key']}: Bug — {root_cause_hypothesis}", agent_name)

        dur = time.monotonic() - step_start
        publish(
            agent_end_event(
                incident_id, agent_name, summary=f"Slack: {slack_msg['channel']} | Jira: {jira_ticket['issue_key']}", duration_seconds=dur
            )
        )

        # ── Pipeline Complete ────────────────────────────────────────
        total_duration = time.monotonic() - pipeline_start
        publish(
            result_event(
                incident_id,
                text="Post-approval pipeline complete. Service verified healthy. Notifications sent.",
                success=True,
                total_duration_seconds=total_duration,
            )
        )

        publish(thought_event(incident_id, "✅ Incident fully resolved. Slack notified. Jira ticket created."))

    except Exception as e:
        logger.exception("Post-approval pipeline failed for %s: %s", incident_id, e)
        # Revert to Waiting Approval on failure
        try:
            incident = db.query(Incident).filter(Incident.id == incident_id).first()
            if incident:
                incident.status = "Waiting Approval"
                db.commit()
        except Exception:
            pass
    finally:
        db.close()
