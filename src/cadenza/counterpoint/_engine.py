"""Shared backtracking search engine for species counterpoint generation."""

from __future__ import annotations

import random
from typing import Callable

from cadenza.core.pitch import Pitch


def _backtrack(
    cf_pitches: list[Pitch],
    candidates_fn: Callable[[int, list[Pitch], Pitch], list[Pitch]],
    validate_fn: Callable[[int, list[Pitch], Pitch, Pitch], bool],
    position: int,
    partial: list[Pitch],
) -> list[Pitch] | None:
    """Recursive depth-first search for valid counterpoint.

    Args:
        cf_pitches: List of cantus firmus pitches.
        candidates_fn: Function(position, partial, cf_pitch) -> candidate pitches.
        validate_fn: Function(position, partial, candidate, cf_pitch) -> bool.
        position: Current position in the counterpoint.
        partial: Partially built list of counterpoint pitches.

    Returns:
        Complete list of counterpoint pitches, or None if no solution found.
    """
    if position == len(cf_pitches):
        return partial

    candidates = candidates_fn(position, partial, cf_pitches[position])

    for candidate in candidates:
        if validate_fn(position, partial, candidate, cf_pitches[position]):
            partial.append(candidate)
            result = _backtrack(
                cf_pitches, candidates_fn, validate_fn,
                position + 1, partial,
            )
            if result is not None:
                return result
            partial.pop()

    return None
