"""Simulated Metrics Agent."""

import asyncio


async def fetch_metrics(service: str) -> dict:
    """
    Simulates a Metrics Agent reading APM/Infrastructure metrics.
    """
    await asyncio.sleep(0.8)
    if service == "Payment Service":
        return {"cpu": "99%", "memory": "99%", "requests": "12,000/min", "latency": "15 sec"}
    return {"cpu": "15%", "memory": "40%", "requests": "800/min", "latency": "45 ms"}
