# Phase 4: REST API v1 - Research

**Researched:** 2026-03-19
**Domain:** FastAPI REST API wrapping existing Python music library
**Confidence:** HIGH

## Summary

Phase 4 is a pure HTTP layer over the existing `cadenza.core`, `cadenza.transforms`, `cadenza.theory`, and `cadenza.cn` modules. No new music-theory logic is added. The work involves: (1) adding FastAPI + uvicorn as the first runtime dependencies, (2) creating Pydantic v2 request/response schemas that parse compact music strings (like `"m3"`, `"eb4"`, `"dorian"`) into core types, (3) wiring ~25 endpoints as thin wrappers over existing functions, (4) building a structured error handling layer that catches `ValueError`/`ParseError` from the core library and translates them into music-theory-aware HTTP error codes, and (5) ensuring OpenAPI docs auto-generate correctly.

A critical implementation detail: neither `Pitch` nor `Interval` have `from_string()` classmethods. The API layer must implement parsing utilities (or Pydantic validators) that convert compact string representations (`"eb4"` -> `Pitch(step="e", accidental="b", octave=4)`, `"m3"` -> `Interval(quality="m", number=3, direction=1)`) into the frozen dataclass instances the core library expects. This is the main "glue code" in the phase.

**Primary recommendation:** Build a thin `cadenza.api.parsing` module with `parse_pitch_string()` and `parse_interval_string()` helper functions, then use them as Pydantic field validators in the schema models. Keep all route handlers as 3-5 line functions: parse input, call library, serialize output.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Request envelope:** Input field name is `"phrase"` (the musical concept). CN strings only in v1. Musical parameters as compact CN strings (`"m3"`, `"eb4"`, `"dorian"`).
- **Response envelope:** Single-phrase responses are flat `{ "phrase": "...", "events": [...] }`. Multi-phrase responses use `{ "phrases": [{"phrase": "...", "events": [...]}, ...] }`.
- **Events format:** Uses existing `cadenza.core.json_codec` output format exactly. No custom serialization.
- **One endpoint per function** with explicit URL hierarchy:
  - `GET /v1/health`
  - `POST /v1/transform/{operation}` for all transforms (kebab-case)
  - `POST /v1/theory/scale`, `POST /v1/theory/chord`, `POST /v1/theory/diatonic-chords`, `POST /v1/theory/secondary-dominant`, `POST /v1/theory/aug6`, `POST /v1/theory/neapolitan`
- **HTTP status codes:** `422` for domain errors, `400` for malformed JSON, `500` for unexpected.
- **Error body shape:** `{ "error": "INVALID_PITCH", "message": "...", "input": "..." }`
- **Music-theory-aware error codes:** `INVALID_CN`, `INVALID_PITCH`, `INVALID_INTERVAL`, `INVALID_SCALE_NAME`, `INVALID_CHORD_SYMBOL`, `TRANSPOSE_OUT_OF_RANGE`, `NOT_IMPLEMENTED`
- **Deployment:** Localhost `127.0.0.1:8000` by default, `--host 0.0.0.0` flag for network.
- **Health endpoint response:** `{ "status": "ok", "version": "1", "cadenza_version": "0.1.0" }`
- **FastAPI + Pydantic v2** as first runtime dep. Core library remains zero-dep.
- **Module layout:**
  - `src/cadenza/api/__init__.py` -- FastAPI app instance
  - `src/cadenza/api/routes/transforms.py`
  - `src/cadenza/api/routes/theory.py`
  - `src/cadenza/api/routes/health.py`
  - `src/cadenza/api/schemas.py`
  - `src/cadenza/api/errors.py`

### Claude's Discretion
- Exact Pydantic model field validators (how interval strings are parsed in schemas)
- OpenAPI tags and description strings
- Whether to use FastAPI `APIRouter` per route file (yes -- standard pattern)
- `uvicorn` as the ASGI server (standard FastAPI choice)

