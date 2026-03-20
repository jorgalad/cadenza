"""Counterpoint validation: check_counterpoint and CounterpointViolation."""

from __future__ import annotations

from dataclasses import dataclass

from cadenza.core.interval import Interval
from cadenza.core.note import Note, Rest
from cadenza.core.phrase import Phrase
from cadenza.core.pitch import Pitch
from cadenza.counterpoint.rules import (
    DEFAULT_SEVERITIES,
    DISSONANCES,
    IMPERFECT_CONSONANCES,
    PERFECT_CONSONANCES,
    classify_interval,
)


@dataclass(frozen=True, slots=True)
class CounterpointViolation:
    """A single counterpoint violation.

    Attributes:
        rule: Type of violation (parallel_fifth, parallel_octave, etc.).
        species: Species number (1-5).
        position: 0-based note index where the violation occurs.
        interval: The Interval object at the violation point.
        severity: 'error', 'warning', or 'suggestion'.
    """

    rule: str
    species: int
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


def _check_cp_parallels(
    cf_pitches: list[Pitch | None],
    cp_pitches: list[Pitch | None],
    species: int,
    target_semitones_mod12: int,
    rule_name: str,
    severity: str,
) -> list[CounterpointViolation]:
    """Check for parallel motion at a specific interval (fifths or octaves)."""
    violations: list[CounterpointViolation] = []
    length = min(len(cf_pitches), len(cp_pitches))

    for i in range(1, length):
        prev_cf = cf_pitches[i - 1]
        curr_cf = cf_pitches[i]
        prev_cp = cp_pitches[i - 1]
        curr_cp = cp_pitches[i]

        if any(p is None for p in (prev_cf, curr_cf, prev_cp, curr_cp)):
            continue

        # Both voices must actually move
        if prev_cf.midi_number == curr_cf.midi_number:
            continue
        if prev_cp.midi_number == curr_cp.midi_number:
            continue

        # Check both intervals match target
        prev_interval_mod12 = abs(
            Interval.between(prev_cf, prev_cp).semitones
        ) % 12
        curr_interval_mod12 = abs(
            Interval.between(curr_cf, curr_cp).semitones
        ) % 12

        if prev_interval_mod12 != target_semitones_mod12:
            continue
        if curr_interval_mod12 != target_semitones_mod12:
            continue

        # Check same direction
        motion_cf = curr_cf.midi_number - prev_cf.midi_number
        motion_cp = curr_cp.midi_number - prev_cp.midi_number

        if (motion_cf > 0) != (motion_cp > 0):
            continue  # Contrary motion -- not parallel

        violations.append(
            CounterpointViolation(
                rule=rule_name,
                species=species,
                position=i,
                interval=Interval.between(curr_cf, curr_cp),
                severity=severity,
            )
        )

    return violations


def _check_cp_dissonance_on_beat(
    cf_pitches: list[Pitch | None],
    cp_pitches: list[Pitch | None],
    species: int,
    severity: str,
) -> list[CounterpointViolation]:
    """Check for dissonances on strong beats.

    For species 1, every note must be consonant.
    """
    violations: list[CounterpointViolation] = []
    length = min(len(cf_pitches), len(cp_pitches))

    for i in range(length):
        cf_p = cf_pitches[i]
        cp_p = cp_pitches[i]

        if cf_p is None or cp_p is None:
            continue

        interval_semitones = abs(
            Interval.between(cf_p, cp_p).semitones
        ) % 12

        if classify_interval(interval_semitones) == "dissonant":
            violations.append(
                CounterpointViolation(
                    rule="dissonance_on_beat",
                    species=species,
                    position=i,
                    interval=Interval.between(cf_p, cp_p),
                    severity=severity,
                )
            )

    return violations


