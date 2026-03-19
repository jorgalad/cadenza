"""Batch operations for phrase mutation.

Re-exports all public functions from submodules.
"""

from cadenza.batch.mutations import (
    set_articulation_nth,
    set_dynamic_nth,
    crescendo,
    decrescendo,
    add_articulation_if,
    remove_articulation_if,
)
from cadenza.batch.pitch_ops import replace_pitch, filter_phrase
from cadenza.batch.rhythm_ops import quantize_lengths
from cadenza.batch.humanize import humanize
from cadenza.batch.windowed import apply_windowed

__all__ = [
    "set_articulation_nth",
    "set_dynamic_nth",
    "crescendo",
    "decrescendo",
    "add_articulation_if",
    "remove_articulation_if",
    "replace_pitch",
    "filter_phrase",
    "quantize_lengths",
    "humanize",
    "apply_windowed",
]
