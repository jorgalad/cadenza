"""Integration tests for all theory endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_scale_lookup(client: TestClient) -> None:
    r = client.post("/v1/theory/scale", json={"root": "c4", "name": "major"})
    assert r.status_code == 200
    data = r.json()
    assert "phrase" in data
    assert "c4" in data["phrase"].lower()
    assert "events" in data
    assert isinstance(data["events"], list)


def test_chord_lookup(client: TestClient) -> None:
    r = client.post("/v1/theory/chord", json={"root": "c4", "symbol": "maj"})
    assert r.status_code == 200
    data = r.json()
    assert "phrase" in data
    assert "events" in data


def test_chord_with_inversion(client: TestClient) -> None:
    r = client.post(
        "/v1/theory/chord", json={"root": "c4", "symbol": "maj", "inversion": 1}
    )
    assert r.status_code == 200
    data = r.json()
    assert "phrase" in data


def test_diatonic_chords(client: TestClient) -> None:
    r = client.post("/v1/theory/diatonic-chords", json={"root": "c4"})
    assert r.status_code == 200
    data = r.json()
    assert "phrases" in data
    assert len(data["phrases"]) == 7
    for chord in data["phrases"]:
        assert "phrase" in chord
        assert "events" in chord


def test_secondary_dominant(client: TestClient) -> None:
    r = client.post(
        "/v1/theory/secondary-dominant",
        json={"degree": 5, "root": "c4", "key_name": "major"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "phrase" in data
    assert "events" in data


def test_aug6_italian(client: TestClient) -> None:
    r = client.post(
        "/v1/theory/aug6",
        json={"aug6_type": "italian", "root": "c4", "key_name": "major"},
    )
    assert r.status_code == 200
    assert "phrase" in r.json()


def test_neapolitan(client: TestClient) -> None:
    r = client.post(
        "/v1/theory/neapolitan", json={"root": "c4", "key_name": "major"}
    )
    assert r.status_code == 200
    assert "phrase" in r.json()


def test_unknown_scale_returns_422(client: TestClient) -> None:
    r = client.post("/v1/theory/scale", json={"root": "c4", "name": "nonexistent"})
    assert r.status_code == 422
    assert r.json()["error"] == "INVALID_SCALE_NAME"


def test_unknown_chord_returns_422(client: TestClient) -> None:
    r = client.post("/v1/theory/chord", json={"root": "c4", "symbol": "nonexistent"})
    assert r.status_code == 422
    assert r.json()["error"] == "INVALID_CHORD_SYMBOL"


def test_invalid_root_pitch_returns_422(client: TestClient) -> None:
    r = client.post("/v1/theory/scale", json={"root": "xb4", "name": "major"})
    assert r.status_code == 422
    assert r.json()["error"] == "INVALID_PITCH"
