"""API tests for the restructured IncidentOps AI backend.

These tests mirror the original test_api.py assertions while using
the new modular architecture with SQLAlchemy and JWT authentication.
"""

from __future__ import annotations


def test_health_and_versioned_alias_are_available(client) -> None:
    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/api/v1/health").json()["service"] == "incidentops-ai-api"


def test_login_accepts_seeded_user_and_rejects_bad_password(client) -> None:
    bad = client.post("/login", json={"email": "maya.chen@incidentops.dev", "password": "not-demo123"})
    assert bad.status_code == 401

    response = client.post("/api/v1/login", json={"email": "maya.chen@incidentops.dev", "password": "demo123"})
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["role"] == "incident_commander"
    assert "password" not in body["user"]
    assert "hashed_password" not in body["user"]


def test_me_endpoint_returns_current_user(client, auth_headers) -> None:
    response = client.get("/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "maya.chen@incidentops.dev"


def test_incident_listing_detail_and_query_filters(client, auth_headers) -> None:
    listing = client.get("/incidents", params={"status": "Waiting Approval"}, headers=auth_headers)
    assert listing.status_code == 200
    body = listing.json()
    assert body["total"] == 1
    assert body["items"] == body["incidents"]

    incident_id = body["items"][0]["id"]
    detail = client.get(f"/incidents/{incident_id}", headers=auth_headers)
    assert detail.status_code == 200
    assert detail.json()["ai_recommendations"][0]["status"] == "pending_approval"

    filtered = client.get("/incidents", params={"q": "checkout", "severity": "P1"}, headers=auth_headers).json()
    assert filtered["total"] == 1
    assert filtered["items"][0]["service"] == "Checkout API"


def test_create_approve_resolve_and_audit_flow(client, auth_headers) -> None:
    created = client.post(
        "/incidents",
        json={
            "title": "Search index write latency",
            "description": "Writes are exceeding the indexing latency service objective.",
            "service": "Search Platform",
            "severity": "P2",
            "tags": ["search", "latency"],
        },
        headers=auth_headers,
    )
    assert created.status_code == 201
    created_body = created.json()
    assert created_body["status"] == "Open"

    waiting = client.get("/incidents", params={"status": "Waiting Approval"}, headers=auth_headers).json()["items"][0]
    approved = client.post(
        f"/incidents/{waiting['id']}/approve",
        json={"decision": "approve", "actor": "Samir Patel"},
        headers=auth_headers,
    )
    assert approved.status_code == 200
    assert approved.json()["incident"]["status"] == "Investigating"
    assert approved.json()["recommendation"]["status"] == "approved"

    resolved = client.post(
        f"/incidents/{created_body['id']}/resolve",
        json={"summary": "Index workers were restarted and p95 latency recovered.", "actor": "Samir Patel"},
        headers=auth_headers,
    )
    assert resolved.status_code == 200
    assert resolved.json()["status"] == "Resolved"
    assert resolved.json()["resolution_summary"].startswith("Index workers")

    audit = client.get("/audit-logs", params={"incident_id": created_body["id"]}, headers=auth_headers).json()
    assert audit["total"] >= 2
    assert {row["action"] for row in audit["items"]} >= {"incident.created", "incident.resolved"}


def test_analytics_agent_status_and_integration_tests(client, auth_headers) -> None:
    analytics = client.get("/analytics", headers=auth_headers)
    assert analytics.status_code == 200
    assert analytics.json()["overview"]["total_incidents"] == 4
    assert "Waiting Approval" in analytics.json()["by_status"]

    agents = client.get("/agents/status", headers=auth_headers).json()
    assert agents["total"] == 4
    assert agents["healthy"] >= 1

    slack = client.post("/slack/test", json={"channel": "#ops-test"}, headers=auth_headers)
    assert slack.status_code == 200
    assert slack.json()["slack_message"]["channel"] == "#ops-test"

    jira = client.post("/jira/test", json={"project_key": "INC"}, headers=auth_headers)
    assert jira.status_code == 200
    assert jira.json()["jira_sync"]["issue_key"].startswith("INC-")


def test_role_based_access_with_different_users(client) -> None:
    """Verify that all three demo users can log in and have correct roles."""
    users = [
        ("maya.chen@incidentops.dev", "incident_commander"),
        ("samir.patel@incidentops.dev", "responder"),
        ("lena.ortiz@incidentops.dev", "admin"),
    ]
    for email, expected_role in users:
        resp = client.post("/login", json={"email": email, "password": "demo123"})
        assert resp.status_code == 200
        assert resp.json()["user"]["role"] == expected_role

        # Use the token to access a protected endpoint.
        token = resp.json()["access_token"]
        me = client.get("/me", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200
        assert me.json()["role"] == expected_role


def test_incident_update_and_delete(client, auth_headers) -> None:
    """Verify PATCH and DELETE work correctly."""
    # Get the first incident.
    listing = client.get("/incidents", headers=auth_headers).json()
    incident_id = listing["items"][0]["id"]

    # Update the title.
    updated = client.patch(
        f"/incidents/{incident_id}",
        json={"title": "Updated incident title for test"},
        headers=auth_headers,
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Updated incident title for test"

    # Delete it.
    deleted = client.delete(f"/incidents/{incident_id}", headers=auth_headers)
    assert deleted.status_code == 204

    # Verify it's gone.
    detail = client.get(f"/incidents/{incident_id}", headers=auth_headers)
    assert detail.status_code == 404
