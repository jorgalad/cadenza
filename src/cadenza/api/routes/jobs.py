"""Job polling endpoint -- check status of async counterpoint jobs."""

from __future__ import annotations

import time

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from cadenza.api.routes.counterpoint import _JOB_TTL, _jobs

router = APIRouter(prefix="/v1/jobs", tags=["jobs"])


@router.get(
    "/{job_id}",
    response_model=None,
    summary="Check async job status",
    description="Poll for the result of a previously submitted async counterpoint job.",
)
def get_job_status(job_id: str) -> dict | JSONResponse:
    job = _jobs.get(job_id)
    if job is None:
        return JSONResponse(
            status_code=404,
            content={"error": "JOB_NOT_FOUND", "message": f"No job with id '{job_id}'"},
        )

    # Check TTL expiry for finished jobs
    if job["finished_at"] is not None and time.monotonic() - job["finished_at"] > _JOB_TTL:
        del _jobs[job_id]
        return JSONResponse(
            status_code=410,
            content={"error": "JOB_EXPIRED", "message": f"Job '{job_id}' has expired after {_JOB_TTL}s"},
        )

    return {
        "job_id": job_id,
        "status": job["status"],
        "result": job["result"],
        "error": job["error"],
    }
