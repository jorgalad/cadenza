"""Integration tests for transform endpoints -- TDD RED phase."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


def test_chromatic_transpose_response_format(client: TestClient) -> None:
    """POST /v1/transform/chromatic-transpose returns phrase + events."""
    r = client.post(
        "/v1/transform/chromatic-transpose",
        json={"phrase": "e c4 q d4 e4", "interval": "m3"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "phrase" in data
    assert isinstance(data["phrase"], str)
    assert "events" in data


def test_pitch_retrograde_response_format(client: TestClient) -> None:
    """POST /v1/transform/pitch-retrograde returns phrase + events."""
    r = client.post("/v1/transform/pitch-retrograde", json={"phrase": "e c4 d4 e4"})
    assert r.status_code == 200
    data = r.json()
    assert "phrase" in data
    assert "events" in data


def test_full_retrograde(client: TestClient) -> None:
    r = client.post("/v1/transform/full-retrograde", json={"phrase": "e c4 q d4 h e4"})
    assert r.status_code == 200
    assert "phrase" in r.json()


def test_augment(client: TestClient) -> None:
    r = client.post("/v1/transform/augment", json={"phrase": "e c4 d4", "ratio": 2.0})
    assert r.status_code == 200


def test_diminish(client: TestClient) -> None:
    r = client.post("/v1/transform/diminish", json={"phrase": "q c4 d4", "ratio": 2.0})
    assert r.status_code == 200


def test_fragment_returns_multi_phrase(client: TestClient) -> None:
    r = client.post(
        "/v1/transform/fragment",
        json={"phrase": "e c4 d4 e4 f4", "lengths": [2, 2]},
    )
    assert r.status_code == 200
    data = r.json()
    assert "phrases" in data
    assert len(data["phrases"]) == 2


def test_concatenate(client: TestClient) -> None:
    r = client.post(
        "/v1/transform/concatenate",
        json={"phrases": ["e c4 d4", "q e4 f4"]},
    )
    assert r.status_code == 200
    assert "phrase" in r.json()


def test_pitch_map_not_implemented(client: TestClient) -> None:
    r = client.post("/v1/transform/pitch-map", json={"phrase": "e c4"})
    assert r.status_code == 422
    assert r.json()["error"] == "NOT_IMPLEMENTED"


def test_swing_not_implemented(client: TestClient) -> None:
    r = client.post("/v1/transform/swing", json={"phrase": "e c4"})
    assert r.status_code == 422
    assert r.json()["error"] == "NOT_IMPLEMENTED"


def test_invalid_cn_returns_422(client: TestClient) -> None:
    r = client.post(
        "/v1/transform/chromatic-transpose",
        json={"phrase": "invalid garbage", "interval": "m3"},
    )
    assert r.status_code == 422
    assert r.json()["error"] == "INVALID_CN"
