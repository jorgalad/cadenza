"""Tests for phrase analysis functions (ANAL-01 through ANAL-09)."""

from __future__ import annotations

from fractions import Fraction

import pytest

from cadenza.core.duration import Duration
from cadenza.core.interval import Interval
from cadenza.core.note import Note, Rest
from cadenza.core.pitch import Pitch

from cadenza.analysis.phrases import (
    MotifMatch,
    SequenceMatch,
    ambitus,
    complexity_score,
    detect_sequence,
    find_motifs,
    interval_sequence,
    melodic_contour,
    phrase_similarity,
    pitch_class_histogram,
    rhythmic_density,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

Q = Duration.from_cn("q")  # quarter note
H = Duration.from_cn("h")  # half note
E = Duration.from_cn("e")  # eighth note
W = Duration.from_cn("w")  # whole note


def n(step: str, acc: str, octave: int, dur: Duration = Q) -> Note:
    """Shorthand note constructor."""
    return Note(pitch=Pitch(step, acc, octave), duration=dur)


def r(dur: Duration = Q) -> Rest:
    """Shorthand rest constructor."""
    return Rest(duration=dur)


C4 = n("c", "n", 4)
D4 = n("d", "n", 4)
E4 = n("e", "n", 4)
F4 = n("f", "n", 4)
G4 = n("g", "n", 4)
A4 = n("a", "n", 4)
B4 = n("b", "n", 4)
C5 = n("c", "n", 5)
G5 = n("g", "n", 5)


# ===========================================================================
# ANAL-01: ambitus
# ===========================================================================


class TestAmbitus:
    def test_basic(self):
        phrase = (C4, E4, G5, D4)
        low, high = ambitus(phrase)
        assert low == Pitch("c", "n", 4)
        assert high == Pitch("g", "n", 5)

    def test_single_note(self):
        phrase = (C4,)
        low, high = ambitus(phrase)
        assert low == Pitch("c", "n", 4)
        assert high == Pitch("c", "n", 4)

    def test_skips_rests(self):
        phrase = (r(), C4, r(), G5)
        low, high = ambitus(phrase)
        assert low == Pitch("c", "n", 4)
        assert high == Pitch("g", "n", 5)

    def test_empty_phrase_raises(self):
        with pytest.raises(ValueError):
            ambitus(())

    def test_only_rests_raises(self):
        with pytest.raises(ValueError):
            ambitus((r(), r()))


# ===========================================================================
# ANAL-02: melodic_contour
# ===========================================================================


class TestMelodicContour:
    def test_basic(self):
        phrase = (C4, E4, D4, D4)
        assert melodic_contour(phrase) == ["U", "D", "S"]

    def test_skips_rests(self):
        phrase = (C4, r(), E4, D4)
        assert melodic_contour(phrase) == ["U", "D"]

    def test_single_note(self):
        assert melodic_contour((C4,)) == []

    def test_empty_phrase(self):
        assert melodic_contour(()) == []

    def test_ascending(self):
        phrase = (C4, D4, E4, F4, G4)
        assert melodic_contour(phrase) == ["U", "U", "U", "U"]


# ===========================================================================
# ANAL-03: interval_sequence
# ===========================================================================


class TestIntervalSequence:
    def test_basic(self):
        phrase = (C4, E4, G4)
        intervals = interval_sequence(phrase)
        assert len(intervals) == 2
        assert intervals[0] == Interval("M", 3, 1)  # C4->E4
        assert intervals[1] == Interval("m", 3, 1)  # E4->G4

    def test_skips_rests(self):
        phrase = (C4, r(), E4)
        intervals = interval_sequence(phrase)
        assert len(intervals) == 1
        assert intervals[0] == Interval("M", 3, 1)

    def test_single_note(self):
        assert interval_sequence((C4,)) == []

    def test_empty(self):
        assert interval_sequence(()) == []


# ===========================================================================
# ANAL-04: pitch_class_histogram
# ===========================================================================


class TestPitchClassHistogram:
    def test_basic(self):
        phrase = (C4, E4, G4, C5)
        hist = pitch_class_histogram(phrase)
        assert hist[0] == 2   # C appears twice
        assert hist[4] == 1   # E
        assert hist[7] == 1   # G

    def test_skips_rests(self):
        phrase = (C4, r(), E4)
        hist = pitch_class_histogram(phrase)
        assert hist[0] == 1
        assert hist[4] == 1
        assert len(hist) == 2

    def test_empty(self):
        assert pitch_class_histogram(()) == {}


# ===========================================================================
# ANAL-05: rhythmic_density
# ===========================================================================


class TestRhythmicDensity:
    def test_basic_quarter_notes(self):
        # 4 quarter notes: each occupies one window (quarter note window)
        phrase = (C4, D4, E4, F4)
        density = rhythmic_density(phrase)
        # Default window = quarter note, each note starts at onset 0, 1/4, 2/4, 3/4
        # Window [0, 1/4): C4 -> 1 note
        # Window [1/4, 2/4): D4 -> 1 note
        # Window [2/4, 3/4): E4 -> 1 note
        # Window [3/4, 4/4): F4 -> 1 note
        assert density == [1.0, 1.0, 1.0, 1.0]

    def test_eighth_notes(self):
        # 4 eighth notes in quarter-note windows
        e_c4 = n("c", "n", 4, E)
        e_d4 = n("d", "n", 4, E)
        e_e4 = n("e", "n", 4, E)
        e_f4 = n("f", "n", 4, E)
        phrase = (e_c4, e_d4, e_e4, e_f4)
        density = rhythmic_density(phrase)
        # Total duration = 4 * 1/8 = 1/2, windows = ceil(0.5 / 0.25) = 2
        # Window [0, 1/4): onsets at 0 and 1/8 -> 2 notes
        # Window [1/4, 1/2): onsets at 2/8 and 3/8 -> 2 notes
        assert density == [2.0, 2.0]

    def test_empty(self):
        assert rhythmic_density(()) == []

    def test_with_rest(self):
        phrase = (C4, r(), D4)
        density = rhythmic_density(phrase)
        # Onsets: C4 at 0, rest at 1/4, D4 at 2/4
        # Window [0, 1/4): C4 -> 1
        # Window [1/4, 2/4): rest (not a note) -> 0
        # Window [2/4, 3/4): D4 -> 1
        assert density == [1.0, 0.0, 1.0]


# ===========================================================================
# ANAL-06: complexity_score
# ===========================================================================


class TestComplexityScore:
    def test_returns_float(self):
        phrase = (C4, D4, E4, F4, G4)
        score = complexity_score(phrase)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_single_note(self):
        assert complexity_score((C4,)) == 0.0

    def test_empty(self):
        assert complexity_score(()) == 0.0

    def test_simple_scale_low_complexity(self):
        # Ascending scale: uniform intervals, uniform rhythm, no direction changes
        phrase = (C4, D4, E4, F4, G4)
        score = complexity_score(phrase)
        # All intervals are seconds (M2, M2, M2, M2) -> 1 unique / 4 = 0.25 for intervals
        # But M2 and m2 have different semitones... C-D=2, D-E=2, E-F=1, F-G=2
        # unique abs semitones: {2, 1} -> 2/4 = 0.5
        # rhythm: all same duration -> 1/5 = 0.2
        # contour: all "U" -> 0 changes / 3 = 0.0
        # Average ~ (0.5 + 0.2 + 0.0) / 3 ~ 0.233
        assert score < 0.5

    def test_two_identical_notes(self):
        phrase = (C4, C4)
        score = complexity_score(phrase)
        # intervals: 1 interval with 0 semitones -> unique = {0}, variety = 1/1 = 1.0
        # rhythm: same duration -> 1/2 = 0.5
        # contour: ["S"] -> 0 changes (len 1, no changes possible)
        # Average = (1.0 + 0.5 + 0.0) / 3 = 0.5
        assert score == pytest.approx(0.5, abs=0.01)


# ===========================================================================
# ANAL-07: find_motifs
# ===========================================================================


class TestFindMotifs:
    def test_repeated_motif(self):
        phrase = (C4, D4, E4, C4, D4, E4)
        matches = find_motifs(phrase, min_length=3)
        assert len(matches) >= 1
        found = matches[0]
        assert isinstance(found, MotifMatch)
        assert len(found.positions) >= 2
        assert 0 in found.positions
        assert 3 in found.positions

    def test_min_length_default(self):
        # Default min_length=2
        phrase = (C4, D4, C4, D4)
        matches = find_motifs(phrase)
        assert len(matches) >= 1

    def test_no_motifs(self):
        phrase = (C4, D4, E4, F4, G4, A4)
        matches = find_motifs(phrase, min_length=3)
        assert matches == []

    def test_rests_not_in_motifs(self):
        # Motifs use notes only, but positions are event indices in original phrase
        phrase = (C4, r(), D4, C4, r(), D4)
        matches = find_motifs(phrase)
        assert len(matches) >= 1

    def test_motifmatch_is_frozen(self):
        phrase = (C4, D4, E4, C4, D4, E4)
        matches = find_motifs(phrase, min_length=3)
        if matches:
            with pytest.raises(AttributeError):
                matches[0].motif = ()  # type: ignore[misc]


# ===========================================================================
# ANAL-08: phrase_similarity
# ===========================================================================


class TestPhraseSimilarity:
    def test_identical_phrases(self):
        phrase = (C4, D4, E4, F4)
        assert phrase_similarity(phrase, phrase) == 1.0

    def test_completely_different(self):
        phrase1 = (C4, C4, C4, C4)
        # Different pitches AND different durations
        phrase2 = (
            n("g", "n", 5, H),
            n("a", "n", 5, H),
            n("b", "n", 5, H),
            n("f", "s", 5, H),
        )
        score = phrase_similarity(phrase1, phrase2)
        assert score < 0.3  # near 0.0

    def test_returns_float_0_1(self):
        score = phrase_similarity((C4, D4), (E4, F4))
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_empty_phrases(self):
        # Two empty phrases: similarity should be well-defined
        score = phrase_similarity((), ())
        assert isinstance(score, float)


# ===========================================================================
# ANAL-09: detect_sequence
# ===========================================================================


class TestDetectSequence:
    def test_exact_match(self):
        phrase1 = (C4, D4, E4, F4, G4)
        phrase2 = (C4, D4, E4)
        matches = detect_sequence(phrase1, phrase2)
        exact = [m for m in matches if m.match_type == "exact"]
        assert len(exact) >= 1
        assert exact[0].offset == 0
        assert exact[0].transposition is None

    def test_transposed_match(self):
        # phrase2 is phrase1[2:5] transposed up by some interval
        # C4 D4 E4 F4 G4 -> intervals M2 M2 m2 M2
        # E4 Fs4 Gs4 -> intervals M2 M2 (matches first 2 interval segment)
        phrase1 = (C4, D4, E4, F4, G4)
        # Transposed version of C4-D4-E4 up a major third
        e4 = n("e", "n", 4)
        fs4 = n("f", "s", 4)
        gs4 = n("g", "s", 4)
        phrase2 = (e4, fs4, gs4)
        matches = detect_sequence(phrase1, phrase2)
        transposed = [m for m in matches if m.match_type == "transposed"]
        assert len(transposed) >= 1
        assert transposed[0].transposition is not None

    def test_no_match(self):
        phrase1 = (C4, D4, E4)
        phrase2 = (n("g", "n", 5, H), n("a", "n", 5, H))
        matches = detect_sequence(phrase1, phrase2)
        assert matches == []

    def test_sequencematch_is_frozen(self):
        phrase1 = (C4, D4, E4)
        phrase2 = (C4, D4, E4)
        matches = detect_sequence(phrase1, phrase2)
        if matches:
            with pytest.raises(AttributeError):
                matches[0].offset = 5  # type: ignore[misc]

    def test_returns_list(self):
        result = detect_sequence((C4,), (D4,))
        assert isinstance(result, list)
