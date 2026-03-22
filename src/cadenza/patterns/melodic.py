"""Melodic pattern generation: isorhythm, ostinato, accent_pattern."""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import replace

from cadenza.core.duration import Duration
from cadenza.core.note import Event, Note, Rest
from cadenza.core.phrase import Phrase
from cadenza.transforms.pitch import from_midi


def isorhythm(
    talea: tuple[Duration, ...],
    color: tuple[int, ...],
    n: int = 1,
) -> Phrase:
    """Generate an isorhythmic phrase by independently cycling talea and color.

    The talea (rhythm pattern) and color (pitch sequence) cycle independently.
    One full cycle is LCM(len(talea), len(color)) notes. The n parameter
    controls how many full cycles to produce.

    Args:
        talea: Duration pattern to cycle.
        color: MIDI pitch numbers to cycle.
        n: Number of complete LCM cycles. Must be >= 1.

    Returns:
        A Phrase with n * LCM(len(talea), len(color)) notes.

    Raises:
        ValueError: If talea or color is empty, or n < 1.
    """
    if not talea:
        raise ValueError("talea must be non-empty")
    if not color:
        raise ValueError("color must be non-empty")
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")

    cycle_len = math.lcm(len(talea), len(color))
    total = n * cycle_len

    events: list[Note] = []
    for i in range(total):
        dur = talea[i % len(talea)]
        midi = color[i % len(color)]
        events.append(Note(pitch=from_midi(midi), duration=dur))

    return tuple(events)


def ostinato(
    phrase: Phrase,
    repeats: int,
    variation: Callable[[Phrase, int], Phrase] | None = None,
) -> Phrase:
    """Repeat a phrase multiple times, optionally applying a variation function.

    Args:
        phrase: The source phrase to repeat.
        repeats: Number of repetitions. Must be >= 1.
        variation: Optional callback(phrase, repetition_index) -> modified phrase.
            Called for each repetition (including the first, with index 0).

    Returns:
        Concatenated phrase of all repetitions.

    Raises:
        ValueError: If repeats < 1.
    """
    if repeats < 1:
        raise ValueError(f"repeats must be >= 1, got {repeats}")

    all_events: list[Event] = []
    for i in range(repeats):
        if variation is None:
            all_events.extend(phrase)
        else:
            all_events.extend(variation(phrase, i))

    return tuple(all_events)


def accent_pattern(phrase: Phrase, n: int) -> Phrase:
    """Add 'accent' articulation to every Nth Note in the phrase.

    Rests are passed through unchanged and do not affect the note count.
    Counting is 1-based: the first Note has count 1, accent is applied
    when count % n == 0.

    Args:
        phrase: Input phrase.
        n: Accent every Nth note. Must be >= 1.

    Returns:
        New phrase with accents applied.

    Raises:
        ValueError: If n < 1.
    """
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")

    events: list[Event] = []
    note_count = 0

    for event in phrase:
        if isinstance(event, Note):
            note_count += 1
            if note_count % n == 0:
                events.append(
                    replace(event, articulations=event.articulations + ("accent",))
                )
            else:
                events.append(event)
        else:
            events.append(event)

    return tuple(events)
