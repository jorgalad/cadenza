"""Theory endpoints -- thin route handlers calling cadenza.theory."""

from __future__ import annotations

from fastapi import APIRouter

from cadenza.api.errors import (
    INVALID_CHORD_SYMBOL,
    INVALID_PITCH,
    INVALID_SCALE_NAME,
    CadenzaAPIError,
)
from cadenza.api.parsing import parse_pitch_string
from cadenza.api.schemas import (
    Aug6Request,
    ChordRequest,
    DiatonicChordsRequest,
    NeapolitanRequest,
    ScaleRequest,
    SecondaryDominantRequest,
)
from cadenza.core.json_codec import _to_serializable
from cadenza.core.pitch import Pitch
from cadenza.theory import (
    aug6_chord,
    diatonic_chords,
    get_chord,
    get_scale,
    neapolitan_chord,
    secondary_dominant,
)

router = APIRouter(prefix="/v1/theory", tags=["theory"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# CN accidental mapping: internal representation -> CN notation
_ACC_TO_CN: dict[str, str] = {
    "n": "",
    "s": "s",
    "b": "b",
    "ss": "ss",
    "bb": "bb",
}


def _pitch_to_cn(p: Pitch) -> str:
    """Convert a Pitch to its CN string representation."""
    acc = _ACC_TO_CN.get(p.accidental, p.accidental)
    return f"{p.step}{acc}{p.octave}"


def _pitches_to_cn(pitches: tuple[Pitch, ...]) -> str:
    """Convert a tuple of Pitches to a space-separated CN string."""
    return " ".join(_pitch_to_cn(p) for p in pitches)


def _safe_parse_pitch(s: str) -> Pitch:
    """Parse pitch string with specific error code on failure."""
    try:
        return parse_pitch_string(s)
    except ValueError as e:
        raise CadenzaAPIError(INVALID_PITCH, str(e), s)


def _pitch_tuple_response(pitches: tuple[Pitch, ...]) -> dict:
    """Build standard {phrase, events} response for pitch tuples."""
    return {
        "phrase": _pitches_to_cn(pitches),
        "events": [_to_serializable(p) for p in pitches],
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/scale", response_model=None, summary="Look up scale pitches by root and name")
def scale_endpoint(req: ScaleRequest) -> dict:
    root = _safe_parse_pitch(req.root)
    try:
        scale = get_scale(root, req.name)
    except ValueError as e:
        raise CadenzaAPIError(INVALID_SCALE_NAME, str(e), req.name)
    return {
        "phrase": _pitches_to_cn(scale.pitches),
        "events": [_to_serializable(p) for p in scale.pitches],
    }


@router.post("/chord", response_model=None, summary="Build chord voicing from root and symbol")
def chord_endpoint(req: ChordRequest) -> dict:
    root = _safe_parse_pitch(req.root)
    try:
        pitches = get_chord(root, req.symbol, req.inversion)
    except ValueError as e:
        raise CadenzaAPIError(INVALID_CHORD_SYMBOL, str(e), req.symbol)
    return _pitch_tuple_response(pitches)


@router.post("/diatonic-chords", response_model=None, summary="Build diatonic chords for every scale degree")
def diatonic_chords_endpoint(req: DiatonicChordsRequest) -> dict:
    root = _safe_parse_pitch(req.root)
    try:
        chords = diatonic_chords(root, req.scale_name, req.quality)
    except ValueError as e:
        raise CadenzaAPIError(INVALID_SCALE_NAME, str(e), req.scale_name)
    return {
        "phrases": [_pitch_tuple_response(chord) for chord in chords],
    }


@router.post("/secondary-dominant", response_model=None, summary="Build secondary dominant (V7) of a scale degree")
def secondary_dominant_endpoint(req: SecondaryDominantRequest) -> dict:
    root = _safe_parse_pitch(req.root)
    pitches = secondary_dominant(req.degree, root, req.key_name)
    return _pitch_tuple_response(pitches)


@router.post("/aug6", response_model=None, summary="Build augmented sixth chord")
def aug6_endpoint(req: Aug6Request) -> dict:
    root = _safe_parse_pitch(req.root)
    pitches = aug6_chord(req.aug6_type, root, req.key_name)
    return _pitch_tuple_response(pitches)


@router.post("/neapolitan", response_model=None, summary="Build Neapolitan chord (bII)")
def neapolitan_endpoint(req: NeapolitanRequest) -> dict:
    root = _safe_parse_pitch(req.root)
    pitches = neapolitan_chord(root, req.key_name)
    return _pitch_tuple_response(pitches)
