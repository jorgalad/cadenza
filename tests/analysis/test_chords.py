"""Tests for cadenza.analysis.chords — HARM-01, HARM-07, HARM-08, HARM-09."""

from __future__ import annotations

import pytest

from cadenza.core.pitch import Pitch
from cadenza.analysis.chords import (
    ChordMatch,
    chord_symbol,
    identify_chord,
    parse_chord_symbol,
    realize_chord,
)
from cadenza.theory.chords import _CHORD_REGISTRY, get_chord

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

P = Pitch  # shorthand


# ---------------------------------------------------------------------------
# HARM-01: Chord identification
# ---------------------------------------------------------------------------

class TestIdentifyChord:
    def test_identify_major_triad_root_position(self) -> None:
        result = identify_chord((P("c", "n", 4), P("e", "n", 4), P("g", "n", 4)))
        assert isinstance(result, ChordMatch)
        assert result.root.pitch_class == 0  # C
        assert result.symbol == "maj"
        assert result.inversion == 0

    def test_identify_minor_triad(self) -> None:
        result = identify_chord((P("a", "n", 4), P("c", "n", 5), P("e", "n", 5)))
        assert result.root.pitch_class == 9  # A
        assert result.symbol == "m"
        assert result.inversion == 0

    def test_identify_dominant_seventh(self) -> None:
        result = identify_chord((P("c", "n", 4), P("e", "n", 4), P("g", "n", 4), P("b", "b", 4)))
        assert result.root.pitch_class == 0  # C
        assert result.symbol == "7"
        assert result.inversion == 0

    def test_identify_first_inversion(self) -> None:
        result = identify_chord((P("e", "n", 4), P("g", "n", 4), P("c", "n", 5)))
        assert result.root.pitch_class == 0  # C
        assert result.symbol == "maj"
        assert result.inversion == 1

    def test_identify_second_inversion(self) -> None:
        result = identify_chord((P("g", "n", 4), P("c", "n", 5), P("e", "n", 5)))
        assert result.root.pitch_class == 0  # C
        assert result.symbol == "maj"
        assert result.inversion == 2

    def test_identify_flat_spelling_preserved(self) -> None:
        result = identify_chord((P("e", "b", 4), P("g", "b", 4), P("b", "b", 4)))
        assert result.root.step == "e"
        assert result.root.accidental == "b"
        assert result.symbol == "m"
        assert result.inversion == 0

    def test_identify_diminished(self) -> None:
        result = identify_chord((P("b", "n", 4), P("d", "n", 5), P("f", "n", 5)))
        assert result.symbol == "dim"

    def test_identify_augmented(self) -> None:
        result = identify_chord((P("c", "n", 4), P("e", "n", 4), P("g", "s", 4)))
        assert result.symbol == "aug"

    def test_identify_no_match_raises(self) -> None:
        # Two pitches a tritone apart -- not a valid chord
        with pytest.raises(ValueError):
            identify_chord((P("c", "n", 4), P("f", "s", 4)))

    def test_identify_prefers_simpler(self) -> None:
        # C E G is both a major triad and a subset of many extended chords,
        # but the algorithm should prefer the simpler triad
        result = identify_chord((P("c", "n", 4), P("e", "n", 4), P("g", "n", 4)))
        assert result.symbol == "maj"

    def test_identify_d_dominant_seventh(self) -> None:
        result = identify_chord((P("d", "n", 4), P("f", "s", 4), P("a", "n", 4), P("c", "n", 5)))
        assert result.root.pitch_class == 2  # D
        assert result.symbol == "7"
        assert result.inversion == 0


# ---------------------------------------------------------------------------
# HARM-09: Chord realization
# ---------------------------------------------------------------------------

class TestRealizeChord:
    def test_realize_chord_root_position(self) -> None:
        result = realize_chord(P("c", "n", 4), "maj")
        assert result == (P("c", "n", 4), P("e", "n", 4), P("g", "n", 4))

    def test_realize_chord_inversion(self) -> None:
        result = realize_chord(P("c", "n", 4), "maj", inversion=1)
        assert result == (P("e", "n", 4), P("g", "n", 4), P("c", "n", 5))


# ---------------------------------------------------------------------------
# HARM-07: Chord symbol generation
# ---------------------------------------------------------------------------

class TestChordSymbol:
    def test_chord_symbol_major(self) -> None:
        assert chord_symbol(P("c", "n", 4), "maj7") == "c4maj7"

    def test_chord_symbol_sharp_root(self) -> None:
        assert chord_symbol(P("f", "s", 4), "m") == "fs4m"

    def test_chord_symbol_flat_root(self) -> None:
        assert chord_symbol(P("b", "b", 4), "dim7") == "bb4dim7"

    def test_chord_symbol_natural(self) -> None:
        assert chord_symbol(P("g", "n", 4), "maj") == "g4maj"


# ---------------------------------------------------------------------------
# HARM-08: Chord symbol parsing
# ---------------------------------------------------------------------------

class TestParseChordSymbol:
    def test_parse_chord_symbol_major(self) -> None:
        result = parse_chord_symbol("c4maj7")
        expected = get_chord(P("c", "n", 4), "maj7")
        assert result == expected

    def test_parse_chord_symbol_default_quality(self) -> None:
        result = parse_chord_symbol("c4")
        expected = get_chord(P("c", "n", 4), "maj")
        assert result == expected

    def test_parse_chord_symbol_sharp_root(self) -> None:
        result = parse_chord_symbol("fs4m")
        expected = get_chord(P("f", "s", 4), "m")
        assert result == expected

    def test_parse_chord_symbol_flat_root(self) -> None:
        result = parse_chord_symbol("bb4dim7")
        expected = get_chord(P("b", "b", 4), "dim7")
        assert result == expected

    def test_parse_chord_symbol_aliases(self) -> None:
        c4 = P("c", "n", 4)
        # Maj7 alias
        assert parse_chord_symbol("c4Maj7") == get_chord(c4, "maj7")
        # min alias
        assert parse_chord_symbol("c4min") == get_chord(c4, "m")
        # - alias for minor
        assert parse_chord_symbol("c4-") == get_chord(c4, "m")

    def test_parse_chord_symbol_invalid(self) -> None:
        with pytest.raises(ValueError):
            parse_chord_symbol("xyz")

    def test_chord_symbol_round_trip(self) -> None:
        root = P("c", "n", 4)
        for key in _CHORD_REGISTRY:
            sym_str = chord_symbol(root, key)
            parsed = parse_chord_symbol(sym_str)
            expected = get_chord(root, key)
            assert parsed == expected, f"Round-trip failed for {key!r}: {sym_str!r}"
