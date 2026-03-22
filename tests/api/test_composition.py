"""Integration tests for composition endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_markov_generate(client: TestClient) -> None:
    r = client.post(
        "/v1/composition/markov-generate",
        json={
            "phrase": "q c4 d4 e4 f4 g4 f4 e4 d4 c4",
            "order": 1,
            "length": 8,
            "seed": 42,
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert "phrase" in data


def test_random_walk(client: TestClient) -> None:
    r = client.post(
        "/v1/composition/random-walk",
        json={
            "start": "c4",
            "length": 8,
            "scale_root": "c4",
            "scale_name": "major",
            "max_step": 2,
            "seed": 42,
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert "phrase" in data


def test_generate_variations(client: TestClient) -> None:
    r = client.post(
        "/v1/composition/generate-variations",
        json={"phrase": "q c4 d4 e4 f4", "n": 3},
    )
    assert r.status_code == 200
    data = r.json()
    assert "variations" in data
    assert len(data["variations"]) == 3


def test_probabilistic_melody(client: TestClient) -> None:
    r = client.post(
        "/v1/composition/probabilistic-melody",
        json={"weights": {"c4": 0.5, "d4": 0.3, "e4": 0.2}, "length": 5, "seed": 42},
    )
    assert r.status_code == 200
    data = r.json()
    assert "phrase" in data


def test_tendency_mask_not_implemented(client: TestClient) -> None:
    r = client.post(
        "/v1/composition/tendency-mask-melody",
        json={"phrase": "q c4"},
    )
    assert r.status_code == 422
    assert r.json()["error"] == "NOT_IMPLEMENTED"


def test_train_markov(client: TestClient) -> None:
    r = client.post(
        "/v1/composition/train-markov",
        json={"phrase": "q c4 d4 e4 f4 g4 f4 e4 d4 c4", "order": 1},
    )
    assert r.status_code == 200
    data = r.json()
    assert "order" in data
    assert "transition_table" in data


def test_lsystem_melody(client: TestClient) -> None:
    r = client.post(
        "/v1/composition/lsystem-melody",
        json={
            "axiom": "A",
            "rules": {"A": "AB", "B": "A"},
            "alphabet": {"A": "q c4", "B": "e d4"},
            "generations": 3,
        },
    )
    assert r.status_code == 200
    assert "phrase" in r.json()
