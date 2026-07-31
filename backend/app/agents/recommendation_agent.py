"""Simulated Recommendation Agent."""

from app.agents.llm import call_llm, parse_json_response


async def propose_recommendation(root_cause: dict) -> dict:
    """
    Uses an LLM to propose a fix based on the root cause.
    """
    prompt = (
        f"The root cause of the incident is: {root_cause.get('hypothesis', 'Unknown')}\n\n"
        "Propose a remediation plan. Return ONLY a JSON object with:\n"
        "- 'title' (string): A short summary of the fix.\n"
        "- 'rationale' (string): Why this fix works.\n"
        "- 'risk_level' (string): 'Low', 'Medium', or 'High'.\n"
        "- 'proposed_actions' (list of strings): Concrete steps to execute.\n"
    )

    response = await call_llm(
        system_prompt="You are an expert SRE. Provide JSON only without markdown formatting.",
        user_prompt=prompt,
    )

    try:
        data = parse_json_response(response)
        return {
            "title": data.get("title", "Fallback Mitigation Plan"),
            "rationale": data.get("rationale", "Apply generic mitigation steps."),
            "risk_level": data.get("risk_level", "Medium"),
            "proposed_actions": data.get("proposed_actions", ["Investigate manually."]),
        }
    except Exception:
        return {
            "title": "Failed to parse recommendation",
            "rationale": response[:200],
            "risk_level": "High",
            "proposed_actions": ["Review logs manually."],
        }
