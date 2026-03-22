"""Shared route handler helpers -- parse and serialize CN phrases and scores."""

from __future__ import annotations

from cadenza.api.errors import INVALID_INTERVAL, INVALID_PITCH, CadenzaAPIError
from cadenza.api.parsing import parse_interval_string, parse_pitch_string
from cadenza.cn import parse_cn, to_cn
from cadenza.core.interval import Interval
from cadenza.core.json_codec import _to_serializable
from cadenza.core.pitch import Pitch
from cadenza.core.score import Score

# CN accidental mapping: internal representation -> CN notation
_ACC_TO_CN: dict[str, str] = {"n": "", "s": "s", "b": "b", "ss": "ss", "bb": "bb"}


def _parse_phrase(cn_string: str) -> tuple:
    """Parse CN string, return phrase (discard warnings)."""
    phrase, _warnings = parse_cn(cn_string)
    return phrase


def _phrase_response(phrase: tuple) -> dict:
    """Build standard {phrase, events} response dict."""
    return {"phrase": to_cn(phrase), "events": _to_serializable(phrase)}


def _score_response(score: Score) -> dict:
    """Serialize Score to {voices: [{name, phrase, events}]}."""
    voices = []
    for name, phrase in score._voices:
        voices.append({
            "name": name,
            "phrase": to_cn(phrase),
            "events": _to_serializable(phrase),
        })
    return {"voices": voices}


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


def _safe_parse_interval(s: str) -> Interval:
    """Parse interval string with specific error code on failure."""
    try:
        return parse_interval_string(s)
    except ValueError as e:
        raise CadenzaAPIError(INVALID_INTERVAL, str(e), s)


def _pitch_tuple_response(pitches: tuple[Pitch, ...]) -> dict:
    """Build standard {phrase, events} response for pitch tuples."""
    return {
        "phrase": _pitches_to_cn(pitches),
        "events": [_to_serializable(p) for p in pitches],
    }
