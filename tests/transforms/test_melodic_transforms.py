"""Tests for melodic transforms (MELO-01 through MELO-12 + chaining)."""

from __future__ import annotations

from fractions import Fraction

import pytest

from cadenza.core.duration import Duration
from cadenza.core.interval import Interval
from cadenza.core.note import Note, Rest
from cadenza.core.phrase import Phrase
from cadenza.core.pitch import Pitch
from cadenza.transforms.melodic import (
    concatenate,
    fragment,
    full_retrograde,
    interpolate,
    interleave,
    mirror,
    omit,
    permute,
    pitch_map,
    pitch_retrograde,
    repeat,
    retrograde_inversion,
    rotate,
)
from cadenza.transforms.pitch import chromatic_transpose, invert


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _p(step: str, acc: str = "n", octave: int = 4) -> Pitch:
    return Pitch(step=step, accidental=acc, octave=octave)


def _n(step: str, acc: str = "n", octave: int = 4, dur: str = "q") -> Note:
    return Note(pitch=_p(step, acc, octave), duration=Duration.from_omn(dur))


def _r(dur: str = "q") -> Rest:
    return Rest(duration=Duration.from_omn(dur))


# ---------------------------------------------------------------------------
# MELO-01: pitch_retrograde
# ---------------------------------------------------------------------------

class TestPitchRetrograde:
    def test_pitch_retrograde_basic(self, simple_phrase: Phrase) -> None:
        """[C4(q), E4(e), G4(h)] -> pitches [G4, E4, C4] with durations [q, e, h]."""
        result = pitch_retrograde(simple_phrase)
        assert len(result) == 3
        # Pitches reversed
        assert result[0].pitch == _p("g")  # type: ignore[union-attr]
        assert result[1].pitch == _p("e")  # type: ignore[union-attr]
        assert result[2].pitch == _p("c")  # type: ignore[union-attr]
        # Durations preserved in original order
        assert result[0].duration == Duration.from_omn("q")
        assert result[1].duration == Duration.from_omn("e")
        assert result[2].duration == Duration.from_omn("h")

    def test_pitch_retrograde_with_rests(self, phrase_with_rests: Phrase) -> None:
        """[C4(q), Rest(e), E4(q), Rest(e)] -> [E4(q), Rest(e), C4(q), Rest(e)]."""
        result = pitch_retrograde(phrase_with_rests)
        assert len(result) == 4
        assert isinstance(result[0], Note)
        assert result[0].pitch == _p("e")
        assert isinstance(result[1], Rest)
        assert isinstance(result[2], Note)
        assert result[2].pitch == _p("c")
        assert isinstance(result[3], Rest)

    def test_pitch_retrograde_empty(self) -> None:
        result = pitch_retrograde(())
        assert result == ()

    def test_pitch_retrograde_preserves_dynamics(self) -> None:
        """Dynamic and articulations on notes are preserved."""
        phrase = (
            Note(pitch=_p("c"), duration=Duration.from_omn("q"), dynamic="pp"),
            Note(pitch=_p("e"), duration=Duration.from_omn("q"), dynamic="ff", articulations=("stacc",)),
        )
        result = pitch_retrograde(phrase)
        # Pitches reversed, but dynamics/articulations stay with original note position
        assert result[0].pitch == _p("e")  # type: ignore[union-attr]
        assert result[0].dynamic == "pp"  # type: ignore[union-attr]
        assert result[1].pitch == _p("c")  # type: ignore[union-attr]
        assert result[1].dynamic == "ff"  # type: ignore[union-attr]
        assert result[1].articulations == ("stacc",)  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# MELO-02: retrograde_inversion
# ---------------------------------------------------------------------------

class TestRetrogradeInversion:
    def test_retrograde_inversion_basic(self) -> None:
        """[C4, E4, G4] -> pitch_retrograde [G4, E4, C4] -> invert around G4."""
        phrase = (_n("c"), _n("e"), _n("g"))
        result = retrograde_inversion(phrase)
        # After pitch_retrograde: pitches are [G4, E4, C4]
        # Default axis = first note of retrograded = G4
        # Invert around G4: G4 stays, E4 (m3 below) -> Bb4 (m3 above), C4 (P5 below) -> D5 (P5 above)
        assert len(result) == 3
        assert result[0].pitch == _p("g")  # type: ignore[union-attr]

    def test_retrograde_inversion_with_axis(self) -> None:
        """Accepts optional axis parameter."""
        phrase = (_n("c"), _n("e"), _n("g"))
        result = retrograde_inversion(phrase, axis=_p("c"))
        assert len(result) == 3

    def test_retrograde_inversion_empty(self) -> None:
        assert retrograde_inversion(()) == ()


