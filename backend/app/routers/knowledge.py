from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.incident import Incident
from app.models.recommendation import AIRecommendation

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])


class IncidentKnowledge(BaseModel):
    id: str
    title: str
    service: str
    severity: str
    root_cause: str
    resolution: str
    date: str


class Runbook(BaseModel):
    id: str
    title: str
    service: str
    description: str
    steps: list[str]


from app.middleware.auth import get_current_user
from app.models.user import User

@router.get("/incidents", response_model=list[IncidentKnowledge])
def get_knowledge_incidents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Return resolved incidents with their root cause and resolution for the Knowledge Base."""
    resolved_incidents = db.query(Incident).filter(
        Incident.status == "Resolved",
        Incident.workspace_id == current_user.workspace_id
    ).all()

    knowledge_list = []
    for inc in resolved_incidents:
        # Get the approved recommendation to find the resolution
        rec = db.query(AIRecommendation).filter(AIRecommendation.incident_id == inc.id, AIRecommendation.status == "approved").first()

        resolution_text = f"{rec.title}: {rec.rationale}" if rec else "Resolved manually by operator."
        root_cause_text = inc.resolution_summary or "Unknown root cause."

        knowledge_list.append(
            IncidentKnowledge(
                id=inc.id,
                title=inc.title,
                service=inc.service,
                severity=inc.severity,
                root_cause=root_cause_text,
                resolution=resolution_text,
                date=inc.updated_at.strftime("%b %d, %Y") if inc.updated_at else "",
            )
        )

    return knowledge_list


@router.get("/runbooks", response_model=list[Runbook])
def get_runbooks():
    """Return a static list of simulated runbooks."""
    return [
        Runbook(
            id="RB-001",
            title="Restart Service via Kubernetes",
            service="Any",
            description="Safely perform a rolling restart of a Kubernetes deployment.",
            steps=[
                "Check current pod status: kubectl get pods -l app=<service>",
                "Initiate rolling restart: kubectl rollout restart deployment/<service>",
                "Monitor rollout status: kubectl rollout status deployment/<service>",
                "Verify health endpoints return 200 OK.",
            ],
        ),
        Runbook(
            id="RB-002",
            title="Rollback Deployment",
            service="Any",
            description="Revert a Kubernetes deployment to the previous stable revision.",
            steps=[
                "Identify previous revision: kubectl rollout history deployment/<service>",
                "Execute rollback: kubectl rollout undo deployment/<service>",
                "Monitor rollback status: kubectl rollout status deployment/<service>",
                "Verify application logs for successful startup.",
            ],
        ),
        Runbook(
            id="RB-003",
            title="Database Connection Pool Exhaustion",
            service="Database",
            description="Steps to mitigate application crashes due to exhausted DB connection pools.",
            steps=[
                "Check active connections in Postgres: SELECT sum(numbackends) FROM pg_stat_database;",
                "Identify offending pods (usually high CPU/Memory).",
                "Scale down application pods temporarily to release connections.",
                "Increase max_connections if resource limits allow.",
                "Investigate application code for unclosed connections.",
            ],
        ),
        Runbook(
            id="RB-004",
            title="Scale Pods for Traffic Spike",
            service="Any",
            description="Manually scale a service to handle unexpected high traffic.",
            steps=[
                "Check current HPA limits: kubectl get hpa",
                'Increase maxReplicas if HPA is saturated: kubectl patch hpa <service> -p \'{"spec":{"maxReplicas": 20}}\'',
                "If no HPA, scale deployment manually: kubectl scale deployment/<service> --replicas=<new_value>",
                "Monitor node resources to ensure enough capacity exists.",
            ],
        ),
    ]
