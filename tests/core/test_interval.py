"""Tests for Interval frozen dataclass."""

from __future__ import annotations

import pytest

from cadenza.core.pitch import Pitch
from cadenza.core.interval import Interval


class TestIntervalBetween:
    def test_major_third(self) -> None:
        i = Interval.between(Pitch("c", "n", 4), Pitch("e", "n", 4))
        assert i.quality == "M"
        assert i.number == 3
        assert i.direction == 1

    def test_minor_third(self) -> None:
        i = Interval.between(Pitch("c", "n", 4), Pitch("e", "b", 4))
        assert i.quality == "m"
        assert i.number == 3

    def test_perfect_fifth(self) -> None:
        i = Interval.between(Pitch("c", "n", 4), Pitch("g", "n", 4))
        assert i.quality == "P"
        assert i.number == 5

    def test_perfect_fourth(self) -> None:
        i = Interval.between(Pitch("c", "n", 4), Pitch("f", "n", 4))
        assert i.quality == "P"
        assert i.number == 4

    def test_perfect_octave(self) -> None:
        i = Interval.between(Pitch("c", "n", 4), Pitch("c", "n", 5))
        assert i.quality == "P"
        assert i.number == 8

    def test_perfect_unison(self) -> None:
        i = Interval.between(Pitch("c", "n", 4), Pitch("c", "n", 4))
        assert i.quality == "P"
        assert i.number == 1

    def test_diminished_fifth(self) -> None:
        i = Interval.between(Pitch("c", "n", 4), Pitch("g", "b", 4))
        assert i.quality == "d"
        assert i.number == 5

    def test_augmented_fourth(self) -> None:
        i = Interval.between(Pitch("c", "n", 4), Pitch("f", "s", 4))
        assert i.quality == "A"
        assert i.number == 4


class TestIntervalCompound:
    def test_compound_ninth(self) -> None:
        i = Interval.between(Pitch("c", "n", 4), Pitch("d", "n", 5))
        assert i.number == 9


class TestIntervalImmutability:
    def test_frozen(self) -> None:
        i = Interval.between(Pitch("c", "n", 4), Pitch("e", "n", 4))
        with pytest.raises(AttributeError):
            i.quality = "m"  # type: ignore[misc]

    def test_hashable(self) -> None:
        i = Interval.between(Pitch("c", "n", 4), Pitch("e", "n", 4))
        {i}
        {i: 1}
