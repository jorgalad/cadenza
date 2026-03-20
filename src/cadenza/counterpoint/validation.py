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
    For species 2, every other note (downbeats) must be consonant.
    For species 3, every 4th note (strong beats) must be consonant.
    For species 4, consonant syncopation or valid suspensions allowed.
    For species 5, per-beat validation based on rhythm.
    For species 0 (free), every note must be consonant.
    """
    violations: list[CounterpointViolation] = []
    n_cf = len(cf_pitches)
    n_cp = len(cp_pitches)

    if species == 2:
        # Check downbeats (even indices) against CF
        for cf_i in range(n_cf):
            cp_i = cf_i * 2  # downbeat
            if cp_i >= n_cp:
                break
            cf_p = cf_pitches[cf_i]
            cp_p = cp_pitches[cp_i]
            if cf_p is None or cp_p is None:
                continue
            interval_semitones = abs(Interval.between(cf_p, cp_p).semitones) % 12
            if classify_interval(interval_semitones) == "dissonant":
                violations.append(
                    CounterpointViolation(
                        rule="dissonance_on_beat",
                        species=species,
                        position=cf_i,
                        interval=Interval.between(cf_p, cp_p),
                        severity=severity,
                    )
                )
    elif species == 3:
        # Check first-of-four (indices 0,4,8...) against CF
        for cf_i in range(n_cf):
            cp_i = cf_i * 4
            if cp_i >= n_cp:
                break
            cf_p = cf_pitches[cf_i]
            cp_p = cp_pitches[cp_i]
            if cf_p is None or cp_p is None:
                continue
            interval_semitones = abs(Interval.between(cf_p, cp_p).semitones) % 12
            if classify_interval(interval_semitones) == "dissonant":
                violations.append(
                    CounterpointViolation(
                        rule="dissonance_on_beat",
                        species=species,
                        position=cf_i,
                        interval=Interval.between(cf_p, cp_p),
                        severity=severity,
                    )
                )
    elif species == 4:
        # Species 4: suspensions allowed (dissonance on beat is OK if resolved)
        # Skip dissonance_on_beat for species 4 -- handled by suspension check
        pass
    elif species == 5:
        # Species 5: per-beat validation -- check alignment with CF
        # For simplicity, validate 1:1 alignment if same length
        if n_cp == n_cf:
            for i in range(min(n_cf, n_cp)):
                cf_p = cf_pitches[i]
                cp_p = cp_pitches[i]
                if cf_p is None or cp_p is None:
                    continue
                interval_semitones = abs(Interval.between(cf_p, cp_p).semitones) % 12
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
        # For mixed lengths, skip (florid rhythm makes beat alignment complex)
    else:
        # Species 1, 0 (free): every note must be consonant (1:1)
        length = min(n_cf, n_cp)
        for i in range(length):
            cf_p = cf_pitches[i]
            cp_p = cp_pitches[i]
            if cf_p is None or cp_p is None:
                continue
            interval_semitones = abs(Interval.between(cf_p, cp_p).semitones) % 12
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


def _check_cp_unresolved_suspension(
    cf_pitches: list[Pitch | None],
    cp_pitches: list[Pitch | None],
    species: int,
    severity: str,
) -> list[CounterpointViolation]:
    """Check for unresolved suspensions in species 4 counterpoint.

    A suspension occurs when a held CP note is dissonant with the new CF note.
    It must resolve stepwise downward (if above CF) or upward (if below CF).
    """
    violations: list[CounterpointViolation] = []
    length = min(len(cf_pitches), len(cp_pitches))

    if length < 2:
        return violations

    # Determine voice direction from first pair
    cp_above: bool | None = None
    for i in range(length):
        if cf_pitches[i] is not None and cp_pitches[i] is not None:
            cp_above = cp_pitches[i].midi_number >= cf_pitches[i].midi_number
            break

    if cp_above is None:
        return violations

    for i in range(length - 1):
        cf_p = cf_pitches[i]
        cp_p = cp_pitches[i]
        cp_next = cp_pitches[i + 1]

        if cf_p is None or cp_p is None or cp_next is None:
            continue

        interval_semitones = abs(Interval.between(cf_p, cp_p).semitones) % 12
        if classify_interval(interval_semitones) != "dissonant":
            continue

        # This is a suspension -- check resolution
        cp_midi = cp_p.midi_number
        next_midi = cp_next.midi_number

        if cp_above:
            # Above CF: resolve stepwise downward (1-2 semitones down)
            step_down = cp_midi - next_midi
            resolved = 1 <= step_down <= 2
        else:
            # Below CF: resolve stepwise upward
            step_up = next_midi - cp_midi
            resolved = 1 <= step_up <= 2

        if not resolved:
            violations.append(
                CounterpointViolation(
                    rule="unresolved_suspension",
                    species=species,
                    position=i,
                    interval=Interval.between(cf_p, cp_p),
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

    # For species 2/3/5, extract downbeat-aligned pitches for parallel checks
    if species == 2:
        # Map CP downbeats to CF positions for parallel checking
        cp_downbeats = [cp_pitches[i * 2] if i * 2 < len(cp_pitches) else None
                        for i in range(len(cf_pitches))]
    elif species == 3:
        cp_downbeats = [cp_pitches[i * 4] if i * 4 < len(cp_pitches) else None
                        for i in range(len(cf_pitches))]
    elif species == 5 and len(cp_pitches) != len(cf_pitches):
        # Species 5 (florid): mixed-length output; skip alignment-dependent checks
        # Only run large_leap and repeated_note checks
        violations.extend(
            _check_cp_leaps(cp_pitches, species, effective["large_leap"])
        )
        violations.extend(
            _check_cp_repeated_notes(cp_pitches, species, effective["repeated_note"])
        )
        violations.sort(key=lambda v: v.position)
        return violations
    else:
        cp_downbeats = cp_pitches

    # Parallel fifths and octaves (on strong beats)
    violations.extend(
        _check_cp_parallels(
            cf_pitches, cp_downbeats, species, 7, "parallel_fifth",
            effective["parallel_fifth"],
        )
    )
    violations.extend(
        _check_cp_parallels(
            cf_pitches, cp_downbeats, species, 0, "parallel_octave",
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

    # Voice crossing (on strong beats)
    violations.extend(
        _check_cp_crossing(
            cf_pitches, cp_downbeats, species,
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

    # Repeated notes (skip for species 0/free -- more relaxed)
    if species != 0:
        violations.extend(
            _check_cp_repeated_notes(
                cp_pitches, species,
                effective["repeated_note"],
            )
        )

    # Unresolved suspensions (species 4)
    if species == 4:
        violations.extend(
            _check_cp_unresolved_suspension(
                cf_pitches, cp_pitches, species,
                effective["unresolved_suspension"],
            )
        )

    # Sort by position
    violations.sort(key=lambda v: v.position)

    return violations
