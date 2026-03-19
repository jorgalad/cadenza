"""CN recursive descent parser with sticky parameter resolution."""

from __future__ import annotations

import re

from cadenza.core.duration import Duration
from cadenza.core.note import Event, Note, Rest
from cadenza.core.phrase import Phrase
from cadenza.core.pitch import Pitch
from cadenza.cn.errors import ParseError, ParseWarning
from cadenza.cn.tokenizer import CnTokenizer, Token, TokenType


# Regex for parsing rest token values: -[digit]letter[dots]
_REST_VALUE_RE = re.compile(r"^-(\d?)([whqestx])(\.*)$")
# Regex for parsing duration token values: [digit]letter[dots]
_DUR_VALUE_RE = re.compile(r"^(\d?)([whqestx])(\.*)$")
# Regex for parsing a single pitch component: letter + optional accidental + digits
_PITCH_COMPONENT_RE = re.compile(r"([a-g])(ss|bb|s|b|n)?(\d+)")


class CnParser:
    """Recursive descent parser for CN notation with sticky state.

    Sticky parameters (duration, dynamic, articulations) carry forward
    from one note to the next unless explicitly overridden.
    """

    def __init__(self, source: str) -> None:
        self._source = source
        self._tokenizer = CnTokenizer(source)
        self._tokens: list[Token]
        self._tokenizer_warnings: list[ParseWarning]
        self._tokens, self._tokenizer_warnings = self._tokenizer.tokenize()
        self._pos = 0
        self._warnings: list[ParseWarning] = list(self._tokenizer_warnings)

        # Sticky state
        self._current_duration: Duration | None = None
        self._current_dynamic: str | None = None
        self._current_articulations: tuple[str, ...] = ()

    def parse(self) -> tuple[Phrase, list[ParseWarning]]:
        """Parse the token stream into a Phrase."""
        events: list[Event] = []
        while not self._at_end():
            if self._check(TokenType.LPAREN):
                events.extend(self._parse_group())
            elif self._check(TokenType.EOF):
                break
            else:
                event = self._parse_event()
                if event is not None:
                    events.append(event)
        return tuple(events), self._warnings

    # ── Event parsing ────────────────────────────────────────────────

    def _parse_event(self) -> Event | None:
        """Parse a single event (Note or Rest) from the token stream."""

        # 1. Optional duration token -> update sticky duration
        if self._check(TokenType.DURATION):
            token = self._advance()
            self._current_duration = self._parse_duration_value(token.value)

        # 2. Rest token
        if self._check(TokenType.REST):
            token = self._advance()
            rest_dur = self._parse_rest_value(token.value)
            return Rest(duration=rest_dur)

        # 3. Expect pitch
        if not self._check(TokenType.PITCH):
            if self._at_end():
                return None
            token = self._peek_token()
            snippet = self._snippet(token.position)
            raise ParseError(
                message=f"Expected pitch, got {token.type.name}: '{token.value}'",
                position=token.position,
                line=token.line,
                column=token.column,
                source_snippet=snippet,
            )

        pitch_token = self._advance()
        pitch = self._parse_pitch_value(pitch_token.value)

        # 4. Optional dynamic
        if self._check(TokenType.DYNAMIC):
            self._current_dynamic = self._advance().value

        # 5. Optional articulations (one or more; replaces sticky if any present)
        new_arts: list[str] = []
        while self._check(TokenType.ARTICULATION):
            new_arts.append(self._advance().value)
        if new_arts:
            self._current_articulations = tuple(new_arts)

        # 6. Build Note with sticky values
        duration = (
            self._current_duration
            if self._current_duration is not None
            else Duration.from_cn("q")
        )
        return Note(
            pitch=pitch,
            duration=duration,
            dynamic=self._current_dynamic,
            articulations=self._current_articulations,
        )

    # ── Group parsing ────────────────────────────────────────────────

    def _parse_group(self) -> list[Event]:
        """Parse a parenthesized group of events."""
        self._expect(TokenType.LPAREN)
        events: list[Event] = []
        while not self._check(TokenType.RPAREN) and not self._at_end():
            event = self._parse_event()
            if event is not None:
                events.append(event)
        self._expect(TokenType.RPAREN)
        return events

    # ── Value parsers ────────────────────────────────────────────────

    def _parse_duration_value(self, value: str) -> Duration:
        """Parse a duration token value like 'q', 'q.', '3q', '5e.'."""
        m = _DUR_VALUE_RE.match(value)
        if not m:
            raise ValueError(f"Invalid duration value: {value!r}")
        tuplet_str, base, dots_str = m.groups()
        tuplet = int(tuplet_str) if tuplet_str else None
        dots = len(dots_str)
        return Duration.from_cn(base, dots=dots, tuplet=tuplet)

    def _parse_rest_value(self, value: str) -> Duration:
        """Parse a rest token value like '-q', '-e.', '-3q'."""
        m = _REST_VALUE_RE.match(value)
        if not m:
            raise ValueError(f"Invalid rest value: {value!r}")
        tuplet_str, base, dots_str = m.groups()
        tuplet = int(tuplet_str) if tuplet_str else None
        dots = len(dots_str)
        return Duration.from_cn(base, dots=dots, tuplet=tuplet)

    def _parse_pitch_value(self, value: str) -> Pitch:
        """Parse a pitch token value like 'c4', 'eb3', 'css4'.

        For chord tokens (c4e4g4), parses only the first pitch.
        """
        matches = list(_PITCH_COMPONENT_RE.finditer(value))
        if not matches:
            raise ValueError(f"Invalid pitch value: {value!r}")

        if len(matches) > 1:
            self._warnings.append(
                ParseWarning(
                    message=f"Chord '{value}' parsed as first pitch only (chords deferred)",
                    position=0,
                    line=1,
                    column=1,
                )
            )

        m = matches[0]
        step = m.group(1)
        acc = m.group(2) or "n"
        octave = int(m.group(3))
        return Pitch(step=step, accidental=acc, octave=octave)

    # ── Token stream helpers ─────────────────────────────────────────

    def _at_end(self) -> bool:
        return self._pos >= len(self._tokens) or self._tokens[self._pos].type == TokenType.EOF

    def _check(self, token_type: TokenType) -> bool:
        if self._at_end() and token_type != TokenType.EOF:
            return False
        return self._tokens[self._pos].type == token_type

    def _advance(self) -> Token:
        token = self._tokens[self._pos]
        self._pos += 1
        return token

    def _expect(self, token_type: TokenType) -> Token:
        if not self._check(token_type):
            token = self._peek_token()
            raise ParseError(
                message=f"Expected {token_type.name}, got {token.type.name}: '{token.value}'",
                position=token.position,
                line=token.line,
                column=token.column,
                source_snippet=self._snippet(token.position),
            )
        return self._advance()

    def _peek_token(self) -> Token:
        if self._pos < len(self._tokens):
            return self._tokens[self._pos]
        # Return a synthetic EOF token
        return Token(TokenType.EOF, "", len(self._source), 1, 1)

    def _snippet(self, position: int) -> str:
        start = max(0, position - 10)
        end = min(len(self._source), position + 20)
        return self._source[start:end]


def parse_cn(source: str) -> tuple[Phrase, list[ParseWarning]]:
    """Convenience function: parse a CN string into a Phrase."""
    return CnParser(source).parse()


