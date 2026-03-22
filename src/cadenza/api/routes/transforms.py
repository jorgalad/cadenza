"""Transform endpoints -- thin route handlers calling cadenza.transforms."""

from __future__ import annotations

from fractions import Fraction

from fastapi import APIRouter

from cadenza.api.errors import (
    INVALID_SCALE_NAME,
    NOT_IMPLEMENTED,
    CadenzaAPIError,
)
from cadenza.api.helpers import (
    _parse_phrase,
    _phrase_response,
    _safe_parse_interval,
    _safe_parse_pitch,
)
from cadenza.api.schemas import (
    ConcatenateRequest,
    DiatonicTransposeRequest,
    FragmentRequest,
    InterleaveRequest,
    InterpolateRequest,
    InvertRequest,
    MetricModulationRequest,
    OmitRequest,
    PermuteRequest,
    PhraseOnlyRequest,
    QuantizeRequest,
    RatioRequest,
    RepeatRequest,
    RotateRequest,
    TransposeRequest,
)
from cadenza.core.json_codec import _to_serializable
from cadenza.core.note import Note
from cadenza.theory import get_scale
from cadenza.transforms import (
    augment,
    chromatic_transpose,
    concatenate,
    diatonic_transpose,
    diminish,
    extract_rhythm,
    fragment,
    full_retrograde,
    interleave,
    interpolate,
    invert,
    metric_modulation,
    mirror,
    omit,
    permute,
    pitch_retrograde,
    quantize,
    repeat,
    retrograde_inversion,
    rhythmic_retrograde,
    rhythmic_rotation,
    rotate,
    total_duration,
)

router = APIRouter(prefix="/v1/transform", tags=["transforms"])


# ---------------------------------------------------------------------------
# Pitch transforms
# ---------------------------------------------------------------------------