# ---------------------------------------------------------------------------
# MELO-03 (full_retrograde)
# ---------------------------------------------------------------------------

class TestFullRetrograde:
    def test_full_retrograde_basic(self, simple_phrase: Phrase) -> None:
        """[C4(q), E4(e), G4(h)] -> [G4(h), E4(e), C4(q)]."""
        result = full_retrograde(simple_phrase)
        assert len(result) == 3
        assert result[0].pitch == _p("g")  # type: ignore[union-attr]
        assert result[0].duration == Duration.from_omn("h")
        assert result[2].pitch == _p("c")  # type: ignore[union-attr]
        assert result[2].duration == Duration.from_omn("q")

    def test_full_retrograde_empty(self) -> None:
        assert full_retrograde(()) == ()


# ---------------------------------------------------------------------------
# MELO-03 (rotate)
# ---------------------------------------------------------------------------

class TestRotate:
    def test_rotate_positive(self) -> None:
        """[A, B, C] rotate +1 -> [B, C, A]."""
        phrase = (_n("a"), _n("b"), _n("c"))
        result = rotate(phrase, 1)
        assert result[0].pitch == _p("b")  # type: ignore[union-attr]
        assert result[1].pitch == _p("c")  # type: ignore[union-attr]
        assert result[2].pitch == _p("a")  # type: ignore[union-attr]

    def test_rotate_negative(self) -> None:
        """[A, B, C] rotate -1 -> [C, A, B]."""
        phrase = (_n("a"), _n("b"), _n("c"))
        result = rotate(phrase, -1)
        assert result[0].pitch == _p("c")  # type: ignore[union-attr]
        assert result[1].pitch == _p("a")  # type: ignore[union-attr]
        assert result[2].pitch == _p("b")  # type: ignore[union-attr]

    def test_rotate_zero(self) -> None:
        phrase = (_n("c"), _n("d"))
        result = rotate(phrase, 0)
        assert result[0].pitch == _p("c")  # type: ignore[union-attr]
        assert result[1].pitch == _p("d")  # type: ignore[union-attr]

    def test_rotate_empty(self) -> None:
        assert rotate((), 5) == ()


# ---------------------------------------------------------------------------
# MELO-04: permute
# ---------------------------------------------------------------------------

class TestPermute:
    def test_permute_basic(self) -> None:
        """[A, B, C] permute [2, 0, 1] -> [C, A, B]."""
        phrase = (_n("a"), _n("b"), _n("c"))
        result = permute(phrase, [2, 0, 1])
        assert result[0].pitch == _p("c")  # type: ignore[union-attr]
        assert result[1].pitch == _p("a")  # type: ignore[union-attr]
        assert result[2].pitch == _p("b")  # type: ignore[union-attr]

    def test_permute_invalid_length(self) -> None:
        phrase = (_n("a"), _n("b"))
        with pytest.raises((ValueError, IndexError)):
            permute(phrase, [0, 1, 2])

    def test_permute_invalid_index(self) -> None:
        phrase = (_n("a"), _n("b"))
        with pytest.raises((ValueError, IndexError)):
            permute(phrase, [0, 5])


# ---------------------------------------------------------------------------
# MELO-05: interpolate
# ---------------------------------------------------------------------------

class TestInterpolate:
    def test_interpolate_one_step(self) -> None:
        """[C4(q), E4(q)] with 1 step -> inserts chromatic passing notes."""
        q = Duration.from_omn("q")
        phrase = (_n("c", dur="q"), _n("e", dur="q"))
        result = interpolate(phrase, steps=1)
        # Between C4 and E4 (4 semitones), 1 passing note = C#4/Db4
        # Original C4 duration subdivided: q/2 = e for each
        assert len(result) >= 3  # at least: C4, passing, E4

    def test_interpolate_preserves_last_note(self) -> None:
        """Last note in phrase is always kept unchanged."""
        phrase = (_n("c", dur="q"), _n("d", dur="q"))
        result = interpolate(phrase, steps=1)
        # Last note should be D4 with original duration
        assert isinstance(result[-1], Note)
        assert result[-1].pitch == _p("d")

    def test_interpolate_with_rests_no_interpolation(self) -> None:
        """No interpolation before/after rests."""
        phrase = (_n("c", dur="q"), _r("e"), _n("e", dur="q"))
        result = interpolate(phrase, steps=1)
        # Should not insert passing notes around the rest
        # C4 -> Rest -> E4: no interpolation at rest boundaries
        assert any(isinstance(e, Rest) for e in result)

    def test_interpolate_empty(self) -> None:
        assert interpolate((), steps=1) == ()

    def test_interpolate_single_note(self) -> None:
        result = interpolate((_n("c"),), steps=1)
        assert len(result) == 1


