"""Multi-destination output handler system.

Provides a pluggable registry of output handlers that can post AI agent
results to external services (GitHub PR/issue comments, Slack channels,
Jira tickets, etc.).

Architecture ported from IncidentFox's production ``output_handlers/``.

Usage:
    from app.services.output_handlers import get_output_registry, post_to_destinations

    # Post to all configured destinations
    results = await post_to_destinations(
        destinations=[{"type": "github_pr_comment", "repo": "org/repo", "pr_number": 42}],
        result_text="Analysis complete. Root cause: ...",
    )
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

logger = logging.getLogger(__name__)


def _structured_log(event: str, **fields: Any) -> None:
    """Structured JSON logging for output handlers."""
    try:
        payload = {"component": "output_handlers", "event": event, **fields}
        logger.info(json.dumps(payload, default=str))
    except Exception:
        logger.info("%s %s", event, fields)


@dataclass
class OutputResult:
    """Result of posting to an output destination."""

    success: bool
    destination_type: str
    message_id: str | None = None
    error: str | None = None


class OutputHandler(ABC):
    """Base class for output handlers.

    Subclass this to add support for new output destinations
    (e.g., Microsoft Teams, Google Chat, email).
    """

    @property
    @abstractmethod
    def destination_type(self) -> str:
        """The destination type this handler supports (e.g., 'github_pr_comment')."""

    @abstractmethod
    async def post_result(
        self,
        config: dict[str, Any],
        result_text: str,
        *,
        success: bool = True,
        agent_name: str = "IncidentOps AI",
        run_id: str | None = None,
        duration_seconds: float | None = None,
        error: str | None = None,
    ) -> OutputResult:
        """Post agent result to the destination."""


class OutputHandlerRegistry:
    """Registry of output handlers by destination type."""

    def __init__(self) -> None:
        self._handlers: dict[str, OutputHandler] = {}

    def register(self, handler: OutputHandler) -> None:
        """Register an output handler."""
        self._handlers[handler.destination_type] = handler
        _structured_log(
            "handler_registered", destination_type=handler.destination_type
        )

    def get(self, destination_type: str) -> OutputHandler | None:
        """Get handler for a given destination type."""
        return self._handlers.get(destination_type)

    def list_types(self) -> list[str]:
        """List all registered destination types."""
        return list(self._handlers.keys())


# ── Global registry singleton ─────────────────────────────────────────

_registry: OutputHandlerRegistry | None = None


def get_output_registry() -> OutputHandlerRegistry:
    """Get the global output handler registry (lazy singleton)."""
    global _registry
    if _registry is None:
        _registry = OutputHandlerRegistry()
        _register_default_handlers(_registry)
    return _registry


def _register_default_handlers(registry: OutputHandlerRegistry) -> None:
    """Register all built-in handlers."""
    from app.services.output_handlers.github import (
        GitHubIssueCommentHandler,
        GitHubPRCommentHandler,
    )
    from app.services.output_handlers.slack import SlackWebhookHandler

    registry.register(GitHubPRCommentHandler())
    registry.register(GitHubIssueCommentHandler())
    registry.register(SlackWebhookHandler())


async def post_to_destinations(
    destinations: list[dict[str, Any]],
    result_text: str,
    *,
    success: bool = True,
    agent_name: str = "IncidentOps AI",
    run_id: str | None = None,
    duration_seconds: float | None = None,
    error: str | None = None,
) -> list[OutputResult]:
    """Post agent result to all configured destinations.

    Destinations with unknown types are silently skipped.
    """
    if not destinations:
        return []

    registry = get_output_registry()
    results: list[OutputResult] = []

    for dest in destinations:
        dest_type = dest.get("type", "")
        handler = registry.get(dest_type)
        if not handler:
            _structured_log("handler_not_found", destination_type=dest_type)
            continue

        try:
            result = await handler.post_result(
                config=dest,
                result_text=result_text,
                success=success,
                agent_name=agent_name,
                run_id=run_id,
                duration_seconds=duration_seconds,
                error=error,
            )
            results.append(result)
            _structured_log(
                "output_posted",
                destination_type=dest_type,
                success=result.success,
                message_id=result.message_id,
            )
        except Exception as e:
            _structured_log(
                "output_post_failed", destination_type=dest_type, error=str(e)
            )
            results.append(
                OutputResult(success=False, destination_type=dest_type, error=str(e))
            )

    return results
