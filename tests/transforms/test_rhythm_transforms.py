"""Tests for rhythm transforms (RHYT-01..05, 07..09)."""

from __future__ import annotations

from fractions import Fraction

import pytest

from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest
from cadenza.core.pitch import Pitch
from cadenza.core.phrase import Phrase
from cadenza.transforms.rhythm import (
    augment,
    diminish,
    extract_rhythm,
    metric_modulation,
    quantize,
    rhythmic_retrograde,
    rhythmic_rotation,
    total_duration,
)

# ---------------------------------------------------------------------------
# Helpers / Fixtures
# ---------------------------------------------------------------------------

C4 = Pitch(step="c", accidental="n", octave=4)
E4 = Pitch(step="e", accidental="n", octave=4)
G4 = Pitch(step="g", accidental="n", octave=4)

DUR_Q = Duration.from_cn("q")
DUR_E = Duration.from_cn("e")
DUR_H = Duration.from_cn("h")
DUR_W = Duration.from_cn("w")


def _note(pitch: Pitch, dur: Duration) -> Note:
    return Note(pitch=pitch, duration=dur)


# Standard test phrases
PHRASE_CEG: Phrase = (_note(C4, DUR_Q), _note(E4, DUR_E), _note(G4, DUR_H))
PHRASE_WITH_REST: Phrase = (_note(C4, DUR_Q), Rest(duration=DUR_E))
EMPTY: Phrase = ()


# ===================================================================
# RHYT-01: rhythmic_retrograde
# ===================================================================

class TestRhythmicRetrograde:
    def test_reverses_durations_keeps_pitch_order(self) -> None:
        result = rhythmic_retrograde(PHRASE_CEG)
        # Pitches should stay in original order: C4, E4, G4
        assert result[0].pitch == C4  # type: ignore[union-attr]
        assert result[1].pitch == E4  # type: ignore[union-attr]
        assert result[2].pitch == G4  # type: ignore[union-attr]
        # Durations should be reversed: h, e, q
        assert result[0].duration == DUR_H
        assert result[1].duration == DUR_E
        assert result[2].duration == DUR_Q

    def test_with_rest(self) -> None:
        result = rhythmic_retrograde(PHRASE_WITH_REST)
        # C4 gets Rest's duration, Rest gets C4's duration
        assert isinstance(result[0], Note)
        assert result[0].duration == DUR_E
        assert isinstance(result[1], Rest)
        assert result[1].duration == DUR_Q

    def test_empty(self) -> None:
        assert rhythmic_retrograde(EMPTY) == ()

    def test_single_event(self) -> None:
        phrase: Phrase = (_note(C4, DUR_Q),)
        assert rhythmic_retrograde(phrase) == phrase


# ===================================================================
# RHYT-02: augment
# ===================================================================

class TestAugment:
    def test_augment_by_2_doubles_durations(self) -> None:
        phrase: Phrase = (_note(C4, DUR_Q), _note(E4, DUR_E))
        result = augment(phrase, 2)
        assert result[0].duration.fraction == Fraction(1, 2)
        assert result[1].duration.fraction == Fraction(1, 4)

    def test_augment_with_fraction(self) -> None:
        phrase: Phrase = (_note(C4, DUR_Q),)
        result = augment(phrase, Fraction(3, 2))
        assert result[0].duration.fraction == Fraction(3, 8)

    def test_augment_with_float(self) -> None:
        phrase: Phrase = (_note(C4, DUR_Q),)
        result = augment(phrase, 1.5)
        # 1.5 -> Fraction(3,2); q=1/4 * 3/2 = 3/8
        assert result[0].duration.fraction == Fraction(3, 8)

    def test_augment_rest(self) -> None:
        phrase: Phrase = (Rest(duration=DUR_Q),)
        result = augment(phrase, 2)
        assert result[0].duration.fraction == Fraction(1, 2)

    def test_augment_empty(self) -> None:
        assert augment(EMPTY, 2) == ()


# ===================================================================
# RHYT-03: diminish
# ===================================================================

class TestDiminish:
    def test_diminish_by_2_halves_durations(self) -> None:
        phrase: Phrase = (_note(C4, DUR_Q), _note(E4, DUR_H))
        result = diminish(phrase, 2)
        assert result[0].duration.fraction == Fraction(1, 8)
        assert result[1].duration.fraction == Fraction(1, 4)

    def test_diminish_rest(self) -> None:
        phrase: Phrase = (Rest(duration=DUR_H),)
        result = diminish(phrase, 2)
        assert result[0].duration.fraction == Fraction(1, 4)

    def test_diminish_empty(self) -> None:
        assert diminish(EMPTY, 2) == ()


# ===================================================================
# RHYT-04: rhythmic_rotation
# ===================================================================

