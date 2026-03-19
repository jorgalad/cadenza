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

__all__ = [
    "Scale",
    "get_scale",
    "parallel_key",
    "register_scale",
    "relative_key",
    "scale_degree",
    "scales_for_pitches",
]
