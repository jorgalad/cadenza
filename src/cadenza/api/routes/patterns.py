"""Pattern generation endpoints -- thin route handlers calling cadenza.patterns."""

from __future__ import annotations

from fastapi import APIRouter

from cadenza.api.helpers import _parse_phrase, _phrase_response, _score_response
from cadenza.api.schemas import (
    AccentPatternRequest,
    ApplyRhythmRequest,
    BinaryRhythmRequest,
    EuclideanRequest,
    HocketRequest,
    IsorhythmRequest,
    OstinatoRequest,
    RhythmicCanonRequest,
)
from cadenza.patterns import (
    accent_pattern,
    apply_rhythm,
    binary_rhythm,
    euclidean_rhythm,
    hocket,
    isorhythm,
    ostinato,
    rhythmic_canon,
)

router = APIRouter(prefix="/v1/patterns", tags=["patterns"])


# ---------------------------------------------------------------------------
# Rhythm pattern endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/euclidean-rhythm",
    response_model=None,
    summary="Generate Euclidean rhythm pattern",
    description="Distribute m active pulses as evenly as possible across n time slots using Bjorklund's algorithm.",
)
def euclidean_rhythm_endpoint(req: EuclideanRequest) -> dict:
    result = euclidean_rhythm(req.n, req.m)
    return {"pattern": list(result)}


@router.post(
    "/binary-rhythm",
    response_model=None,
    summary="Generate binary rhythm pattern",
    description="Convert an integer n to its binary representation as a boolean rhythm pattern.",
)
def binary_rhythm_endpoint(req: BinaryRhythmRequest) -> dict:
    result = binary_rhythm(req.n)
    return {"pattern": list(result)}


@router.post(
    "/apply-rhythm",
    response_model=None,
    summary="Apply rhythm pattern to pitches",
    description="Combine a boolean rhythm pattern with a CN pitch phrase, inserting rests for False slots.",
)
def apply_rhythm_endpoint(req: ApplyRhythmRequest) -> dict:
    pitches = _parse_phrase(req.pitches)
    result = apply_rhythm(tuple(req.rhythm), pitches)
    return _phrase_response(result)


@router.post(
    "/isorhythm",
    response_model=None,
    summary="Generate isorhythmic pattern",
    description="Combine a rhythmic talea pattern with a pitch color pattern, cycling to the specified length or LCM.",
)
def isorhythm_endpoint(req: IsorhythmRequest) -> dict:
    talea = _parse_phrase(req.talea)
    color = _parse_phrase(req.color)
    result = isorhythm(talea, color, req.length)
    return _phrase_response(result)


@router.post(
    "/ostinato",
    response_model=None,
    summary="Generate ostinato repetition",
    description="Repeat a CN phrase n times to create an ostinato pattern.",
)
def ostinato_endpoint(req: OstinatoRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = ostinato(phrase, req.n)
    return _phrase_response(result)


@router.post(
    "/accent-pattern",
    response_model=None,
    summary="Apply accent pattern to phrase",
    description="Add accent articulation to every Nth note in a phrase.",
)
def accent_pattern_endpoint(req: AccentPatternRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = accent_pattern(phrase, req.n)
    return _phrase_response(result)


# ---------------------------------------------------------------------------
# Multi-voice pattern endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/rhythmic-canon",
    response_model=None,
    summary="Generate rhythmic canon",
    description="Create a multi-voice canon by staggering entries of the same phrase at a time offset.",
)
def rhythmic_canon_endpoint(req: RhythmicCanonRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    # Parse offset duration by creating a tiny CN snippet
    offset_phrase = _parse_phrase(f"{req.offset} c4")
    offset_dur = offset_phrase[0].duration
    result = rhythmic_canon(phrase, req.n, offset_dur)
    return _score_response(result)


@router.post(
    "/hocket",
    response_model=None,
    summary="Split phrase into hocket voices",
    description="Distribute notes round-robin across n voices, filling gaps with rests.",
)
def hocket_endpoint(req: HocketRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = hocket(phrase, req.n)
    return _score_response(result)
