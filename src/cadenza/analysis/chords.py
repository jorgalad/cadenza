"""Chord identification, symbol parsing/generation, and realization.

Provides identify_chord for recognizing chords from pitch sets,
chord_symbol/parse_chord_symbol for CN chord string format,
and realize_chord as a consistent analysis API wrapper around get_chord.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from cadenza.api.parsing import parse_pitch_string
from cadenza.core.pitch import Pitch
from cadenza.theory.chords import _CHORD_REGISTRY, get_chord


# ---------------------------------------------------------------------------
# ChordMatch dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ChordMatch:
    """Result of chord identification."""

    root: Pitch
    symbol: str  # Registry key: "maj", "m", "7", "dim7", etc.
    inversion: int  # 0-based: 0 = root position
    pitches: tuple[Pitch, ...]


# ---------------------------------------------------------------------------
# Complexity ranking for preferring simpler interpretations
# ---------------------------------------------------------------------------

_COMPLEXITY_RANK: dict[str, int] = {
    # Triads
    "maj": 0,
    "m": 0,
    "dim": 0,
    "aug": 0,
    # Sevenths
    "7": 1,
    "maj7": 1,
    "m7": 1,
    "m7b5": 1,
    "dim7": 1,
    "mM7": 1,
    "aug7": 1,
    # Sus / add
    "sus2": 1,
    "sus4": 1,
    "add9": 1,
    "add11": 1,
    # Extended
    "9": 2,
    "maj9": 2,
    "m9": 2,
    "11": 3,
    "maj11": 3,
    "13": 4,
    "maj13": 4,
}


# ---------------------------------------------------------------------------
# Chord identification engine
# ---------------------------------------------------------------------------


def identify_chord(pitches: tuple[Pitch, ...]) -> ChordMatch:
    """Identify a chord from a tuple of pitches.

    Args:
        pitches: Two or more Pitch objects forming a chord.

    Returns:
        ChordMatch with root, symbol, inversion, and realized pitches.

    Raises:
        ValueError: If fewer than 2 pitches or no matching chord found.
    """
    if len(pitches) < 2:
        raise ValueError("Need at least 2 pitches to identify a chord")

    input_pcs = frozenset(p.pitch_class for p in pitches)
    # Sort by MIDI number to find bass note
    sorted_pitches = sorted(pitches, key=lambda p: p.midi_number)
    bass_pc = sorted_pitches[0].pitch_class

    # Build a map from pitch class to the actual input pitch (prefer lower octave)
    pc_to_pitch: dict[int, Pitch] = {}
    for p in sorted_pitches:
        if p.pitch_class not in pc_to_pitch:
            pc_to_pitch[p.pitch_class] = p

    best_candidate: tuple[tuple[int, ...], int, str, int, Pitch] | None = None

    for root_pc in range(12):
        for symbol, (semitones, _degree_steps) in _CHORD_REGISTRY.items():
            chord_pcs = frozenset((root_pc + s) % 12 for s in semitones)
            if chord_pcs != input_pcs:
                continue

            # Determine inversion from bass note
            inversion = 0
            for inv_idx, s in enumerate(semitones):
                if (root_pc + s) % 12 == bass_pc:
                    inversion = inv_idx
                    break

            complexity = _COMPLEXITY_RANK.get(symbol, 99)
            score = (inversion, complexity, len(semitones))

            if best_candidate is None or score < best_candidate[0]:
                # Find root pitch from input
                root_pitch = pc_to_pitch.get(root_pc)
                if root_pitch is None:
                    # Root not sounded (rare in inversions) -- skip this candidate
                    continue
                best_candidate = (score, root_pc, symbol, inversion, root_pitch)

    if best_candidate is None:
        raise ValueError(
            f"No matching chord found for pitch classes {sorted(input_pcs)}"
        )

    _score, _root_pc, symbol, inversion, root_pitch = best_candidate

    # Normalize root pitch to lowest reasonable octave for realization
    # Use a root in octave 4 by default for get_chord, preserving step/accidental
    root_for_realization = Pitch(
        step=root_pitch.step,
        accidental=root_pitch.accidental,
        octave=root_pitch.octave,
    )

    # For inversions, the root might need to be in a lower octave
    # so the inverted chord voicing makes sense
    realized = get_chord(root_for_realization, symbol, inversion)

    return ChordMatch(
        root=root_pitch,
        symbol=symbol,
        inversion=inversion,
        pitches=realized,
    )


# ---------------------------------------------------------------------------
# Chord realization
# ---------------------------------------------------------------------------


def realize_chord(
    root: Pitch,
    symbol: str,
    inversion: int = 0,
    octave: int = 4,
) -> tuple[Pitch, ...]:
    """Realize a chord from root, symbol, and optional inversion.

    Delegates to theory.chords.get_chord, adjusting the root octave
    if it differs from the requested octave.

    Args:
        root: Root pitch.
        symbol: Chord quality symbol (e.g., 'maj', 'm', '7').
        inversion: 0 = root position, 1 = first inversion, etc.
        octave: Target octave for the root (default 4).

    Returns:
        Tuple of Pitch objects forming the chord.
    """
    if root.octave != octave:
        root = Pitch(step=root.step, accidental=root.accidental, octave=octave)
    return get_chord(root, symbol, inversion)


# ---------------------------------------------------------------------------
# Chord symbol regex and quality aliases
# ---------------------------------------------------------------------------

_CHORD_SYMBOL_RE = re.compile(r"^([a-g](?:ss|bb|s|b|n)?\d)(.*)$", re.IGNORECASE)

_QUALITY_ALIASES: dict[str, str] = {
    "": "maj",       # bare root defaults to major triad
    "M": "maj",
    "Maj": "maj",
    "maj": "maj",
    "mi": "m",
    "min": "m",
    "-": "m",
    "\u00b0": "dim",  # degree symbol
    "o": "dim",
    "+": "aug",
}


# ---------------------------------------------------------------------------
# Chord symbol generation
# ---------------------------------------------------------------------------


def chord_symbol(root: Pitch, symbol: str) -> str:
    """Generate a CN chord symbol string from root pitch and quality.

    Args:
        root: Root pitch of the chord.
        symbol: Chord quality symbol (registry key).

    Returns:
        CN chord symbol string like 'c4maj7', 'fs4m', 'bb4dim7'.
    """
    acc = "" if root.accidental == "n" else root.accidental
    return f"{root.step}{acc}{root.octave}{symbol}"


def _resolve_quality(quality_str: str) -> str | None:
    """Resolve a quality string to a canonical registry key.

    Tries: exact alias, exact registry, lowercase registry,
    then prefix-based alias matching (e.g., "Maj7" -> "maj" prefix not found,
    but "maj7" lowercase match in registry).
    """
    # 1. Exact alias match
    if quality_str in _QUALITY_ALIASES:
        return _QUALITY_ALIASES[quality_str]
    # 2. Exact registry match
    if quality_str in _CHORD_REGISTRY:
        return quality_str
    # 3. Lowercase in registry (e.g., "Maj7" -> "maj7")
    lower = quality_str.lower()
    if lower in _CHORD_REGISTRY:
        return lower
    # 4. Lowercase alias match
    if lower in _QUALITY_ALIASES:
        return _QUALITY_ALIASES[lower]
    return None


# ---------------------------------------------------------------------------
# Chord symbol parsing
# ---------------------------------------------------------------------------


def parse_chord_symbol(symbol: str) -> tuple[Pitch, ...]:
    """Parse a CN chord symbol string into realized chord pitches.

    Accepts formats like 'c4maj7', 'fs4m', 'bb4dim7', 'c4' (defaults to major).
    Supports quality aliases: Maj, min, mi, -, +, o.

    Args:
        symbol: CN chord symbol string.

    Returns:
        Tuple of Pitch objects forming the chord.

    Raises:
        ValueError: If the symbol cannot be parsed.
    """
    m = _CHORD_SYMBOL_RE.match(symbol)
    if not m:
        raise ValueError(f"Invalid chord symbol: {symbol!r}")

    root_str = m.group(1).lower()
    quality_str = m.group(2)

    root = parse_pitch_string(root_str)

    # Resolve quality through multiple strategies
    normalized = _resolve_quality(quality_str)
    if normalized is None:
        raise ValueError(
            f"Unknown chord quality: {quality_str!r} in {symbol!r}"
        )

    return get_chord(root, normalized)
