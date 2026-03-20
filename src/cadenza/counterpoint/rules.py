"""Counterpoint rules engine: consonance classification, default severities, species constants."""

from __future__ import annotations

PERFECT_CONSONANCES: frozenset[int] = frozenset({0, 7})
IMPERFECT_CONSONANCES: frozenset[int] = frozenset({3, 4, 8, 9})
DISSONANCES: frozenset[int] = frozenset({1, 2, 5, 6, 10, 11})


def classify_interval(semitones_mod12: int) -> str:
    """Return 'perfect', 'imperfect', or 'dissonant' for a semitone value mod 12."""
    if semitones_mod12 in PERFECT_CONSONANCES:
        return "perfect"
    if semitones_mod12 in IMPERFECT_CONSONANCES:
        return "imperfect"
    return "dissonant"


DEFAULT_SEVERITIES: dict[str, str] = {
    "parallel_fifth": "error",
    "parallel_octave": "error",
    "direct_octave": "error",
    "dissonance_on_beat": "error",
    "voice_crossing": "error",
    "unresolved_suspension": "error",
    "large_leap": "warning",
    "repeated_note": "warning",
    "voice_overlap": "warning",
    "augmented_leap": "suggestion",
    "climax_placement": "suggestion",
}
