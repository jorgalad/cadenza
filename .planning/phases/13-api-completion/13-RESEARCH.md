# Phase 13: API Completion - Research

**Researched:** 2026-03-22
**Domain:** FastAPI route coverage, async job pattern, batch dispatch
**Confidence:** HIGH

## Summary

Phase 13 is a purely HTTP-layer phase: no new music theory logic, only new FastAPI route modules wrapping existing library functions. The codebase has extremely well-established patterns from Phase 4 (`transforms.py`, `theory.py`) that should be replicated exactly across 7 new route files + 1 jobs file + 1 batch dispatcher. The two new architectural concerns are (1) the async job pattern for counterpoint generators using `threading.Thread` with in-memory job storage, and (2) a batch dispatcher that routes operation slugs to handler functions.

Key complexity lies in the volume of endpoints (~40+), the variety of return types (phrases, scores, dataclass results, file downloads), and the fact that several library functions accept Python callables (`filter_phrase`, `add_articulation_if`, `remove_articulation_if`, `apply_windowed`, `tendency_mask_melody`) which cannot be directly exposed over HTTP. These need either stub endpoints (like `pitch-map`) or predicate-based alternatives with fixed predicate names.

**Primary recommendation:** Follow the established thin-handler pattern exactly. Factor `_parse_phrase` and `_phrase_response` into a shared helpers module so all route files can import them. Build the batch dispatcher as a registry dict populated at import time.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Route coverage: 7 new route files (`analysis.py`, `batch_ops.py`, `counterpoint.py`, `settheory.py`, `patterns.py`, `composition.py`, `io.py`) + `jobs.py`
- URL hierarchy: `POST /v1/{module}/{operation}` with specific module names (analysis, batch-ops, counterpoint, settheory, patterns, composition, io)
- Score response format: `{"voices": [{"name": "...", "phrase": "...", "events": [...]}]}` with `ScoreResponse` / `VoiceResponse` Pydantic models
- I/O endpoints: multipart/form-data upload for import, octet-stream/XML download for export
- Stochastic endpoints: optional `seed: int | None = null` field
- Markov: separate train + generate, plus optional combined `POST /v1/composition/markov-generate`
- Async job pattern (API-06): counterpoint only, `POST /v1/counterpoint/{op}/async`, in-memory dict, `threading.Thread`, `GET /v1/jobs/{id}`, TTL 5 min after done/failed, 410 Gone on expiry
- Batch endpoint (API-09): `POST /v1/batch`, sequential execution, continue-on-error, max 50 ops, registry-based dispatcher
- OpenAPI polish: summary + description + tags + Field descriptions on all new endpoints

### Claude's Discretion
- Exact Pydantic model names for new request types
- Whether to use `APIRouter(prefix=...)` or manual prefix in route decorators
- Threading model details (thread pool vs. new thread per job)
- Whether markov_melody gets combined train+generate endpoint or separate endpoints

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| API-06 | Async job pattern for expensive operations (counterpoint generation) | Async job pattern architecture: in-memory dict, threading.Thread, polling endpoint, TTL expiry. All counterpoint generators return Phrase or Score -- route handlers serialize to ScoreResponse. |
| API-09 | Batch endpoint: apply multiple operations in a single request | Batch dispatcher architecture: registry dict mapping slug to handler, sequential execution, per-operation error handling, 50-op cap. All existing route handlers need factored logic callable without HTTP. |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | >=0.115,<1.0 | HTTP framework | Already in use (pyproject.toml `[api]` extra) |
| Pydantic | v2 (via FastAPI) | Request/response validation | Already in use for all schemas |
| uvicorn | >=0.30 | ASGI server | Already in use |
| python-multipart | (FastAPI dep) | File upload handling | Required by FastAPI for `UploadFile` / `Form` |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| threading (stdlib) | N/A | Async job execution | Counterpoint async endpoints only |
| uuid (stdlib) | N/A | Job ID generation | `uuid.uuid4()` for job IDs |
| time (stdlib) | N/A | Job TTL tracking | `time.monotonic()` for expiry timestamps |
| tempfile (stdlib) | N/A | I/O file handling | Writing uploaded files to disk for import, writing export output |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| threading.Thread | concurrent.futures.ThreadPoolExecutor | Pool limits max concurrent jobs but is heavier setup; per-thread is simpler for localhost use |
| In-memory dict | Redis/SQLite | Massive overkill for localhost Dorico integration |

