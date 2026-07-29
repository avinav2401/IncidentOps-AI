"""Analytics response schemas."""

from __future__ import annotations

from pydantic import BaseModel


class TrendPoint(BaseModel):
    label: str
    opened: int
    resolved: int


class AnalyticsOverview(BaseModel):
    overview: dict
    by_status: dict
    by_severity: dict
    trend: list[TrendPoint]
