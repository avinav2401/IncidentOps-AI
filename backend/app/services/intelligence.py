"""AI Intelligence Engine — classification, severity, priority, and cost impact.

Provides smart auto-classification of incidents by failure type, automatic
severity assignment based on impact scoring, and cost impact estimation.
These run as lightweight post-analysis enrichments after the AI pipeline.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.models.service import Service

# ── Incident Classification ──────────────────────────────────────────

# Maps keywords found in logs/titles/descriptions to failure categories.
CLASSIFICATION_RULES: list[tuple[list[str], str]] = [
    (["outofmemory", "oom", "heap", "memory leak", "memory 99%", "memory 98%"], "Memory Leak"),
    (["timeout", "timed out", "connection refused", "gateway timeout", "504"], "Service Timeout"),
    (["connection pool", "max_connections", "cannot acquire connection"], "Database Failure"),
    (["crashloopbackoff", "crashloop", "crash loop", "container exited"], "Pod Crash"),
    (["rate limit", "429", "too many requests", "throttl"], "API Rate Limit"),
    (["ssl", "tls", "certificate expired", "handshake fail"], "SSL/TLS Failure"),
    (["dns", "nxdomain", "resolve", "coredns"], "DNS Failure"),
    (["disk", "no space left", "disk pressure", "storage full"], "Disk Exhaustion"),
    (["redis", "cache", "sentinel", "quorum"], "Cache Failure"),
    (["staging", "wrong environment", "wrong config", "misconfigur"], "Configuration Error"),
    (["deploy", "rollout", "rollback", "version"], "Deployment Failure"),
    (["auth", "jwt", "token", "unauthorized", "403", "401"], "Authentication Failure"),
    (["payment", "razorpay", "stripe", "charge", "billing"], "Payment Gateway"),
    (["network", "unreachable", "connection reset"], "Network Failure"),
    (["cpu 99%", "cpu 100%", "high cpu", "cpu spike"], "CPU Saturation"),
]


def classify_incident(title: str, description: str, logs: str = "") -> list[str]:
    """Return a list of classification tags based on incident content.

    Scans the title, description, and logs for keyword patterns and returns
    matching failure categories. Returns ["Unclassified"] if nothing matches.
    """
    text = f"{title} {description} {logs}".lower()
    classifications = []

    for keywords, category in CLASSIFICATION_RULES:
        if any(kw in text for kw in keywords):
            classifications.append(category)

    return classifications if classifications else ["Unclassified"]


# ── Severity Engine ──────────────────────────────────────────────────

# Scoring weights for automatic severity calculation.
_CRITICALITY_SCORES = {
    "Critical": 40,
    "High": 25,
    "Medium": 15,
    "Low": 5,
}


def calculate_severity(
    affected_users: int,
    service_criticality: str = "Medium",
    error_rate: float = 0.0,
    classifications: list[str] | None = None,
) -> str:
    """Calculate P1-P4 severity based on multi-factor impact scoring.

    Factors:
    - Number of affected users (0-40 points)
    - Service criticality level (0-40 points)
    - Error rate percentage (0-10 points)
    - Classification severity bonus (0-10 points)

    Score thresholds: P1 >= 70, P2 >= 45, P3 >= 20, P4 < 20
    """
    score = 0

    # User impact (0-40 points)
    if affected_users >= 50000:
        score += 40
    elif affected_users >= 10000:
        score += 30
    elif affected_users >= 1000:
        score += 20
    elif affected_users >= 100:
        score += 10
    else:
        score += 5

    # Service criticality (0-40 points)
    score += _CRITICALITY_SCORES.get(service_criticality, 15)

    # Error rate (0-10 points)
    if error_rate >= 90:
        score += 10
    elif error_rate >= 50:
        score += 7
    elif error_rate >= 20:
        score += 4

    # Classification severity bonus (0-10 points)
    critical_types = {"SSL/TLS Failure", "DNS Failure", "Pod Crash", "Database Failure"}
    if classifications and any(c in critical_types for c in classifications):
        score += 10

    # Map score to severity
    if score >= 70:
        return "P1"
    elif score >= 45:
        return "P2"
    elif score >= 20:
        return "P3"
    else:
        return "P4"


# ── Cost Impact Calculator ───────────────────────────────────────────

# Revenue-per-user-per-minute estimates by service criticality.
_REVENUE_PER_USER_PER_MINUTE = {
    "Critical": 0.05,  # $0.05 per user per minute (e.g., payment service)
    "High": 0.02,
    "Medium": 0.005,
    "Low": 0.001,
}


def estimate_cost_impact(
    affected_users: int,
    duration_minutes: float,
    service_criticality: str = "Medium",
) -> dict:
    """Estimate the financial impact of an incident.

    Returns a dict with estimated revenue loss, cost breakdown, and
    impact category (Low / Moderate / High / Critical).
    """
    rate = _REVENUE_PER_USER_PER_MINUTE.get(service_criticality, 0.005)
    revenue_loss = round(affected_users * duration_minutes * rate, 2)

    # Engineering cost (assume $150/hr for incident response team of 3)
    engineering_cost = round((duration_minutes / 60) * 150 * 3, 2)

    total_cost = round(revenue_loss + engineering_cost, 2)

    # Impact category
    if total_cost >= 10000:
        category = "Critical"
    elif total_cost >= 1000:
        category = "High"
    elif total_cost >= 100:
        category = "Moderate"
    else:
        category = "Low"

    return {
        "estimated_revenue_loss": revenue_loss,
        "engineering_cost": engineering_cost,
        "total_estimated_cost": total_cost,
        "impact_category": category,
        "affected_users": affected_users,
        "duration_minutes": round(duration_minutes, 1),
        "currency": "USD",
    }


# ── Enrichment Entrypoint ────────────────────────────────────────────


def enrich_incident(
    db: Session,
    incident: Incident,
    logs: str = "",
    error_rate: float = 0.0,
) -> dict:
    """Run all intelligence enrichments on an incident and return the results.

    This is called by the orchestrator after the evidence-gathering phase.
    It classifies the incident, recalculates severity, and estimates cost.
    """
    # Classify
    classifications = classify_incident(incident.title, incident.description, logs)

    # Get service criticality
    service = (
        db.query(Service)
        .filter(
            Service.workspace_id == incident.workspace_id,
            Service.name == incident.service,
        )
        .first()
    )
    service_criticality = service.critical_level if service else "Medium"

    # Calculate severity
    calculated_severity = calculate_severity(
        affected_users=incident.affected_users or 0,
        service_criticality=service_criticality,
        error_rate=error_rate,
        classifications=classifications,
    )

    # Calculate duration so far
    now = datetime.now(UTC)
    created = incident.created_at
    if created and created.tzinfo is None:
        created = created.replace(tzinfo=UTC)
    duration_minutes = (now - created).total_seconds() / 60 if created else 0

    # Cost impact
    cost_impact = estimate_cost_impact(
        affected_users=incident.affected_users or 0,
        duration_minutes=duration_minutes,
        service_criticality=service_criticality,
    )

    # Update incident tags with classifications
    existing_tags = incident.tags or []
    new_tags = list(set(existing_tags + [c.lower().replace(" ", "-") for c in classifications]))
    incident.tags = new_tags

    # Auto-upgrade severity if calculated severity is worse
    severity_order = {"P1": 1, "P2": 2, "P3": 3, "P4": 4}
    if severity_order.get(calculated_severity, 4) < severity_order.get(incident.severity, 4):
        incident.severity = calculated_severity

    return {
        "classifications": classifications,
        "calculated_severity": calculated_severity,
        "cost_impact": cost_impact,
        "service_criticality": service_criticality,
    }