**Installation:**
```bash
pip install cadenza[api]  # python-multipart comes with FastAPI
```

**Note:** `python-multipart` is required for `UploadFile` in FastAPI. Verify it is installed with the `[api]` extra. If not, add it to `pyproject.toml`.

## Architecture Patterns

### Recommended Project Structure
```
src/cadenza/api/
    __init__.py          # create_app() -- add include_router for all new routers
    errors.py            # Add new error codes: BATCH_TOO_LARGE, JOB_NOT_FOUND, JOB_EXPIRED
    schemas.py           # Add ~30+ new Pydantic request models + ScoreResponse + VoiceResponse + JobResponse + BatchRequest/Response
    parsing.py           # Existing (no changes needed)
    helpers.py           # NEW: factor _parse_phrase, _phrase_response, _score_response out of transforms.py
    routes/
        health.py        # Existing
        transforms.py    # Existing (update imports to use helpers.py)
        theory.py        # Existing (no changes)
        analysis.py      # NEW
        batch_ops.py     # NEW
        counterpoint.py  # NEW (sync + async variants)
        settheory.py     # NEW
        patterns.py      # NEW
        composition.py   # NEW
        io.py            # NEW
        jobs.py          # NEW (GET /v1/jobs/{id})
        batch.py         # NEW (POST /v1/batch dispatcher)
```

### Pattern 1: Thin Route Handler (established)
**What:** Route handler parses CN input, calls library function, serializes response.
**When to use:** All endpoints.
**Example:**
```python
# Source: existing transforms.py pattern
@router.post("/detect-key", response_model=None, summary="Detect most likely key", description="...")
def detect_key_endpoint(req: PhraseOnlyRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = detect_key(phrase)
    return {
        "root": _pitch_to_cn(result.root),
        "mode": result.mode,
        "confidence": result.confidence,
    }
```

### Pattern 2: Score Response Serialization
**What:** Operations returning `Score` serialize to the named-voices array format.
**When to use:** Counterpoint generators, `rhythmic_canon`, `hocket`, `generate_multi_voice_counterpoint`.
**Example:**
```python
def _score_response(score: Score) -> dict:
    """Serialize Score to {voices: [{name, phrase, events}]}."""
    voices = []
    for name, phrase in score._voices:
        voices.append({
            "name": name,
            "phrase": to_cn(phrase),
            "events": _to_serializable(phrase),
        })
    return {"voices": voices}
```

### Pattern 3: Async Job Submission
**What:** POST to `/async` variant starts a thread, returns job ID immediately.
**When to use:** Counterpoint generation endpoints only.
**Example:**
```python
import threading, uuid, time

_jobs: dict[str, dict] = {}  # Global in-memory store
_JOB_TTL = 300  # 5 minutes

def _run_job(job_id: str, func, *args, **kwargs):
    _jobs[job_id]["status"] = "running"
    try:
        result = func(*args, **kwargs)
        _jobs[job_id]["result"] = _score_response(result) if isinstance(result, Score) else _phrase_response(result)
        _jobs[job_id]["status"] = "done"
    except Exception as e:
        _jobs[job_id]["error"] = {"error": type(e).__name__, "message": str(e)}
        _jobs[job_id]["status"] = "failed"
    _jobs[job_id]["finished_at"] = time.monotonic()

@router.post("/generate-first-species/async", response_model=None, summary="Generate first species (async)")
def generate_first_species_async(req: CounterpointRequest) -> dict:
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"status": "pending", "result": None, "error": None, "finished_at": None}
    cf = _parse_phrase(req.phrase)
    t = threading.Thread(target=_run_job, args=(job_id, generate_first_species, cf, req.above))
    t.daemon = True
    t.start()
    return {"job_id": job_id, "status": "pending"}
```

