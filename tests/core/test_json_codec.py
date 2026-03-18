"""Tests for JSON codec round-trip serialization."""

from __future__ import annotations

from fractions import Fraction

from hypothesis import given

from cadenza.core.pitch import Pitch
from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest
from cadenza.core.phrase import Phrase
from cadenza.core.score import Score
from cadenza.core.json_codec import to_json, from_json
from tests.strategies import pitch_strategy, duration_strategy


class TestPitchRoundTrip:
    def test_pitch_round_trip(self) -> None:
        p = Pitch("e", "b", 3)
        assert from_json(to_json(p)) == p

    def test_pitch_with_double_sharp(self) -> None:
        p = Pitch("c", "ss", 4)
        assert from_json(to_json(p)) == p


class TestDurationRoundTrip:
    def test_duration_round_trip(self) -> None:
        d = Duration.from_omn("q", dots=1)
        assert from_json(to_json(d)) == d

    def test_duration_with_tuplet(self) -> None:
        d = Duration.from_omn("e", tuplet=3)
        assert from_json(to_json(d)) == d


class TestNoteRoundTrip:
    def test_note_round_trip(self) -> None:
        n = Note(Pitch("c", "n", 4), Duration.from_omn("q"), "mf", ("stacc",))
        assert from_json(to_json(n)) == n

    def test_note_no_dynamic(self) -> None:
        n = Note(Pitch("c", "n", 4), Duration.from_omn("q"), None, ())
        assert from_json(to_json(n)) == n


class TestRestRoundTrip:
    def test_rest_round_trip(self) -> None:
        r = Rest(Duration.from_omn("h"))
        assert from_json(to_json(r)) == r


class TestPhraseRoundTrip:
    def test_phrase_round_trip(self) -> None:
        phrase: Phrase = (
            Note(Pitch("c", "n", 4), Duration.from_omn("q"), "mf", ()),
            Rest(Duration.from_omn("e")),
            Note(Pitch("d", "n", 4), Duration.from_omn("q"), "pp", ("trill",)),
        )
        result = from_json(to_json(phrase))
        assert isinstance(result, tuple)
        assert result == phrase


class TestScoreRoundTrip:
    def test_score_round_trip(self) -> None:
        soprano: Phrase = (
            Note(Pitch("c", "n", 4), Duration.from_omn("q"), "mf", ()),
        )
        bass: Phrase = (
            Note(Pitch("c", "n", 3), Duration.from_omn("h"), "f", ()),
        )
        score = Score.from_dict({"soprano": soprano, "bass": bass})
        result = from_json(to_json(score))
        assert result == score


class TestFractionSerialization:
    def test_fraction_format(self) -> None:
        """Fraction serialized as _type/numerator/denominator dict."""
        import json
        from cadenza.core.json_codec import CadenzaEncoder

        data = json.loads(json.dumps(Fraction(3, 8), cls=CadenzaEncoder))
        assert data["_type"] == "Fraction"
        assert data["numerator"] == 3
        assert data["denominator"] == 8


class TestHypothesisRoundTrip:
    @given(p=pitch_strategy())
    def test_pitch_hypothesis_round_trip(self, p: Pitch) -> None:
        assert from_json(to_json(p)) == p

    @given(d=duration_strategy())
    def test_duration_hypothesis_round_trip(self, d: Duration) -> None:
        assert from_json(to_json(d)) == d
