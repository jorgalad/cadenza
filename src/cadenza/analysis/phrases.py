"""Phrase analysis: melodic, rhythmic, and structural inspection functions.

Provides 9 analysis functions (ANAL-01 through ANAL-09) for inspecting
properties of musical phrases -- ambitus, contour, intervals, histograms,
density, complexity, motif detection, similarity, and sequence detection.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction

from cadenza.core.duration import Duration
from cadenza.core.interval import Interval
from cadenza.core.note import Note, Rest
from cadenza.core.phrase import Phrase
from cadenza.core.pitch import Pitch


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class MotifMatch:
    """A repeated motif found within a phrase."""

    motif: Phrase
    positions: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class SequenceMatch:
    """A sequential (exact or transposed) imitation match."""

    match_type: str  # "exact" or "transposed"
    offset: int  # 0-based event index in phrase1 where match starts
    transposition: Interval | None  # None for exact, Interval for transposed


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _extract_notes(phrase: Phrase) -> list[Note]:
    """Extract only Note events from a phrase, preserving order."""
    return [e for e in phrase if isinstance(e, Note)]


def _extract_notes_with_indices(phrase: Phrase) -> list[tuple[int, Note]]:
    """Extract Note events with their original event indices in the phrase."""
    return [(i, e) for i, e in enumerate(phrase) if isinstance(e, Note)]


# ---------------------------------------------------------------------------
# ANAL-01: ambitus
# ---------------------------------------------------------------------------


def ambitus(phrase: Phrase) -> tuple[Pitch, Pitch]:
    """Return the lowest and highest pitches in the phrase.

    Args:
        phrase: A phrase of events.

    Returns:
        Tuple of (lowest_pitch, highest_pitch) by MIDI number.

    Raises:
        ValueError: If the phrase contains no notes.
    """
    notes = _extract_notes(phrase)
    if not notes:
        raise ValueError("Phrase contains no notes")
    lowest = min(notes, key=lambda n: n.pitch.midi_number)
    highest = max(notes, key=lambda n: n.pitch.midi_number)
    return (lowest.pitch, highest.pitch)


# ---------------------------------------------------------------------------
# ANAL-02: melodic_contour
# ---------------------------------------------------------------------------


def melodic_contour(phrase: Phrase) -> list[str]:
    """Return the melodic contour as a list of direction markers.

    "U" = ascending, "D" = descending, "S" = same pitch.
    Rests are skipped; contour is computed between consecutive Note events.

    Returns:
        List of "U", "D", or "S" strings. Empty if fewer than 2 notes.
    """
    notes = _extract_notes(phrase)
    if len(notes) < 2:
        return []
    result: list[str] = []
    for i in range(1, len(notes)):
        prev_midi = notes[i - 1].pitch.midi_number
        curr_midi = notes[i].pitch.midi_number
        if curr_midi > prev_midi:
            result.append("U")
        elif curr_midi < prev_midi:
            result.append("D")
        else:
            result.append("S")
    return result


# ---------------------------------------------------------------------------
# ANAL-03: interval_sequence
# ---------------------------------------------------------------------------


def interval_sequence(phrase: Phrase) -> list[Interval]:
    """Return intervals between consecutive notes (rests skipped).

    Returns:
        List of Interval objects computed via Interval.between().
    """
    notes = _extract_notes(phrase)
    if len(notes) < 2:
        return []
    return [
        Interval.between(notes[i].pitch, notes[i + 1].pitch)
        for i in range(len(notes) - 1)
    ]


# ---------------------------------------------------------------------------
# ANAL-04: pitch_class_histogram
# ---------------------------------------------------------------------------


def pitch_class_histogram(phrase: Phrase) -> dict[int, int]:
    """Return a histogram of pitch class frequencies (0-11).

    Returns:
        Dict mapping pitch class (int) to occurrence count.
    """
    notes = _extract_notes(phrase)
    if not notes:
        return {}
    return dict(Counter(n.pitch.pitch_class for n in notes))


# ---------------------------------------------------------------------------
# ANAL-05: rhythmic_density
# ---------------------------------------------------------------------------


def rhythmic_density(
    phrase: Phrase, window: Fraction = Fraction(1, 4)
) -> list[float]:
    """Compute note density per time window.

    Args:
        phrase: A phrase of events.
        window: Window size as fraction of whole note (default: quarter note).

    Returns:
        List of floats representing note count per window.
    """
    if not phrase:
        return []

    # Compute onset times for each event
    onset = Fraction(0)
    onsets: list[tuple[Fraction, bool]] = []  # (onset_time, is_note)
    for event in phrase:
        is_note = isinstance(event, Note)
        onsets.append((onset, is_note))
        onset += event.duration.fraction

    total_duration = onset
    if total_duration <= 0:
        return []

    num_windows = math.ceil(total_duration / window)
    counts = [0.0] * num_windows

    for onset_time, is_note in onsets:
        if is_note:
            win_idx = int(onset_time / window)
            if win_idx >= num_windows:
                win_idx = num_windows - 1
            counts[win_idx] += 1.0

    return counts


# ---------------------------------------------------------------------------
# ANAL-06: complexity_score
# ---------------------------------------------------------------------------


def complexity_score(phrase: Phrase) -> float:
    """Compute a 0.0-1.0 complexity score for the phrase.

    Averages three sub-scores:
    - Interval variety (unique absolute semitone counts / total intervals)
    - Rhythm variety (unique durations / total notes)
    - Contour change rate (direction changes / possible change points)

    Returns 0.0 for phrases with fewer than 2 notes.
    """
    notes = _extract_notes(phrase)
    if len(notes) < 2:
        return 0.0

    # Interval variety
    intervals = interval_sequence(phrase)
    if intervals:
        unique_semitones = len(set(abs(iv.semitones) for iv in intervals))
        interval_variety = unique_semitones / len(intervals)
    else:
        interval_variety = 0.0

    # Rhythm variety
    rhythm_variety = len(set(n.duration.fraction for n in notes)) / len(notes)

    # Contour change rate
    contour = melodic_contour(phrase)
    if len(contour) > 1:
        direction_changes = sum(
            1 for i in range(1, len(contour)) if contour[i] != contour[i - 1]
        )
        contour_change_rate = direction_changes / (len(contour) - 1)
    else:
        contour_change_rate = 0.0

    return (interval_variety + rhythm_variety + contour_change_rate) / 3.0


# ---------------------------------------------------------------------------
# ANAL-07: find_motifs
# ---------------------------------------------------------------------------


def find_motifs(phrase: Phrase, min_length: int = 2) -> list[MotifMatch]:
    """Find repeated motifs within a phrase.

    Motif comparison uses MIDI number + duration fraction (sound-based).
    Positions are 0-based event indices in the original phrase.

    Args:
        phrase: A phrase of events.
        min_length: Minimum number of notes in a motif (default: 2).

    Returns:
        List of MotifMatch objects, sorted by motif length descending,
        then by first position ascending.
    """
    indexed_notes = _extract_notes_with_indices(phrase)
    if len(indexed_notes) < min_length * 2:
        return []

    # Build fingerprints: (midi_number, duration_fraction) for each note
    fingerprints = [
        (note.pitch.midi_number, note.duration.fraction)
        for _, note in indexed_notes
    ]
    event_indices = [idx for idx, _ in indexed_notes]

    results: list[MotifMatch] = []
    seen_fingerprints: set[tuple[tuple[int, Fraction], ...]] = set()

    max_length = len(indexed_notes) // 2

    for length in range(min_length, max_length + 1):
        # Group windows by fingerprint content
        groups: dict[tuple[tuple[int, Fraction], ...], list[int]] = {}
        for start in range(len(fingerprints) - length + 1):
            fp = tuple(fingerprints[start : start + length])
            if fp not in groups:
                groups[fp] = []
            groups[fp].append(start)

        for fp, starts in groups.items():
            if len(starts) < 2:
                continue
            # Check for overlapping windows -- only keep non-overlapping
            # Actually, the spec says positions where the motif occurs,
            # overlaps are fine for reporting
            if fp in seen_fingerprints:
                continue
            seen_fingerprints.add(fp)

            # Build the motif from the first occurrence
            first_start = starts[0]
            motif_events = tuple(
                indexed_notes[first_start + j][1] for j in range(length)
            )
            positions = tuple(event_indices[s] for s in starts)

            results.append(MotifMatch(motif=motif_events, positions=positions))

    # Sort: longest motifs first, then by first position
    results.sort(key=lambda m: (-len(m.motif), m.positions[0]))
    return results


# ---------------------------------------------------------------------------
# ANAL-08: phrase_similarity
# ---------------------------------------------------------------------------


def phrase_similarity(phrase1: Phrase, phrase2: Phrase) -> float:
    """Compute similarity between two phrases (0.0-1.0).

    Combines pitch, rhythm, and contour sub-scores via aligned matching.

    Returns:
        Float between 0.0 and 1.0. Identical phrases return 1.0.
    """
    notes1 = _extract_notes(phrase1)
    notes2 = _extract_notes(phrase2)

    if not notes1 and not notes2:
        return 1.0
    if not notes1 or not notes2:
        return 0.0

    # Pitch similarity (MIDI-based aligned matching)
    midi1 = [n.pitch.midi_number for n in notes1]
    midi2 = [n.pitch.midi_number for n in notes2]
    pitch_matches = sum(1 for a, b in zip(midi1, midi2) if a == b)
    pitch_score = pitch_matches / max(len(midi1), len(midi2), 1)

    # Rhythm similarity (duration fraction matching)
    dur1 = [n.duration.fraction for n in notes1]
    dur2 = [n.duration.fraction for n in notes2]
    rhythm_matches = sum(1 for a, b in zip(dur1, dur2) if a == b)
    rhythm_score = rhythm_matches / max(len(dur1), len(dur2), 1)

    # Contour similarity
    contour1 = melodic_contour(phrase1)
    contour2 = melodic_contour(phrase2)
    if not contour1 and not contour2:
        contour_score = 1.0
    elif not contour1 or not contour2:
        contour_score = 0.0
    else:
        contour_matches = sum(1 for a, b in zip(contour1, contour2) if a == b)
        contour_score = contour_matches / max(len(contour1), len(contour2), 1)

    return (pitch_score + rhythm_score + contour_score) / 3.0


# ---------------------------------------------------------------------------
# ANAL-09: detect_sequence
# ---------------------------------------------------------------------------


def detect_sequence(
    phrase1: Phrase, phrase2: Phrase
) -> list[SequenceMatch]:
    """Detect sequential imitation of phrase2 within phrase1.

    Finds exact matches (same MIDI + duration) and transposed matches
    (same interval sequence) of phrase2's notes within phrase1's notes.

    Args:
        phrase1: The larger phrase to search within.
        phrase2: The motif/pattern to search for.

    Returns:
        List of SequenceMatch objects. Empty if no matches found.
    """
    indexed1 = _extract_notes_with_indices(phrase1)
    indexed2 = _extract_notes_with_indices(phrase2)

    if not indexed2 or not indexed1:
        return []
    if len(indexed2) > len(indexed1):
        return []

    notes1 = [note for _, note in indexed1]
    notes2 = [note for _, note in indexed2]
    indices1 = [idx for idx, _ in indexed1]

    # Fingerprints for exact matching
    fp1 = [(n.pitch.midi_number, n.duration.fraction) for n in notes1]
    fp2 = [(n.pitch.midi_number, n.duration.fraction) for n in notes2]

    results: list[SequenceMatch] = []

    # Exact match: slide phrase2 fingerprint across phrase1
    for start in range(len(fp1) - len(fp2) + 1):
        if fp1[start : start + len(fp2)] == fp2:
            results.append(
                SequenceMatch(
                    match_type="exact",
                    offset=indices1[start],
                    transposition=None,
                )
            )

    # Transposed match: compare interval sequences
    if len(notes2) >= 2:
        ivs2 = [
            abs(Interval.between(notes2[i].pitch, notes2[i + 1].pitch).semitones)
            for i in range(len(notes2) - 1)
        ]
        # Also check duration pattern matches for transposed
        dur2 = [n.duration.fraction for n in notes2]

        for start in range(len(notes1) - len(notes2) + 1):
            window_notes = notes1[start : start + len(notes2)]

            # Check duration pattern matches
            dur_window = [n.duration.fraction for n in window_notes]
            if dur_window != dur2:
                continue

            ivs_window = [
                abs(
                    Interval.between(
                        window_notes[i].pitch, window_notes[i + 1].pitch
                    ).semitones
                )
                for i in range(len(window_notes) - 1)
            ]

            if ivs_window == ivs2:
                # Check it's not already an exact match
                window_fp = fp1[start : start + len(fp2)]
                if window_fp == fp2:
                    continue  # Already recorded as exact

                transposition = Interval.between(
                    notes2[0].pitch, window_notes[0].pitch
                )
                results.append(
                    SequenceMatch(
                        match_type="transposed",
                        offset=indices1[start],
                        transposition=transposition,
                    )
                )

    return results