### Deferred Ideas (OUT OF SCOPE)
- Async jobs (API-06) -- deferred to Phase 13
- Batch endpoint (API-09) -- deferred to Phase 13
- API key authentication for network deployment
- WebSocket support for streaming results
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| API-01 | FastAPI server exposing all transform, analysis, and generation operations as HTTP endpoints | Standard Stack (FastAPI + uvicorn), Architecture Patterns (router-per-domain), endpoint-to-function mapping |
| API-02 | All endpoints accept CN notation strings as input | `cadenza.cn.parse_cn()` exists; Pydantic validators parse compact pitch/interval strings; `"phrase"` field convention |
| API-03 | All endpoints return both CN string and JSON event list in every response | Response envelope pattern using `cadenza.cn.to_cn()` + `cadenza.core.json_codec._to_serializable()` |
| API-04 | Versioned API (`/v1/` prefix) from day one | FastAPI APIRouter with `prefix="/v1"` |
| API-05 | Comprehensive OpenAPI/Swagger documentation auto-generated | FastAPI auto-generates from Pydantic models + `summary`/`description` kwargs on route decorators |
| API-07 | Structured error responses with music-theory-aware error codes | Custom exception classes + FastAPI exception handlers mapping to 422 responses |
| API-08 | Health check endpoint for DAW integration probing | Simple `GET /v1/health` returning JSON with status, version, cadenza_version |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| fastapi | >=0.115,<1.0 | ASGI web framework with auto OpenAPI | De facto Python API framework; Pydantic-native validation; auto /docs |
| pydantic | >=2.10 | Request/response schema validation | Ships with FastAPI; v2 is the current standard |
| uvicorn | >=0.30 | ASGI server | Official FastAPI recommendation; lightweight |

### Supporting (dev/test only)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| httpx | >=0.27 | Async HTTP client for TestClient | FastAPI's TestClient requires it; replaces requests for async |
| pytest | >=8.0 | Test framework | Already in dev deps |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| FastAPI | Litestar | Locked decision: FastAPI chosen |
| uvicorn | hypercorn | uvicorn is simpler, standard for FastAPI |
| httpx (test) | requests | FastAPI TestClient uses httpx internally since 0.100+ |

**Installation (runtime):**
```bash
# Add to pyproject.toml [project.dependencies]
fastapi>=0.115,<1.0
uvicorn[standard]>=0.30

# Add to [project.optional-dependencies] dev
httpx>=0.27
```

**Version verification (2026-03-19):**
- fastapi: 0.135.1 (latest on PyPI)
- uvicorn: 0.42.0 (latest on PyPI)
- pydantic: 2.12.5 (latest on PyPI, ships with FastAPI)
- httpx: 0.28.1 (latest on PyPI)

## Architecture Patterns

### Recommended Project Structure
```
src/cadenza/api/
    __init__.py          # create_app() factory, FastAPI instance
    schemas.py           # All Pydantic request/response models
    errors.py            # Exception classes, error codes, exception handlers
    parsing.py           # String-to-core-type parsing (pitch, interval, etc.)
    routes/
        __init__.py
        health.py        # GET /v1/health
        transforms.py    # POST /v1/transform/{operation}
        theory.py        # POST /v1/theory/*
tests/api/
    __init__.py
    conftest.py          # TestClient fixture
    test_health.py
    test_transforms.py
    test_theory.py
    test_errors.py
```

### Pattern 1: Thin Route Handler
**What:** Each endpoint is a 3-5 line function: validate input via Pydantic, call library function, build response.
**When to use:** Every endpoint in this phase.
**Example:**
```python
from fastapi import APIRouter
from cadenza.cn import parse_cn, to_cn
from cadenza.core.json_codec import _to_serializable
from cadenza.transforms import chromatic_transpose
from cadenza.api.schemas import TransposeRequest, PhraseResponse
from cadenza.api.parsing import parse_interval_string

router = APIRouter(prefix="/v1/transform", tags=["transforms"])

@router.post("/chromatic-transpose", response_model=PhraseResponse)
def chromatic_transpose_endpoint(req: TransposeRequest) -> dict:
    phrase, _warnings = parse_cn(req.phrase)
    interval = parse_interval_string(req.interval)
    result = chromatic_transpose(phrase, interval)
    return {"phrase": to_cn(result), "events": _to_serializable(result)}
```

