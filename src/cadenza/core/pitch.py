"""Pitch: immutable compound pitch type preserving enharmonic spelling."""

from __future__ import annotations

from dataclasses import dataclass

# Semitone offsets for each letter name (C-based)
STEP_SEMITONES: dict[str, int] = {
    "c": 0, "d": 2, "e": 4, "f": 5, "g": 7, "a": 9, "b": 11,
}

# Semitone offsets for accidentals
ACCIDENTAL_SEMITONES: dict[str, int] = {
    "bb": -2, "b": -1, "n": 0, "s": 1, "ss": 2,
}

# Letter-name index for generic interval computation
STEP_INDEX: dict[str, int] = {
    "c": 0, "d": 1, "e": 2, "f": 3, "g": 4, "a": 5, "b": 6,
}


@dataclass(frozen=True, order=False)
class Pitch:
    """Immutable pitch with step, accidental, and octave.

    Equality is spelling-sensitive: Eb3 != D#3.
    Use enharmonic_equal() to compare by MIDI number.
    """

    step: str          # lowercase a-g
    accidental: str    # "n", "s", "b", "ss", "bb"
    octave: int        # SPN: middle C = C4, range -1..10

    def __post_init__(self) -> None:
        if self.step not in STEP_SEMITONES:
            raise ValueError(f"Invalid step: {self.step!r}")
        if self.accidental not in ACCIDENTAL_SEMITONES:
            raise ValueError(f"Invalid accidental: {self.accidental!r}")
        if not (-1 <= self.octave <= 10):
            raise ValueError(f"Octave out of range: {self.octave}")

    @property
    def midi_number(self) -> int:
        """MIDI note number. C4 = 60."""
        return (self.octave + 1) * 12 + STEP_SEMITONES[self.step] + ACCIDENTAL_SEMITONES[self.accidental]

    @property
    def pitch_class(self) -> int:
        """Pitch class 0-11 (C=0)."""
        return self.midi_number % 12

    def enharmonic_equal(self, other: Pitch) -> bool:
        """True if same sounding pitch (same MIDI number)."""
        return self.midi_number == other.midi_number

    def __lt__(self, other: object) -> bool:
        """Order by MIDI number, then by step index for enharmonic ties."""
        if not isinstance(other, Pitch):
            return NotImplemented
        if self.midi_number != other.midi_number:
            return self.midi_number < other.midi_number
        return STEP_INDEX[self.step] < STEP_INDEX[other.step]

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Pitch):
            return NotImplemented
        return self == other or self.__lt__(other)

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Pitch):
            return NotImplemented
        return other.__lt__(self)  # type: ignore[arg-type]

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Pitch):
            return NotImplemented
        return self == other or self.__gt__(other)
