"""Centralized application configuration loaded from environment variables.

All settings are validated by Pydantic on startup. Override any value by
setting the corresponding environment variable or adding it to your ``.env``
file.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide configuration.

    Pydantic Settings reads from environment variables (case-insensitive) and
    from a ``.env`` file when present.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Runtime ────────────────────────────────────────────────────────
    app_env: str = "development"
    demo_mode: bool = True
    debug: bool = False

    # ── Database ───────────────────────────────────────────────────────
    database_url: str = "sqlite:///./incidentops_dev.db"
    # When using PostgreSQL via Docker Compose the URL is injected as:
    #   postgresql+psycopg://incidentops:incidentops_dev_password@postgres:5432/incidentops

    # ── Redis (optional — used by scheduler / background jobs) ─────────
    redis_url: str = "redis://localhost:6379/0"

    # ── JWT / Authentication ───────────────────────────────────────────
    jwt_secret_key: str = "change-this-before-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480  # 8 hours
    supabase_jwt_secret: str = ""
    supabase_url: str = ""

    # ── CORS ───────────────────────────────────────────────────────────
    cors_origins: str = "http://localhost:3000"

    # ── Persistence (demo JSON store — kept for backward compat) ──────
    incidentops_data_file: str = ""

    # ── Integration credentials (opt-in) ──────────────────────────────
    slack_webhook_url: str = ""
    slack_bot_token: str = ""
    slack_channel: str = ""
    jira_base_url: str = ""
    jira_email: str = ""
    jira_api_token: str = ""
    jira_project_key: str = ""
    github_token: str = ""
    openai_api_key: str = ""

    # ── Derived helpers ────────────────────────────────────────────────

    @property
    def allowed_origins(self) -> list[str]:
        """Parse the comma-separated CORS_ORIGINS string."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


# Singleton — imported everywhere as ``from app.config import settings``.
settings = Settings()
