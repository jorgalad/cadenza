"""Shared fixtures for counterpoint tests."""

from __future__ import annotations

import pytest

from cadenza.core.duration import Duration
from cadenza.core.note import Note
from cadenza.core.phrase import Phrase
from cadenza.core.pitch import Pitch


def make_phrase(
    pitches: list[tuple[str, str, int]],
    base: str = "w",
) -> Phrase:
    """Build a Phrase from a list of (step, accidental, octave) tuples."""
    dur = Duration.from_cn(base)
    return tuple(
        Note(
            pitch=Pitch(step=s, accidental=a, octave=o),
            duration=dur,
            dynamic=None,
            articulations=(),
        )
        for s, a, o in pitches
    )


@pytest.fixture
def cf_c_major() -> Phrase:
    """Standard 8-note cantus firmus in C major using whole notes."""
    return make_phrase([
        ("c", "n", 4),
        ("d", "n", 4),
        ("f", "n", 4),
        ("e", "n", 4),
        ("a", "n", 4),
        ("g", "n", 4),
        ("f", "n", 4),
        ("e", "n", 4),
    ])
