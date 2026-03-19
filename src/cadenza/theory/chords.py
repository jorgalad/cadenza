"""Chord registry, construction, and query functions.

Provides get_chord for building any standard chord type from a root pitch,
with support for inversions, custom chord registration, and lead-sheet
chord symbol conventions.
"""

from __future__ import annotations

from cadenza.core.pitch import (
    ACCIDENTAL_SEMITONES,
    STEP_INDEX,
    STEP_SEMITONES,
    Pitch,
)

# ---------------------------------------------------------------------------
# Reverse lookup tables (same as scales.py)
# ---------------------------------------------------------------------------

_INDEX_TO_STEP: dict[int, str] = {v: k for k, v in STEP_INDEX.items()}
_SEMITONES_TO_ACC: dict[int, str] = {v: k for k, v in ACCIDENTAL_SEMITONES.items()}

# ---------------------------------------------------------------------------
# Pitch building (same algorithm as scales._build_pitch)
# ---------------------------------------------------------------------------


def _build_pitch(root: Pitch, degree_offset: int, semitone_offset: int) -> Pitch:
    """Build a chord pitch from root, letter-name offset, and semitone offset."""
    target_step_idx = (STEP_INDEX[root.step] + degree_offset) % 7
    target_step = _INDEX_TO_STEP[target_step_idx]
    target_midi = root.midi_number + semitone_offset
    base_pc = STEP_SEMITONES[target_step]
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
# Chord registry — name -> (semitone_offsets, degree_steps)
# ---------------------------------------------------------------------------

_CHORD_REGISTRY: dict[str, tuple[tuple[int, ...], tuple[int, ...]]] = {
    # Triads (CHRD-01)
    "maj": ((0, 4, 7), (0, 2, 4)),
    "m": ((0, 3, 7), (0, 2, 4)),
    "dim": ((0, 3, 6), (0, 2, 4)),
    "aug": ((0, 4, 8), (0, 2, 4)),
    # Seventh chords (CHRD-02)
    "7": ((0, 4, 7, 10), (0, 2, 4, 6)),
    "maj7": ((0, 4, 7, 11), (0, 2, 4, 6)),
    "m7": ((0, 3, 7, 10), (0, 2, 4, 6)),
    "m7b5": ((0, 3, 6, 10), (0, 2, 4, 6)),
    "dim7": ((0, 3, 6, 9), (0, 2, 4, 6)),
    "mM7": ((0, 3, 7, 11), (0, 2, 4, 6)),
    "aug7": ((0, 4, 8, 10), (0, 2, 4, 6)),
    # Extended (CHRD-03)
    "9": ((0, 4, 7, 10, 14), (0, 2, 4, 6, 8)),
    "maj9": ((0, 4, 7, 11, 14), (0, 2, 4, 6, 8)),
    "m9": ((0, 3, 7, 10, 14), (0, 2, 4, 6, 8)),
    "11": ((0, 4, 7, 10, 14, 17), (0, 2, 4, 6, 8, 10)),
    "maj11": ((0, 4, 7, 11, 14, 17), (0, 2, 4, 6, 8, 10)),
    "13": ((0, 4, 7, 10, 14, 17, 21), (0, 2, 4, 6, 8, 10, 12)),
    "maj13": ((0, 4, 7, 11, 14, 17, 21), (0, 2, 4, 6, 8, 10, 12)),
    # Added/Suspended (CHRD-04)
    "add9": ((0, 4, 7, 14), (0, 2, 4, 8)),
    "add11": ((0, 4, 7, 17), (0, 2, 4, 10)),
    "sus2": ((0, 2, 7), (0, 1, 4)),
    "sus4": ((0, 5, 7), (0, 3, 4)),
}

# ---------------------------------------------------------------------------
# Aliases
# ---------------------------------------------------------------------------

_CHORD_ALIASES: dict[str, str] = {
    "min": "m",
    "M7": "maj7",
    "half_dim7": "m7b5",
    "min7": "m7",
    "min_maj7": "mM7",
}

# ---------------------------------------------------------------------------
# Inversion
# ---------------------------------------------------------------------------


def _apply_inversion(pitches: tuple[Pitch, ...], inversion: int) -> tuple[Pitch, ...]:
    """Rotate bottom N pitches up one octave for the given inversion."""
    if inversion < 0 or inversion >= len(pitches):
        raise ValueError(
            f"Inversion {inversion} out of range for {len(pitches)}-note chord"
        )
    result = list(pitches)
    for _ in range(inversion):
        p = result.pop(0)
        result.append(Pitch(step=p.step, accidental=p.accidental, octave=p.octave + 1))
    return tuple(result)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_chord(
    root: Pitch, symbol: str, inversion: int = 0
) -> tuple[Pitch, ...]:
    """Build a chord from root pitch and lead-sheet symbol.

    Args:
        root: Root pitch of the chord.
        symbol: Chord quality symbol (e.g., 'maj', 'm', '7', 'dim7').
        inversion: 0 = root position, 1 = first inversion, etc.

    Returns:
        Tuple of correctly-spelled Pitch objects.

    Raises:
        ValueError: If symbol is unknown or inversion is out of range.
    """
    canonical = _CHORD_ALIASES.get(symbol, symbol)
    if canonical not in _CHORD_REGISTRY:
        raise ValueError(f"Unknown chord symbol: {symbol!r}")
    semitones, degree_steps = _CHORD_REGISTRY[canonical]
    pitches = tuple(
        _build_pitch(root, degree_steps[i], semitones[i])
        for i in range(len(semitones))
    )
    if inversion != 0:
        pitches = _apply_inversion(pitches, inversion)
    return pitches


def register_chord(
    name: str, intervals: list[int], degree_steps: tuple[int, ...]
) -> None:
    """Register a custom chord definition.

    Args:
        name: Chord symbol name.
        intervals: Semitone offsets from root.
        degree_steps: Letter-name step offsets from root.

    Raises:
        ValueError: If name already exists in registry or aliases.
    """
    if name in _CHORD_REGISTRY or name in _CHORD_ALIASES:
        raise ValueError(f"Chord name {name!r} already registered")
    _CHORD_REGISTRY[name] = (tuple(intervals), degree_steps)
