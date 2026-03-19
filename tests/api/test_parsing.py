"""Unit tests for cadenza.api.parsing -- pitch and interval string parsers."""

from __future__ import annotations

import pytest

from cadenza.api.parsing import parse_interval_string, parse_pitch_string
from cadenza.core.interval import Interval
from cadenza.core.pitch import Pitch


# --- parse_pitch_string ---


def test_parse_pitch_string_natural() -> None:
    """'c4' -> natural C4."""
    assert parse_pitch_string("c4") == Pitch(step="c", accidental="n", octave=4)


def test_parse_pitch_string_flat() -> None:
    """'eb4' -> E-flat 4."""
    assert parse_pitch_string("eb4") == Pitch(step="e", accidental="b", octave=4)


def test_parse_pitch_string_sharp() -> None:
    """'fs5' -> F-sharp 5."""
    assert parse_pitch_string("fs5") == Pitch(step="f", accidental="s", octave=5)


def test_parse_pitch_string_double_sharp() -> None:
    """'css3' -> C-double-sharp 3."""
    assert parse_pitch_string("css3") == Pitch(step="c", accidental="ss", octave=3)


def test_parse_pitch_string_double_flat() -> None:
    """'dbb2' -> D-double-flat 2."""
    assert parse_pitch_string("dbb2") == Pitch(step="d", accidental="bb", octave=2)


def test_parse_pitch_string_uppercase_ok() -> None:
    """Input is case-insensitive."""
    assert parse_pitch_string("Eb4") == Pitch(step="e", accidental="b", octave=4)


def test_parse_pitch_string_invalid_step() -> None:
    """Invalid step letter raises ValueError."""
    with pytest.raises(ValueError, match="Invalid pitch string"):
        parse_pitch_string("xb4")


def test_parse_pitch_string_no_octave() -> None:
    """Missing octave raises ValueError."""
    with pytest.raises(ValueError, match="Invalid pitch string"):
        parse_pitch_string("eb")


# --- parse_interval_string ---


def test_parse_interval_string_minor() -> None:
    """'m3' -> minor third ascending."""
    assert parse_interval_string("m3") == Interval(quality="m", number=3, direction=1)


def test_parse_interval_string_perfect() -> None:
    """'P5' -> perfect fifth ascending."""
    assert parse_interval_string("P5") == Interval(quality="P", number=5, direction=1)


def test_parse_interval_string_augmented() -> None:
    """'A4' -> augmented fourth ascending."""
    assert parse_interval_string("A4") == Interval(quality="A", number=4, direction=1)


def test_parse_interval_string_diminished() -> None:
    """'d5' -> diminished fifth ascending."""
    assert parse_interval_string("d5") == Interval(quality="d", number=5, direction=1)


def test_parse_interval_string_double_aug() -> None:
    """'AA4' -> doubly-augmented fourth ascending."""
    assert parse_interval_string("AA4") == Interval(quality="AA", number=4, direction=1)


def test_parse_interval_string_double_dim() -> None:
    """'dd7' -> doubly-diminished seventh ascending."""
    assert parse_interval_string("dd7") == Interval(quality="dd", number=7, direction=1)


def test_parse_interval_string_invalid() -> None:
    """Invalid interval string raises ValueError."""
    with pytest.raises(ValueError, match="Invalid interval string"):
        parse_interval_string("x3")


def test_parse_interval_string_major() -> None:
    """'M3' -> major third ascending."""
    assert parse_interval_string("M3") == Interval(quality="M", number=3, direction=1)
