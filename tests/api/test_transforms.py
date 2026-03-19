"""Integration tests for all transform endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Response format tests (API-02, API-03)
# ---------------------------------------------------------------------------


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
    assert data["events"]["_type"] == "tuple"


def test_pitch_retrograde_response_format(client: TestClient) -> None:
    """POST /v1/transform/pitch-retrograde returns phrase + events."""
    r = client.post("/v1/transform/pitch-retrograde", json={"phrase": "e c4 d4 e4"})
    assert r.status_code == 200
    data = r.json()
    assert "phrase" in data
    assert "events" in data


# ---------------------------------------------------------------------------
# Correctness tests
# ---------------------------------------------------------------------------


def test_chromatic_transpose_correctness(client: TestClient) -> None:
    """Transposing C4 up a minor third gives Eb4."""
    r = client.post(
        "/v1/transform/chromatic-transpose",
        json={"phrase": "e c4 d4 e4", "interval": "m3"},
    )
    assert r.status_code == 200
    phrase = r.json()["phrase"].lower()
    assert "eb" in phrase


def test_full_retrograde(client: TestClient) -> None:
    r = client.post("/v1/transform/full-retrograde", json={"phrase": "e c4 q d4 h e4"})
    assert r.status_code == 200
    assert "phrase" in r.json()


def test_augment(client: TestClient) -> None:
    r = client.post("/v1/transform/augment", json={"phrase": "e c4 d4", "ratio": 2.0})
    assert r.status_code == 200
    assert "phrase" in r.json()


def test_diminish(client: TestClient) -> None:
    r = client.post("/v1/transform/diminish", json={"phrase": "q c4 d4", "ratio": 2.0})
    assert r.status_code == 200
    assert "phrase" in r.json()


def test_invert(client: TestClient) -> None:
    r = client.post("/v1/transform/invert", json={"phrase": "e c4 d4 e4"})
    assert r.status_code == 200
    assert "phrase" in r.json()


def test_rotate(client: TestClient) -> None:
    r = client.post("/v1/transform/rotate", json={"phrase": "e c4 d4 e4", "n": 1})
    assert r.status_code == 200
    assert "phrase" in r.json()


def test_omit(client: TestClient) -> None:
    r = client.post("/v1/transform/omit", json={"phrase": "e c4 d4 e4 f4", "n": 2})
    assert r.status_code == 200
    assert "phrase" in r.json()


def test_repeat(client: TestClient) -> None:
    r = client.post("/v1/transform/repeat", json={"phrase": "e c4 d4", "n": 2})
    assert r.status_code == 200
    assert "phrase" in r.json()


def test_mirror(client: TestClient) -> None:
    r = client.post("/v1/transform/mirror", json={"phrase": "e c4 d4 e4"})
    assert r.status_code == 200
    assert "phrase" in r.json()


def test_interpolate(client: TestClient) -> None:
    r = client.post("/v1/transform/interpolate", json={"phrase": "e c4 e4", "steps": 1})
    assert r.status_code == 200
    assert "phrase" in r.json()


def test_permute(client: TestClient) -> None:
    r = client.post(
        "/v1/transform/permute", json={"phrase": "e c4 d4 e4", "indices": [2, 0, 1]}
    )
    assert r.status_code == 200
    assert "phrase" in r.json()


def test_rhythmic_rotation(client: TestClient) -> None:
    r = client.post(
        "/v1/transform/rhythmic-rotation", json={"phrase": "e c4 q d4", "n": 1}
    )
    assert r.status_code == 200
    assert "phrase" in r.json()


def test_rhythmic_retrograde(client: TestClient) -> None:
    r = client.post("/v1/transform/rhythmic-retrograde", json={"phrase": "e c4 q d4"})
    assert r.status_code == 200
    assert "phrase" in r.json()


def test_extract_rhythm(client: TestClient) -> None:
    r = client.post("/v1/transform/extract-rhythm", json={"phrase": "e c4 q d4"})
    assert r.status_code == 200
    data = r.json()
    assert "events" in data


def test_total_duration(client: TestClient) -> None:
    r = client.post("/v1/transform/total-duration", json={"phrase": "q c4 q d4"})
    assert r.status_code == 200
    data = r.json()
    assert "total" in data
    assert "numerator" in data
    assert "denominator" in data


def test_quantize(client: TestClient) -> None:
    r = client.post(
        "/v1/transform/quantize", json={"phrase": "e c4 q d4", "grid": ["q"]}
    )
    assert r.status_code == 200
    assert "phrase" in r.json()


def test_diatonic_transpose(client: TestClient) -> None:
    r = client.post(
        "/v1/transform/diatonic-transpose",
        json={"phrase": "e c4 d4 e4", "n": 2, "scale_name": "major"},
    )
    assert r.status_code == 200
    assert "phrase" in r.json()


def test_retrograde_inversion(client: TestClient) -> None:
    r = client.post(
        "/v1/transform/retrograde-inversion", json={"phrase": "e c4 d4 e4"}
    )
    assert r.status_code == 200
    assert "phrase" in r.json()


def test_metric_modulation(client: TestClient) -> None:
    r = client.post(
        "/v1/transform/metric-modulation",
        json={"phrase": "q c4 d4 e4", "old_unit": "q", "new_unit": "e"},
    )
    assert r.status_code == 200
    assert "phrase" in r.json()


# ---------------------------------------------------------------------------
# Multi-phrase endpoint tests
# ---------------------------------------------------------------------------


def test_fragment_returns_multi_phrase(client: TestClient) -> None:
    r = client.post(
        "/v1/transform/fragment",
        json={"phrase": "e c4 d4 e4 f4", "lengths": [2, 2]},
    )
    assert r.status_code == 200
    data = r.json()
    assert "phrases" in data
    assert len(data["phrases"]) == 2
    for sub in data["phrases"]:
        assert "phrase" in sub
        assert "events" in sub


def test_concatenate(client: TestClient) -> None:
    r = client.post(
        "/v1/transform/concatenate",
        json={"phrases": ["e c4 d4", "q e4 f4"]},
    )
    assert r.status_code == 200
    assert "phrase" in r.json()


def test_interleave(client: TestClient) -> None:
    r = client.post(
        "/v1/transform/interleave",
        json={"phrase": "e c4 e4", "phrase2": "e d4 f4"},
    )
    assert r.status_code == 200
    assert "phrase" in r.json()


# ---------------------------------------------------------------------------
# Stub endpoint tests
# ---------------------------------------------------------------------------


def test_pitch_map_not_implemented(client: TestClient) -> None:
    r = client.post("/v1/transform/pitch-map", json={"phrase": "e c4"})
    assert r.status_code == 422
    assert r.json()["error"] == "NOT_IMPLEMENTED"


def test_swing_not_implemented(client: TestClient) -> None:
    r = client.post("/v1/transform/swing", json={"phrase": "e c4"})
    assert r.status_code == 422
    assert r.json()["error"] == "NOT_IMPLEMENTED"


# ---------------------------------------------------------------------------
# Error handling tests (API-07)
# ---------------------------------------------------------------------------


def test_invalid_cn_returns_422(client: TestClient) -> None:
    r = client.post(
        "/v1/transform/chromatic-transpose",
        json={"phrase": "invalid garbage", "interval": "m3"},
    )
    assert r.status_code == 422
    assert r.json()["error"] == "INVALID_CN"


def test_invalid_interval_returns_422(client: TestClient) -> None:
    r = client.post(
        "/v1/transform/chromatic-transpose",
        json={"phrase": "e c4 d4", "interval": "bad"},
    )
    assert r.status_code == 422
    assert r.json()["error"] == "INVALID_INTERVAL"
