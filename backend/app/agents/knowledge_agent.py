"""Simulated Knowledge Agent."""

import asyncio


async def fetch_past_incidents(service: str) -> list[dict]:
    """
    Queries the database (or vector store) for past resolved incidents on this service.
    For simulation, returns hardcoded relevant historical incidents.
    """
    await asyncio.sleep(0.8)  # Simulate DB latency
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
