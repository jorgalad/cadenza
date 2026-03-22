"""Tests for variation generation (ALGO-07)."""

from __future__ import annotations

import pytest

from cadenza.core.duration import Duration
from cadenza.core.interval import Interval
from cadenza.core.note import Event, Note
from cadenza.core.phrase import Phrase
from cadenza.composition.variation import generate_variations
from cadenza.transforms.pitch import chromatic_transpose, invert
from cadenza.transforms.melodic import pitch_retrograde, rotate
from cadenza.transforms.rhythm import augment, diminish


@pytest.fixture
def phrase() -> Phrase:
    """Simple 4-note phrase for variation tests."""
    q = Duration.from_cn("q")
    from cadenza.transforms.pitch import from_midi

    return tuple(Note(pitch=from_midi(midi), duration=q) for midi in (60, 64, 67, 72))


class TestGenerateVariationsCount:
    def test_generate_variations_count(self, phrase: Phrase) -> None:
        result = generate_variations(phrase, 3)
        assert len(result) == 3

    def test_all_variations_are_phrases(self, phrase: Phrase) -> None:
        result = generate_variations(phrase, 5)
        for var in result:
            assert isinstance(var, tuple)
            for event in var:
                assert isinstance(event, Event)


class TestVariationPriorityOrder:
    def test_first_variation_is_transpose_up_1(self, phrase: Phrase) -> None:
        result = generate_variations(phrase, 1)
        expected = chromatic_transpose(phrase, Interval("m", 2, 1))
        assert result[0] == expected

    def test_second_variation_is_transpose_up_2(self, phrase: Phrase) -> None:
        result = generate_variations(phrase, 2)
        expected = chromatic_transpose(phrase, Interval("M", 2, 1))
        assert result[1] == expected

    def test_variation_12_is_invert(self, phrase: Phrase) -> None:
        result = generate_variations(phrase, 12)
        expected = invert(phrase)
        assert result[11] == expected

    def test_variation_13_is_retrograde(self, phrase: Phrase) -> None:
        result = generate_variations(phrase, 13)
        expected = pitch_retrograde(phrase)
        assert result[12] == expected

    def test_variation_14_is_augment(self, phrase: Phrase) -> None:
        result = generate_variations(phrase, 14)
        expected = augment(phrase, 2)
        assert result[13] == expected

    def test_variation_15_is_diminish(self, phrase: Phrase) -> None:
        result = generate_variations(phrase, 15)
        expected = diminish(phrase, 2)
        assert result[14] == expected

    def test_variation_16_is_rotate_1(self, phrase: Phrase) -> None:
        result = generate_variations(phrase, 16)
        expected = rotate(phrase, 1)
        assert result[15] == expected


class TestVariationCycling:
    def test_variations_cycle(self, phrase: Phrase) -> None:
        # Total unique = 11 transpositions + 1 invert + 1 retrograde +
        #                1 augment + 1 diminish + (len(phrase)-1) rotations
        total_unique = 11 + 1 + 1 + 1 + 1 + (len(phrase) - 1)
        result = generate_variations(phrase, total_unique + 1)
        assert result[0] == result[total_unique]


class TestVariationEdgeCases:
    def test_empty_phrase_raises(self) -> None:
        with pytest.raises(ValueError, match="empty phrase"):
            generate_variations((), 1)

    def test_n_zero_raises(self) -> None:
        q = Duration.from_cn("q")
        from cadenza.transforms.pitch import from_midi

        phrase = (Note(pitch=from_midi(60), duration=q),)
        with pytest.raises(ValueError, match="n must be positive"):
            generate_variations(phrase, 0)