@router.post("/chromatic-transpose", response_model=None, summary="Transpose phrase by chromatic interval")
def chromatic_transpose_endpoint(req: TransposeRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    interval = _safe_parse_interval(req.interval)
    result = chromatic_transpose(phrase, interval)
    return _phrase_response(result)


@router.post("/diatonic-transpose", response_model=None, summary="Transpose phrase by diatonic scale steps")
def diatonic_transpose_endpoint(req: DiatonicTransposeRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    scale = None
    if req.scale_name:
        # Use first pitch of phrase as scale root
        first_pitch = None
        for event in phrase:
            if isinstance(event, Note):
                first_pitch = event.pitch
                break
        if first_pitch is not None:
            try:
                scale = get_scale(first_pitch, req.scale_name)
            except ValueError as e:
                raise CadenzaAPIError(INVALID_SCALE_NAME, str(e), req.scale_name)
    result = diatonic_transpose(phrase, req.n, scale)
    return _phrase_response(result)


@router.post("/invert", response_model=None, summary="Invert phrase around optional pitch axis")
def invert_endpoint(req: InvertRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    axis = _safe_parse_pitch(req.axis) if req.axis else None
    result = invert(phrase, axis)
    return _phrase_response(result)


@router.post("/pitch-retrograde", response_model=None, summary="Reverse pitch order, keep rhythm")
def pitch_retrograde_endpoint(req: PhraseOnlyRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = pitch_retrograde(phrase)
    return _phrase_response(result)


@router.post("/full-retrograde", response_model=None, summary="Reverse entire phrase (pitches and rhythms)")
def full_retrograde_endpoint(req: PhraseOnlyRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = full_retrograde(phrase)
    return _phrase_response(result)


@router.post("/retrograde-inversion", response_model=None, summary="Retrograde then invert phrase")
def retrograde_inversion_endpoint(req: InvertRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    axis = _safe_parse_pitch(req.axis) if req.axis else None
    result = retrograde_inversion(phrase, axis)
    return _phrase_response(result)


# ---------------------------------------------------------------------------
# Rhythm transforms
# ---------------------------------------------------------------------------


@router.post("/augment", response_model=None, summary="Augment durations by ratio")
def augment_endpoint(req: RatioRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = augment(phrase, Fraction(req.ratio).limit_denominator(1000))
    return _phrase_response(result)


@router.post("/diminish", response_model=None, summary="Diminish durations by ratio")
def diminish_endpoint(req: RatioRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = diminish(phrase, Fraction(req.ratio).limit_denominator(1000))
    return _phrase_response(result)


@router.post("/rhythmic-retrograde", response_model=None, summary="Reverse rhythm, keep pitches")
def rhythmic_retrograde_endpoint(req: PhraseOnlyRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = rhythmic_retrograde(phrase)
    return _phrase_response(result)


@router.post("/rhythmic-rotation", response_model=None, summary="Rotate rhythm by n positions")
def rhythmic_rotation_endpoint(req: RotateRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = rhythmic_rotation(phrase, req.n)
    return _phrase_response(result)


@router.post("/extract-rhythm", response_model=None, summary="Extract durations from phrase")
def extract_rhythm_endpoint(req: PhraseOnlyRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = extract_rhythm(phrase)
    return {"events": _to_serializable(result)}


@router.post("/total-duration", response_model=None, summary="Compute total duration of phrase")
def total_duration_endpoint(req: PhraseOnlyRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = total_duration(phrase)
    return {
        "total": str(result),
        "numerator": result.numerator,
        "denominator": result.denominator,
    }


@router.post("/quantize", response_model=None, summary="Quantize durations to grid")
def quantize_endpoint(req: QuantizeRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = quantize(phrase, req.grid)
    return _phrase_response(result)


@router.post("/metric-modulation", response_model=None, summary="Re-interpret beat unit")
def metric_modulation_endpoint(req: MetricModulationRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    # Parse duration strings by creating tiny CN snippets
    old_phrase = _parse_phrase(f"{req.old_unit} c4")
    new_phrase = _parse_phrase(f"{req.new_unit} c4")
    old_dur = old_phrase[0].duration
    new_dur = new_phrase[0].duration
    result = metric_modulation(phrase, old_dur, new_dur)
    return _phrase_response(result)


# ---------------------------------------------------------------------------
# Melodic transforms
# ---------------------------------------------------------------------------


@router.post("/rotate", response_model=None, summary="Rotate events by n positions")
def rotate_endpoint(req: RotateRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = rotate(phrase, req.n)
    return _phrase_response(result)


@router.post("/permute", response_model=None, summary="Reorder events by index list")
def permute_endpoint(req: PermuteRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = permute(phrase, req.indices)
    return _phrase_response(result)


@router.post("/interpolate", response_model=None, summary="Insert passing notes between events")
def interpolate_endpoint(req: InterpolateRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = interpolate(phrase, req.steps)
    return _phrase_response(result)


@router.post("/omit", response_model=None, summary="Remove every nth event")
def omit_endpoint(req: OmitRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = omit(phrase, n=req.n)
    return _phrase_response(result)


@router.post("/repeat", response_model=None, summary="Repeat phrase n times")
def repeat_endpoint(req: RepeatRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = repeat(phrase, req.n)
    return _phrase_response(result)


@router.post("/mirror", response_model=None, summary="Mirror phrase (palindrome)")
def mirror_endpoint(req: PhraseOnlyRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = mirror(phrase)
    return _phrase_response(result)


@router.post("/fragment", response_model=None, summary="Split phrase into sub-phrases")
def fragment_endpoint(req: FragmentRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    fragments = fragment(phrase, req.lengths)
    return {
        "phrases": [_phrase_response(f) for f in fragments],
    }


@router.post("/concatenate", response_model=None, summary="Join multiple phrases into one")
def concatenate_endpoint(req: ConcatenateRequest) -> dict:
    parsed = [_parse_phrase(p) for p in req.phrases]
    result = concatenate(*parsed)
    return _phrase_response(result)


@router.post("/interleave", response_model=None, summary="Interleave two phrases")
def interleave_endpoint(req: InterleaveRequest) -> dict:
    p1 = _parse_phrase(req.phrase)
    p2 = _parse_phrase(req.phrase2)
    result = interleave(p1, p2)
    return _phrase_response(result)


# ---------------------------------------------------------------------------
# Stub endpoints (not available over HTTP)
# ---------------------------------------------------------------------------


@router.post("/pitch-map", response_model=None, summary="Apply pitch mapping function (not available over HTTP)")
def pitch_map_endpoint(req: PhraseOnlyRequest) -> dict:
    raise CadenzaAPIError(
        NOT_IMPLEMENTED,
        "pitch-map requires a Python callable; not available over HTTP",
        "",
    )


@router.post("/swing", response_model=None, summary="Apply swing feel (not yet implemented)")
def swing_endpoint(req: PhraseOnlyRequest) -> dict:
    raise CadenzaAPIError(
        NOT_IMPLEMENTED,
        "swing is not yet implemented in the core library",
        "",
    )
