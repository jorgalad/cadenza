"""Integration tests for theory endpoints -- TDD RED phase."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_scale_lookup(client: TestClient) -> None:
    r = client.post("/v1/theory/scale", json={"root": "c4", "name": "major"})
    assert r.status_code == 200
    data = r.json()
    assert "phrase" in data
    assert "c4" in data["phrase"].lower()
    assert "events" in data


def test_chord_lookup(client: TestClient) -> None:
    r = client.post("/v1/theory/chord", json={"root": "c4", "symbol": "maj"})
    assert r.status_code == 200
    data = r.json()
    assert "phrase" in data
    assert "events" in data


def test_unknown_scale_returns_422(client: TestClient) -> None:
    r = client.post("/v1/theory/scale", json={"root": "c4", "name": "nonexistent"})
    assert r.status_code == 422
    assert r.json()["error"] == "INVALID_SCALE_NAME"
