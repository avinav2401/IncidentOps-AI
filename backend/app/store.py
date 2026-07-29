"""Small JSON-capable repository for the IncidentOps AI demonstration service.

The app intentionally has no infrastructure dependency: it starts with useful
data immediately, while setting ``INCIDENTOPS_DATA_FILE`` turns the same store
into a durable JSON-backed demo.  The store is guarded with an RLock so the
development server and test client can safely share it.
"""

from __future__ import annotations

import copy
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import RLock
from typing import Any
from uuid import uuid4

from .schemas import (
    AIRecommendation,
    ApprovalRequest,
    IncidentCreate,
    IncidentState,
    IncidentUpdate,
    ResolutionRequest,
)


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _timestamp(value: datetime) -> str:
    return value.isoformat()


def _seed_state() -> dict[str, Any]:
    """Return fresh, realistic demo data relative to the current time."""
    now = utcnow()
    minutes = lambda number: _timestamp(now - timedelta(minutes=number))
    hours = lambda number: _timestamp(now - timedelta(hours=number))
    days = lambda number: _timestamp(now - timedelta(days=number))

    incidents = [
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
            "resolved_at": None,
            "resolution_summary": None,
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
            "resolved_at": None,
            "resolution_summary": None,
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

    def event(
        event_id: str,
        incident_id: str,
        event_type: str,
        message: str,
        actor: str,
        occurred: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "id": event_id,
            "incident_id": incident_id,
            "event_type": event_type,
            "message": message,
            "actor": actor,
            "created_at": occurred,
            "metadata": metadata or {},
        }

    logs = [
        event("log_001", "inc_checkout_auth", "alert_received", "Datadog monitor detected a 12.8% authorization error rate.", "Datadog", minutes(52)),
        event("log_002", "inc_checkout_auth", "ownership_assigned", "Maya Chen accepted incident command.", "IncidentOps AI", minutes(47)),
        event("log_003", "inc_checkout_auth", "ai_analysis", "AI correlation linked the error increase to the gateway rollout.", "Triage Agent", minutes(34), {"confidence": 92}),
        event("log_004", "inc_checkout_auth", "status_changed", "Status changed to Investigating.", "Maya Chen", minutes(31)),
        event("log_005", "inc_warehouse_lag", "alert_received", "PagerDuty opened an alert for consumer lag above 18 minutes.", "PagerDuty", hours(3)),
        event("log_006", "inc_warehouse_lag", "recommendation_created", "A safe queue-consumer scale-out plan is awaiting approval.", "Runbook Agent", minutes(18), {"recommendation_id": "rec_queue_scale"}),
        event("log_007", "inc_mobile_push", "resolved", "Secondary provider traffic shift completed and delivery SLO recovered.", "Lena Ortiz", hours(19)),
    ]
    audits = [
        {
            "id": "audit_001",
            "entity_type": "incident",
            "entity_id": "inc_checkout_auth",
            "action": "incident.created",
            "actor": "Datadog",
            "message": "Incident INC-2026-041 was created from a Datadog alert.",
            "created_at": minutes(52),
            "metadata": {"severity": "P1"},
        },
        {
            "id": "audit_002",
            "entity_type": "recommendation",
            "entity_id": "rec_queue_scale",
            "action": "recommendation.proposed",
            "actor": "Runbook Agent",
            "message": "Queue-consumer scale-out plan was submitted for human approval.",
            "created_at": minutes(18),
            "metadata": {"incident_id": "inc_warehouse_lag"},
        },
        {
            "id": "audit_003",
            "entity_type": "incident",
            "entity_id": "inc_mobile_push",
            "action": "incident.resolved",
            "actor": "Lena Ortiz",
            "message": "Mobile push incident was marked resolved.",
            "created_at": hours(19),
            "metadata": {},
        },
    ]
    recommendations = [
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
            "approved_at": None,
            "approved_by": None,
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
            "approved_at": None,
            "approved_by": None,
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

    return {
        "version": 1,
        "users": [
            {"id": "usr_maya", "name": "Maya Chen", "email": "maya.chen@incidentops.dev", "role": "incident_commander", "avatar_initials": "MC", "password": "demo123"},
            {"id": "usr_samir", "name": "Samir Patel", "email": "samir.patel@incidentops.dev", "role": "responder", "avatar_initials": "SP", "password": "demo123"},
            {"id": "usr_lena", "name": "Lena Ortiz", "email": "lena.ortiz@incidentops.dev", "role": "admin", "avatar_initials": "LO", "password": "demo123"},
        ],
        "incidents": incidents,
        "incident_logs": logs,
        "audit_logs": audits,
        "ai_recommendations": recommendations,
        "agent_status": [
            {"id": "agent_triage", "name": "Triage Agent", "purpose": "Classifies alerts and establishes incident context.", "status": "healthy", "last_heartbeat": minutes(1), "active_incidents": 1, "success_rate": 98.4},
            {"id": "agent_correlation", "name": "Correlation Agent", "purpose": "Links signals, deployments, and related incidents.", "status": "working", "last_heartbeat": minutes(1), "active_incidents": 2, "success_rate": 96.7},
            {"id": "agent_runbook", "name": "Runbook Agent", "purpose": "Proposes bounded, auditable remediation steps.", "status": "awaiting_approval", "last_heartbeat": minutes(2), "active_incidents": 1, "success_rate": 94.8},
            {"id": "agent_comms", "name": "Comms Agent", "purpose": "Prepares stakeholder updates and handoff summaries.", "status": "healthy", "last_heartbeat": minutes(1), "active_incidents": 0, "success_rate": 99.1},
        ],
        "jira_sync": [
            {"id": "jira_sync_001", "incident_id": "inc_mobile_push", "issue_key": "OPS-184", "status": "synced", "synced_at": hours(18), "project_key": "OPS"}
        ],
        "slack_messages": [
            {"id": "slack_001", "incident_id": "inc_checkout_auth", "channel": "#inc-checkout-auth", "message": "Incident commander assigned; investigation is underway.", "sent_at": minutes(43), "status": "delivered"}
        ],
    }


class DemoStore:
    """Repository that can persist its state to a JSON file when configured."""

    def __init__(self, data_file: str | Path | None = None) -> None:
        self._lock = RLock()
        self._data_file = Path(data_file) if data_file else None
        self._state = self._load_or_seed()

    @classmethod
    def from_environment(cls) -> "DemoStore":
        return cls(os.getenv("INCIDENTOPS_DATA_FILE") or None)

    def _load_or_seed(self) -> dict[str, Any]:
        if self._data_file and self._data_file.exists():
            try:
                loaded = json.loads(self._data_file.read_text(encoding="utf-8"))
                if isinstance(loaded, dict) and loaded.get("version") == 1:
                    return loaded
            except (OSError, json.JSONDecodeError):
                # A demo service should remain usable if its optional state file is damaged.
                pass
        state = _seed_state()
        if self._data_file:
            self._persist(state)
        return state

    def _persist(self, state: dict[str, Any] | None = None) -> None:
        if not self._data_file:
            return
        payload = state if state is not None else self._state
        self._data_file.parent.mkdir(parents=True, exist_ok=True)
        temporary = self._data_file.with_suffix(f"{self._data_file.suffix}.tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        temporary.replace(self._data_file)

    @staticmethod
    def _copy(value: Any) -> Any:
        return copy.deepcopy(value)

    def _find_incident(self, incident_id: str) -> dict[str, Any] | None:
        return next((item for item in self._state["incidents"] if item["id"] == incident_id), None)

    def _add_log(
        self,
        incident_id: str,
        event_type: str,
        message: str,
        actor: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        item = {
            "id": f"log_{uuid4().hex[:12]}",
            "incident_id": incident_id,
            "event_type": event_type,
            "message": message,
            "actor": actor,
            "created_at": _timestamp(utcnow()),
            "metadata": metadata or {},
        }
        self._state["incident_logs"].append(item)
        return item

    def _add_audit(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        actor: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        item = {
            "id": f"audit_{uuid4().hex[:12]}",
            "entity_type": entity_type,
            "entity_id": entity_id,
            "action": action,
            "actor": actor,
            "message": message,
            "created_at": _timestamp(utcnow()),
            "metadata": metadata or {},
        }
        self._state["audit_logs"].append(item)
        return item

    def authenticate(self, email: str, password: str) -> dict[str, Any] | None:
        with self._lock:
            user = next((item for item in self._state["users"] if item["email"].casefold() == email.casefold()), None)
            if not user or user["password"] != password:
                return None
            safe_user = {key: value for key, value in user.items() if key != "password"}
            return self._copy(safe_user)

    def list_incidents(
        self,
        status: str | None = None,
        severity: str | None = None,
        service: str | None = None,
        query: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        with self._lock:
            rows = self._state["incidents"]
            if status:
                rows = [row for row in rows if row["status"].casefold() == status.casefold()]
            if severity:
                rows = [row for row in rows if row["severity"].casefold() == severity.casefold()]
            if service:
                rows = [row for row in rows if row["service"].casefold() == service.casefold()]
            if query:
                needle = query.casefold()
                rows = [
                    row
                    for row in rows
                    if needle in row["title"].casefold()
                    or needle in row["description"].casefold()
                    or any(needle in tag.casefold() for tag in row["tags"])
                ]
            rows = sorted(rows, key=lambda row: row["created_at"], reverse=True)
            return self._copy(rows[offset : offset + limit]), len(rows)

    def get_incident(self, incident_id: str) -> dict[str, Any] | None:
        with self._lock:
            row = self._find_incident(incident_id)
            return self._copy(row) if row else None

    def get_detail(self, incident_id: str) -> dict[str, Any] | None:
        with self._lock:
            incident = self._find_incident(incident_id)
            if not incident:
                return None
            logs = [item for item in self._state["incident_logs"] if item["incident_id"] == incident_id]
            audits = [item for item in self._state["audit_logs"] if item["entity_id"] == incident_id or item["metadata"].get("incident_id") == incident_id]
            recommendations = [item for item in self._state["ai_recommendations"] if item["incident_id"] == incident_id]
            return self._copy(
                {
                    **incident,
                    "incident": incident,
                    "incident_logs": sorted(logs, key=lambda item: item["created_at"]),
                    "logs": sorted(logs, key=lambda item: item["created_at"]),
                    "audit_logs": sorted(audits, key=lambda item: item["created_at"], reverse=True),
                    "ai_recommendations": sorted(recommendations, key=lambda item: item["created_at"], reverse=True),
                }
            )

    def create_incident(self, request: IncidentCreate, actor: str = "Maya Chen") -> dict[str, Any]:
        with self._lock:
            now = _timestamp(utcnow())
            next_number = len(self._state["incidents"]) + 38
            incident = {
                "id": f"inc_{uuid4().hex[:12]}",
                "incident_number": f"INC-{utcnow().year}-{next_number:03d}",
                **request.model_dump(mode="json"),
                "created_at": now,
                "updated_at": now,
                "resolved_at": now if request.status in {IncidentState.RESOLVED, IncidentState.CLOSED} else None,
                "resolution_summary": None,
            }
            self._state["incidents"].append(incident)
            self._add_log(incident["id"], "incident_created", f"{incident['incident_number']} was created.", actor, {"source": incident["source"]})
            self._add_audit("incident", incident["id"], "incident.created", actor, f"Created {incident['incident_number']}.", {"severity": incident["severity"]})
            self._persist()
            return self._copy(incident)

    def update_incident(self, incident_id: str, request: IncidentUpdate, actor: str = "Maya Chen") -> dict[str, Any] | None:
        with self._lock:
            incident = self._find_incident(incident_id)
            if not incident:
                return None
            changes = request.model_dump(exclude_unset=True, mode="json")
            if not changes:
                return self._copy(incident)
            previous_status = incident["status"]
            incident.update(changes)
            incident["updated_at"] = _timestamp(utcnow())
            if changes.get("status") in {IncidentState.RESOLVED.value, IncidentState.CLOSED.value} and not incident.get("resolved_at"):
                incident["resolved_at"] = incident["updated_at"]
            self._add_log(incident_id, "incident_updated", "Incident fields were updated.", actor, {"fields": sorted(changes)})
            if "status" in changes and changes["status"] != previous_status:
                self._add_log(incident_id, "status_changed", f"Status changed from {previous_status} to {changes['status']}.", actor)
            self._add_audit("incident", incident_id, "incident.updated", actor, f"Updated {incident['incident_number']}.", {"fields": sorted(changes)})
            self._persist()
            return self._copy(incident)

    def approve(self, incident_id: str, request: ApprovalRequest) -> tuple[dict[str, Any], dict[str, Any]] | None:
        with self._lock:
            incident = self._find_incident(incident_id)
            if not incident:
                return None
            recommendations = [item for item in self._state["ai_recommendations"] if item["incident_id"] == incident_id]
            recommendation = next((item for item in recommendations if item["id"] == request.recommendation_id), None) if request.recommendation_id else next((item for item in recommendations if item["status"] in {"pending_approval", "ready_for_review"}), None)
            if not recommendation:
                recommendation = {
                    "id": f"rec_{uuid4().hex[:12]}",
                    "incident_id": incident_id,
                    "title": "Operator approval recorded",
                    "rationale": "Approval was recorded without a linked AI recommendation.",
                    "confidence": 100,
                    "risk": "Low",
                    "status": "pending_approval",
                    "proposed_actions": [],
                    "created_at": _timestamp(utcnow()),
                    "approved_at": None,
                    "approved_by": None,
                }
                self._state["ai_recommendations"].append(recommendation)
            now = _timestamp(utcnow())
            if request.decision == "approve":
                recommendation["status"] = "approved"
                recommendation["approved_at"] = now
                recommendation["approved_by"] = request.actor
                old_status = incident["status"]
                if incident["status"] == IncidentState.WAITING_APPROVAL.value:
                    incident["status"] = IncidentState.INVESTIGATING.value
                message = f"Approved recommendation: {recommendation['title']}."
                action = "recommendation.approved"
            else:
                recommendation["status"] = "rejected"
                old_status = incident["status"]
                if incident["status"] == IncidentState.WAITING_APPROVAL.value:
                    incident["status"] = IncidentState.INVESTIGATING.value
                message = f"Rejected recommendation: {recommendation['title']}."
                action = "recommendation.rejected"
            incident["updated_at"] = now
            metadata = {"recommendation_id": recommendation["id"], "decision": request.decision}
            if request.note:
                metadata["note"] = request.note
            self._add_log(incident_id, "approval_recorded", message, request.actor, metadata)
            if incident["status"] != old_status:
                self._add_log(incident_id, "status_changed", f"Status changed from {old_status} to {incident['status']}.", request.actor)
            self._add_audit("recommendation", recommendation["id"], action, request.actor, message, {"incident_id": incident_id, **metadata})
            self._persist()
            return self._copy(incident), self._copy(recommendation)

    def resolve(self, incident_id: str, request: ResolutionRequest) -> dict[str, Any] | None:
        with self._lock:
            incident = self._find_incident(incident_id)
            if not incident:
                return None
            now = _timestamp(utcnow())
            previous_status = incident["status"]
            incident["status"] = IncidentState.RESOLVED.value
            incident["updated_at"] = now
            incident["resolved_at"] = now
            incident["resolution_summary"] = request.summary
            self._add_log(incident_id, "incident_resolved", "Incident marked resolved after operator confirmation.", request.actor, {"summary": request.summary})
            if previous_status != IncidentState.RESOLVED.value:
                self._add_log(incident_id, "status_changed", f"Status changed from {previous_status} to Resolved.", request.actor)
            self._add_audit("incident", incident_id, "incident.resolved", request.actor, f"Resolved {incident['incident_number']}.", {"summary": request.summary})
            self._persist()
            return self._copy(incident)

    def delete_incident(self, incident_id: str, actor: str = "Maya Chen") -> bool:
        with self._lock:
            incident = self._find_incident(incident_id)
            if not incident:
                return False
            self._state["incidents"] = [item for item in self._state["incidents"] if item["id"] != incident_id]
            self._add_audit("incident", incident_id, "incident.deleted", actor, f"Deleted {incident['incident_number']}.")
            self._persist()
            return True

    def get_incident_logs(self, incident_id: str) -> list[dict[str, Any]] | None:
        with self._lock:
            if not self._find_incident(incident_id):
                return None
            rows = [item for item in self._state["incident_logs"] if item["incident_id"] == incident_id]
            return self._copy(sorted(rows, key=lambda item: item["created_at"]))

    def audit_logs(self, incident_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        with self._lock:
            rows = self._state["audit_logs"]
            if incident_id:
                rows = [row for row in rows if row["entity_id"] == incident_id or row["metadata"].get("incident_id") == incident_id]
            return self._copy(sorted(rows, key=lambda item: item["created_at"], reverse=True)[:limit])

    def analytics(self) -> dict[str, Any]:
        with self._lock:
            incidents = self._state["incidents"]
            statuses = {state.value: 0 for state in IncidentState}
            severities = {f"P{number}": 0 for number in range(1, 5)}
            for incident in incidents:
                statuses[incident["status"]] = statuses.get(incident["status"], 0) + 1
                severities[incident["severity"]] = severities.get(incident["severity"], 0) + 1
            resolved = [row for row in incidents if row["status"] in {IncidentState.RESOLVED.value, IncidentState.CLOSED.value}]
            mttr_values: list[float] = []
            for item in resolved:
                if item.get("resolved_at"):
                    started = datetime.fromisoformat(item["created_at"])
                    ended = datetime.fromisoformat(item["resolved_at"])
                    mttr_values.append(round((ended - started).total_seconds() / 60, 1))
            now = utcnow()
            active = statuses[IncidentState.OPEN.value] + statuses[IncidentState.INVESTIGATING.value] + statuses[IncidentState.WAITING_APPROVAL.value]
            created_this_week = sum(1 for row in incidents if datetime.fromisoformat(row["created_at"]) >= now - timedelta(days=7))
            return self._copy(
                {
                    "overview": {
                        "total_incidents": len(incidents),
                        "active_incidents": active,
                        "waiting_approval": statuses[IncidentState.WAITING_APPROVAL.value],
                        "resolved_incidents": len(resolved),
                        "resolution_rate": round((len(resolved) / len(incidents) * 100) if incidents else 0, 1),
                        "mean_time_to_resolution_minutes": round(sum(mttr_values) / len(mttr_values), 1) if mttr_values else 0,
                        "incidents_this_week": created_this_week,
                    },
                    "by_status": statuses,
                    "by_severity": severities,
                    "trend": [
                        {"label": "Mon", "opened": 2, "resolved": 1},
                        {"label": "Tue", "opened": 1, "resolved": 2},
                        {"label": "Wed", "opened": 3, "resolved": 2},
                        {"label": "Thu", "opened": 2, "resolved": 2},
                        {"label": "Fri", "opened": 1, "resolved": 1},
                        {"label": "Today", "opened": active, "resolved": 0},
                    ],
                }
            )

    def agent_status(self) -> list[dict[str, Any]]:
        with self._lock:
            return self._copy(self._state["agent_status"])

    def test_slack(self, channel: str | None, message: str | None, actor: str) -> dict[str, Any]:
        with self._lock:
            item = {
                "id": f"slack_{uuid4().hex[:12]}",
                "incident_id": None,
                "channel": channel or "#incidentops-test",
                "message": message or "IncidentOps AI Slack connection test succeeded.",
                "sent_at": _timestamp(utcnow()),
                "status": "delivered",
            }
            self._state["slack_messages"].append(item)
            self._add_audit("integration", item["id"], "slack.tested", actor, f"Sent Slack test message to {item['channel']}.")
            self._persist()
            return self._copy(item)

    def test_jira(self, project_key: str | None, message: str | None, actor: str) -> dict[str, Any]:
        with self._lock:
            project = (project_key or "OPS").upper()
            item = {
                "id": f"jira_sync_{uuid4().hex[:12]}",
                "incident_id": None,
                "issue_key": f"{project}-{180 + len(self._state['jira_sync']) + 1}",
                "status": "synced",
                "synced_at": _timestamp(utcnow()),
                "project_key": project,
                "summary": message or "IncidentOps AI Jira connection test",
            }
            self._state["jira_sync"].append(item)
            self._add_audit("integration", item["id"], "jira.tested", actor, f"Created Jira test issue {item['issue_key']}.")
            self._persist()
            return self._copy(item)

