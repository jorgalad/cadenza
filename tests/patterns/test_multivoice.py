"""Tests for multi-voice pattern generation: rhythmic canon and hocket."""

from __future__ import annotations

from fractions import Fraction

import pytest

from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest
from cadenza.core.phrase import Phrase
from cadenza.core.pitch import Pitch
from cadenza.core.score import Score
from cadenza.patterns.multivoice import hocket, rhythmic_canon
from cadenza.transforms.pitch import from_midi


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_phrase(*midis: int, base: str = "q") -> Phrase:
    """Build a phrase from MIDI numbers, all with the same base duration."""
    dur = Duration.from_cn(base)
    return tuple(Note(pitch=from_midi(m), duration=dur) for m in midis)


# ---------------------------------------------------------------------------
# rhythmic_canon tests
# ---------------------------------------------------------------------------


class TestRhythmicCanon:
    def test_canon_three_voices(self) -> None:
        phrase = _make_phrase(60, 62, 64)  # C4, D4, E4 quarter notes
        offset = Duration.from_cn("q")
        result = rhythmic_canon(phrase, n=3, offset=offset)

        assert isinstance(result, Score)
        assert result.voice_names == ("voice_0", "voice_1", "voice_2")

        # voice_0 == original phrase, no leading rest
        assert result["voice_0"] == phrase

        # voice_1: 1 rest (quarter) + 3 notes = 4 events
        v1 = result["voice_1"]
        assert len(v1) == 4
        assert isinstance(v1[0], Rest)
        assert v1[0].duration.fraction == Fraction(1, 4)
        assert v1[1:] == phrase

        # voice_2: 1 rest (half-note fraction) + 3 notes = 4 events
        v2 = result["voice_2"]
        assert len(v2) == 4
        assert isinstance(v2[0], Rest)
        assert v2[0].duration.fraction == Fraction(1, 2)
        assert v2[1:] == phrase

    def test_canon_single_voice(self) -> None:
        phrase = _make_phrase(60, 62, 64)
        offset = Duration.from_cn("q")
        result = rhythmic_canon(phrase, n=1, offset=offset)

        assert result.voice_names == ("voice_0",)
        assert result["voice_0"] == phrase

    def test_canon_empty_phrase(self) -> None:
        offset = Duration.from_cn("q")
        with pytest.raises(ValueError):
            rhythmic_canon((), n=3, offset=offset)

    def test_canon_n_zero(self) -> None:
        phrase = _make_phrase(60)
        offset = Duration.from_cn("q")
        with pytest.raises(ValueError):
            rhythmic_canon(phrase, n=0, offset=offset)

    def test_canon_offset_half(self) -> None:
        phrase = _make_phrase(60, 62)
        offset = Duration.from_cn("h")
        result = rhythmic_canon(phrase, n=2, offset=offset)

        v1 = result["voice_1"]
        assert isinstance(v1[0], Rest)
        assert v1[0].duration.fraction == Fraction(1, 2)


# ---------------------------------------------------------------------------
# hocket tests
# ---------------------------------------------------------------------------


