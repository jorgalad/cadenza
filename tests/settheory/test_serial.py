"""Tests for 12-tone serial operations (SERI-01 through SERI-06)."""

from __future__ import annotations

import pytest

from cadenza.core.pitch import Pitch
from cadenza.settheory.serial import (
    ToneRow,
    derive_row,
    is_all_interval,
    is_combinatorial,
    realize_row,
    segment_row,
)
from cadenza.transforms.pitch import from_midi


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def chromatic_row() -> ToneRow:
    """Chromatic scale as a tone row."""
    return ToneRow(pcs=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11))


@pytest.fixture
def webern_op21() -> ToneRow:
    """Webern Op. 21 row."""
    return ToneRow(pcs=(9, 10, 3, 11, 4, 8, 2, 7, 0, 5, 6, 1))


@pytest.fixture
def schoenberg_op25() -> ToneRow:
    """Schoenberg Op. 25 row."""
    return ToneRow(pcs=(4, 5, 7, 1, 6, 3, 8, 2, 11, 0, 9, 10))


@pytest.fixture
def all_interval_row_pcs() -> tuple[int, ...]:
    """Known all-interval row."""
    return (0, 1, 4, 2, 9, 5, 11, 3, 8, 10, 7, 6)


# ---------------------------------------------------------------------------
# SERI-01: ToneRow construction
# ---------------------------------------------------------------------------

class TestToneRowCreation:
    def test_chromatic_row_creation(self, chromatic_row: ToneRow) -> None:
        assert chromatic_row.pcs == (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)

    def test_webern_row_creation(self, webern_op21: ToneRow) -> None:
        assert webern_op21.pcs == (9, 10, 3, 11, 4, 8, 2, 7, 0, 5, 6, 1)

    def test_rejects_wrong_length(self) -> None:
        with pytest.raises(ValueError, match="12 pitch classes"):
            ToneRow(pcs=(0, 1, 2, 3))

    def test_rejects_duplicates(self) -> None:
        with pytest.raises(ValueError, match="12 pitch classes"):
            ToneRow(pcs=(0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10))


# ---------------------------------------------------------------------------
# SERI-02: Prime, Inversion, Retrograde, RI, Matrix
# ---------------------------------------------------------------------------

class TestPrimeMethod:
    def test_prime_0_starts_on_0(self, webern_op21: ToneRow) -> None:
        p0 = webern_op21.prime(0)
        assert p0[0] == 0

    def test_prime_5_starts_on_5(self, webern_op21: ToneRow) -> None:
        p5 = webern_op21.prime(5)
        assert p5[0] == 5

    def test_prime_preserves_intervals(self, webern_op21: ToneRow) -> None:
        p0 = webern_op21.prime(0)
        p5 = webern_op21.prime(5)
        intervals_p0 = [(p0[i + 1] - p0[i]) % 12 for i in range(11)]
        intervals_p5 = [(p5[i + 1] - p5[i]) % 12 for i in range(11)]
        assert intervals_p0 == intervals_p5

    def test_prime_chromatic(self, chromatic_row: ToneRow) -> None:
        assert chromatic_row.prime(0) == (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)


class TestInversionMethod:
    def test_inversion_0_starts_on_0(self, webern_op21: ToneRow) -> None:
        i0 = webern_op21.inversion(0)
        assert i0[0] == 0

    def test_inversion_flips_intervals(self, webern_op21: ToneRow) -> None:
        p0 = webern_op21.prime(0)
        i0 = webern_op21.inversion(0)
        for k in range(11):
            p_interval = (p0[k + 1] - p0[k]) % 12
            i_interval = (i0[k + 1] - i0[k]) % 12
            assert (p_interval + i_interval) % 12 == 0


class TestRetrogradeMethod:
    def test_retrograde_is_reverse_of_prime(self, webern_op21: ToneRow) -> None:
        p0 = webern_op21.prime(0)
        r0 = webern_op21.retrograde(0)
        assert r0 == p0[::-1]

    def test_retrograde_5(self, webern_op21: ToneRow) -> None:
        p5 = webern_op21.prime(5)
        r5 = webern_op21.retrograde(5)
        assert r5 == p5[::-1]


class TestRetrogradeInversionMethod:
    def test_ri_is_reverse_of_inversion(self, webern_op21: ToneRow) -> None:
        i0 = webern_op21.inversion(0)
        ri0 = webern_op21.retrograde_inversion(0)
        assert ri0 == i0[::-1]

    def test_ri_5(self, webern_op21: ToneRow) -> None:
        i5 = webern_op21.inversion(5)
        ri5 = webern_op21.retrograde_inversion(5)
        assert ri5 == i5[::-1]


class TestMatrix:
    def test_matrix_is_12x12(self, webern_op21: ToneRow) -> None:
        m = webern_op21.matrix()
        assert len(m) == 12
        assert all(len(row) == 12 for row in m)

    def test_top_left_is_0(self, webern_op21: ToneRow) -> None:
        m = webern_op21.matrix()
        assert m[0][0] == 0

    def test_first_row_is_p0(self, webern_op21: ToneRow) -> None:
        m = webern_op21.matrix()
        assert tuple(m[0]) == webern_op21.prime(0)

    def test_first_column_is_i0(self, webern_op21: ToneRow) -> None:
        m = webern_op21.matrix()
        first_col = tuple(m[i][0] for i in range(12))
        assert first_col == webern_op21.inversion(0)

    def test_diagonal_all_zeros(self, webern_op21: ToneRow) -> None:
        m = webern_op21.matrix()
        diagonal = [m[i][i] for i in range(12)]
        assert all(d == 0 for d in diagonal)

    def test_chromatic_matrix_diagonal(self, chromatic_row: ToneRow) -> None:
        m = chromatic_row.matrix()
        diagonal = [m[i][i] for i in range(12)]
        assert all(d == 0 for d in diagonal)


