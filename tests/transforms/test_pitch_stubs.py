"""Tests for Phase 2 stub completion: diatonic_transpose, pitch_in_scale, nearest_in_scale."""

from __future__ import annotations

import pytest

from cadenza.core.duration import Duration
from cadenza.core.note import Note
from cadenza.core.pitch import Pitch
from cadenza.theory.scales import get_scale, Scale
from cadenza.transforms.pitch import (
    diatonic_transpose,
    pitch_in_scale,
    nearest_in_scale,
)

P = Pitch


def _make_phrase(*pitches: Pitch) -> tuple[Note, ...]:
    """Create a phrase of quarter notes from pitches."""
    q = Duration.from_cn("q")
    return tuple(Note(pitch=p, duration=q) for p in pitches)


# ---------------------------------------------------------------------------
# diatonic_transpose
# ---------------------------------------------------------------------------

class TestDiatonicTranspose:
    def test_up_two_degrees_c_major(self) -> None:
        scale = get_scale(P("c", "n", 4), "major")
        phrase = _make_phrase(P("c", "n", 4), P("d", "n", 4), P("e", "n", 4))
        result = diatonic_transpose(phrase, 2, scale)
        assert result[0].pitch == P("e", "n", 4)
        assert result[1].pitch == P("f", "n", 4)
        assert result[2].pitch == P("g", "n", 4)

    def test_down_one_degree_c_major(self) -> None:
        scale = get_scale(P("c", "n", 4), "major")
        phrase = _make_phrase(P("c", "n", 4), P("d", "n", 4), P("e", "n", 4))
        result = diatonic_transpose(phrase, -1, scale)
        assert result[0].pitch == P("b", "n", 3)
        assert result[1].pitch == P("c", "n", 4)
        assert result[2].pitch == P("d", "n", 4)

    def test_across_octave_boundary(self) -> None:
        scale = get_scale(P("c", "n", 4), "major")
        phrase = _make_phrase(P("b", "n", 4))
        result = diatonic_transpose(phrase, 1, scale)
        assert result[0].pitch == P("c", "n", 5)

    def test_empty_phrase(self) -> None:
        scale = get_scale(P("c", "n", 4), "major")
        assert diatonic_transpose((), 2, scale) == ()


# ---------------------------------------------------------------------------
# pitch_in_scale
# ---------------------------------------------------------------------------

class TestPitchInScale:
    def test_c_in_c_major(self) -> None:
        scale = get_scale(P("c", "n", 4), "major")
        assert pitch_in_scale(P("c", "n", 4), scale) is True

    def test_fs_not_in_c_major(self) -> None:
        scale = get_scale(P("c", "n", 4), "major")
        assert pitch_in_scale(P("f", "s", 4), scale) is False

    def test_octave_independent(self) -> None:
        scale = get_scale(P("c", "n", 4), "major")
        assert pitch_in_scale(P("c", "n", 6), scale) is True


# ---------------------------------------------------------------------------
# nearest_in_scale
# ---------------------------------------------------------------------------

class TestNearestInScale:
    def test_fs_nearest_in_c_major(self) -> None:
        scale = get_scale(P("c", "n", 4), "major")
        result = nearest_in_scale(P("f", "s", 4), scale)
        # F# is equidistant from F and G; either is acceptable
        assert result in (P("f", "n", 4), P("g", "n", 4))

    def test_already_in_scale(self) -> None:
        scale = get_scale(P("c", "n", 4), "major")
        result = nearest_in_scale(P("c", "n", 4), scale)
        assert result == P("c", "n", 4)
