"""Counterpoint generation: species I-V and free counterpoint."""

from __future__ import annotations

import builtins
import random
from fractions import Fraction

from cadenza.core.duration import Duration
from cadenza.core.interval import Interval
from cadenza.core.note import Note, Rest
from cadenza.core.phrase import Phrase
from cadenza.core.pitch import Pitch
from cadenza.counterpoint._engine import _backtrack
from cadenza.counterpoint.rules import (
    DISSONANCES,
    IMPERFECT_CONSONANCES,
    PERFECT_CONSONANCES,
    classify_interval,
)
from cadenza.theory.scales import Scale
from cadenza.transforms.pitch import from_midi


# All consonant intervals (mod 12)
_CONSONANCES = PERFECT_CONSONANCES | IMPERFECT_CONSONANCES


def _build_pc_map(scale: Scale) -> dict[int, tuple[str, str]]:
    """Map pitch class (0-11) -> (step, accidental) from a Scale for key-aware spelling."""
    return {p.midi_number % 12: (p.step, p.accidental) for p in scale.pitches}


def _pitch_for_midi(
    midi: int,
    pc_map: dict[int, tuple[str, str]],
    prefer_sharps: bool,
) -> Pitch:
    """Return a Pitch with key-correct spelling, falling back to from_midi."""
    pc = midi % 12
    octave = (midi // 12) - 1
    if pc in pc_map:
        step, acc = pc_map[pc]
        return Pitch(step=step, accidental=acc, octave=octave)
    return from_midi(midi, prefer_sharps=prefer_sharps)

# Duration base halving maps
_HALF_BASE: dict[str, str] = {
    "w": "h", "h": "q", "q": "e", "e": "s", "s": "t", "t": "x",
}

_QUARTER_BASE: dict[str, str] = {
    "w": "q", "h": "e", "q": "s", "e": "t",
}


def _extract_cf(cf: Phrase) -> tuple[list[Pitch], list[Duration]]:
    """Extract pitches and durations from a cantus firmus phrase."""
    if not cf:
        raise ValueError("Cantus firmus must not be empty")
    pitches: list[Pitch] = []
    durations: list[Duration] = []
    for event in cf:
        if isinstance(event, Note):
            pitches.append(event.pitch)
            durations.append(event.duration)
        else:
            pitches.append(Pitch("c", "n", 4))  # placeholder
            durations.append(event.duration)
    if not pitches:
        raise ValueError("Cantus firmus contains no notes")
    return pitches, durations


def _compute_range(
    cf_pitches: list[Pitch],
    above: bool,
    range: tuple[Pitch, Pitch] | None,  # noqa: A002
) -> tuple[int, int]:
    """Compute MIDI range for candidate generation."""
    cf_midis = [p.midi_number for p in cf_pitches]
    cf_min = min(cf_midis)
    cf_max = max(cf_midis)

    if range is not None:
        return range[0].midi_number, range[1].midi_number
    elif above:
        return cf_min, cf_max + 16
    else:
        # Bass: practical register anchored ~one octave below the median pitch.
        # E2–E4 (MIDI 40–64) is the standard bass range.
        # Note-by-note, each candidate is still filtered to sit at or below the
        # current CF pitch, so no upper-ceiling based on cf_min is needed here.
        cf_median = sorted(cf_midis)[len(cf_midis) // 2]
        bass_center = max(40, min(52, cf_median - 12))  # E2–E3 center
        bass_low    = max(28, bass_center - 12)          # no lower than E1
        bass_high   = min(64, bass_center + 12)          # no higher than E4
        return bass_low, bass_high


# ---------------------------------------------------------------------------
# First species
# ---------------------------------------------------------------------------


def generate_first_species(
    cf: Phrase,
    above: bool = True,
    range: tuple[Pitch, Pitch] | None = None,  # noqa: A002
    scale: Scale | None = None,
) -> Phrase:
    """Generate first species counterpoint against a cantus firmus.

    Args:
        cf: The cantus firmus phrase (tuple of Note/Rest events).
        above: If True, generate counterpoint above CF; if False, below.
        range: Optional (low_pitch, high_pitch) to constrain output.
        scale: When provided, candidates are strongly biased toward scale
               pitches and spelled with key-correct accidentals.

    Returns:
        A Phrase of the same length as cf with valid first species counterpoint.

    Raises:
        ValueError: If cf is empty or no valid counterpoint can be found.
    """
    cf_pitches, cf_durations = _extract_cf(cf)
    low_midi, high_midi = _compute_range(cf_pitches, above, range)
    n_notes = len(cf_pitches)
    prefer_sharps = above

    scale_pcs: frozenset[int] | None = None
    pc_map: dict[int, tuple[str, str]] = {}
    if scale is not None:
        scale_pcs = frozenset(p.midi_number % 12 for p in scale.pitches)
        pc_map = _build_pc_map(scale)

    def _candidates(position: int, partial: list[Pitch], cf_pitch: Pitch) -> list[Pitch]:
        cf_midi = cf_pitch.midi_number
        results: list[tuple[int, int, Pitch]] = []

        for midi in builtins.range(low_midi, high_midi + 1):
            interval_mod12 = abs(midi - cf_midi) % 12

            if interval_mod12 not in _CONSONANCES:
                continue
            if above and midi < cf_midi:
                continue
            if not above and midi > cf_midi:
                continue
            if (position == 0 or position == n_notes - 1):
                if interval_mod12 not in PERFECT_CONSONANCES:
                    continue

            priority = 0
            if interval_mod12 in IMPERFECT_CONSONANCES:
                priority -= 1
            if partial:
                step_dist = abs(midi - partial[-1].midi_number)
                if step_dist <= 2:
                    priority -= 3
                elif step_dist <= 4:
                    priority -= 1
            # Strongly prefer diatonic pitches when a scale is given
            if scale_pcs is not None and midi % 12 not in scale_pcs:
                priority += 8

            pitch = _pitch_for_midi(midi, pc_map, prefer_sharps)
            results.append((priority, midi, pitch))

        random.shuffle(results)
        results.sort(key=lambda x: x[0])
        return [r[2] for r in results]

    def _validate(position: int, partial: list[Pitch], candidate: Pitch, cf_pitch: Pitch) -> bool:
        cf_midi = cf_pitch.midi_number
        cand_midi = candidate.midi_number

        if position > 0:
            prev_cp = partial[-1]
            prev_cf = cf_pitches[position - 1]
            prev_cp_midi = prev_cp.midi_number
            prev_cf_midi = prev_cf.midi_number

            prev_interval_mod12 = abs(prev_cp_midi - prev_cf_midi) % 12
            curr_interval_mod12 = abs(cand_midi - cf_midi) % 12

            if prev_interval_mod12 == curr_interval_mod12 and prev_interval_mod12 in (0, 7):
                motion_cf = cf_midi - prev_cf_midi
                motion_cp = cand_midi - prev_cp_midi
                if motion_cf != 0 and motion_cp != 0:
                    if (motion_cf > 0) == (motion_cp > 0):
                        return False

            if above and cand_midi < cf_midi:
                return False
            if not above and cand_midi > cf_midi:
                return False

            if cand_midi == prev_cp_midi:
                return False

            if len(partial) >= 3:
                consecutive_imperfect = 0
                for j in builtins.range(len(partial) - 1, max(len(partial) - 4, -1), -1):
                    if j < 0:
                        break
                    itv = abs(partial[j].midi_number - cf_pitches[j].midi_number) % 12
                    if itv in IMPERFECT_CONSONANCES:
                        consecutive_imperfect += 1
                    else:
                        break
                if consecutive_imperfect >= 3 and curr_interval_mod12 in IMPERFECT_CONSONANCES:
                    return False

        if position == n_notes - 2 and n_notes >= 2:
            last_cf = cf_pitches[n_notes - 1]
            last_cf_midi = last_cf.midi_number
            has_valid_step_final = False
            for final_midi in builtins.range(low_midi, high_midi + 1):
                final_mod12 = abs(final_midi - last_cf_midi) % 12
                if final_mod12 not in PERFECT_CONSONANCES:
                    continue
                if above and final_midi < last_cf_midi:
                    continue
                if not above and final_midi > last_cf_midi:
                    continue
                step_dist = abs(final_midi - cand_midi)
                if step_dist <= 2:
                    has_valid_step_final = True
                    break
            if not has_valid_step_final:
                return False

        return True

    result = _backtrack(cf_pitches, _candidates, _validate, 0, [])
    if result is None:
        raise ValueError("No valid first species counterpoint found")

    events: list[Note] = []
    for i, pitch in enumerate(result):
        events.append(Note(pitch=pitch, duration=cf_durations[i], dynamic=None, articulations=()))
    return tuple(events)


# ---------------------------------------------------------------------------
# Second species
# ---------------------------------------------------------------------------


def generate_second_species(
    cf: Phrase,
    above: bool = True,
    range: tuple[Pitch, Pitch] | None = None,  # noqa: A002
) -> Phrase:
    """Generate second species counterpoint (2 CP notes per CF note).

    Downbeats are consonant; offbeats may be passing tones.
    """
    cf_pitches, cf_durations = _extract_cf(cf)
    low_midi, high_midi = _compute_range(cf_pitches, above, range)
    n_cf = len(cf_pitches)
    n_positions = 2 * n_cf
    prefer_sharps = above

    def _cf_index(pos: int) -> int:
        return pos // 2

    def _is_downbeat(pos: int) -> bool:
        return pos % 2 == 0

    def _candidates(position: int, partial: list[Pitch], cf_pitch: Pitch) -> list[Pitch]:
        cf_idx = _cf_index(position)
        cf_midi = cf_pitches[cf_idx].midi_number
        results: list[tuple[int, int, Pitch]] = []

        for midi in builtins.range(low_midi, high_midi + 1):
            interval_mod12 = abs(midi - cf_midi) % 12

            if above and midi < cf_midi:
                continue
            if not above and midi > cf_midi:
                continue

            if _is_downbeat(position):
                # Downbeats must be consonant
                if interval_mod12 not in _CONSONANCES:
                    continue
                # First and last downbeats: perfect consonance
                if (position == 0 or position == n_positions - 2):
                    if interval_mod12 not in PERFECT_CONSONANCES:
                        continue
            else:
                # Offbeats: consonant OR stepwise from previous (passing tone)
                if interval_mod12 not in _CONSONANCES:
                    # Dissonant offbeat: must be stepwise from previous
                    if partial:
                        step = abs(midi - partial[-1].midi_number)
                        if step > 2:
                            continue
                    else:
                        continue

            priority = 0
            if interval_mod12 in IMPERFECT_CONSONANCES:
                priority -= 1
            if partial:
                step_dist = abs(midi - partial[-1].midi_number)
                if step_dist <= 2:
                    priority -= 3
                elif step_dist <= 4:
                    priority -= 1

            pitch = from_midi(midi, prefer_sharps=prefer_sharps)
            results.append((priority, midi, pitch))

        random.shuffle(results)
        results.sort(key=lambda x: x[0])
        return [r[2] for r in results]

    def _validate(position: int, partial: list[Pitch], candidate: Pitch, cf_pitch: Pitch) -> bool:
        cf_idx = _cf_index(position)
        cf_midi = cf_pitches[cf_idx].midi_number
        cand_midi = candidate.midi_number

        if above and cand_midi < cf_midi:
            return False
        if not above and cand_midi > cf_midi:
            return False

        if partial:
            if cand_midi == partial[-1].midi_number:
                return False

        # No parallel 5ths/8ths between consecutive downbeats
        if _is_downbeat(position) and position >= 2:
            prev_db_idx = position - 2  # previous downbeat
            prev_db_cf_idx = _cf_index(prev_db_idx)
            prev_cp_midi = partial[prev_db_idx].midi_number
            prev_cf_midi = cf_pitches[prev_db_cf_idx].midi_number

            prev_interval = abs(prev_cp_midi - prev_cf_midi) % 12
            curr_interval = abs(cand_midi - cf_midi) % 12

            if prev_interval == curr_interval and prev_interval in (0, 7):
                motion_cf = cf_midi - prev_cf_midi
                motion_cp = cand_midi - prev_cp_midi
                if motion_cf != 0 and motion_cp != 0:
                    if (motion_cf > 0) == (motion_cp > 0):
                        return False

        # Offbeat dissonance: must be approached and left by step in same direction
        if not _is_downbeat(position):
            interval_mod12 = abs(cand_midi - cf_midi) % 12
            if interval_mod12 in DISSONANCES and partial:
                step_from_prev = abs(cand_midi - partial[-1].midi_number)
                if step_from_prev > 2:
                    return False

        return True

    # Use expanded backtrack engine
    expanded_cf = []
    for p in cf_pitches:
        expanded_cf.append(p)
        expanded_cf.append(p)  # each CF note maps to 2 positions

    result = _backtrack(expanded_cf, _candidates, _validate, 0, [])
    if result is None:
        raise ValueError("No valid second species counterpoint found")

    # Build phrase with halved durations
    events: list[Note] = []
    for i, pitch in enumerate(result):
        cf_idx = i // 2
        cf_dur = cf_durations[cf_idx]
        if cf_dur.base in _HALF_BASE:
            half_base = _HALF_BASE[cf_dur.base]
            cp_dur = Duration.from_cn(half_base, dots=0)
        else:
            cp_dur = Duration(fraction=cf_dur.fraction / 2, base=cf_dur.base)
        events.append(Note(pitch=pitch, duration=cp_dur, dynamic=None, articulations=()))
    return tuple(events)


# ---------------------------------------------------------------------------
# Third species
# ---------------------------------------------------------------------------


def generate_third_species(
    cf: Phrase,
    above: bool = True,
    range: tuple[Pitch, Pitch] | None = None,  # noqa: A002
) -> Phrase:
    """Generate third species counterpoint (4 CP notes per CF note).

    First-of-four must be consonant; others may be passing/neighbor/cambiata.
    """
    cf_pitches, cf_durations = _extract_cf(cf)
    low_midi, high_midi = _compute_range(cf_pitches, above, range)
    n_cf = len(cf_pitches)
    n_positions = 4 * n_cf
    prefer_sharps = above

    def _cf_index(pos: int) -> int:
        return pos // 4

    def _is_strong(pos: int) -> bool:
        return pos % 4 == 0

    def _candidates(position: int, partial: list[Pitch], cf_pitch: Pitch) -> list[Pitch]:
        cf_idx = _cf_index(position)
        cf_midi = cf_pitches[cf_idx].midi_number
        results: list[tuple[int, int, Pitch]] = []

        for midi in builtins.range(low_midi, high_midi + 1):
            interval_mod12 = abs(midi - cf_midi) % 12

            if above and midi < cf_midi:
                continue
            if not above and midi > cf_midi:
                continue

            if _is_strong(position):
                # Strong beats: consonant only
                if interval_mod12 not in _CONSONANCES:
                    continue
                # First and last strong beats: perfect consonance
                if (position == 0 or position == n_positions - 4):
                    if interval_mod12 not in PERFECT_CONSONANCES:
                        continue
            else:
                # Weak beats: consonant or stepwise dissonance
                if interval_mod12 not in _CONSONANCES:
                    if partial:
                        step = abs(midi - partial[-1].midi_number)
                        if step > 2:
                            continue
                    else:
                        continue

            priority = 0
            if partial:
                step_dist = abs(midi - partial[-1].midi_number)
                if step_dist <= 2:
                    priority -= 3
                elif step_dist <= 4:
                    priority -= 1

            pitch = from_midi(midi, prefer_sharps=prefer_sharps)
            results.append((priority, midi, pitch))

        random.shuffle(results)
        results.sort(key=lambda x: x[0])
        return [r[2] for r in results]

    def _validate(position: int, partial: list[Pitch], candidate: Pitch, cf_pitch: Pitch) -> bool:
        cf_idx = _cf_index(position)
        cf_midi = cf_pitches[cf_idx].midi_number
        cand_midi = candidate.midi_number

        if above and cand_midi < cf_midi:
            return False
        if not above and cand_midi > cf_midi:
            return False

        if partial and cand_midi == partial[-1].midi_number:
            return False

        # No parallel 5ths/8ths on consecutive strong beats
        if _is_strong(position) and position >= 4:
            prev_strong_idx = position - 4
            prev_cf_idx = _cf_index(prev_strong_idx)
            prev_cp_midi = partial[prev_strong_idx].midi_number
            prev_cf_midi = cf_pitches[prev_cf_idx].midi_number

            prev_interval = abs(prev_cp_midi - prev_cf_midi) % 12
            curr_interval = abs(cand_midi - cf_midi) % 12

            if prev_interval == curr_interval and prev_interval in (0, 7):
                motion_cf = cf_midi - prev_cf_midi
                motion_cp = cand_midi - prev_cp_midi
                if motion_cf != 0 and motion_cp != 0:
                    if (motion_cf > 0) == (motion_cp > 0):
                        return False

        return True

    # Expand CF: each CF note maps to 4 positions
    expanded_cf = []
    for p in cf_pitches:
        for _ in builtins.range(4):
            expanded_cf.append(p)

    result = _backtrack(expanded_cf, _candidates, _validate, 0, [])
    if result is None:
        raise ValueError("No valid third species counterpoint found")

    events: list[Note] = []
    for i, pitch in enumerate(result):
        cf_idx = i // 4
        cf_dur = cf_durations[cf_idx]
        if cf_dur.base in _QUARTER_BASE:
            q_base = _QUARTER_BASE[cf_dur.base]
            cp_dur = Duration.from_cn(q_base, dots=0)
        else:
            cp_dur = Duration(fraction=cf_dur.fraction / 4, base=cf_dur.base)
        events.append(Note(pitch=pitch, duration=cp_dur, dynamic=None, articulations=()))
    return tuple(events)


# ---------------------------------------------------------------------------
# Fourth species
# ---------------------------------------------------------------------------


def generate_fourth_species(
    cf: Phrase,
    above: bool = True,
    range: tuple[Pitch, Pitch] | None = None,  # noqa: A002
) -> Phrase:
    """Generate fourth species counterpoint (syncopated, with suspensions).

    Same number of notes as CF. Suspensions (dissonances) resolve stepwise downward.
    """
    cf_pitches, cf_durations = _extract_cf(cf)
    low_midi, high_midi = _compute_range(cf_pitches, above, range)
    n_cf = len(cf_pitches)
    prefer_sharps = above

    def _candidates(position: int, partial: list[Pitch], cf_pitch: Pitch) -> list[Pitch]:
        cf_midi = cf_pitch.midi_number
        results: list[tuple[int, int, Pitch]] = []

        # Check if previous note is a suspension that needs resolving
        must_resolve_from: int | None = None
        if position > 0:
            prev_cp_midi = partial[-1].midi_number
            prev_interval_with_curr_cf = abs(prev_cp_midi - cf_midi) % 12
            if prev_interval_with_curr_cf in DISSONANCES:
                must_resolve_from = prev_cp_midi

        for midi in builtins.range(low_midi, high_midi + 1):
            interval_mod12 = abs(midi - cf_midi) % 12

            if above and midi < cf_midi:
                continue
            if not above and midi > cf_midi:
                continue

            # If previous note is a suspension, this note MUST resolve stepwise down
            if must_resolve_from is not None:
                if above:
                    step_down = must_resolve_from - midi
                    if not (1 <= step_down <= 2):
                        continue
                else:
                    step_up = midi - must_resolve_from
                    if not (1 <= step_up <= 2):
                        continue
                # Resolution must be consonant
                if interval_mod12 not in _CONSONANCES:
                    continue
            else:
                # First and last must be consonant and perfect
                if position == 0 or position == n_cf - 1:
                    if interval_mod12 not in PERFECT_CONSONANCES:
                        continue
                else:
                    # Allow consonant notes, or dissonant if they can be a
                    # valid suspension (same pitch as previous = held note)
                    if interval_mod12 in DISSONANCES:
                        # Only allow if this is a held note from previous position
                        if not partial or midi != partial[-1].midi_number:
                            continue
                        # And there must be room to resolve after this
                        if position >= n_cf - 1:
                            continue

            priority = 0
            if interval_mod12 in IMPERFECT_CONSONANCES:
                priority -= 1
            if partial:
                step_dist = abs(midi - partial[-1].midi_number)
                if step_dist <= 2:
                    priority -= 3
                elif step_dist <= 4:
                    priority -= 1
                # Encourage suspensions (held notes) occasionally
                if midi == partial[-1].midi_number and interval_mod12 in DISSONANCES:
                    priority -= 2  # Encourage suspensions

            pitch = from_midi(midi, prefer_sharps=prefer_sharps)
            results.append((priority, midi, pitch))

        random.shuffle(results)
        results.sort(key=lambda x: x[0])
        return [r[2] for r in results]

    def _validate(position: int, partial: list[Pitch], candidate: Pitch, cf_pitch: Pitch) -> bool:
        cf_midi = cf_pitch.midi_number
        cand_midi = candidate.midi_number

        if above and cand_midi < cf_midi:
            return False
        if not above and cand_midi > cf_midi:
            return False

        if position > 0:
            prev_cp_midi = partial[-1].midi_number
            prev_cf_midi = cf_pitches[position - 1].midi_number

            # No parallel 5ths/8ths
            prev_interval = abs(prev_cp_midi - prev_cf_midi) % 12
            curr_interval = abs(cand_midi - cf_midi) % 12

            if prev_interval == curr_interval and prev_interval in (0, 7):
                motion_cf = cf_midi - prev_cf_midi
                motion_cp = cand_midi - prev_cp_midi
                if motion_cf != 0 and motion_cp != 0:
                    if (motion_cf > 0) == (motion_cp > 0):
                        return False

        return True

    result = _backtrack(cf_pitches, _candidates, _validate, 0, [])
    if result is None:
        raise ValueError("No valid fourth species counterpoint found")

    events: list[Note] = []
    for i, pitch in enumerate(result):
        events.append(Note(pitch=pitch, duration=cf_durations[i], dynamic=None, articulations=()))
    return tuple(events)


# ---------------------------------------------------------------------------
# Fifth species (florid)
# ---------------------------------------------------------------------------


def generate_fifth_species(
    cf: Phrase,
    above: bool = True,
    range: tuple[Pitch, Pitch] | None = None,  # noqa: A002
) -> Phrase:
    """Generate fifth species (florid) counterpoint mixing rhythmic values.

    Combines patterns from species I-IV with at least 2 different durations.
    """
    cf_pitches, cf_durations = _extract_cf(cf)
    low_midi, high_midi = _compute_range(cf_pitches, above, range)
    n_cf = len(cf_pitches)
    prefer_sharps = above

    # For each CF beat, choose a rhythmic pattern
    # Patterns: 1 = whole (1 note), 2 = half (2 notes), 4 = quarter (4 notes)
    # Ensure at least 2 different patterns
    patterns: list[int] = []
    for i in builtins.range(n_cf):
        if i == 0 or i == n_cf - 1:
            patterns.append(1)  # Whole notes at start and end
        elif i == n_cf // 2:
            patterns.append(4)  # Quarters in the middle for variety
        else:
            patterns.append(random.choice([1, 2, 2, 4]))

    # Ensure variety: at least 2 different patterns
    if len(set(patterns)) < 2 and n_cf > 2:
        # Force at least one different pattern
        mid = n_cf // 2
        if patterns[mid] == 1:
            patterns[mid] = 2
        else:
            patterns[mid] = 1

    # Build all CP notes with their CF alignment
    all_notes: list[Note] = []
    for cf_idx in builtins.range(n_cf):
        pattern = patterns[cf_idx]
        cf_midi = cf_pitches[cf_idx].midi_number
        cf_dur = cf_durations[cf_idx]

        # Generate notes for this beat
        if pattern == 1:
            # Single note: use first species approach (consonant)
            beat_result = _generate_beat_notes(
                cf_pitches, cf_idx, 1, above, low_midi, high_midi, prefer_sharps,
                all_notes,
            )
            for pitch in beat_result:
                all_notes.append(Note(pitch=pitch, duration=cf_dur, dynamic=None, articulations=()))
        elif pattern == 2:
            # Two notes: halved duration
            if cf_dur.base in _HALF_BASE:
                half_dur = Duration.from_cn(_HALF_BASE[cf_dur.base])
            else:
                half_dur = Duration(fraction=cf_dur.fraction / 2, base=cf_dur.base)
            beat_result = _generate_beat_notes(
                cf_pitches, cf_idx, 2, above, low_midi, high_midi, prefer_sharps,
                all_notes,
            )
            for pitch in beat_result:
                all_notes.append(Note(pitch=pitch, duration=half_dur, dynamic=None, articulations=()))
        else:  # pattern == 4
            if cf_dur.base in _QUARTER_BASE:
                q_dur = Duration.from_cn(_QUARTER_BASE[cf_dur.base])
            else:
                q_dur = Duration(fraction=cf_dur.fraction / 4, base=cf_dur.base)
            beat_result = _generate_beat_notes(
                cf_pitches, cf_idx, 4, above, low_midi, high_midi, prefer_sharps,
                all_notes,
            )
            for pitch in beat_result:
                all_notes.append(Note(pitch=pitch, duration=q_dur, dynamic=None, articulations=()))

    return tuple(all_notes)


def _generate_beat_notes(
    cf_pitches: list[Pitch],
    cf_idx: int,
    count: int,
    above: bool,
    low_midi: int,
    high_midi: int,
    prefer_sharps: bool,
    existing_notes: list[Note],
) -> list[Pitch]:
    """Generate `count` pitches for a single CF beat.

    First note must be consonant; subsequent notes may be stepwise dissonances.
    """
    cf_midi = cf_pitches[cf_idx].midi_number
    result: list[Pitch] = []

    # Get previous pitch for stepwise motion
    prev_midi: int | None = None
    if existing_notes:
        prev_midi = existing_notes[-1].pitch.midi_number

    for sub_pos in builtins.range(count):
        candidates: list[tuple[int, Pitch]] = []

        for midi in builtins.range(low_midi, high_midi + 1):
            interval_mod12 = abs(midi - cf_midi) % 12

            if above and midi < cf_midi:
                continue
            if not above and midi > cf_midi:
                continue

            if sub_pos == 0:
                # First of group: must be consonant
                if interval_mod12 not in _CONSONANCES:
                    continue
            else:
                # Subsequent: consonant or stepwise
                if interval_mod12 not in _CONSONANCES:
                    last = result[-1].midi_number if result else (prev_midi or cf_midi)
                    if abs(midi - last) > 2:
                        continue

            priority = 0
            ref = result[-1].midi_number if result else prev_midi
            if ref is not None:
                step_dist = abs(midi - ref)
                if step_dist <= 2:
                    priority -= 3
                elif step_dist <= 4:
                    priority -= 1
                # Avoid repeated note
                if midi == ref:
                    continue

            pitch = from_midi(midi, prefer_sharps=prefer_sharps)
            candidates.append((priority, pitch))

        if not candidates:
            # Fallback: any consonant pitch
            for midi in builtins.range(low_midi, high_midi + 1):
                interval_mod12 = abs(midi - cf_midi) % 12
                if interval_mod12 in _CONSONANCES:
                    if above and midi < cf_midi:
                        continue
                    if not above and midi > cf_midi:
                        continue
                    candidates.append((0, from_midi(midi, prefer_sharps=prefer_sharps)))

        random.shuffle(candidates)
        candidates.sort(key=lambda x: x[0])
        if candidates:
            result.append(candidates[0][1])

    return result


# ---------------------------------------------------------------------------
# Free counterpoint
# ---------------------------------------------------------------------------


def generate_free_counterpoint(
    cf: Phrase,
    above: bool = True,
    range: tuple[Pitch, Pitch] | None = None,  # noqa: A002
) -> Phrase:
    """Generate free counterpoint (tonal voice-leading, relaxed species rules).

    Same number of notes as CF, consonant on beats, no parallel 5ths/8ths.
    More relaxed than strict species: no climax rule, no repeated-note prohibition.
    """
    cf_pitches, cf_durations = _extract_cf(cf)
    low_midi, high_midi = _compute_range(cf_pitches, above, range)
    n_notes = len(cf_pitches)
    prefer_sharps = above

    def _candidates(position: int, partial: list[Pitch], cf_pitch: Pitch) -> list[Pitch]:
        cf_midi = cf_pitch.midi_number
        results: list[tuple[int, int, Pitch]] = []

        for midi in builtins.range(low_midi, high_midi + 1):
            interval_mod12 = abs(midi - cf_midi) % 12

            # Must be consonant
            if interval_mod12 not in _CONSONANCES:
                continue
            if above and midi < cf_midi:
                continue
            if not above and midi > cf_midi:
                continue

            # First and last: perfect consonance
            if (position == 0 or position == n_notes - 1):
                if interval_mod12 not in PERFECT_CONSONANCES:
                    continue

            priority = 0
            if interval_mod12 in IMPERFECT_CONSONANCES:
                priority -= 1
            if partial:
                step_dist = abs(midi - partial[-1].midi_number)
                if step_dist <= 2:
                    priority -= 3
                elif step_dist <= 4:
                    priority -= 1

            pitch = from_midi(midi, prefer_sharps=prefer_sharps)
            results.append((priority, midi, pitch))

        random.shuffle(results)
        results.sort(key=lambda x: x[0])
        return [r[2] for r in results]

    def _validate(position: int, partial: list[Pitch], candidate: Pitch, cf_pitch: Pitch) -> bool:
        cf_midi = cf_pitch.midi_number
        cand_midi = candidate.midi_number

        if above and cand_midi < cf_midi:
            return False
        if not above and cand_midi > cf_midi:
            return False

        if position > 0:
            prev_cp = partial[-1]
            prev_cf = cf_pitches[position - 1]
            prev_cp_midi = prev_cp.midi_number
            prev_cf_midi = prev_cf.midi_number

            # No parallel 5ths/8ths
            prev_interval_mod12 = abs(prev_cp_midi - prev_cf_midi) % 12
            curr_interval_mod12 = abs(cand_midi - cf_midi) % 12

            if prev_interval_mod12 == curr_interval_mod12 and prev_interval_mod12 in (0, 7):
                motion_cf = cf_midi - prev_cf_midi
                motion_cp = cand_midi - prev_cp_midi
                if motion_cf != 0 and motion_cp != 0:
                    if (motion_cf > 0) == (motion_cp > 0):
                        return False

        return True

    result = _backtrack(cf_pitches, _candidates, _validate, 0, [])
    if result is None:
        raise ValueError("No valid free counterpoint found")

    events: list[Note] = []
    for i, pitch in enumerate(result):
        events.append(Note(pitch=pitch, duration=cf_durations[i], dynamic=None, articulations=()))
    return tuple(events)


# ---------------------------------------------------------------------------
# Multi-voice counterpoint
# ---------------------------------------------------------------------------


def _avg_midi(phrase: Phrase) -> float:
    """Return the mean MIDI number of Note events in a phrase."""
    midis = [e.pitch.midi_number for e in phrase if isinstance(e, Note)]
    return sum(midis) / len(midis) if midis else 0.0


def _species_generator(species: int):  # noqa: ANN201
    """Return the appropriate generation function for a species number."""
    generators = {
        0: generate_free_counterpoint,
        1: generate_first_species,
        2: generate_second_species,
        3: generate_third_species,
        4: generate_fourth_species,
        5: generate_fifth_species,
    }
    return generators[species]


def generate_multi_voice_counterpoint(
    cf: Phrase,
    n: int = 2,
    species: int = 1,
    above: int | None = None,
) -> "Score":
    """Generate multi-voice counterpoint as a Score.

    Args:
        cf: The cantus firmus phrase.
        n: Number of counterpoint voices to generate (1-4).
        species: Species number (0-5) for all generated voices.
        above: How many voices to place above CF. If None, all above.

    Returns:
        Score with CF and n counterpoint voices, ordered highest to lowest.

    Raises:
        ValueError: If cf is empty or n > 4.
    """
    from cadenza.core.score import Score

    if not cf:
        raise ValueError("Cantus firmus must not be empty")
    if n > 4:
        raise ValueError(f"Maximum 4 counterpoint voices, got {n}")

    above_count = above if above is not None else n
    below_count = n - above_count

    gen_fn = _species_generator(species)

    voices: list[tuple[str, Phrase]] = []

    def _has_parallel_issues(new_voice: Phrase, existing: list[tuple[str, Phrase]]) -> bool:
        """Check if new_voice has parallel 5ths/8ths with any existing voice."""
        from cadenza.counterpoint.validation import check_counterpoint as _check
        for _, existing_phrase in existing:
            # Use species=1 for inter-voice check (1:1 note alignment)
            violations = _check(existing_phrase, new_voice, species=1)
            parallels = [
                v for v in violations
                if v.rule in ("parallel_fifth", "parallel_octave")
                and v.severity == "error"
            ]
            if parallels:
                return True
        return False

    def _gen_voice(is_above: bool, existing: list[tuple[str, Phrase]]) -> Phrase:
        """Generate a voice, retrying to avoid inter-voice parallels."""
        best: Phrase | None = None
        best_issues = 999
        for _attempt in builtins.range(50):
            candidate = gen_fn(cf, above=is_above)
            if not _has_parallel_issues(candidate, existing):
                return candidate
            # Track best candidate (fewest parallel issues)
            from cadenza.counterpoint.validation import check_counterpoint as _check
            issues = 0
            for _, ep in existing:
                vs = _check(ep, candidate, species=1)
                issues += sum(1 for v in vs if v.rule in ("parallel_fifth", "parallel_octave") and v.severity == "error")
            if issues < best_issues:
                best_issues = issues
                best = candidate
        return best if best is not None else gen_fn(cf, above=is_above)

    # Generate voices above CF
    for i in builtins.range(above_count):
        voice_name = f"cp{len(voices) + 1}"
        voice = _gen_voice(True, voices)
        voices.append((voice_name, voice))

    # Generate voices below CF
    for i in builtins.range(below_count):
        voice_name = f"cp{len(voices) + 1}"
        voice = _gen_voice(False, voices)
        voices.append((voice_name, voice))

    # Add CF
    voices.append(("cf", cf))

    # Sort all voices by average MIDI pitch (highest first)
    voices.sort(key=lambda v: _avg_midi(v[1]), reverse=True)

    return Score(_voices=tuple(voices))