### Pattern 2: Compact String Parsing at the API Boundary
**What:** Parse pitch strings like `"eb4"`, interval strings like `"m3"`, scale names like `"dorian"` into core types at the Pydantic validation layer or in a dedicated parsing module.
**When to use:** Every endpoint that accepts musical parameters beyond CN phrases.
**Key insight:** The core `Pitch` and `Interval` classes have NO `from_string()` methods. The CN parser handles full phrases, but not standalone pitch/interval tokens. The API layer must implement this.
**Example:**
```python
import re
from cadenza.core.pitch import Pitch

_PITCH_RE = re.compile(r"^([a-g])(ss|bb|s|b|n)?(\d+)$")

def parse_pitch_string(s: str) -> Pitch:
    """Parse compact pitch string 'eb4' -> Pitch(step='e', accidental='b', octave=4)."""
    m = _PITCH_RE.match(s.lower())
    if not m:
        raise ValueError(f"Invalid pitch string: {s!r}")
    step, acc, octave = m.group(1), m.group(2) or "n", int(m.group(3))
    return Pitch(step=step, accidental=acc, octave=octave)

_INTERVAL_RE = re.compile(r"^([PMmAd]|AA|dd)(\d+)$")

def parse_interval_string(s: str) -> Interval:
    """Parse compact interval string 'P5' -> Interval(quality='P', number=5, direction=1).
    Also accept shorthand: 'm3' for minor 3rd, 'M3' for major 3rd.
    """
    m = _INTERVAL_RE.match(s)
    if not m:
        raise ValueError(f"Invalid interval string: {s!r}")
    quality, number = m.group(1), int(m.group(2))
    return Interval(quality=quality, number=number, direction=1)
```

### Pattern 3: Exception Handler Chain
**What:** Map library exceptions to structured API error responses using FastAPI exception handlers.
**When to use:** Global error handling.
**Example:**
```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from cadenza.cn.errors import ParseError

class CadenzaAPIError(Exception):
    def __init__(self, error_code: str, message: str, input_value: str = ""):
        self.error_code = error_code
        self.message = message
        self.input_value = input_value

async def cadenza_error_handler(request: Request, exc: CadenzaAPIError) -> JSONResponse:
    body = {"error": exc.error_code, "message": exc.message}
    if exc.input_value:
        body["input"] = exc.input_value
    return JSONResponse(status_code=422, content=body)

async def parse_error_handler(request: Request, exc: ParseError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"error": "INVALID_CN", "message": str(exc)},
    )
```

### Pattern 4: APIRouter Per Domain
**What:** Separate `APIRouter` instances for transforms, theory, and health, included in the main app.
**When to use:** Standard FastAPI organization.
**Example:**
```python
# src/cadenza/api/__init__.py
from fastapi import FastAPI
from cadenza.api.routes.health import router as health_router
from cadenza.api.routes.transforms import router as transforms_router
from cadenza.api.routes.theory import router as theory_router

def create_app() -> FastAPI:
    app = FastAPI(title="Cadenza API", version="1")
    app.include_router(health_router)
    app.include_router(transforms_router)
    app.include_router(theory_router)
    # Register exception handlers
    ...
    return app

app = create_app()
```

### Anti-Patterns to Avoid
- **Business logic in route handlers:** Route handlers should ONLY parse, call, and serialize. No music theory logic.
- **Pydantic models wrapping core types:** Don't make Pydantic versions of `Pitch`, `Note`, etc. Core types stay frozen dataclasses. Pydantic only lives at the HTTP boundary.
- **Manual JSON serialization:** Use `_to_serializable()` from `json_codec` for the `events` field. Don't build a parallel serialization system.
- **Catching broad exceptions:** Catch specific exceptions (`ParseError`, `ValueError`, `KeyError`) and map to specific error codes. Never swallow `Exception`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| OpenAPI docs | Custom documentation | FastAPI auto-generated `/docs` | FastAPI generates from Pydantic models automatically |
| Request validation | Manual if/else checking | Pydantic model validators | Type-safe, auto-generates OpenAPI schema |
| JSON serialization | Custom JSON encoder for API | `_to_serializable()` from `json_codec` | Already handles all core types correctly |
| Test HTTP client | `urllib` or `requests` | `fastapi.testclient.TestClient` (backed by httpx) | Synchronous, in-process, no server needed |
| CORS/middleware | Custom headers | FastAPI `CORSMiddleware` (only if needed later) | Standard; not needed for localhost v1 |

**Key insight:** The entire API layer is glue code. The music logic exists in Phases 1-3. Phase 4's job is to expose it correctly via HTTP, not to re-implement anything.

## Common Pitfalls

### Pitfall 1: Fraction Serialization in Events
**What goes wrong:** `json.dumps` cannot serialize `fractions.Fraction`. If you pass raw core objects to a JSON response, you get `TypeError`.
**Why it happens:** Core types use `Fraction` internally for exact arithmetic.
**How to avoid:** Always use `_to_serializable()` from `json_codec` to convert events before putting them in responses. This recursively converts `Fraction` to `{"_type": "Fraction", "numerator": N, "denominator": D}`.
**Warning signs:** `TypeError: Object of type Fraction is not JSON serializable`

