# Phase 4: REST API v1 - Context

**Gathered:** 2026-03-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Expose all Phase 1–3 functionality (transforms, scale library, chord library) as HTTP endpoints using FastAPI. CN (Cadenza Notation) strings are the primary wire format for both input and output. No new music-theory logic is added here — this phase is purely the HTTP layer on top of existing `cadenza.core`, `cadenza.transforms`, and `cadenza.theory` modules. Phase 4 covers API-01, API-02, API-03, API-04, API-05, API-07, API-08. Async jobs (API-06) and batch endpoint (API-09) are deferred to Phase 13.

</domain>

<decisions>
## Implementation Decisions

### Request Envelope
- **Input field name:** `"phrase"` — the musical concept, not the format name
- **CN strings only in v1:** All phrase inputs are CN strings. JSON event lists are output-only. No dual-format input in v1.
- **Musical parameter encoding:** Compact CN strings for musical params — interval as `"m3"`, pitch as `"eb4"`, scale name as `"dorian"`. NOT structured JSON objects. Keeps requests readable and consistent.

Example request:
```json
POST /v1/transform/chromatic-transpose
{
  "phrase": "(e c4 q d4 e4)",
  "interval": "m3"
}
```

### Response Envelope
- **Single-phrase responses:** Flat `phrase` + `events` — no wrapper object.
  ```json
  { "phrase": "(e eb4 q f4 g4)", "events": [...] }
  ```
- **Multi-phrase responses** (e.g., `diatonic-chords`, `fragment`): `"phrases"` array where each element has both `phrase` and `events`.
  ```json
  { "phrases": [ {"phrase": "...", "events": [...]}, ... ] }
  ```
- **`events` format:** Uses the existing `cadenza.core.json_codec` output format exactly. No custom serialization.

### Endpoint Organization
- **One endpoint per function** — each function is its own URL. Explicit, self-documenting, Dorico scripts call by name.
- **URL hierarchy:**
  - `GET /v1/health` — health check
  - `POST /v1/transform/{operation}` — all pitch, rhythm, melodic transforms (use kebab-case: `chromatic-transpose`, `pitch-retrograde`, `full-retrograde`, `augment`, `diminish`, `rotate`, `invert`, `interpolate`, `omit`, `mirror`, `fragment`, `concatenate`, `interleave`, `permute`, `pitch-map`, `rhythmic-rotation`, `metric-modulation`, `quantize`, `swing`, `total-duration`, `extract-rhythm`)
  - `POST /v1/theory/scale` — scale lookup
  - `POST /v1/theory/chord` — chord lookup
  - `POST /v1/theory/diatonic-chords` — diatonic chord generation
  - `POST /v1/theory/secondary-dominant` — secondary dominant
  - `POST /v1/theory/aug6` — augmented sixth chord
  - `POST /v1/theory/neapolitan` — Neapolitan chord
- **URL naming:** kebab-case for multi-word operations (`chromatic-transpose` not `chromatic_transpose`)

### Error Response Contract
- **HTTP status for domain errors:** `422 Unprocessable Entity` — semantic validation failures (invalid pitch, bad CN string). `400` for malformed JSON. `500` for unexpected server errors.
- **Error body shape:**
  ```json
  { "error": "INVALID_PITCH", "message": "'xb4' is not a valid pitch — step must be a-g", "input": "xb4" }
  ```
- **Music-theory-aware error codes (API-07):**
  - `INVALID_CN` — CN string couldn't be parsed at all
  - `INVALID_PITCH` — pitch token malformed (e.g., `'xb4'`)
  - `INVALID_INTERVAL` — interval string malformed (e.g., `'x3'`)
  - `INVALID_SCALE_NAME` — unknown scale name in registry
  - `INVALID_CHORD_SYMBOL` — unknown chord symbol in registry
  - `TRANSPOSE_OUT_OF_RANGE` — transposition result outside MIDI range (0–127)
  - `NOT_IMPLEMENTED` — stub endpoint (e.g., diatonic transpose until Phase 3 was unlocked)

### Deployment Model
- **Localhost-only by default:** Server binds to `127.0.0.1:8000`. Dorico scripts call `http://localhost:8000`. No auth needed for localhost.
- **Network override:** `--host 0.0.0.0` flag available for users who need network access (e.g., Sibelius on a different machine).
- **Health endpoint response:**
  ```json
  { "status": "ok", "version": "1", "cadenza_version": "0.1.0" }
  ```

