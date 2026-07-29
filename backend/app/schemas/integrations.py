"""Integration test schemas (Slack, Jira)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class IntegrationTestRequest(BaseModel):
    channel: str | None = Field(default=None, max_length=100)
    project_key: str | None = Field(default=None, max_length=20)
    message: str | None = Field(default=None, max_length=1_000)
    actor: str = Field(default="Maya Chen", max_length=120)
