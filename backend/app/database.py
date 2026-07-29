"""SQLAlchemy engine, session factory, and declarative base.

Works with both SQLite (local dev without Docker) and PostgreSQL (Docker
Compose / production).  Import ``get_db`` as a FastAPI dependency to obtain a
scoped session for each request.
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

# SQLite requires ``check_same_thread=False`` when used with FastAPI's
# threaded request model.  PostgreSQL ignores this option.
connect_args: dict = {"check_same_thread": False} if settings.is_sqlite else {}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    echo=settings.debug,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session and closes it after
    the request completes — regardless of success or failure."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
