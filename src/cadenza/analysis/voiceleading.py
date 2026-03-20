"""Voice leading violation detection for multi-voice scores.

Detects parallel fifths, parallel octaves, voice crossing, voice overlap,
large leaps, and augmented/diminished leaps across all voice pairs in a Score.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from itertools import permutations

from cadenza.core.interval import Interval
from cadenza.core.note import Note
from cadenza.core.phrase import Phrase
from cadenza.core.pitch import Pitch
from cadenza.core.score import Score


# ---------------------------------------------------------------------------
# VoiceLeadingViolation dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class VoiceLeadingViolation:
    """A single voice leading violation.

    Attributes:
        rule: Type of violation (parallel_fifth, parallel_octave,
              voice_crossing, voice_overlap, large_leap, augmented_leap).
        voice1: Name of the first voice involved.
        voice2: Name of the second voice involved (same as voice1 for leaps).
        position: 0-based note index where the violation occurs.
        interval: The Interval object at the violation point.
        severity: 'error', 'warning', or 'suggestion'.
    """

    rule: str
    voice1: str
    voice2: str
    position: int
    interval: Interval
    severity: str


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _extract_pitches(phrase: Phrase) -> list[Pitch | None]:
    """Extract pitches from a phrase, returning None for rests."""
    result: list[Pitch | None] = []
    for event in phrase:
        if isinstance(event, Note):
            result.append(event.pitch)
        else:
            result.append(None)
    return result


def _check_parallels(
    pitches_a: list[Pitch | None],
    pitches_b: list[Pitch | None],
    voice_a: str,
    voice_b: str,
    target_semitones_mod12: int,
    rule_name: str,
) -> list[VoiceLeadingViolation]:
    """Check for parallel motion at a specific interval (fifths or octaves).

    pitches_a is the upper voice, pitches_b is the lower voice.
    """
    violations: list[VoiceLeadingViolation] = []
    length = min(len(pitches_a), len(pitches_b))

    for i in range(1, length):
        prev_a = pitches_a[i - 1]
        curr_a = pitches_a[i]
        prev_b = pitches_b[i - 1]
        curr_b = pitches_b[i]

        # Skip if any pitch is None (rest)
        if any(p is None for p in (prev_a, curr_a, prev_b, curr_b)):
            continue

        # Both voices must actually move (not oblique)
        if prev_a.midi_number == curr_a.midi_number:
            continue
        if prev_b.midi_number == curr_b.midi_number:
            continue

        # Check both intervals match target
        prev_interval_mod12 = abs(Interval.between(prev_b, prev_a).semitones) % 12
        curr_interval_mod12 = abs(Interval.between(curr_b, curr_a).semitones) % 12

        if prev_interval_mod12 != target_semitones_mod12:
            continue
        if curr_interval_mod12 != target_semitones_mod12:
            continue

        # Check same direction
        motion_a = curr_a.midi_number - prev_a.midi_number
        motion_b = curr_b.midi_number - prev_b.midi_number

        if (motion_a > 0) != (motion_b > 0):
            continue  # Contrary motion

        violations.append(
            VoiceLeadingViolation(
                rule=rule_name,
                voice1=voice_a,
                voice2=voice_b,
                position=i,
                interval=Interval.between(curr_b, curr_a),
                severity="error",
            )
        )

    return violations


def _check_crossing(
    pitches_upper: list[Pitch | None],
    pitches_lower: list[Pitch | None],
    voice_upper: str,
    voice_lower: str,
) -> list[VoiceLeadingViolation]:
    """Check for voice crossing (lower voice exceeds upper voice pitch)."""
    violations: list[VoiceLeadingViolation] = []
    length = min(len(pitches_upper), len(pitches_lower))

    for i in range(length):
        upper = pitches_upper[i]
        lower = pitches_lower[i]

        if upper is None or lower is None:
            continue

        if lower.midi_number > upper.midi_number:
            violations.append(
                VoiceLeadingViolation(
                    rule="voice_crossing",
                    voice1=voice_upper,
                    voice2=voice_lower,
                    position=i,
                    interval=Interval.between(upper, lower),
                    severity="error",
                )
            )

    return violations


def _check_overlap(
    pitches_upper: list[Pitch | None],
    pitches_lower: list[Pitch | None],
    voice_upper: str,
    voice_lower: str,
) -> list[VoiceLeadingViolation]:
    """Check for voice overlap (voice moves past adjacent voice's previous position)."""
    violations: list[VoiceLeadingViolation] = []
    length = min(len(pitches_upper), len(pitches_lower))

    for i in range(1, length):
        curr_upper = pitches_upper[i]
        prev_lower = pitches_lower[i - 1]
        curr_lower = pitches_lower[i]
        prev_upper = pitches_upper[i - 1]

        # Upper voice at pos i goes below lower voice at pos i-1
        if curr_upper is not None and prev_lower is not None:
            if curr_upper.midi_number < prev_lower.midi_number:
                violations.append(
                    VoiceLeadingViolation(
                        rule="voice_overlap",
                        voice1=voice_upper,
                        voice2=voice_lower,
                        position=i,
                        interval=Interval.between(curr_upper, prev_lower),
                        severity="warning",
                    )
                )

        # Lower voice at pos i goes above upper voice at pos i-1
        if curr_lower is not None and prev_upper is not None:
            if curr_lower.midi_number > prev_upper.midi_number:
                violations.append(
                    VoiceLeadingViolation(
                        rule="voice_overlap",
                        voice1=voice_upper,
                        voice2=voice_lower,
                        position=i,
                        interval=Interval.between(prev_upper, curr_lower),
                        severity="warning",
                    )
                )

    return violations


def _check_leaps(
    pitches: list[Pitch | None],
    voice_name: str,
) -> list[VoiceLeadingViolation]:
    """Check for large leaps and augmented/diminished leaps within a single voice."""
    violations: list[VoiceLeadingViolation] = []

    for i in range(1, len(pitches)):
        prev = pitches[i - 1]
        curr = pitches[i]

        if prev is None or curr is None:
            continue

        interval = Interval.between(prev, curr)
        semitones = abs(interval.semitones)

        # Large leap: greater than an octave (>12 semitones)
        if semitones > 12:
            violations.append(
                VoiceLeadingViolation(
                    rule="large_leap",
                    voice1=voice_name,
                    voice2=voice_name,
                    position=i,
                    interval=interval,
                    severity="warning",
                )
            )

        # Augmented or diminished leap (non-zero)
        if interval.quality in ("A", "d") and semitones > 0:
            violations.append(
                VoiceLeadingViolation(
                    rule="augmented_leap",
                    voice1=voice_name,
                    voice2=voice_name,
                    position=i,
                    interval=interval,
                    severity="suggestion",
                )
            )

    return violations


# ---------------------------------------------------------------------------
# smooth_voice_leading
# ---------------------------------------------------------------------------


def smooth_voice_leading(
    chord1: tuple[Pitch, ...], chord2: tuple[Pitch, ...]
) -> tuple[Pitch, ...]:
    """Find the reordering of *chord2* that minimises total semitone movement.

    Each pitch in *chord1* is paired with exactly one pitch in the reordered
    *chord2*.  The function tries every permutation of *chord2* and returns the
    one whose summed absolute MIDI-number differences with *chord1* is smallest.

    Raises ``ValueError`` when the two chords have different sizes.
    """
    if len(chord1) != len(chord2):
        raise ValueError(
            f"Chord size mismatch: {len(chord1)} vs {len(chord2)}"
        )
    if len(chord1) == 0:
        return ()

    midi1 = tuple(p.midi_number for p in chord1)
    best: tuple[Pitch, ...] = chord2
    best_cost = sum(abs(a - b) for a, b in zip(midi1, (p.midi_number for p in chord2)))

    for perm in permutations(chord2):
        cost = sum(abs(a - p.midi_number) for a, p in zip(midi1, perm))
        if cost < best_cost:
            best_cost = cost
            best = perm  # type: ignore[assignment]

    return tuple(best)


# ---------------------------------------------------------------------------
# Public orchestrator
# ---------------------------------------------------------------------------


def check_voice_leading(score: Score) -> list[VoiceLeadingViolation]:
    """Check a multi-voice Score for all voice leading violations.

    Returns a list of VoiceLeadingViolation sorted by position.

    Checks performed:
    - Parallel fifths (error)
    - Parallel octaves/unisons (error)
    - Voice crossing (error)
    - Voice overlap (warning)
    - Large leaps >octave (warning)
    - Augmented/diminished leaps (suggestion)
    """
    if not score._voices:
        return []

    # Extract pitches for all voices
    voice_data: list[tuple[str, list[Pitch | None]]] = []
    for name, phrase in score._voices:
        voice_data.append((name, _extract_pitches(phrase)))

    violations: list[VoiceLeadingViolation] = []

    # Check all voice pairs (combinations, not permutations)
    for (name_a, pitches_a), (name_b, pitches_b) in itertools.combinations(
        voice_data, 2
    ):
        # First voice in pair is "upper" (earlier in Score order)
        violations.extend(
            _check_parallels(pitches_a, pitches_b, name_a, name_b, 7, "parallel_fifth")
        )
        violations.extend(
            _check_parallels(
                pitches_a, pitches_b, name_a, name_b, 0, "parallel_octave"
            )
        )
        violations.extend(_check_crossing(pitches_a, pitches_b, name_a, name_b))
        violations.extend(_check_overlap(pitches_a, pitches_b, name_a, name_b))

    # Check leaps for each individual voice
    for name, pitches in voice_data:
        violations.extend(_check_leaps(pitches, name))

    # Sort by position
    violations.sort(key=lambda v: v.position)

    return violations
