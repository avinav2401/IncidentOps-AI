from sqlalchemy.orm import Session

from app.agents.llm import call_llm
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

        action_taken = recommendation.action if recommendation else "Manual resolution"
        root_cause = incident.analysis or "Unknown"

        prompt = f"""
        You are an expert Site Reliability Engineer (SRE) writing a postmortem report.
        Based on the following incident details, generate a concise 'Lessons Learned' section
        with 3 bullet points outlining what we can learn to prevent this in the future.

        Incident: {incident.title}
        Service: {incident.service}
        Root Cause: {root_cause}
        Resolution Action: {action_taken}

        Format your response as a JSON array of strings.
        """

        # In a real system, we'd parse the JSON array from the LLM.
        # For the demo, if the LLM fails to return JSON, we fallback.
        try:
            llm_response = await call_llm(system_prompt=prompt, user_prompt="Generate lessons learned.")
            # Simple extraction if LLM adds markdown block
            if "[" in llm_response and "]" in llm_response:
                import json

                start = llm_response.find("[")
                end = llm_response.rfind("]") + 1
                lessons = json.loads(llm_response[start:end])
            else:
                lessons = [
                    "Improve monitoring alerts for this specific failure mode.",
                    "Update runbooks with the resolution steps taken.",
                    "Review capacity planning for the affected service.",
                ]
        except Exception:
            lessons = [
                "Improve monitoring alerts for this specific failure mode.",
                "Update runbooks with the resolution steps taken.",
                "Review capacity planning for the affected service.",
            ]

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
            "metrics_summary": [f"{log.level}: {log.message}" for log in logs[:3]],  # Using logs instead of metrics as fallback
            "lessons_learned": lessons,
        }
