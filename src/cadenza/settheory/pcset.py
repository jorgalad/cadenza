"""Pitch class set operations using Forte (1973) set theory.

All functions operate on frozenset[int] where each int is a pitch class 0-11.
Prime form computation uses Forte's left-packing algorithm, NOT Rahn's.
"""

from __future__ import annotations

from itertools import combinations

from cadenza.settheory._forte_table import FORTE_TABLE, PRIME_TO_FORTE


def _validate_pcs(pcs: frozenset[int]) -> None:
    """Raise ValueError if any pitch class is outside 0-11."""
    for pc in pcs:
        if not (0 <= pc <= 11):
            raise ValueError(
                f"Pitch classes must be 0-11, got {pc} in {pcs}"
            )


def _transposed_rotations(pcs: frozenset[int]) -> list[tuple[int, ...]]:
    """Generate all rotations of a PC set, each transposed to start at 0.

    Returns a list of tuples, one per rotation, each starting with 0.
    """
    pcs_sorted = sorted(pcs)
    n = len(pcs_sorted)
    if n <= 1:
        return [(0,)] if n == 1 else [()]

    results = []
    for i in range(n):
        rotation = tuple(pcs_sorted[(i + j) % n] for j in range(n))
        t0 = tuple((pc - rotation[0]) % 12 for pc in rotation)
        results.append(t0)
    return results


def _forte_key(t0: tuple[int, ...]) -> tuple[int, ...]:
    """Comparison key for Forte's prime form selection.

    Forte compares from the right: minimize last element (span), then
    second-to-last, etc. This is equivalent to comparing reversed tuples.
    """
    return t0[::-1]


def prime_form(pcs: frozenset[int]) -> tuple[int, ...]:
    """Compute the Forte (1973) prime form of a pitch class set.

    Returns an ascending tuple of integers starting from 0.

    Forte's algorithm: among all rotations of both the original set and
    its inversion (each transposed to start at 0), pick the candidate
    with the smallest span (last element), breaking ties by comparing
    from the right (second-to-last, third-to-last, etc.).
    """
    if not pcs:
        return ()
    _validate_pcs(pcs)

    # All transposed rotations of original
    candidates = _transposed_rotations(pcs)

    # All transposed rotations of inversion
    inv = frozenset((12 - pc) % 12 for pc in pcs)
    candidates.extend(_transposed_rotations(inv))

    # Forte: pick the candidate with the smallest reversed-tuple key
    return min(candidates, key=_forte_key)


def interval_vector(
    pcs: frozenset[int],
) -> tuple[int, int, int, int, int, int]:
    """Compute the interval class vector (ic1 through ic6).

    Returns a 6-element tuple counting occurrences of each interval class.
    """
    vec = [0, 0, 0, 0, 0, 0]
    pcs_list = sorted(pcs)
    for i in range(len(pcs_list)):
        for j in range(i + 1, len(pcs_list)):
            diff = (pcs_list[j] - pcs_list[i]) % 12
            ic = min(diff, 12 - diff)
            if 1 <= ic <= 6:
                vec[ic - 1] += 1
    return (vec[0], vec[1], vec[2], vec[3], vec[4], vec[5])


def forte_number(pcs: frozenset[int]) -> str:
    """Look up the Forte number for a pitch class set.

    Computes the prime form, then looks it up in the reverse index.
    Raises ValueError if the set has no Forte classification (e.g., empty set).
    """
    pf = prime_form(pcs)
    if pf not in PRIME_TO_FORTE:
        raise ValueError(f"No Forte number for prime form {pf}")
    return PRIME_TO_FORTE[pf]


def lookup_by_forte(forte: str) -> tuple[int, ...]:
    """Look up the prime form for a Forte number.

    Raises ValueError if the Forte number is not in the table.
    """
    if forte not in FORTE_TABLE:
        raise ValueError(f"Unknown Forte number: {forte!r}")
    return FORTE_TABLE[forte]


def complement(pcs: frozenset[int]) -> frozenset[int]:
    """Compute the complement: all pitch classes not in the set."""
    return frozenset(range(12)) - pcs


def invert_pcs(pcs: frozenset[int]) -> frozenset[int]:
    """Invert a pitch class set (T0I): each pc -> (12 - pc) mod 12."""
    return frozenset((12 - pc) % 12 for pc in pcs)


def transpose_pcs(pcs: frozenset[int], n: int) -> frozenset[int]:
    """Transpose a pitch class set by n semitones."""
    return frozenset((pc + n) % 12 for pc in pcs)


def is_subset(a: frozenset[int], b: frozenset[int]) -> bool:
    """True if a is a subset of b (includes equality)."""
    return a <= b


def is_superset(a: frozenset[int], b: frozenset[int]) -> bool:
    """True if a is a superset of b (includes equality)."""
    return a >= b


def is_z_related(a: frozenset[int], b: frozenset[int]) -> bool:
    """True if a and b have the same interval vector but different prime forms."""
    return (
        interval_vector(a) == interval_vector(b)
        and prime_form(a) != prime_form(b)
    )


def rp_relation(a: frozenset[int], b: frozenset[int]) -> bool:
    """Rp: same cardinality, share at least one (n-1)-subset prime form."""
    if len(a) != len(b):
        return False
    if len(a) <= 1:
        return len(a) == len(b)
    a_subs = {prime_form(frozenset(s)) for s in combinations(a, len(a) - 1)}
    b_subs = {prime_form(frozenset(s)) for s in combinations(b, len(b) - 1)}
    return bool(a_subs & b_subs)


def r0(a: frozenset[int], b: frozenset[int]) -> bool:
    """R0: same interval vector."""
    return interval_vector(a) == interval_vector(b)


def r1(a: frozenset[int], b: frozenset[int]) -> bool:
    """R1: interval vectors differ in exactly one position by exactly 1."""
    va, vb = interval_vector(a), interval_vector(b)
    diffs = [abs(x - y) for x, y in zip(va, vb)]
    return diffs.count(1) == 1 and diffs.count(0) == 5


def r2(a: frozenset[int], b: frozenset[int]) -> bool:
    """R2: IVs differ in exactly two positions, each by 1, sum of diffs = 0."""
    va, vb = interval_vector(a), interval_vector(b)
    diffs = [x - y for x, y in zip(va, vb)]
    abs_diffs = [abs(d) for d in diffs]
    return (
        abs_diffs.count(1) == 2
        and abs_diffs.count(0) == 4
        and sum(diffs) == 0
    )