class TestRhythmicRotation:
    def test_rotate_positive_1(self) -> None:
        # [C4(q), E4(e), G4(h)] rotate durations by +1 ->
        # durations shift left: [e, h, q], pitches stay [C4, E4, G4]
        result = rhythmic_rotation(PHRASE_CEG, 1)
        assert result[0].pitch == C4  # type: ignore[union-attr]
        assert result[0].duration == DUR_E
        assert result[1].pitch == E4  # type: ignore[union-attr]
        assert result[1].duration == DUR_H
        assert result[2].pitch == G4  # type: ignore[union-attr]
        assert result[2].duration == DUR_Q

    def test_rotate_negative(self) -> None:
        # Negative rotation = rotate right: last duration moves to front
        result = rhythmic_rotation(PHRASE_CEG, -1)
        assert result[0].duration == DUR_H  # h from end moves to front
        assert result[1].duration == DUR_Q
        assert result[2].duration == DUR_E

    def test_rotate_empty(self) -> None:
        assert rhythmic_rotation(EMPTY, 1) == ()

    def test_rotate_full_cycle(self) -> None:
        # Rotating by len should give back the same phrase
        result = rhythmic_rotation(PHRASE_CEG, 3)
        for i in range(3):
            assert result[i].duration == PHRASE_CEG[i].duration


# ===================================================================
# RHYT-05: metric_modulation
# ===================================================================

class TestMetricModulation:
    def test_dotted_quarter_to_quarter(self) -> None:
        # old_unit = dotted quarter (3/8), new_unit = quarter (1/4)
        # ratio = (1/4) / (3/8) = 2/3
        old_unit = Duration.from_cn("q", dots=1)
        new_unit = Duration.from_cn("q")
        phrase: Phrase = (_note(C4, DUR_Q), _note(E4, DUR_H))
        result = metric_modulation(phrase, old_unit, new_unit)
        # q = 1/4 * 2/3 = 1/6
        assert result[0].duration.fraction == Fraction(1, 6)
        # h = 1/2 * 2/3 = 1/3
        assert result[1].duration.fraction == Fraction(1, 3)

    def test_modulation_empty(self) -> None:
        old_unit = Duration.from_cn("q", dots=1)
        new_unit = Duration.from_cn("q")
        assert metric_modulation(EMPTY, old_unit, new_unit) == ()


# ===================================================================
# RHYT-07: extract_rhythm
# ===================================================================

class TestExtractRhythm:
    def test_basic(self) -> None:
        result = extract_rhythm(PHRASE_CEG)
        assert result == (DUR_Q, DUR_E, DUR_H)

    def test_includes_rest_durations(self) -> None:
        result = extract_rhythm(PHRASE_WITH_REST)
        assert result == (DUR_Q, DUR_E)

    def test_empty(self) -> None:
        assert extract_rhythm(EMPTY) == ()


# ===================================================================
# RHYT-08: quantize
# ===================================================================

class TestQuantize:
    def test_snap_to_nearest(self) -> None:
        # Duration 3/16 is between eighth (2/16) and quarter (4/16)
        # Closer to eighth (distance 1/16 vs 1/16... actually equidistant;
        # but 3/16 - 2/16 = 1/16 and 4/16 - 3/16 = 1/16)
        # With equal distance, first grid value wins (or implementation detail)
        odd_dur = Duration(fraction=Fraction(3, 16), base="e")
        phrase: Phrase = (_note(C4, odd_dur),)
        grid = [DUR_Q, DUR_E]
        result = quantize(phrase, grid)
        # Either eighth or quarter is acceptable when equidistant;
        # test that it snaps to one of them
        assert result[0].duration.fraction in (Fraction(1, 4), Fraction(1, 8))

    def test_snap_closer_to_quarter(self) -> None:
        # Duration 7/32 = 0.21875, quarter=0.25, eighth=0.125
        # Distance to quarter: |7/32 - 8/32| = 1/32
        # Distance to eighth: |7/32 - 4/32| = 3/32
        # Should snap to quarter
        odd_dur = Duration(fraction=Fraction(7, 32), base="e")
        phrase: Phrase = (_note(C4, odd_dur),)
        grid = [DUR_Q, DUR_E]
        result = quantize(phrase, grid)
        assert result[0].duration.fraction == Fraction(1, 4)

    def test_cn_string_grid(self) -> None:
        odd_dur = Duration(fraction=Fraction(7, 32), base="e")
        phrase: Phrase = (_note(C4, odd_dur),)
        result = quantize(phrase, ["q", "e"])
        assert result[0].duration.fraction == Fraction(1, 4)

    def test_quantize_rest(self) -> None:
        odd_dur = Duration(fraction=Fraction(7, 32), base="e")
        phrase: Phrase = (Rest(duration=odd_dur),)
        result = quantize(phrase, [DUR_Q, DUR_E])
        assert result[0].duration.fraction == Fraction(1, 4)


# ===================================================================
# RHYT-09: total_duration
# ===================================================================

class TestTotalDuration:
    def test_basic(self) -> None:
        # q + e + h = 1/4 + 1/8 + 1/2 = 7/8
        assert total_duration(PHRASE_CEG) == Fraction(7, 8)

    def test_includes_rests(self) -> None:
        # q + e = 1/4 + 1/8 = 3/8
        assert total_duration(PHRASE_WITH_REST) == Fraction(3, 8)

    def test_empty(self) -> None:
        assert total_duration(EMPTY) == Fraction(0)
