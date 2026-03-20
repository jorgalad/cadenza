"""Counterpoint: rules, validation, and generation for species counterpoint."""

from cadenza.counterpoint.validation import (
    CounterpointViolation,
    check_counterpoint,
)

__all__ = [
    "CounterpointViolation",
    "check_counterpoint",
]
