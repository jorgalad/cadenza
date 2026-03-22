"""Tests for rhythm pattern functions: euclidean_rhythm, binary_rhythm, apply_rhythm."""

from __future__ import annotations

from fractions import Fraction

import pytest

from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest
from cadenza.patterns.rhythm import apply_rhythm, binary_rhythm, euclidean_rhythm
from cadenza.transforms.pitch import from_midi


# ---------------------------------------------------------------------------
# euclidean_rhythm
# ---------------------------------------------------------------------------


class TestEuclideanRhythm:
    def test_euclidean_tresillo(self) -> None:
        assert euclidean_rhythm(3, 8) == (
            True, False, False, True, False, False, True, False
        )

    def test_euclidean_cinquillo(self) -> None:
        assert euclidean_rhythm(5, 8) == (
            True, False, True, True, False, True, True, False
        )

    def test_euclidean_all_rests(self) -> None:
        assert euclidean_rhythm(0, 8) == (False,) * 8

    def test_euclidean_all_hits(self) -> None:
        assert euclidean_rhythm(8, 8) == (True,) * 8

    def test_euclidean_7_16(self) -> None:
        result = euclidean_rhythm(7, 16)
        assert sum(result) == 7
        assert len(result) == 16

    def test_euclidean_invalid_n_gt_m(self) -> None:
        with pytest.raises(ValueError):
            euclidean_rhythm(9, 8)

    def test_euclidean_invalid_negative(self) -> None:
        with pytest.raises(ValueError):
            euclidean_rhythm(-1, 8)


# ---------------------------------------------------------------------------
# binary_rhythm
# ---------------------------------------------------------------------------


class TestBinaryRhythm:
    def test_binary_rhythm_10110(self) -> None:
        assert binary_rhythm(0b10110) == (True, False, True, True, False)

    def test_binary_rhythm_all_ones(self) -> None:
        assert binary_rhythm(0b1111) == (True, True, True, True)

    def test_binary_rhythm_zero(self) -> None:
        assert binary_rhythm(0) == (False,)

    def test_binary_rhythm_negative(self) -> None:
        with pytest.raises(ValueError):
            binary_rhythm(-1)


# ---------------------------------------------------------------------------
# apply_rhythm
# ---------------------------------------------------------------------------


class TestApplyRhythm:
    def test_apply_rhythm_basic(self) -> None:
        result = apply_rhythm(
            pitches=(60, 64, 67),
            rhythm=(True, False, True, False, True),
        )
        assert len(result) == 5
        # Notes at indices 0, 2, 4; Rests at 1, 3
        assert isinstance(result[0], Note)
        assert isinstance(result[1], Rest)
        assert isinstance(result[2], Note)
        assert isinstance(result[3], Rest)
        assert isinstance(result[4], Note)
        # Check pitches: C4, E4, G4
        assert result[0].pitch == from_midi(60)
        assert result[2].pitch == from_midi(64)
        assert result[4].pitch == from_midi(67)

    def test_apply_rhythm_cycles_pitches(self) -> None:
        result = apply_rhythm(
            pitches=(60, 64, 67),
            rhythm=(True, True, True, True, True),
        )
        assert len(result) == 5
        expected_midi = [60, 64, 67, 60, 64]
        for i, midi in enumerate(expected_midi):
            assert isinstance(result[i], Note)
            assert result[i].pitch == from_midi(midi)

    def test_apply_rhythm_all_rests(self) -> None:
        result = apply_rhythm(
            pitches=(60, 64, 67),
            rhythm=(False, False, False),
        )
        assert all(isinstance(e, Rest) for e in result)

    def test_apply_rhythm_custom_duration(self) -> None:
        result = apply_rhythm(
            pitches=(60,),
            rhythm=(True, False),
            slot_duration=Duration.from_cn("e"),
        )
        for event in result:
            assert event.duration.fraction == Fraction(1, 8)

    def test_apply_rhythm_default_quarter(self) -> None:
        result = apply_rhythm(
            pitches=(60,),
            rhythm=(True, False),
        )
        for event in result:
            assert event.duration.fraction == Fraction(1, 4)
