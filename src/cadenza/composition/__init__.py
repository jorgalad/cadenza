"""Algorithmic composition: generative melody algorithms."""

from cadenza.composition.lsystem import lsystem_melody
from cadenza.composition.markov import MarkovModel, markov_melody, train_markov
from cadenza.composition.stochastic import (
    probabilistic_melody,
    random_walk,
    tendency_mask_melody,
)

__all__ = [
    "MarkovModel",
    "lsystem_melody",
    "markov_melody",
    "probabilistic_melody",
    "random_walk",
    "tendency_mask_melody",
    "train_markov",
]