### Pattern 4: Batch Dispatcher
**What:** Registry mapping operation slugs to handler callables.
**When to use:** `POST /v1/batch` endpoint.
**Example:**
```python
# Registry built at module import
_DISPATCH: dict[str, Callable[[dict], dict]] = {}

def register(slug: str):
    def decorator(func):
        _DISPATCH[slug] = func
        return func
    return decorator

# In batch.py route handler:
@router.post("", response_model=None, summary="Execute multiple operations in one request")
def batch_endpoint(req: BatchRequest) -> dict:
    if len(req.operations) > 50:
        raise CadenzaAPIError(BATCH_TOO_LARGE, f"Max 50 operations, got {len(req.operations)}", "")
    results = []
    for op in req.operations:
        try:
            handler = _DISPATCH.get(op.operation)
            if handler is None:
                results.append({"status": "error", "error": {"error": "UNKNOWN_OPERATION", "message": f"Unknown: {op.operation}"}})
                continue
            result = handler(op.params)
            results.append({"status": "ok", "result": result})
        except Exception as e:
            results.append({"status": "error", "error": {"error": type(e).__name__, "message": str(e)}})
    return {"results": results}
```

### Pattern 5: File Upload/Download for I/O
**What:** Multipart upload for import, streaming download for export.
**When to use:** I/O endpoints only.
**Example:**
```python
from fastapi import UploadFile, File, Form
from fastapi.responses import StreamingResponse
import tempfile, io

@router.post("/import-musicxml", response_model=None, summary="Import MusicXML file")
async def import_musicxml_endpoint(file: UploadFile = File(...)) -> dict:
    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp.flush()
        result, warnings = import_musicxml(tmp.name)
    if isinstance(result, Score):
        response = _score_response(result)
    else:
        response = _phrase_response(result)
    response["warnings"] = [{"category": w.category, "message": w.message} for w in warnings]
    return response

@router.post("/export-musicxml", response_model=None, summary="Export to MusicXML")
def export_musicxml_endpoint(req: ExportPhraseRequest) -> StreamingResponse:
    phrase = _parse_phrase(req.phrase)
    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tmp:
        export_musicxml(phrase, tmp.name)
        tmp.seek(0)
        content = open(tmp.name, "rb").read()
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/xml",
        headers={"Content-Disposition": "attachment; filename=export.xml"},
    )
```

### Anti-Patterns to Avoid
- **Internal HTTP requests for batch:** Never have the batch dispatcher call the API endpoints via HTTP. Always call the handler function directly.
- **Blocking the event loop with threads:** Use `threading.Thread` with `daemon=True` -- do not use `asyncio.to_thread` since the counterpoint functions are CPU-bound and this is a localhost server.
- **Duplicating helper code:** Factor `_parse_phrase`, `_phrase_response`, `_score_response` into `helpers.py` -- do not copy them into each route file.
- **Exposing callable-based functions without adaptation:** `filter_phrase`, `add_articulation_if`, `remove_articulation_if`, `apply_windowed`, and `tendency_mask_melody` accept Python callables. Either provide fixed predicate names or mark as NOT_IMPLEMENTED over HTTP (like `pitch-map`).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| File upload parsing | Manual multipart parsing | FastAPI `UploadFile` + `python-multipart` | Edge cases in multipart boundary handling |
| Job ID generation | Custom ID scheme | `uuid.uuid4()` | Collision-free, standard |
| Thread-safe dict access | Custom locking | Python GIL + dict (sufficient for localhost) | dict operations are atomic under GIL for simple get/set |
| OpenAPI docs | Manual spec writing | FastAPI auto-generation with `summary`, `description`, `tags`, `Field(description=...)` | Already established pattern |
| Streaming responses | Manual chunked encoding | `fastapi.responses.StreamingResponse` | Handles headers, content-type correctly |

**Key insight:** This phase is high-volume but low-novelty. Every pattern exists already in the codebase. The risk is inconsistency, not missing capabilities.

## Common Pitfalls

