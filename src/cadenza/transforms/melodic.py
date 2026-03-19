"""Melodic transforms: MELO-01 through MELO-12.

Higher-level musical operations that compose pitch and rhythm operations.
All functions are pure -- they accept a Phrase and return a new Phrase.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import replace
from fractions import Fraction

from cadenza.core.duration import Duration
from cadenza.core.interval import Interval
from cadenza.core.note import Event, Note, Rest
from cadenza.core.phrase import Phrase
from cadenza.core.pitch import Pitch
from cadenza.transforms.pitch import (
    _map_pitches,
    _transpose_pitch,
    from_midi,
    invert as _invert,
)


# ---------------------------------------------------------------------------
# MELO-01: pitch_retrograde
# ---------------------------------------------------------------------------

def pitch_retrograde(phrase: Phrase) -> Phrase:
    """Reverse pitch sequence while keeping original durations and positions.

    Rests stay in place; only Note pitches are reversed among note positions.
    """
    if not phrase:
        return ()

    note_indices = [i for i, e in enumerate(phrase) if isinstance(e, Note)]
    pitches = [phrase[i].pitch for i in note_indices]  # type: ignore[union-attr]
    pitches.reverse()

    events = list(phrase)
    for idx, pitch in zip(note_indices, pitches):
        events[idx] = replace(events[idx], pitch=pitch)  # type: ignore[misc]
    return tuple(events)


# ---------------------------------------------------------------------------
# MELO-02: retrograde_inversion
# ---------------------------------------------------------------------------

def retrograde_inversion(phrase: Phrase, axis: Pitch | None = None) -> Phrase:
    """Apply pitch retrograde then invert around axis.

    Default axis = first note of the retrograded phrase.
    """
    if not phrase:
        return ()
    return _invert(pitch_retrograde(phrase), axis=axis)


# ---------------------------------------------------------------------------
# full_retrograde
# ---------------------------------------------------------------------------

def full_retrograde(phrase: Phrase) -> Phrase:
    """Reverse entire event sequence (classical retrograde)."""
    return phrase[::-1]


# ---------------------------------------------------------------------------
# MELO-03: rotate
# ---------------------------------------------------------------------------

def rotate(phrase: Phrase, n: int) -> Phrase:
    """Cyclic rotation of events. Positive n = rotate left."""
    if not phrase:
        return ()
    n = n % len(phrase)
    return phrase[n:] + phrase[:n]


# ---------------------------------------------------------------------------
# MELO-04: permute
# ---------------------------------------------------------------------------

def permute(phrase: Phrase, indices: Sequence[int]) -> Phrase:
    """Reorder events by index list.

    Raises ValueError if len(indices) != len(phrase).
    Raises IndexError if any index is out of range.
    """
    if len(indices) != len(phrase):
        raise ValueError(
            f"indices length ({len(indices)}) != phrase length ({len(phrase)})"
        )
    return tuple(phrase[i] for i in indices)


# ---------------------------------------------------------------------------
# MELO-05: interpolate
# ---------------------------------------------------------------------------

def interpolate(phrase: Phrase, steps: int = 1) -> Phrase:
    """Insert chromatic passing notes between consecutive notes.

    For each consecutive pair of Notes, inserts *steps* passing notes
    with pitches computed by even semitone division. The original note's
    duration is subdivided evenly among the note + passing notes.

    No interpolation occurs at Rest boundaries.
    """
    if not phrase or len(phrase) < 2:
        return phrase if not phrase else tuple(phrase)

    result: list[Event] = []

    for i in range(len(phrase) - 1):
        current = phrase[i]
        nxt = phrase[i + 1]

        # Only interpolate between two Notes
        if isinstance(current, Note) and isinstance(nxt, Note):
            midi_start = current.pitch.midi_number
            midi_end = nxt.pitch.midi_number
            midi_diff = midi_end - midi_start

            if midi_diff == 0 or steps == 0:
                result.append(current)
                continue

            # Subdivide duration
            subdivisions = steps + 1
            new_fraction = current.duration.fraction / subdivisions
            short_dur = Duration(
                fraction=new_fraction,
                base=current.duration.base,
                dots=current.duration.dots,
                tuplet=current.duration.tuplet,
            )

            # Add original note with subdivided duration
            result.append(replace(current, duration=short_dur))

            # Add passing notes
            ascending = midi_diff > 0
            for s in range(1, steps + 1):
                # Evenly spaced MIDI values
                passing_midi = midi_start + round(midi_diff * s / subdivisions)
                passing_pitch = from_midi(passing_midi, prefer_sharps=ascending)
                result.append(Note(pitch=passing_pitch, duration=short_dur))
        else:
            result.append(current)

    # Always append the last event unchanged
    result.append(phrase[-1])
    return tuple(result)


# ---------------------------------------------------------------------------
# MELO-06: omit
# ---------------------------------------------------------------------------

def omit(
    phrase: Phrase,
    n: int | None = None,
    predicate: Callable[[Event], bool] | None = None,
) -> Phrase:
    """Remove events from a phrase by position or predicate.

    If *n* provided: remove every nth event (1-indexed).
    If *predicate* provided: remove events where predicate returns True.
    Exactly one of n or predicate must be provided.
    """
    if (n is not None) == (predicate is not None):
        raise ValueError("Exactly one of 'n' or 'predicate' must be provided")

    if n is not None:
        return tuple(e for i, e in enumerate(phrase) if (i + 1) % n != 0)
    else:
        assert predicate is not None
        return tuple(e for e in phrase if not predicate(e))


# ---------------------------------------------------------------------------
# MELO-07: repeat
# ---------------------------------------------------------------------------

def repeat(
    phrase: Phrase,
    n: int,
    variation: Callable[[int, Phrase], Phrase] | None = None,
) -> Phrase:
    """Repeat phrase n times, with optional variation callback.

    The variation callback receives (repetition_index, phrase) and returns
    a modified phrase for that repetition.
    """
    repetitions: list[Phrase] = []
    for i in range(n):
        if variation is not None:
            repetitions.append(variation(i, phrase))
        else:
            repetitions.append(phrase)
    return tuple(event for rep in repetitions for event in rep)


# ---------------------------------------------------------------------------
# MELO-08: mirror
# ---------------------------------------------------------------------------

def mirror(phrase: Phrase) -> Phrase:
    """Palindrome: phrase + full_retrograde(phrase)."""
    if not phrase:
        return ()
    return phrase + full_retrograde(phrase)


# ---------------------------------------------------------------------------
# MELO-09: fragment
# ---------------------------------------------------------------------------

def fragment(phrase: Phrase, lengths: Sequence[int]) -> tuple[Phrase, ...]:
    """Split phrase into sub-phrases of given lengths.

    If sum(lengths) < len(phrase), remaining events are dropped.
    """
    fragments: list[Phrase] = []
    offset = 0
    for length in lengths:
        fragments.append(phrase[offset : offset + length])
        offset += length
    return tuple(fragments)


# ---------------------------------------------------------------------------
# MELO-10: concatenate
# ---------------------------------------------------------------------------

def concatenate(*phrases: Phrase) -> Phrase:
    """Join multiple phrases into one."""
    return tuple(event for phrase in phrases for event in phrase)


# ---------------------------------------------------------------------------
# MELO-11: interleave
# ---------------------------------------------------------------------------

def interleave(phrase1: Phrase, phrase2: Phrase) -> Phrase:
    """Alternate events from two phrases.

    If phrases have unequal length, the remaining events from the longer
    phrase are appended after the shorter one is exhausted.
    """
    result: list[Event] = []
    for i in range(max(len(phrase1), len(phrase2))):
        if i < len(phrase1):
            result.append(phrase1[i])
        if i < len(phrase2):
            result.append(phrase2[i])
    return tuple(result)


# ---------------------------------------------------------------------------
# MELO-12: pitch_map
# ---------------------------------------------------------------------------

def pitch_map(phrase: Phrase, fn: Callable[[Pitch], Pitch]) -> Phrase:
    """Apply a callable to every note's pitch. Rests pass through."""
    if not phrase:
        return ()
    return _map_pitches(phrase, fn)
