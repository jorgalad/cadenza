"""Algorithmic composition: generative melody algorithms."""

from cadenza.composition.lsystem import lsystem_melody
from cadenza.composition.markov import MarkovModel, markov_melody, train_markov
from cadenza.composition.stochastic import (
    probabilistic_melody,
    random_walk,
    tendency_mask_melody,
)
from cadenza.composition.variation import generate_variations

__all__ = [
    "MarkovModel",
    "generate_variations",
    "lsystem_melody",
    "markov_melody",
    "probabilistic_melody",
    "random_walk",
    "tendency_mask_melody",
    "train_markov",
]
