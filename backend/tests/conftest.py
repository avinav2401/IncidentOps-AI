"""Shared test fixtures for the IncidentOps AI test suite."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.seed import seed_database


@pytest.fixture()
def client():
    """Create a test client backed by an in-memory SQLite database.

    Each test gets a completely fresh database so tests never interfere
    with each other.
    """
    test_engine = create_engine(
        "sqlite:///:memory:", 
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestSession = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)

    # Import models so Base.metadata knows about all tables.
    import app.models  # noqa: F401

    # Create all tables in the test database.
    Base.metadata.create_all(bind=test_engine)

    # Seed demo data.
    db = TestSession()
    seed_database(db)
    db.close()

    # Override the get_db dependency to use our test database.
    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    # Build the app without lifespan (we handle DB setup ourselves above).
    from app.main import create_app
    from app.config import settings
    settings.demo_mode = True
    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app, raise_server_exceptions=True) as test_client:
        yield test_client

    # Cleanup.
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def auth_headers(client: TestClient) -> dict[str, str]:
    """Get a valid Authorization header for the default demo user."""
    response = client.post("/login", json={"email": "maya.chen@incidentops.dev", "password": "demo123"})
    assert response.status_code == 200, f"Login failed: {response.text}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
