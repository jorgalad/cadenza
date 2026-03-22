"""Algorithmic composition: generative melody algorithms."""

from cadenza.composition.markov import MarkovModel, train_markov, markov_melody
from cadenza.composition.lsystem import lsystem_melody

__all__ = [
    "MarkovModel",
    "train_markov",
    "markov_melody",
    "lsystem_melody",
]
