"""Simulated Log Analysis Agent.

Uses scenario-specific log data when available. Sends the logs to the
LLM for analysis regardless of whether they're from a scenario or
the legacy mock.
"""

import asyncio

from app.agents.llm import call_llm


async def analyze_logs(incident_id: str, service: str, scenario_data: dict | None = None) -> str:
    """Analyze recent application logs for the given service.

    If ``scenario_data`` is provided, use its realistic log content.
    Otherwise, fall back to hardcoded mock logs.
    """
    await asyncio.sleep(0.5)

    if scenario_data and "logs" in scenario_data:
        mock_logs = scenario_data["logs"]
    elif service == "Payment Service":
        mock_logs = "OutOfMemoryError\nJava Heap Space\nKilled by Linux OOM Killer\n"
    else:
        mock_logs = (
            "10:00:01 ERROR [auth-service] Connection pool exhausted\n"
            "10:00:02 ERROR [auth-service] Connection pool exhausted\n"
            "10:00:05 ERROR [auth-service] Timeout waiting for DB connection\n"
        )

    prompt = f"Analyze these recent logs for the service '{service}' and provide a 1-2 sentence summary of what went wrong:\n\n{mock_logs}"

    return await call_llm(
        system_prompt="You are an expert SRE log analysis agent. Be concise.",
        user_prompt=prompt,
    )
