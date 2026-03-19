"""Integration tests verifying all 5 ROADMAP Phase 1 success criteria.

Each test_roadmap_criterion_N function maps directly to the corresponding
success criterion in ROADMAP.md Phase 1.

Tests requiring the CN parser (plan 01-02) are skipped if not available.
"""

from __future__ import annotations

from fractions import Fraction

import pytest

from cadenza.core import (
    Pitch,
    Duration,
    Note,
    Rest,
    Score,
    to_json,
    from_json,
)
from cadenza.core.phrase import Phrase

# Detect whether the CN parser is available (plan 01-02)
try:
    from cadenza.cn import parse_cn, to_cn  # type: ignore[import-untyped]
    from cadenza.cn.errors import ParseError
    HAS_CN = True
except ImportError:
    HAS_CN = False

cn_required = pytest.mark.skipif(not HAS_CN, reason="CN parser not available (plan 01-02)")


# ---------------------------------------------------------------------------
# ROADMAP Criterion 1: Pitch spelling preservation
# ---------------------------------------------------------------------------


def test_roadmap_criterion_1_pitch_spelling_preservation() -> None:
    """A Pitch object preserves spelling (Eb3 and D#3 are distinct objects
    that compare unequal, but enharmonic_equal() returns True)."""
    eb3 = Pitch("e", "b", 3)
    ds3 = Pitch("d", "s", 3)

    # Spelling-sensitive equality
    assert eb3 != ds3, "Eb3 and D#3 must be distinct (spelling-sensitive equality)"
    assert eb3.enharmonic_equal(ds3), "Eb3 and D#3 must be enharmonically equal"
    assert eb3.midi_number == ds3.midi_number, "Same MIDI number"

    # Verify through JSON pipeline
    eb_json = to_json(eb3)
    ds_json = to_json(ds3)
    assert eb_json != ds_json, "JSON representations differ"
    assert from_json(eb_json) != from_json(ds_json), "JSON round-trip preserves distinction"
    assert from_json(eb_json).enharmonic_equal(from_json(ds_json))


@cn_required
def test_roadmap_criterion_1_pitch_spelling_through_cn() -> None:
    """Pitch spelling preserved through the CN parser pipeline."""
    phrase_eb, _ = parse_cn("q eb3")
    phrase_ds, _ = parse_cn("q ds3")
    assert phrase_eb[0].pitch != phrase_ds[0].pitch, "Spelling preserved through parser"
    assert phrase_eb[0].pitch.enharmonic_equal(phrase_ds[0].pitch)


# ---------------------------------------------------------------------------
# ROADMAP Criterion 2: Duration fraction precision
# ---------------------------------------------------------------------------


def test_roadmap_criterion_2_duration_fraction_precision() -> None:
    """Duration arithmetic using Fraction never loses precision -- a measure of
    dotted-quarter + eighth + half sums to exactly Fraction(1, 1)."""
    dotted_q = Duration.from_cn("q", dots=1)  # 3/8
    eighth = Duration.from_cn("e")  # 1/8
    half = Duration.from_cn("h")  # 1/2
    total = dotted_q.fraction + eighth.fraction + half.fraction
    assert total == Fraction(1, 1), f"Expected exactly 1/1, got {total}"
    assert isinstance(total, Fraction), "Result must be Fraction, not float"

    # Triplet arithmetic
    triplet_q = Duration.from_cn("q", tuplet=3)  # 1/6
    three_triplets = triplet_q.fraction * 3
    assert three_triplets == Fraction(1, 2), "Three triplet quarters = one half note"

    # Dotted half + quarter = whole
    dotted_h = Duration.from_cn("h", dots=1)  # 3/4
    quarter = Duration.from_cn("q")  # 1/4
    assert dotted_h.fraction + quarter.fraction == Fraction(1, 1)


# ---------------------------------------------------------------------------
# ROADMAP Criterion 3: CN round-trip
# ---------------------------------------------------------------------------


