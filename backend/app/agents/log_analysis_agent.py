"""Simulated Log Analysis Agent."""

import asyncio

from app.agents.llm import call_llm


async def analyze_logs(incident_id: str, service: str) -> str:
    """
    Simulates fetching logs and uses a real LLM to analyze them.
    In a complete setup, this agent would use an Elasticsearch tool.
    """
    # Mock log fetch for the demo
    await asyncio.sleep(0.5)
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