# ---------------------------------------------------------------------------
# SERI-03: Row properties
# ---------------------------------------------------------------------------

class TestIsAllInterval:
    def test_all_interval_row_true(self, all_interval_row_pcs: tuple[int, ...]) -> None:
        assert is_all_interval(all_interval_row_pcs) is True

    def test_chromatic_not_all_interval(self) -> None:
        chromatic = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
        assert is_all_interval(chromatic) is False

    def test_accepts_tone_row(self, all_interval_row_pcs: tuple[int, ...]) -> None:
        row = ToneRow(pcs=all_interval_row_pcs)
        assert is_all_interval(row) is True


class TestIsCombinatorial:
    def test_returns_dict_with_correct_keys(self, webern_op21: ToneRow) -> None:
        result = is_combinatorial(webern_op21)
        assert set(result.keys()) == {"P", "I", "R", "RI"}
        assert all(isinstance(v, list) for v in result.values())

    def test_webern_op21_combinatorial(self, webern_op21: ToneRow) -> None:
        result = is_combinatorial(webern_op21)
        # Webern Op. 21 hexachords {0,1,2,6,7,11}/{3,4,5,8,9,10} in P(0)
        # Each value is a list of transposition levels
        assert all(isinstance(v, list) for v in result.values())
        assert all(all(isinstance(n, int) for n in v) for v in result.values())

    def test_chromatic_combinatorial(self, chromatic_row: ToneRow) -> None:
        result = is_combinatorial(chromatic_row)
        # Chromatic row: first hexachord {0-5}, complement {6-11}
        # P-combinatorial at T6 (shifts {0-5} to {6-11})
        assert 6 in result["P"]


# ---------------------------------------------------------------------------
# SERI-04: Row realization
# ---------------------------------------------------------------------------

class TestRealizeRow:
    def test_returns_12_pitches(self, chromatic_row: ToneRow) -> None:
        pitches = realize_row(chromatic_row.prime(0), base_octave=4)
        assert len(pitches) == 12
        assert all(isinstance(p, Pitch) for p in pitches)

    def test_pitch_classes_match(self, webern_op21: ToneRow) -> None:
        p0 = webern_op21.prime(0)
        pitches = realize_row(p0, base_octave=4)
        for pc, pitch in zip(p0, pitches):
            assert pitch.pitch_class == pc

    def test_fixed_octave_midi_range(self, chromatic_row: ToneRow) -> None:
        pitches = realize_row(chromatic_row.prime(0), base_octave=4, nearest=False)
        for p in pitches:
            assert 60 <= p.midi_number <= 71

    def test_nearest_minimizes_distance(self, webern_op21: ToneRow) -> None:
        p0 = webern_op21.prime(0)
        pitches = realize_row(p0, base_octave=4, nearest=True)
        # Check consecutive intervals are small (no more than 6 semitones ideally)
        for i in range(1, len(pitches)):
            dist = abs(pitches[i].midi_number - pitches[i - 1].midi_number)
            assert dist <= 6  # nearest should keep intervals tight


# ---------------------------------------------------------------------------
# SERI-05: Row segmentation
# ---------------------------------------------------------------------------

class TestSegmentRow:
    def test_trichords(self, chromatic_row: ToneRow) -> None:
        p0 = chromatic_row.prime(0)
        segments = segment_row(p0, (3, 3, 3, 3))
        assert len(segments) == 4
        assert all(len(s) == 3 for s in segments)
        assert segments[0] == (0, 1, 2)
        assert segments[3] == (9, 10, 11)

    def test_hexachords(self, chromatic_row: ToneRow) -> None:
        p0 = chromatic_row.prime(0)
        segments = segment_row(p0, (6, 6))
        assert len(segments) == 2
        assert segments[0] == (0, 1, 2, 3, 4, 5)
        assert segments[1] == (6, 7, 8, 9, 10, 11)

    def test_wrong_sizes_raises(self, chromatic_row: ToneRow) -> None:
        p0 = chromatic_row.prime(0)
        with pytest.raises(ValueError, match="sum"):
            segment_row(p0, (5, 5))


# ---------------------------------------------------------------------------
# SERI-06: Row derivation
# ---------------------------------------------------------------------------

class TestDeriveRow:
    def test_derive_from_diminished_tetrachord(self) -> None:
        seed = frozenset({0, 3, 6, 9})
        row = derive_row(seed)
        assert set(row.pcs) == set(range(12))
        assert len(row.pcs) == 12

    def test_derive_from_augmented_trichord(self) -> None:
        seed = frozenset({0, 4, 8})
        row = derive_row(seed)
        assert set(row.pcs) == set(range(12))
        assert len(row.pcs) == 12

    def test_derive_rejects_invalid_seed_size(self) -> None:
        with pytest.raises(ValueError):
            derive_row(frozenset({0, 1, 2, 3, 4}))  # 5 doesn't divide 12
