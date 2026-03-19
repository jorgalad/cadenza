"""Tests for cadenza.theory.scales — SCAL-01 through SCAL-12."""

from __future__ import annotations

import pytest

from cadenza.core.pitch import Pitch
from cadenza.theory.scales import (
    Scale,
    get_scale,
    register_scale,
    scales_for_pitches,
    scale_degree,
    relative_key,
    parallel_key,
    _SCALE_REGISTRY,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

P = Pitch  # shorthand


# ---------------------------------------------------------------------------
# SCAL-01: Scale type
# ---------------------------------------------------------------------------

class TestScaleType:
    def test_scale_is_frozen_dataclass(self) -> None:
        s = get_scale(P("c", "n", 4), "major")
        with pytest.raises(AttributeError):
            s.name = "oops"  # type: ignore[misc]

    def test_scale_fields(self) -> None:
        s = get_scale(P("c", "n", 4), "major")
        assert isinstance(s.root, Pitch)
        assert isinstance(s.name, str)
        assert isinstance(s.pitches, tuple)
        assert isinstance(s.intervals, tuple)


# ---------------------------------------------------------------------------
# SCAL-01: Major scales
# ---------------------------------------------------------------------------

class TestMajorScales:
    def test_c_major(self) -> None:
        s = get_scale(P("c", "n", 4), "major")
        assert s.pitches == (
            P("c", "n", 4), P("d", "n", 4), P("e", "n", 4),
            P("f", "n", 4), P("g", "n", 4), P("a", "n", 4), P("b", "n", 4),
        )

    def test_g_major(self) -> None:
        s = get_scale(P("g", "n", 4), "major")
        assert s.pitches == (
            P("g", "n", 4), P("a", "n", 4), P("b", "n", 4),
            P("c", "n", 5), P("d", "n", 5), P("e", "n", 5), P("f", "s", 5),
        )

    def test_f_major(self) -> None:
        s = get_scale(P("f", "n", 4), "major")
        assert s.pitches == (
            P("f", "n", 4), P("g", "n", 4), P("a", "n", 4),
            P("b", "b", 4), P("c", "n", 5), P("d", "n", 5), P("e", "n", 5),
        )

    def test_bb_major(self) -> None:
        s = get_scale(P("b", "b", 3), "major")
        assert s.pitches == (
            P("b", "b", 3), P("c", "n", 4), P("d", "n", 4),
            P("e", "b", 4), P("f", "n", 4), P("g", "n", 4), P("a", "n", 4),
        )


# ---------------------------------------------------------------------------
# SCAL-01: Minor scales
# ---------------------------------------------------------------------------

class TestMinorScales:
    def test_a_natural_minor(self) -> None:
        s = get_scale(P("a", "n", 4), "natural_minor")
        assert s.pitches == (
            P("a", "n", 4), P("b", "n", 4), P("c", "n", 5),
            P("d", "n", 5), P("e", "n", 5), P("f", "n", 5), P("g", "n", 5),
        )

    def test_c_harmonic_minor(self) -> None:
        s = get_scale(P("c", "n", 4), "harmonic_minor")
        assert s.pitches == (
            P("c", "n", 4), P("d", "n", 4), P("e", "b", 4),
            P("f", "n", 4), P("g", "n", 4), P("a", "b", 4), P("b", "n", 4),
        )

    def test_c_melodic_minor(self) -> None:
        s = get_scale(P("c", "n", 4), "melodic_minor")
        assert s.pitches == (
            P("c", "n", 4), P("d", "n", 4), P("e", "b", 4),
            P("f", "n", 4), P("g", "n", 4), P("a", "n", 4), P("b", "n", 4),
        )


# ---------------------------------------------------------------------------
# SCAL-02: Church modes
# ---------------------------------------------------------------------------

class TestChurchModes:
    def test_dorian(self) -> None:
        s = get_scale(P("d", "n", 4), "dorian")
        assert s.pitches == (
            P("d", "n", 4), P("e", "n", 4), P("f", "n", 4),
            P("g", "n", 4), P("a", "n", 4), P("b", "n", 4), P("c", "n", 5),
        )

    def test_phrygian(self) -> None:
        s = get_scale(P("e", "n", 4), "phrygian")
        assert s.pitches == (
            P("e", "n", 4), P("f", "n", 4), P("g", "n", 4),
            P("a", "n", 4), P("b", "n", 4), P("c", "n", 5), P("d", "n", 5),
        )

    def test_lydian(self) -> None:
        s = get_scale(P("f", "n", 4), "lydian")
        assert s.pitches == (
            P("f", "n", 4), P("g", "n", 4), P("a", "n", 4),
            P("b", "n", 4), P("c", "n", 5), P("d", "n", 5), P("e", "n", 5),
        )

    def test_mixolydian(self) -> None:
        s = get_scale(P("g", "n", 4), "mixolydian")
        assert s.pitches == (
            P("g", "n", 4), P("a", "n", 4), P("b", "n", 4),
            P("c", "n", 5), P("d", "n", 5), P("e", "n", 5), P("f", "n", 5),
        )

    def test_locrian(self) -> None:
        s = get_scale(P("b", "n", 4), "locrian")
        assert s.pitches == (
            P("b", "n", 4), P("c", "n", 5), P("d", "n", 5),
            P("e", "n", 5), P("f", "n", 5), P("g", "n", 5), P("a", "n", 5),
        )


# ---------------------------------------------------------------------------
# Aliases
# ---------------------------------------------------------------------------

class TestAliases:
    def test_ionian_is_major(self) -> None:
        root = P("c", "n", 4)
        assert get_scale(root, "ionian") == get_scale(root, "major")

    def test_aeolian_is_natural_minor(self) -> None:
        root = P("a", "n", 4)
        assert get_scale(root, "aeolian") == get_scale(root, "natural_minor")

    def test_minor_is_natural_minor(self) -> None:
        root = P("a", "n", 4)
        assert get_scale(root, "minor") == get_scale(root, "natural_minor")


# ---------------------------------------------------------------------------
# SCAL-03: Pentatonic
# ---------------------------------------------------------------------------

class TestPentatonic:
    def test_c_major_pentatonic(self) -> None:
        s = get_scale(P("c", "n", 4), "major_pentatonic")
        assert s.pitches == (
            P("c", "n", 4), P("d", "n", 4), P("e", "n", 4),
            P("g", "n", 4), P("a", "n", 4),
        )

    def test_a_minor_pentatonic(self) -> None:
        s = get_scale(P("a", "n", 4), "minor_pentatonic")
        assert s.pitches == (
            P("a", "n", 4), P("c", "n", 5), P("d", "n", 5),
            P("e", "n", 5), P("g", "n", 5),
        )


# ---------------------------------------------------------------------------
# SCAL-04: Blues
# ---------------------------------------------------------------------------

class TestBlues:
    def test_c_blues(self) -> None:
        s = get_scale(P("c", "n", 4), "blues")
        assert s.pitches == (
            P("c", "n", 4), P("e", "b", 4), P("f", "n", 4),
            P("g", "b", 4), P("g", "n", 4), P("b", "b", 4),
        )


# ---------------------------------------------------------------------------
# SCAL-05: Symmetric scales
# ---------------------------------------------------------------------------

class TestSymmetric:
    def test_whole_tone(self) -> None:
        s = get_scale(P("c", "n", 4), "whole_tone")
        assert s.pitches == (
            P("c", "n", 4), P("d", "n", 4), P("e", "n", 4),
            P("f", "s", 4), P("g", "s", 4), P("a", "s", 4),
        )

    def test_diminished_length_and_intervals(self) -> None:
        s = get_scale(P("c", "n", 4), "diminished")
        assert len(s.pitches) == 8
        assert s.intervals == (0, 2, 3, 5, 6, 8, 9, 11)

    def test_augmented_length_and_intervals(self) -> None:
        s = get_scale(P("c", "n", 4), "augmented")
        assert len(s.pitches) == 6
        assert s.intervals == (0, 3, 4, 7, 8, 11)


# ---------------------------------------------------------------------------
# SCAL-06: Bebop
# ---------------------------------------------------------------------------

class TestBebop:
    def test_bebop_dominant_has_8_pitches(self) -> None:
        s = get_scale(P("c", "n", 4), "bebop_dominant")
        assert len(s.pitches) == 8

    def test_bebop_major_has_8_pitches(self) -> None:
        s = get_scale(P("c", "n", 4), "bebop_major")
        assert len(s.pitches) == 8

    def test_bebop_minor_has_8_pitches(self) -> None:
        s = get_scale(P("c", "n", 4), "bebop_minor")
        assert len(s.pitches) == 8


# ---------------------------------------------------------------------------
# SCAL-07: Non-Western scales
# ---------------------------------------------------------------------------

class TestNonWestern:
    def test_hijaz(self) -> None:
        s = get_scale(P("c", "n", 4), "hijaz")
        assert len(s.pitches) == 7
        assert s.intervals == (0, 1, 4, 5, 7, 8, 10)

    def test_hungarian_minor(self) -> None:
        s = get_scale(P("c", "n", 4), "hungarian_minor")
        assert len(s.pitches) == 7

    def test_persian(self) -> None:
        s = get_scale(P("c", "n", 4), "persian")
        assert len(s.pitches) == 7

    def test_hirajoshi(self) -> None:
        s = get_scale(P("c", "n", 4), "hirajoshi")
        assert len(s.pitches) == 5

    def test_at_least_15_non_western(self) -> None:
        non_western = [
            "hijaz", "hijaz_kar", "rast", "bayati", "hungarian_minor",
            "romanian", "neapolitan_major", "neapolitan_minor", "persian",
            "phrygian_dominant", "double_harmonic", "enigmatic",
            "hirajoshi", "in_sen", "iwato", "yo",
        ]
        for name in non_western:
            assert name in _SCALE_REGISTRY, f"{name} not in registry"


# ---------------------------------------------------------------------------
# SCAL-08: register_scale
# ---------------------------------------------------------------------------

class TestRegisterScale:
    def test_register_and_retrieve(self) -> None:
        register_scale("test_custom", [0, 2, 4, 7, 9])
        s = get_scale(P("c", "n", 4), "test_custom")
        assert s.pitches == (
            P("c", "n", 4), P("d", "n", 4), P("e", "n", 4),
            P("g", "n", 4), P("a", "n", 4),
        )

    def test_register_duplicate_raises(self) -> None:
        with pytest.raises(ValueError, match="already"):
            register_scale("major", [0, 2, 4, 5, 7, 9, 11])


# ---------------------------------------------------------------------------
# SCAL-09: Error handling
# ---------------------------------------------------------------------------

class TestErrorHandling:
    def test_unknown_scale_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown scale"):
            get_scale(P("c", "n", 4), "nonexistent_scale")


# ---------------------------------------------------------------------------
# Scale intervals field
# ---------------------------------------------------------------------------

class TestScaleIntervals:
    def test_major_intervals(self) -> None:
        s = get_scale(P("c", "n", 4), "major")
        assert s.intervals == (0, 2, 4, 5, 7, 9, 11)

    def test_dorian_intervals(self) -> None:
        s = get_scale(P("d", "n", 4), "dorian")
        assert s.intervals == (0, 2, 3, 5, 7, 9, 10)


# ---------------------------------------------------------------------------
# SCAL-10: scales_for_pitches
# ---------------------------------------------------------------------------

class TestScalesForPitches:
    def test_c_major_pitches_find_c_major(self) -> None:
        pitches = [
            P("c", "n", 4), P("d", "n", 4), P("e", "n", 4),
            P("f", "n", 4), P("g", "n", 4), P("a", "n", 4), P("b", "n", 4),
        ]
        result = scales_for_pitches(pitches)
        assert ("c", "major") in result

    def test_subset_pitches_find_multiple(self) -> None:
        pitches = [P("d", "n", 4), P("e", "n", 4), P("f", "n", 4)]
        result = scales_for_pitches(pitches)
        assert ("d", "dorian") in result
        assert ("c", "major") in result

    def test_empty_returns_empty(self) -> None:
        assert scales_for_pitches([]) == []


# ---------------------------------------------------------------------------
# SCAL-11: scale_degree
# ---------------------------------------------------------------------------

class TestScaleDegree:
    def test_first_degree(self) -> None:
        s = get_scale(P("c", "n", 4), "major")
        assert scale_degree(P("c", "n", 4), s) == 1

    def test_third_degree(self) -> None:
        s = get_scale(P("c", "n", 4), "major")
        assert scale_degree(P("e", "n", 4), s) == 3

    def test_seventh_degree(self) -> None:
        s = get_scale(P("c", "n", 4), "major")
        assert scale_degree(P("b", "n", 4), s) == 7

    def test_not_in_scale_raises(self) -> None:
        s = get_scale(P("c", "n", 4), "major")
        with pytest.raises(ValueError):
            scale_degree(P("f", "s", 4), s)


# ---------------------------------------------------------------------------
# SCAL-12: relative_key, parallel_key
# ---------------------------------------------------------------------------

class TestRelativeKey:
    def test_c_major_relative_minor(self) -> None:
        s = relative_key(P("c", "n", 4), "major")
        assert s.root.step == "a"
        assert s.name == "natural_minor"

    def test_a_minor_relative_major(self) -> None:
        s = relative_key(P("a", "n", 4), "natural_minor")
        assert s.root.step == "c"
        assert s.name == "major"


class TestParallelKey:
    def test_c_major_parallel_minor(self) -> None:
        s = parallel_key(P("c", "n", 4), "major")
        assert s.root.step == "c"
        assert s.name == "natural_minor"

    def test_c_minor_parallel_major(self) -> None:
        s = parallel_key(P("c", "n", 4), "natural_minor")
        assert s.root.step == "c"
        assert s.name == "major"
