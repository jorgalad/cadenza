"""Roman numeral analysis, functional harmony, and harmonic rhythm.

Provides roman_numeral for labeling chords within a key context,
harmonic_rhythm for detecting chord change points in a phrase,
and borrowed chord identification via parallel key comparison.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from cadenza.analysis.chords import ChordMatch, identify_chord
from cadenza.analysis.keys import KeyResult
from cadenza.core.note import Note, Rest
from cadenza.core.pitch import Pitch
from cadenza.theory.scales import get_scale, scale_degree


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class RomanNumeral:
    """Roman numeral analysis result for a chord in a key context."""

    numeral: str  # e.g. "I", "ii", "V7", "bVII", "I6", "V6/5"
    function: str  # "tonic", "subdominant", "dominant", "predominant", "borrowed", "other"
    chord: ChordMatch


@dataclass(frozen=True, slots=True)
class HarmonicBeat:
    """A segment of harmonic rhythm with a single chord."""

    onset: Fraction
    duration: Fraction
    chord: ChordMatch
    numeral: RomanNumeral


# ---------------------------------------------------------------------------
# Lookup tables
# ---------------------------------------------------------------------------

_TRIAD_FIGURES: dict[int, str] = {0: "", 1: "6", 2: "6/4"}
_SEVENTH_FIGURES: dict[int, str] = {0: "7", 1: "6/5", 2: "4/3", 3: "4/2"}

_DEGREE_FUNCTION: dict[int, str] = {
    1: "tonic",
    2: "predominant",
    3: "tonic",
    4: "subdominant",
    5: "dominant",
    6: "tonic",
    7: "dominant",
}

_NUMERAL_UPPER = ("I", "II", "III", "IV", "V", "VI", "VII")
_NUMERAL_LOWER = ("i", "ii", "iii", "iv", "v", "vi", "vii")

# Chord symbols that use uppercase Roman numerals (major/augmented quality)
_MAJOR_QUALITIES = frozenset({
    "maj", "aug", "7", "maj7", "maj9", "maj11", "maj13",
    "9", "11", "13", "add9", "add11", "sus2", "sus4", "aug7",
})


# ---------------------------------------------------------------------------
# Helper: parallel mode for borrowed chord detection
# ---------------------------------------------------------------------------


def _parallel_mode(mode: str) -> str:
    """Get the parallel mode for borrowed chord detection."""
    if "minor" in mode:
        return "major"
    return "natural_minor"


def _chromatic_degree_and_prefix(
    chord_root_pc: int, tonic_pc: int
) -> tuple[int, str]:
    """Compute chromatic degree (1-based) and b/# prefix for non-diatonic chords."""
    # Semitone distance from tonic
    semitones = (chord_root_pc - tonic_pc) % 12

    # Map semitone to nearest diatonic degree and determine prefix
    # Major scale semitones: 0, 2, 4, 5, 7, 9, 11
    _SEMITONE_TO_DEGREE: dict[int, tuple[int, str]] = {
        0: (1, ""),
        1: (2, "b"),
        2: (2, ""),
        3: (3, "b"),
        4: (3, ""),
        5: (4, ""),
        6: (4, "#"),  # or b5
        7: (5, ""),
        8: (6, "b"),
        9: (6, ""),
        10: (7, "b"),
        11: (7, ""),
    }
    degree, prefix = _SEMITONE_TO_DEGREE[semitones]
    return degree, prefix


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def roman_numeral(chord: ChordMatch, key: KeyResult) -> RomanNumeral:
    """Label a chord with its Roman numeral and function in a key.

    Args:
        chord: A ChordMatch (from identify_chord or manual construction).
        key: The key context for analysis.

    Returns:
        RomanNumeral with numeral string, function label, and original chord.
    """
    scale = get_scale(key.root, key.mode)
    tonic_pc = key.root.pitch_class
    chord_root_pc = chord.root.pitch_class

    # Try to find degree in the key's scale
    degree: int | None = None
    function = "other"
    prefix = ""

    try:
        degree = scale_degree(chord.root, scale)
        function = _DEGREE_FUNCTION.get(degree, "other")
    except ValueError:
        # Not diatonic -- check parallel key for borrowed chord
        parallel_mode = _parallel_mode(key.mode)
        try:
            parallel_scale = get_scale(key.root, parallel_mode)
            degree = scale_degree(chord.root, parallel_scale)
            function = "borrowed"

            # Determine b/# prefix by comparing to diatonic pitch class at this degree
            diatonic_pc = scale.pitches[degree - 1].pitch_class if degree <= len(scale.pitches) else None
            if diatonic_pc is not None and chord_root_pc != diatonic_pc:
                # Check if chromatically lower or higher
                diff = (chord_root_pc - diatonic_pc) % 12
                if diff > 6:
                    prefix = "b"
                else:
                    prefix = "#"
            elif diatonic_pc is None:
                # Compute from chromatic distance
                _, prefix = _chromatic_degree_and_prefix(chord_root_pc, tonic_pc)
        except ValueError:
            # Not in parallel key either -- use chromatic degree
            degree_info = _chromatic_degree_and_prefix(chord_root_pc, tonic_pc)
            degree = degree_info[0]
            prefix = degree_info[1]
            function = "other"

    # Build numeral string
    is_upper = chord.symbol in _MAJOR_QUALITIES
    base_numeral = _NUMERAL_UPPER[degree - 1] if is_upper else _NUMERAL_LOWER[degree - 1]
    numeral_str = prefix + base_numeral

    # Add figured bass suffix
    num_pitches = len(chord.pitches)
    if num_pitches >= 4:
        # Seventh or extended chord
        figure = _SEVENTH_FIGURES.get(chord.inversion, "")
        numeral_str += figure
    elif num_pitches == 3:
        # Triad
        figure = _TRIAD_FIGURES.get(chord.inversion, "")
        numeral_str += figure

    return RomanNumeral(numeral=numeral_str, function=function, chord=chord)


