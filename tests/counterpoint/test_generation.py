"""Tests for counterpoint generation: all species."""

from __future__ import annotations

import pytest

from cadenza.core.interval import Interval
from cadenza.core.note import Note
from cadenza.core.pitch import Pitch
from cadenza.counterpoint.generation import (
    generate_first_species,
    generate_second_species,
    generate_third_species,
    generate_fourth_species,
    generate_fifth_species,
    generate_free_counterpoint,
)
from cadenza.counterpoint.rules import (
    IMPERFECT_CONSONANCES,
    PERFECT_CONSONANCES,
)
from cadenza.counterpoint.validation import check_counterpoint

from .conftest import make_phrase


# ---------------------------------------------------------------------------
# First species tests (from 08-01)
# ---------------------------------------------------------------------------


class TestGenerateFirstSpecies:
    """Test first species counterpoint generation."""

    def test_returns_same_length_as_cf(self, cf_c_major) -> None:
        result = generate_first_species(cf_c_major)
        assert len(result) == len(cf_c_major)

    def test_all_notes_consonant(self, cf_c_major) -> None:
        """Every note must be consonant with corresponding CF note."""
        result = generate_first_species(cf_c_major)
        consonances = PERFECT_CONSONANCES | IMPERFECT_CONSONANCES
        for i, (cf_event, cp_event) in enumerate(zip(cf_c_major, result)):
            assert isinstance(cf_event, Note)
            assert isinstance(cp_event, Note)
            interval_mod12 = abs(
                Interval.between(cf_event.pitch, cp_event.pitch).semitones
            ) % 12
            assert interval_mod12 in consonances, (
                f"Position {i}: interval {interval_mod12} not consonant"
            )

    def test_no_parallel_fifths_or_octaves(self, cf_c_major) -> None:
        """Generated result should have no parallel fifths or octaves."""
        result = generate_first_species(cf_c_major)
        violations = check_counterpoint(cf_c_major, result, species=1)
        parallels = [
            v for v in violations
            if v.rule in ("parallel_fifth", "parallel_octave")
        ]
        assert parallels == []

    def test_first_note_perfect_consonance(self, cf_c_major) -> None:
        """First note interval with CF must be a perfect consonance."""
        result = generate_first_species(cf_c_major)
        cf_first = cf_c_major[0]
        cp_first = result[0]
        assert isinstance(cf_first, Note)
        assert isinstance(cp_first, Note)
        interval_mod12 = abs(
            Interval.between(cf_first.pitch, cp_first.pitch).semitones
        ) % 12
        assert interval_mod12 in PERFECT_CONSONANCES

    def test_last_note_perfect_consonance(self, cf_c_major) -> None:
        """Last note interval with CF must be a perfect consonance."""
        result = generate_first_species(cf_c_major)
        cf_last = cf_c_major[-1]
        cp_last = result[-1]
        assert isinstance(cf_last, Note)
        assert isinstance(cp_last, Note)
        interval_mod12 = abs(
            Interval.between(cf_last.pitch, cp_last.pitch).semitones
        ) % 12
        assert interval_mod12 in PERFECT_CONSONANCES

    def test_above_generates_above_cf(self, cf_c_major) -> None:
        """above=True generates CP with MIDI >= CF MIDI."""
        result = generate_first_species(cf_c_major, above=True)
        for cf_event, cp_event in zip(cf_c_major, result):
            assert isinstance(cf_event, Note)
            assert isinstance(cp_event, Note)
            assert cp_event.pitch.midi_number >= cf_event.pitch.midi_number

    def test_below_generates_below_cf(self, cf_c_major) -> None:
        """above=False generates CP with MIDI <= CF MIDI."""
        result = generate_first_species(cf_c_major, above=False)
        for cf_event, cp_event in zip(cf_c_major, result):
            assert isinstance(cf_event, Note)
            assert isinstance(cp_event, Note)
            assert cp_event.pitch.midi_number <= cf_event.pitch.midi_number

    def test_range_constraint(self, cf_c_major) -> None:
        """Custom range constrains all pitches within bounds."""
        low = Pitch("c", "n", 5)
        high = Pitch("c", "n", 6)
        result = generate_first_species(cf_c_major, above=True, range=(low, high))
        for event in result:
            assert isinstance(event, Note)
            assert event.pitch.midi_number >= low.midi_number
            assert event.pitch.midi_number <= high.midi_number

    def test_empty_cf_raises(self) -> None:
        """Empty CF should raise ValueError."""
        with pytest.raises(ValueError):
            generate_first_species(())

    def test_predominantly_stepwise_motion(self, cf_c_major) -> None:
        """Majority of intervals should be stepwise (<= 4 semitones)."""
        result = generate_first_species(cf_c_major)
        stepwise = 0
        total = 0
        for i in range(1, len(result)):
            prev = result[i - 1]
            curr = result[i]
            if isinstance(prev, Note) and isinstance(curr, Note):
                semitones = abs(
                    Interval.between(prev.pitch, curr.pitch).semitones
                )
                total += 1
                if semitones <= 4:
                    stepwise += 1
        assert total > 0
        assert stepwise / total > 0.5, (
            f"Only {stepwise}/{total} intervals are stepwise"
        )


