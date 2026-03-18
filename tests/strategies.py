"""Hypothesis custom strategies for cadenza property-based tests."""

from __future__ import annotations

from hypothesis import assume, strategies as st
from hypothesis.strategies import composite

from cadenza.core.pitch import Pitch
from cadenza.core.duration import Duration


STEPS = ["c", "d", "e", "f", "g", "a", "b"]
ACCIDENTALS = ["n", "s", "b", "ss", "bb"]
DYNAMICS = ["ppp", "pp", "p", "mp", "mf", "f", "ff", "fff", None]
ARTICULATIONS = ["stacc", "ten", "acc", "leg", "marc", "fermata", "trill", "pizz", "arco"]
BASES = ["w", "h", "q", "e", "s", "t"]


@composite
def pitch_strategy(draw: st.DrawFn) -> Pitch:
    step = draw(st.sampled_from(STEPS))
    acc = draw(st.sampled_from(ACCIDENTALS))
    octave = draw(st.integers(min_value=0, max_value=9))
    p = Pitch(step=step, accidental=acc, octave=octave)
    # Filter out pitches with invalid MIDI numbers
    assume(0 <= p.midi_number <= 127)
    return p


@composite
def duration_strategy(draw: st.DrawFn) -> Duration:
    base = draw(st.sampled_from(BASES))
    dots = draw(st.integers(min_value=0, max_value=2))
    use_tuplet = draw(st.booleans())
    tuplet = draw(st.integers(min_value=3, max_value=7)) if use_tuplet else None
    return Duration.from_omn(base, dots=dots, tuplet=tuplet)