### Pitfall 1: Functions That Accept Callables
**What goes wrong:** `filter_phrase(phrase, predicate)`, `add_articulation_if(phrase, predicate, art)`, `remove_articulation_if(phrase, predicate, art)`, `apply_windowed(phrase, func, window_size)`, and `tendency_mask_melody(mask, length, ...)` all accept Python callables that cannot be serialized as JSON.
**Why it happens:** These are designed for Python-native use, not HTTP.
**How to avoid:** For predicate-based batch ops, define a fixed set of named predicates (e.g., "every_nth", "on_beat") and map strings to callables in the route handler. For `apply_windowed` and `tendency_mask_melody`, mark as NOT_IMPLEMENTED over HTTP (like `pitch-map`). Or omit them from the route list entirely since CONTEXT.md lists specific batch ops.
**Warning signs:** Getting 422 errors from Pydantic trying to accept a function parameter.

### Pitfall 2: Score vs Phrase Return Type Ambiguity
**What goes wrong:** Some counterpoint generators return `Phrase` (single voice), others return `Score` (multi-voice). The route handler must check the return type.
**Why it happens:** `generate_first_species` through `generate_free_counterpoint` return `Phrase`. Only `generate_multi_voice_counterpoint` returns `Score`. But for the API, wrapping single-voice results in a ScoreResponse (CF + generated voice) is more useful.
**How to avoid:** In the route handler, always construct a `Score` from the CF + generated counterpoint for consistent response shape. Return as `ScoreResponse`.
**Warning signs:** Inconsistent response shapes between counterpoint endpoints.

### Pitfall 3: Batch Dispatcher Registry Must Include All Operations
**What goes wrong:** New operations added but not registered in the batch dispatcher, causing "unknown operation" errors.
**Why it happens:** Registration is separate from route definition.
**How to avoid:** Build the registry programmatically at import time. Consider having each route handler register itself, or build the registry from a central mapping.
**Warning signs:** Batch operations returning errors for operations that work individually.

### Pitfall 4: I/O Functions Require File Paths, Not Bytes
**What goes wrong:** `import_musicxml(path)`, `import_midi(path)`, `export_musicxml(source, path)`, and `export_midi(source, path)` all take filesystem paths, not file-like objects.
**Why it happens:** The I/O module was designed for CLI/script use.
**How to avoid:** Use `tempfile.NamedTemporaryFile` to write uploaded content to disk, pass the path to the library function, then read results and return.
**Warning signs:** TypeError about expected path.

### Pitfall 5: Markov Model Serialization
**What goes wrong:** `MarkovModel` is a frozen dataclass with `transition_table: dict[tuple[int, ...], dict[int, float]]`. Tuple keys in JSON become strings.
**Why it happens:** JSON does not support tuple keys in dicts.
**How to avoid:** The combined `markov-generate` endpoint (train from phrase + generate in one call) avoids serialization entirely. For the separate train/generate flow, serialize `MarkovModel` with string keys (e.g., `"60,62,64"`) and deserialize back.
**Warning signs:** JSON serialization errors on tuple-keyed dicts.

### Pitfall 6: python-multipart Dependency
**What goes wrong:** `UploadFile` fails at runtime with "pip install python-multipart" error.
**Why it happens:** `python-multipart` is not a direct FastAPI dependency, but is required for form/file handling.
**How to avoid:** Ensure `python-multipart` is in the `[api]` extra dependencies in `pyproject.toml`. FastAPI >= 0.115 should include it as a dependency, but verify.
**Warning signs:** Import error or runtime error mentioning multipart.

### Pitfall 7: Thread Safety of Job Store
**What goes wrong:** Race condition between job thread writing result and polling endpoint reading.
**Why it happens:** Concurrent access to `_jobs` dict.
**How to avoid:** Python's GIL makes simple dict get/set atomic. The job thread sets `result` then `status` (in that order), so the polling endpoint sees `done` only after result is written. Use `threading.Lock` only if doing compound operations.
**Warning signs:** Polling returns `done` but `result` is `None`.

## Code Examples

### Shared Helpers Module (helpers.py)
```python
"""Shared route handler helpers -- parse and serialize CN phrases and scores."""
from cadenza.cn import parse_cn, to_cn
from cadenza.core.json_codec import _to_serializable
from cadenza.core.score import Score

def _parse_phrase(cn_string: str) -> tuple:
    phrase, _warnings = parse_cn(cn_string)
    return phrase

def _phrase_response(phrase: tuple) -> dict:
    return {"phrase": to_cn(phrase), "events": _to_serializable(phrase)}

def _score_response(score: Score) -> dict:
    voices = []
    for name, phrase in score._voices:
        voices.append({
            "name": name,
            "phrase": to_cn(phrase),
            "events": _to_serializable(phrase),
        })
    return {"voices": voices}
```

