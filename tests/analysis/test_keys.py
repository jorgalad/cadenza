"""Tests for key detection and modulation detection (HARM-03, HARM-06)."""

from __future__ import annotations

from fractions import Fraction

import pytest

from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest
from cadenza.core.pitch import Pitch

from cadenza.analysis.keys import (
    KeyResult,
    Modulation,
    detect_key,
    detect_modulations,
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _pitch(step: str, acc: str = "n", octave: int = 4) -> Pitch:
    return Pitch(step=step, accidental=acc, octave=octave)


def _note(step: str, acc: str = "n", octave: int = 4) -> Note:
    return Note(pitch=_pitch(step, acc, octave), duration=Duration.from_cn("q"))


# ---------------------------------------------------------------------------
# detect_key tests
# ---------------------------------------------------------------------------


class TestDetectKey:
    def test_detect_key_c_major(self) -> None:
        pitches = [_pitch(s) for s in "cdefgab"]
        result = detect_key(pitches)
        assert result.root.pitch_class == 0
        assert result.mode == "major"
        assert result.confidence > 0.8

    def test_detect_key_a_minor(self) -> None:
        pitches = [_pitch(s) for s in "abcdefg"]
        result = detect_key(pitches)
        assert result.root.pitch_class == 9
        assert result.mode == "natural_minor"
        assert result.confidence > 0.7

    def test_detect_key_from_phrase(self) -> None:
        # G major: G A B C D E F#
        phrase = (
            _note("g"), _note("a"), _note("b"),
            _note("c"), _note("d"), _note("e"),
            _note("f", "s"),
        )
        result = detect_key(phrase)
        assert result.mode == "major"
        assert result.root.pitch_class == 7

    def test_detect_key_from_pitch_tuple(self) -> None:
        pitches = tuple(_pitch(s) for s in "cdefgab")
        result = detect_key(pitches)
        assert result.root.pitch_class == 0
        assert result.mode == "major"

    def test_detect_key_from_pitch_list(self) -> None:
        pitches = [_pitch(s) for s in "cdefgab"]
        result = detect_key(pitches)
        assert result.root.pitch_class == 0

    def test_detect_key_empty_input(self) -> None:
        result = detect_key([])
        assert result.confidence == 0.0

    def test_detect_key_confidence_range(self) -> None:
        pitches = [_pitch(s) for s in "cdefgab"]
        result = detect_key(pitches)
        assert 0.0 <= result.confidence <= 1.0

    def test_detect_key_preserves_spelling(self) -> None:
        # Eb major: Eb F G Ab Bb C D
        pitches = [
            _pitch("e", "b"), _pitch("f"), _pitch("g"),
            _pitch("a", "b"), _pitch("b", "b"), _pitch("c"), _pitch("d"),
        ]
        result = detect_key(pitches)
        assert result.root.pitch_class == 3  # Eb
        assert result.mode == "major"
        # Root should use flat spelling from input
        assert result.root.step == "e"
        assert result.root.accidental == "b"


# ---------------------------------------------------------------------------
# detect_modulations tests
# ---------------------------------------------------------------------------


class TestDetectModulations:
    def test_detect_modulations_no_modulation(self) -> None:
        # All in C major -- repeat scale pitches
        pitches = [_pitch(s) for s in "cdefgab"] * 3
        result = detect_modulations(pitches)
        assert result == []

    def test_detect_modulations_key_change(self) -> None:
        # Start in C major, shift to G major (F# instead of F)
        c_major = [_pitch(s) for s in "cdefgab"] * 4
        g_major = [
            _pitch("g"), _pitch("a"), _pitch("b"),
            _pitch("c"), _pitch("d"), _pitch("e"),
            _pitch("f", "s"),
        ] * 4
        pitches = c_major + g_major
        result = detect_modulations(pitches, window=4)
        assert len(result) >= 1
        mod = result[0]
        assert isinstance(mod, Modulation)
        assert mod.from_key.root.pitch_class == 0  # C
        assert mod.to_key.root.pitch_class == 7  # G

    def test_detect_modulations_window_parameter(self) -> None:
        # With smaller window, potentially more sensitivity
        c_major = [_pitch(s) for s in "cdefgab"] * 4
        g_major = [
            _pitch("g"), _pitch("a"), _pitch("b"),
            _pitch("c"), _pitch("d"), _pitch("e"),
            _pitch("f", "s"),
        ] * 4
        pitches = c_major + g_major
        large_window = detect_modulations(pitches, window=7)
        small_window = detect_modulations(pitches, window=4)
        # Smaller window should detect at least as many modulations
        assert len(small_window) >= len(large_window)
