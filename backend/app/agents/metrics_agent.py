"""Simulated Metrics Agent.

Returns scenario-specific APM/infrastructure metrics when available,
or falls back to generic mock data for non-simulator incidents.
"""

import asyncio


async def fetch_metrics(service: str, scenario_data: dict | None = None) -> dict:
    """Fetch APM and infrastructure metrics for the given service.

    If ``scenario_data`` is provided (from the simulator), use the
    pre-built metrics. Otherwise, simulate generic data.
    """
    await asyncio.sleep(0.8)

    if scenario_data and "metrics" in scenario_data:
        return scenario_data["metrics"]

    # Legacy fallback
    if service == "Payment Service":
        return {"cpu": "99%", "memory": "99%", "error_rate": "95%", "latency": "15 sec", "requests": "12,000/min"}
    return {"cpu": "15%", "memory": "40%", "error_rate": "2%", "latency": "45 ms", "requests": "800/min"}
