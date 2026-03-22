"""Set theory endpoints -- thin route handlers calling cadenza.settheory."""

from __future__ import annotations

from fastapi import APIRouter

from cadenza.api.helpers import _phrase_response
from cadenza.api.schemas import (
    DeriveRowRequest,
    ForteRequest,
    PitchClassSetRequest,
    RealizeRowRequest,
    SegmentRowRequest,
    ToneRowRequest,
    TransposePCSRequest,
    TwoPCSRequest,
)
from cadenza.settheory import (
    ToneRow,
    complement,
    derive_row,
    forte_number,
    interval_vector,
    invert_pcs,
    is_all_interval,
    is_combinatorial,
    is_subset,
    is_superset,
    is_z_related,
    lookup_by_forte,
    prime_form,
    r0,
    r1,
    r2,
    realize_row,
    rp_relation,
    segment_row,
    transpose_pcs,
)

router = APIRouter(prefix="/v1/settheory", tags=["settheory"])


# ---------------------------------------------------------------------------
# Pitch class set endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/prime-form",
    response_model=None,
    summary="Compute prime form of a pitch-class set",
    description="Return the most compact normal-order representation (Forte prime form) of a pitch-class set.",
)
def prime_form_endpoint(req: PitchClassSetRequest) -> dict:
    result = prime_form(frozenset(req.pcs))
    return {"prime_form": list(result)}


@router.post(
    "/interval-vector",
    response_model=None,
    summary="Compute interval vector of a pitch-class set",
    description="Return the 6-element interval vector counting each interval class (1-6).",
)
def interval_vector_endpoint(req: PitchClassSetRequest) -> dict:
    result = interval_vector(frozenset(req.pcs))
    return {"interval_vector": list(result)}


@router.post(
    "/forte-number",
    response_model=None,
    summary="Look up Forte number of a pitch-class set",
    description="Return the Forte catalog number (e.g. '3-1') for a pitch-class set.",
)
def forte_number_endpoint(req: PitchClassSetRequest) -> dict:
    result = forte_number(frozenset(req.pcs))
    return {"forte_number": result}


@router.post(
    "/lookup-by-forte",
    response_model=None,
    summary="Look up prime form by Forte number",
    description="Return the prime form tuple for a given Forte catalog number.",
)
def lookup_by_forte_endpoint(req: ForteRequest) -> dict:
    result = lookup_by_forte(req.forte)
    return {"prime_form": list(result)}


@router.post(
    "/complement",
    response_model=None,
    summary="Compute complement of a pitch-class set",
    description="Return all pitch classes not in the given set.",
)
def complement_endpoint(req: PitchClassSetRequest) -> dict:
    result = complement(frozenset(req.pcs))
    return {"complement": sorted(result)}


@router.post(
    "/invert-pcs",
    response_model=None,
    summary="Invert a pitch-class set",
    description="Apply T0I inversion (negate mod 12) to each pitch class.",
)
def invert_pcs_endpoint(req: PitchClassSetRequest) -> dict:
    result = invert_pcs(frozenset(req.pcs))
    return {"inverted": sorted(result)}


@router.post(
    "/transpose-pcs",
    response_model=None,
    summary="Transpose a pitch-class set",
    description="Add n semitones (mod 12) to each pitch class.",
)
def transpose_pcs_endpoint(req: TransposePCSRequest) -> dict:
    result = transpose_pcs(frozenset(req.pcs), req.n)
    return {"transposed": sorted(result)}


@router.post(
    "/is-subset",
    response_model=None,
    summary="Check if one set is a subset of another",
    description="Return true if pcs_a is a subset of pcs_b.",
)
def is_subset_endpoint(req: TwoPCSRequest) -> dict:
    return {"result": is_subset(frozenset(req.pcs_a), frozenset(req.pcs_b))}


@router.post(
    "/is-superset",
    response_model=None,
    summary="Check if one set is a superset of another",
    description="Return true if pcs_a is a superset of pcs_b.",
)
def is_superset_endpoint(req: TwoPCSRequest) -> dict:
    return {"result": is_superset(frozenset(req.pcs_a), frozenset(req.pcs_b))}


