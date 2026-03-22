"""Stochastic melody generators (ALGO-04, ALGO-05, ALGO-06).

probabilistic_melody: weighted random pitch selection.
tendency_mask_melody: time-varying pitch distributions.
random_walk: scale-constrained stepwise motion.
"""

from __future__ import annotations

import random as _random
from typing import Callable

from cadenza.core.duration import Duration
from cadenza.core.note import Note
from cadenza.core.phrase import Phrase
from cadenza.core.pitch import Pitch
from cadenza.theory.scales import Scale
from cadenza.transforms.pitch import from_midi, nearest_in_scale


def probabilistic_melody(
    weights: dict[Pitch, float],
    length: int,
    seed: int | None = None,
    duration: Duration | None = None,
) -> Phrase:
    """Generate a melody by randomly selecting pitches from weighted set.

    Args:
        weights: Mapping of Pitch to selection probability weight.
        length: Number of notes to generate (must be > 0).
        seed: Random seed for reproducibility.
        duration: Duration for each note (defaults to quarter note).

    Returns:
        A Phrase of Notes with randomly selected pitches.

    Raises:
        ValueError: If length < 1 or weights is empty.
    """
    if length < 1:
        raise ValueError(f"Length must be > 0, got {length}")
    if not weights:
        raise ValueError("Weights must not be empty")

    rng = _random.Random(seed)
    dur = duration if duration is not None else Duration.from_cn("q")

    pitches = list(weights.keys())
    wts = list(weights.values())

    events: list[Note] = []
    for _ in range(length):
        chosen = rng.choices(pitches, weights=wts, k=1)[0]
        events.append(Note(pitch=chosen, duration=dur))

    return tuple(events)


def tendency_mask_melody(
    mask: Callable[[float], dict[Pitch, float]],
    length: int,
    seed: int | None = None,
    duration: Duration | None = None,
) -> Phrase:
    """Generate a melody with time-varying pitch distributions.

    Args:
        mask: Function mapping normalized position [0.0, 1.0] to pitch weights.
        length: Number of notes to generate (must be > 0).
        seed: Random seed for reproducibility.
        duration: Duration for each note (defaults to quarter note).

    Returns:
        A Phrase of Notes with position-dependent pitch selection.

    Raises:
        ValueError: If length < 1.
    """
    if length < 1:
        raise ValueError(f"Length must be > 0, got {length}")

    rng = _random.Random(seed)
    dur = duration if duration is not None else Duration.from_cn("q")

    events: list[Note] = []
    for i in range(length):
        t = i / max(length - 1, 1)
        pitch_weights = mask(t)
        pitches = list(pitch_weights.keys())
        wts = list(pitch_weights.values())
        chosen = rng.choices(pitches, weights=wts, k=1)[0]
        events.append(Note(pitch=chosen, duration=dur))

    return tuple(events)


def random_walk(
    start: Pitch,
    length: int,
    scale: Scale,
    max_step: int = 2,
    seed: int | None = None,
    duration: Duration | None = None,
) -> Phrase:
    """Generate a scale-constrained random walk melody.

    Args:
        start: Starting pitch (snapped to scale if not already in it).
        length: Number of notes to generate (must be > 0).
        scale: Scale to constrain pitches to.
        max_step: Maximum step size in semitones (must be >= 1).
        seed: Random seed for reproducibility.
        duration: Duration for each note (defaults to quarter note).

    Returns:
        A Phrase of Notes following a random walk within the scale.

    Raises:
        ValueError: If length < 1 or max_step < 1.
    """
    if length < 1:
        raise ValueError(f"Length must be > 0, got {length}")
    if max_step < 1:
        raise ValueError(f"max_step must be >= 1, got {max_step}")

    rng = _random.Random(seed)
    dur = duration if duration is not None else Duration.from_cn("q")

    # Snap start to scale
    current = nearest_in_scale(start, scale)
    events: list[Note] = [Note(pitch=current, duration=dur)]

    for _ in range(length - 1):
        # Generate candidates: step by -max_step to +max_step semitones (skip 0)
        candidates: list[Pitch] = []
        seen: set[int] = set()
        for delta in range(-max_step, max_step + 1):
            if delta == 0:
                continue
            candidate_midi = current.midi_number + delta
            if candidate_midi < 0 or candidate_midi > 127:
                continue
            raw = from_midi(candidate_midi)
            snapped = nearest_in_scale(raw, scale)
            # Only include if within max_step of current
            if abs(snapped.midi_number - current.midi_number) <= max_step:
                midi_key = snapped.midi_number
                if midi_key not in seen:
                    seen.add(midi_key)
                    candidates.append(snapped)

        if candidates:
            current = rng.choice(candidates)
        # else: stay on current (shouldn't happen with reasonable scales)

        events.append(Note(pitch=current, duration=dur))

    return tuple(events)
