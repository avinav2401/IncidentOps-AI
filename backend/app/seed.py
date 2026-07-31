"""Seed the database with realistic demo data.

Called once on startup when the ``users`` table is empty.  The seed data
is identical in spirit to the original ``store._seed_state()`` but targets
SQLAlchemy ORM models and uses bcrypt-hashed passwords.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.models.agent_status import AgentStatus
from app.models.audit_log import AuditLog
from app.models.incident import Incident
from app.models.incident_log import IncidentLog
from app.models.jira_sync import JiraSync
from app.models.recommendation import AIRecommendation
from app.models.slack_message import SlackMessage
from app.models.user import User


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def seed_database(db: Session) -> None:
    """Populate all tables with demo-quality data if the database is empty."""
    if db.query(User).first():
        return  # Already seeded.

    now = _utcnow()

    def minutes(n: int) -> datetime:
        return now - timedelta(minutes=n)

    def hours(n: int) -> datetime:
        return now - timedelta(hours=n)

    def days(n: int) -> datetime:
        return now - timedelta(days=n)

    # ── Users ──────────────────────────────────────────────────────────
    users = [
        User(id="usr_maya", name="Maya Chen", email="maya.chen@incidentops.dev", role="incident_commander", avatar_initials="MC"),
        User(id="usr_samir", name="Samir Patel", email="samir.patel@incidentops.dev", role="responder", avatar_initials="SP"),
        User(id="usr_lena", name="Lena Ortiz", email="lena.ortiz@incidentops.dev", role="admin", avatar_initials="LO"),
    ]
    db.add_all(users)

    # ── Incidents ──────────────────────────────────────────────────────
    incidents_data = [
        {
            "id": "inc_checkout_auth",
            "incident_number": "INC-2026-041",
            "title": "Checkout payment authorization failures",
            "description": "Card authorization errors rose above the alert threshold after the payments gateway rollout.",
            "service": "Checkout API",
            "severity": "P1",
            "status": "Investigating",
            "owner": "Maya Chen",
            "source": "Datadog",
            "affected_users": 1840,
            "tags": ["payments", "gateway", "customer-impact"],
            "created_at": minutes(52),
            "updated_at": minutes(4),
        },
        {
            "id": "inc_warehouse_lag",
            "incident_number": "INC-2026-040",
            "title": "Warehouse event queue lag",
            "description": "Fulfilment events are delayed while the primary queue consumer is saturated.",
            "service": "Fulfilment Events",
            "severity": "P2",
            "status": "Waiting Approval",
            "owner": "Samir Patel",
            "source": "PagerDuty",
            "affected_users": 326,
            "tags": ["queue", "fulfilment", "approval-required"],
            "created_at": hours(3),
            "updated_at": minutes(18),
        },
        {
            "id": "inc_mobile_push",
            "incident_number": "INC-2026-039",
            "title": "Mobile push delivery degradation",
            "description": "Android push delivery fell below the 99% SLO after a provider rate-limit event.",
            "service": "Notifications",
            "severity": "P3",
            "status": "Resolved",
            "owner": "Lena Ortiz",
            "source": "Sentry",
            "affected_users": 712,
            "tags": ["mobile", "notifications"],
            "created_at": days(1),
            "updated_at": hours(19),
            "resolved_at": hours(19),
            "resolution_summary": "Traffic was shifted to the secondary push provider and the backlog was replayed.",
        },
        {
            "id": "inc_catalog_cache",
            "incident_number": "INC-2026-038",
            "title": "Catalog cache invalidation delay",
            "description": "A short cache propagation delay showed stale inventory counts in a subset of regions.",
            "service": "Catalog API",
            "severity": "P4",
            "status": "Closed",
            "owner": "Lena Ortiz",
            "source": "New Relic",
            "affected_users": 94,
            "tags": ["catalog", "cache"],
            "created_at": days(4),
            "updated_at": days(3),
            "resolved_at": days(3),
            "resolution_summary": "Invalidation worker capacity was restored and customer-impact verification passed.",
        },
    ]
    for data in incidents_data:
        inc = Incident(
            id=data["id"],
            incident_number=data["incident_number"],
            title=data["title"],
            description=data["description"],
            service=data["service"],
            severity=data["severity"],
            status=data["status"],
            owner=data["owner"],
            source=data["source"],
            affected_users=data["affected_users"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            resolved_at=data.get("resolved_at"),
            resolution_summary=data.get("resolution_summary"),
        )
        inc.tags = data["tags"]  # type: ignore
        db.add(inc)

    # ── Incident Logs ──────────────────────────────────────────────────
    logs_data = [
        (
            "log_001",
            "inc_checkout_auth",
            "alert_received",
            "Datadog monitor detected a 12.8% authorization error rate.",
            "Datadog",
            minutes(52),
            {},
        ),
        ("log_002", "inc_checkout_auth", "ownership_assigned", "Maya Chen accepted incident command.", "IncidentOps AI", minutes(47), {}),
        (
            "log_003",
            "inc_checkout_auth",
            "ai_analysis",
            "AI correlation linked the error increase to the gateway rollout.",
            "Triage Agent",
            minutes(34),
            {"confidence": 92},
        ),
        ("log_004", "inc_checkout_auth", "status_changed", "Status changed to Investigating.", "Maya Chen", minutes(31), {}),
        (
            "log_005",
            "inc_warehouse_lag",
            "alert_received",
            "PagerDuty opened an alert for consumer lag above 18 minutes.",
            "PagerDuty",
            hours(3),
            {},
        ),
        (
            "log_006",
            "inc_warehouse_lag",
            "recommendation_created",
            "A safe queue-consumer scale-out plan is awaiting approval.",
            "Runbook Agent",
            minutes(18),
            {"recommendation_id": "rec_queue_scale"},
        ),
        (
            "log_007",
            "inc_mobile_push",
            "resolved",
            "Secondary provider traffic shift completed and delivery SLO recovered.",
            "Lena Ortiz",
            hours(19),
            {},
        ),
    ]
    for lid, iid, etype, msg, actor, ts, meta in logs_data:
        log = IncidentLog(id=lid, incident_id=iid, event_type=etype, message=msg, actor=actor, created_at=ts)
        log.metadata_dict = meta  # type: ignore
        db.add(log)

    # ── Audit Logs ─────────────────────────────────────────────────────
    audits_data = [
        (
            "audit_001",
            "incident",
            "inc_checkout_auth",
            "incident.created",
            "Datadog",
            "Incident INC-2026-041 was created from a Datadog alert.",
            minutes(52),
            {"severity": "P1"},
        ),
        (
            "audit_002",
            "recommendation",
            "rec_queue_scale",
            "recommendation.proposed",
            "Runbook Agent",
            "Queue-consumer scale-out plan was submitted for human approval.",
            minutes(18),
            {"incident_id": "inc_warehouse_lag"},
        ),
        (
            "audit_003",
            "incident",
            "inc_mobile_push",
            "incident.resolved",
            "Lena Ortiz",
            "Mobile push incident was marked resolved.",
            hours(19),
            {},
        ),
    ]
    for aid, etype, eid, action, actor, msg, ts, meta in audits_data:
        audit = AuditLog(id=aid, entity_type=etype, entity_id=eid, action=action, actor=actor, message=msg, created_at=ts)
        audit.metadata_dict = meta  # type: ignore
        db.add(audit)

    # ── AI Recommendations ─────────────────────────────────────────────
    recs_data = [
        {
            "id": "rec_checkout_roll_back",
            "incident_id": "inc_checkout_auth",
            "title": "Rollback gateway routing configuration",
            "rationale": "The configuration change is strongly correlated with failed authorizations and can be reversed without a deploy.",
            "confidence": 92,
            "risk": "Medium",
            "status": "ready_for_review",
            "proposed_actions": [
                "Shift 25% of traffic back to gateway-v3.",
                "Monitor authorization error rate for five minutes.",
                "Complete rollback if the rate remains above 2%.",
            ],
            "created_at": minutes(29),
        },
        {
            "id": "rec_queue_scale",
            "incident_id": "inc_warehouse_lag",
            "title": "Scale queue consumers from 6 to 12",
            "rationale": "Lag is isolated to a single consumer group; capacity is available in the worker pool.",
            "confidence": 87,
            "risk": "Low",
            "status": "pending_approval",
            "proposed_actions": [
                "Increase fulfilment-consumer replicas to 12.",
                "Verify queue lag decreases for ten minutes.",
                "Create a Jira follow-up for capacity planning.",
            ],
            "created_at": minutes(18),
        },
        {
            "id": "rec_push_failover",
            "incident_id": "inc_mobile_push",
            "title": "Fail over Android push traffic",
            "rationale": "Provider telemetry showed a sustained regional rate limit.",
            "confidence": 96,
            "risk": "Low",
            "status": "executed",
            "proposed_actions": ["Route Android push traffic to the secondary provider.", "Replay the delayed notification backlog."],
            "created_at": days(1),
            "approved_at": hours(20),
            "approved_by": "Lena Ortiz",
        },
    ]
    for data in recs_data:
        rec = AIRecommendation(
            id=data["id"],
            incident_id=data["incident_id"],
            title=data["title"],
            rationale=data["rationale"],
            confidence=data["confidence"],
            risk=data["risk"],
            status=data["status"],
            created_at=data["created_at"],
            approved_at=data.get("approved_at"),
            approved_by=data.get("approved_by"),
        )
        rec.proposed_actions = data["proposed_actions"]  # type: ignore
        db.add(rec)

    # ── Agent Status ───────────────────────────────────────────────────
    agents = [
        AgentStatus(
            id="agent_triage",
            name="Triage Agent",
            purpose="Classifies alerts and establishes incident context.",
            status="healthy",
            last_heartbeat=minutes(1),
            active_incidents=1,
            success_rate=98.4,
        ),
        AgentStatus(
            id="agent_correlation",
            name="Correlation Agent",
            purpose="Links signals, deployments, and related incidents.",
            status="working",
            last_heartbeat=minutes(1),
            active_incidents=2,
            success_rate=96.7,
        ),
        AgentStatus(
            id="agent_runbook",
            name="Runbook Agent",
            purpose="Proposes bounded, auditable remediation steps.",
            status="awaiting_approval",
            last_heartbeat=minutes(2),
            active_incidents=1,
            success_rate=94.8,
        ),
        AgentStatus(
            id="agent_comms",
            name="Comms Agent",
            purpose="Prepares stakeholder updates and handoff summaries.",
            status="healthy",
            last_heartbeat=minutes(1),
            active_incidents=0,
            success_rate=99.1,
        ),
    ]
    db.add_all(agents)

    # ── Jira Sync ──────────────────────────────────────────────────────
    db.add(
        JiraSync(
            id="jira_sync_001", incident_id="inc_mobile_push", issue_key="OPS-184", status="synced", synced_at=hours(18), project_key="OPS"
        )
    )

    # ── Slack Messages ─────────────────────────────────────────────────
    db.add(
        SlackMessage(
            id="slack_001",
            incident_id="inc_checkout_auth",
            channel="#inc-checkout-auth",
            message="Incident commander assigned; investigation is underway.",
            sent_at=minutes(43),
            status="delivered",
        )
    )

    db.commit()
