"""Tests for the GET /v1/health endpoint (API-08)."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_returns_200(client: TestClient) -> None:
    """GET /v1/health returns HTTP 200."""
    response = client.get("/v1/health")
    assert response.status_code == 200


def test_health_response_body(client: TestClient) -> None:
    """Response body matches expected health payload exactly."""
    response = client.get("/v1/health")
    data = response.json()
    assert data == {"status": "ok", "version": "1", "cadenza_version": "0.1.0"}


def test_health_response_content_type(client: TestClient) -> None:
    """Response Content-Type is application/json."""
    response = client.get("/v1/health")
    assert response.headers["content-type"] == "application/json"
