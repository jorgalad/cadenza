"""Tests for pitch transform functions (PTCH-01 through PTCH-09)."""

from __future__ import annotations

import pytest

from cadenza.core.pitch import Pitch
from cadenza.core.duration import Duration
from cadenza.core.interval import Interval
from cadenza.core.note import Note, Rest
from cadenza.core.phrase import Phrase
from cadenza.transforms.pitch import (
    chromatic_transpose,
    diatonic_transpose,
    enharmonic_respell,
    from_frequency,
    from_midi,
    interval_between,
    invert,
    nearest_in_scale,
    pitch_class,
    pitch_in_scale,
    to_frequency,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _p(step: str, acc: str, octave: int) -> Pitch:
    """Shorthand pitch constructor."""
    return Pitch(step=step, accidental=acc, octave=octave)


# ---------------------------------------------------------------------------
# PTCH-01: chromatic_transpose
# ---------------------------------------------------------------------------

class TestChromaticTranspose:
    """Tests for chromatic_transpose."""

    def test_c4_up_minor_third(self) -> None:
        """C4 up minor 3rd -> Eb4."""
        phrase: Phrase = (
            Note(pitch=_p("c", "n", 4), duration=Duration.from_omn("q")),
        )
        iv = Interval(quality="m", number=3, direction=1)
        result = chromatic_transpose(phrase, iv)
        assert len(result) == 1
        note = result[0]
        assert isinstance(note, Note)
        assert note.pitch == _p("e", "b", 4)

    def test_c_major_scale_up_minor_third(self, c_major_scale_phrase: Phrase) -> None:
        """C major scale up m3 -> Eb,F,G,Ab,Bb,C,D (all flats, no sharps)."""
        iv = Interval(quality="m", number=3, direction=1)
        result = chromatic_transpose(c_major_scale_phrase, iv)
        expected_pitches = [
            _p("e", "b", 4),   # Eb4
            _p("f", "n", 4),   # F4
            _p("g", "n", 4),   # G4
            _p("a", "b", 4),   # Ab4
            _p("b", "b", 4),   # Bb4
            _p("c", "n", 5),   # C5
            _p("d", "n", 5),   # D5
        ]
        for i, event in enumerate(result):
            assert isinstance(event, Note)
            assert event.pitch == expected_pitches[i], (
                f"Note {i}: expected {expected_pitches[i]}, got {event.pitch}"
            )

    def test_b4_up_minor_second_octave_boundary(self) -> None:
        """B4 up minor 2nd -> C5 (crosses octave boundary)."""
        phrase: Phrase = (
            Note(pitch=_p("b", "n", 4), duration=Duration.from_omn("q")),
        )
        iv = Interval(quality="m", number=2, direction=1)
        result = chromatic_transpose(phrase, iv)
        assert isinstance(result[0], Note)
        assert result[0].pitch == _p("c", "n", 5)

    def test_rest_passes_through(self, phrase_with_rests: Phrase) -> None:
        """Rests pass through chromatic transpose unchanged."""
        iv = Interval(quality="P", number=5, direction=1)
        result = chromatic_transpose(phrase_with_rests, iv)
        assert isinstance(result[1], Rest)
        assert isinstance(result[3], Rest)
        assert result[1].duration == phrase_with_rests[1].duration
        assert result[3].duration == phrase_with_rests[3].duration

    def test_empty_phrase(self) -> None:
        """Empty phrase returns ()."""
        result = chromatic_transpose((), Interval(quality="P", number=5, direction=1))
        assert result == ()

    def test_preserves_dynamics_and_articulations(self) -> None:
        """Dynamics and articulations are preserved after transpose."""
        phrase: Phrase = (
            Note(
                pitch=_p("c", "n", 4),
                duration=Duration.from_omn("q"),
                dynamic="ff",
                articulations=("staccato",),
            ),
        )
        iv = Interval(quality="M", number=2, direction=1)
        result = chromatic_transpose(phrase, iv)
        assert isinstance(result[0], Note)
        assert result[0].dynamic == "ff"
        assert result[0].articulations == ("staccato",)

    def test_descending_transpose(self) -> None:
        """G4 down perfect 5th -> C4."""
        phrase: Phrase = (
            Note(pitch=_p("g", "n", 4), duration=Duration.from_omn("q")),
        )
        iv = Interval(quality="P", number=5, direction=-1)
        result = chromatic_transpose(phrase, iv)
        assert isinstance(result[0], Note)
        assert result[0].pitch == _p("c", "n", 4)


# ---------------------------------------------------------------------------
# PTCH-01: diatonic_transpose (stub)
# ---------------------------------------------------------------------------

class TestDiatonicTranspose:
    """Tests for diatonic_transpose (now implemented with Scale)."""

    def test_diatonic_transpose_no_scale_returns_phrase(self) -> None:
        """Without a scale argument, returns phrase unchanged."""
        phrase: Phrase = (
            Note(pitch=_p("c", "n", 4), duration=Duration.from_omn("q")),
        )
        result = diatonic_transpose(phrase, 2)
        assert result == phrase


# ---------------------------------------------------------------------------
# PTCH-02: invert
# ---------------------------------------------------------------------------

class TestInvert:
    """Tests for invert."""

    def test_ceg_around_c4(self) -> None:
        """[C4, E4, G4] around C4 -> [C4, Ab3, F3]."""
        q = Duration.from_omn("q")
        phrase: Phrase = (
            Note(pitch=_p("c", "n", 4), duration=q),
            Note(pitch=_p("e", "n", 4), duration=q),
            Note(pitch=_p("g", "n", 4), duration=q),
        )
        result = invert(phrase)
        pitches = [e.pitch for e in result if isinstance(e, Note)]
        assert pitches == [_p("c", "n", 4), _p("a", "b", 3), _p("f", "n", 3)]

    def test_default_axis_is_first_note(self) -> None:
        """Default axis = first note's pitch."""
        q = Duration.from_omn("q")
        phrase: Phrase = (
            Note(pitch=_p("e", "n", 4), duration=q),
            Note(pitch=_p("g", "n", 4), duration=q),
        )
        result = invert(phrase)
        # First note stays the same (axis)
        assert isinstance(result[0], Note)
        assert result[0].pitch == _p("e", "n", 4)

    def test_explicit_axis_override(self) -> None:
        """Explicit axis overrides the default."""
        q = Duration.from_omn("q")
        phrase: Phrase = (
            Note(pitch=_p("c", "n", 4), duration=q),
            Note(pitch=_p("e", "n", 4), duration=q),
        )
        # Invert around D4 instead of C4
        result = invert(phrase, axis=_p("d", "n", 4))
        pitches = [e.pitch for e in result if isinstance(e, Note)]
        # C4 is M2 below D4 -> reflected M2 above D4 -> E4
        # E4 is M2 above D4 -> reflected M2 below D4 -> C4
        assert pitches == [_p("e", "n", 4), _p("c", "n", 4)]

    def test_all_rests_returns_unchanged(self) -> None:
        """All-rests phrase returns unchanged."""
        e = Duration.from_omn("e")
        phrase: Phrase = (Rest(duration=e), Rest(duration=e))
        result = invert(phrase)
        assert result == phrase

    def test_empty_phrase(self) -> None:
        """Empty phrase returns ()."""
        assert invert(()) == ()

    def test_rests_pass_through(self, phrase_with_rests: Phrase) -> None:
        """Rests in a mixed phrase pass through inversion unchanged."""
        result = invert(phrase_with_rests)
        assert isinstance(result[1], Rest)
        assert isinstance(result[3], Rest)


# ---------------------------------------------------------------------------
# PTCH-03: interval_between
# ---------------------------------------------------------------------------

class TestIntervalBetween:
    """Tests for interval_between."""

    def test_c4_to_e4(self) -> None:
        """C4 to E4 -> Interval(M, 3, 1)."""
        iv = interval_between(_p("c", "n", 4), _p("e", "n", 4))
        assert iv.quality == "M"
        assert iv.number == 3
        assert iv.direction == 1

    def test_e4_to_c4(self) -> None:
        """E4 to C4 -> Interval(M, 3, -1)."""
        iv = interval_between(_p("e", "n", 4), _p("c", "n", 4))
        assert iv.quality == "M"
        assert iv.number == 3
        assert iv.direction == -1


# ---------------------------------------------------------------------------
# PTCH-04: enharmonic_respell
# ---------------------------------------------------------------------------

class TestEnharmonicRespell:
    """Tests for enharmonic_respell."""

    def test_eb3_to_ds3_prefer_sharps(self) -> None:
        """Eb3 -> D#3 (prefer_sharps=True, default)."""
        result = enharmonic_respell(_p("e", "b", 3))
        assert result == _p("d", "s", 3)

    def test_ds3_to_eb3_prefer_flats(self) -> None:
        """D#3 -> Eb3 (prefer_sharps=False)."""
        result = enharmonic_respell(_p("d", "s", 3), prefer_sharps=False)
        assert result == _p("e", "b", 3)

    def test_c4_natural_unchanged(self) -> None:
        """C4 natural -> C4 (no respelling needed, stays C4)."""
        result = enharmonic_respell(_p("c", "n", 4))
        assert result == _p("c", "n", 4)

    def test_enharmonic_equal(self) -> None:
        """Respelled pitch has same MIDI number."""
        original = _p("e", "b", 3)
        respelled = enharmonic_respell(original)
        assert original.midi_number == respelled.midi_number


# ---------------------------------------------------------------------------
# PTCH-05: pitch_class
# ---------------------------------------------------------------------------

class TestPitchClass:
    """Tests for pitch_class."""

    def test_c4(self) -> None:
        assert pitch_class(_p("c", "n", 4)) == 0

    def test_a4(self) -> None:
        assert pitch_class(_p("a", "n", 4)) == 9

    def test_eb3(self) -> None:
        assert pitch_class(_p("e", "b", 3)) == 3


# ---------------------------------------------------------------------------
# PTCH-06: from_midi
# ---------------------------------------------------------------------------

class TestFromMidi:
    """Tests for from_midi."""

    def test_midi_60_is_c4(self) -> None:
        """MIDI 60 -> C4."""
        assert from_midi(60) == _p("c", "n", 4)

    def test_midi_61_sharp(self) -> None:
        """MIDI 61, prefer_sharps=True -> C#4."""
        assert from_midi(61, prefer_sharps=True) == _p("c", "s", 4)

    def test_midi_61_flat(self) -> None:
        """MIDI 61, prefer_sharps=False -> Db4."""
        assert from_midi(61, prefer_sharps=False) == _p("d", "b", 4)

    def test_midi_69_is_a4(self) -> None:
        """MIDI 69 -> A4."""
        assert from_midi(69) == _p("a", "n", 4)

    def test_roundtrip_c4(self) -> None:
        """C4 -> MIDI 60 -> C4 roundtrip."""
        p = _p("c", "n", 4)
        assert from_midi(p.midi_number) == p


# ---------------------------------------------------------------------------
# PTCH-07: to_frequency / from_frequency
# ---------------------------------------------------------------------------

class TestFrequencyConversion:
    """Tests for to_frequency and from_frequency."""

    def test_a4_to_440(self) -> None:
        """A4 -> 440.0 Hz."""
        assert to_frequency(_p("a", "n", 4)) == pytest.approx(440.0, abs=0.01)

    def test_c4_frequency(self) -> None:
        """C4 -> ~261.63 Hz."""
        assert to_frequency(_p("c", "n", 4)) == pytest.approx(261.63, abs=0.01)

    def test_from_frequency_440(self) -> None:
        """from_frequency(440.0) -> A4."""
        assert from_frequency(440.0) == _p("a", "n", 4)

    def test_from_frequency_261(self) -> None:
        """from_frequency(261.63) -> C4."""
        assert from_frequency(261.63) == _p("c", "n", 4)

    def test_roundtrip_a4(self) -> None:
        """A4 -> Hz -> A4 roundtrip."""
        p = _p("a", "n", 4)
        assert from_frequency(to_frequency(p)) == p


# ---------------------------------------------------------------------------
# PTCH-08: pitch_in_scale (stub)
# ---------------------------------------------------------------------------

class TestPitchInScaleStub:
    """Tests for pitch_in_scale (now implemented with Scale)."""

    def test_pitch_in_scale_implemented(self) -> None:
        """pitch_in_scale works with a Scale object."""
        from cadenza.theory.scales import get_scale
        scale = get_scale(_p("c", "n", 4), "major")
        assert pitch_in_scale(_p("c", "n", 4), scale) is True


# ---------------------------------------------------------------------------
# PTCH-09: nearest_in_scale (stub)
# ---------------------------------------------------------------------------

class TestNearestInScaleStub:
    """Tests for nearest_in_scale (now implemented with Scale)."""

    def test_nearest_in_scale_implemented(self) -> None:
        """nearest_in_scale works with a Scale object."""
        from cadenza.theory.scales import get_scale
        scale = get_scale(_p("c", "n", 4), "major")
        result = nearest_in_scale(_p("c", "n", 4), scale)
        assert result == _p("c", "n", 4)
