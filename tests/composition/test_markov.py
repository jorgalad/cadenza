"""Tests for Markov chain melody generation (ALGO-01, ALGO-02)."""

from __future__ import annotations

import pytest

from cadenza.core.note import Note
from cadenza.core.phrase import Phrase
from cadenza.composition.markov import MarkovModel, train_markov, markov_melody


class TestTrainMarkov:
    """Tests for train_markov."""

    def test_train_markov_order1(self, sample_phrase: Phrase) -> None:
        model = train_markov(sample_phrase, order=1)
        assert model.order == 1
        assert isinstance(model.transition_table, dict)
        assert len(model.transition_table) > 0

    def test_train_markov_order2(self, sample_phrase: Phrase) -> None:
        model = train_markov(sample_phrase, order=2)
        assert model.order == 2
        # All keys should be 2-tuples
        for key in model.transition_table:
            assert len(key) == 2

    def test_train_markov_too_short(self) -> None:
        from cadenza.core.duration import Duration
        from cadenza.transforms.pitch import from_midi

        q = Duration.from_cn("q")
        short = (
            Note(pitch=from_midi(60), duration=q),
            Note(pitch=from_midi(62), duration=q),
        )
        with pytest.raises(ValueError):
            train_markov(short, order=2)

    def test_train_markov_invalid_order(self, sample_phrase: Phrase) -> None:
        with pytest.raises(ValueError):
            train_markov(sample_phrase, order=0)


class TestMarkovMelody:
    """Tests for markov_melody."""

    def test_markov_melody_seeded_reproducible(self, sample_phrase: Phrase) -> None:
        model = train_markov(sample_phrase, order=1)
        a = markov_melody(model, 10, seed=42)
        b = markov_melody(model, 10, seed=42)
        assert a == b

    def test_markov_melody_transitions_valid(self, sample_phrase: Phrase) -> None:
        model = train_markov(sample_phrase, order=1)
        result = markov_melody(model, 10, seed=42)
        # Extract MIDI numbers from training phrase
        train_midis = [e.pitch.midi_number for e in sample_phrase if isinstance(e, Note)]
        # Build set of valid transitions (consecutive pairs)
        valid_pairs = set()
        for i in range(len(train_midis) - 1):
            valid_pairs.add((train_midis[i], train_midis[i + 1]))
        # Check every consecutive pair in result
        result_midis = [e.pitch.midi_number for e in result if isinstance(e, Note)]
        for i in range(len(result_midis) - 1):
            assert (result_midis[i], result_midis[i + 1]) in valid_pairs

    def test_markov_melody_length(self, sample_phrase: Phrase) -> None:
        model = train_markov(sample_phrase, order=1)
        result = markov_melody(model, 10, seed=42)
        assert len(result) == 10

    def test_markov_melody_invalid_length(self, sample_phrase: Phrase) -> None:
        model = train_markov(sample_phrase, order=1)
        with pytest.raises(ValueError):
            markov_melody(model, 0, seed=42)

    def test_higher_order_differs(self, sample_phrase: Phrase) -> None:
        m1 = train_markov(sample_phrase, order=1)
        m2 = train_markov(sample_phrase, order=2)
        r1 = markov_melody(m1, 10, seed=42)
        r2 = markov_melody(m2, 10, seed=42)
        assert r1 != r2