def harmonic_rhythm(
    phrase: tuple[object, ...],
    key: KeyResult,
    window: int = 3,
) -> list[HarmonicBeat]:
    """Analyze harmonic rhythm by detecting chord changes in a phrase.

    Uses a sliding window of notes to identify chords and detect changes.

    Args:
        phrase: A Phrase (tuple of Note/Rest Events).
        key: The key context for Roman numeral labeling.
        window: Number of notes to group for chord identification.

    Returns:
        List of HarmonicBeat objects with onset/duration as Fractions.
    """
    if not phrase:
        return []

    # Extract notes with their onsets
    notes: list[tuple[Note, Fraction]] = []
    onset = Fraction(0)
    for event in phrase:
        if isinstance(event, Note):
            notes.append((event, onset))
        if isinstance(event, (Note, Rest)):
            onset += event.duration.fraction

    if len(notes) < 2:
        return []

    total_duration = onset

    # Identify chord for each window of notes
    beats: list[HarmonicBeat] = []
    current_chord: ChordMatch | None = None
    segment_onset = Fraction(0)

    i = 0
    while i <= len(notes) - window:
        window_notes = notes[i : i + window]
        window_pitches = tuple(n.pitch for n, _ in window_notes)

        new_chord: ChordMatch | None = None
        try:
            new_chord = identify_chord(window_pitches)
        except ValueError:
            new_chord = None

        note_onset = window_notes[0][1]

        if new_chord is not None:
            chord_changed = current_chord is not None and (
                new_chord.root.pitch_class != current_chord.root.pitch_class
                or new_chord.symbol != current_chord.symbol
            )

            if chord_changed:
                # Close previous segment
                seg_dur = note_onset - segment_onset
                if seg_dur > 0 and current_chord is not None:
                    rn = roman_numeral(current_chord, key)
                    beats.append(HarmonicBeat(
                        onset=segment_onset,
                        duration=seg_dur,
                        chord=current_chord,
                        numeral=rn,
                    ))
                segment_onset = note_onset
                current_chord = new_chord
            elif current_chord is None:
                current_chord = new_chord

        i += 1

    # Close final segment
    if current_chord is not None:
        seg_dur = total_duration - segment_onset
        if seg_dur > 0:
            rn = roman_numeral(current_chord, key)
            beats.append(HarmonicBeat(
                onset=segment_onset,
                duration=seg_dur,
                chord=current_chord,
                numeral=rn,
            ))

    return beats