### FastAPI & Pydantic
- FastAPI is the first runtime dependency added outside stdlib — added to `pyproject.toml` as a proper dep (not dev-only)
- Pydantic v2 models for all request/response schemas — lives in `cadenza.api.schemas` module
- Core library (`cadenza.core`, `cadenza.transforms`, `cadenza.theory`) remains zero-runtime-dep
- The `cadenza.cn` module (CN parser/serializer) is imported by the API layer, not Pydantic-ified internally

### Module Layout
- `src/cadenza/api/__init__.py` — FastAPI app instance
- `src/cadenza/api/routes/transforms.py` — all transform endpoints
- `src/cadenza/api/routes/theory.py` — all theory endpoints
- `src/cadenza/api/routes/health.py` — health check
- `src/cadenza/api/schemas.py` — Pydantic request/response models
- `src/cadenza/api/errors.py` — exception handlers and error code constants

### Claude's Discretion
- Exact Pydantic model field validators (how interval strings are parsed in schemas)
- OpenAPI tags and description strings
- Whether to use FastAPI `APIRouter` per route file (yes — standard pattern)
- `uvicorn` as the ASGI server (standard FastAPI choice)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing library modules (what the API wraps)
- `src/cadenza/transforms/__init__.py` — all transform functions exported (what becomes endpoints)
- `src/cadenza/theory/__init__.py` — all theory functions exported (what becomes endpoints)
- `src/cadenza/core/json_codec.py` — the `events` field format in responses uses this codec exactly
- `src/cadenza/cn/` — CN parser/serializer (note: module is `cadenza.cn`, not `cadenza.omn`)

### Requirements
- `.planning/REQUIREMENTS.md` — API-01, API-02, API-03, API-04, API-05, API-07, API-08

### Project context
- `.planning/PROJECT.md` — Dorico/Sibelius integration context; REST API as primary integration mechanism
- `.planning/phases/01-foundation/01-CONTEXT.md` — CN notation spec, pitch conventions (C4=middle C)
- `.planning/phases/02-transforms/02-CONTEXT.md` — all transform function signatures
- `.planning/phases/03-theory-libraries/03-CONTEXT.md` — all theory function signatures

No external specs — FastAPI/Pydantic docs are the reference for API structure.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `cadenza.transforms` — 32 public functions already implemented; the API is a thin HTTP wrapper over these
- `cadenza.theory.scales` — `get_scale`, `scale_degree`, `scales_for_pitches`, `relative_key`, `parallel_key`
- `cadenza.theory.chords` — `get_chord`, `diatonic_chords`, `secondary_dominant`, `aug6_chord`, `neapolitan_chord`, `register_chord`
- `cadenza.core.json_codec` — lossless JSON serialization already handles the `events` field format
- `cadenza.cn` — CN parser/serializer for the `phrase` input field (note: must rename from `cadenza.omn`)

### Established Patterns
- **Pure functions:** All library code is module-level functions — API endpoints are thin wrappers calling these directly, no business logic in the route handlers
- **Frozen dataclasses:** Core types are immutable — no mutation concerns in request handling
- **TDD:** Tests written first (RED → GREEN)

### Integration Points
- **Phase 13 (API Completion)** will add async jobs (API-06) and batch endpoints (API-09) — the route structure should make adding new routers easy
- **Dorico integration:** Dorico Python scripts will POST to `http://localhost:8000/v1/...` — the API must start fast and handle one request at a time reliably
- **Sibelius integration:** HTTP from a potentially different host — the `--host` flag enables this

### Known Rename Required
- `cadenza.omn` must be renamed to `cadenza.cn` before or during this phase — the API imports the CN parser and the module name must match the brand

</code_context>

<specifics>
## Specific Ideas

- Dorico scripts are the primary consumer: they will call `http://localhost:8000/v1/transform/chromatic-transpose` with a CN string and get back a CN string they can parse back into Dorico notation
- The `GET /v1/health` endpoint is specifically for DAW integration probing — Dorico scripts should be able to call this on startup to confirm the server is running before making transform calls
- The OpenAPI docs at `/docs` should be immediately useful to Dorico/Sibelius developers — every endpoint should have a meaningful description and example

</specifics>

<deferred>
## Deferred Ideas

- Async jobs (API-06) — deferred to Phase 13 (API Completion)
- Batch endpoint applying multiple operations in one request (API-09) — deferred to Phase 13
- API key authentication for network deployment — deferred; not needed for localhost v1
- WebSocket support for streaming results — deferred; not discussed

</deferred>

---

*Phase: 04-rest-api-v1*
*Context gathered: 2026-03-19*
