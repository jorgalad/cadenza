"""Scale type, registry, and query functions.

Provides the Scale dataclass, 40+ built-in scale definitions, and functions
for scale lookup, registration, and querying.
"""

from __future__ import annotations

from dataclasses import dataclass

from cadenza.core.pitch import (
    ACCIDENTAL_SEMITONES,
    STEP_INDEX,
    STEP_SEMITONES,
    Pitch,
)

# ---------------------------------------------------------------------------
# Reverse lookup tables
# ---------------------------------------------------------------------------

_INDEX_TO_STEP: dict[int, str] = {v: k for k, v in STEP_INDEX.items()}
_SEMITONES_TO_ACC: dict[int, str] = {v: k for k, v in ACCIDENTAL_SEMITONES.items()}

# ---------------------------------------------------------------------------
# Scale dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Scale:
    """Immutable scale: root pitch, canonical name, spelled pitches, intervals."""

    root: Pitch
    name: str
    pitches: tuple[Pitch, ...]
    intervals: tuple[int, ...]


# ---------------------------------------------------------------------------
# Scale registry — name -> semitone pattern from root
# ---------------------------------------------------------------------------

_SCALE_REGISTRY: dict[str, tuple[int, ...]] = {
    # Western (SCAL-01)
    "major": (0, 2, 4, 5, 7, 9, 11),
    "natural_minor": (0, 2, 3, 5, 7, 8, 10),
    "harmonic_minor": (0, 2, 3, 5, 7, 8, 11),
    "melodic_minor": (0, 2, 3, 5, 7, 9, 11),
    # Church modes (SCAL-02)
    "dorian": (0, 2, 3, 5, 7, 9, 10),
    "phrygian": (0, 1, 3, 5, 7, 8, 10),
    "lydian": (0, 2, 4, 6, 7, 9, 11),
    "mixolydian": (0, 2, 4, 5, 7, 9, 10),
    "locrian": (0, 1, 3, 5, 6, 8, 10),
    # Pentatonic (SCAL-03)
    "major_pentatonic": (0, 2, 4, 7, 9),
    "minor_pentatonic": (0, 3, 5, 7, 10),
    # Blues (SCAL-04)
    "blues": (0, 3, 5, 6, 7, 10),
    # Symmetric (SCAL-05)
    "whole_tone": (0, 2, 4, 6, 8, 10),
    "diminished": (0, 2, 3, 5, 6, 8, 9, 11),
    "diminished_half_whole": (0, 1, 3, 4, 6, 7, 9, 10),
    "augmented": (0, 3, 4, 7, 8, 11),
    # Bebop (SCAL-06)
    "bebop_dominant": (0, 2, 4, 5, 7, 9, 10, 11),
    "bebop_major": (0, 2, 4, 5, 7, 8, 9, 11),
    "bebop_minor": (0, 2, 3, 5, 7, 8, 9, 10),
    # Non-Western (SCAL-07)
    "hijaz": (0, 1, 4, 5, 7, 8, 10),
    "hijaz_kar": (0, 1, 4, 5, 7, 8, 11),
    "rast": (0, 2, 4, 5, 7, 9, 10),
    "bayati": (0, 1, 3, 5, 7, 8, 10),
    "hungarian_minor": (0, 2, 3, 6, 7, 8, 11),
    "romanian": (0, 2, 3, 6, 7, 9, 10),
    "neapolitan_major": (0, 1, 3, 5, 7, 9, 11),
    "neapolitan_minor": (0, 1, 3, 5, 7, 8, 11),
    "persian": (0, 1, 4, 5, 6, 8, 11),
    "phrygian_dominant": (0, 1, 4, 5, 7, 8, 10),
    "double_harmonic": (0, 1, 4, 5, 7, 8, 11),
    "enigmatic": (0, 1, 4, 6, 8, 10, 11),
    "hirajoshi": (0, 2, 3, 7, 8),
    "in_sen": (0, 1, 5, 7, 10),
    "iwato": (0, 1, 5, 6, 10),
    "yo": (0, 2, 5, 7, 9),
}

# ---------------------------------------------------------------------------
# Aliases
# ---------------------------------------------------------------------------

_SCALE_ALIASES: dict[str, str] = {
    "ionian": "major",
    "aeolian": "natural_minor",
    "minor": "natural_minor",
    "diminished_whole_half": "diminished",
    "ukrainian_dorian": "romanian",
    "spanish_gypsy": "phrygian_dominant",
    "byzantine": "double_harmonic",
}

