"""12-tone serial operations (SERI-01 through SERI-06).

ToneRow dataclass with matrix generation, row forms (P, I, R, RI),
property detection, realization as pitched notes, segmentation,
and row derivation from seed sets.
"""

from __future__ import annotations

from dataclasses import dataclass

from cadenza.settheory.pcset import prime_form
from cadenza.transforms.pitch import from_midi


# ---------------------------------------------------------------------------
# SERI-01: ToneRow dataclass
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class ToneRow:
    """A 12-tone row: an ordered sequence of all 12 pitch classes.

    Immutable. Methods return derived row forms as tuples.
    """

    pcs: tuple[int, ...]

    def __post_init__(self) -> None:
        if len(self.pcs) != 12 or set(self.pcs) != set(range(12)):
            raise ValueError(
                "ToneRow must contain all 12 pitch classes exactly once"
            )

    # -------------------------------------------------------------------
    # SERI-02: Row forms
    # -------------------------------------------------------------------

    def prime(self, n: int) -> tuple[int, ...]:
        """P(n): transpose row so first note maps to pitch class n.

        P(0) always starts on 0.
        """
        offset = (n - self.pcs[0]) % 12
        return tuple((pc + offset) % 12 for pc in self.pcs)

    def inversion(self, n: int) -> tuple[int, ...]:
        """I(n): invert row around its first note, then transpose to n.

        I(0) starts on 0 with all intervals negated.
        """
        return tuple((n - (pc - self.pcs[0])) % 12 for pc in self.pcs)

    def retrograde(self, n: int) -> tuple[int, ...]:
        """R(n): reverse of P(n)."""
        return self.prime(n)[::-1]

    def retrograde_inversion(self, n: int) -> tuple[int, ...]:
        """RI(n): reverse of I(n)."""
        return self.inversion(n)[::-1]

    def matrix(self) -> list[list[int]]:
        """Generate the 12x12 tone row matrix.

        Rows are P-forms, columns are I-forms. Top-left is always 0.
        The diagonal from top-left to bottom-right contains all 0s.
        """
        p0 = self.prime(0)
        i0 = self.inversion(0)
        return [[(pc + row_start) % 12 for pc in p0] for row_start in i0]


# ---------------------------------------------------------------------------
# SERI-03: Row property detection
# ---------------------------------------------------------------------------

def is_all_interval(row: ToneRow | tuple[int, ...]) -> bool:
    """Check if a row has all 11 distinct adjacent intervals.

    An all-interval row contains each interval class 1-11 exactly once
    among its 11 consecutive pairs.
    """
    pcs = row.pcs if isinstance(row, ToneRow) else row
    intervals = [(pcs[i + 1] - pcs[i]) % 12 for i in range(len(pcs) - 1)]
    return len(set(intervals)) == 11


def is_combinatorial(row: ToneRow | tuple[int, ...]) -> dict[str, list[int]]:
    """Check hexachordal combinatoriality for all four form types.

    Returns a dict mapping 'P', 'I', 'R', 'RI' to lists of transposition
    levels (0-11) at which the form's first hexachord is disjoint from
    the first hexachord of P(0).
    """
    pcs = row.pcs if isinstance(row, ToneRow) else row
    # Normalize to P(0)
    offset = (0 - pcs[0]) % 12
    p0 = tuple((pc + offset) % 12 for pc in pcs)

    h1 = frozenset(p0[:6])
    result: dict[str, list[int]] = {"P": [], "I": [], "R": [], "RI": []}

    for n in range(12):
        # P(n)
        p_n = tuple((pc + n) % 12 for pc in p0)
        if frozenset(p_n[:6]).isdisjoint(h1):
            result["P"].append(n)

        # I(n)
        i_n = tuple((n - pc) % 12 for pc in p0)
        if frozenset(i_n[:6]).isdisjoint(h1):
            result["I"].append(n)

        # R(n)
        r_n = p_n[::-1]
        if frozenset(r_n[6:]).isdisjoint(h1):
            result["R"].append(n)

        # RI(n)
        ri_n = i_n[::-1]
        if frozenset(ri_n[6:]).isdisjoint(h1):
            result["RI"].append(n)

    return result


