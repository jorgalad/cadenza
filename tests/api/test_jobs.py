"""Integration tests for job polling endpoints."""

from __future__ import annotations

import time

from fastapi.testclient import TestClient


def test_job_not_found(client: TestClient) -> None:
    r = client.get("/v1/jobs/nonexistent")
    assert r.status_code == 404
    data = r.json()
    assert data["error"] == "JOB_NOT_FOUND"


def test_job_submit_and_complete(client: TestClient) -> None:
    # Submit async counterpoint job
    r = client.post(
        "/v1/counterpoint/generate-first-species/async",
        json={"phrase": "w c4 d4 e4 f4 g4 a4 g4 f4 e4 d4 c4"},
    )
    assert r.status_code == 200
    job_id = r.json()["job_id"]

    # Poll until done
    for _ in range(20):
        r = client.get(f"/v1/jobs/{job_id}")
        assert r.status_code == 200
        status = r.json()["status"]
        if status in ("done", "failed"):
            break
        time.sleep(0.2)

    data = r.json()
    assert data["status"] in ("done", "failed")
    if data["status"] == "done":
        assert data["result"] is not None


def test_job_expiry(client: TestClient) -> None:
    # Submit a job
    r = client.post(
        "/v1/counterpoint/generate-first-species/async",
        json={"phrase": "w c4 d4 e4 f4 g4 a4 g4 f4 e4 d4 c4"},
    )
    job_id = r.json()["job_id"]

    # Wait for completion
    for _ in range(20):
        r = client.get(f"/v1/jobs/{job_id}")
        if r.json()["status"] in ("done", "failed"):
            break
        time.sleep(0.2)

    # Manually set finished_at far in the past to simulate expiry
    from cadenza.api.routes.counterpoint import _jobs
    if job_id in _jobs and _jobs[job_id]["finished_at"] is not None:
        _jobs[job_id]["finished_at"] = time.monotonic() - 1000

    r = client.get(f"/v1/jobs/{job_id}")
    assert r.status_code == 410
    assert r.json()["error"] == "JOB_EXPIRED"


def test_job_pending_status(client: TestClient) -> None:
    r = client.post(
        "/v1/counterpoint/generate-first-species/async",
        json={"phrase": "w c4 d4 e4 f4 g4 a4 g4 f4 e4 d4 c4"},
    )
    assert r.status_code == 200
    job_id = r.json()["job_id"]

    # Immediately poll -- should be pending or running
    r = client.get(f"/v1/jobs/{job_id}")
    assert r.status_code == 200
    assert r.json()["status"] in ("pending", "running", "done", "failed")
