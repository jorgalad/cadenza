"""First species counterpoint generation."""

from __future__ import annotations

import builtins
import random

from cadenza.core.duration import Duration
from cadenza.core.interval import Interval
from cadenza.core.note import Note, Rest
from cadenza.core.phrase import Phrase
from cadenza.core.pitch import Pitch
from cadenza.counterpoint._engine import _backtrack
from cadenza.counterpoint.rules import (
    IMPERFECT_CONSONANCES,
    PERFECT_CONSONANCES,
)
from cadenza.transforms.pitch import from_midi


# All consonant intervals (mod 12)
_CONSONANCES = PERFECT_CONSONANCES | IMPERFECT_CONSONANCES


def generate_first_species(
    cf: Phrase,
    above: bool = True,
    range: tuple[Pitch, Pitch] | None = None,  # noqa: A002
) -> Phrase:
    """Generate first species counterpoint against a cantus firmus.

    Args:
        cf: The cantus firmus phrase (tuple of Note/Rest events).
        above: If True, generate counterpoint above CF; if False, below.
        range: Optional (low_pitch, high_pitch) to constrain output.

    Returns:
        A Phrase of the same length as cf with valid first species counterpoint.

    Raises:
        ValueError: If cf is empty or no valid counterpoint can be found.
    """
    if not cf:
        raise ValueError("Cantus firmus must not be empty")

    # Extract CF pitches and durations (skip rests)
    cf_pitches: list[Pitch] = []
    cf_durations: list[Duration] = []
    for event in cf:
        if isinstance(event, Note):
            cf_pitches.append(event.pitch)
            cf_durations.append(event.duration)
        else:
            # For rests, we still need a placeholder
            cf_pitches.append(Pitch("c", "n", 4))  # placeholder
            cf_durations.append(event.duration)

    if not cf_pitches:
        raise ValueError("Cantus firmus contains no notes")

    # Compute pitch range
    cf_midis = [p.midi_number for p in cf_pitches]
    cf_min = min(cf_midis)
    cf_max = max(cf_midis)

    if range is not None:
        low_midi = range[0].midi_number
        high_midi = range[1].midi_number
    elif above:
        low_midi = cf_min
        high_midi = cf_max + 16  # 10th above CF max
    else:
        low_midi = cf_min - 16  # 10th below CF min
        high_midi = cf_max

    n_notes = len(cf_pitches)
    prefer_sharps = above  # sharps ascending, flats descending

    def _candidates(position: int, partial: list[Pitch], cf_pitch: Pitch) -> list[Pitch]:
        """Generate candidate pitches for a position."""
        cf_midi = cf_pitch.midi_number
        results: list[tuple[int, int, Pitch]] = []  # (priority, midi, pitch)

        for midi in builtins.range(low_midi, high_midi + 1):
            interval_mod12 = abs(midi - cf_midi) % 12

            # Must be consonant
            if interval_mod12 not in _CONSONANCES:
                continue

            # Direction constraint
            if above and midi < cf_midi:
                continue
            if not above and midi > cf_midi:
                continue

            # First and last: only perfect consonances
            if (position == 0 or position == n_notes - 1):
                if interval_mod12 not in PERFECT_CONSONANCES:
                    continue

            # Priority: stepwise from previous note, imperfect over perfect
            priority = 0

            # Prefer imperfect consonances (more variety)
            if interval_mod12 in IMPERFECT_CONSONANCES:
                priority -= 1  # lower = better

            # Prefer stepwise from previous
            if partial:
                step_dist = abs(midi - partial[-1].midi_number)
                if step_dist <= 2:
                    priority -= 3  # strong preference for steps
                elif step_dist <= 4:
                    priority -= 1

            pitch = from_midi(midi, prefer_sharps=prefer_sharps)
            results.append((priority, midi, pitch))

        # Sort by priority (lower first) with random tiebreaking for variety
        random.shuffle(results)
        results.sort(key=lambda x: x[0])
        return [r[2] for r in results]

    def _validate(position: int, partial: list[Pitch], candidate: Pitch, cf_pitch: Pitch) -> bool:
        """Validate a candidate pitch at a position."""
        cf_midi = cf_pitch.midi_number
        cand_midi = candidate.midi_number

        if position > 0:
            prev_cp = partial[-1]
            prev_cf = cf_pitches[position - 1]

            prev_cp_midi = prev_cp.midi_number
            prev_cf_midi = prev_cf.midi_number

            # No parallel fifths
            prev_interval_mod12 = abs(prev_cp_midi - prev_cf_midi) % 12
            curr_interval_mod12 = abs(cand_midi - cf_midi) % 12

            if prev_interval_mod12 == curr_interval_mod12 and prev_interval_mod12 in (0, 7):
                # Check same direction and both moved
                motion_cf = cf_midi - prev_cf_midi
                motion_cp = cand_midi - prev_cp_midi
                if motion_cf != 0 and motion_cp != 0:
                    if (motion_cf > 0) == (motion_cp > 0):
                        return False

            # No voice crossing
            if above and cand_midi < cf_midi:
                return False
            if not above and cand_midi > cf_midi:
                return False

            # No repeated notes
            if cand_midi == prev_cp_midi:
                return False

            # No more than 3 consecutive parallel thirds or sixths
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

        # Penultimate check: must be step away from a valid final pitch
        if position == n_notes - 2 and n_notes >= 2:
            last_cf = cf_pitches[n_notes - 1]
            last_cf_midi = last_cf.midi_number
            # Find valid final pitches (perfect consonances within range)
            has_valid_step_final = False
            for final_midi in builtins.range(low_midi, high_midi + 1):
                final_mod12 = abs(final_midi - last_cf_midi) % 12
                if final_mod12 not in PERFECT_CONSONANCES:
                    continue
                if above and final_midi < last_cf_midi:
                    continue
                if not above and final_midi > last_cf_midi:
                    continue
                # Step from candidate to this final?
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

    # Convert to Phrase
    events: list[Note] = []
    for i, pitch in enumerate(result):
        events.append(
            Note(
                pitch=pitch,
                duration=cf_durations[i],
                dynamic=None,
                articulations=(),
            )
        )

    return tuple(events)
