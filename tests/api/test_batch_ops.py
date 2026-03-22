"""Integration tests for batch operations endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_set_articulation_nth(client: TestClient) -> None:
    r = client.post(
        "/v1/batch-ops/set-articulation-nth",
        json={"phrase": "q c4 d4 e4 f4", "n": 2, "articulation": "staccato"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "phrase" in data
    assert "events" in data


def test_set_dynamic_nth(client: TestClient) -> None:
    r = client.post(
        "/v1/batch-ops/set-dynamic-nth",
        json={"phrase": "q c4 d4 e4 f4", "n": 1, "dynamic": "ff"},
    )
    assert r.status_code == 200
    assert "phrase" in r.json()


def test_crescendo(client: TestClient) -> None:
    r = client.post(
        "/v1/batch-ops/crescendo",
        json={"phrase": "q c4 d4 e4 f4", "start": "pp", "end": "ff"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "phrase" in data


def test_decrescendo(client: TestClient) -> None:
    r = client.post(
        "/v1/batch-ops/decrescendo",
        json={"phrase": "q c4 d4 e4 f4", "start": "ff", "end": "pp"},
    )
    assert r.status_code == 200
    assert "phrase" in r.json()


def test_replace_pitch(client: TestClient) -> None:
    r = client.post(
        "/v1/batch-ops/replace-pitch",
        json={"phrase": "q c4 d4 c4 e4", "old_pitch": "c4", "new_pitch": "g4"},
    )
    assert r.status_code == 200
    assert "phrase" in r.json()


def test_humanize(client: TestClient) -> None:
    r = client.post(
        "/v1/batch-ops/humanize",
        json={"phrase": "q c4 d4 e4", "seed": 42},
    )
    assert r.status_code == 200
    assert "phrase" in r.json()


def test_quantize_lengths(client: TestClient) -> None:
    r = client.post(
        "/v1/batch-ops/quantize-lengths",
        json={"phrase": "q c4 e d4", "grid": "q"},
    )
    assert r.status_code == 200
    assert "phrase" in r.json()


def test_apply_windowed_not_implemented(client: TestClient) -> None:
    r = client.post(
        "/v1/batch-ops/apply-windowed",
        json={"phrase": "q c4 d4"},
    )
    assert r.status_code == 422
    assert r.json()["error"] == "NOT_IMPLEMENTED"


def test_filter_phrase(client: TestClient) -> None:
    r = client.post(
        "/v1/batch-ops/filter-phrase",
        json={"phrase": "q c4 d4 e4", "is_note": True},
    )
    assert r.status_code == 200
    assert "phrase" in r.json()
