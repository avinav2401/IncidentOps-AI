"""Stream Event Protocol for real-time agent communication.

Defines structured SSE (Server-Sent Events) for communication between
the AI agent pipeline and frontend clients. Adapted from IncidentFox's
production streaming architecture.

Event Types:
- thought:        Agent reasoning / status text
- agent_start:    An agent step begins (e.g., "Log Analysis Agent")
- agent_end:      An agent step completes
- result:         Final pipeline result
- error:          Error occurred during pipeline
- approval:       Human approval needed for a recommendation
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class StreamEvent:
    """Structured event for agent-to-client SSE communication."""

    type: str
    data: dict[str, Any]
    incident_id: str
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_sse(self) -> str:
        """Format as a Server-Sent Event data line."""
        return f"data: {json.dumps(self.to_dict())}\n\n"


# ── Factory functions ─────────────────────────────────────────────────


def thought_event(incident_id: str, text: str) -> StreamEvent:
    """Agent is thinking / providing a status update."""
    return StreamEvent(type="thought", data={"text": text}, incident_id=incident_id)


def agent_start_event(
    incident_id: str,
    agent_name: str,
    *,
    description: str = "",
) -> StreamEvent:
    """An agent step in the pipeline has started."""
    return StreamEvent(
        type="agent_start",
        data={
            "agent_name": agent_name,
            "description": description,
        },
        incident_id=incident_id,
    )


def agent_end_event(
    incident_id: str,
    agent_name: str,
    *,
    success: bool = True,
    summary: str = "",
    duration_seconds: float | None = None,
) -> StreamEvent:
    """An agent step in the pipeline has completed."""
    data: dict[str, Any] = {
        "agent_name": agent_name,
        "success": success,
        "summary": summary,
    }
    if duration_seconds is not None:
        data["duration_seconds"] = round(duration_seconds, 2)
    return StreamEvent(type="agent_end", data=data, incident_id=incident_id)


def result_event(
    incident_id: str,
    text: str,
    *,
    success: bool = True,
    total_duration_seconds: float | None = None,
    recommendation_id: str | None = None,
    classifications: list[str] | None = None,
    cost_impact: dict[str, Any] | None = None,
) -> StreamEvent:
    """Final pipeline result."""
    data: dict[str, Any] = {
        "text": text,
        "success": success,
    }
    if total_duration_seconds is not None:
        data["total_duration_seconds"] = round(total_duration_seconds, 2)
    if recommendation_id:
        data["recommendation_id"] = recommendation_id
    if classifications:
        data["classifications"] = classifications
    if cost_impact:
        data["cost_impact"] = cost_impact
    return StreamEvent(type="result", data=data, incident_id=incident_id)


def error_event(
    incident_id: str,
    message: str,
    *,
    recoverable: bool = False,
    agent_name: str | None = None,
) -> StreamEvent:
    """Error occurred during pipeline execution."""
    data: dict[str, Any] = {
        "message": message,
        "recoverable": recoverable,
    }
    if agent_name:
        data["agent_name"] = agent_name
    return StreamEvent(type="error", data=data, incident_id=incident_id)


def approval_event(
    incident_id: str,
    recommendation_id: str,
    title: str,
    rationale: str,
    risk: str,
    proposed_actions: list[str],
) -> StreamEvent:
    """Human approval is requested for a recommendation."""
    return StreamEvent(
        type="approval",
        data={
            "recommendation_id": recommendation_id,
            "title": title,
            "rationale": rationale,
            "risk": risk,
            "proposed_actions": proposed_actions,
        },
        incident_id=incident_id,
    )


# ── Utilities ─────────────────────────────────────────────────────────


def truncate_dict(d: dict[str, Any], max_str_len: int = 500) -> dict[str, Any]:
    """Truncate string values in a dict to avoid huge SSE payloads."""
    result: dict[str, Any] = {}
    for k, v in d.items():
        if isinstance(v, str) and len(v) > max_str_len:
            result[k] = v[:max_str_len] + "..."
        elif isinstance(v, dict):
            result[k] = truncate_dict(v, max_str_len)
        else:
            result[k] = v
    return result
