"""Key detection and modulation detection using Krumhansl-Schmuckler profiles.

Provides detect_key for identifying the most likely key from pitch data,
and detect_modulations for finding key changes within a phrase.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from cadenza.core.note import Note
from cadenza.core.pitch import Pitch


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class KeyResult:
    """Result of key detection."""

    root: Pitch
    mode: str  # "major", "natural_minor", "harmonic_minor", "melodic_minor"
    confidence: float  # 0.0 to 1.0 (Pearson r, clipped via max(0.0, r))


@dataclass(frozen=True, slots=True)
class Modulation:
    """Detected key change within a phrase."""

    position: int  # Index in pitch sequence where modulation is detected
    from_key: KeyResult
    to_key: KeyResult


# ---------------------------------------------------------------------------
# Krumhansl-Kessler tonal profiles
# ---------------------------------------------------------------------------

# Standard K-K profiles (pitch classes: C, C#, D, D#, E, F, F#, G, G#, A, A#, B)
MAJOR_PROFILE: tuple[float, ...] = (
    6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88
)
MINOR_PROFILE: tuple[float, ...] = (
    6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17
)


# ---------------------------------------------------------------------------
# Synthetic profiles for harmonic and melodic minor
# ---------------------------------------------------------------------------


def _make_synthetic_profile(
    scale_pcs: frozenset[int], tonic_pc: int = 0, dominant_pc: int = 7
) -> tuple[float, ...]:
    """Build a synthetic tonal profile from scale pitch classes."""
    profile: list[float] = []
    for pc in range(12):
        if pc == tonic_pc:
            profile.append(7.0)
        elif pc == dominant_pc:
            profile.append(5.5)
        elif pc in scale_pcs:
            profile.append(3.5)
        else:
            profile.append(1.0)
    return tuple(profile)


# Harmonic minor: 0, 2, 3, 5, 7, 8, 11
HARMONIC_MINOR_PROFILE: tuple[float, ...] = _make_synthetic_profile(
    frozenset({0, 2, 3, 5, 7, 8, 11})
)

# Melodic minor: 0, 2, 3, 5, 7, 9, 11
MELODIC_MINOR_PROFILE: tuple[float, ...] = _make_synthetic_profile(
    frozenset({0, 2, 3, 5, 7, 9, 11})
)

# All profiles keyed by mode name
_PROFILES: dict[str, tuple[float, ...]] = {
    "major": MAJOR_PROFILE,
    "natural_minor": MINOR_PROFILE,
    "harmonic_minor": HARMONIC_MINOR_PROFILE,
    "melodic_minor": MELODIC_MINOR_PROFILE,
}


# ---------------------------------------------------------------------------
# Pitch-class to Pitch mapping (sharp preference, matching scales.py)
# ---------------------------------------------------------------------------

_PC_TO_PITCH_SHARP: list[tuple[str, str]] = [
    ("c", "n"), ("c", "s"), ("d", "n"), ("d", "s"), ("e", "n"), ("f", "n"),
    ("f", "s"), ("g", "n"), ("g", "s"), ("a", "n"), ("a", "s"), ("b", "n"),
]


# ---------------------------------------------------------------------------
# Statistical helpers
# ---------------------------------------------------------------------------


def _pearson_correlation(x: tuple[float, ...], y: tuple[float, ...]) -> float:
    """Compute Pearson correlation coefficient between two equal-length sequences."""
    n = len(x)
    if n == 0:
        return 0.0
    mx = sum(x) / n
    my = sum(y) / n
    dx = tuple(xi - mx for xi in x)
    dy = tuple(yi - my for yi in y)
    numerator = sum(a * b for a, b in zip(dx, dy))
    denom_x = sum(a * a for a in dx)
    denom_y = sum(b * b for b in dy)
    denominator = math.sqrt(denom_x * denom_y)
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _pitch_class_histogram(pitches: list[Pitch]) -> tuple[float, ...]:
    """Build a 12-element normalized pitch class frequency histogram."""
    counts = [0] * 12
    for p in pitches:
        counts[p.pitch_class] += 1
    total = sum(counts)
    if total == 0:
        return tuple(0.0 for _ in range(12))
    return tuple(c / total for c in counts)


# ---------------------------------------------------------------------------
# Pitch extraction
# ---------------------------------------------------------------------------


def _extract_pitches(
    input_data: tuple[object, ...] | list[object],
) -> list[Pitch]:
    """Extract Pitch objects from various input types.

    Accepts:
    - list[Pitch] or tuple[Pitch, ...]
    - Phrase (tuple[Event, ...]) -- extracts pitch from Note, skips Rest
    """
    if not input_data:
        return []
    first = input_data[0]
    if isinstance(first, Pitch):
        return list(input_data)  # type: ignore[arg-type]
    # Assume it's a Phrase (tuple of Events)
    return [event.pitch for event in input_data if isinstance(event, Note)]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def detect_key(
    phrase_or_pitches: tuple[object, ...] | list[object],
) -> KeyResult:
    """Detect the most likely key from pitch data.

    Args:
        phrase_or_pitches: A Phrase, tuple of Pitches, or list of Pitches.

    Returns:
        KeyResult with root, mode, and confidence.
    """
    pitches = _extract_pitches(phrase_or_pitches)
    if not pitches:
        return KeyResult(root=Pitch("c", "n", 4), mode="major", confidence=0.0)

    histogram = _pitch_class_histogram(pitches)

    best_root_pc = 0
    best_mode = "major"
    best_confidence = 0.0

    for root_pc in range(12):
        for mode, profile in _PROFILES.items():
            # Rotate profile so index 0 aligns with root_pc
            rotated_profile = tuple(profile[(i - root_pc) % 12] for i in range(12))
            correlation = _pearson_correlation(histogram, rotated_profile)
            clipped = max(0.0, correlation)
            if clipped > best_confidence:
                best_confidence = clipped
                best_root_pc = root_pc
                best_mode = mode

    # Map root_pc to a Pitch, preferring spelling from input
    root_pitch = _find_root_pitch(best_root_pc, pitches)

    return KeyResult(root=root_pitch, mode=best_mode, confidence=best_confidence)


def _find_root_pitch(root_pc: int, pitches: list[Pitch]) -> Pitch:
    """Find a Pitch for the given pitch class, preferring input spelling."""
    for p in pitches:
        if p.pitch_class == root_pc:
            return Pitch(step=p.step, accidental=p.accidental, octave=4)
    # Fallback: sharp-default
    step, acc = _PC_TO_PITCH_SHARP[root_pc % 12]
    return Pitch(step=step, accidental=acc, octave=4)


def detect_modulations(
    phrase_or_pitches: tuple[object, ...] | list[object],
    window: int = 4,
) -> list[Modulation]:
    """Detect key changes within a phrase using a sliding window.

    Args:
        phrase_or_pitches: A Phrase, tuple of Pitches, or list of Pitches.
        window: Size of the sliding window (number of pitches).

    Returns:
        List of Modulation objects, possibly empty.
    """
    pitches = _extract_pitches(phrase_or_pitches)

    if len(pitches) < window * 2:
        return []

    modulations: list[Modulation] = []

    # Detect key for the first window to establish the initial key
    current_key = detect_key(pitches[:window])
    change_start: int | None = None
    candidate_key: KeyResult | None = None
    consecutive_count = 0

    for i in range(1, len(pitches) - window + 1):
        window_pitches = pitches[i : i + window]
        window_key = detect_key(window_pitches)

        same_as_current = (
            window_key.root.pitch_class == current_key.root.pitch_class
            and window_key.mode == current_key.mode
        )

        if same_as_current:
            # Reset change tracking
            change_start = None
            candidate_key = None
            consecutive_count = 0
        else:
            if candidate_key is not None and (
                window_key.root.pitch_class == candidate_key.root.pitch_class
                and window_key.mode == candidate_key.mode
            ):
                consecutive_count += 1
            else:
                # New candidate
                change_start = i
                candidate_key = window_key
                consecutive_count = 1

            # Confirm modulation after window consecutive different-key windows
            if consecutive_count >= window:
                modulations.append(
                    Modulation(
                        position=change_start if change_start is not None else i,
                        from_key=current_key,
                        to_key=candidate_key if candidate_key is not None else window_key,
                    )
                )
                current_key = candidate_key if candidate_key is not None else window_key
                change_start = None
                candidate_key = None
                consecutive_count = 0

    return modulations
