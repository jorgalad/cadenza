"""Counterpoint: rules, validation, and generation for species counterpoint."""

from cadenza.counterpoint.generation import generate_first_species
from cadenza.counterpoint.validation import (
    CounterpointViolation,
    check_counterpoint,
)

__all__ = [
    "CounterpointViolation",
    "check_counterpoint",
    "generate_first_species",
]
