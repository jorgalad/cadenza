"""Interval: immutable interval type with quality, number, and direction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from cadenza.core.pitch import Pitch, STEP_INDEX


# Major scale semitone offsets for generic intervals 1-7
MAJOR_SCALE_SEMITONES: dict[int, int] = {
    1: 0, 2: 2, 3: 4, 4: 5, 5: 7, 6: 9, 7: 11,
}

# Generic interval numbers that are "perfect" type (mod 7 equivalents)
_PERFECT_GENERIC: set[int] = {1, 4, 5}  # unison, fourth, fifth (mod 7: 0, 3, 4)


@dataclass(frozen=True)
class Interval:
    """Immutable musical interval with quality, number, and direction.

    quality: "P" (perfect), "M" (major), "m" (minor),
             "A" (augmented), "d" (diminished), "AA", "dd"
    number: 1 = unison, 2 = second, ..., 8 = octave, 9+ = compound
    direction: +1 ascending, -1 descending
    """

    quality: str
    number: int
    direction: int

    _PERFECT_INTERVALS: ClassVar[set[int]] = {1, 4, 5, 8}

    @property
    def semitones(self) -> int:
        """Signed semitone distance represented by this interval."""
        # Reduce to simple interval (1-7) for lookup
        simple = ((self.number - 1) % 7) + 1
        octaves = (self.number - 1) // 7

        base = MAJOR_SCALE_SEMITONES[simple] + 12 * octaves

        # Adjust for quality
        is_perfect = simple in _PERFECT_GENERIC or self.number == 8
        if is_perfect:
            offset = {"dd": -2, "d": -1, "P": 0, "A": 1, "AA": 2}[self.quality]
        else:
            offset = {"dd": -3, "d": -2, "m": -1, "M": 0, "A": 1, "AA": 2}[self.quality]

        return self.direction * (base + offset)

    @staticmethod
    def between(p1: Pitch, p2: Pitch) -> Interval:
        """Compute the interval from p1 to p2.

        Ascending if p2 >= p1 (by MIDI number), descending otherwise.
        For equal MIDI numbers, returns ascending unison or appropriate interval.
        """
        # Determine direction
        midi_diff = p2.midi_number - p1.midi_number
        if midi_diff >= 0:
            direction = 1
            lower, upper = p1, p2
        else:
            direction = -1
            lower, upper = p2, p1

        # Generic interval from letter distance
        lower_idx = STEP_INDEX[lower.step]
        upper_idx = STEP_INDEX[upper.step]
        generic = (upper_idx - lower_idx) % 7 + 1

        # Account for octave span
        octave_span = upper.octave - lower.octave
        if upper_idx < lower_idx:
            octave_span -= 1

        number = generic + 7 * octave_span

        # Actual semitone distance (always positive after normalization)
        actual_semitones = abs(upper.midi_number - lower.midi_number)

        # Expected semitones for this generic interval in the major scale
        simple_generic = ((number - 1) % 7) + 1
        expected_octaves = (number - 1) // 7
        expected_semitones = MAJOR_SCALE_SEMITONES[simple_generic] + 12 * expected_octaves

        # Derive quality from difference
        diff = actual_semitones - expected_semitones

        is_perfect = simple_generic in _PERFECT_GENERIC or number == 8
        if is_perfect:
            quality_map = {-2: "dd", -1: "d", 0: "P", 1: "A", 2: "AA"}
        else:
            quality_map = {-3: "dd", -2: "d", -1: "m", 0: "M", 1: "A", 2: "AA"}

        quality = quality_map.get(diff, "A" if diff > 0 else "d")

        return Interval(quality=quality, number=number, direction=direction)
