"""Shared fixtures for transform tests."""

from __future__ import annotations

import pytest

from cadenza.core.pitch import Pitch
from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest
from cadenza.core.phrase import Phrase


@pytest.fixture
def c_major_scale_phrase() -> Phrase:
    """7-note C major scale phrase: C4,D4,E4,F4,G4,A4,B4, all quarter notes."""
    q = Duration.from_omn("q")
    return (
        Note(pitch=Pitch(step="c", accidental="n", octave=4), duration=q),
        Note(pitch=Pitch(step="d", accidental="n", octave=4), duration=q),
        Note(pitch=Pitch(step="e", accidental="n", octave=4), duration=q),
        Note(pitch=Pitch(step="f", accidental="n", octave=4), duration=q),
        Note(pitch=Pitch(step="g", accidental="n", octave=4), duration=q),
        Note(pitch=Pitch(step="a", accidental="n", octave=4), duration=q),
        Note(pitch=Pitch(step="b", accidental="n", octave=4), duration=q),
    )


@pytest.fixture
def simple_phrase() -> Phrase:
    """3-note phrase: C4(q, pp), E4(e), G4(h)."""
    return (
        Note(
            pitch=Pitch(step="c", accidental="n", octave=4),
            duration=Duration.from_omn("q"),
            dynamic="pp",
        ),
        Note(
            pitch=Pitch(step="e", accidental="n", octave=4),
            duration=Duration.from_omn("e"),
        ),
        Note(
            pitch=Pitch(step="g", accidental="n", octave=4),
            duration=Duration.from_omn("h"),
        ),
    )


@pytest.fixture
def phrase_with_rests() -> Phrase:
    """Phrase with interleaved rests: C4(q), Rest(e), E4(q), Rest(e)."""
    return (
        Note(
            pitch=Pitch(step="c", accidental="n", octave=4),
            duration=Duration.from_omn("q"),
        ),
        Rest(duration=Duration.from_omn("e")),
        Note(
            pitch=Pitch(step="e", accidental="n", octave=4),
            duration=Duration.from_omn("q"),
        ),
        Rest(duration=Duration.from_omn("e")),
    )
