"""Tests for L-system melody generation (ALGO-03)."""

from __future__ import annotations

import pytest

from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest
from cadenza.core.pitch import Pitch
from cadenza.composition.lsystem import lsystem_melody


@pytest.fixture
def c4_q() -> Note:
    return Note(pitch=Pitch(step="c", accidental="n", octave=4), duration=Duration.from_cn("q"))


@pytest.fixture
def e4_q() -> Note:
    return Note(pitch=Pitch(step="e", accidental="n", octave=4), duration=Duration.from_cn("q"))


class TestLsystemMelody:
    """Tests for lsystem_melody."""

    def test_lsystem_expansion(self, c4_q: Note, e4_q: Note) -> None:
        # A -> AB, B -> A, 3 generations:
        # gen0: A
        # gen1: AB
        # gen2: ABA
        # gen3: ABAAB
        result = lsystem_melody(
            axiom="A",
            rules={"A": "AB", "B": "A"},
            alphabet={"A": c4_q, "B": e4_q},
            generations=3,
        )
        assert len(result) == 5
        assert result == (c4_q, e4_q, c4_q, c4_q, e4_q)

    def test_lsystem_zero_generations(self, c4_q: Note, e4_q: Note) -> None:
        result = lsystem_melody(
            axiom="AB",
            rules={"A": "AB", "B": "A"},
            alphabet={"A": c4_q, "B": e4_q},
            generations=0,
        )
        assert len(result) == 2
        assert result == (c4_q, e4_q)

    def test_lsystem_unknown_symbols_skipped(self, c4_q: Note, e4_q: Note) -> None:
        result = lsystem_melody(
            axiom="AXB",
            rules={},
            alphabet={"A": c4_q, "B": e4_q},
            generations=0,
        )
        # X not in alphabet, so only A and B
        assert len(result) == 2
        assert result == (c4_q, e4_q)

    def test_lsystem_negative_generations(self, c4_q: Note) -> None:
        with pytest.raises(ValueError):
            lsystem_melody(
                axiom="A",
                rules={},
                alphabet={"A": c4_q},
                generations=-1,
            )

    def test_lsystem_empty_alphabet(self) -> None:
        result = lsystem_melody(
            axiom="AB",
            rules={"A": "AB", "B": "A"},
            alphabet={},
            generations=2,
        )
        assert result == ()
