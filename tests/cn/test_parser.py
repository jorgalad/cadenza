"""Tests for CN recursive descent parser with sticky state."""

from __future__ import annotations

from fractions import Fraction

import pytest

from cadenza.cn.parser import CnParser, parse_cn
from cadenza.cn.errors import ParseError, ParseWarning
from cadenza.core.pitch import Pitch
from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest


# ── Helpers ──────────────────────────────────────────────────────────


def parse(source: str):
    """Parse CN string, return phrase tuple."""
    phrase, _ = parse_cn(source)
    return phrase


def parse_with_warnings(source: str):
    """Parse CN string, return (phrase, warnings)."""
    return parse_cn(source)


# ── Basic parsing ────────────────────────────────────────────────────


class TestBasicParsing:
    def test_single_note(self):
        phrase = parse("q c4")
        assert len(phrase) == 1
        note = phrase[0]
        assert isinstance(note, Note)
        assert note.pitch == Pitch("c", "n", 4)
        assert note.duration == Duration.from_cn("q")

    def test_empty_string(self):
        phrase = parse("")
        assert phrase == ()

    def test_pitch_accidentals(self):
        phrase = parse("q eb3 fs5 css4 dbb3")
        assert phrase[0].pitch == Pitch("e", "b", 3)
        assert phrase[1].pitch == Pitch("f", "s", 5)
        assert phrase[2].pitch == Pitch("c", "ss", 4)
        assert phrase[3].pitch == Pitch("d", "bb", 3)

    def test_octave_zero(self):
        phrase = parse("q c0")
        assert phrase[0].pitch.octave == 0

    def test_octave_ten(self):
        phrase = parse("q c10")
        assert phrase[0].pitch.octave == 10


# ── Sticky state ─────────────────────────────────────────────────────


class TestStickyState:
    def test_sticky_duration_dynamic_articulation(self):
        """'e c4 pp stacc d4 e4' -> 3 notes, d4/e4 inherit e, pp, stacc."""
        phrase = parse("e c4 pp stacc d4 e4")
        assert len(phrase) == 3
        # Note 0
        assert phrase[0].pitch == Pitch("c", "n", 4)
        assert phrase[0].duration == Duration.from_cn("e")
        assert phrase[0].dynamic == "pp"
        assert phrase[0].articulations == ("stacc",)
        # Note 1 -- sticky
        assert phrase[1].pitch == Pitch("d", "n", 4)
        assert phrase[1].duration == Duration.from_cn("e")
        assert phrase[1].dynamic == "pp"
        assert phrase[1].articulations == ("stacc",)
        # Note 2 -- sticky
        assert phrase[2].pitch == Pitch("e", "n", 4)
        assert phrase[2].duration == Duration.from_cn("e")
        assert phrase[2].dynamic == "pp"
        assert phrase[2].articulations == ("stacc",)

    def test_duration_changes_dynamic_sticks(self):
        """'q c4 mf e d4' -> first q/mf, second e/mf."""
        phrase = parse("q c4 mf e d4")
        assert phrase[0].duration == Duration.from_cn("q")
        assert phrase[0].dynamic == "mf"
        assert phrase[1].duration == Duration.from_cn("e")
        assert phrase[1].dynamic == "mf"

    def test_articulation_change_replaces(self):
        """Articulation changes replace previous sticky articulation."""
        phrase = parse("q c4 stacc d4 ten")
        assert phrase[0].articulations == ("stacc",)
        assert phrase[1].articulations == ("ten",)

    def test_multiple_articulations(self):
        """Multiple articulations on one note."""
        phrase = parse("q c4 stacc trill")
        assert phrase[0].articulations == ("stacc", "trill")


# ── Rests ────────────────────────────────────────────────────────────


class TestRests:
    def test_quarter_rest(self):
        phrase = parse("-q")
        assert len(phrase) == 1
        assert isinstance(phrase[0], Rest)
        assert phrase[0].duration == Duration.from_cn("q")

    def test_dotted_eighth_rest(self):
        phrase = parse("-e.")
        assert len(phrase) == 1
        assert isinstance(phrase[0], Rest)
        assert phrase[0].duration == Duration.from_cn("e", dots=1)

    def test_rest_in_middle(self):
        phrase = parse("q c4 -q e4")
        assert len(phrase) == 3
        assert isinstance(phrase[0], Note)
        assert isinstance(phrase[1], Rest)
        assert isinstance(phrase[2], Note)


# ── Tuplets and dots ─────────────────────────────────────────────────


class TestTupletsAndDots:
    def test_triplet_quarter(self):
        phrase = parse("3q c4")
        assert phrase[0].duration.tuplet == 3
        assert phrase[0].duration.fraction == Fraction(1, 6)

    def test_dotted_quarter(self):
        phrase = parse("q. c4")
        assert phrase[0].duration.dots == 1
        assert phrase[0].duration.fraction == Fraction(3, 8)


# ── Parenthesized groups ────────────────────────────────────────────


class TestParenthesizedGroups:
    def test_two_groups(self):
        """'(e c4 pp stacc d4 e4) (q f4 mf)' produces 4 Notes total."""
        phrase = parse("(e c4 pp stacc d4 e4) (q f4 mf)")
        assert len(phrase) == 4

    def test_sticky_across_groups(self):
        """Dynamic/duration from first group carries into second unless overridden."""
        phrase = parse("(e c4 pp d4) (g4)")
        # g4 should inherit e duration and pp dynamic from first group
        assert phrase[2].duration == Duration.from_cn("e")
        assert phrase[2].dynamic == "pp"


# ── Dynamics ─────────────────────────────────────────────────────────


class TestDynamics:
    @pytest.mark.parametrize(
        "dyn", ["ppp", "pp", "p", "mp", "mf", "f", "ff", "fff"]
    )
    def test_all_dynamics(self, dyn: str):
        phrase = parse(f"q c4 {dyn}")
        assert phrase[0].dynamic == dyn


# ── Articulations ────────────────────────────────────────────────────


class TestArticulations:
    @pytest.mark.parametrize(
        "art", ["stacc", "ten", "acc", "leg", "marc", "fermata", "trill", "pizz", "arco"]
    )
    def test_all_articulations(self, art: str):
        phrase = parse(f"q c4 {art}")
        assert art in phrase[0].articulations


# ── Warnings ─────────────────────────────────────────────────────────


class TestWarnings:
    def test_unknown_articulation_warning(self):
        phrase, warnings = parse_with_warnings("q c4 unknownthing")
        assert len(warnings) >= 1
        assert "unknownthing" in phrase[0].articulations


# ── Errors ───────────────────────────────────────────────────────────


class TestErrors:
    def test_invalid_input_raises_parse_error(self):
        with pytest.raises(ParseError):
            parse("q zzz")

    def test_parse_error_has_position(self):
        with pytest.raises(ParseError) as exc_info:
            parse("q 123badtoken")
        err = exc_info.value
        assert err.line >= 1
        assert err.column >= 1
