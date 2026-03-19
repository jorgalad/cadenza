"""Tests for Duration frozen dataclass."""

from __future__ import annotations

from fractions import Fraction

import pytest

from cadenza.core.duration import Duration, BASE_DURATIONS


class TestDurationFromOmn:
    def test_quarter(self) -> None:
        assert Duration.from_cn("q").fraction == Fraction(1, 4)

    def test_half(self) -> None:
        assert Duration.from_cn("h").fraction == Fraction(1, 2)

    def test_whole(self) -> None:
        assert Duration.from_cn("w").fraction == Fraction(1, 1)

    def test_eighth(self) -> None:
        assert Duration.from_cn("e").fraction == Fraction(1, 8)

    def test_sixteenth(self) -> None:
        assert Duration.from_cn("s").fraction == Fraction(1, 16)

    def test_thirtysecond(self) -> None:
        assert Duration.from_cn("t").fraction == Fraction(1, 32)

    def test_sixtyfourth(self) -> None:
        assert Duration.from_cn("x").fraction == Fraction(1, 64)


class TestDurationDots:
    def test_dotted_quarter(self) -> None:
        assert Duration.from_cn("q", dots=1).fraction == Fraction(3, 8)

    def test_dotted_half(self) -> None:
        assert Duration.from_cn("h", dots=1).fraction == Fraction(3, 4)

    def test_double_dotted_quarter(self) -> None:
        assert Duration.from_cn("q", dots=2).fraction == Fraction(7, 16)


class TestDurationTuplets:
    def test_triplet_quarter(self) -> None:
        assert Duration.from_cn("q", tuplet=3).fraction == Fraction(1, 6)

    def test_triplet_eighth(self) -> None:
        assert Duration.from_cn("e", tuplet=3).fraction == Fraction(1, 12)

    def test_quintuplet_quarter(self) -> None:
        # Quintuplet: 5 in the time of 4 -> multiply by 4/5
        assert Duration.from_cn("q", tuplet=5).fraction == Fraction(1, 5)


class TestDurationImmutability:
    def test_frozen(self) -> None:
        d = Duration.from_cn("q")
        with pytest.raises(AttributeError):
            d.fraction = Fraction(1, 2)  # type: ignore[misc]

    def test_hashable(self) -> None:
        d = Duration.from_cn("q")
        {d}  # usable in set
        {d: 1}  # usable as dict key


class TestDurationValidation:
    def test_invalid_base_raises(self) -> None:
        with pytest.raises((ValueError, KeyError)):
            Duration.from_cn("z")


class TestDurationMeasureMath:
    def test_dotted_q_plus_e_plus_h_equals_whole(self) -> None:
        dq = Duration.from_cn("q", dots=1).fraction
        e = Duration.from_cn("e").fraction
        h = Duration.from_cn("h").fraction
        assert dq + e + h == Fraction(1, 1)


class TestDurationOrdering:
    def test_shorter_is_less(self) -> None:
        e = Duration.from_cn("e")
        q = Duration.from_cn("q")
        assert e < q

    def test_longer_is_greater(self) -> None:
        h = Duration.from_cn("h")
        q = Duration.from_cn("q")
        assert h > q


class TestBaseDurations:
    def test_all_keys_present(self) -> None:
        assert set(BASE_DURATIONS.keys()) == {"w", "h", "q", "e", "s", "t", "x"}
