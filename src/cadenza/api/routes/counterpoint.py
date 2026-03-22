"""Counterpoint endpoints -- sync and async generation with job-based polling."""

from __future__ import annotations

import threading
import time
import uuid

from fastapi import APIRouter

from cadenza.api.helpers import _parse_phrase, _phrase_response, _score_response
from cadenza.api.schemas import (
    CheckCounterpointRequest,
    CounterpointRequest,
    MultiVoiceCounterpointRequest,
)
from cadenza.core.score import Score
from cadenza.counterpoint import (
    check_counterpoint,
    generate_fifth_species,
    generate_first_species,
    generate_fourth_species,
    generate_free_counterpoint,
    generate_multi_voice_counterpoint,
    generate_second_species,
    generate_third_species,
)

router = APIRouter(prefix="/v1/counterpoint", tags=["counterpoint"])

# ---------------------------------------------------------------------------
# Shared job store (imported by jobs.py for polling)
# ---------------------------------------------------------------------------

_jobs: dict[str, dict] = {}
_JOB_TTL = 300  # 5 minutes after done/failed


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _counterpoint_score_response(cf: tuple, cp: tuple, above: bool) -> dict:
    """Wrap CF + counterpoint Phrase into ScoreResponse format."""
    if above:
        score = Score(_voices=(("counterpoint", cp), ("cantus_firmus", cf)))
    else:
        score = Score(_voices=(("cantus_firmus", cf), ("counterpoint", cp)))
    return _score_response(score)


def _run_job(job_id: str, func, cf, above: bool) -> None:
    """Execute counterpoint generation in background thread."""
    _jobs[job_id]["status"] = "running"
    try:
        result = func(cf, above=above)
        _jobs[job_id]["result"] = _counterpoint_score_response(cf, result, above)
        _jobs[job_id]["status"] = "done"
    except Exception as e:
        _jobs[job_id]["error"] = {"error": type(e).__name__, "message": str(e)}
        _jobs[job_id]["status"] = "failed"
    _jobs[job_id]["finished_at"] = time.monotonic()


def _run_multi_job(job_id: str, cf, n: int, species: int, above_count: int | None) -> None:
    """Execute multi-voice counterpoint generation in background thread."""
    _jobs[job_id]["status"] = "running"
    try:
        result = generate_multi_voice_counterpoint(cf, n, species, above_count)
        _jobs[job_id]["result"] = _score_response(result)
        _jobs[job_id]["status"] = "done"
    except Exception as e:
        _jobs[job_id]["error"] = {"error": type(e).__name__, "message": str(e)}
        _jobs[job_id]["status"] = "failed"
    _jobs[job_id]["finished_at"] = time.monotonic()


def _submit_async(func, req_phrase: str, above: bool = True) -> dict:
    """Submit a single-voice counterpoint job for background execution."""
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"status": "pending", "result": None, "error": None, "finished_at": None}
    cf = _parse_phrase(req_phrase)
    t = threading.Thread(target=_run_job, args=(job_id, func, cf, above), daemon=True)
    t.start()
    return {"job_id": job_id, "status": "pending"}


def _submit_multi_async(req_phrase: str, n: int, species: int, above: int | None) -> dict:
    """Submit a multi-voice counterpoint job for background execution."""
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"status": "pending", "result": None, "error": None, "finished_at": None}
    cf = _parse_phrase(req_phrase)
    t = threading.Thread(target=_run_multi_job, args=(job_id, cf, n, species, above), daemon=True)
    t.start()
    return {"job_id": job_id, "status": "pending"}


# ---------------------------------------------------------------------------
# Sync endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/generate-first-species",
    response_model=None,
    summary="Generate first species counterpoint",
    description="Generate note-against-note counterpoint above or below a cantus firmus.",
)
def generate_first_species_endpoint(req: CounterpointRequest) -> dict:
    cf = _parse_phrase(req.phrase)
    result = generate_first_species(cf, above=req.above)
    return _counterpoint_score_response(cf, result, req.above)


@router.post(
    "/generate-second-species",
    response_model=None,
    summary="Generate second species counterpoint",
    description="Generate two-notes-against-one counterpoint above or below a cantus firmus.",
)
def generate_second_species_endpoint(req: CounterpointRequest) -> dict:
    cf = _parse_phrase(req.phrase)
    result = generate_second_species(cf, above=req.above)
    return _counterpoint_score_response(cf, result, req.above)


@router.post(
    "/generate-third-species",
    response_model=None,
    summary="Generate third species counterpoint",
    description="Generate four-notes-against-one counterpoint above or below a cantus firmus.",
)
def generate_third_species_endpoint(req: CounterpointRequest) -> dict:
    cf = _parse_phrase(req.phrase)
    result = generate_third_species(cf, above=req.above)
    return _counterpoint_score_response(cf, result, req.above)


