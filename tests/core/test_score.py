"""Tests for Score frozen dataclass."""

from __future__ import annotations

import pytest

from cadenza.core.pitch import Pitch
from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest
from cadenza.core.phrase import Phrase
from cadenza.core.score import Score


def _make_phrase(*pitches: str) -> Phrase:
    """Helper to create a phrase from pitch step names."""
    return tuple(
        Note(Pitch(p, "n", 4), Duration.from_cn("q"), "mf", ())
        for p in pitches
    )


class TestScoreCreation:
    def test_from_dict(self) -> None:
        soprano = _make_phrase("c", "d", "e")
        bass = _make_phrase("c", "g")
        score = Score.from_dict({"soprano": soprano, "bass": bass})
        assert len(score.voice_names) == 2

    def test_voices_property(self) -> None:
        soprano = _make_phrase("c", "d", "e")
        bass = _make_phrase("c", "g")
        score = Score.from_dict({"soprano": soprano, "bass": bass})
        voices = score.voices
        assert isinstance(voices, dict)
        assert "soprano" in voices
        assert "bass" in voices

    def test_voice_names(self) -> None:
        soprano = _make_phrase("c", "d")
        bass = _make_phrase("c",)
        score = Score.from_dict({"soprano": soprano, "bass": bass})
        assert score.voice_names == ("soprano", "bass")

    def test_getitem(self) -> None:
        soprano = _make_phrase("c", "d")
        score = Score.from_dict({"soprano": soprano})
        assert score["soprano"] == soprano

    def test_getitem_missing_raises(self) -> None:
        score = Score.from_dict({"soprano": _make_phrase("c",)})
        with pytest.raises(KeyError):
            score["nonexistent"]


class TestScoreImmutability:
    def test_frozen(self) -> None:
        score = Score.from_dict({"soprano": _make_phrase("c",)})
        with pytest.raises(AttributeError):
            score._voices = ()  # type: ignore[misc]

    def test_hashable(self) -> None:
        score = Score.from_dict({"soprano": _make_phrase("c",)})
        {score}
        {score: 1}
