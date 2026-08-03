"""Simulated Knowledge Agent.

Returns scenario-specific historical context when available, or
falls back to generic past incident data.
"""

import asyncio


async def fetch_past_incidents(service: str, scenario_data: dict | None = None) -> list[dict]:
    """Query for past resolved incidents similar to the current one.

    If ``scenario_data`` is provided, use its pre-built knowledge context.
    Otherwise, return generic historical incidents.
    """
    await asyncio.sleep(0.8)

    if scenario_data and "knowledge_context" in scenario_data:
        return scenario_data["knowledge_context"]

    # Legacy fallback
    return [
        {
            "incident_number": "INC-142",
            "title": "Payment API Gateway Timeout",
            "resolution": "Rollback to previous deployment (v1.12.4). The new deployment had a misconfigured connection pool.",
            "similarity": 0.92,
        },
        {
            "incident_number": "INC-089",
            "title": "Database connection exhaustion in Payment Service",
            "resolution": "Increased max_connections in PostgreSQL config from 100 to 500 and restarted the service.",
            "similarity": 0.75,
        },
    ]


async def get_prevention_suggestions(service: str, root_cause: str) -> list[str]:
    """Query past resolutions and return structural fixes to prevent recurrence."""
    await asyncio.sleep(0.5)

    # In a real implementation, this would query a vector DB (like Chroma)
    # to find structural fixes from past postmortems for this service.
    # For now, we simulate AI generated structural fixes based on the root cause.

    root_cause_lower = root_cause.lower()

    if "memory" in root_cause_lower or "oom" in root_cause_lower:
        return [
            f"Implement a memory profiler in {service} CI pipeline.",
            f"Set up an alert for {service} when heap usage exceeds 85% for 5 minutes.",
            "Review and adjust Kubernetes resource limits and requests.",
        ]
    elif "database" in root_cause_lower or "connection" in root_cause_lower:
        return [
            f"Implement connection pooling (e.g., PgBouncer) for {service}.",
            "Add automated chaos testing for database failover.",
            "Review query optimization and add missing indexes.",
        ]
    elif "timeout" in root_cause_lower or "gateway" in root_cause_lower:
        return [
            f"Implement circuit breaker pattern in {service} client calls.",
            "Add distributed tracing to pinpoint latency bottlenecks.",
            "Configure proper timeout and retry policies.",
        ]
    else:
        return [
            f"Add specific anomaly detection alerts for {service}.",
            "Update runbooks with the resolution steps taken.",
            "Schedule a blameless postmortem review with the team.",
        ]
