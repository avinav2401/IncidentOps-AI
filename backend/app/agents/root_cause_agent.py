"""Simulated Root Cause Agent."""

from app.agents.llm import call_llm, parse_json_response


async def determine_root_cause(log_summary: str, commits: list[str], monitor_data: dict, metrics_data: dict, knowledge_context: list[dict] = None) -> dict:
    """
    Uses an LLM to synthesize logs, commits, monitor status, and metrics into a root cause hypothesis.
    """
    commits_str = "\n".join(commits)
    prompt = (
        f"Based on the following evidence:\n"
        f"- Monitor Status: {monitor_data.get('status')} ({monitor_data.get('details')})\n"
        f"- Metrics: CPU {metrics_data.get('cpu')}, Memory {metrics_data.get('memory')}, Latency {metrics_data.get('latency')}\n"
        f"- Log summary: {log_summary}\n"
        f"- Recent commits:\n{commits_str}\n"
        f"- Historical context (similar past incidents):\n{knowledge_context or []}\n\n"
        "Provide a root cause hypothesis. Return ONLY a JSON object with 'hypothesis' (string), 'confidence' (integer 0-100), "
        "'evidence_chain' (list of objects with 'step' and 'type' which must be one of 'observation', 'deduction', 'conclusion'), "
        "and 'similar_incidents' (list of strings representing incident IDs like 'INC-142')."
    )

    response = await call_llm(
        system_prompt="You are an expert SRE. Provide JSON only without markdown formatting.",
        user_prompt=prompt,
    )

    try:
        data = parse_json_response(response)
        return {
            "hypothesis": data.get("hypothesis", "Unable to determine hypothesis."),
            "confidence": data.get("confidence", 50),
            "evidence_chain": data.get("evidence_chain", []),
            "similar_incidents": data.get("similar_incidents", ["INC-142"]),
        }
    except Exception:
        return {
            "hypothesis": "Failed to parse LLM JSON response. " + response[:100],
            "confidence": 0,
            "evidence_chain": [],
            "similar_incidents": [],
        }