@cn_required
def test_roadmap_criterion_3_cn_round_trip() -> None:
    """An CN string like '(e f3 pp stacc)' round-trips through parse then
    serialize and produces an identical string (structural equality)."""
    test_cases = [
        "e c4 pp stacc",
        "e c4 pp stacc d4 e4",
        "q c4 mf e d4 pp stacc",
        "q. c4",
        "3q c4 d4 e4",
        "-q",
        "q c4 -e q d4",
    ]
    for cn_input in test_cases:
        phrase, warnings = parse_cn(cn_input)
        cn_output = to_cn(phrase)
        phrase2, warnings2 = parse_cn(cn_output)
        # Structural equality
        assert len(phrase) == len(phrase2), f"Length mismatch for '{cn_input}'"
        for orig, reparsed in zip(phrase, phrase2):
            assert type(orig) == type(reparsed)
            if isinstance(orig, Note):
                assert orig.pitch == reparsed.pitch
                assert orig.duration.fraction == reparsed.duration.fraction
                assert orig.dynamic == reparsed.dynamic
                assert orig.articulations == reparsed.articulations
            else:  # Rest
                assert orig.duration.fraction == reparsed.duration.fraction

    # Canonical form exact string match
    canonical = "e c4 pp stacc d4 e4"
    phrase, _ = parse_cn(canonical)
    assert to_cn(phrase) == canonical, "Canonical CN string must round-trip exactly"


# ---------------------------------------------------------------------------
# ROADMAP Criterion 4: Parse error position
# ---------------------------------------------------------------------------


@cn_required
def test_roadmap_criterion_4_parse_error_position() -> None:
    """The parser rejects malformed input with a clear error message including
    the position of the problem."""
    # Completely invalid token
    with pytest.raises(ParseError) as exc_info:
        parse_cn("q 123invalid")
    err = exc_info.value
    assert err.line >= 1, "Error must include line number"
    assert err.column >= 1, "Error must include column number"
    assert err.position >= 0, "Error must include character position"
    assert len(err.message) > 0, "Error must have descriptive message"

    # Another invalid input
    with pytest.raises(ParseError) as exc_info:
        parse_cn("q c4 pp stacc !!!")
    err = exc_info.value
    assert err.line >= 1
    assert err.column >= 1


# ---------------------------------------------------------------------------
# ROADMAP Criterion 5: Hashable, comparable, JSON-serializable
# ---------------------------------------------------------------------------


def test_roadmap_criterion_5_hashable_comparable_json_serializable() -> None:
    """All core types (Pitch, Duration, Note, Rest, Phrase, Score) are hashable,
    comparable, and JSON-serializable without information loss."""
    # Build a complete musical example
    c4 = Pitch("c", "n", 4)
    e4 = Pitch("e", "n", 4)
    g4 = Pitch("g", "n", 4)
    q = Duration.from_cn("q")
    e_dur = Duration.from_cn("e")

    note1 = Note(c4, q, "mf", ("stacc",))
    note2 = Note(e4, e_dur, "f", ())
    note3 = Note(g4, q, "mf", ("ten",))
    rest = Rest(q)
    phrase: Phrase = (note1, note2, rest, note3)
    score = Score.from_dict({"melody": phrase})

    # Hashable: can be used in sets and dicts
    pitch_set = {c4, e4, g4, c4}  # c4 deduplicates
    assert len(pitch_set) == 3
    note_set = {note1, note2, note3}
    assert len(note_set) == 3
    # Phrase (tuple) is hashable
    phrase_set = {phrase, phrase}
    assert len(phrase_set) == 1
    # Score is hashable
    score_set = {score, score}
    assert len(score_set) == 1

    # Comparable: Pitch ordering
    assert c4 < e4 < g4

    # JSON serializable without info loss
    for obj, name in [
        (c4, "Pitch"),
        (q, "Duration"),
        (note1, "Note"),
        (rest, "Rest"),
        (score, "Score"),
    ]:
        json_str = to_json(obj)
        restored = from_json(json_str)
        assert restored == obj, f"{name} JSON round-trip failed"

    # Phrase JSON round-trip
    phrase_json = to_json(phrase)
    restored_phrase = from_json(phrase_json)
    assert restored_phrase == phrase, "Phrase JSON round-trip failed"


