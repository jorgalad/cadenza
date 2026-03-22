"""L-system melody generation (ALGO-03).

Stub -- tests should fail.
"""

from __future__ import annotations

from cadenza.core.note import Event
from cadenza.core.phrase import Phrase


def lsystem_melody(
    axiom: str,
    rules: dict[str, str],
    alphabet: dict[str, Event],
    generations: int,
) -> Phrase:
    raise NotImplementedError