# ---------------------------------------------------------------------------
# MELO-06: omit
# ---------------------------------------------------------------------------

class TestOmit:
    def test_omit_every_2nd(self) -> None:
        """Every 2nd note: [A,B,C,D] -> [A,C] (remove indices 1,3)."""
        phrase = (_n("a"), _n("b"), _n("c"), _n("d"))
        result = omit(phrase, n=2)
        assert len(result) == 2
        assert result[0].pitch == _p("a")  # type: ignore[union-attr]
        assert result[1].pitch == _p("c")  # type: ignore[union-attr]

    def test_omit_by_predicate(self) -> None:
        """Remove notes where pitch step == 'c'."""
        phrase = (_n("c"), _n("d"), _n("c", octave=5), _n("e"))
        result = omit(phrase, predicate=lambda e: isinstance(e, Note) and e.pitch.step == "c")
        assert len(result) == 2
        assert result[0].pitch == _p("d")  # type: ignore[union-attr]
        assert result[1].pitch == _p("e")  # type: ignore[union-attr]

    def test_omit_both_raises(self) -> None:
        """Providing both n and predicate raises ValueError."""
        phrase = (_n("c"),)
        with pytest.raises(ValueError):
            omit(phrase, n=2, predicate=lambda e: True)

    def test_omit_neither_raises(self) -> None:
        """Providing neither n nor predicate raises ValueError."""
        phrase = (_n("c"),)
        with pytest.raises(ValueError):
            omit(phrase)


# ---------------------------------------------------------------------------
# MELO-07: repeat
# ---------------------------------------------------------------------------

class TestRepeat:
    def test_repeat_basic(self) -> None:
        """Repeat N=3 -> phrase concatenated 3 times."""
        phrase = (_n("c"), _n("d"))
        result = repeat(phrase, 3)
        assert len(result) == 6

    def test_repeat_with_variation(self) -> None:
        """Variation callback applied to each repetition."""
        phrase = (_n("c"), _n("d"))
        # Variation: on repetition 1+, transpose up an octave (simulate by just returning phrase)
        def var(i: int, p: Phrase) -> Phrase:
            if i == 0:
                return p
            # Return notes shifted up
            return tuple(
                Note(pitch=Pitch(step=e.pitch.step, accidental=e.pitch.accidental, octave=e.pitch.octave + 1),
                     duration=e.duration)
                if isinstance(e, Note) else e
                for e in p
            )
        result = repeat(phrase, 2, variation=var)
        assert len(result) == 4
        # First pair: octave 4
        assert result[0].pitch.octave == 4  # type: ignore[union-attr]
        # Second pair: octave 5
        assert result[2].pitch.octave == 5  # type: ignore[union-attr]

    def test_repeat_zero(self) -> None:
        result = repeat((_n("c"),), 0)
        assert result == ()


# ---------------------------------------------------------------------------
# MELO-08: mirror
# ---------------------------------------------------------------------------

class TestMirror:
    def test_mirror_basic(self) -> None:
        """[C4,E4,G4] -> phrase + full_retrograde(phrase)."""
        phrase = (_n("c"), _n("e"), _n("g"))
        result = mirror(phrase)
        assert len(result) == 6
        # First half is original
        assert result[0].pitch == _p("c")  # type: ignore[union-attr]
        assert result[1].pitch == _p("e")  # type: ignore[union-attr]
        assert result[2].pitch == _p("g")  # type: ignore[union-attr]
        # Second half is full retrograde
        assert result[3].pitch == _p("g")  # type: ignore[union-attr]
        assert result[4].pitch == _p("e")  # type: ignore[union-attr]
        assert result[5].pitch == _p("c")  # type: ignore[union-attr]

    def test_mirror_empty(self) -> None:
        assert mirror(()) == ()


# ---------------------------------------------------------------------------
# MELO-09: fragment
# ---------------------------------------------------------------------------

class TestFragment:
    def test_fragment_basic(self) -> None:
        """[A,B,C,D,E] fragment [2,3] -> ([A,B], [C,D,E])."""
        phrase = (_n("a"), _n("b"), _n("c"), _n("d"), _n("e"))
        result = fragment(phrase, [2, 3])
        assert len(result) == 2
        assert len(result[0]) == 2
        assert len(result[1]) == 3
        assert result[0][0].pitch == _p("a")  # type: ignore[union-attr]
        assert result[1][0].pitch == _p("c")  # type: ignore[union-attr]

    def test_fragment_partial(self) -> None:
        """If sum(lengths) < len(phrase), remaining events dropped."""
        phrase = (_n("a"), _n("b"), _n("c"), _n("d"))
        result = fragment(phrase, [2])
        assert len(result) == 1
        assert len(result[0]) == 2


