"""Batch operation endpoints -- thin route handlers calling cadenza.batch."""

from __future__ import annotations

from fastapi import APIRouter

from cadenza.api.errors import NOT_IMPLEMENTED, CadenzaAPIError
from cadenza.api.helpers import (
    _parse_phrase,
    _phrase_response,
    _safe_parse_pitch,
)
from cadenza.api.schemas import (
    AddArticulationIfRequest,
    CrescendoRequest,
    FilterPhraseRequest,
    HumanizeRequest,
    PhraseOnlyRequest,
    QuantizeLengthsRequest,
    RemoveArticulationIfRequest,
    ReplacePitchRequest,
    SetArticulationNthRequest,
    SetDynamicNthRequest,
)
from cadenza.batch import (
    add_articulation_if,
    crescendo,
    decrescendo,
    filter_phrase,
    humanize,
    quantize_lengths,
    remove_articulation_if,
    replace_pitch,
    set_articulation_nth,
    set_dynamic_nth,
)
from cadenza.core.note import Note

router = APIRouter(prefix="/v1/batch-ops", tags=["batch-ops"])


# ---------------------------------------------------------------------------
# Articulation / dynamic endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/set-articulation-nth",
    response_model=None,
    summary="Set articulation on every Nth note",
    description="Add an articulation marking to every Nth note in a phrase (1-indexed, rests skipped).",
)
def set_articulation_nth_endpoint(req: SetArticulationNthRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = set_articulation_nth(phrase, req.n, req.articulation)
    return _phrase_response(result)


@router.post(
    "/set-dynamic-nth",
    response_model=None,
    summary="Set dynamic on every Nth note",
    description="Set a dynamic marking on every Nth note in a phrase (1-indexed, rests skipped).",
)
def set_dynamic_nth_endpoint(req: SetDynamicNthRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = set_dynamic_nth(phrase, req.n, req.dynamic)
    return _phrase_response(result)


@router.post(
    "/crescendo",
    response_model=None,
    summary="Apply crescendo across a phrase",
    description="Distribute dynamics linearly from start to end across all notes in the phrase.",
)
def crescendo_endpoint(req: CrescendoRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = crescendo(phrase, req.start, req.end)
    return _phrase_response(result)


@router.post(
    "/decrescendo",
    response_model=None,
    summary="Apply decrescendo across a phrase",
    description="Distribute dynamics linearly from start to end (loud to soft) across all notes in the phrase.",
)
def decrescendo_endpoint(req: CrescendoRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = decrescendo(phrase, req.start, req.end)
    return _phrase_response(result)


# ---------------------------------------------------------------------------
# Predicate-based articulation endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/add-articulation-if",
    response_model=None,
    summary="Add articulation to every Nth note",
    description="Add an articulation to every Nth note using a modular index predicate. "
    "For example, nth=2 adds the articulation to every 2nd note.",
)
def add_articulation_if_endpoint(req: AddArticulationIfRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    note_count = 0

    def predicate(event: object) -> bool:
        nonlocal note_count
        if isinstance(event, Note):
            note_count += 1
            return note_count % req.nth == 0
        return False

    result = add_articulation_if(phrase, predicate, req.articulation)
    return _phrase_response(result)


@router.post(
    "/remove-articulation-if",
    response_model=None,
    summary="Remove articulation from every Nth note",
    description="Remove an articulation from every Nth note using a modular index predicate.",
)
def remove_articulation_if_endpoint(req: RemoveArticulationIfRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    note_count = 0

    def predicate(event: object) -> bool:
        nonlocal note_count
        if isinstance(event, Note):
            note_count += 1
            return note_count % req.nth == 0
        return False

    result = remove_articulation_if(phrase, predicate, req.articulation)
    return _phrase_response(result)


# ---------------------------------------------------------------------------
# Pitch / filter endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/replace-pitch",
    response_model=None,
    summary="Replace all occurrences of a pitch",
    description="Replace every occurrence of a specific pitch with a new pitch throughout the phrase.",
)
def replace_pitch_endpoint(req: ReplacePitchRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    old = _safe_parse_pitch(req.old_pitch)
    new = _safe_parse_pitch(req.new_pitch)
    result = replace_pitch(phrase, old, new)
    return _phrase_response(result)


@router.post(
    "/filter-phrase",
    response_model=None,
    summary="Filter phrase events by criteria",
    description="Keep only events matching the filter criteria: articulation match or note/rest selection.",
)
def filter_phrase_endpoint(req: FilterPhraseRequest) -> dict:
    phrase = _parse_phrase(req.phrase)

    def predicate(event: object) -> bool:
        if req.has_articulation is not None:
            if isinstance(event, Note):
                return req.has_articulation in event.articulations
            return False
        if not req.is_note:
            return not isinstance(event, Note)
        return isinstance(event, Note)

    result = filter_phrase(phrase, predicate)
    return _phrase_response(result)


# ---------------------------------------------------------------------------
# Rhythm endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/quantize-lengths",
    response_model=None,
    summary="Quantize durations to a rhythmic grid",
    description="Snap all event durations to the nearest value on a specified grid.",
)
def quantize_lengths_endpoint(req: QuantizeLengthsRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = quantize_lengths(phrase, req.grid)
    return _phrase_response(result)


@router.post(
    "/humanize",
    response_model=None,
    summary="Humanize timing of a phrase",
    description="Add subtle random variations to timing for a more natural feel.",
)
def humanize_endpoint(req: HumanizeRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = humanize(phrase, req.seed)
    return _phrase_response(result)


# ---------------------------------------------------------------------------
# Stub endpoints (not available over HTTP)
# ---------------------------------------------------------------------------


@router.post(
    "/apply-windowed",
    response_model=None,
    summary="Apply windowed function (not available over HTTP)",
    description="This operation requires a Python callable and cannot be executed over HTTP.",
)
def apply_windowed_endpoint(req: PhraseOnlyRequest) -> dict:
    raise CadenzaAPIError(
        NOT_IMPLEMENTED,
        "apply-windowed requires a Python callable; not available over HTTP",
        "",
    )
