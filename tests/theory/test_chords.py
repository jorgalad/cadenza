"""Tests for cadenza.theory.chords — CHRD-01 through CHRD-09."""

from __future__ import annotations

import pytest

from cadenza.core.pitch import Pitch
from cadenza.theory.chords import (
    get_chord,
    register_chord,
    _CHORD_REGISTRY,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

P = Pitch  # shorthand


# ---------------------------------------------------------------------------
# CHRD-01: Triads
# ---------------------------------------------------------------------------

class TestTriads:
    def test_major_triad(self) -> None:
        assert get_chord(P("c", "n", 4), "maj") == (
            P("c", "n", 4), P("e", "n", 4), P("g", "n", 4),
        )

    def test_minor_triad(self) -> None:
        assert get_chord(P("a", "n", 4), "m") == (
            P("a", "n", 4), P("c", "n", 5), P("e", "n", 5),
        )

    def test_dim_triad(self) -> None:
        assert get_chord(P("b", "n", 4), "dim") == (
            P("b", "n", 4), P("d", "n", 5), P("f", "n", 5),
        )

    def test_aug_triad(self) -> None:
        assert get_chord(P("c", "n", 4), "aug") == (
            P("c", "n", 4), P("e", "n", 4), P("g", "s", 4),
        )


# ---------------------------------------------------------------------------
# CHRD-02: Seventh chords
# ---------------------------------------------------------------------------

class TestSeventhChords:
    def test_dom7(self) -> None:
        assert get_chord(P("c", "n", 4), "7") == (
            P("c", "n", 4), P("e", "n", 4), P("g", "n", 4), P("b", "b", 4),
        )

    def test_maj7(self) -> None:
        assert get_chord(P("c", "n", 4), "maj7") == (
            P("c", "n", 4), P("e", "n", 4), P("g", "n", 4), P("b", "n", 4),
        )

    def test_m7(self) -> None:
        assert get_chord(P("d", "n", 4), "m7") == (
            P("d", "n", 4), P("f", "n", 4), P("a", "n", 4), P("c", "n", 5),
        )

    def test_m7b5(self) -> None:
        assert get_chord(P("b", "n", 4), "m7b5") == (
            P("b", "n", 4), P("d", "n", 5), P("f", "n", 5), P("a", "n", 5),
        )

    def test_dim7(self) -> None:
        assert get_chord(P("b", "n", 4), "dim7") == (
            P("b", "n", 4), P("d", "n", 5), P("f", "n", 5), P("a", "b", 5),
        )

    def test_mM7(self) -> None:
        assert get_chord(P("c", "n", 4), "mM7") == (
            P("c", "n", 4), P("e", "b", 4), P("g", "n", 4), P("b", "n", 4),
        )

    def test_aug7(self) -> None:
        assert get_chord(P("c", "n", 4), "aug7") == (
            P("c", "n", 4), P("e", "n", 4), P("g", "s", 4), P("b", "b", 4),
        )


# ---------------------------------------------------------------------------
# CHRD-03: Extended chords
# ---------------------------------------------------------------------------

class TestExtendedChords:
    def test_dom9(self) -> None:
        assert get_chord(P("c", "n", 4), "9") == (
            P("c", "n", 4), P("e", "n", 4), P("g", "n", 4),
            P("b", "b", 4), P("d", "n", 5),
        )

    def test_maj9(self) -> None:
        assert get_chord(P("c", "n", 4), "maj9") == (
            P("c", "n", 4), P("e", "n", 4), P("g", "n", 4),
            P("b", "n", 4), P("d", "n", 5),
        )

    def test_m9(self) -> None:
        assert get_chord(P("c", "n", 4), "m9") == (
            P("c", "n", 4), P("e", "b", 4), P("g", "n", 4),
            P("b", "b", 4), P("d", "n", 5),
        )

    def test_dom11(self) -> None:
        chord = get_chord(P("c", "n", 4), "11")
        assert len(chord) == 6
        assert chord[-1] == P("f", "n", 5)

    def test_dom13(self) -> None:
        chord = get_chord(P("c", "n", 4), "13")
        assert len(chord) == 7
        assert chord[-1] == P("a", "n", 5)


# ---------------------------------------------------------------------------
# CHRD-04: Added and suspended chords
# ---------------------------------------------------------------------------

class TestAddedSuspended:
    def test_sus2(self) -> None:
        assert get_chord(P("c", "n", 4), "sus2") == (
            P("c", "n", 4), P("d", "n", 4), P("g", "n", 4),
        )

    def test_sus4(self) -> None:
        assert get_chord(P("c", "n", 4), "sus4") == (
            P("c", "n", 4), P("f", "n", 4), P("g", "n", 4),
        )

    def test_add9(self) -> None:
        assert get_chord(P("c", "n", 4), "add9") == (
            P("c", "n", 4), P("e", "n", 4), P("g", "n", 4), P("d", "n", 5),
        )

    def test_add11(self) -> None:
        assert get_chord(P("c", "n", 4), "add11") == (
            P("c", "n", 4), P("e", "n", 4), P("g", "n", 4), P("f", "n", 5),
        )


# ---------------------------------------------------------------------------
# CHRD-05: Inversions
# ---------------------------------------------------------------------------

class TestInversions:
    def test_first_inversion(self) -> None:
        assert get_chord(P("c", "n", 4), "maj", inversion=1) == (
            P("e", "n", 4), P("g", "n", 4), P("c", "n", 5),
        )

    def test_second_inversion(self) -> None:
        assert get_chord(P("c", "n", 4), "maj", inversion=2) == (
            P("g", "n", 4), P("c", "n", 5), P("e", "n", 5),
        )

    def test_seventh_first_inversion(self) -> None:
        assert get_chord(P("c", "n", 4), "7", inversion=1) == (
            P("e", "n", 4), P("g", "n", 4), P("b", "b", 4), P("c", "n", 5),
        )

    def test_inversion_out_of_range(self) -> None:
        with pytest.raises(ValueError):
            get_chord(P("c", "n", 4), "maj", inversion=3)


# ---------------------------------------------------------------------------
# CHRD-09: Aliases, errors, custom chords
# ---------------------------------------------------------------------------

class TestAliasesAndRegistry:
    def test_alias_min(self) -> None:
        root = P("c", "n", 4)
        assert get_chord(root, "min") == get_chord(root, "m")

    def test_alias_M7(self) -> None:
        root = P("c", "n", 4)
        assert get_chord(root, "M7") == get_chord(root, "maj7")

    def test_unknown_chord(self) -> None:
        with pytest.raises(ValueError):
            get_chord(P("c", "n", 4), "xyz")

    def test_register_chord(self) -> None:
        register_chord("test_custom_chord", [0, 4, 8, 11], (0, 2, 4, 6))
        chord = get_chord(P("c", "n", 4), "test_custom_chord")
        assert len(chord) == 4

    def test_registry_has_at_least_21_entries(self) -> None:
        assert len(_CHORD_REGISTRY) >= 21


# ---------------------------------------------------------------------------
# Correct spelling with sharps/flats
# ---------------------------------------------------------------------------

class TestEnharmonicSpelling:
    def test_sharp_root(self) -> None:
        assert get_chord(P("f", "s", 4), "maj") == (
            P("f", "s", 4), P("a", "s", 4), P("c", "s", 5),
        )

    def test_flat_root(self) -> None:
        assert get_chord(P("b", "b", 4), "maj") == (
            P("b", "b", 4), P("d", "n", 5), P("f", "n", 5),
        )
