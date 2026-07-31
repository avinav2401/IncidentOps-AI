"""Simulated Monitor Agent."""

import asyncio


async def check_service_status(service: str) -> dict:
    """
    Simulates a Monitor Agent checking the status of the service endpoints and containers.
    """
    await asyncio.sleep(0.5)
    if service == "Payment Service":
        return {"status": "DOWN", "details": "Health endpoints unresponsive. Containers failing liveness probe."}
    return {"status": "UP", "details": "Service is operating normally."}