# ---------------------------------------------------------------------------
# Degree step mappings for non-7-note scales
# ---------------------------------------------------------------------------

_DEGREE_STEPS: dict[str, tuple[int, ...]] = {
    # 5-note scales
    "major_pentatonic": (0, 1, 2, 4, 5),
    "minor_pentatonic": (0, 2, 3, 4, 6),
    "hirajoshi": (0, 1, 2, 4, 5),
    "in_sen": (0, 1, 3, 4, 6),
    "iwato": (0, 1, 3, 4, 6),
    "yo": (0, 1, 3, 4, 5),
    # 6-note scales
    "blues": (0, 2, 3, 4, 4, 6),
    "whole_tone": (0, 1, 2, 3, 4, 5),
    "augmented": (0, 2, 2, 4, 4, 6),
    # 8-note scales
    "diminished": (0, 1, 2, 3, 3, 4, 5, 6),
    "diminished_half_whole": (0, 1, 2, 2, 3, 4, 5, 6),
    "bebop_dominant": (0, 1, 2, 3, 4, 5, 6, 6),
    "bebop_major": (0, 1, 2, 3, 4, 5, 5, 6),
    "bebop_minor": (0, 1, 2, 3, 4, 5, 5, 6),
}

# ---------------------------------------------------------------------------
# Pitch building
# ---------------------------------------------------------------------------


def _build_pitch(root: Pitch, degree_offset: int, semitone_offset: int) -> Pitch:
    """Build a scale pitch from root, letter-name offset, and semitone offset."""
    target_step_idx = (STEP_INDEX[root.step] + degree_offset) % 7
    target_step = _INDEX_TO_STEP[target_step_idx]
    target_midi = root.midi_number + semitone_offset
    base_pc = STEP_SEMITONES[target_step]
    # Compute octave: target_midi = (octave + 1) * 12 + base_pc + acc
    # We need the octave such that natural_midi is closest to target_midi
    # Find the octave that places the accidental in [-2, 2] range
    raw_octave = (target_midi - base_pc) / 12 - 1
    octave = round(raw_octave)
    natural_midi = (octave + 1) * 12 + base_pc
    acc_semitones = target_midi - natural_midi
    if acc_semitones not in _SEMITONES_TO_ACC:
        raise ValueError(
            f"Cannot spell pitch: degree_offset={degree_offset}, "
            f"semitone_offset={semitone_offset} from {root} "
            f"(acc_semitones={acc_semitones})"
        )
    return Pitch(
        step=target_step,
        accidental=_SEMITONES_TO_ACC[acc_semitones],
        octave=octave,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def _infer_degree_steps(intervals: tuple[int, ...]) -> tuple[int, ...]:
    """Infer letter-name offsets from semitone intervals.

    Maps each semitone offset to the most natural diatonic step.
    For 7-note scales, returns (0,1,2,3,4,5,6) — sequential letters.
    For other lengths, uses the chromatic-to-diatonic mapping.
    """
    n = len(intervals)
    if n == 7:
        return tuple(range(7))
    # Map semitone -> most natural diatonic step offset
    # C=0, D=2, E=4, F=5, G=7, A=9, B=11
    _SEMITONE_TO_STEP = {0: 0, 1: 0, 2: 1, 3: 1, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4, 9: 5, 10: 6, 11: 6}
    return tuple(_SEMITONE_TO_STEP[st % 12] for st in intervals)


def get_scale(root: Pitch, name: str) -> Scale:
    """Look up a scale by name and build it from the given root.

    Raises ValueError if the scale name is not found.
    """
    canonical = _SCALE_ALIASES.get(name, name)
    if canonical not in _SCALE_REGISTRY:
        raise ValueError(f"Unknown scale: {name!r}")
    intervals = _SCALE_REGISTRY[canonical]
    degree_steps = _DEGREE_STEPS.get(canonical, _infer_degree_steps(intervals))
    pitches = tuple(
        _build_pitch(root, degree_steps[i], intervals[i])
        for i in range(len(intervals))
    )
    return Scale(root=root, name=canonical, pitches=pitches, intervals=intervals)


def register_scale(name: str, intervals: list[int]) -> None:
    """Register a custom scale definition.

    Raises ValueError if the name is already registered or is an alias.
    """
    if name in _SCALE_REGISTRY or name in _SCALE_ALIASES:
        raise ValueError(f"Scale name {name!r} already registered")
    _SCALE_REGISTRY[name] = tuple(intervals)
