"""Batch rhythm operations: quantize_lengths.

BATCH-05: quantize_lengths
"""

from __future__ import annotations

from collections.abc import Sequence
from fractions import Fraction

from cadenza.core.duration import Duration
from cadenza.core.phrase import Phrase
from cadenza.transforms.rhythm import quantize


def quantize_lengths(
    phrase: Phrase, grid: Sequence[Duration | str]
) -> Phrase:
    """Snap each event's duration to the nearest grid value.

    Thin wrapper around cadenza.transforms.rhythm.quantize for API
    consistency in the batch package.

    Grid values may be Duration objects or CN base strings (e.g. "q").
    """
    return quantize(phrase, grid)
