"""Tests for voice leading violation detection and voice leading generation."""

from __future__ import annotations

from fractions import Fraction

import pytest

from cadenza.core.pitch import Pitch
from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest
from cadenza.core.score import Score
from cadenza.analysis.voiceleading import VoiceLeadingViolation, check_voice_leading, smooth_voice_leading


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

Q = Duration(fraction=Fraction(1, 4))  # quarter note


def _n(step: str, acc: str, octave: int) -> Note:
    """Shorthand for creating a quarter note."""
    return Note(pitch=Pitch(step=step, accidental=acc, octave=octave), duration=Q)


def _r() -> Rest:
    """Shorthand for creating a quarter rest."""
    return Rest(duration=Q)


# ---------------------------------------------------------------------------
# Parallel fifths
# ---------------------------------------------------------------------------


def test_parallel_fifths():
    """Two voices moving C4->D4 and F3->G3 form P5->P5 in same direction."""
    score = Score.from_dict({
        "soprano": (_n("c", "n", 4), _n("d", "n", 4)),
        "bass": (_n("f", "n", 3), _n("g", "n", 3)),
    })
    violations = check_voice_leading(score)
    pf = [v for v in violations if v.rule == "parallel_fifth"]
    assert len(pf) == 1
    assert pf[0].severity == "error"
    assert pf[0].position == 1


def test_parallel_fifths_contrary_motion_no_flag():
    """Contrary motion arriving at fifths should NOT flag parallel fifths."""
    # Soprano descends G4->D4, Bass ascends C3->G3.
    # At pos 0: G4-C3 = P5 (mod12=7). At pos 1: D4-G3 = P5 (mod12=7).
    # But motion is contrary (soprano goes down, bass goes up), so no flag.
    score = Score.from_dict({
        "soprano": (_n("g", "n", 4), _n("d", "n", 4)),
        "bass": (_n("c", "n", 3), _n("g", "n", 3)),
    })
    violations = check_voice_leading(score)
    pf = [v for v in violations if v.rule == "parallel_fifth"]
    assert len(pf) == 0


def test_parallel_fifths_oblique_no_flag():
    """One stationary voice forming fifths should NOT flag parallel fifths."""
    # Soprano stays on G4, Bass moves C3->C3 (stationary too — but let's do one moving)
    # Actually: soprano stays G4, bass moves C3->D3. Pos0: G4-C3=P5. Pos1: G4-D3 != P5.
    # Better: soprano stays D4, bass moves G3->G3. Both intervals are P5 but bass is stationary.
    score = Score.from_dict({
        "soprano": (_n("d", "n", 4), _n("d", "n", 4)),
        "bass": (_n("g", "n", 3), _n("g", "n", 3)),
    })
    violations = check_voice_leading(score)
    pf = [v for v in violations if v.rule == "parallel_fifth"]
    assert len(pf) == 0


# ---------------------------------------------------------------------------
# Parallel octaves
# ---------------------------------------------------------------------------


def test_parallel_octaves():
    """Two voices moving C4->D4 and C3->D3 form P8->P8."""
    score = Score.from_dict({
        "soprano": (_n("c", "n", 4), _n("d", "n", 4)),
        "bass": (_n("c", "n", 3), _n("d", "n", 3)),
    })
    violations = check_voice_leading(score)
    po = [v for v in violations if v.rule == "parallel_octave"]
    assert len(po) == 1
    assert po[0].severity == "error"
    assert po[0].position == 1


def test_parallel_octaves_compound():
    """Compound octave (P15, 24 semitones) should be flagged as parallel octaves."""
    # Soprano C5->D5, Bass C3->D3: distance = 24 semitones (two octaves), mod12=0
    score = Score.from_dict({
        "soprano": (_n("c", "n", 5), _n("d", "n", 5)),
        "bass": (_n("c", "n", 3), _n("d", "n", 3)),
    })
    violations = check_voice_leading(score)
    po = [v for v in violations if v.rule == "parallel_octave"]
    assert len(po) == 1


def test_parallel_unison():
    """Unison (P1, 0 semitones mod12=0) flagged as parallel octaves."""
    # Both voices move C4->D4 in unison
    score = Score.from_dict({
        "soprano": (_n("c", "n", 4), _n("d", "n", 4)),
        "alto": (_n("c", "n", 4), _n("d", "n", 4)),
    })
    violations = check_voice_leading(score)
    po = [v for v in violations if v.rule == "parallel_octave"]
    assert len(po) == 1


