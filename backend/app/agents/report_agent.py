from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.models.incident_log import IncidentLog
from app.models.recommendation import AIRecommendation


class ReportAgent:
    """Generates comprehensive postmortem reports for resolved incidents."""

    @staticmethod
    async def generate_report(db: Session, incident: Incident) -> dict:
        """Collects all incident data and uses the LLM to generate a 'Lessons Learned' section."""

        # Collect data
        recommendation = (
            db.query(AIRecommendation).filter(AIRecommendation.incident_id == incident.id, AIRecommendation.status == "approved").first()
        )

        logs = db.query(IncidentLog).filter(IncidentLog.incident_id == incident.id).all()

        action_taken = recommendation.title if recommendation else "Manual resolution"
        root_cause = incident.resolution_summary or "Unknown"

        # Get prevention suggestions from Knowledge Agent
        from app.agents.knowledge_agent import get_prevention_suggestions

        lessons = await get_prevention_suggestions(incident.service, root_cause)

        # Calculate duration if possible
        duration = "Unknown"
        if incident.created_at and incident.updated_at:
            delta = incident.updated_at - incident.created_at
            minutes = delta.total_seconds() / 60
            duration = f"{int(minutes)} minutes"

        return {
            "incident_id": incident.id,
            "title": incident.title,
            "service": incident.service,
            "severity": incident.severity,
            "duration": duration,
            "root_cause": root_cause,
            "action_taken": action_taken,
            "metrics_summary": [f"{log.event_type}: {log.message}" for log in logs[:3]],  # Using logs instead of metrics as fallback
            "lessons_learned": lessons,
        }