def _check_cp_crossing(
    cf_pitches: list[Pitch | None],
    cp_pitches: list[Pitch | None],
    species: int,
    severity: str,
) -> list[CounterpointViolation]:
    """Check for voice crossing.

    Determines upper/lower by comparing the first available pair of pitches.
    If CP starts above CF, any position where CP goes below CF is a crossing
    (and vice versa).
    """
    violations: list[CounterpointViolation] = []
    length = min(len(cf_pitches), len(cp_pitches))

    # Determine which voice should be on top from first available pair
    cp_above: bool | None = None
    for i in range(length):
        if cf_pitches[i] is not None and cp_pitches[i] is not None:
            cp_above = cp_pitches[i].midi_number >= cf_pitches[i].midi_number
            break

    if cp_above is None:
        return violations

    for i in range(length):
        cf_p = cf_pitches[i]
        cp_p = cp_pitches[i]

        if cf_p is None or cp_p is None:
            continue

        if cp_above and cp_p.midi_number < cf_p.midi_number:
            violations.append(
                CounterpointViolation(
                    rule="voice_crossing",
                    species=species,
                    position=i,
                    interval=Interval.between(cf_p, cp_p),
                    severity=severity,
                )
            )
        elif not cp_above and cp_p.midi_number > cf_p.midi_number:
            violations.append(
                CounterpointViolation(
                    rule="voice_crossing",
                    species=species,
                    position=i,
                    interval=Interval.between(cf_p, cp_p),
                    severity=severity,
                )
            )

    return violations


def _check_cp_leaps(
    cp_pitches: list[Pitch | None],
    species: int,
    severity: str,
) -> list[CounterpointViolation]:
    """Check for large leaps (> 12 semitones) in the counterpoint."""
    violations: list[CounterpointViolation] = []

    for i in range(1, len(cp_pitches)):
        prev = cp_pitches[i - 1]
        curr = cp_pitches[i]

        if prev is None or curr is None:
            continue

        interval = Interval.between(prev, curr)
        semitones = abs(interval.semitones)

        if semitones > 12:
            violations.append(
                CounterpointViolation(
                    rule="large_leap",
                    species=species,
                    position=i,
                    interval=interval,
                    severity=severity,
                )
            )

    return violations


def _check_cp_repeated_notes(
    cp_pitches: list[Pitch | None],
    species: int,
    severity: str,
) -> list[CounterpointViolation]:
    """Check for repeated notes in the counterpoint."""
    violations: list[CounterpointViolation] = []

    for i in range(1, len(cp_pitches)):
        prev = cp_pitches[i - 1]
        curr = cp_pitches[i]

        if prev is None or curr is None:
            continue

        if prev.midi_number == curr.midi_number:
            violations.append(
                CounterpointViolation(
                    rule="repeated_note",
                    species=species,
                    position=i,
                    interval=Interval.between(prev, curr),
                    severity=severity,
                )
            )

    return violations


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def check_counterpoint(
    cf: Phrase,
    counterpoint: Phrase,
    species: int,
    rules: dict[str, str] | None = None,
) -> list[CounterpointViolation]:
    """Validate counterpoint against a cantus firmus.

    Args:
        cf: The cantus firmus phrase.
        counterpoint: The counterpoint phrase to validate.
        species: Species number (1-5).
        rules: Optional severity overrides. Keys are rule names,
               values are severity strings. Overrides DEFAULT_SEVERITIES
               for specified rules while preserving defaults for others.

    Returns:
        List of CounterpointViolation sorted by position.
    """
    # Build effective severity map
    effective: dict[str, str] = dict(DEFAULT_SEVERITIES)
    if rules is not None:
        effective.update(rules)

    # Extract pitches
    cf_pitches = _extract_pitches(cf)
    cp_pitches = _extract_pitches(counterpoint)

    violations: list[CounterpointViolation] = []

    # Parallel fifths and octaves
    violations.extend(
        _check_cp_parallels(
            cf_pitches, cp_pitches, species, 7, "parallel_fifth",
            effective["parallel_fifth"],
        )
    )
    violations.extend(
        _check_cp_parallels(
            cf_pitches, cp_pitches, species, 0, "parallel_octave",
            effective["parallel_octave"],
        )
    )

    # Dissonance on beat
    violations.extend(
        _check_cp_dissonance_on_beat(
            cf_pitches, cp_pitches, species,
            effective["dissonance_on_beat"],
        )
    )

    # Voice crossing
    violations.extend(
        _check_cp_crossing(
            cf_pitches, cp_pitches, species,
            effective["voice_crossing"],
        )
    )

    # Large leaps
    violations.extend(
        _check_cp_leaps(
            cp_pitches, species,
            effective["large_leap"],
        )
    )

    # Repeated notes
    violations.extend(
        _check_cp_repeated_notes(
            cp_pitches, species,
            effective["repeated_note"],
        )
    )

    # Sort by position
    violations.sort(key=lambda v: v.position)

    return violations