@router.post(
    "/is-z-related",
    response_model=None,
    summary="Check Z-relation between two sets",
    description="Return true if two sets have the same interval vector but different prime forms.",
)
def is_z_related_endpoint(req: TwoPCSRequest) -> dict:
    return {"result": is_z_related(frozenset(req.pcs_a), frozenset(req.pcs_b))}


@router.post(
    "/rp-relation",
    response_model=None,
    summary="Check Rp relation between two sets",
    description="Return true if one set can be derived from the other by a single pitch-class substitution.",
)
def rp_relation_endpoint(req: TwoPCSRequest) -> dict:
    return {"result": rp_relation(frozenset(req.pcs_a), frozenset(req.pcs_b))}


@router.post(
    "/r0",
    response_model=None,
    summary="Check R0 similarity relation",
    description="Return true if two sets of the same cardinality share the same interval vector.",
)
def r0_endpoint(req: TwoPCSRequest) -> dict:
    return {"result": r0(frozenset(req.pcs_a), frozenset(req.pcs_b))}


@router.post(
    "/r1",
    response_model=None,
    summary="Check R1 similarity relation",
    description="Return true if two sets differ by exactly one entry in their interval vectors.",
)
def r1_endpoint(req: TwoPCSRequest) -> dict:
    return {"result": r1(frozenset(req.pcs_a), frozenset(req.pcs_b))}


@router.post(
    "/r2",
    response_model=None,
    summary="Check R2 similarity relation",
    description="Return true if two sets differ by exactly two entries in their interval vectors.",
)
def r2_endpoint(req: TwoPCSRequest) -> dict:
    return {"result": r2(frozenset(req.pcs_a), frozenset(req.pcs_b))}


# ---------------------------------------------------------------------------
# Serial / 12-tone endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/tone-row",
    response_model=None,
    summary="Create tone row and compute matrix",
    description="Construct a ToneRow from 12 pitch classes and return the row with its full 12x12 matrix.",
)
def tone_row_endpoint(req: ToneRowRequest) -> dict:
    row = ToneRow(tuple(req.pcs))
    return {
        "row": list(row.pcs),
        "matrix": [[int(c) for c in r] for r in row.matrix()],
    }


@router.post(
    "/realize-row",
    response_model=None,
    summary="Realize tone row as pitched notes",
    description="Convert a pitch-class row into actual pitched notes at a specified octave.",
)
def realize_row_endpoint(req: RealizeRowRequest) -> dict:
    result = realize_row(tuple(req.row_form), req.base_octave, req.nearest)
    return _phrase_response(result)


@router.post(
    "/segment-row",
    response_model=None,
    summary="Segment tone row into subsets",
    description="Split a tone row into segments of specified sizes.",
)
def segment_row_endpoint(req: SegmentRowRequest) -> dict:
    result = segment_row(tuple(req.row_form), tuple(req.sizes))
    return {"segments": [list(s) for s in result]}


@router.post(
    "/derive-row",
    response_model=None,
    summary="Derive a tone row from a seed set",
    description="Generate a complete 12-tone row from a seed pitch-class set.",
)
def derive_row_endpoint(req: DeriveRowRequest) -> dict:
    result = derive_row(frozenset(req.seed))
    return {"row": list(result.pcs)}


@router.post(
    "/is-all-interval",
    response_model=None,
    summary="Check if row is all-interval",
    description="Return true if the tone row contains all 11 distinct interval classes.",
)
def is_all_interval_endpoint(req: ToneRowRequest) -> dict:
    return {"result": is_all_interval(ToneRow(tuple(req.pcs)))}


@router.post(
    "/is-combinatorial",
    response_model=None,
    summary="Check row combinatoriality",
    description="Return which transformation types (P, I, R, RI) yield combinatorial hexachords.",
)
def is_combinatorial_endpoint(req: ToneRowRequest) -> dict:
    return {"result": is_combinatorial(ToneRow(tuple(req.pcs)))}
