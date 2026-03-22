"""Integration tests for the batch dispatcher endpoint."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_batch_multiple_operations(client: TestClient) -> None:
    r = client.post(
        "/v1/batch",
        json={
            "operations": [
                {"operation": "mirror", "params": {"phrase": "q c4 d4 e4"}},
                {"operation": "detect-key", "params": {"phrase": "q c4 e4 g4 c5"}},
                {"operation": "euclidean-rhythm", "params": {"n": 3, "m": 8}},
            ]
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert len(data["results"]) == 3
    for item in data["results"]:
        assert item["status"] == "ok"


def test_batch_continue_on_error(client: TestClient) -> None:
    r = client.post(
        "/v1/batch",
        json={
            "operations": [
                {"operation": "mirror", "params": {"phrase": "q c4 d4 e4"}},
                {"operation": "chromatic-transpose", "params": {"phrase": "invalid garbage", "interval": "P5"}},
                {"operation": "detect-key", "params": {"phrase": "q c4 e4 g4 c5"}},
            ]
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert len(data["results"]) == 3
    assert data["results"][0]["status"] == "ok"
    assert data["results"][1]["status"] == "error"
    assert data["results"][2]["status"] == "ok"


def test_batch_unknown_operation(client: TestClient) -> None:
    r = client.post(
        "/v1/batch",
        json={
            "operations": [
                {"operation": "nonexistent-op", "params": {}},
            ]
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["results"][0]["status"] == "error"
    assert data["results"][0]["error"]["error"] == "UNKNOWN_OPERATION"


def test_batch_too_large(client: TestClient) -> None:
    r = client.post(
        "/v1/batch",
        json={
            "operations": [
                {"operation": "mirror", "params": {"phrase": "q c4"}}
            ]
            * 51
        },
    )
    assert r.status_code == 422
    assert "BATCH_TOO_LARGE" in r.json().get("error", "")


def test_batch_empty(client: TestClient) -> None:
    r = client.post("/v1/batch", json={"operations": []})
    assert r.status_code == 200
    data = r.json()
    assert data["results"] == []
