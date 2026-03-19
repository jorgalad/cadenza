"""Tests for cadenza.theory.chords — CHRD-01 through CHRD-09."""

from __future__ import annotations

import pytest

from cadenza.core.pitch import Pitch
from cadenza.theory.chords import (
    get_chord,
    register_chord,
    diatonic_chords,
    secondary_dominant,
    aug6_chord,
    neapolitan_chord,
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


# ---------------------------------------------------------------------------
# CHRD-06: Diatonic chords
# ---------------------------------------------------------------------------

class TestDiatonicChords:
    def test_diatonic_triads_c_major(self) -> None:
        chords = diatonic_chords(P("c", "n", 4), "major", "triad")
        assert len(chords) == 7
        # I: C major
        assert chords[0] == (P("c", "n", 4), P("e", "n", 4), P("g", "n", 4))
        # ii: D minor
        assert chords[1] == (P("d", "n", 4), P("f", "n", 4), P("a", "n", 4))
        # iii: E minor
        assert chords[2] == (P("e", "n", 4), P("g", "n", 4), P("b", "n", 4))
        # IV: F major
        assert chords[3] == (P("f", "n", 4), P("a", "n", 4), P("c", "n", 5))
        # V: G major
        assert chords[4] == (P("g", "n", 4), P("b", "n", 4), P("d", "n", 5))
        # vi: A minor
        assert chords[5] == (P("a", "n", 4), P("c", "n", 5), P("e", "n", 5))
        # vii-dim: B diminished
        assert chords[6] == (P("b", "n", 4), P("d", "n", 5), P("f", "n", 5))

    def test_diatonic_sevenths_c_major(self) -> None:
        chords = diatonic_chords(P("c", "n", 4), "major", "seventh")
        assert len(chords) == 7
        # I: Cmaj7
        assert chords[0] == (P("c", "n", 4), P("e", "n", 4), P("g", "n", 4), P("b", "n", 4))
        # ii: Dm7
        assert chords[1] == (P("d", "n", 4), P("f", "n", 4), P("a", "n", 4), P("c", "n", 5))
        # iii: Em7
        assert chords[2] == (P("e", "n", 4), P("g", "n", 4), P("b", "n", 4), P("d", "n", 5))
        # IV: Fmaj7
        assert chords[3] == (P("f", "n", 4), P("a", "n", 4), P("c", "n", 5), P("e", "n", 5))
        # V: G7 (dominant)
        assert chords[4] == (P("g", "n", 4), P("b", "n", 4), P("d", "n", 5), P("f", "n", 5))
        # vi: Am7
        assert chords[5] == (P("a", "n", 4), P("c", "n", 5), P("e", "n", 5), P("g", "n", 5))
        # vii: Bm7b5
        assert chords[6] == (P("b", "n", 4), P("d", "n", 5), P("f", "n", 5), P("a", "n", 5))

    def test_diatonic_triads_g_major(self) -> None:
        chords = diatonic_chords(P("g", "n", 4), "major", "triad")
        # vii: F#dim
        assert chords[6] == (P("f", "s", 5), P("a", "n", 5), P("c", "n", 6))

    def test_diatonic_chords_minor(self) -> None:
        chords = diatonic_chords(P("a", "n", 4), "natural_minor", "triad")
        # III: C major
        assert chords[2] == (P("c", "n", 5), P("e", "n", 5), P("g", "n", 5))


# ---------------------------------------------------------------------------
# CHRD-07: Secondary dominants
# ---------------------------------------------------------------------------

class TestSecondaryDominants:
    def test_secondary_dominant_V_of_V(self) -> None:
        # V/V in C major = D7 (D-F#-A-C)
        chord = secondary_dominant(5, P("c", "n", 4), "major")
        steps = [p.step for p in chord]
        accs = [p.accidental for p in chord]
        assert steps == ["d", "f", "a", "c"]
        assert accs[1] == "s"  # F#

    def test_secondary_dominant_V_of_ii(self) -> None:
        # V/ii in C major = A7 (A-C#-E-G)
        chord = secondary_dominant(2, P("c", "n", 4), "major")
        steps = [p.step for p in chord]
        accs = [p.accidental for p in chord]
        assert steps == ["a", "c", "e", "g"]
        assert accs[1] == "s"  # C#

    def test_secondary_dominant_V_of_vi(self) -> None:
        # V/vi in C major = E7 (E-G#-B-D)
        chord = secondary_dominant(6, P("c", "n", 4), "major")
        steps = [p.step for p in chord]
        accs = [p.accidental for p in chord]
        assert steps == ["e", "g", "b", "d"]
        assert accs[1] == "s"  # G#

    def test_secondary_dominant_invalid_degree(self) -> None:
        with pytest.raises(ValueError):
            secondary_dominant(1, P("c", "n", 4), "major")


# ---------------------------------------------------------------------------
# CHRD-08: Augmented sixth chords and Neapolitan
# ---------------------------------------------------------------------------

class TestAugmentedSixth:
    def test_italian_sixth(self) -> None:
        chord = aug6_chord("italian", P("c", "n", 4), "major")
        assert len(chord) == 3
        assert chord == (P("a", "b", 4), P("c", "n", 5), P("f", "s", 5))

    def test_french_sixth(self) -> None:
        chord = aug6_chord("french", P("c", "n", 4), "major")
        assert len(chord) == 4
        assert chord == (P("a", "b", 4), P("c", "n", 5), P("d", "n", 5), P("f", "s", 5))

    def test_german_sixth(self) -> None:
        chord = aug6_chord("german", P("c", "n", 4), "major")
        assert len(chord) == 4
        assert chord == (P("a", "b", 4), P("c", "n", 5), P("e", "b", 5), P("f", "s", 5))

    def test_aug6_unknown_type(self) -> None:
        with pytest.raises(ValueError):
            aug6_chord("unknown", P("c", "n", 4), "major")


class TestNeapolitan:
    def test_neapolitan(self) -> None:
        chord = neapolitan_chord(P("c", "n", 4), "major")
        assert chord == (P("d", "b", 4), P("f", "n", 4), P("a", "b", 4))

    def test_neapolitan_in_minor(self) -> None:
        chord = neapolitan_chord(P("a", "n", 4), "natural_minor")
        assert chord == (P("b", "b", 4), P("d", "n", 5), P("f", "n", 5))
