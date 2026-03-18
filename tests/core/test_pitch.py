"""Tests for Pitch frozen dataclass."""

from __future__ import annotations

import pytest
from hypothesis import given

from cadenza.core.pitch import Pitch, STEP_SEMITONES, ACCIDENTAL_SEMITONES, STEP_INDEX
from tests.strategies import pitch_strategy


class TestPitchCreation:
    def test_c4_midi_number(self) -> None:
        p = Pitch("c", "n", 4)
        assert p.midi_number == 60

    def test_a4_midi_number(self) -> None:
        p = Pitch("a", "n", 4)
        assert p.midi_number == 69

    def test_css4_midi_equals_d4(self) -> None:
        css4 = Pitch("c", "ss", 4)
        d4 = Pitch("d", "n", 4)
        assert css4.midi_number == d4.midi_number == 62


class TestPitchEquality:
    def test_eb3_not_equal_ds3(self) -> None:
        eb3 = Pitch("e", "b", 3)
        ds3 = Pitch("d", "s", 3)
        assert eb3 != ds3

    def test_eb3_enharmonic_equal_ds3(self) -> None:
        eb3 = Pitch("e", "b", 3)
        ds3 = Pitch("d", "s", 3)
        assert eb3.enharmonic_equal(ds3)

    def test_identical_pitches_equal(self) -> None:
        p1 = Pitch("c", "n", 4)
        p2 = Pitch("c", "n", 4)
        assert p1 == p2


class TestPitchClass:
    def test_c4_pitch_class(self) -> None:
        assert Pitch("c", "n", 4).pitch_class == 0

    def test_fs5_pitch_class(self) -> None:
        assert Pitch("f", "s", 5).pitch_class == 6


class TestPitchValidation:
    def test_invalid_step_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid step"):
            Pitch("x", "n", 4)

    def test_invalid_accidental_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid accidental"):
            Pitch("c", "sharp", 4)

    def test_octave_too_low_raises(self) -> None:
        with pytest.raises(ValueError, match="Octave out of range"):
            Pitch("c", "n", -2)

    def test_octave_too_high_raises(self) -> None:
        with pytest.raises(ValueError, match="Octave out of range"):
            Pitch("c", "n", 11)


class TestPitchImmutability:
    def test_frozen(self) -> None:
        p = Pitch("c", "n", 4)
        with pytest.raises(AttributeError):
            p.step = "d"  # type: ignore[misc]

    def test_hashable(self) -> None:
        p = Pitch("c", "n", 4)
        {p}  # usable in set
        {p: 1}  # usable as dict key

    def test_identical_hash_equally(self) -> None:
        p1 = Pitch("c", "n", 4)
        p2 = Pitch("c", "n", 4)
        assert hash(p1) == hash(p2)


class TestPitchOrdering:
    def test_lower_midi_is_less(self) -> None:
        c4 = Pitch("c", "n", 4)
        d4 = Pitch("d", "n", 4)
        assert c4 < d4

    def test_higher_midi_is_greater(self) -> None:
        d4 = Pitch("d", "n", 4)
        c4 = Pitch("c", "n", 4)
        assert d4 > c4


class TestPitchHypothesis:
    @given(p=pitch_strategy())
    def test_midi_number_in_range(self, p: Pitch) -> None:
        assert 0 <= p.midi_number <= 127

    @given(p=pitch_strategy())
    def test_hash_consistency(self, p: Pitch) -> None:
        p2 = Pitch(step=p.step, accidental=p.accidental, octave=p.octave)
        assert p == p2
        assert hash(p) == hash(p2)


class TestConstants:
    def test_step_semitones_keys(self) -> None:
        assert set(STEP_SEMITONES.keys()) == {"c", "d", "e", "f", "g", "a", "b"}

    def test_accidental_semitones_keys(self) -> None:
        assert set(ACCIDENTAL_SEMITONES.keys()) == {"bb", "b", "n", "s", "ss"}

    def test_step_index_keys(self) -> None:
        assert set(STEP_INDEX.keys()) == {"c", "d", "e", "f", "g", "a", "b"}
