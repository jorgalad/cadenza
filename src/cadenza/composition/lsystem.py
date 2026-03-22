"""L-system melody generation (ALGO-03).

Deterministic string-rewriting L-system with alphabet-to-note translation.
"""

from __future__ import annotations

from cadenza.core.note import Event
from cadenza.core.phrase import Phrase


def lsystem_melody(
    axiom: str,
    rules: dict[str, str],
    alphabet: dict[str, Event],
    generations: int,
) -> Phrase:
    """Generate a melody by expanding an L-system and translating via alphabet.

    Args:
        axiom: Starting string.
        rules: Rewriting rules mapping single characters to replacement strings.
        alphabet: Mapping from characters to Note/Rest events.
        generations: Number of rewriting generations (must be >= 0).

    Returns:
        A Phrase of events corresponding to alphabet-mapped characters.

    Raises:
        ValueError: If generations < 0.
    """
    if generations < 0:
        raise ValueError(f"Generations must be >= 0, got {generations}")

    # String rewriting
    current = axiom
    for _ in range(generations):
        current = "".join(rules.get(ch, ch) for ch in current)

    # Translate to events (skip characters not in alphabet)
    events = tuple(alphabet[ch] for ch in current if ch in alphabet)
    return events
