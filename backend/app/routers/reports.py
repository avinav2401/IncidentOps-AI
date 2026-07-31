from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.agents.report_agent import ReportAgent
from app.database import get_db
from app.models.incident import Incident

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/{incident_id}/json")
async def get_report_json(incident_id: str, db: Session = Depends(get_db)):
    """Generate and return the postmortem report as JSON."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return await ReportAgent.generate_report(db, incident)


@router.get("/{incident_id}/markdown", response_class=PlainTextResponse)
async def get_report_markdown(incident_id: str, db: Session = Depends(get_db)):
    """Generate and return the postmortem report as Markdown."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    report = await ReportAgent.generate_report(db, incident)

    md = f"""# Postmortem Report: {report["title"]}

**Incident ID:** {report["incident_id"]}
**Service:** {report["service"]}
**Severity:** {report["severity"]}
**Duration:** {report["duration"]}

## Root Cause Analysis
{report["root_cause"]}

## Resolution Action Taken
{report["action_taken"]}

## Metrics Summary
"""
    for m in report["metrics_summary"]:
        md += f"- {m}\n"

    md += "\n## Lessons Learned\n"
    for lesson in report["lessons_learned"]:
        md += f"- {lesson}\n"

    return md
