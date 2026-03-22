"""Integration tests for pattern generation endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_euclidean_rhythm(client: TestClient) -> None:
    # n=active pulses, m=total slots per library convention
    r = client.post("/v1/patterns/euclidean-rhythm", json={"n": 3, "m": 8})
    assert r.status_code == 200
    data = r.json()
    assert "pattern" in data
    assert isinstance(data["pattern"], list)
    assert len(data["pattern"]) == 8
    assert sum(data["pattern"]) == 3


def test_binary_rhythm(client: TestClient) -> None:
    r = client.post("/v1/patterns/binary-rhythm", json={"n": 5})
    assert r.status_code == 200
    data = r.json()
    assert "pattern" in data
    assert isinstance(data["pattern"], list)


def test_ostinato(client: TestClient) -> None:
    r = client.post(
        "/v1/patterns/ostinato",
        json={"phrase": "q c4 d4", "n": 3},
    )
    assert r.status_code == 200
    data = r.json()
    assert "phrase" in data


def test_rhythmic_canon(client: TestClient) -> None:
    r = client.post(
        "/v1/patterns/rhythmic-canon",
        json={"phrase": "q c4 d4 e4", "n": 2, "offset": "q"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "voices" in data
    assert len(data["voices"]) == 2


def test_hocket(client: TestClient) -> None:
    r = client.post(
        "/v1/patterns/hocket",
        json={"phrase": "q c4 d4 e4 f4", "n": 2},
    )
    assert r.status_code == 200
    data = r.json()
    assert "voices" in data
    assert len(data["voices"]) == 2


def test_accent_pattern(client: TestClient) -> None:
    r = client.post(
        "/v1/patterns/accent-pattern",
        json={"phrase": "q c4 d4 e4 f4", "n": 2},
    )
    assert r.status_code == 200
    assert "phrase" in r.json()


def test_apply_rhythm(client: TestClient) -> None:
    r = client.post(
        "/v1/patterns/apply-rhythm",
        json={"rhythm": [True, False, True, True], "pitches": "q c4 d4 e4"},
    )
    assert r.status_code == 200
    assert "phrase" in r.json()