### Pitfall 2: Tuple vs List in Responses
**What goes wrong:** Core library uses `tuple[Event, ...]` for phrases. FastAPI/Pydantic may try to validate these as lists.
**Why it happens:** Pydantic v2 distinguishes between `tuple` and `list` types strictly.
**How to avoid:** The response models should accept the serialized form (which is already dicts/lists from `_to_serializable()`), not the raw core types. Route handlers convert via `_to_serializable()` before returning.
**Warning signs:** Pydantic validation errors about tuple vs list types.

### Pitfall 3: Missing String Parsers for Pitch/Interval
**What goes wrong:** Attempting to pass `"eb4"` to `Pitch()` constructor directly fails -- it expects `step`, `accidental`, `octave` separately.
**Why it happens:** Core types are intentionally low-level frozen dataclasses, not string-parsing types.
**How to avoid:** Build `parse_pitch_string()` and `parse_interval_string()` utilities in `cadenza.api.parsing`. Use them in Pydantic validators or route handlers.
**Warning signs:** `TypeError: Pitch.__init__() got an unexpected keyword argument`

### Pitfall 4: kebab-case URLs vs snake_case Functions
**What goes wrong:** URL uses `chromatic-transpose` but Python function is `chromatic_transpose`.
**Why it happens:** REST conventions use kebab-case; Python uses snake_case.
**How to avoid:** Map explicitly in route decorators: `@router.post("/chromatic-transpose")` calling `chromatic_transpose()`.
**Warning signs:** 404 errors from URL mismatches.

### Pitfall 5: Functions with Callable Parameters Not API-Exposable
**What goes wrong:** `pitch_map(phrase, fn)`, `omit(phrase, predicate=...)`, `repeat(phrase, n, variation=...)` accept Python callables that cannot be serialized over HTTP.
**Why it happens:** These are designed for Python-level composition, not HTTP.
**How to avoid:** Either (a) expose a simplified version (e.g., `omit` with `n` only, no predicate), or (b) skip these endpoints entirely with a `NOT_IMPLEMENTED` stub, or (c) define a small DSL for common operations. The CONTEXT.md lists `pitch-map` in the URL hierarchy, so provide a stub or limited version.
**Warning signs:** Trying to accept a Python function in a JSON request body.

### Pitfall 6: `_to_serializable` Returns Nested Dicts, Not Pydantic Models
**What goes wrong:** Trying to use `response_model=PhraseResponse` with strict Pydantic validation on the events list, when events are already plain dicts.
**Why it happens:** `_to_serializable()` produces dicts with `_type` discriminators, not typed Pydantic models.
**How to avoid:** Use `response_model=None` or define loose Pydantic models (with `dict[str, Any]` for events items), or return `JSONResponse` directly.
**Warning signs:** Pydantic validation errors on the response side.

## Code Examples

### TestClient Setup
```python
# tests/api/conftest.py
import pytest
from fastapi.testclient import TestClient
from cadenza.api import create_app

@pytest.fixture
def client() -> TestClient:
    app = create_app()
    return TestClient(app)
```

### Health Endpoint Test
```python
def test_health(client: TestClient) -> None:
    resp = client.get("/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["version"] == "1"
    assert "cadenza_version" in data
```

### Transform Endpoint Test
```python
def test_chromatic_transpose(client: TestClient) -> None:
    resp = client.post("/v1/transform/chromatic-transpose", json={
        "phrase": "e c4 q d4 e4",
        "interval": "m3",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "phrase" in data
    assert "events" in data
    assert isinstance(data["events"], dict)  # _to_serializable tuple wrapper
```

### Error Response Test
```python
def test_invalid_cn_returns_422(client: TestClient) -> None:
    resp = client.post("/v1/transform/chromatic-transpose", json={
        "phrase": "invalid garbage",
        "interval": "m3",
    })
    assert resp.status_code == 422
    data = resp.json()
    assert data["error"] == "INVALID_CN"
    assert "message" in data
```

### Pydantic Schema Example
```python
from pydantic import BaseModel, Field

class TransposeRequest(BaseModel):
    phrase: str = Field(..., description="CN notation string, e.g. 'e c4 q d4 e4'")
    interval: str = Field(..., description="Interval string, e.g. 'm3', 'P5', 'A4'")

class PhraseResponse(BaseModel):
    phrase: str = Field(..., description="Result as CN notation string")
    events: list | dict = Field(..., description="Result as JSON event list")

class MultiPhraseResponse(BaseModel):
    phrases: list[PhraseResponse]

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error code, e.g. 'INVALID_CN'")
    message: str = Field(..., description="Human-readable error description")
    input: str | None = Field(None, description="The invalid input value, if applicable")

class HealthResponse(BaseModel):
    status: str
    version: str
    cadenza_version: str
```

