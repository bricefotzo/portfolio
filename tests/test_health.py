"""Tests — Health check endpoint."""

from __future__ import annotations


def test_health_returns_ok(client):
    """GET /health doit retourner status=ok."""
    resp = client.get("/health")
    assert resp.status_code == 200

    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_health_response_schema(client):
    """La réponse /health doit contenir status et version."""
    resp = client.get("/health")
    data = resp.json()
    assert isinstance(data["status"], str)
    assert isinstance(data["version"], str)
