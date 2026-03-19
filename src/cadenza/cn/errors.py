"""CN parsing error types."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ParseError(Exception):
    """Error raised when CN parsing fails."""

    message: str
    position: int = 0
    line: int = 1
    column: int = 1
    source_snippet: str = ""

    def __str__(self) -> str:
        return f"ParseError at line {self.line}, column {self.column}: {self.message}"


@dataclass(frozen=True)
class ParseWarning:
    """Warning issued during CN parsing (e.g., unknown articulation)."""

    message: str
    position: int = 0
    line: int = 1
    column: int = 1
