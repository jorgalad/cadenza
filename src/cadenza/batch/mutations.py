"""Batch mutation operations: nth-note articulation/dynamic, crescendo/decrescendo, predicate-based articulation.

BATCH-01: set_articulation_nth
BATCH-02: set_dynamic_nth
BATCH-03: crescendo / decrescendo
BATCH-04: add_articulation_if / remove_articulation_if
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace

from cadenza.core.note import Event, Note, Rest
from cadenza.core.phrase import Phrase

# Ordered dynamic levels from softest to loudest.
DYNAMICS: tuple[str, ...] = ("ppp", "pp", "p", "mp", "mf", "f", "ff", "fff")
DYNAMIC_INDEX: dict[str, int] = {d: i for i, d in enumerate(DYNAMICS)}


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _map_nth_notes(
    phrase: Phrase, n: int, fn: Callable[[Note], Note]
) -> Phrase:
    """Apply *fn* to every Nth Note (1-indexed). Rests and non-Nth Notes pass through."""
    result: list[Event] = []
    note_count = 0
    for event in phrase:
        if isinstance(event, Note):
            note_count += 1
            if note_count % n == 0:
                result.append(fn(event))
            else:
                result.append(event)
        else:
            result.append(event)
    return tuple(result)


# ---------------------------------------------------------------------------
# BATCH-01: set_articulation_nth
# ---------------------------------------------------------------------------

def set_articulation_nth(phrase: Phrase, n: int, articulation: str) -> Phrase:
    """Set an articulation on every Nth Note in the phrase.

    Rests are skipped in counting (only Notes count toward N).
    Raises ValueError if n < 1.
    """
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")

    def _add_art(note: Note) -> Note:
        if articulation in note.articulations:
            return note
        return replace(note, articulations=note.articulations + (articulation,))

    return _map_nth_notes(phrase, n, _add_art)


# ---------------------------------------------------------------------------
# BATCH-02: set_dynamic_nth
# ---------------------------------------------------------------------------

def set_dynamic_nth(phrase: Phrase, n: int, dynamic: str) -> Phrase:
    """Set a dynamic on every Nth Note in the phrase.

    Rests are skipped in counting (only Notes count toward N).
    Raises ValueError if n < 1.
    """
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")

    return _map_nth_notes(phrase, n, lambda note: replace(note, dynamic=dynamic))


# ---------------------------------------------------------------------------
# BATCH-03: crescendo / decrescendo
# ---------------------------------------------------------------------------

def crescendo(phrase: Phrase, start: str, end: str) -> Phrase:
    """Apply a crescendo (soft to loud) across all Notes in the phrase.

    Rests pass through unchanged. Only Notes consume dynamic progression positions.
    Single-note phrase gets the end dynamic.
    Raises ValueError if start >= end in dynamic level.
    """
    start_idx = DYNAMIC_INDEX[start]
    end_idx = DYNAMIC_INDEX[end]
    if start_idx >= end_idx:
        raise ValueError(
            f"crescendo requires start < end, got {start!r} (idx={start_idx}) >= {end!r} (idx={end_idx})"
        )
    return _apply_dynamic_gradient(phrase, start_idx, end_idx)


def decrescendo(phrase: Phrase, start: str, end: str) -> Phrase:
    """Apply a decrescendo (loud to soft) across all Notes in the phrase.

    Rests pass through unchanged. Only Notes consume dynamic progression positions.
    Single-note phrase gets the end dynamic.
    Raises ValueError if start <= end in dynamic level.
    """
    start_idx = DYNAMIC_INDEX[start]
    end_idx = DYNAMIC_INDEX[end]
    if start_idx <= end_idx:
        raise ValueError(
            f"decrescendo requires start > end, got {start!r} (idx={start_idx}) <= {end!r} (idx={end_idx})"
        )
    return _apply_dynamic_gradient(phrase, start_idx, end_idx)


def _apply_dynamic_gradient(
    phrase: Phrase, start_idx: int, end_idx: int
) -> Phrase:
    """Internal: distribute dynamics linearly across Notes."""
    # Count notes
    note_indices: list[int] = []
    for i, event in enumerate(phrase):
        if isinstance(event, Note):
            note_indices.append(i)

    n_notes = len(note_indices)
    if n_notes == 0:
        return phrase

    result = list(phrase)
    for pos, idx in enumerate(note_indices):
        if n_notes == 1:
            dyn_idx = end_idx
        else:
            dyn_idx = round(start_idx + (end_idx - start_idx) * pos / (n_notes - 1))
        result[idx] = replace(result[idx], dynamic=DYNAMICS[dyn_idx])  # type: ignore[misc]

    return tuple(result)


# ---------------------------------------------------------------------------
# BATCH-04: add_articulation_if / remove_articulation_if
# ---------------------------------------------------------------------------

def add_articulation_if(
    phrase: Phrase, predicate: Callable[[Event], bool], articulation: str
) -> Phrase:
    """Add an articulation to Notes matching the predicate.

    Rests matching the predicate are passed through unchanged.
    Does not add duplicate articulations.
    """
    result: list[Event] = []
    for event in phrase:
        if predicate(event) and isinstance(event, Note):
            if articulation not in event.articulations:
                result.append(replace(event, articulations=event.articulations + (articulation,)))
            else:
                result.append(event)
        else:
            result.append(event)
    return tuple(result)


def remove_articulation_if(
    phrase: Phrase, predicate: Callable[[Event], bool], articulation: str
) -> Phrase:
    """Remove an articulation from Notes matching the predicate."""
    result: list[Event] = []
    for event in phrase:
        if predicate(event) and isinstance(event, Note):
            new_arts = tuple(a for a in event.articulations if a != articulation)
            result.append(replace(event, articulations=new_arts))
        else:
            result.append(event)
    return tuple(result)
