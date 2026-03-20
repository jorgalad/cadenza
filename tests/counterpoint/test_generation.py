"""Tests for first species counterpoint generation."""

from __future__ import annotations

import pytest

from cadenza.core.interval import Interval
from cadenza.core.note import Note
from cadenza.core.pitch import Pitch
from cadenza.counterpoint.generation import generate_first_species
from cadenza.counterpoint.rules import (
    IMPERFECT_CONSONANCES,
    PERFECT_CONSONANCES,
)
from cadenza.counterpoint.validation import check_counterpoint

from .conftest import make_phrase


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
