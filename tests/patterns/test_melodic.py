"""Tests for melodic pattern functions: isorhythm, ostinato, accent_pattern."""

from __future__ import annotations

import pytest

from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest
from cadenza.core.phrase import Phrase
from cadenza.patterns.melodic import accent_pattern, isorhythm, ostinato
from cadenza.transforms.pitch import from_midi


# ---------------------------------------------------------------------------
# isorhythm
# ---------------------------------------------------------------------------


class TestIsorhythm:
    def test_isorhythm_basic_cycle(self) -> None:
        q = Duration.from_cn("q")
        e = Duration.from_cn("e")
        talea = (q, e, e)
        color = (60, 64, 67, 72)
        result = isorhythm(talea, color, n=1)
        # LCM(3, 4) = 12 notes
        assert len(result) == 12
        # note[0]: duration=q (0%3=0), pitch=from_midi(60) (0%4=0)
        assert isinstance(result[0], Note)
        assert result[0].duration == q
        assert result[0].pitch == from_midi(60)
        # note[3]: duration=q (3%3=0), pitch=from_midi(72) (3%4=3)
        assert result[3].duration == q
        assert result[3].pitch == from_midi(72)
        # note[4]: duration=e (4%3=1), pitch=from_midi(60) (4%4=0)
        assert result[4].duration == e
        assert result[4].pitch == from_midi(60)

    def test_isorhythm_two_cycles(self) -> None:
        q = Duration.from_cn("q")
        talea = (q, q, q)
        color = (60, 64, 67, 72)
        result = isorhythm(talea, color, n=2)
        # LCM(3, 4) = 12, 2 * 12 = 24
        assert len(result) == 24

    def test_isorhythm_same_length(self) -> None:
        q = Duration.from_cn("q")
        talea = (q, q, q)
        color = (60, 64, 67)
        result = isorhythm(talea, color, n=1)
        # LCM(3, 3) = 3
        assert len(result) == 3

    def test_isorhythm_empty_talea(self) -> None:
        with pytest.raises(ValueError):
            isorhythm((), (60, 64), n=1)

    def test_isorhythm_empty_color(self) -> None:
        q = Duration.from_cn("q")
        with pytest.raises(ValueError):
            isorhythm((q,), (), n=1)

    def test_isorhythm_n_zero(self) -> None:
        q = Duration.from_cn("q")
        with pytest.raises(ValueError):
            isorhythm((q,), (60,), n=0)


# ---------------------------------------------------------------------------
# ostinato
# ---------------------------------------------------------------------------


class TestOstinato:
    def test_ostinato_exact_repeat(self, sample_phrase: Phrase) -> None:
        result = ostinato(sample_phrase, repeats=3)
        assert len(result) == 3 * len(sample_phrase)
        # Each repetition matches original
        n = len(sample_phrase)
        for rep in range(3):
            for j in range(n):
                assert result[rep * n + j] == sample_phrase[j]

    def test_ostinato_with_variation(self, sample_phrase: Phrase) -> None:
        # Variation: on repetitions > 0, reverse the phrase
        def var(phrase: Phrase, i: int) -> Phrase:
            if i == 0:
                return phrase
            return tuple(reversed(phrase))

        result = ostinato(sample_phrase, repeats=2, variation=var)
        n = len(sample_phrase)
        assert len(result) == 2 * n
        # First repetition unchanged
        for j in range(n):
            assert result[j] == sample_phrase[j]
        # Second repetition reversed
        for j in range(n):
            assert result[n + j] == sample_phrase[n - 1 - j]

    def test_ostinato_repeats_zero(self, sample_phrase: Phrase) -> None:
        with pytest.raises(ValueError):
            ostinato(sample_phrase, repeats=0)


# ---------------------------------------------------------------------------
# accent_pattern
# ---------------------------------------------------------------------------


class TestAccentPattern:
    def test_accent_pattern_every_2nd(self) -> None:
        q = Duration.from_cn("q")
        phrase: Phrase = tuple(
            Note(pitch=from_midi(60 + i), duration=q) for i in range(4)
        )
        result = accent_pattern(phrase, n=2)
        # Notes at positions 0,1,2,3 -> note_count 1,2,3,4
        # Accent when count % 2 == 0 -> notes 1, 3 (0-indexed)
        assert "accent" not in result[0].articulations
        assert "accent" in result[1].articulations
        assert "accent" not in result[2].articulations
        assert "accent" in result[3].articulations

    def test_accent_pattern_skips_rests(self) -> None:
        q = Duration.from_cn("q")
        # Phrase: Note, Rest, Note, Note, Note
        phrase: Phrase = (
            Note(pitch=from_midi(60), duration=q),
            Rest(duration=q),
            Note(pitch=from_midi(64), duration=q),
            Note(pitch=from_midi(67), duration=q),
            Note(pitch=from_midi(72), duration=q),
        )
        result = accent_pattern(phrase, n=2)
        # note_count: note0=1, rest(skip), note2=2, note3=3, note4=4
        # Accent at count 2 (idx 2) and count 4 (idx 4)
        assert "accent" not in result[0].articulations  # count 1
        assert isinstance(result[1], Rest)               # rest unchanged
        assert "accent" in result[2].articulations        # count 2
        assert "accent" not in result[3].articulations    # count 3
        assert "accent" in result[4].articulations        # count 4

    def test_accent_pattern_n_zero(self) -> None:
        q = Duration.from_cn("q")
        phrase: Phrase = (Note(pitch=from_midi(60), duration=q),)
        with pytest.raises(ValueError):
            accent_pattern(phrase, n=0)

    def test_accent_pattern_preserves_existing_articulations(self) -> None:
        q = Duration.from_cn("q")
        # Note with existing staccato; n=1 means every note gets accent
        phrase: Phrase = (
            Note(pitch=from_midi(60), duration=q, articulations=("staccato",)),
        )
        result = accent_pattern(phrase, n=1)
        assert result[0].articulations == ("staccato", "accent")
