"""Simulated Root Cause Agent."""

import asyncio
import json

from app.agents.llm import call_llm, parse_json_response


async def determine_root_cause(log_summary: str, commits: list[str]) -> dict:
    """
    Uses an LLM to synthesize logs and commits into a root cause hypothesis.
    """
    commits_str = "\n".join(commits)
    prompt = (
        f"Based on the following log summary:\n{log_summary}\n\n"
        f"And these recent commits:\n{commits_str}\n\n"
        "Provide a root cause hypothesis. Return ONLY a JSON object with 'hypothesis' (string) and 'confidence' (integer 0-100)."
    )
    
    response = await call_llm(
        system_prompt="You are an expert SRE. Provide JSON only without markdown formatting.",
        user_prompt=prompt,
    )
    
    try:
        data = parse_json_response(response)
        return {
            "hypothesis": data.get("hypothesis", "Unable to determine hypothesis."),
            "confidence": data.get("confidence", 50)
        }
    except Exception:
        return {
            "hypothesis": "Failed to parse LLM JSON response. " + response[:100],
            "confidence": 0
        }