# ---------------------------------------------------------------------------
# Second species tests
# ---------------------------------------------------------------------------


class TestGenerateSecondSpecies:
    """Test second species counterpoint generation."""

    def test_returns_double_length(self, cf_c_major) -> None:
        """Second species: 2 CP notes per CF note."""
        result = generate_second_species(cf_c_major)
        assert len(result) == 2 * len(cf_c_major)

    def test_downbeats_consonant(self, cf_c_major) -> None:
        """Downbeats (even indices) must be consonant with CF."""
        result = generate_second_species(cf_c_major)
        consonances = PERFECT_CONSONANCES | IMPERFECT_CONSONANCES
        for i in range(len(cf_c_major)):
            cp_idx = i * 2  # downbeat
            cf_event = cf_c_major[i]
            cp_event = result[cp_idx]
            assert isinstance(cf_event, Note)
            assert isinstance(cp_event, Note)
            interval_mod12 = abs(
                Interval.between(cf_event.pitch, cp_event.pitch).semitones
            ) % 12
            assert interval_mod12 in consonances, (
                f"Downbeat {i}: interval {interval_mod12} not consonant"
            )

    def test_passes_check_counterpoint(self, cf_c_major) -> None:
        """No error-level violations from check_counterpoint species=2."""
        result = generate_second_species(cf_c_major)
        violations = check_counterpoint(cf_c_major, result, species=2)
        errors = [v for v in violations if v.severity == "error"]
        assert errors == [], f"Error violations: {errors}"

    def test_above_false(self, cf_c_major) -> None:
        """above=False produces valid output below CF."""
        result = generate_second_species(cf_c_major, above=False)
        assert len(result) == 2 * len(cf_c_major)
        # Check downbeats are below CF
        for i in range(len(cf_c_major)):
            cp_idx = i * 2
            cf_event = cf_c_major[i]
            cp_event = result[cp_idx]
            assert isinstance(cf_event, Note)
            assert isinstance(cp_event, Note)
            assert cp_event.pitch.midi_number <= cf_event.pitch.midi_number

    def test_range_constraint(self, cf_c_major) -> None:
        """Range parameter constrains pitches."""
        low = Pitch("c", "n", 5)
        high = Pitch("c", "n", 6)
        result = generate_second_species(cf_c_major, above=True, range=(low, high))
        for event in result:
            assert isinstance(event, Note)
            assert event.pitch.midi_number >= low.midi_number
            assert event.pitch.midi_number <= high.midi_number


# ---------------------------------------------------------------------------
# Third species tests
# ---------------------------------------------------------------------------


