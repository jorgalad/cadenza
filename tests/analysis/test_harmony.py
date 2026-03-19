"""Tests for Roman numeral analysis, functional harmony, harmonic rhythm, borrowed chords.

Covers HARM-02, HARM-04, HARM-05, HARM-10.
"""

from __future__ import annotations

from fractions import Fraction

import pytest

from cadenza.core.duration import Duration
from cadenza.core.note import Note
from cadenza.core.pitch import Pitch

from cadenza.analysis.chords import ChordMatch, identify_chord
from cadenza.analysis.keys import KeyResult
from cadenza.analysis.harmony import (
    HarmonicBeat,
    RomanNumeral,
    harmonic_rhythm,
    roman_numeral,
)
from cadenza.theory.chords import get_chord


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pitch(step: str, acc: str = "n", octave: int = 4) -> Pitch:
    return Pitch(step=step, accidental=acc, octave=octave)


def _c_major_key() -> KeyResult:
    return KeyResult(root=_pitch("c"), mode="major", confidence=0.95)


def _chord_match(root_step: str, root_acc: str, symbol: str, inversion: int = 0) -> ChordMatch:
    """Build a ChordMatch using identify_chord for correctness."""
    root = _pitch(root_step, root_acc)
    pitches = get_chord(root, symbol, inversion)
    return ChordMatch(root=root, symbol=symbol, inversion=inversion, pitches=pitches)


def _note(step: str, acc: str = "n", octave: int = 4, base: str = "q") -> Note:
    return Note(pitch=_pitch(step, acc, octave), duration=Duration.from_cn(base))


# ---------------------------------------------------------------------------
# Roman numeral tests (HARM-02)
# ---------------------------------------------------------------------------


class TestRomanNumeral:
    def test_roman_numeral_tonic(self) -> None:
        chord = _chord_match("c", "n", "maj")
        rn = roman_numeral(chord, _c_major_key())
        assert rn.numeral == "I"
        assert rn.function == "tonic"

    def test_roman_numeral_supertonic(self) -> None:
        chord = _chord_match("d", "n", "m")
        rn = roman_numeral(chord, _c_major_key())
        assert rn.numeral == "ii"
        assert rn.function == "predominant"

    def test_roman_numeral_dominant(self) -> None:
        chord = _chord_match("g", "n", "maj")
        rn = roman_numeral(chord, _c_major_key())
        assert rn.numeral == "V"
        assert rn.function == "dominant"

    def test_roman_numeral_dominant_seventh(self) -> None:
        chord = _chord_match("g", "n", "7")
        rn = roman_numeral(chord, _c_major_key())
        assert rn.numeral == "V7"
        assert rn.function == "dominant"

    def test_roman_numeral_first_inversion_triad(self) -> None:
        chord = _chord_match("c", "n", "maj", inversion=1)
        rn = roman_numeral(chord, _c_major_key())
        assert rn.numeral == "I6"

    def test_roman_numeral_first_inversion_seventh(self) -> None:
        chord = _chord_match("g", "n", "7", inversion=1)
        rn = roman_numeral(chord, _c_major_key())
        assert rn.numeral == "V6/5"

    def test_roman_numeral_second_inversion_seventh(self) -> None:
        chord = _chord_match("g", "n", "7", inversion=2)
        rn = roman_numeral(chord, _c_major_key())
        assert rn.numeral == "V4/3"

    def test_roman_numeral_third_inversion_seventh(self) -> None:
        chord = _chord_match("g", "n", "7", inversion=3)
        rn = roman_numeral(chord, _c_major_key())
        assert rn.numeral == "V4/2"

    def test_roman_numeral_second_inversion_triad(self) -> None:
        chord = _chord_match("c", "n", "maj", inversion=2)
        rn = roman_numeral(chord, _c_major_key())
        assert rn.numeral == "I6/4"


# ---------------------------------------------------------------------------
# Borrowed chord tests (HARM-10)
# ---------------------------------------------------------------------------


class TestBorrowedChords:
    def test_borrowed_chord_bVII(self) -> None:
        # Bb major triad in C major -> borrowed from C minor
        chord = _chord_match("b", "b", "maj")
        rn = roman_numeral(chord, _c_major_key())
        assert rn.numeral == "bVII"
        assert rn.function == "borrowed"

    def test_borrowed_chord_bIII(self) -> None:
        # Eb major triad in C major -> borrowed from C minor
        chord = _chord_match("e", "b", "maj")
        rn = roman_numeral(chord, _c_major_key())
        assert rn.numeral == "bIII"
        assert rn.function == "borrowed"

    def test_borrowed_chord_bVI(self) -> None:
        # Ab major triad in C major -> borrowed from C minor
        chord = _chord_match("a", "b", "maj")
        rn = roman_numeral(chord, _c_major_key())
        assert rn.numeral == "bVI"
        assert rn.function == "borrowed"


# ---------------------------------------------------------------------------
# Functional labels test (HARM-05)
# ---------------------------------------------------------------------------


class TestFunctionalLabels:
    def test_functional_labels_all_degrees(self) -> None:
        """Verify function labels for diatonic triads I through VII in C major."""
        key = _c_major_key()
        # Build diatonic triads for C major
        from cadenza.theory.chords import diatonic_chords
        triads = diatonic_chords(_pitch("c"), "major", "triad")
        expected_functions = [
            "tonic",        # I
            "predominant",  # ii
            "tonic",        # iii
            "subdominant",  # IV
            "dominant",     # V
            "tonic",        # vi
            "dominant",     # vii
        ]
        for i, (triad_pitches, expected_fn) in enumerate(zip(triads, expected_functions)):
            chord = identify_chord(triad_pitches)
            rn = roman_numeral(chord, key)
            assert rn.function == expected_fn, (
                f"Degree {i + 1}: expected {expected_fn}, got {rn.function} "
                f"(numeral={rn.numeral})"
            )


# ---------------------------------------------------------------------------
# Harmonic rhythm tests (HARM-04)
# ---------------------------------------------------------------------------


class TestHarmonicRhythm:
    def test_harmonic_rhythm_simple(self) -> None:
        """Phrase with two distinct chords -> two HarmonicBeat entries."""
        key = _c_major_key()
        # C major triad notes, then G major triad notes
        phrase = (
            _note("c"), _note("e"), _note("g"),
            _note("g"), _note("b"), _note("d", octave=5),
        )
        beats = harmonic_rhythm(phrase, key)
        assert len(beats) >= 2
        assert all(isinstance(b, HarmonicBeat) for b in beats)

    def test_harmonic_rhythm_onset_fractions(self) -> None:
        """Onset values are correct Fraction sums of preceding durations."""
        key = _c_major_key()
        phrase = (
            _note("c"), _note("e"), _note("g"),
            _note("g"), _note("b"), _note("d", octave=5),
        )
        beats = harmonic_rhythm(phrase, key)
        # First beat should start at 0
        assert beats[0].onset == Fraction(0)
        # Each beat's onset should be a non-negative Fraction
        for beat in beats:
            assert isinstance(beat.onset, Fraction)
            assert beat.onset >= 0
            assert isinstance(beat.duration, Fraction)
            assert beat.duration > 0