### Endpoint-to-Function Mapping (Complete)
```python
# Transforms: POST /v1/transform/{operation}
TRANSFORM_MAP = {
    # Pitch transforms
    "chromatic-transpose": (chromatic_transpose, ["phrase", "interval"]),
    "diatonic-transpose":  (diatonic_transpose, ["phrase", "n", "scale_name?"]),
    "invert":              (invert, ["phrase", "axis?"]),
    "pitch-retrograde":    (pitch_retrograde, ["phrase"]),
    "full-retrograde":     (full_retrograde, ["phrase"]),
    # Rhythm transforms
    "augment":             (augment, ["phrase", "ratio"]),
    "diminish":            (diminish, ["phrase", "ratio"]),
    "rhythmic-rotation":   (rhythmic_rotation, ["phrase", "n"]),
    "metric-modulation":   (metric_modulation, ["phrase", "old_unit", "new_unit"]),
    "quantize":            (quantize, ["phrase", "grid"]),
    "extract-rhythm":      (extract_rhythm, ["phrase"]),
    "total-duration":      (total_duration, ["phrase"]),
    # Melodic transforms
    "rotate":              (rotate, ["phrase", "n"]),
    "permute":             (permute, ["phrase", "indices"]),
    "interpolate":         (interpolate, ["phrase", "steps?"]),
    "omit":                (omit, ["phrase", "n"]),  # predicate not HTTP-exposable
    "mirror":              (mirror, ["phrase"]),
    "fragment":            (fragment, ["phrase", "lengths"]),
    "concatenate":         (concatenate, ["phrases"]),  # multi-phrase input
    "interleave":          (interleave, ["phrase", "phrase2"]),
    "pitch-map":           (pitch_map, ...),  # needs special handling or NOT_IMPLEMENTED
    "swing":               (...),  # listed in CONTEXT but not in transforms -- check
}

# Theory: POST /v1/theory/{operation}
# scale        -> get_scale(root, name)
# chord        -> get_chord(root, symbol, inversion?)
# diatonic-chords -> diatonic_chords(scale_root, scale_name, quality?)
# secondary-dominant -> secondary_dominant(degree, key_root, key_name)
# aug6         -> aug6_chord(aug6_type, key_root, key_name)
# neapolitan   -> neapolitan_chord(key_root, key_name)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| FastAPI < 0.100 used `requests` for TestClient | FastAPI >= 0.100 uses `httpx` for TestClient | 2023 | Must add `httpx` to dev deps |
| Pydantic v1 `class Config` | Pydantic v2 `model_config = ConfigDict(...)` | 2023 | Use v2 syntax only |
| `@app.on_event("startup")` | `lifespan` context manager | FastAPI 0.95+ | Use lifespan if startup logic needed (not needed here) |
| `response_model` with strict validation | `response_model=None` + return dicts | Current best practice for flexible responses | Avoid response-side validation issues with complex types |

**Deprecated/outdated:**
- Pydantic v1 syntax (`class Config`, `@validator`): Use `model_config`, `@field_validator` instead
- `TestClient` from `starlette.testclient`: Import from `fastapi.testclient` (same thing, clearer import)
- `@app.on_event`: Use `lifespan` parameter if needed

## Open Questions

1. **`pitch-map` endpoint**
   - What we know: `pitch_map(phrase, fn)` requires a Python callable. Cannot serialize over HTTP.
   - What's unclear: Should this be a `NOT_IMPLEMENTED` stub, or should we define a limited version (e.g., "transpose all pitches by interval")?
   - Recommendation: Skip or stub with `NOT_IMPLEMENTED`. The `chromatic-transpose` and `invert` endpoints already cover the most common pitch mapping use cases.

2. **`swing` endpoint**
   - What we know: Listed in CONTEXT.md URL hierarchy, but no `swing` function exists in `cadenza.transforms`.
   - What's unclear: Was this planned but not implemented in Phase 2?
   - Recommendation: Stub with `NOT_IMPLEMENTED` error code. It can be implemented when the underlying function is added.

3. **`repeat` endpoint**
   - What we know: `repeat(phrase, n, variation=None)` -- `variation` is a callable, not HTTP-exposable.
   - What's unclear: Is `repeat` with just `n` (no variation) useful enough for an endpoint?
   - Recommendation: Expose with `n` only. Simple repetition is a valid use case.

4. **CN phrase format: with or without parentheses?**
   - What we know: CN example in CONTEXT.md uses `"(e c4 q d4 e4)"` with parens. Need to verify if `parse_cn()` accepts both with and without parens.
   - Recommendation: Test and document. If parens are required, document in OpenAPI schema. If optional, accept both.

5. **Theory endpoints return Pitch tuples, not Phrases**
   - What we know: `get_chord()` and `get_scale()` return `tuple[Pitch, ...]` and `Scale` objects, not `Phrase` objects. These can't be serialized with `to_cn()` directly.
   - Recommendation: Theory endpoints return pitch lists as CN-compatible strings (e.g., `"c4 e4 g4"`) plus individual pitch objects in a JSON list. Use a different response schema for theory endpoints.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest >= 8.0 |
| Config file | `pyproject.toml` [tool.pytest.ini_options] |
| Quick run command | `python -m pytest tests/api/ -x -q` |
| Full suite command | `python -m pytest tests/ -v --tb=short` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| API-01 | All transform/theory endpoints accessible | integration | `python -m pytest tests/api/test_transforms.py tests/api/test_theory.py -x` | Wave 0 |
| API-02 | Endpoints accept CN strings as input | integration | `python -m pytest tests/api/test_transforms.py -k "cn_input" -x` | Wave 0 |
| API-03 | Responses contain both CN string and JSON events | integration | `python -m pytest tests/api/test_transforms.py -k "response_format" -x` | Wave 0 |
| API-04 | All endpoints under /v1/ prefix | integration | `python -m pytest tests/api/test_health.py tests/api/test_transforms.py -k "v1" -x` | Wave 0 |
| API-05 | OpenAPI docs auto-generated accurately | integration | `python -m pytest tests/api/test_openapi.py -x` | Wave 0 |
| API-07 | Structured error responses with domain error codes | integration | `python -m pytest tests/api/test_errors.py -x` | Wave 0 |
| API-08 | Health check returns 200 with correct body | integration | `python -m pytest tests/api/test_health.py -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/api/ -x -q`
- **Per wave merge:** `python -m pytest tests/ -v --tb=short`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/api/__init__.py` -- test package init
- [ ] `tests/api/conftest.py` -- TestClient fixture
- [ ] `tests/api/test_health.py` -- covers API-08
- [ ] `tests/api/test_transforms.py` -- covers API-01, API-02, API-03, API-04
- [ ] `tests/api/test_theory.py` -- covers API-01, API-02, API-03, API-04
- [ ] `tests/api/test_errors.py` -- covers API-07
- [ ] `tests/api/test_openapi.py` -- covers API-05
- [ ] Framework: `httpx>=0.27` added to dev deps in `pyproject.toml`