@router.post(
    "/generate-fourth-species",
    response_model=None,
    summary="Generate fourth species counterpoint",
    description="Generate suspension-based counterpoint above or below a cantus firmus.",
)
def generate_fourth_species_endpoint(req: CounterpointRequest) -> dict:
    cf = _parse_phrase(req.phrase)
    result = generate_fourth_species(cf, above=req.above)
    return _counterpoint_score_response(cf, result, req.above)


@router.post(
    "/generate-fifth-species",
    response_model=None,
    summary="Generate fifth species counterpoint",
    description="Generate florid counterpoint (mixed note values) above or below a cantus firmus.",
)
def generate_fifth_species_endpoint(req: CounterpointRequest) -> dict:
    cf = _parse_phrase(req.phrase)
    result = generate_fifth_species(cf, above=req.above)
    return _counterpoint_score_response(cf, result, req.above)


@router.post(
    "/generate-free-counterpoint",
    response_model=None,
    summary="Generate free counterpoint",
    description="Generate free (unconstrained species) counterpoint above or below a cantus firmus.",
)
def generate_free_counterpoint_endpoint(req: CounterpointRequest) -> dict:
    cf = _parse_phrase(req.phrase)
    result = generate_free_counterpoint(cf, above=req.above)
    return _counterpoint_score_response(cf, result, req.above)


@router.post(
    "/generate-multi-voice",
    response_model=None,
    summary="Generate multi-voice counterpoint",
    description="Generate multiple counterpoint voices around a cantus firmus, returned as a Score.",
)
def generate_multi_voice_endpoint(req: MultiVoiceCounterpointRequest) -> dict:
    cf = _parse_phrase(req.phrase)
    result = generate_multi_voice_counterpoint(cf, req.n, req.species, req.above)
    return _score_response(result)


@router.post(
    "/check-counterpoint",
    response_model=None,
    summary="Check counterpoint for rule violations",
    description="Validate counterpoint against species rules and return any violations.",
)
def check_counterpoint_endpoint(req: CheckCounterpointRequest) -> dict:
    cf = _parse_phrase(req.cantus_firmus)
    cp = _parse_phrase(req.counterpoint)
    violations = check_counterpoint(cf, cp, req.species, req.rules)
    return {
        "violations": [
            {
                "rule": v.rule,
                "species": v.species,
                "position": v.position,
                "severity": v.severity,
            }
            for v in violations
        ]
    }


# ---------------------------------------------------------------------------
# Async endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/generate-first-species/async",
    response_model=None,
    summary="Async first species counterpoint",
    description="Submit first species counterpoint generation as a background job.",
)
def generate_first_species_async(req: CounterpointRequest) -> dict:
    return _submit_async(generate_first_species, req.phrase, req.above)


@router.post(
    "/generate-second-species/async",
    response_model=None,
    summary="Async second species counterpoint",
    description="Submit second species counterpoint generation as a background job.",
)
def generate_second_species_async(req: CounterpointRequest) -> dict:
    return _submit_async(generate_second_species, req.phrase, req.above)


@router.post(
    "/generate-third-species/async",
    response_model=None,
    summary="Async third species counterpoint",
    description="Submit third species counterpoint generation as a background job.",
)
def generate_third_species_async(req: CounterpointRequest) -> dict:
    return _submit_async(generate_third_species, req.phrase, req.above)


@router.post(
    "/generate-fourth-species/async",
    response_model=None,
    summary="Async fourth species counterpoint",
    description="Submit fourth species counterpoint generation as a background job.",
)
def generate_fourth_species_async(req: CounterpointRequest) -> dict:
    return _submit_async(generate_fourth_species, req.phrase, req.above)


@router.post(
    "/generate-fifth-species/async",
    response_model=None,
    summary="Async fifth species counterpoint",
    description="Submit fifth species counterpoint generation as a background job.",
)
def generate_fifth_species_async(req: CounterpointRequest) -> dict:
    return _submit_async(generate_fifth_species, req.phrase, req.above)


@router.post(
    "/generate-free-counterpoint/async",
    response_model=None,
    summary="Async free counterpoint",
    description="Submit free counterpoint generation as a background job.",
)
def generate_free_counterpoint_async(req: CounterpointRequest) -> dict:
    return _submit_async(generate_free_counterpoint, req.phrase, req.above)


@router.post(
    "/generate-multi-voice/async",
    response_model=None,
    summary="Async multi-voice counterpoint",
    description="Submit multi-voice counterpoint generation as a background job.",
)
def generate_multi_voice_async(req: MultiVoiceCounterpointRequest) -> dict:
    return _submit_multi_async(req.phrase, req.n, req.species, req.above)
