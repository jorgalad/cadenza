"""Tests for cadenza.batch.humanize — BATCH-06."""

from __future__ import annotations

from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest
from cadenza.core.pitch import Pitch
from cadenza.batch.humanize import humanize


def _make_note(dynamic: str | None = "mf") -> Note:
    return Note(
        pitch=Pitch("c", "n", 4),
        duration=Duration.from_cn("q"),
        dynamic=dynamic,
    )


def _make_rest() -> Rest:
    return Rest(duration=Duration.from_cn("q"))


# ---------------------------------------------------------------------------
# BATCH-06: humanize
# ---------------------------------------------------------------------------

class TestHumanize:
    def test_deterministic_with_seed(self):
        """Truth: same seed -> identical output."""
        phrase = tuple(_make_note("mf") for _ in range(10))
        result1 = humanize(phrase, seed=42)
        result2 = humanize(phrase, seed=42)
        assert result1 == result2

    def test_dynamics_shift_by_at_most_one(self):
        from cadenza.batch.mutations import DYNAMICS, DYNAMIC_INDEX
        phrase = tuple(_make_note("mf") for _ in range(20))
        result = humanize(phrase, seed=123)
        original_idx = DYNAMIC_INDEX["mf"]
        for event in result:
            assert isinstance(event, Note)
            new_idx = DYNAMIC_INDEX[event.dynamic]
            assert abs(new_idx - original_idx) <= 1

    def test_none_dynamic_unchanged(self):
        phrase = (_make_note(dynamic=None),)
        result = humanize(phrase, seed=42)
        assert result[0].dynamic is None

    def test_ppp_clamp(self):
        """ppp can only become ppp or pp."""
        from cadenza.batch.mutations import DYNAMIC_INDEX
        phrase = tuple(_make_note("ppp") for _ in range(50))
        result = humanize(phrase, seed=99)
        for event in result:
            assert isinstance(event, Note)
            assert event.dynamic in ("ppp", "pp")

    def test_fff_clamp(self):
        """fff can only become fff or ff."""
        phrase = tuple(_make_note("fff") for _ in range(50))
        result = humanize(phrase, seed=99)
        for event in result:
            assert isinstance(event, Note)
            assert event.dynamic in ("fff", "ff")

    def test_rests_unchanged(self):
        phrase = (_make_rest(), _make_note("f"))
        result = humanize(phrase, seed=42)
        assert isinstance(result[0], Rest)
