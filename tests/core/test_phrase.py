"""Tests for Phrase type alias."""

from __future__ import annotations

from cadenza.core.pitch import Pitch
from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest
from cadenza.core.phrase import Phrase


class TestPhrase:
    def test_phrase_with_notes_and_rests(self) -> None:
        p: Phrase = (
            Note(Pitch("c", "n", 4), Duration.from_omn("q"), "mf", ()),
            Rest(Duration.from_omn("e")),
            Note(Pitch("d", "n", 4), Duration.from_omn("q"), "mf", ()),
        )
        assert len(p) == 3

    def test_phrase_is_immutable(self) -> None:
        p: Phrase = (
            Note(Pitch("c", "n", 4), Duration.from_omn("q"), "mf", ()),
        )
        # Tuples are immutable
        assert isinstance(p, tuple)

    def test_phrase_is_hashable(self) -> None:
        p: Phrase = (
            Note(Pitch("c", "n", 4), Duration.from_omn("q"), "mf", ()),
        )
        {p}
        {p: 1}

    def test_empty_phrase(self) -> None:
        p: Phrase = ()
        assert len(p) == 0

    def test_phrase_preserves_order(self) -> None:
        n1 = Note(Pitch("c", "n", 4), Duration.from_omn("q"), "mf", ())
        n2 = Note(Pitch("d", "n", 4), Duration.from_omn("q"), "mf", ())
        p: Phrase = (n1, n2)
        assert p[0] is n1
        assert p[1] is n2