### New Error Codes
```python
# Add to errors.py
BATCH_TOO_LARGE = "BATCH_TOO_LARGE"
JOB_NOT_FOUND = "JOB_NOT_FOUND"
JOB_EXPIRED = "JOB_EXPIRED"
UNKNOWN_OPERATION = "UNKNOWN_OPERATION"
```

### ScoreResponse Model
```python
# Add to schemas.py
class VoiceResponse(BaseModel):
    name: str = Field(..., description="Voice name")
    phrase: str = Field(..., description="CN notation string for this voice")
    events: dict | list = Field(..., description="JSON event structure")

class ScoreResponse(BaseModel):
    voices: list[VoiceResponse] = Field(..., description="Named voices array")

class JobStatusResponse(BaseModel):
    job_id: str = Field(..., description="UUID of the job")
    status: str = Field(..., description="pending | running | done | failed")
    result: ScoreResponse | None = Field(None, description="Result when status is done")
    error: ErrorResponse | None = Field(None, description="Error when status is failed")

class BatchOperation(BaseModel):
    operation: str = Field(..., description="Operation slug matching endpoint path")
    params: dict = Field(..., description="Operation parameters")

class BatchRequest(BaseModel):
    operations: list[BatchOperation] = Field(..., description="List of operations to execute")

class BatchResultItem(BaseModel):
    status: str = Field(..., description="ok | error")
    result: dict | None = Field(None, description="Operation result on success")
    error: dict | None = Field(None, description="Error details on failure")

class BatchResponse(BaseModel):
    results: list[BatchResultItem]
```

### Callable-Parameter Workarounds
Functions accepting Python callables need HTTP-friendly alternatives:

| Function | Callable Param | HTTP Solution |
|----------|---------------|---------------|
| `add_articulation_if(phrase, predicate, art)` | `predicate: Callable` | Accept `"nth": int` param, construct `lambda e, i=i: i % nth == 0` in handler |
| `remove_articulation_if(phrase, predicate, art)` | `predicate: Callable` | Same as above |
| `filter_phrase(phrase, predicate)` | `predicate: Callable` | Accept `"has_articulation": str` or `"min_pitch"/"max_pitch"` filters |
| `apply_windowed(phrase, func, window_size)` | `func: Callable` | Mark NOT_IMPLEMENTED (or omit -- CONTEXT.md lists it but callable can't be serialized) |
| `tendency_mask_melody(mask, length, ...)` | `mask: Callable` | Mark NOT_IMPLEMENTED (requires arbitrary Python function) |

Per CONTEXT.md, `add_articulation_if`, `remove_articulation_if`, and `filter_phrase` are listed as batch_ops routes. Simplest approach: accept fixed predicate types as string enums (e.g., `"every_nth"`) with parameters.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual OpenAPI specs | FastAPI auto-generation | Already in use | All endpoints get free Swagger docs |
| Celery/Redis for async | In-memory + threading | Phase design decision | No external deps for localhost use |

**No deprecated patterns to worry about** -- this phase uses established project patterns only.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest >=8.0 with httpx TestClient |
| Config file | `pyproject.toml [tool.pytest.ini_options]` |
| Quick run command | `python -m pytest tests/api/ -x -q` |
| Full suite command | `python -m pytest tests/ -x -q` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| API-06 | Async job submit returns job_id + pending | integration | `python -m pytest tests/api/test_jobs.py -x` | No -- Wave 0 |
| API-06 | Job polling returns done/failed with result | integration | `python -m pytest tests/api/test_jobs.py -x` | No -- Wave 0 |
| API-06 | Job TTL expiry returns 410 Gone | integration | `python -m pytest tests/api/test_jobs.py -x` | No -- Wave 0 |
| API-09 | Batch endpoint executes operations sequentially | integration | `python -m pytest tests/api/test_batch.py -x` | No -- Wave 0 |
| API-09 | Batch continues on error, reports per-op status | integration | `python -m pytest tests/api/test_batch.py -x` | No -- Wave 0 |
| API-09 | Batch rejects > 50 operations | integration | `python -m pytest tests/api/test_batch.py -x` | No -- Wave 0 |
| API-06/09 | All new endpoints appear in OpenAPI schema | smoke | `python -m pytest tests/api/test_openapi.py -x` | Yes (needs update) |
| -- | Each new route module endpoints return 200 | integration | `python -m pytest tests/api/test_analysis.py tests/api/test_counterpoint.py tests/api/test_settheory.py tests/api/test_patterns.py tests/api/test_composition.py tests/api/test_io.py tests/api/test_batch_ops.py -x` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/api/ -x -q`
- **Per wave merge:** `python -m pytest tests/ -x -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/api/test_analysis.py` -- covers analysis route endpoints
- [ ] `tests/api/test_batch_ops.py` -- covers batch_ops route endpoints
- [ ] `tests/api/test_counterpoint.py` -- covers counterpoint sync + async endpoints
- [ ] `tests/api/test_settheory.py` -- covers set theory route endpoints
- [ ] `tests/api/test_patterns.py` -- covers patterns route endpoints
- [ ] `tests/api/test_composition.py` -- covers composition route endpoints
- [ ] `tests/api/test_io.py` -- covers I/O import/export endpoints
- [ ] `tests/api/test_jobs.py` -- covers job polling, TTL, 410 Gone
- [ ] `tests/api/test_batch.py` -- covers batch dispatch endpoint (API-09)
- [ ] Update `tests/api/test_openapi.py` -- add assertions for new endpoint paths

## Open Questions

1. **`apply_windowed` over HTTP**
   - What we know: Accepts a `Callable[[Phrase], Phrase]` -- cannot be serialized.
   - What's unclear: Whether to omit it entirely or provide a limited set of named transforms.
   - Recommendation: Mark as NOT_IMPLEMENTED over HTTP (like `pitch-map`). CONTEXT.md lists it but the callable restriction makes full HTTP exposure impossible.

2. **`tendency_mask_melody` over HTTP**
   - What we know: Accepts `Callable[[float], dict[Pitch, float]]` -- cannot be serialized.
   - What's unclear: Same as above.
   - Recommendation: Mark as NOT_IMPLEMENTED. The Python library API remains the way to use this function.

3. **`filter_phrase` predicate options**
   - What we know: CONTEXT.md lists `filter_phrase` as a batch_ops endpoint.
   - What's unclear: Which fixed predicates to expose.
   - Recommendation: Expose a few useful predicates: `has_articulation`, `min_pitch`, `max_pitch`, `is_note` (filter out rests). Accept as optional filter params.

4. **Thread pool vs per-job thread**
   - What we know: CONTEXT.md says Claude's discretion.
   - Recommendation: Use `threading.Thread` per job (simpler, sufficient for localhost). If needed later, swap to `ThreadPoolExecutor` with max_workers=4.

## Sources

### Primary (HIGH confidence)
- Existing codebase: `src/cadenza/api/` -- all established patterns
- `src/cadenza/api/routes/transforms.py` -- thin handler pattern, `_parse_phrase`, `_phrase_response`
- `src/cadenza/api/schemas.py` -- Pydantic v2 model patterns
- `src/cadenza/api/errors.py` -- error handling infrastructure
- All module `__init__.py` files -- public API surface for each module
- Function signatures from `analysis/`, `counterpoint/`, `composition/`, `patterns/`, `batch/`, `io/` -- parameter types and return types

### Secondary (MEDIUM confidence)
- FastAPI docs on `UploadFile`, `StreamingResponse`, `python-multipart` requirement
- Python `threading.Thread` for CPU-bound tasks

### Tertiary (LOW confidence)
- None -- all findings verified against existing codebase

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- already in use, no new dependencies
- Architecture: HIGH -- all patterns established in Phase 4, just replication
- Pitfalls: HIGH -- identified from reading actual function signatures (callable params, path-based I/O, Score vs Phrase)

**Research date:** 2026-03-22
**Valid until:** 2026-04-22 (stable -- no external dependency changes expected)
