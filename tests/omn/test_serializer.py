"""Tests for OMN serializer with sticky optimization."""

from __future__ import annotations

import pytest

from cadenza.omn.serializer import to_omn
from cadenza.omn.parser import parse_omn
from cadenza.core.pitch import Pitch
from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest


# ── Helpers ──────────────────────────────────────────────────────────


def make_note(
    step: str = "c",
    acc: str = "n",
    octave: int = 4,
    base: str = "q",
    dots: int = 0,
    tuplet: int | None = None,
    dynamic: str | None = None,
    articulations: tuple[str, ...] = (),
) -> Note:
    return Note(
        pitch=Pitch(step, acc, octave),
        duration=Duration.from_omn(base, dots=dots, tuplet=tuplet),
        dynamic=dynamic,
        articulations=articulations,
    )


def make_rest(base: str = "q", dots: int = 0, tuplet: int | None = None) -> Rest:
    return Rest(duration=Duration.from_omn(base, dots=dots, tuplet=tuplet))


# ── Compact output (sticky optimization) ─────────────────────────────


class TestCompactOutput:
    def test_identical_duration_emitted_once(self):
        """Three notes with same duration: only first emits duration."""
        phrase = (
            make_note(step="c", dynamic="pp", articulations=("stacc",), base="e"),
            make_note(step="d", dynamic="pp", articulations=("stacc",), base="e"),
            make_note(step="e", dynamic="pp", articulations=("stacc",), base="e"),
        )
        result = to_omn(phrase)
        assert result == "e c4 pp stacc d4 e4"

    def test_dynamic_emitted_on_change(self):
        phrase = (
            make_note(step="c", dynamic="pp", base="q"),
            make_note(step="d", dynamic="mf", base="q"),
        )
        result = to_omn(phrase)
        assert result == "q c4 pp d4 mf"

    def test_articulation_emitted_on_change(self):
        phrase = (
            make_note(step="c", articulations=("stacc",), base="q"),
            make_note(step="d", articulations=("ten",), base="q"),
        )
        result = to_omn(phrase)
        assert result == "q c4 stacc d4 ten"

    def test_pitch_always_emitted(self):
        """Every Note must have its pitch emitted."""
        phrase = (
            make_note(step="c", base="q"),
            make_note(step="c", base="q"),
        )
        result = to_omn(phrase)
        # Both c4 must appear even though they're the same pitch
        assert result.count("c4") == 2


# ── Rests ────────────────────────────────────────────────────────────


class TestRestSerialization:
    def test_quarter_rest(self):
        phrase = (make_rest("q"),)
        result = to_omn(phrase)
        assert result == "-q"

    def test_dotted_rest(self):
        phrase = (make_rest("e", dots=1),)
        result = to_omn(phrase)
        assert result == "-e."

    def test_tuplet_rest(self):
        phrase = (make_rest("q", tuplet=3),)
        result = to_omn(phrase)
        assert result == "-3q"


# ── Duration formats ─────────────────────────────────────────────────


class TestDurationFormats:
    def test_dotted_quarter(self):
        phrase = (make_note(base="q", dots=1),)
        result = to_omn(phrase)
        assert result.startswith("q.")

    def test_tuplet_quarter(self):
        phrase = (make_note(base="q", tuplet=3),)
        result = to_omn(phrase)
        assert result.startswith("3q")


# ── Mixed phrases ────────────────────────────────────────────────────


class TestMixedPhrases:
    def test_notes_and_rests(self):
        phrase = (
            make_note(step="c", base="q"),
            make_rest("q"),
            make_note(step="e", base="q"),
        )
        result = to_omn(phrase)
        assert "-q" in result
        assert "c4" in result
        assert "e4" in result


# ── Round-trip ───────────────────────────────────────────────────────


class TestRoundTrip:
    def test_canonical_round_trip(self):
        """parse -> serialize -> parse must produce same phrase."""
        source = "e c4 pp stacc d4 e4"
        phrase1, _ = parse_omn(source)
        serialized = to_omn(phrase1)
        phrase2, _ = parse_omn(serialized)
        assert phrase1 == phrase2

    def test_round_trip_preserves_rests(self):
        source = "q c4 -q e4"
        phrase1, _ = parse_omn(source)
        serialized = to_omn(phrase1)
        phrase2, _ = parse_omn(serialized)
        assert phrase1 == phrase2

    def test_round_trip_with_dynamics_changes(self):
        source = "q c4 pp e d4 mf"
        phrase1, _ = parse_omn(source)
        serialized = to_omn(phrase1)
        phrase2, _ = parse_omn(serialized)
        assert phrase1 == phrase2

    def test_round_trip_exact_string(self):
        """Canonical OMN should round-trip to the exact same string."""
        source = "e c4 pp stacc d4 e4"
        phrase, _ = parse_omn(source)
        assert to_omn(phrase) == source