# ---------------------------------------------------------------------------
# Voice crossing
# ---------------------------------------------------------------------------


def test_voice_crossing():
    """Alto goes above soprano at position 1."""
    score = Score.from_dict({
        "soprano": (_n("c", "n", 4), _n("c", "n", 4)),
        "alto": (_n("e", "n", 3), _n("d", "n", 5)),
    })
    violations = check_voice_leading(score)
    vc = [v for v in violations if v.rule == "voice_crossing"]
    assert len(vc) == 1
    assert vc[0].severity == "error"
    assert vc[0].position == 1


def test_voice_crossing_uses_score_order():
    """First voice in Score tuple order is 'upper'."""
    # "alto" listed first, "soprano" listed second.
    # At pos 0: alto=C4, soprano=G4 -> soprano > alto -> crossing (lower exceeds upper).
    # Wait, "upper" = first in tuple. So alto is upper, soprano is lower.
    # Crossing = lower.midi > upper.midi. At pos 0: soprano(G4=67) > alto(C4=60) -> crossing!
    score = Score.from_dict({
        "alto": (_n("c", "n", 4), _n("c", "n", 4)),
        "soprano": (_n("g", "n", 4), _n("g", "n", 4)),
    })
    violations = check_voice_leading(score)
    vc = [v for v in violations if v.rule == "voice_crossing"]
    # Lower voice (soprano, second in tuple) exceeds upper (alto, first in tuple)
    assert len(vc) == 2  # crossing at both positions


# ---------------------------------------------------------------------------
# Voice overlap
# ---------------------------------------------------------------------------


def test_voice_overlap():
    """Soprano goes below alto's previous position."""
    # Soprano: G4, C4. Alto: D4, E4.
    # At pos 1: soprano(C4=60) < alto_prev(D4=62) -> overlap, position=1
    score = Score.from_dict({
        "soprano": (_n("g", "n", 4), _n("c", "n", 4)),
        "alto": (_n("d", "n", 4), _n("e", "n", 4)),
    })
    violations = check_voice_leading(score)
    vo = [v for v in violations if v.rule == "voice_overlap"]
    assert len(vo) == 1
    assert vo[0].severity == "warning"
    assert vo[0].position == 1


# ---------------------------------------------------------------------------
# Leap analysis
# ---------------------------------------------------------------------------


def test_large_leap():
    """A voice moving C4 to D5 (14 semitones, >12) is a large leap."""
    score = Score.from_dict({
        "soprano": (_n("c", "n", 4), _n("d", "n", 5)),
    })
    violations = check_voice_leading(score)
    ll = [v for v in violations if v.rule == "large_leap"]
    assert len(ll) == 1
    assert ll[0].severity == "warning"


def test_augmented_leap():
    """C4 to G#4 (augmented fifth) flagged as augmented_leap."""
    score = Score.from_dict({
        "soprano": (_n("c", "n", 4), _n("g", "s", 4)),
    })
    violations = check_voice_leading(score)
    al = [v for v in violations if v.rule == "augmented_leap"]
    assert len(al) == 1
    assert al[0].severity == "suggestion"


def test_diminished_leap():
    """B3 to F4 (diminished fifth) flagged as augmented_leap rule."""
    score = Score.from_dict({
        "soprano": (_n("b", "n", 3), _n("f", "n", 4)),
    })
    violations = check_voice_leading(score)
    al = [v for v in violations if v.rule == "augmented_leap"]
    assert len(al) == 1
    assert al[0].severity == "suggestion"


# ---------------------------------------------------------------------------
# Rest handling
# ---------------------------------------------------------------------------


def test_rest_skipped():
    """Position with a rest produces no violation for that position pair."""
    score = Score.from_dict({
        "soprano": (_n("c", "n", 4), _r(), _n("d", "n", 4)),
        "bass": (_n("c", "n", 3), _n("d", "n", 3), _n("d", "n", 3)),
    })
    violations = check_voice_leading(score)
    # No parallel octave at pos 1 because soprano has rest
    po = [v for v in violations if v.rule == "parallel_octave"]
    assert len(po) == 0


# ---------------------------------------------------------------------------
# Orchestrator behavior
# ---------------------------------------------------------------------------


