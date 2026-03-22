"""Stochastic melody generators (ALGO-04, ALGO-05, ALGO-06).

Stub -- tests should fail.
"""

from __future__ import annotations

from typing import Callable

from cadenza.core.duration import Duration
from cadenza.core.phrase import Phrase
from cadenza.core.pitch import Pitch
from cadenza.theory.scales import Scale


def probabilistic_melody(
    weights: dict[Pitch, float],
    length: int,
    seed: int | None = None,
    duration: Duration | None = None,
) -> Phrase:
    raise NotImplementedError


def tendency_mask_melody(
    mask: Callable[[float], dict[Pitch, float]],
    length: int,
    seed: int | None = None,
    duration: Duration | None = None,
) -> Phrase:
    raise NotImplementedError


def random_walk(
    start: Pitch,
    length: int,
    scale: Scale,
    max_step: int = 2,
    seed: int | None = None,
    duration: Duration | None = None,
) -> Phrase:
    raise NotImplementedError