# ---------------------------------------------------------------------------
# MELO-10: concatenate
# ---------------------------------------------------------------------------

class TestConcatenate:
    def test_concatenate_two(self) -> None:
        """join([A,B], [C,D]) -> [A,B,C,D]."""
        p1 = (_n("a"), _n("b"))
        p2 = (_n("c"), _n("d"))
        result = concatenate(p1, p2)
        assert len(result) == 4
        assert result[2].pitch == _p("c")  # type: ignore[union-attr]

    def test_concatenate_multiple(self) -> None:
        """join([A], [B], [C]) -> [A,B,C]."""
        result = concatenate((_n("a"),), (_n("b"),), (_n("c"),))
        assert len(result) == 3

    def test_concatenate_empty(self) -> None:
        result = concatenate((), ())
        assert result == ()


# ---------------------------------------------------------------------------
# MELO-11: interleave
# ---------------------------------------------------------------------------

class TestInterleave:
    def test_interleave_equal_length(self) -> None:
        """[A,B,C] and [X,Y,Z] -> [A,X,B,Y,C,Z]."""
        p1 = (_n("a"), _n("b"), _n("c"))
        p2 = (_n("d"), _n("e"), _n("f"))
        result = interleave(p1, p2)
        assert len(result) == 6
        assert result[0].pitch == _p("a")  # type: ignore[union-attr]
        assert result[1].pitch == _p("d")  # type: ignore[union-attr]
        assert result[2].pitch == _p("b")  # type: ignore[union-attr]
        assert result[3].pitch == _p("e")  # type: ignore[union-attr]

    def test_interleave_unequal(self) -> None:
        """Shorter exhausted, rest of longer appended."""
        p1 = (_n("a"), _n("b"), _n("c"))
        p2 = (_n("d"),)
        result = interleave(p1, p2)
        assert len(result) == 4  # A, D, B, C
        assert result[0].pitch == _p("a")  # type: ignore[union-attr]
        assert result[1].pitch == _p("d")  # type: ignore[union-attr]
        assert result[2].pitch == _p("b")  # type: ignore[union-attr]
        assert result[3].pitch == _p("c")  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# MELO-12: pitch_map
# ---------------------------------------------------------------------------

class TestPitchMap:
    def test_pitch_map_basic(self) -> None:
        """Apply a function to every note's pitch."""
        phrase = (_n("c"), _n("d"), _n("e"))
        # Shift all pitches up one octave
        result = pitch_map(phrase, lambda p: Pitch(step=p.step, accidental=p.accidental, octave=p.octave + 1))
        assert result[0].pitch.octave == 5  # type: ignore[union-attr]
        assert result[1].pitch.octave == 5  # type: ignore[union-attr]

    def test_pitch_map_rests_pass_through(self) -> None:
        """Rests are not affected by pitch mapping."""
        phrase = (_n("c"), _r(), _n("e"))
        result = pitch_map(phrase, lambda p: Pitch(step=p.step, accidental=p.accidental, octave=p.octave + 1))
        assert isinstance(result[1], Rest)

    def test_pitch_map_empty(self) -> None:
        assert pitch_map((), lambda p: p) == ()


# ---------------------------------------------------------------------------
# Chaining test
# ---------------------------------------------------------------------------

class TestChaining:
    def test_chain_retrograde_invert_transpose(self, c_major_scale_phrase: Phrase) -> None:
        """chromatic_transpose(invert(pitch_retrograde(phrase))) produces valid Phrase."""
        step1 = pitch_retrograde(c_major_scale_phrase)
        step2 = invert(step1)
        interval = Interval("m", 3, 1)
        step3 = chromatic_transpose(step2, interval)

        assert isinstance(step3, tuple)
        assert len(step3) == len(c_major_scale_phrase)
        for event in step3:
            assert isinstance(event, Note)


# ---------------------------------------------------------------------------
# Empty phrase for all transforms
# ---------------------------------------------------------------------------

class TestAllEmptyPhrase:
    def test_all_transforms_empty(self) -> None:
        """All transforms on empty phrase return empty tuple."""
        empty: Phrase = ()
        assert pitch_retrograde(empty) == ()
        assert retrograde_inversion(empty) == ()
        assert full_retrograde(empty) == ()
        assert rotate(empty, 1) == ()
        assert interpolate(empty, steps=1) == ()
        assert repeat(empty, 3) == ()
        assert mirror(empty) == ()
        assert concatenate(empty, empty) == ()
        assert interleave(empty, empty) == ()
        assert pitch_map(empty, lambda p: p) == ()
