"""Pitch transforms: PTCH-01 through PTCH-09.

Pure functions that operate on Phrase/Pitch types from cadenza.core.
All transforms return new objects (no mutation).
"""

from __future__ import annotations

import math
from dataclasses import replace
from typing import Any, Callable

from cadenza.theory.scales import Scale

from cadenza.core.interval import Interval
from cadenza.core.note import Event, Note, Rest
from cadenza.core.phrase import Phrase
from cadenza.core.pitch import (
    ACCIDENTAL_SEMITONES,
    STEP_INDEX,
    STEP_SEMITONES,
    Pitch,
)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_INDEX_TO_STEP: dict[int, str] = {v: k for k, v in STEP_INDEX.items()}

_SEMITONES_TO_ACC: dict[int, str] = {v: k for k, v in ACCIDENTAL_SEMITONES.items()}

_MIDI_TO_PITCH_SHARP: list[tuple[str, str]] = [
    ("c", "n"), ("c", "s"), ("d", "n"), ("d", "s"), ("e", "n"), ("f", "n"),
    ("f", "s"), ("g", "n"), ("g", "s"), ("a", "n"), ("a", "s"), ("b", "n"),
]

_MIDI_TO_PITCH_FLAT: list[tuple[str, str]] = [
    ("c", "n"), ("d", "b"), ("d", "n"), ("e", "b"), ("e", "n"), ("f", "n"),
    ("g", "b"), ("g", "n"), ("a", "b"), ("a", "n"), ("b", "b"), ("b", "n"),
]


def _transpose_pitch(pitch: Pitch, interval: Interval) -> Pitch:
    """Transpose a single pitch by an interval, preserving correct spelling."""
    # 1. Compute target letter name from generic interval number
    source_idx = STEP_INDEX[pitch.step]
    generic_steps = interval.number - 1  # 0 for unison, 1 for second, etc.
    target_idx = (source_idx + interval.direction * generic_steps) % 7
    target_step = _INDEX_TO_STEP[target_idx]

    # 2. Compute target MIDI number
    target_midi = pitch.midi_number + interval.semitones

    # 3. Compute target octave
    # target_midi = (octave + 1) * 12 + STEP_SEMITONES[target_step] + acc_semitones
    raw_octave = (target_midi - STEP_SEMITONES[target_step]) / 12 - 1
    octave = round(raw_octave)

    # 4. Compute required accidental
    natural_midi = (octave + 1) * 12 + STEP_SEMITONES[target_step]
    acc_semitones = target_midi - natural_midi

    if acc_semitones not in _SEMITONES_TO_ACC:
        raise ValueError(
            f"Transposition produces out-of-range accidental: {acc_semitones} semitones"
        )
    accidental = _SEMITONES_TO_ACC[acc_semitones]

    return Pitch(step=target_step, accidental=accidental, octave=octave)


def _map_pitches(phrase: Phrase, fn: Callable[[Pitch], Pitch]) -> Phrase:
    """Apply a pitch transformation to all Notes in a phrase, preserving Rests."""
    events: list[Event] = []
    for event in phrase:
        if isinstance(event, Note):
            events.append(replace(event, pitch=fn(event.pitch)))
        else:
            events.append(event)  # Rest passes through
    return tuple(events)


# ---------------------------------------------------------------------------
# PTCH-01: chromatic_transpose / diatonic_transpose
# ---------------------------------------------------------------------------

def chromatic_transpose(phrase: Phrase, interval: Interval) -> Phrase:
    """Transpose all notes chromatically by the given interval.

    Rests pass through unchanged. Empty phrase returns ().
    """
    if not phrase:
        return ()
    return _map_pitches(phrase, lambda p: _transpose_pitch(p, interval))


def diatonic_transpose(phrase: Phrase, n: int, scale: Scale | None = None) -> Phrase:
    """Transpose diatonically within a scale by n scale degrees.

    Each pitch is moved by n steps within the given scale.
    Raises ValueError if a pitch is not in the scale.
    """
    if not phrase or scale is None:
        return () if not phrase else phrase
    scale_pitches = scale.pitches
    num_degrees = len(scale_pitches)

    def _transpose_one(p: Pitch) -> Pitch:
        pc = p.pitch_class
        for i, sp in enumerate(scale_pitches):
            if sp.pitch_class == pc:
                target_degree = i + n
                octave_shift, target_idx = divmod(target_degree, num_degrees)
                target_sp = scale_pitches[target_idx]
                oct_diff = p.octave - sp.octave
                return Pitch(
                    target_sp.step,
                    target_sp.accidental,
                    target_sp.octave + oct_diff + octave_shift,
                )
        raise ValueError(f"Pitch {p} is not in scale {scale.name}")

    return _map_pitches(phrase, _transpose_one)


