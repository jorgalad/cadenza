"""Shared fixtures for composition tests."""

from __future__ import annotations

import pytest

from cadenza.core.duration import Duration
from cadenza.core.note import Note
from cadenza.core.phrase import Phrase
from cadenza.core.pitch import Pitch
from cadenza.theory.scales import Scale, get_scale
from cadenza.transforms.pitch import from_midi


@pytest.fixture
def quarter() -> Duration:
    return Duration.from_cn("q")


@pytest.fixture
def sample_phrase() -> Phrase:
    """An 8-note Phrase: C4-D4-E4-F4-G4-A4-B4-C5, all quarter duration."""
    q = Duration.from_cn("q")
    return tuple(
        Note(pitch=from_midi(midi), duration=q)
        for midi in (60, 62, 64, 65, 67, 69, 71, 72)
    )


@pytest.fixture
def c_major_scale() -> Scale:
    """C major scale."""
    return get_scale(Pitch(step="c", accidental="n", octave=4), "major")
