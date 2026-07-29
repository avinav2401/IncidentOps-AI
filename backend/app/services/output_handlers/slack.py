"""Slack output handler — posts agent results to Slack channels via webhook.

Supports both incoming webhook URLs and Bot token API calls.
"""

from __future__ import annotations

import os
from typing import Any

import httpx

from app.services.output_handlers import OutputHandler, OutputResult, _structured_log


class SlackWebhookHandler(OutputHandler):
    """Posts agent results to Slack via incoming webhook or Bot API."""

    @property
    def destination_type(self) -> str:
        return "slack"

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
        # Determine whether to use webhook URL or Bot API
        webhook_url = config.get("webhook_url") or os.getenv("SLACK_WEBHOOK_URL", "")
        bot_token = config.get("bot_token") or os.getenv("SLACK_BOT_TOKEN", "")
        channel_id = config.get("channel_id") or os.getenv("SLACK_CHANNEL", "")

        if webhook_url:
            return await self._post_via_webhook(
                webhook_url, result_text, success, agent_name, duration_seconds, error
            )
        elif bot_token and channel_id:
            return await self._post_via_api(
                bot_token, channel_id, result_text, success, agent_name, duration_seconds, error
            )
        else:
            return OutputResult(
                success=False,
                destination_type=self.destination_type,
                error="No webhook_url or bot_token+channel_id configured",
            )

    async def _post_via_webhook(
        self,
        webhook_url: str,
        result_text: str,
        success: bool,
        agent_name: str,
        duration_seconds: float | None,
        error: str | None,
    ) -> OutputResult:
        """Post via Slack incoming webhook."""
        status_emoji = "\u2705" if success else "\u274c"
        header = f"{status_emoji} *{agent_name}*"

        blocks = [
            {"type": "section", "text": {"type": "mrkdwn", "text": header}},
            {"type": "divider"},
        ]

        if not success:
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Error:* {error or 'Unknown'}"},
            })
        else:
            # Truncate for Slack's 3000 char block limit
            text = result_text[:2900] + "..." if len(result_text) > 2900 else result_text
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": text},
            })

        if duration_seconds is not None:
            blocks.append({
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": f"_Duration: {duration_seconds:.1f}s_"},
                ],
            })

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    webhook_url,
                    json={"blocks": blocks, "text": f"{agent_name}: {result_text[:200]}"},
                )
                resp.raise_for_status()

            _structured_log("slack_webhook_posted", webhook_url=webhook_url[:50])
            return OutputResult(success=True, destination_type=self.destination_type)

        except Exception as e:
            _structured_log("slack_webhook_failed", error=str(e))
            return OutputResult(
                success=False, destination_type=self.destination_type, error=str(e)
            )

    async def _post_via_api(
        self,
        bot_token: str,
        channel_id: str,
        result_text: str,
        success: bool,
        agent_name: str,
        duration_seconds: float | None,
        error: str | None,
    ) -> OutputResult:
        """Post via Slack Web API (chat.postMessage)."""
        status_emoji = "\u2705" if success else "\u274c"
        text = f"{status_emoji} *{agent_name}*\n\n"

        if not success:
            text += f"*Error:* {error or 'Unknown'}"
        else:
            text += result_text[:3500]

        if duration_seconds is not None:
            text += f"\n\n_Duration: {duration_seconds:.1f}s_"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    "https://slack.com/api/chat.postMessage",
                    headers={
                        "Authorization": f"Bearer {bot_token}",
                        "Content-Type": "application/json; charset=utf-8",
                    },
                    json={
                        "channel": channel_id,
                        "text": text,
                        "unfurl_links": False,
                    },
                )
                data = resp.json()
                if data.get("ok"):
                    _structured_log(
                        "slack_api_posted",
                        channel=channel_id,
                        message_ts=data.get("ts"),
                    )
                    return OutputResult(
                        success=True,
                        destination_type=self.destination_type,
                        message_id=data.get("ts"),
                    )
                else:
                    _structured_log(
                        "slack_api_error",
                        error=data.get("error", "unknown"),
                        channel=channel_id,
                    )
                    return OutputResult(
                        success=False,
                        destination_type=self.destination_type,
                        error=data.get("error", "unknown"),
                    )
        except Exception as e:
            _structured_log("slack_api_failed", error=str(e))
            return OutputResult(
                success=False, destination_type=self.destination_type, error=str(e)
            )
