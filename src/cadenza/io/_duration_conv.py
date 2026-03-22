"""Duration conversion utilities for MusicXML divisions and MIDI ticks."""

from __future__ import annotations

import math
from collections.abc import Iterable
from fractions import Fraction

from cadenza.core.duration import BASE_DURATIONS, Duration
from cadenza.core.note import Event

# Allowed prime factors for MusicXML divisions. Standard musical durations
# only require factors of 2 (binary subdivisions) and 3 (triplets).
# Quintuplets need 5. Any other prime factor indicates a non-standard duration.
_ALLOWED_DIVISION_PRIMES = {2, 3, 5}


def _validate_divisions_primes(divisions: int) -> None:
    """Raise ValueError if divisions has prime factors beyond 2, 3, 5."""
    n = divisions
    for p in _ALLOWED_DIVISION_PRIMES:
        while n % p == 0:
            n //= p
    if n > 1:
        raise ValueError(
            f"Duration requires divisions with prime factor {n}, "
            "which is not representable in standard MusicXML notation."
        )


def fraction_to_mxml_duration(frac: Fraction, divisions: int) -> int:
    """Convert Duration.fraction (fraction of whole note) to MusicXML integer duration.

    MusicXML duration = fraction_of_whole * 4 * divisions.
    Raises ValueError if the result is not an integer.
    """
    result = frac * 4 * divisions
    if result.denominator != 1:
        raise ValueError(
            f"Duration {frac} not representable with divisions={divisions}"
        )
    return int(result)


def mxml_duration_to_fraction(mxml_dur: int, divisions: int) -> Fraction:
    """Convert MusicXML integer duration to Duration.fraction (fraction of whole note).

    fraction = mxml_dur / (divisions * 4)
    """
    return Fraction(mxml_dur, divisions * 4)


def fraction_to_best_duration(frac: Fraction) -> Duration:
    """Find the best CN base+dots match for a fraction.

    Walks BASE_DURATIONS checking exact match, then dotted (1.5x), then
    double-dotted (1.75x). If no clean match, creates Duration with the
    fraction and closest base.
    """
    # Try exact match
    for base, base_frac in BASE_DURATIONS.items():
        if frac == base_frac:
            return Duration(fraction=frac, base=base, dots=0)

    # Try dotted (1.5x base)
    for base, base_frac in BASE_DURATIONS.items():
        dotted = base_frac * Fraction(3, 2)
        if frac == dotted:
            return Duration(fraction=frac, base=base, dots=1)

    # Try double-dotted (1.75x base)
    for base, base_frac in BASE_DURATIONS.items():
        double_dotted = base_frac * Fraction(7, 4)
        if frac == double_dotted:
            return Duration(fraction=frac, base=base, dots=2)

    # No clean match: find closest base
    closest_base = "q"
    closest_diff = abs(frac - Fraction(1, 4))
    for base, base_frac in BASE_DURATIONS.items():
        diff = abs(frac - base_frac)
        if diff < closest_diff:
            closest_diff = diff
            closest_base = base
    return Duration(fraction=frac, base=closest_base, dots=0)


def compute_divisions(events: Iterable[Event]) -> int:
    """Compute the MusicXML divisions value that cleanly represents all event durations.

    Scans all event durations, collects fraction denominators, computes LCM,
    and returns a divisions value such that all durations are representable as
    integer MusicXML duration values.

    The formula: divisions = lcm_of_all_denominators (after multiplying fraction by 4).
    Minimum return value is 1.
    """
    denoms: set[int] = set()
    for event in events:
        # fraction * 4 must be integer for given divisions
        # fraction * 4 * divisions must be integer
        # So we need divisions such that (fraction * 4).denominator divides divisions
        quarter_frac = event.duration.fraction * 4
        denoms.add(quarter_frac.denominator)

    if not denoms:
        return 1

    result = 1
    for d in denoms:
        result = math.lcm(result, d)

    # Validate prime factors
    _validate_divisions_primes(result)
    return max(result, 1)
