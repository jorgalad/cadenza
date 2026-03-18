"""Cadenza: Music analysis, transformation, and generation library."""

__version__ = "0.1.0"

from cadenza.core import (
    Pitch,
    Duration,
    Interval,
    Note,
    Rest,
    Event,
    Phrase,
    Score,
    to_json,
    from_json,
)

__all__ = [
    "Pitch",
    "Duration",
    "Interval",
    "Note",
    "Rest",
    "Event",
    "Phrase",
    "Score",
    "to_json",
    "from_json",
]
