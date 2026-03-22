"""Shared fixtures for pattern tests."""

from __future__ import annotations

import pytest

from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest
from cadenza.core.phrase import Phrase
from cadenza.core.pitch import Pitch
from cadenza.transforms.pitch import from_midi


@pytest.fixture
def quarter() -> Duration:
    return Duration.from_cn("q")


@pytest.fixture
def sample_phrase() -> Phrase:
    """A 4-note Phrase: C4, D4, E4, F4 all quarter duration."""
    q = Duration.from_cn("q")
    return (
        Note(pitch=from_midi(60), duration=q),
        Note(pitch=from_midi(62), duration=q),
        Note(pitch=from_midi(64), duration=q),
        Note(pitch=from_midi(65), duration=q),
    )