# ---------------------------------------------------------------------------
# SERI-04: Row realization
# ---------------------------------------------------------------------------

def realize_row(
    row_form: tuple[int, ...],
    base_octave: int = 4,
    nearest: bool = False,
) -> tuple:
    """Convert a row form (pitch classes) to concrete Pitch objects.

    Args:
        row_form: Ordered pitch classes (0-11).
        base_octave: Starting octave (default 4, middle C region).
        nearest: If True, choose octave to minimize interval from previous note.

    Returns:
        Tuple of Pitch objects.
    """
    if not nearest:
        # All notes in one octave: MIDI = pc + (base_octave + 1) * 12
        base_midi = (base_octave + 1) * 12
        return tuple(from_midi(pc + base_midi) for pc in row_form)

    # Nearest-note voice leading
    base_midi = (base_octave + 1) * 12
    pitches = [from_midi(row_form[0] + base_midi)]
    for i in range(1, len(row_form)):
        prev_midi = pitches[-1].midi_number
        pc = row_form[i]
        # Find the octave placement closest to previous note
        # Candidate MIDI numbers: pc + oct * 12 for various octaves
        candidates = [pc + oct * 12 for oct in range(12)]
        # Filter to valid MIDI range and pick closest
        valid = [m for m in candidates if 0 <= m <= 127]
        best = min(valid, key=lambda m: abs(m - prev_midi))
        pitches.append(from_midi(best))
    return tuple(pitches)


# ---------------------------------------------------------------------------
# SERI-05: Row segmentation
# ---------------------------------------------------------------------------

def segment_row(
    row_form: tuple[int, ...],
    sizes: tuple[int, ...],
) -> tuple[tuple[int, ...], ...]:
    """Split a row form into segments of specified sizes.

    Args:
        row_form: Ordered pitch classes.
        sizes: Tuple of segment sizes that must sum to len(row_form).

    Returns:
        Tuple of tuples, each containing the pitch classes for that segment.

    Raises:
        ValueError: If sizes don't sum to the row length.
    """
    if sum(sizes) != len(row_form):
        raise ValueError(
            f"Segment sizes {sizes} sum to {sum(sizes)}, "
            f"but row has {len(row_form)} elements"
        )
    segments: list[tuple[int, ...]] = []
    offset = 0
    for size in sizes:
        segments.append(row_form[offset : offset + size])
        offset += size
    return tuple(segments)


# ---------------------------------------------------------------------------
# SERI-06: Row derivation
# ---------------------------------------------------------------------------

def derive_row(seed: frozenset[int]) -> ToneRow:
    """Derive a 12-tone row from a smaller seed set.

    Partitions the 12 pitch classes into groups, each a transposition
    or inversion of the seed. Concatenates all segments.

    Args:
        seed: A frozenset of pitch classes forming the seed.

    Returns:
        A ToneRow containing all 12 pitch classes.

    Raises:
        ValueError: If 12 is not evenly divisible by seed size,
            or if a complete partition cannot be found.
    """
    n = len(seed)
    if n == 0 or 12 % n != 0:
        raise ValueError(
            f"Seed of size {n} cannot evenly partition 12 pitch classes"
        )

    used: set[int] = set()
    segments: list[tuple[int, ...]] = []

    # Try transpositions first
    for t in range(12):
        candidate = frozenset((pc + t) % 12 for pc in seed)
        if not candidate & used:
            segments.append(tuple(sorted(candidate)))
            used |= candidate
        if len(used) == 12:
            break

    # Try inversions for remaining PCs
    if len(used) < 12:
        for t in range(12):
            candidate = frozenset((t - pc) % 12 for pc in seed)
            if not candidate & used:
                segments.append(tuple(sorted(candidate)))
                used |= candidate
            if len(used) == 12:
                break

    if len(used) != 12:
        raise ValueError(f"Cannot derive a complete row from seed {seed}")

    row_pcs: list[int] = []
    for seg in segments:
        row_pcs.extend(seg)
    return ToneRow(pcs=tuple(row_pcs))