class TestGenerateThirdSpecies:
    """Test third species counterpoint generation."""

    def test_returns_quadruple_length(self, cf_c_major) -> None:
        """Third species: 4 CP notes per CF note."""
        result = generate_third_species(cf_c_major)
        assert len(result) == 4 * len(cf_c_major)

    def test_first_of_four_consonant(self, cf_c_major) -> None:
        """First-of-four notes (indices 0,4,8...) must be consonant with CF."""
        result = generate_third_species(cf_c_major)
        consonances = PERFECT_CONSONANCES | IMPERFECT_CONSONANCES
        for i in range(len(cf_c_major)):
            cp_idx = i * 4  # first of four
            cf_event = cf_c_major[i]
            cp_event = result[cp_idx]
            assert isinstance(cf_event, Note)
            assert isinstance(cp_event, Note)
            interval_mod12 = abs(
                Interval.between(cf_event.pitch, cp_event.pitch).semitones
            ) % 12
            assert interval_mod12 in consonances, (
                f"Beat {i}: interval {interval_mod12} not consonant"
            )

    def test_passes_check_counterpoint(self, cf_c_major) -> None:
        """No error-level violations from check_counterpoint species=3."""
        result = generate_third_species(cf_c_major)
        violations = check_counterpoint(cf_c_major, result, species=3)
        errors = [v for v in violations if v.severity == "error"]
        assert errors == [], f"Error violations: {errors}"

    def test_above_false(self, cf_c_major) -> None:
        """above=False produces valid output."""
        result = generate_third_species(cf_c_major, above=False)
        assert len(result) == 4 * len(cf_c_major)

    def test_range_constraint(self, cf_c_major) -> None:
        """Range parameter constrains pitches."""
        low = Pitch("c", "n", 5)
        high = Pitch("c", "n", 6)
        result = generate_third_species(cf_c_major, above=True, range=(low, high))
        for event in result:
            assert isinstance(event, Note)
            assert event.pitch.midi_number >= low.midi_number
            assert event.pitch.midi_number <= high.midi_number


# ---------------------------------------------------------------------------
# Fourth species tests
# ---------------------------------------------------------------------------


class TestGenerateFourthSpecies:
    """Test fourth species counterpoint generation."""

    def test_returns_same_length(self, cf_c_major) -> None:
        """Fourth species: same length as CF (syncopated whole notes)."""
        result = generate_fourth_species(cf_c_major)
        assert len(result) == len(cf_c_major)

    def test_suspensions_resolve_downward(self, cf_c_major) -> None:
        """Dissonant held notes must resolve stepwise downward."""
        result = generate_fourth_species(cf_c_major)
        for i in range(1, len(result) - 1):
            cf_event = cf_c_major[i]
            cp_event = result[i]
            assert isinstance(cf_event, Note)
            assert isinstance(cp_event, Note)
            interval_mod12 = abs(
                Interval.between(cf_event.pitch, cp_event.pitch).semitones
            ) % 12
            # If dissonant (suspension), next note must be step down
            if interval_mod12 not in (PERFECT_CONSONANCES | IMPERFECT_CONSONANCES):
                next_cp = result[i + 1]
                assert isinstance(next_cp, Note)
                step = cp_event.pitch.midi_number - next_cp.pitch.midi_number
                assert 1 <= step <= 2, (
                    f"Position {i}: suspension resolves by {step} semitones "
                    f"(expected 1-2 down)"
                )

    def test_passes_check_counterpoint(self, cf_c_major) -> None:
        """No error-level violations from check_counterpoint species=4."""
        result = generate_fourth_species(cf_c_major)
        violations = check_counterpoint(cf_c_major, result, species=4)
        errors = [v for v in violations if v.severity == "error"]
        assert errors == [], f"Error violations: {errors}"

    def test_above_false(self, cf_c_major) -> None:
        """above=False produces valid output."""
        result = generate_fourth_species(cf_c_major, above=False)
        assert len(result) == len(cf_c_major)

    def test_range_constraint(self, cf_c_major) -> None:
        """Range parameter constrains pitches."""
        low = Pitch("c", "n", 5)
        high = Pitch("c", "n", 6)
        result = generate_fourth_species(cf_c_major, above=True, range=(low, high))
        for event in result:
            assert isinstance(event, Note)
            assert event.pitch.midi_number >= low.midi_number
            assert event.pitch.midi_number <= high.midi_number