# ---------------------------------------------------------------------------
# Integration: Sticky parameters
# ---------------------------------------------------------------------------


@cn_required
def test_integration_sticky_parameters() -> None:
    """Full integration test: sticky parameters carry through a complex example."""
    cn_str = "e c4 pp stacc d4 e4 q f4 mf ten g4 a4 ff"
    phrase, warnings = parse_cn(cn_str)
    assert len(phrase) == 6

    # c4: e, pp, stacc
    assert phrase[0].pitch == Pitch("c", "n", 4)
    assert phrase[0].duration.base == "e"
    assert phrase[0].dynamic == "pp"
    assert phrase[0].articulations == ("stacc",)

    # d4: inherits e, pp, stacc
    assert phrase[1].duration.base == "e"
    assert phrase[1].dynamic == "pp"
    assert phrase[1].articulations == ("stacc",)

    # e4: inherits e, pp, stacc
    assert phrase[2].duration.base == "e"
    assert phrase[2].dynamic == "pp"
    assert phrase[2].articulations == ("stacc",)

    # f4: q (new), mf (new), ten (new)
    assert phrase[3].duration.base == "q"
    assert phrase[3].dynamic == "mf"
    assert phrase[3].articulations == ("ten",)

    # g4: inherits q, mf, ten
    assert phrase[4].duration.base == "q"
    assert phrase[4].dynamic == "mf"
    assert phrase[4].articulations == ("ten",)

    # a4: inherits q, ten; ff (new dynamic)
    assert phrase[5].dynamic == "ff"
    assert phrase[5].articulations == ("ten",)


# ---------------------------------------------------------------------------
# Integration: Score with voices
# ---------------------------------------------------------------------------


@cn_required
def test_integration_score_with_voices() -> None:
    """Score correctly stores and retrieves multiple voices."""
    soprano, _ = parse_cn("q c5 mf e5 g5 c6")
    bass, _ = parse_cn("h c3 mf g3")
    score = Score.from_dict({"soprano": soprano, "bass": bass})
    assert score.voice_names == ("soprano", "bass")
    assert score["soprano"] == soprano
    assert score["bass"] == bass
    # JSON round-trip
    score_json = to_json(score)
    restored = from_json(score_json)
    assert restored == score


# ---------------------------------------------------------------------------
# Integration: Score with voices (JSON-only, no CN dependency)
# ---------------------------------------------------------------------------


def test_integration_score_with_voices_json_only() -> None:
    """Score multi-voice storage verified with JSON round-trip (no CN dependency)."""
    c5 = Pitch("c", "n", 5)
    e5 = Pitch("e", "n", 5)
    g5 = Pitch("g", "n", 5)
    c3 = Pitch("c", "n", 3)
    g3 = Pitch("g", "n", 3)
    q = Duration.from_cn("q")
    h = Duration.from_cn("h")

    soprano: Phrase = (
        Note(c5, q, "mf", ()),
        Note(e5, q, "mf", ()),
        Note(g5, q, "mf", ()),
    )
    bass: Phrase = (
        Note(c3, h, "mf", ()),
        Note(g3, h, "mf", ()),
    )
    score = Score.from_dict({"soprano": soprano, "bass": bass})
    assert score.voice_names == ("soprano", "bass")
    assert score["soprano"] == soprano
    assert score["bass"] == bass

    # JSON round-trip
    score_json = to_json(score)
    restored = from_json(score_json)
    assert restored == score