## Sources

### Primary (HIGH confidence)
- Codebase inspection: `src/cadenza/transforms/__init__.py`, `src/cadenza/theory/__init__.py`, `src/cadenza/core/json_codec.py`, `src/cadenza/cn/__init__.py`
- Codebase inspection: `src/cadenza/core/pitch.py`, `src/cadenza/core/interval.py` -- confirmed NO `from_string()` methods
- PyPI version check (2026-03-19): fastapi 0.135.1, uvicorn 0.42.0, pydantic 2.12.5, httpx 0.28.1

### Secondary (MEDIUM confidence)
- FastAPI documentation patterns (TestClient, APIRouter, exception handlers) -- from training data, verified against current PyPI versions
- Pydantic v2 patterns (field_validator, ConfigDict) -- verified as current API

### Tertiary (LOW confidence)
- `swing` endpoint status: listed in CONTEXT.md URL hierarchy but no underlying function found in transforms module. Needs validation during implementation.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- versions verified on PyPI, FastAPI/Pydantic are well-established
- Architecture: HIGH -- standard FastAPI patterns, verified against existing codebase structure
- Pitfalls: HIGH -- identified from direct codebase inspection (Fraction serialization, missing parsers)
- Endpoint mapping: MEDIUM -- some endpoints (pitch-map, swing) have unresolved questions about underlying function availability

**Research date:** 2026-03-19
**Valid until:** 2026-04-19 (stable domain, mature libraries)
