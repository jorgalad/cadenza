"""Windowed transform application.

BATCH-09: apply_windowed
"""

from __future__ import annotations

from collections.abc import Callable

from cadenza.core.phrase import Phrase


def apply_windowed(
    phrase: Phrase,
    fn: Callable[[Phrase], Phrase],
    window_size: int,
    step: int | None = None,
) -> Phrase:
    """Apply a transform function to sliding windows over a phrase.

    - step defaults to window_size (non-overlapping).
    - Partial tail windows are included (no events dropped).
    - Raises ValueError if window_size < 1 or step < 1.
    """
    if window_size < 1:
        raise ValueError(f"window_size must be >= 1, got {window_size}")
    if step is None:
        step = window_size
    if step < 1:
        raise ValueError(f"step must be >= 1, got {step}")

    result: list = []
    i = 0
    while i < len(phrase):
        window = phrase[i : i + window_size]
        result.extend(fn(window))
        i += step
    return tuple(result)
