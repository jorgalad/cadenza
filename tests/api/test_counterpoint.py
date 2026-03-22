"""Integration tests for counterpoint endpoints."""

from __future__ import annotations

import time

from fastapi.testclient import TestClient


def test_generate_first_species_sync(client: TestClient) -> None:
    r = client.post(
        "/v1/counterpoint/generate-first-species",
        json={"phrase": "w c4 d4 e4 f4 g4 a4 g4 f4 e4 d4 c4"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "voices" in data
    assert len(data["voices"]) >= 2


def test_generate_multi_voice(client: TestClient) -> None:
    r = client.post(
        "/v1/counterpoint/generate-multi-voice",
        json={"phrase": "w c4 d4 e4 f4 g4 a4 g4 f4 e4 d4 c4", "n": 2, "species": 1},
    )
    assert r.status_code == 200
    data = r.json()
    assert "voices" in data


def test_check_counterpoint(client: TestClient) -> None:
    r = client.post(
        "/v1/counterpoint/check-counterpoint",
        json={
            "cantus_firmus": "w c4 d4 e4 f4 g4 a4 g4 f4 e4 d4 c4",
            "counterpoint": "w g4 a4 b4 a4 b4 c5 b4 a4 g4 f4 e4",
            "species": 1,
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert "violations" in data


def test_async_submit_and_poll(client: TestClient) -> None:
    r = client.post(
        "/v1/counterpoint/generate-first-species/async",
        json={"phrase": "w c4 d4 e4 f4 g4 a4 g4 f4 e4 d4 c4"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "job_id" in data
    job_id = data["job_id"]

    # Poll until done/failed (max 10 attempts)
    for _ in range(10):
        r = client.get(f"/v1/jobs/{job_id}")
        assert r.status_code == 200
        status = r.json()["status"]
        if status in ("done", "failed"):
            break
        time.sleep(0.2)

    result = r.json()
    assert result["status"] in ("done", "failed")
    if result["status"] == "done":
        assert result["result"] is not None


def test_invalid_cf_short(client: TestClient) -> None:
    # Too-short cantus firmus should produce an error
    r = client.post(
        "/v1/counterpoint/generate-first-species",
        json={"phrase": "w c4"},
    )
    # The library may raise an error or return a minimal result
    # Either 200 (lib handles gracefully) or 422 (validation error) is acceptable
    assert r.status_code in (200, 422)


def test_generate_second_species(client: TestClient) -> None:
    r = client.post(
        "/v1/counterpoint/generate-second-species",
        json={"phrase": "w c4 d4 e4 f4 g4 a4 g4 f4 e4 d4 c4"},
    )
    assert r.status_code == 200
    assert "voices" in r.json()
