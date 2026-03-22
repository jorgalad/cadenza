"""Integration tests for set theory endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_prime_form(client: TestClient) -> None:
    r = client.post("/v1/settheory/prime-form", json={"pcs": [0, 1, 3, 7]})
    assert r.status_code == 200
    data = r.json()
    assert "prime_form" in data
    assert isinstance(data["prime_form"], list)


def test_forte_number(client: TestClient) -> None:
    r = client.post("/v1/settheory/forte-number", json={"pcs": [0, 1, 3, 7]})
    assert r.status_code == 200
    data = r.json()
    assert "forte_number" in data
    assert isinstance(data["forte_number"], str)


def test_complement(client: TestClient) -> None:
    r = client.post("/v1/settheory/complement", json={"pcs": [0, 1, 2, 3, 4, 5]})
    assert r.status_code == 200
    data = r.json()
    assert "complement" in data
    # Complement of 6 pcs should have 6 pcs
    assert len(data["complement"]) == 6


def test_tone_row(client: TestClient) -> None:
    r = client.post(
        "/v1/settheory/tone-row",
        json={"pcs": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]},
    )
    assert r.status_code == 200
    data = r.json()
    assert "row" in data
    assert "matrix" in data
    assert len(data["matrix"]) == 12


def test_realize_row(client: TestClient) -> None:
    r = client.post(
        "/v1/settheory/realize-row",
        json={"row_form": [0, 2, 4, 5, 7, 9, 11, 1, 3, 6, 8, 10], "base_octave": 4},
    )
    assert r.status_code == 200
    data = r.json()
    assert "phrase" in data


def test_is_z_related(client: TestClient) -> None:
    r = client.post(
        "/v1/settheory/is-z-related",
        json={"pcs_a": [0, 1, 4, 6], "pcs_b": [0, 1, 3, 7]},
    )
    assert r.status_code == 200
    data = r.json()
    assert "result" in data
    assert isinstance(data["result"], bool)


def test_interval_vector(client: TestClient) -> None:
    r = client.post("/v1/settheory/interval-vector", json={"pcs": [0, 1, 3, 7]})
    assert r.status_code == 200
    data = r.json()
    assert "interval_vector" in data
    assert len(data["interval_vector"]) == 6


def test_transpose_pcs(client: TestClient) -> None:
    r = client.post(
        "/v1/settheory/transpose-pcs",
        json={"pcs": [0, 3, 7], "n": 5},
    )
    assert r.status_code == 200
    data = r.json()
    assert "transposed" in data


def test_is_subset(client: TestClient) -> None:
    r = client.post(
        "/v1/settheory/is-subset",
        json={"pcs_a": [0, 3], "pcs_b": [0, 3, 7]},
    )
    assert r.status_code == 200
    assert r.json()["result"] is True
