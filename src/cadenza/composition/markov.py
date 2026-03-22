"""Markov chain melody generation (ALGO-01, ALGO-02).

MarkovModel frozen dataclass, train_markov for building models from Phrases,
and markov_melody for generating new melodies from trained models.
"""

from __future__ import annotations

import random as _random
from dataclasses import dataclass

from cadenza.core.duration import Duration
from cadenza.core.note import Note
from cadenza.core.phrase import Phrase
from cadenza.transforms.pitch import from_midi


@dataclass(frozen=True, slots=True)
class MarkovModel:
    """Trained Markov chain model for melody generation.

    transition_table maps MIDI n-grams (tuple of ints) to probability
    distributions over successor MIDI numbers (dict[int, float]).
    """

    order: int
    transition_table: dict[tuple[int, ...], dict[int, float]]


def train_markov(phrase: Phrase, order: int = 1) -> MarkovModel:
    """Train a Markov model from a Phrase.

    Args:
        phrase: Source phrase (Notes and Rests). Rests are skipped.
        order: Markov chain order (1 = first-order, 2+ = higher-order).

    Returns:
        A frozen MarkovModel with normalized transition probabilities.

    Raises:
        ValueError: If order < 1 or phrase has insufficient notes.
    """
    if order < 1:
        raise ValueError(f"Order must be >= 1, got {order}")

    # Extract MIDI numbers from Notes only
    midis = [e.pitch.midi_number for e in phrase if isinstance(e, Note)]

    if len(midis) <= order:
        raise ValueError(
            f"Phrase has {len(midis)} notes but order={order} requires "
            f"at least {order + 1} notes"
        )

    # Build count table
    counts: dict[tuple[int, ...], dict[int, int]] = {}
    for i in range(len(midis) - order):
        key = tuple(midis[i : i + order])
        successor = midis[i + order]
        if key not in counts:
            counts[key] = {}
        counts[key][successor] = counts[key].get(successor, 0) + 1

    # Normalize to probabilities
    prob_table: dict[tuple[int, ...], dict[int, float]] = {}
    for key, successors in counts.items():
        total = sum(successors.values())
        prob_table[key] = {m: c / total for m, c in successors.items()}

    return MarkovModel(order=order, transition_table=prob_table)


def markov_melody(
    model: MarkovModel,
    length: int,
    seed: int | None = None,
    duration: Duration | None = None,
) -> Phrase:
    """Generate a melody from a trained Markov model.

    Uses one-step look-ahead to prefer successors that have their own
    transitions, maintaining valid transition chains. On dead-ends,
    restarts from a random state.

    Args:
        model: A trained MarkovModel.
        length: Number of events to generate (must be > 0).
        seed: Random seed for reproducibility.
        duration: Duration for each note (defaults to quarter note).

    Returns:
        A Phrase of the requested length.

    Raises:
        ValueError: If length < 1.
    """
    if length < 1:
        raise ValueError(f"Length must be > 0, got {length}")

    rng = _random.Random(seed)
    dur = duration if duration is not None else Duration.from_cn("q")
    table = model.transition_table
    order = model.order

    states = list(table.keys())
    # Pick random initial state
    state = rng.choice(states)
    result_midis: list[int] = list(state)

    while len(result_midis) < length:
        if state not in table:
            # Dead end: restart from a random state
            state = rng.choice(states)
            result_midis = list(state)
            continue

        successors = table[state]
        remaining = length - len(result_midis)

        if remaining <= 1:
            # Last note needed: any successor is fine
            pitches = list(successors.keys())
            weights = list(successors.values())
        else:
            # Prefer successors whose resulting state also has transitions
            viable: dict[int, float] = {}
            for midi_val, prob in successors.items():
                ns = (state[1:] + (midi_val,)) if order > 1 else (midi_val,)
                if ns in table:
                    viable[midi_val] = prob

            if viable:
                pitches = list(viable.keys())
                weights = list(viable.values())
            else:
                # All successors lead to dead-ends; pick any
                pitches = list(successors.keys())
                weights = list(successors.values())

        next_midi = rng.choices(pitches, weights=weights, k=1)[0]
        result_midis.append(next_midi)
        state = tuple(result_midis[-order:])

    # Truncate to exact length and convert to Notes
    result_midis = result_midis[:length]
    events = tuple(Note(pitch=from_midi(m), duration=dur) for m in result_midis)
    return events
