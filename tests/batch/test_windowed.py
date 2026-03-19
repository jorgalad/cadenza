"""Tests for cadenza.batch.windowed — BATCH-09."""

from __future__ import annotations

import pytest

from cadenza.core.duration import Duration
from cadenza.core.note import Note
from cadenza.core.pitch import Pitch
from cadenza.core.phrase import Phrase
from cadenza.batch.windowed import apply_windowed


def _make_note(step: str = "c") -> Note:
    return Note(
        pitch=Pitch(step, "n", 4),
        duration=Duration.from_cn("q"),
    )


def _identity(phrase: Phrase) -> Phrase:
    return phrase


def _double(phrase: Phrase) -> Phrase:
    """Double each event in the window."""
    return phrase + phrase


# ---------------------------------------------------------------------------
# BATCH-09: apply_windowed
# ---------------------------------------------------------------------------

class TestApplyWindowed:
    def test_non_overlapping_with_partial_tail(self):
        """Truth: 7 events, window=3 -> windows [0:3], [3:6], [6:7]."""
        phrase = tuple(_make_note() for _ in range(7))
        windows_seen: list[int] = []

        def track_fn(p: Phrase) -> Phrase:
            windows_seen.append(len(p))
            return p

        result = apply_windowed(phrase, track_fn, window_size=3)
        assert windows_seen == [3, 3, 1]
        assert len(result) == 7

    def test_overlapping_step_1(self):
        phrase = tuple(_make_note() for _ in range(5))
        windows_seen: list[int] = []

        def track_fn(p: Phrase) -> Phrase:
            windows_seen.append(len(p))
            return p

        result = apply_windowed(phrase, track_fn, window_size=3, step=1)
        # Windows: [0:3], [1:4], [2:5]
        assert len(windows_seen) == 3
        # With overlapping, result length = sum of window sizes
        assert len(result) == 9  # 3 + 3 + 3

    def test_window_size_lt_1_raises(self):
        phrase = (_make_note(),)
        with pytest.raises(ValueError):
            apply_windowed(phrase, _identity, window_size=0)

    def test_step_lt_1_raises(self):
        phrase = (_make_note(),)
        with pytest.raises(ValueError):
            apply_windowed(phrase, _identity, window_size=1, step=0)

    def test_identity_preserves_all(self):
        phrase = tuple(_make_note() for _ in range(10))
        result = apply_windowed(phrase, _identity, window_size=4)
        assert len(result) == 10
        assert result == phrase

    def test_transform_applied_to_each_window(self):
        phrase = tuple(_make_note() for _ in range(4))
        result = apply_windowed(phrase, _double, window_size=2)
        # Two windows of 2, each doubled -> 4 + 4 = 8
        assert len(result) == 8
