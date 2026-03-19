"""Tests for cadenza.batch.mutations — BATCH-01, BATCH-02, BATCH-03, BATCH-04."""

from __future__ import annotations

import pytest

from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest
from cadenza.core.pitch import Pitch
from cadenza.core.phrase import Phrase
from cadenza.batch.mutations import (
    set_articulation_nth,
    set_dynamic_nth,
    crescendo,
    decrescendo,
    add_articulation_if,
    remove_articulation_if,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_note(step: str = "c", octave: int = 4, dynamic: str | None = None,
               articulations: tuple[str, ...] = ()) -> Note:
    return Note(
        pitch=Pitch(step, "n", octave),
        duration=Duration.from_cn("q"),
        dynamic=dynamic,
        articulations=articulations,
    )


def _make_rest() -> Rest:
    return Rest(duration=Duration.from_cn("q"))


def _phrase_12_notes() -> Phrase:
    """12 notes, no rests."""
    return tuple(_make_note("c", 4) for _ in range(12))


def _phrase_with_rests() -> Phrase:
    """10 notes + 2 rests interspersed (12 events total)."""
    events = []
    for i in range(12):
        if i in (3, 7):
            events.append(_make_rest())
        else:
            events.append(_make_note("c", 4))
    return tuple(events)


# ---------------------------------------------------------------------------
# BATCH-01: set_articulation_nth
# ---------------------------------------------------------------------------

class TestSetArticulationNth:
    def test_every_3rd_of_12(self):
        phrase = _phrase_12_notes()
        result = set_articulation_nth(phrase, 3, "stacc")
        note_count = 0
        for event in result:
            assert isinstance(event, Note)
            note_count += 1
            if note_count % 3 == 0:
                assert "stacc" in event.articulations
            else:
                assert "stacc" not in event.articulations
        assert note_count == 12

    def test_positions_3_6_9_12_have_staccato(self):
        """Truth: Setting staccato on every 3rd note of 12-note phrase produces exactly 4."""
        phrase = _phrase_12_notes()
        result = set_articulation_nth(phrase, 3, "stacc")
        stacc_positions = [
            i + 1 for i, e in enumerate(result)
            if isinstance(e, Note) and "stacc" in e.articulations
        ]
        assert stacc_positions == [3, 6, 9, 12]

    def test_rests_skipped_in_counting(self):
        phrase = _phrase_with_rests()
        result = set_articulation_nth(phrase, 3, "stacc")
        note_count = 0
        stacc_notes = 0
        for event in result:
            if isinstance(event, Note):
                note_count += 1
                if "stacc" in event.articulations:
                    stacc_notes += 1
            else:
                assert isinstance(event, Rest)
        # 10 notes, every 3rd -> positions 3, 6, 9 -> 3 staccato notes
        assert stacc_notes == 3

    def test_n_less_than_1_raises(self):
        phrase = _phrase_12_notes()
        with pytest.raises(ValueError):
            set_articulation_nth(phrase, 0, "stacc")

    def test_no_duplicate_articulations(self):
        phrase = tuple(
            _make_note("c", 4, articulations=("stacc",)) for _ in range(3)
        )
        result = set_articulation_nth(phrase, 1, "stacc")
        for event in result:
            assert isinstance(event, Note)
            assert event.articulations.count("stacc") == 1


# ---------------------------------------------------------------------------
# BATCH-02: set_dynamic_nth
# ---------------------------------------------------------------------------

class TestSetDynamicNth:
    def test_every_2nd_of_12(self):
        phrase = _phrase_12_notes()
        result = set_dynamic_nth(phrase, 2, "f")
        note_count = 0
        for event in result:
            assert isinstance(event, Note)
            note_count += 1
            if note_count % 2 == 0:
                assert event.dynamic == "f"
            else:
                assert event.dynamic is None

    def test_rests_skipped(self):
        phrase = _phrase_with_rests()
        result = set_dynamic_nth(phrase, 2, "f")
        note_count = 0
        dyn_notes = 0
        for event in result:
            if isinstance(event, Note):
                note_count += 1
                if event.dynamic == "f":
                    dyn_notes += 1
        # 10 notes, every 2nd -> 5 forte notes
        assert dyn_notes == 5

    def test_n_less_than_1_raises(self):
        phrase = _phrase_12_notes()
        with pytest.raises(ValueError):
            set_dynamic_nth(phrase, 0, "f")


# ---------------------------------------------------------------------------
# BATCH-03: crescendo / decrescendo
# ---------------------------------------------------------------------------

class TestCrescendo:
    def test_pp_to_ff_6_notes(self):
        """Truth: crescendo from pp to ff across 6 notes produces smooth progression."""
        phrase = tuple(_make_note() for _ in range(6))
        result = crescendo(phrase, "pp", "ff")
        dynamics = [e.dynamic for e in result]
        # Proportional linear mapping: pp(1) -> ff(6), 5 steps across 5 gaps
        assert dynamics == ["pp", "p", "mp", "mf", "f", "ff"]

    def test_start_gte_end_raises(self):
        phrase = tuple(_make_note() for _ in range(4))
        with pytest.raises(ValueError):
            crescendo(phrase, "ff", "pp")
        with pytest.raises(ValueError):
            crescendo(phrase, "mf", "mf")

    def test_rests_pass_through(self):
        phrase = (_make_note(), _make_rest(), _make_note(), _make_note())
        result = crescendo(phrase, "p", "f")
        assert isinstance(result[1], Rest)
        # 3 notes get dynamics
        note_dynamics = [e.dynamic for e in result if isinstance(e, Note)]
        assert len(note_dynamics) == 3

    def test_single_note_gets_end_dynamic(self):
        phrase = (_make_note(),)
        result = crescendo(phrase, "pp", "ff")
        assert result[0].dynamic == "ff"


class TestDecrescendo:
    def test_ff_to_pp(self):
        phrase = tuple(_make_note() for _ in range(6))
        result = decrescendo(phrase, "ff", "pp")
        dynamics = [e.dynamic for e in result]
        # Proportional linear mapping: ff(6) -> pp(1), 5 steps across 5 gaps
        assert dynamics == ["ff", "f", "mf", "mp", "p", "pp"]

    def test_start_lte_end_raises(self):
        phrase = tuple(_make_note() for _ in range(4))
        with pytest.raises(ValueError):
            decrescendo(phrase, "pp", "ff")
        with pytest.raises(ValueError):
            decrescendo(phrase, "mf", "mf")


# ---------------------------------------------------------------------------
# BATCH-04: add_articulation_if / remove_articulation_if
# ---------------------------------------------------------------------------

class TestAddArticulationIf:
    def test_add_accent_to_matching(self):
        phrase = (
            _make_note("c", 4, dynamic="f"),
            _make_note("d", 4, dynamic="p"),
            _make_note("e", 4, dynamic="f"),
        )
        result = add_articulation_if(
            phrase, lambda e: isinstance(e, Note) and e.dynamic == "f", "accent"
        )
        assert "accent" in result[0].articulations
        assert "accent" not in result[1].articulations
        assert "accent" in result[2].articulations

    def test_no_duplicate(self):
        phrase = (_make_note("c", 4, articulations=("accent",)),)
        result = add_articulation_if(phrase, lambda _: True, "accent")
        assert result[0].articulations.count("accent") == 1

    def test_rests_matching_predicate_unchanged(self):
        phrase = (_make_rest(),)
        result = add_articulation_if(phrase, lambda _: True, "accent")
        assert isinstance(result[0], Rest)


class TestRemoveArticulationIf:
    def test_remove_stacc_from_matching(self):
        phrase = (
            _make_note("c", 4, articulations=("stacc", "accent")),
            _make_note("d", 4, articulations=("stacc",)),
            _make_note("e", 4, articulations=("accent",)),
        )
        result = remove_articulation_if(phrase, lambda _: True, "stacc")
        assert "stacc" not in result[0].articulations
        assert "accent" in result[0].articulations
        assert "stacc" not in result[1].articulations
        assert result[2].articulations == ("accent",)