# ---------------------------------------------------------------------------
# Fifth species tests
# ---------------------------------------------------------------------------


class TestGenerateFifthSpecies:
    """Test fifth species (florid) counterpoint generation."""

    def test_returns_phrase_with_mixed_durations(self, cf_c_major) -> None:
        """Fifth species must have mixed durations (not all same)."""
        result = generate_fifth_species(cf_c_major)
        assert len(result) > 0
        durations = {event.duration.fraction for event in result if isinstance(event, Note)}
        assert len(durations) >= 2, (
            f"Expected at least 2 different durations, got {durations}"
        )

    def test_passes_check_counterpoint(self, cf_c_major) -> None:
        """No error-level violations from check_counterpoint species=5."""
        result = generate_fifth_species(cf_c_major)
        violations = check_counterpoint(cf_c_major, result, species=5)
        errors = [v for v in violations if v.severity == "error"]
        assert errors == [], f"Error violations: {errors}"

    def test_above_false(self, cf_c_major) -> None:
        """above=False produces valid output."""
        result = generate_fifth_species(cf_c_major, above=False)
        assert len(result) > 0

    def test_range_constraint(self, cf_c_major) -> None:
        """Range parameter constrains pitches."""
        low = Pitch("c", "n", 5)
        high = Pitch("c", "n", 6)
        result = generate_fifth_species(cf_c_major, above=True, range=(low, high))
        for event in result:
            assert isinstance(event, Note)
            assert event.pitch.midi_number >= low.midi_number
            assert event.pitch.midi_number <= high.midi_number


# ---------------------------------------------------------------------------
# Free counterpoint tests
# ---------------------------------------------------------------------------


class TestGenerateFreeCounterpoint:
    """Test free counterpoint generation."""

    def test_no_parallel_fifths_or_octaves(self, cf_c_major) -> None:
        """Free counterpoint should have no parallel fifths or octaves."""
        result = generate_free_counterpoint(cf_c_major)
        violations = check_counterpoint(cf_c_major, result, species=0)
        parallels = [
            v for v in violations
            if v.rule in ("parallel_fifth", "parallel_octave")
        ]
        assert parallels == []

    def test_downbeats_consonant(self, cf_c_major) -> None:
        """Downbeats should be consonant with CF."""
        result = generate_free_counterpoint(cf_c_major)
        consonances = PERFECT_CONSONANCES | IMPERFECT_CONSONANCES
        for i, (cf_event, cp_event) in enumerate(zip(cf_c_major, result)):
            assert isinstance(cf_event, Note)
            assert isinstance(cp_event, Note)
            interval_mod12 = abs(
                Interval.between(cf_event.pitch, cp_event.pitch).semitones
            ) % 12
            assert interval_mod12 in consonances, (
                f"Position {i}: interval {interval_mod12} not consonant"
            )

    def test_passes_check_counterpoint(self, cf_c_major) -> None:
        """No error-level violations from check_counterpoint species=0."""
        result = generate_free_counterpoint(cf_c_major)
        violations = check_counterpoint(cf_c_major, result, species=0)
        errors = [v for v in violations if v.severity == "error"]
        assert errors == [], f"Error violations: {errors}"

    def test_above_false(self, cf_c_major) -> None:
        """above=False produces valid output."""
        result = generate_free_counterpoint(cf_c_major, above=False)
        assert len(result) == len(cf_c_major)

    def test_range_constraint(self, cf_c_major) -> None:
        """Range parameter constrains pitches."""
        low = Pitch("c", "n", 5)
        high = Pitch("c", "n", 6)
        result = generate_free_counterpoint(cf_c_major, above=True, range=(low, high))
        for event in result:
            assert isinstance(event, Note)
            assert event.pitch.midi_number >= low.midi_number
            assert event.pitch.midi_number <= high.midi_number
