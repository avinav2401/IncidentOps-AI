"""Simulated Verification Agent.

Re-checks service health after a fix has been applied to confirm recovery.
"""

import asyncio


async def verify_fix(service: str) -> dict:
    """
    Simulates a post-fix health check by the Monitor Agent.
    Returns healthy metrics indicating the service has recovered.
    """
    await asyncio.sleep(1.0)  # Simulate health check delay

    import random
    if random.random() < 0.10:
        return {
            "health": "Failing",
            "cpu": "95%",
            "memory": "85%",
            "latency": "5000ms",
            "error_rate": "100%",
            "status": "DOWN",
            "details": "Health endpoints timing out. Remediation failed to restore service.",
        }

    return {
        "health": "Healthy",
        "cpu": "18%",
        "memory": "42%",
        "latency": "120ms",
        "error_rate": "0%",
        "status": "UP",
        "details": "All health endpoints responding. Liveness and readiness probes passing.",
    }