def test_check_voice_leading_returns_sorted():
    """Multiple violations at different positions are sorted by position."""
    # Create score with violations at multiple positions
    # Soprano: C4, D4, E4; Bass: C3, D3, E3 — parallel octaves at pos 1 and 2
    score = Score.from_dict({
        "soprano": (_n("c", "n", 4), _n("d", "n", 4), _n("e", "n", 4)),
        "bass": (_n("c", "n", 3), _n("d", "n", 3), _n("e", "n", 3)),
    })
    violations = check_voice_leading(score)
    positions = [v.position for v in violations]
    assert positions == sorted(positions)


def test_check_voice_leading_empty_score():
    """Empty score returns empty list."""
    score = Score(_voices=())
    violations = check_voice_leading(score)
    assert violations == []


def test_check_voice_leading_single_voice():
    """Single voice returns only leap violations, no pair checks."""
    # C4 to D5 = 14 semitones = large leap
    score = Score.from_dict({
        "soprano": (_n("c", "n", 4), _n("d", "n", 5)),
    })
    violations = check_voice_leading(score)
    # Should have large_leap but no parallel/crossing/overlap
    rules = {v.rule for v in violations}
    assert "parallel_fifth" not in rules
    assert "parallel_octave" not in rules
    assert "voice_crossing" not in rules
    assert "voice_overlap" not in rules
    assert "large_leap" in rules


# ---------------------------------------------------------------------------
# smooth_voice_leading
# ---------------------------------------------------------------------------


def test_smooth_voice_leading_basic():
    """Identity mapping C4,E4,G4 -> B3,D4,F4 gives cost 5 (optimal)."""
    chord1 = (Pitch("c", "n", 4), Pitch("e", "n", 4), Pitch("g", "n", 4))
    chord2 = (Pitch("b", "n", 3), Pitch("d", "n", 4), Pitch("f", "n", 4))
    result = smooth_voice_leading(chord1, chord2)
    assert isinstance(result, tuple)
    assert len(result) == 3
    # Total movement should be <= 5 (the identity cost)
    total = sum(abs(p1.midi_number - p2.midi_number) for p1, p2 in zip(chord1, result))
    assert total <= 5


def test_smooth_voice_leading_reorder():
    """Verify that reordering actually occurs when beneficial.

    chord1=(C4,G4,E5), chord2=(D4,F4,B4).
    Identity: |60-62|+|67-65|+|76-71| = 2+2+5 = 9
    (F4,B4,D4): |60-65|+|67-71|+|76-62| = 5+4+14 = 23
    (D4,B4,F4): |60-62|+|67-71|+|76-65| = 2+4+11 = 17
    (F4,D4,B4): |60-65|+|67-62|+|76-71| = 5+5+5 = 15
    (B4,D4,F4): |60-71|+|67-62|+|76-65| = 11+5+11 = 27
    (B4,F4,D4): |60-71|+|67-65|+|76-62| = 11+2+14 = 27
    Best is identity with cost 9.

    Better example forcing reorder:
    chord1=(C4,E4,C5), chord2=(D4,B4,F4).
    Identity: |60-62|+|64-71|+|72-65| = 2+7+7 = 16
    (D4,F4,B4): |60-62|+|64-65|+|72-71| = 2+1+1 = 4  <-- best
    """
    chord1 = (Pitch("c", "n", 4), Pitch("e", "n", 4), Pitch("c", "n", 5))
    chord2 = (Pitch("d", "n", 4), Pitch("b", "n", 4), Pitch("f", "n", 4))
    result = smooth_voice_leading(chord1, chord2)
    assert result == (Pitch("d", "n", 4), Pitch("f", "n", 4), Pitch("b", "n", 4))


def test_smooth_voice_leading_size_mismatch():
    """Mismatched chord sizes raise ValueError."""
    chord1 = (Pitch("c", "n", 4), Pitch("e", "n", 4), Pitch("g", "n", 4))
    chord2 = (Pitch("d", "n", 4), Pitch("f", "n", 4), Pitch("a", "n", 4), Pitch("c", "n", 5))
    with pytest.raises(ValueError, match="Chord size mismatch"):
        smooth_voice_leading(chord1, chord2)


def test_smooth_voice_leading_single_note():
    """Single-note chords return trivially."""
    chord1 = (Pitch("c", "n", 4),)
    chord2 = (Pitch("d", "n", 4),)
    result = smooth_voice_leading(chord1, chord2)
    assert result == (Pitch("d", "n", 4),)


def test_smooth_voice_leading_identical():
    """Identical chords return identity with cost 0."""
    chord = (Pitch("c", "n", 4), Pitch("e", "n", 4), Pitch("g", "n", 4))
    result = smooth_voice_leading(chord, chord)
    assert result == chord
