"""Workspace-related Pydantic schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    industry: str = Field(min_length=2, max_length=100)
    company_size: str = Field(min_length=1, max_length=40)


class WorkspaceRead(BaseModel):
    id: str
    name: str
    slug: str
    industry: str
    company_size: str
    owner_id: str
    created_at: str | None = None
