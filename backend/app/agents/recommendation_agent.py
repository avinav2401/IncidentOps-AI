"""Simulated Recommendation Agent."""

import asyncio

async def propose_recommendation(root_cause: dict) -> dict:
    """
    Simulates a Recommendation Agent proposing a fix based on the root cause.
    """
    await asyncio.sleep(2)  # Simulate LLM thinking delay
    return {
        "title": "Rollback commit a1b2c3d and redeploy",
        "rationale": "Rolling back the commit that increased the DB pool size limit should mitigate the connection exhaustion immediately.",
        "risk_level": "Low",
        "proposed_actions": [
            "git revert a1b2c3d",
            "trigger deployment pipeline"
        ]
    }
