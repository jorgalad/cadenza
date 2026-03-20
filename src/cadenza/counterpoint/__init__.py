"""Counterpoint: rules, validation, and generation for species counterpoint."""

from cadenza.counterpoint.generation import (
    generate_fifth_species,
    generate_first_species,
    generate_fourth_species,
    generate_free_counterpoint,
    generate_multi_voice_counterpoint,
    generate_second_species,
    generate_third_species,
)
from cadenza.counterpoint.validation import (
    CounterpointViolation,
    check_counterpoint,
)

__all__ = [
    "CounterpointViolation",
    "check_counterpoint",
    "generate_fifth_species",
    "generate_first_species",
    "generate_fourth_species",
    "generate_free_counterpoint",
    "generate_multi_voice_counterpoint",
    "generate_second_species",
    "generate_third_species",
]
