"""Tests for OMN tokenizer."""

from __future__ import annotations

import pytest

from cadenza.omn.tokenizer import OmnTokenizer, Token, TokenType
from cadenza.omn.errors import ParseError, ParseWarning


# ── Helpers ──────────────────────────────────────────────────────────


def tokenize(source: str) -> list[Token]:
    """Tokenize source, return tokens (excluding EOF)."""
    tokens, _ = OmnTokenizer(source).tokenize()
    return [t for t in tokens if t.type != TokenType.EOF]


def tokenize_with_warnings(source: str) -> tuple[list[Token], list[ParseWarning]]:
    """Tokenize source, return tokens and warnings."""
    tokens, warnings = OmnTokenizer(source).tokenize()
    return [t for t in tokens if t.type != TokenType.EOF], warnings


# ── Duration tokens ──────────────────────────────────────────────────


class TestDurationTokens:
    def test_quarter(self):
        tokens = tokenize("q")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.DURATION
        assert tokens[0].value == "q"

    def test_dotted_quarter(self):
        tokens = tokenize("q.")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.DURATION
        assert tokens[0].value == "q."

    def test_double_dotted_quarter(self):
        tokens = tokenize("q..")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.DURATION
        assert tokens[0].value == "q.."

    def test_tuplet_quarter(self):
        tokens = tokenize("3q")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.DURATION
        assert tokens[0].value == "3q"

    def test_tuplet_eighth(self):
        tokens = tokenize("5e")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.DURATION
        assert tokens[0].value == "5e"

    @pytest.mark.parametrize("base", ["w", "h", "q", "e", "s", "t", "x"])
    def test_all_base_durations(self, base: str):
        tokens = tokenize(base)
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.DURATION
        assert tokens[0].value == base


# ── Rest tokens ──────────────────────────────────────────────────────


class TestRestTokens:
    def test_quarter_rest(self):
        tokens = tokenize("-q")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.REST
        assert tokens[0].value == "-q"

    def test_dotted_eighth_rest(self):
        tokens = tokenize("-e.")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.REST
        assert tokens[0].value == "-e."

    def test_tuplet_rest(self):
        tokens = tokenize("-3q")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.REST
        assert tokens[0].value == "-3q"


# ── Pitch tokens ─────────────────────────────────────────────────────


class TestPitchTokens:
    def test_c4(self):
        tokens = tokenize("c4")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.PITCH
        assert tokens[0].value == "c4"

    def test_eb3(self):
        tokens = tokenize("eb3")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.PITCH
        assert tokens[0].value == "eb3"

    def test_fs5(self):
        tokens = tokenize("fs5")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.PITCH
        assert tokens[0].value == "fs5"

    def test_double_sharp(self):
        tokens = tokenize("css4")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.PITCH
        assert tokens[0].value == "css4"

    def test_double_flat(self):
        tokens = tokenize("dbb3")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.PITCH
        assert tokens[0].value == "dbb3"

    def test_chord_single_token(self):
        """Chord: multiple pitches concatenated without spaces."""
        tokens = tokenize("c4e4g4")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.PITCH
        assert tokens[0].value == "c4e4g4"


# ── Dynamic tokens ───────────────────────────────────────────────────


class TestDynamicTokens:
    def test_pp(self):
        tokens = tokenize("pp")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.DYNAMIC
        assert tokens[0].value == "pp"

    @pytest.mark.parametrize("dyn", ["ppp", "pp", "p", "mp", "mf", "f", "ff", "fff"])
    def test_all_dynamics(self, dyn: str):
        tokens = tokenize(dyn)
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.DYNAMIC
        assert tokens[0].value == dyn


# ── Articulation tokens ──────────────────────────────────────────────


class TestArticulationTokens:
    def test_stacc(self):
        tokens = tokenize("stacc")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.ARTICULATION
        assert tokens[0].value == "stacc"

    @pytest.mark.parametrize(
        "art", ["stacc", "ten", "acc", "leg", "marc", "fermata", "trill", "pizz", "arco"]
    )
    def test_all_phase1_articulations(self, art: str):
        tokens = tokenize(art)
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.ARTICULATION
        assert tokens[0].value == art


