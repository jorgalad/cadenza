"""CN tokenizer: breaks CN notation strings into typed tokens."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto

from cadenza.cn.errors import ParseError, ParseWarning


class TokenType(Enum):
    """Types of tokens in CN notation."""

    DURATION = auto()
    REST = auto()
    PITCH = auto()
    DYNAMIC = auto()
    ARTICULATION = auto()
    LPAREN = auto()
    RPAREN = auto()
    EOF = auto()


@dataclass(frozen=True)
class Token:
    """A single token from CN source."""

    type: TokenType
    value: str
    position: int
    line: int
    column: int


# ── Vocabulary sets ──────────────────────────────────────────────────

DYNAMICS: set[str] = {
    "ppppp", "pppp", "ppp", "pp", "p",
    "mp", "mf",
    "f", "ff", "fff", "ffff", "fffff",
}

KNOWN_ARTICULATIONS: set[str] = {
    "stacc", "ten", "acc", "leg", "marc",
    "fermata", "trill", "pizz", "arco",
}

PITCH_LETTERS: set[str] = {"c", "d", "e", "f", "g", "a", "b"}

DURATION_LETTERS: set[str] = {"w", "h", "q", "e", "s", "t", "x"}

# Precompiled patterns for the word-based tokenizer
_TUPLET_DUR_RE = re.compile(r"^(\d[whqestx]\.*)$")
_REST_RE = re.compile(r"^-(\d?[whqestx]\.*)$")
_PITCH_RE = re.compile(r"^([a-g])(ss|bb|s|b|n)?(\d+)$")
_CHORD_RE = re.compile(r"^(([a-g])(ss|bb|s|b|n)?(\d+)){2,}$")
_PITCH_COMPONENT_RE = re.compile(r"([a-g])(ss|bb|s|b|n)?(\d+)")
_DUR_PLAIN_RE = re.compile(r"^([whqestx])(\.*)$")


class CnTokenizer:
    """Tokenizes CN notation strings into Token sequences.

    Uses a word-based approach: splits on whitespace and classifies each word,
    with special handling for parentheses (which may be attached to words).
    """

    def __init__(self, source: str) -> None:
        self._source = source
        self._pos = 0
        self._line = 1
        self._col = 1
        self._tokens: list[Token] = []
        self._warnings: list[ParseWarning] = []

    def tokenize(self) -> tuple[list[Token], list[ParseWarning]]:
        """Tokenize the source, returning (tokens, warnings)."""
        while self._pos < len(self._source):
            self._skip_whitespace()
            if self._pos >= len(self._source):
                break

            ch = self._source[self._pos]

            if ch == "(":
                self._tokens.append(
                    Token(TokenType.LPAREN, "(", self._pos, self._line, self._col)
                )
                self._advance()
                continue

            if ch == ")":
                self._tokens.append(
                    Token(TokenType.RPAREN, ")", self._pos, self._line, self._col)
                )
                self._advance()
                continue

            # Read a word (non-whitespace, non-paren)
            word, word_pos, word_line, word_col = self._read_word()
            if word:
                self._classify_word(word, word_pos, word_line, word_col)

        self._tokens.append(
            Token(TokenType.EOF, "", self._pos, self._line, self._col)
        )
        return self._tokens, self._warnings

    # ── Word reading ─────────────────────────────────────────────────

    def _read_word(self) -> tuple[str, int, int, int]:
        """Read the next non-whitespace, non-paren word."""
        start_pos = self._pos
        start_line = self._line
        start_col = self._col
        chars: list[str] = []
        while self._pos < len(self._source):
            ch = self._source[self._pos]
            if ch in " \t\n\r" or ch in "()" :
                break
            chars.append(ch)
            self._advance()
        return "".join(chars), start_pos, start_line, start_col

    # ── Word classification ──────────────────────────────────────────

    def _classify_word(
        self, word: str, pos: int, line: int, col: int
    ) -> None:
        """Classify a single word and append token(s)."""

        # 1. Rest: starts with '-'
        if word.startswith("-"):
            m = _REST_RE.match(word)
            if m:
                self._tokens.append(Token(TokenType.REST, word, pos, line, col))
                return
            # Could be malformed rest -- fall through to error

        # 2. Tuplet duration: digit + duration letter + optional dots (e.g., '3q', '5e.')
        if word[0].isdigit():
            m = _TUPLET_DUR_RE.match(word)
            if m:
                self._tokens.append(Token(TokenType.DURATION, word, pos, line, col))
                return

        # 3. Check for pitch: letter + optional accidental + digit(s)
        # Also handles chords (multiple pitches concatenated)
        if word[0] in PITCH_LETTERS:
            # Try chord first (multiple pitches)
            all_matches = list(_PITCH_COMPONENT_RE.finditer(word))
            if all_matches:
                # Check that the matches cover the entire word
                total_matched = sum(m.end() - m.start() for m in all_matches)
                if total_matched == len(word) and all_matches[0].start() == 0:
                    # Verify contiguous coverage
                    contiguous = True
                    for i in range(1, len(all_matches)):
                        if all_matches[i].start() != all_matches[i - 1].end():
                            contiguous = False
                            break
                    if contiguous:
                        self._tokens.append(
                            Token(TokenType.PITCH, word, pos, line, col)
                        )
                        return

        # 4. Plain duration: single duration letter + optional dots
        # Must check BEFORE dynamics/articulations because 'e', 's', etc. overlap
        m = _DUR_PLAIN_RE.match(word)
        if m:
            base_letter = m.group(1)
            # 'e' alone: could be duration eighth or pitch E.
            # We treat 'e' (without digit after) as DURATION.
            # 'f' alone: could be duration or dynamic forte.
            # 'f' is NOT a duration letter, so it won't match here.
            # 's' alone: could be duration sixteenth. But 's' might start 'stacc' etc.
            # Since we read the whole word, 's' alone IS duration sixteenth.
            if base_letter in DURATION_LETTERS:
                self._tokens.append(
                    Token(TokenType.DURATION, word, pos, line, col)
                )
                return

        # 5. Dynamic: match against known dynamics (alphabetic words)
        if word in DYNAMICS:
            self._tokens.append(Token(TokenType.DYNAMIC, word, pos, line, col))
            return

        # 6. Known articulation
        if word in KNOWN_ARTICULATIONS:
            self._tokens.append(
                Token(TokenType.ARTICULATION, word, pos, line, col)
            )
            return

        # 7. Unknown alphabetic word -> articulation + warning
        if word.isalpha():
            self._tokens.append(
                Token(TokenType.ARTICULATION, word, pos, line, col)
            )
            self._warnings.append(
                ParseWarning(
                    message=f"Unknown articulation: '{word}'",
                    position=pos,
                    line=line,
                    column=col,
                )
            )
            return

        # 8. Unrecognized -> error
        snippet = self._source[max(0, pos - 10) : pos + 20]
        raise ParseError(
            message=f"Unexpected token: '{word}'",
            position=pos,
            line=line,
            column=col,
            source_snippet=snippet,
        )

    # ── Low-level helpers ────────────────────────────────────────────

    def _skip_whitespace(self) -> None:
        while self._pos < len(self._source) and self._source[self._pos] in " \t\n\r":
            if self._source[self._pos] == "\n":
                self._line += 1
                self._col = 1
            else:
                self._col += 1
            self._pos += 1

    def _advance(self) -> str:
        ch = self._source[self._pos]
        self._pos += 1
        if ch == "\n":
            self._line += 1
            self._col = 1
        else:
            self._col += 1
        return ch

    def _peek(self) -> str | None:
        if self._pos < len(self._source):
            return self._source[self._pos]
        return None


