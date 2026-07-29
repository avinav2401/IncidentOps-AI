"""AI Agent Orchestrator."""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.agents.github_agent import fetch_recent_commits
from app.agents.log_analysis_agent import analyze_logs
from app.agents.recommendation_agent import propose_recommendation
from app.agents.root_cause_agent import determine_root_cause
from app.database import SessionLocal
from app.models.incident import Incident
from app.models.incident_log import IncidentLog
from app.models.recommendation import AIRecommendation
from app.models.agent_status import AgentStatus

logger = logging.getLogger(__name__)


def _update_agent_status(db: Session, name: str, status: str):
    """Update the heartbeat and status of an agent."""
    agent = db.query(AgentStatus).filter(AgentStatus.name == name).first()
    if agent:
        agent.status = status
        agent.last_heartbeat = datetime.now(timezone.utc)
    else:
        db.add(AgentStatus(
            id=str(uuid.uuid4()),
            name=name,
            purpose=f"Simulated {name}",
            status=status,
            last_heartbeat=datetime.now(timezone.utc)
        ))
    db.commit()


def _add_incident_log(db: Session, incident_id: str, message: str, actor: str):
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


async def run_pipeline(incident_id: str) -> None:
    """
    Executes the multi-agent AI pipeline for a given incident.
    This runs asynchronously so it does not block the API response.
    """
    logger.info("Starting AI pipeline for incident %s", incident_id)
    db = SessionLocal()
    try:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            logger.error("Incident %s not found for pipeline.", incident_id)
            return

        incident.status = "Investigating"
        db.commit()

        # 1. Log Analysis Agent
        _update_agent_status(db, "Log Analysis Agent", "Running")
        log_summary = await analyze_logs(incident_id, incident.service)
        _add_incident_log(db, incident_id, log_summary, "Log Analysis Agent")
        _update_agent_status(db, "Log Analysis Agent", "Idle")

        # 2. GitHub Commit Agent
        _update_agent_status(db, "GitHub Commit Agent", "Running")
        commits = await fetch_recent_commits(incident.service)
        commits_str = "\\n".join(commits)
        _add_incident_log(db, incident_id, f"Found recent commits:\\n{commits_str}", "GitHub Commit Agent")
        _update_agent_status(db, "GitHub Commit Agent", "Idle")

        # 3. Root Cause Agent
        _update_agent_status(db, "Root Cause Agent", "Running")
        root_cause = await determine_root_cause(log_summary, commits)
        _add_incident_log(
            db, 
            incident_id, 
            f"Hypothesis (Confidence {root_cause['confidence']}%): {root_cause['hypothesis']}", 
            "Root Cause Agent"
        )
        _update_agent_status(db, "Root Cause Agent", "Idle")

        # 4. Recommendation Agent
        _update_agent_status(db, "Recommendation Agent", "Running")
        recommendation_data = await propose_recommendation(root_cause)
        
        # Save the recommendation to the database
        rec = AIRecommendation(
            id=str(uuid.uuid4()),
            incident_id=incident_id,
            title=recommendation_data["title"],
            rationale=recommendation_data["rationale"],
            confidence=root_cause["confidence"],
            risk=recommendation_data["risk_level"],
            status="pending_approval",
        )
        rec.proposed_actions = recommendation_data["proposed_actions"]
        db.add(rec)
        
        _add_incident_log(
            db, 
            incident_id, 
            f"Proposed Fix: {recommendation_data['title']} (Risk: {recommendation_data['risk_level']})", 
            "Recommendation Agent"
        )
        _update_agent_status(db, "Recommendation Agent", "Idle")

        # Finish up
        incident.status = "Waiting Approval"
        db.commit()
        logger.info("AI pipeline completed for incident %s", incident_id)
        
    except Exception as e:
        logger.exception("Error running AI pipeline for incident %s: %s", incident_id, e)
        # Attempt to set status back on failure if incident exists
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if incident:
            incident.status = "Open"
            _add_incident_log(db, incident_id, f"AI Analysis failed: {e}", "Orchestrator")
            db.commit()
    finally:
        db.close()