class TestHocket:
    def test_hocket_two_voices(self) -> None:
        phrase = _make_phrase(60, 62, 64, 65)  # C4, D4, E4, F4
        result = hocket(phrase, n=2)
        q = Duration.from_cn("q")

        assert result.voice_names == ("voice_0", "voice_1")

        v0 = result["voice_0"]
        assert len(v0) == 4
        assert isinstance(v0[0], Note) and v0[0].pitch == from_midi(60)
        assert isinstance(v0[1], Rest) and v0[1].duration == q
        assert isinstance(v0[2], Note) and v0[2].pitch == from_midi(64)
        assert isinstance(v0[3], Rest) and v0[3].duration == q

        v1 = result["voice_1"]
        assert len(v1) == 4
        assert isinstance(v1[0], Rest) and v1[0].duration == q
        assert isinstance(v1[1], Note) and v1[1].pitch == from_midi(62)
        assert isinstance(v1[2], Rest) and v1[2].duration == q
        assert isinstance(v1[3], Note) and v1[3].pitch == from_midi(65)

    def test_hocket_three_voices(self) -> None:
        phrase = _make_phrase(60, 62, 64, 65, 67, 69)  # 6 notes
        result = hocket(phrase, n=3)

        assert result.voice_names == ("voice_0", "voice_1", "voice_2")

        # voice_0 gets indices 0, 3
        v0 = result["voice_0"]
        assert len(v0) == 6
        assert isinstance(v0[0], Note) and v0[0].pitch == from_midi(60)
        assert isinstance(v0[1], Rest)
        assert isinstance(v0[2], Rest)
        assert isinstance(v0[3], Note) and v0[3].pitch == from_midi(65)
        assert isinstance(v0[4], Rest)
        assert isinstance(v0[5], Rest)

        # voice_1 gets indices 1, 4
        v1 = result["voice_1"]
        assert isinstance(v1[0], Rest)
        assert isinstance(v1[1], Note) and v1[1].pitch == from_midi(62)
        assert isinstance(v1[2], Rest)
        assert isinstance(v1[3], Rest)
        assert isinstance(v1[4], Note) and v1[4].pitch == from_midi(67)
        assert isinstance(v1[5], Rest)

        # voice_2 gets indices 2, 5
        v2 = result["voice_2"]
        assert isinstance(v2[0], Rest)
        assert isinstance(v2[1], Rest)
        assert isinstance(v2[2], Note) and v2[2].pitch == from_midi(64)
        assert isinstance(v2[3], Rest)
        assert isinstance(v2[4], Rest)
        assert isinstance(v2[5], Note) and v2[5].pitch == from_midi(69)

    def test_hocket_no_simultaneous_notes(self) -> None:
        phrase = _make_phrase(60, 62, 64, 65, 67)
        result = hocket(phrase, n=3)

        # For every position, at most one voice has a Note
        num_events = len(phrase)
        for pos in range(num_events):
            note_count = 0
            for vname in result.voice_names:
                if isinstance(result[vname][pos], Note):
                    note_count += 1
            assert note_count <= 1, f"Position {pos}: {note_count} voices have Notes"

    def test_hocket_equal_total_duration(self) -> None:
        phrase = _make_phrase(60, 62, 64, 65)
        result = hocket(phrase, n=2)

        durations = []
        for vname in result.voice_names:
            total = sum(ev.duration.fraction for ev in result[vname])
            durations.append(total)

        assert all(d == durations[0] for d in durations)

    def test_hocket_empty_phrase(self) -> None:
        with pytest.raises(ValueError):
            hocket((), n=2)

    def test_hocket_n_zero(self) -> None:
        phrase = _make_phrase(60)
        with pytest.raises(ValueError):
            hocket(phrase, n=0)

    def test_hocket_rest_duration_matches(self) -> None:
        """Each rest in hocket has the same duration as the note it replaces."""
        # Use mixed durations to verify rest durations match
        q = Duration.from_cn("q")
        h = Duration.from_cn("h")
        phrase: Phrase = (
            Note(pitch=from_midi(60), duration=q),
            Note(pitch=from_midi(62), duration=h),
            Note(pitch=from_midi(64), duration=q),
            Note(pitch=from_midi(65), duration=h),
        )
        result = hocket(phrase, n=2)

        # voice_0: Note(q), Rest(h), Note(q), Rest(h)
        v0 = result["voice_0"]
        assert isinstance(v0[1], Rest) and v0[1].duration.fraction == h.fraction
        assert isinstance(v0[3], Rest) and v0[3].duration.fraction == h.fraction

        # voice_1: Rest(q), Note(h), Rest(q), Note(h)
        v1 = result["voice_1"]
        assert isinstance(v1[0], Rest) and v1[0].duration.fraction == q.fraction
        assert isinstance(v1[2], Rest) and v1[2].duration.fraction == q.fraction
