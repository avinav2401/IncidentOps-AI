"""Simulated Monitor Agent.

Checks whether scenario-specific data is available in the incident's
context. Falls back to generic health checks when no scenario is attached.
"""

import asyncio


async def check_service_status(service: str, scenario_data: dict | None = None) -> dict:
    """Check the health status of the given service.

    If ``scenario_data`` is provided (from the simulator), use the
    pre-built monitor evidence. Otherwise, simulate a generic check.
    """
    await asyncio.sleep(0.5)

    if scenario_data:
        return {
            "status": scenario_data.get("monitor_status", "UNKNOWN"),
            "details": scenario_data.get("monitor_details", "No details available."),
        }

    # Legacy fallback for non-simulator incidents
    if service == "Payment Service":
        return {"status": "DOWN", "details": "Health endpoints unresponsive. Containers failing liveness probe."}
    return {"status": "UP", "details": "Service is operating normally."}