# ---------------------------------------------------------------------------
# PTCH-02: invert
# ---------------------------------------------------------------------------

def invert(phrase: Phrase, axis: Pitch | None = None) -> Phrase:
    """Invert phrase around axis pitch. Default axis = first note's pitch.

    Each note's interval from the axis is reflected (direction flipped).
    Rests pass through unchanged. Empty phrase returns ().
    """
    if not phrase:
        return ()

    if axis is None:
        first_note = next((e for e in phrase if isinstance(e, Note)), None)
        if first_note is None:
            return phrase  # all rests, nothing to invert
        axis = first_note.pitch

    def _invert_pitch(p: Pitch) -> Pitch:
        iv = Interval.between(axis, p)
        # Reflect: flip direction
        reflected = Interval(
            quality=iv.quality, number=iv.number, direction=-iv.direction
        )
        return _transpose_pitch(axis, reflected)

    return _map_pitches(phrase, _invert_pitch)


# ---------------------------------------------------------------------------
# PTCH-03: interval_between
# ---------------------------------------------------------------------------

def interval_between(p1: Pitch, p2: Pitch) -> Interval:
    """Compute the interval from p1 to p2. Thin wrapper around Interval.between."""
    return Interval.between(p1, p2)


# ---------------------------------------------------------------------------
# PTCH-04: enharmonic_respell
# ---------------------------------------------------------------------------

def enharmonic_respell(pitch: Pitch, prefer_sharps: bool = True) -> Pitch:
    """Return the canonical enharmonic spelling of a pitch.

    Uses MIDI-to-pitch lookup for the preferred spelling direction.
    """
    return from_midi(pitch.midi_number, prefer_sharps=prefer_sharps)


# ---------------------------------------------------------------------------
# PTCH-05: pitch_class
# ---------------------------------------------------------------------------

def pitch_class(pitch: Pitch) -> int:
    """Return the pitch class (0-11, C=0) of a pitch."""
    return pitch.pitch_class


# ---------------------------------------------------------------------------
# PTCH-06: from_midi
# ---------------------------------------------------------------------------

def from_midi(midi_number: int, prefer_sharps: bool = True) -> Pitch:
    """Convert a MIDI note number to a Pitch.

    Default prefers sharps for black keys (e.g., MIDI 61 -> C#4).
    Set prefer_sharps=False for flats (e.g., MIDI 61 -> Db4).
    """
    table = _MIDI_TO_PITCH_SHARP if prefer_sharps else _MIDI_TO_PITCH_FLAT
    octave = (midi_number // 12) - 1
    pc = midi_number % 12
    step, acc = table[pc]
    return Pitch(step=step, accidental=acc, octave=octave)


# ---------------------------------------------------------------------------
# PTCH-07: to_frequency / from_frequency
# ---------------------------------------------------------------------------

def to_frequency(pitch: Pitch, a4_hz: float = 440.0) -> float:
    """Convert pitch to frequency in Hz. A4 = 440 Hz by default."""
    return a4_hz * (2 ** ((pitch.midi_number - 69) / 12))


def from_frequency(
    hz: float, a4_hz: float = 440.0, prefer_sharps: bool = True
) -> Pitch:
    """Convert frequency to nearest pitch."""
    midi = round(12 * math.log2(hz / a4_hz) + 69)
    return from_midi(midi, prefer_sharps=prefer_sharps)


# ---------------------------------------------------------------------------
# PTCH-08: pitch_in_scale (stub)
# ---------------------------------------------------------------------------

def pitch_in_scale(pitch: Pitch, scale: Scale) -> bool:
    """Check if a pitch belongs to a scale (octave-independent)."""
    scale_pcs = {sp.pitch_class for sp in scale.pitches}
    return pitch.pitch_class in scale_pcs


# ---------------------------------------------------------------------------
# PTCH-09: nearest_in_scale (stub)
# ---------------------------------------------------------------------------

def nearest_in_scale(pitch: Pitch, scale: Scale) -> Pitch:
    """Find the nearest pitch in a scale by MIDI distance.

    Considers scale pitches in nearby octaves to find the closest match.
    """
    candidates: list[Pitch] = []
    for sp in scale.pitches:
        for oct_offset in (-1, 0, 1):
            oct = pitch.octave + oct_offset
            if -1 <= oct <= 10:
                candidates.append(Pitch(sp.step, sp.accidental, oct))
    return min(candidates, key=lambda c: abs(c.midi_number - pitch.midi_number))
