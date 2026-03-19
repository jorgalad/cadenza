"""Theory library: scales, chords, keys, and harmonic analysis."""

from __future__ import annotations

from cadenza.theory.scales import (
    Scale,
    get_scale,
    parallel_key,
    register_scale,
    relative_key,
    scale_degree,
    scales_for_pitches,
)

from cadenza.theory.chords import (
    aug6_chord,
    diatonic_chords,
    get_chord,
    neapolitan_chord,
    register_chord,
    secondary_dominant,
)

__all__ = [
    # Scales
    "Scale",
    "get_scale",
    "parallel_key",
    "register_scale",
    "relative_key",
    "scale_degree",
    "scales_for_pitches",
    # Chords
    "aug6_chord",
    "diatonic_chords",
    "get_chord",
    "neapolitan_chord",
    "register_chord",
    "secondary_dominant",
]
