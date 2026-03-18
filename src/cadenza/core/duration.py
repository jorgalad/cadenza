"""Duration: immutable duration type using Fraction arithmetic."""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction

# OMN base duration -> fraction of whole note
BASE_DURATIONS: dict[str, Fraction] = {
    "w": Fraction(1, 1),       # whole
    "h": Fraction(1, 2),       # half
    "q": Fraction(1, 4),       # quarter
    "e": Fraction(1, 8),       # eighth
    "s": Fraction(1, 16),      # sixteenth
    "t": Fraction(1, 32),      # thirty-second
    "x": Fraction(1, 64),      # sixty-fourth
}


@dataclass(frozen=True, order=False)
class Duration:
    """Immutable duration as a fraction of a whole note.

    The fraction field is the canonical value for arithmetic.
    base, dots, and tuplet are metadata for OMN round-trip fidelity.
    """

    fraction: Fraction    # Duration as fraction of whole note
    base: str = "q"       # OMN base symbol
    dots: int = 0         # 0, 1, 2, or 3
    tuplet: int | None = None  # tuplet ratio: 3 = triplet, 5 = quintuplet

    def __post_init__(self) -> None:
        if self.base not in BASE_DURATIONS:
            raise ValueError(f"Invalid base duration: {self.base!r}")
        if not (0 <= self.dots <= 3):
            raise ValueError(f"Dots out of range: {self.dots}")
        if self.fraction <= 0:
            raise ValueError("Duration fraction must be positive")

    @staticmethod
    def from_omn(base: str, dots: int = 0, tuplet: int | None = None) -> Duration:
        """Construct Duration from OMN components, computing the fraction."""
        if base not in BASE_DURATIONS:
            raise ValueError(f"Invalid base duration: {base!r}")

        base_val = BASE_DURATIONS[base]

        # Apply dots: each dot adds half the previous increment
        frac = base_val
        increment = base_val
        for _ in range(dots):
            increment = increment / 2
            frac = frac + increment

        # Apply tuplet ratio
        if tuplet is not None:
            # Standard tuplet: n notes in the time of the next lower power-of-2
            # Triplet (3): 3 in 2 -> multiply by 2/3
            # Quintuplet (5): 5 in 4 -> multiply by 4/5
            normal = 2 ** (math.ceil(math.log2(tuplet)) - 1) if tuplet > 1 else 1
            frac = frac * Fraction(normal, tuplet)

        return Duration(fraction=frac, base=base, dots=dots, tuplet=tuplet)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Duration):
            return NotImplemented
        return self.fraction < other.fraction

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Duration):
            return NotImplemented
        return self.fraction <= other.fraction

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Duration):
            return NotImplemented
        return self.fraction > other.fraction

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Duration):
            return NotImplemented
        return self.fraction >= other.fraction
