"""Rhythm pattern generation: Euclidean rhythms, binary rhythms, apply_rhythm."""

from __future__ import annotations

import itertools

from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest
from cadenza.core.phrase import Phrase
from cadenza.transforms.pitch import from_midi


def euclidean_rhythm(n: int, m: int) -> tuple[bool, ...]:
    """Generate a Euclidean rhythm with n hits in m slots using Bjorklund's algorithm.

    Args:
        n: Number of hits (True values). Must be 0 <= n <= m.
        m: Total number of slots. Must be > 0.

    Returns:
        Tuple of booleans with exactly n True values distributed as evenly as possible.

    Raises:
        ValueError: If n < 0, m <= 0, or n > m.
    """
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")
    if m <= 0:
        raise ValueError(f"m must be positive, got {m}")
    if n > m:
        raise ValueError(f"n ({n}) cannot exceed m ({m})")

    if n == 0:
        return (False,) * m
    if n == m:
        return (True,) * m

    # Bjorklund's algorithm
    groups: list[list[bool]] = [[True] for _ in range(n)] + [[False] for _ in range(m - n)]

    while True:
        remainder_count = len(groups) - n
        if remainder_count <= 1:
            break
        new_groups: list[list[bool]] = []
        take = min(n, remainder_count)
        for i in range(take):
            new_groups.append(groups[i] + groups[n + i])
        # Leftover from the shorter side
        leftover_start = take
        leftover_end = n
        if take < n:
            for i in range(take, n):
                new_groups.append(groups[i])
        else:
            leftover_start = n + take
            leftover_end = len(groups)
            for i in range(n + take, len(groups)):
                new_groups.append(groups[i])
        groups = new_groups
        n = take
        if remainder_count <= 1:
            break

    result: list[bool] = []
    for g in groups:
        result.extend(g)
    return tuple(result)


def binary_rhythm(n: int) -> tuple[bool, ...]:
    """Convert a non-negative integer to a rhythm bitmap.

    Each bit of the binary representation becomes a True (1) or False (0) slot.
    n=0 returns (False,) as a single-slot rest pattern.

    Args:
        n: Non-negative integer.

    Returns:
        Tuple of booleans from the binary representation.

    Raises:
        ValueError: If n < 0.
    """
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")
    if n == 0:
        return (False,)
    bits = bin(n)[2:]  # strip '0b' prefix
    return tuple(bit == "1" for bit in bits)


def apply_rhythm(
    pitches: tuple[int, ...],
    rhythm: tuple[bool, ...],
    slot_duration: Duration | None = None,
) -> Phrase:
    """Apply a rhythm bitmap to a sequence of MIDI pitches, producing a Phrase.

    True slots get Notes (cycling through pitches), False slots get Rests.
    Default slot duration is a quarter note.

    Args:
        pitches: MIDI note numbers to cycle through for True slots.
        rhythm: Boolean bitmap indicating hits (True) and rests (False).
        slot_duration: Duration for each slot. Defaults to quarter note.

    Returns:
        A Phrase (tuple of Note/Rest events).
    """
    dur = slot_duration if slot_duration is not None else Duration.from_cn("q")
    pitch_cycle = itertools.cycle(pitches)
    events: list[Note | Rest] = []

    for hit in rhythm:
        if hit:
            midi = next(pitch_cycle)
            events.append(Note(pitch=from_midi(midi), duration=dur))
        else:
            events.append(Rest(duration=dur))

    return tuple(events)
