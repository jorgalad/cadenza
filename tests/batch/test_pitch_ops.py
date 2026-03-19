"""Tests for cadenza.batch.pitch_ops — BATCH-07, BATCH-08."""

from __future__ import annotations

from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest
from cadenza.core.pitch import Pitch
from cadenza.batch.pitch_ops import replace_pitch, filter_phrase


def _make_note(step: str = "c", octave: int = 4, dynamic: str | None = None) -> Note:
    return Note(
        pitch=Pitch(step, "n", octave),
        duration=Duration.from_cn("q"),
        dynamic=dynamic,
    )


def _make_rest() -> Rest:
    return Rest(duration=Duration.from_cn("q"))


# ---------------------------------------------------------------------------
# BATCH-07: replace_pitch
# ---------------------------------------------------------------------------

class TestReplacePitch:
    def test_exact_match(self):
        """Truth: Replacing all C4 with D4 changes only C4 notes."""
        phrase = (
            _make_note("c", 4),
            _make_note("d", 4),
            _make_note("c", 4),
            _make_note("e", 5),
        )
        result = replace_pitch(phrase, Pitch("c", "n", 4), Pitch("d", "n", 4))
        assert result[0].pitch == Pitch("d", "n", 4)
        assert result[1].pitch == Pitch("d", "n", 4)  # was already D4
        assert result[2].pitch == Pitch("d", "n", 4)
        assert result[3].pitch == Pitch("e", "n", 5)  # unchanged

    def test_by_class(self):
        """Replace all C (any octave) with D, preserving octave."""
        phrase = (
            _make_note("c", 3),
            _make_note("c", 5),
            _make_note("d", 4),
        )
        result = replace_pitch(
            phrase, Pitch("c", "n", 4), Pitch("d", "n", 4), by_class=True
        )
        assert result[0].pitch == Pitch("d", "n", 3)
        assert result[1].pitch == Pitch("d", "n", 5)
        assert result[2].pitch == Pitch("d", "n", 4)  # unchanged (already D)

    def test_rests_unchanged(self):
        phrase = (_make_rest(), _make_note("c", 4))
        result = replace_pitch(phrase, Pitch("c", "n", 4), Pitch("d", "n", 4))
        assert isinstance(result[0], Rest)
        assert result[1].pitch == Pitch("d", "n", 4)


# ---------------------------------------------------------------------------
# BATCH-08: filter_phrase
# ---------------------------------------------------------------------------

class TestFilterPhrase:
    def test_filter_by_dynamic(self):
        """Truth: Filtering keeps only matching notes."""
        phrase = (
            _make_note("c", 4, dynamic="f"),
            _make_note("d", 4, dynamic="p"),
            _make_note("e", 4, dynamic="f"),
        )
        result = filter_phrase(
            phrase, lambda e: isinstance(e, Note) and e.dynamic == "f"
        )
        assert len(result) == 2
        assert all(isinstance(e, Note) and e.dynamic == "f" for e in result)

    def test_returns_phrase_type(self):
        phrase = (_make_note(), _make_rest())
        result = filter_phrase(phrase, lambda _: True)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_empty_result(self):
        phrase = (_make_note(),)
        result = filter_phrase(phrase, lambda _: False)
        assert result == ()
