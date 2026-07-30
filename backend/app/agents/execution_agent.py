"""Simulated Execution Agent.

Simulates running a remediation command (e.g., kubectl rollout restart)
after human approval.  Returns execution details for the incident timeline.
"""

import asyncio


async def execute_fix(service: str, recommendation_title: str) -> dict:
    """
    Simulates executing a remediation command for the given service.
    In production this would call kubectl, Docker, or a runbook API.
    """
    await asyncio.sleep(1.5)  # Simulate command execution time

    if "restart" in recommendation_title.lower() or "rollback" in recommendation_title.lower():
        command = f"kubectl rollout restart deployment/{service.lower().replace(' ', '-')}"
    else:
        command = f"kubectl scale deployment/{service.lower().replace(' ', '-')} --replicas=3"

    return {
        "command": command,
        "status": "success",
        "output": f"deployment.apps/{service.lower().replace(' ', '-')} restarted",
        "duration_seconds": 1.5,
    }
