"""Tests for Note and Rest frozen dataclasses."""

from __future__ import annotations

import pytest

from cadenza.core.pitch import Pitch
from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest, Event


class TestNoteCreation:
    def test_create_note(self) -> None:
        n = Note(Pitch("c", "n", 4), Duration.from_omn("q"), "mf", ("stacc",))
        assert n.pitch == Pitch("c", "n", 4)
        assert n.duration == Duration.from_omn("q")
        assert n.dynamic == "mf"
        assert n.articulations == ("stacc",)

    def test_note_no_dynamic(self) -> None:
        n = Note(Pitch("c", "n", 4), Duration.from_omn("q"), None, ())
        assert n.dynamic is None

    def test_note_no_articulations(self) -> None:
        n = Note(Pitch("c", "n", 4), Duration.from_omn("q"), "mf", ())
        assert n.articulations == ()


class TestNoteImmutability:
    def test_frozen(self) -> None:
        n = Note(Pitch("c", "n", 4), Duration.from_omn("q"), "mf", ("stacc",))
        with pytest.raises(AttributeError):
            n.pitch = Pitch("d", "n", 4)  # type: ignore[misc]

    def test_hashable(self) -> None:
        n = Note(Pitch("c", "n", 4), Duration.from_omn("q"), "mf", ("stacc",))
        {n}
        {n: 1}

    def test_identical_hash_equally(self) -> None:
        n1 = Note(Pitch("c", "n", 4), Duration.from_omn("q"), "mf", ("stacc",))
        n2 = Note(Pitch("c", "n", 4), Duration.from_omn("q"), "mf", ("stacc",))
        assert n1 == n2
        assert hash(n1) == hash(n2)


class TestNoteEquality:
    def test_eq_all_fields(self) -> None:
        n1 = Note(Pitch("c", "n", 4), Duration.from_omn("q"), "mf", ("stacc",))
        n2 = Note(Pitch("c", "n", 4), Duration.from_omn("q"), "mf", ("stacc",))
        assert n1 == n2

    def test_neq_different_pitch(self) -> None:
        n1 = Note(Pitch("c", "n", 4), Duration.from_omn("q"), "mf", ())
        n2 = Note(Pitch("d", "n", 4), Duration.from_omn("q"), "mf", ())
        assert n1 != n2


class TestRestCreation:
    def test_create_rest(self) -> None:
        r = Rest(Duration.from_omn("q"))
        assert r.duration == Duration.from_omn("q")

    def test_rest_is_not_note(self) -> None:
        r = Rest(Duration.from_omn("q"))
        n = Note(Pitch("c", "n", 4), Duration.from_omn("q"), None, ())
        assert not isinstance(r, Note)
        assert type(r) != type(n)


class TestRestImmutability:
    def test_frozen(self) -> None:
        r = Rest(Duration.from_omn("q"))
        with pytest.raises(AttributeError):
            r.duration = Duration.from_omn("h")  # type: ignore[misc]

    def test_hashable(self) -> None:
        r = Rest(Duration.from_omn("q"))
        {r}
        {r: 1}
