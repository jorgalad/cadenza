"""Hypothesis custom strategies for cadenza property-based tests."""

from __future__ import annotations

from hypothesis import assume, strategies as st
from hypothesis.strategies import composite

from cadenza.core.pitch import Pitch
from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest, Event


STEPS = ["c", "d", "e", "f", "g", "a", "b"]
ACCIDENTALS = ["n", "s", "b", "ss", "bb"]
DYNAMICS = ["ppp", "pp", "p", "mp", "mf", "f", "ff", "fff", None]
# Known articulations that round-trip cleanly through OMN
KNOWN_ARTICULATIONS: tuple[str, ...] = (
    "stacc", "ten", "acc", "leg", "marc", "fermata", "trill", "pizz", "arco",
)
ARTICULATIONS = list(KNOWN_ARTICULATIONS)
BASES = ["w", "h", "q", "e", "s", "t"]


@composite
def pitch_strategy(draw: st.DrawFn) -> Pitch:
    """Generate a valid Pitch with MIDI number 0-127."""
    step = draw(st.sampled_from(STEPS))
    acc = draw(st.sampled_from(ACCIDENTALS))
    octave = draw(st.integers(min_value=0, max_value=9))
    p = Pitch(step=step, accidental=acc, octave=octave)
    # Filter out pitches with invalid MIDI numbers
    assume(0 <= p.midi_number <= 127)
    return p


@composite
def duration_strategy(draw: st.DrawFn) -> Duration:
    """Generate a valid Duration with optional dots and tuplet."""
    base = draw(st.sampled_from(BASES))
    dots = draw(st.integers(min_value=0, max_value=2))
    use_tuplet = draw(st.booleans())
    tuplet = draw(st.integers(min_value=3, max_value=7)) if use_tuplet else None
    return Duration.from_omn(base, dots=dots, tuplet=tuplet)


@composite
def note_strategy(draw: st.DrawFn) -> Note:
    """Generate a valid Note with pitch, duration, optional dynamic and articulations."""
    pitch = draw(pitch_strategy())
    duration = draw(duration_strategy())
    dynamic = draw(st.sampled_from(DYNAMICS))
    # Draw 0-3 unique articulations
    num_artics = draw(st.integers(min_value=0, max_value=3))
    if num_artics > 0:
        artics = draw(
            st.lists(
                st.sampled_from(ARTICULATIONS),
                min_size=num_artics,
                max_size=num_artics,
                unique=True,
            )
        )
        articulations = tuple(artics)
    else:
        articulations = ()
    return Note(pitch=pitch, duration=duration, dynamic=dynamic, articulations=articulations)


@composite
def rest_strategy(draw: st.DrawFn) -> Rest:
    """Generate a valid Rest with a duration."""
    duration = draw(duration_strategy())
    return Rest(duration=duration)


@composite
def event_strategy(draw: st.DrawFn) -> Event:
    """Generate either a Note or a Rest."""
    is_note = draw(st.booleans())
    if is_note:
        return draw(note_strategy())
    else:
        return draw(rest_strategy())


@composite
def phrase_strategy(draw: st.DrawFn) -> tuple[Event, ...]:
    """Generate a tuple of 1-20 events (Notes and Rests)."""
    size = draw(st.integers(min_value=1, max_value=20))
    events = [draw(event_strategy()) for _ in range(size)]
    return tuple(events)


@composite
def phrase_with_rests_strategy(draw: st.DrawFn) -> tuple[Event, ...]:
    """Generate a phrase guaranteed to contain at least one Rest."""
    size = draw(st.integers(min_value=2, max_value=20))
    # Place at least one rest at a random position
    rest_pos = draw(st.integers(min_value=0, max_value=size - 1))
    events: list[Event] = []
    for i in range(size):
        if i == rest_pos:
            events.append(draw(rest_strategy()))
        else:
            events.append(draw(event_strategy()))
    return tuple(events)
