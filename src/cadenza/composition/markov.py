"""Markov chain melody generation (ALGO-01, ALGO-02).

Stub -- tests should fail.
"""

from __future__ import annotations

from dataclasses import dataclass

from cadenza.core.duration import Duration
from cadenza.core.phrase import Phrase


@dataclass(frozen=True, slots=True)
class MarkovModel:
    order: int
    transition_table: dict  # type: ignore[type-arg]


def train_markov(phrase: Phrase, order: int = 1) -> MarkovModel:
    raise NotImplementedError


def markov_melody(
    model: MarkovModel,
    length: int,
    seed: int | None = None,
    duration: Duration | None = None,
) -> Phrase:
    raise NotImplementedError
