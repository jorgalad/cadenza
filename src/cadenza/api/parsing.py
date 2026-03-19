"""Compact-string-to-core-type parsing helpers for API endpoints."""

from __future__ import annotations

import re

from cadenza.core.pitch import Pitch
from cadenza.core.interval import Interval

_PITCH_RE = re.compile(r"^([a-g])(ss|bb|s|b|n)?(\d+)$")
_INTERVAL_RE = re.compile(r"^(AA|dd|[PMmAd])(\d+)$")


def parse_pitch_string(s: str) -> Pitch:
    """Parse a compact pitch string like 'eb4' into a Pitch object.

    Accepts: step (a-g) + optional accidental (ss|bb|s|b|n) + octave digit(s).
    Case-insensitive. Missing accidental defaults to natural ('n').

    Raises ValueError if the string does not match the expected format.
    """
    m = _PITCH_RE.match(s.lower())
    if not m:
        raise ValueError(f"Invalid pitch string: {s!r}")
    step, accidental, octave = m.group(1), m.group(2) or "n", int(m.group(3))
    return Pitch(step=step, accidental=accidental, octave=octave)


def parse_interval_string(s: str) -> Interval:
    """Parse a compact interval string like 'm3' or 'P5' into an Interval object.

    Accepts: quality (P|M|m|A|d|AA|dd) + number (1+). Always ascending (direction=1).

    Raises ValueError if the string does not match the expected format.
    """
    m = _INTERVAL_RE.match(s)
    if not m:
        raise ValueError(f"Invalid interval string: {s!r}")
    quality, number = m.group(1), int(m.group(2))
    return Interval(quality=quality, number=number, direction=1)
