"""Deterministic variation generation (ALGO-07).

Produces N distinct but recognizably related phrases by systematic
application of transforms in a locked priority order.
"""

from __future__ import annotations

from collections.abc import Callable

from cadenza.core.interval import Interval
from cadenza.core.phrase import Phrase
from cadenza.transforms.melodic import pitch_retrograde, rotate
from cadenza.transforms.pitch import chromatic_transpose, invert
from cadenza.transforms.rhythm import augment, diminish

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_SEMITONE_TO_INTERVAL: dict[int, tuple[str, int]] = {
    1: ("m", 2),
    2: ("M", 2),
    3: ("m", 3),
    4: ("M", 3),
    5: ("P", 4),
    6: ("A", 4),
    7: ("P", 5),
    8: ("m", 6),
    9: ("M", 6),
    10: ("m", 7),
    11: ("M", 7),
}


def _chromatic_interval(semitones: int) -> Interval:
    """Map a semitone count (1-11) to the simplest ascending interval."""
    quality, number = _SEMITONE_TO_INTERVAL[semitones]
    return Interval(quality=quality, number=number, direction=1)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_variations(phrase: Phrase, n: int) -> list[Phrase]:
    """Generate *n* variations of *phrase* in deterministic priority order.

    The locked priority order is:
      1. Chromatic transpositions up 1..11 semitones (11 variations)
      2. Inversion around first note (1 variation)
      3. Pitch retrograde (1 variation)
      4. Rhythmic augmentation x2 (1 variation)
      5. Rhythmic diminution /2 (1 variation)
      6. Rotations 1..len(phrase)-1 (len(phrase)-1 variations)

    When *n* exceeds the total number of unique transforms, the sequence
    cycles back to the beginning.

    Raises:
        ValueError: If *n* < 1 or *phrase* is empty.
    """
    if n < 1:
        raise ValueError(f"n must be positive, got {n}")
    if not phrase:
        raise ValueError("Cannot generate variations of empty phrase")

    # Build the ordered list of transform functions
    transforms: list[Callable[[Phrase], Phrase]] = []

    # 1. Chromatic transpositions (semitones 1-11)
    for s in range(1, 12):
        iv = _chromatic_interval(s)
        transforms.append(lambda p, iv=iv: chromatic_transpose(p, iv))

    # 2. Inversion
    transforms.append(lambda p: invert(p))

    # 3. Pitch retrograde
    transforms.append(lambda p: pitch_retrograde(p))

    # 4. Augmentation x2
    transforms.append(lambda p: augment(p, 2))

    # 5. Diminution /2
    transforms.append(lambda p: diminish(p, 2))

    # 6. Rotations 1..len(phrase)-1
    for r in range(1, len(phrase)):
        transforms.append(lambda p, r=r: rotate(p, r))

    return [transforms[i % len(transforms)](phrase) for i in range(n)]