# ── Paren tokens ─────────────────────────────────────────────────────


class TestParenTokens:
    def test_lparen(self):
        tokens = tokenize("(")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.LPAREN

    def test_rparen(self):
        tokens = tokenize(")")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.RPAREN


# ── Unknown articulation ─────────────────────────────────────────────


class TestUnknownArticulation:
    def test_unknown_emits_warning(self):
        tokens, warnings = tokenize_with_warnings("unknownthing")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.ARTICULATION
        assert tokens[0].value == "unknownthing"
        assert len(warnings) >= 1
        assert "unknownthing" in warnings[0].message


# ── Position tracking ────────────────────────────────────────────────


class TestPositionTracking:
    def test_position_line_column(self):
        tokens = tokenize("q c4")
        assert tokens[0].position == 0
        assert tokens[0].line == 1
        assert tokens[0].column == 1
        assert tokens[1].position == 2
        assert tokens[1].line == 1
        assert tokens[1].column == 3


# ── Disambiguation ───────────────────────────────────────────────────


class TestDisambiguation:
    def test_e_then_pitch_is_duration(self):
        """'e c4' -> DURATION('e'), PITCH('c4')."""
        tokens = tokenize("e c4")
        assert tokens[0].type == TokenType.DURATION
        assert tokens[0].value == "e"
        assert tokens[1].type == TokenType.PITCH
        assert tokens[1].value == "c4"

    def test_e4_is_pitch(self):
        """'e4' alone -> PITCH('e4')."""
        tokens = tokenize("e4")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.PITCH
        assert tokens[0].value == "e4"

    def test_f_as_dynamic(self):
        """'f' in dynamic position -> DYNAMIC."""
        tokens = tokenize("f")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.DYNAMIC
        assert tokens[0].value == "f"

    def test_f4_is_pitch(self):
        """'f4' -> PITCH."""
        tokens = tokenize("f4")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.PITCH
        assert tokens[0].value == "f4"


# ── Whitespace handling ──────────────────────────────────────────────


class TestWhitespace:
    def test_multiple_spaces(self):
        tokens = tokenize("q   c4")
        assert len(tokens) == 2

    def test_tabs(self):
        tokens = tokenize("q\tc4")
        assert len(tokens) == 2

    def test_multiline_tracking(self):
        tokens = tokenize("q\nc4")
        assert len(tokens) == 2
        assert tokens[0].line == 1
        assert tokens[1].line == 2
        assert tokens[1].column == 1


# ── Compound expressions ─────────────────────────────────────────────


class TestCompoundExpressions:
    def test_full_omn_phrase(self):
        """Tokenize a realistic OMN phrase."""
        tokens = tokenize("e c4 pp stacc d4 e4")
        types = [t.type for t in tokens]
        assert types == [
            TokenType.DURATION,
            TokenType.PITCH,
            TokenType.DYNAMIC,
            TokenType.ARTICULATION,
            TokenType.PITCH,
            TokenType.PITCH,
        ]

    def test_parenthesized_groups(self):
        tokens = tokenize("(e c4 pp stacc d4 e4) (q f4 mf)")
        types = [t.type for t in tokens]
        assert types == [
            TokenType.LPAREN,
            TokenType.DURATION,
            TokenType.PITCH,
            TokenType.DYNAMIC,
            TokenType.ARTICULATION,
            TokenType.PITCH,
            TokenType.PITCH,
            TokenType.RPAREN,
            TokenType.LPAREN,
            TokenType.DURATION,
            TokenType.PITCH,
            TokenType.DYNAMIC,
            TokenType.RPAREN,
        ]

    def test_rest_in_phrase(self):
        tokens = tokenize("q c4 -q e4")
        types = [t.type for t in tokens]
        assert types == [
            TokenType.DURATION,
            TokenType.PITCH,
            TokenType.REST,
            TokenType.PITCH,
        ]
