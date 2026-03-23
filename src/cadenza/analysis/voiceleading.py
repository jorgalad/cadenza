"""Voice leading violation detection for multi-voice scores.

Detects parallel fifths, parallel octaves, voice crossing, voice overlap,
large leaps, and augmented/diminished leaps across all voice pairs in a Score.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from itertools import permutations

from cadenza.core.interval import Interval
from cadenza.core.note import Note, Rest
from cadenza.core.phrase import Phrase
from cadenza.core.pitch import Pitch
from cadenza.core.score import Score
from cadenza.theory.scales import Scale
from cadenza.transforms.pitch import from_midi


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
# generate_inner_voices
# ---------------------------------------------------------------------------

# Consonant interval classes (semitones mod 12)
_CONSONANCES_MOD12 = frozenset({0, 3, 4, 5, 7, 8, 9})

_DEFAULT_RANGES: list[tuple[Pitch, Pitch]] = [
    (Pitch("g", "n", 3), Pitch("c", "n", 5)),   # Alto:  G3–C5
    (Pitch("c", "n", 3), Pitch("g", "n", 4)),   # Tenor: C3–G4
]


def generate_inner_voices(
    soprano: Phrase,
    bass: Phrase,
    n: int = 2,
    ranges: list[tuple[Pitch, Pitch]] | None = None,
    scale: Scale | None = None,
) -> list[Phrase]:
    """Generate *n* inner voice Phrases between *soprano* and *bass*.

    Beat-by-beat greedy voice leading:
    1. For each beat, collect pitches in the voice's range that are consonant
       with the bass.
    2. Score each candidate: prefer close motion from the previous note,
       prefer completing the chord with the 3rd above the bass, and avoid
       doubling the soprano or crowding other inner voices.
    3. Pick the lowest-cost candidate.

    Default ranges for n=2: alto G3–C5, tenor C3–G4.
    Returns a list of Phrases ordered highest range first (alto before tenor).

    When *scale* is provided, candidates are penalised for pitches outside
    the scale and spelled with key-correct accidentals.

    Raises ``ValueError`` when custom *ranges* length does not match *n*.
    """
    if ranges is not None:
        if len(ranges) != n:
            raise ValueError(f"Expected {n} ranges, got {len(ranges)}")
        voice_ranges = list(ranges)
    else:
        if n <= len(_DEFAULT_RANGES):
            voice_ranges = _DEFAULT_RANGES[:n]
        else:
            voice_ranges = list(_DEFAULT_RANGES)
            for _ in range(n - len(_DEFAULT_RANGES)):
                voice_ranges.append(_DEFAULT_RANGES[-1])

    voice_midi_ranges = [
        (lo.midi_number, hi.midi_number) for lo, hi in voice_ranges
    ]

    # Build key-aware pitch-class map if a scale is provided
    scale_pcs: frozenset[int] | None = None
    pc_to_pitch: dict[int, tuple[str, str]] = {}
    if scale is not None:
        scale_pcs = frozenset(p.midi_number % 12 for p in scale.pitches)
        pc_to_pitch = {p.midi_number % 12: (p.step, p.accidental) for p in scale.pitches}

    def _spell(midi: int, prefer_sharps: bool) -> Pitch:
        """Return a key-correctly spelled Pitch for a MIDI number."""
        pc = midi % 12
        octave = (midi // 12) - 1
        if pc in pc_to_pitch:
            step, acc = pc_to_pitch[pc]
            return Pitch(step=step, accidental=acc, octave=octave)
        return from_midi(midi, prefer_sharps=prefer_sharps)

    soprano_pitches = _extract_pitches(soprano)
    bass_pitches = _extract_pitches(bass)
    beat_count = min(len(soprano), len(bass))

    # Start each voice near the middle of its range
    prev_midis = [(lo + hi) // 2 for lo, hi in voice_midi_ranges]

    voices: list[list[Note | Rest]] = [[] for _ in range(n)]

    for i in range(beat_count):
        dur = soprano[i].duration if i < len(soprano) else bass[i].duration
        sp = soprano_pitches[i] if i < len(soprano_pitches) else None
        bp = bass_pitches[i] if i < len(bass_pitches) else None

        # Rest beats: all inner voices rest
        if sp is None or bp is None:
            for v in range(n):
                voices[v].append(Rest(duration=dur))
            continue

        sp_midi = sp.midi_number
        bp_midi = bp.midi_number
        sp_pc = sp_midi % 12
        bp_pc = bp_midi % 12
        # Chord tones to prefer: minor and major 3rd above bass, perfect 5th
        third_pcs = {(bp_pc + 3) % 12, (bp_pc + 4) % 12}
        fifth_pc = (bp_pc + 7) % 12

        assigned_midis: list[int] = []  # inner voices already placed this beat

        for v in range(n):
            lo, hi = voice_midi_ranges[v]
            prev = prev_midis[v]

            candidates: list[tuple[float, int]] = []

            for midi in range(lo, hi + 1):
                bp_int = abs(midi - bp_midi) % 12
                # Must be consonant with bass
                if bp_int not in _CONSONANCES_MOD12:
                    continue

                pc = midi % 12
                # Prefer chord-tone completion: the 3rd is most important
                score: float = abs(midi - prev)  # smooth voice leading base cost

                if pc in third_pcs:
                    score -= 4.0   # strongly prefer 3rd of the chord
                elif pc == fifth_pc and fifth_pc not in (sp_pc, bp_pc):
                    score -= 1.5   # prefer 5th when it adds a new colour
                elif pc == sp_pc:
                    score += 2.0   # mild penalty for doubling soprano
                elif pc == bp_pc:
                    score += 1.0   # mild penalty for doubling bass root

                # Penalise out-of-key pitches when scale is given
                if scale_pcs is not None and pc not in scale_pcs:
                    score += 8.0

                # Avoid crowding or octave-doubling other inner voices
                for am in assigned_midis:
                    dist = abs(midi - am)
                    if dist == 0 or dist % 12 == 0:
                        score += 6.0   # octave doubling between inner voices
                    elif dist < 3:
                        score += 3.0   # too close together (< minor 3rd)

                candidates.append((score, midi))

            if not candidates:
                # Fallback: any pitch consonant with soprano instead
                for midi in range(lo, hi + 1):
                    sp_int = abs(midi - sp_midi) % 12
                    if sp_int in _CONSONANCES_MOD12:
                        candidates.append((abs(midi - prev), midi))

            if candidates:
                candidates.sort()
                chosen_midi = candidates[0][1]
            else:
                chosen_midi = max(lo, min(hi, prev))

            prev_midis[v] = chosen_midi
            assigned_midis.append(chosen_midi)
            pitch = _spell(chosen_midi, prefer_sharps=(v == 0))
            voices[v].append(
                Note(pitch=pitch, duration=dur, dynamic=None, articulations=())
            )

    return [tuple(v) for v in voices]


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
