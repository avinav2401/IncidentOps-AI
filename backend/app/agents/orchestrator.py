"""AI Agent Orchestrator with SSE streaming and structured logging.

Executes the multi-agent AI pipeline for incident investigation.
Publishes real-time SSE events so the frontend can display live progress.
Architecture inspired by IncidentFox's production agent pipeline.
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.agents.github_agent import fetch_recent_commits
from app.agents.log_analysis_agent import analyze_logs
from app.agents.recommendation_agent import propose_recommendation
from app.agents.root_cause_agent import determine_root_cause
from app.database import SessionLocal
from app.events import (
    agent_end_event,
    agent_start_event,
    approval_event,
    error_event,
    result_event,
    thought_event,
)
from app.models.agent_status import AgentStatus
from app.models.incident import Incident
from app.models.incident_log import IncidentLog
from app.models.recommendation import AIRecommendation
from app.routers.stream import close_stream, publish

logger = logging.getLogger(__name__)


# ── Structured JSON logging ──────────────────────────────────────────


def _structured_log(event: str, **fields: Any) -> None:
    """Structured JSON logging matching production convention."""
    try:
        payload = {"service": "orchestrator", "event": event, **fields}
        logger.info(json.dumps(payload, default=str))
    except Exception:
        logger.info("%s %s", event, fields)


# ── DB helpers ────────────────────────────────────────────────────────


def _update_agent_status(db: Session, name: str, status: str) -> None:
    """Update the heartbeat and status of an agent."""
    agent = db.query(AgentStatus).filter(AgentStatus.name == name).first()
    if agent:
        agent.status = status
        agent.last_heartbeat = datetime.now(UTC)
    else:
        db.add(
            AgentStatus(
                id=str(uuid.uuid4()),
                name=name,
                purpose=f"AI pipeline agent: {name}",
                status=status,
                last_heartbeat=datetime.now(UTC),
            )
        )
    db.commit()


def _add_incident_log(
    db: Session, incident_id: str, message: str, actor: str
) -> None:
    """Add a new log entry to the incident timeline."""
    log = IncidentLog(
        id=str(uuid.uuid4()),
        incident_id=incident_id,
        event_type="ai_analysis",
        message=message,
        actor=actor,
    )
    db.add(log)
    db.commit()


# ── Pipeline ──────────────────────────────────────────────────────────


async def run_pipeline(incident_id: str) -> None:
    """Execute the multi-agent AI pipeline with SSE streaming.

    This runs asynchronously so it does not block the API response.
    Each agent step publishes real-time SSE events for the frontend.
    """
    pipeline_start = time.monotonic()
    _structured_log("pipeline_started", incident_id=incident_id)

    publish(thought_event(incident_id, "Starting AI analysis pipeline..."))

    db = SessionLocal()
    try:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            _structured_log("pipeline_incident_not_found", incident_id=incident_id)
            publish(error_event(incident_id, "Incident not found."))
            return

        incident.status = "Investigating"
        db.commit()

        # ── Step 1: Log Analysis Agent ────────────────────────────────
        step_start = time.monotonic()
        agent_name = "Log Analysis Agent"

        publish(
            agent_start_event(
                incident_id,
                agent_name,
                description="Scanning recent logs for anomalies and error spikes.",
            )
        )
        _update_agent_status(db, agent_name, "Running")
        _structured_log("agent_step_started", agent=agent_name, incident_id=incident_id)

        log_summary = await analyze_logs(incident_id, incident.service)

        step_duration = time.monotonic() - step_start
        _add_incident_log(db, incident_id, log_summary, agent_name)
        _update_agent_status(db, agent_name, "Idle")
        publish(
            agent_end_event(
                incident_id,
                agent_name,
                summary=log_summary[:200],
                duration_seconds=step_duration,
            )
        )
        _structured_log(
            "agent_step_completed",
            agent=agent_name,
            incident_id=incident_id,
            duration_seconds=round(step_duration, 2),
        )

        # ── Step 2: GitHub Commit Agent ───────────────────────────────
        step_start = time.monotonic()
        agent_name = "GitHub Commit Agent"

        publish(
            agent_start_event(
                incident_id,
                agent_name,
                description="Fetching recent commits for the affected service.",
            )
        )
        _update_agent_status(db, agent_name, "Running")
        _structured_log("agent_step_started", agent=agent_name, incident_id=incident_id)

        commits = await fetch_recent_commits(incident.service)
        commits_str = "\n".join(commits)

        step_duration = time.monotonic() - step_start
        _add_incident_log(
            db, incident_id, f"Found recent commits:\n{commits_str}", agent_name
        )
        _update_agent_status(db, agent_name, "Idle")
        publish(
            agent_end_event(
                incident_id,
                agent_name,
                summary=f"Found {len(commits)} recent commits.",
                duration_seconds=step_duration,
            )
        )
        _structured_log(
            "agent_step_completed",
            agent=agent_name,
            incident_id=incident_id,
            commit_count=len(commits),
            duration_seconds=round(step_duration, 2),
        )

        # ── Step 3: Root Cause Agent ──────────────────────────────────
        step_start = time.monotonic()
        agent_name = "Root Cause Agent"

        publish(
            agent_start_event(
                incident_id,
                agent_name,
                description="Synthesizing logs and commits to determine root cause.",
            )
        )
        _update_agent_status(db, agent_name, "Running")
        _structured_log("agent_step_started", agent=agent_name, incident_id=incident_id)

        root_cause = await determine_root_cause(log_summary, commits)

        step_duration = time.monotonic() - step_start
        _add_incident_log(
            db,
            incident_id,
            f"Hypothesis (Confidence {root_cause['confidence']}%): {root_cause['hypothesis']}",
            agent_name,
        )
        _update_agent_status(db, agent_name, "Idle")
        publish(
            agent_end_event(
                incident_id,
                agent_name,
                summary=f"Root cause identified with {root_cause['confidence']}% confidence.",
                duration_seconds=step_duration,
            )
        )
        _structured_log(
            "agent_step_completed",
            agent=agent_name,
            incident_id=incident_id,
            confidence=root_cause["confidence"],
            duration_seconds=round(step_duration, 2),
        )

        # ── Step 4: Recommendation Agent ──────────────────────────────
        step_start = time.monotonic()
        agent_name = "Recommendation Agent"

        publish(
            agent_start_event(
                incident_id,
                agent_name,
                description="Proposing a remediation plan based on root cause analysis.",
            )
        )
        _update_agent_status(db, agent_name, "Running")
        _structured_log("agent_step_started", agent=agent_name, incident_id=incident_id)

        recommendation_data = await propose_recommendation(root_cause)

        rec_id = str(uuid.uuid4())
        rec = AIRecommendation(
            id=rec_id,
            incident_id=incident_id,
            title=recommendation_data["title"],
            rationale=recommendation_data["rationale"],
            confidence=root_cause["confidence"],
            risk=recommendation_data["risk_level"],
            status="pending_approval",
        )
        rec.proposed_actions = recommendation_data["proposed_actions"]
        db.add(rec)

        step_duration = time.monotonic() - step_start
        _add_incident_log(
            db,
            incident_id,
            f"Proposed Fix: {recommendation_data['title']} (Risk: {recommendation_data['risk_level']})",
            agent_name,
        )
        _update_agent_status(db, agent_name, "Idle")
        publish(
            agent_end_event(
                incident_id,
                agent_name,
                summary=f"Proposed: {recommendation_data['title']}",
                duration_seconds=step_duration,
            )
        )
        _structured_log(
            "agent_step_completed",
            agent=agent_name,
            incident_id=incident_id,
            recommendation=recommendation_data["title"],
            risk=recommendation_data["risk_level"],
            duration_seconds=round(step_duration, 2),
        )

        # ── Pipeline complete ─────────────────────────────────────────
        incident.status = "Waiting Approval"
        db.commit()

        total_duration = time.monotonic() - pipeline_start

        # Send approval event so the frontend can display the recommendation
        publish(
            approval_event(
                incident_id,
                recommendation_id=rec_id,
                title=recommendation_data["title"],
                rationale=recommendation_data["rationale"],
                risk=recommendation_data["risk_level"],
                proposed_actions=recommendation_data["proposed_actions"],
            )
        )

        # Send final result event
        publish(
            result_event(
                incident_id,
                text=f"AI analysis complete. Root cause: {root_cause['hypothesis']}",
                success=True,
                total_duration_seconds=total_duration,
                recommendation_id=rec_id,
            )
        )

        _structured_log(
            "pipeline_completed",
            incident_id=incident_id,
            total_duration_seconds=round(total_duration, 2),
            recommendation_id=rec_id,
            confidence=root_cause["confidence"],
        )

    except Exception as e:
        total_duration = time.monotonic() - pipeline_start
        _structured_log(
            "pipeline_failed",
            incident_id=incident_id,
            error=str(e),
            total_duration_seconds=round(total_duration, 2),
        )
        logger.exception("Error running AI pipeline for incident %s: %s", incident_id, e)

        publish(error_event(incident_id, f"Pipeline failed: {e}"))

        # Attempt to set status back on failure
        try:
            incident = (
                db.query(Incident).filter(Incident.id == incident_id).first()
            )
            if incident:
                incident.status = "Open"
                _add_incident_log(
                    db, incident_id, f"AI Analysis failed: {e}", "Orchestrator"
                )
                db.commit()
        except Exception:
            pass

    finally:
        db.close()
        close_stream(incident_id)
