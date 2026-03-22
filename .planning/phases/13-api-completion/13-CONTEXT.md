# Phase 13: API Completion - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 13 adds full HTTP coverage for all phases since Phase 4: new route modules for analysis, voice leading, counterpoint, set theory, patterns, batch operations, algorithmic composition, and I/O (8 modules, ~40 endpoints). It also implements the async job pattern (API-06) for counterpoint generation and a batch endpoint (API-09) accepting multiple operations in one request.

No new music-theory logic — this is purely the HTTP layer on top of existing modules.

</domain>

<decisions>
## Implementation Decisions

### Route Coverage — New Route Modules

Full coverage: add routes for all 8 modules that have been added since Phase 4.

**New route files to create:**
- `src/cadenza/api/routes/analysis.py` — harmonic analysis, key detection, voice leading, phrase analysis (`identify_chord`, `detect_key`, `roman_numeral`, `detect_modulations`, `harmonic_rhythm`, `realize_chord`, `check_voice_leading`, `generate_inner_voices`, `smooth_voice_leading`, `find_motifs`, `phrase_similarity`, `detect_sequence`, `melodic_contour`, `ambitus`, `complexity_score`, `rhythmic_density`, `pitch_class_histogram`, `interval_sequence`)
- `src/cadenza/api/routes/batch_ops.py` — batch note manipulation (`set_articulation_nth`, `set_dynamic_nth`, `crescendo`, `decrescendo`, `add_articulation_if`, `remove_articulation_if`, `replace_pitch`, `filter_phrase`, `quantize_lengths`, `humanize`, `apply_windowed`)
- `src/cadenza/api/routes/counterpoint.py` — all counterpoint generators (`generate_first_species` through `generate_fifth_species`, `generate_free_counterpoint`, `generate_multi_voice_counterpoint`, `check_counterpoint`). These have async variants (see below).
- `src/cadenza/api/routes/settheory.py` — pitch class set analysis and serial operations (`prime_form`, `interval_vector`, `forte_number`, `lookup_by_forte`, `complement`, `invert_pcs`, `transpose_pcs`, `is_subset`, `is_superset`, `is_z_related`, `rp_relation`, `r0`/`r1`/`r2`, `ToneRow` construction, `realize_row`, `segment_row`, `derive_row`, `is_all_interval`, `is_combinatorial`)
- `src/cadenza/api/routes/patterns.py` — pattern generation (`euclidean_rhythm`, `binary_rhythm`, `apply_rhythm`, `isorhythm`, `ostinato`, `accent_pattern`, `rhythmic_canon`, `hocket`)
- `src/cadenza/api/routes/composition.py` — algorithmic composition (`train_markov` + `markov_melody`, `lsystem_melody`, `probabilistic_melody`, `tendency_mask_melody`, `random_walk`, `generate_variations`)
- `src/cadenza/api/routes/io.py` — file import/export (see I/O section below)

**URL hierarchy for new routes** (following established `/v1/{module}/{operation}` pattern):
- `POST /v1/analysis/{operation}`
- `POST /v1/batch-ops/{operation}`
- `POST /v1/counterpoint/{operation}` (sync), `POST /v1/counterpoint/{operation}/async` (async job)
- `POST /v1/settheory/{operation}`
- `POST /v1/patterns/{operation}`
- `POST /v1/composition/{operation}`
- `POST /v1/io/import-musicxml`, `POST /v1/io/export-musicxml`, `POST /v1/io/import-midi`, `POST /v1/io/export-midi`

### Score Response Format

Operations that return `Score` (counterpoint generators, `rhythmic_canon`, `hocket`, `generate_multi_voice_counterpoint`) use a named voices array:

```json
{
  "voices": [
    {"name": "voice_0", "phrase": "(e c4 q d4)", "events": [...]},
    {"name": "voice_1", "phrase": "(q e4 h f4)", "events": [...]}
  ]
}
```

New `ScoreResponse` Pydantic model: `{"voices": list[VoiceResponse]}` where `VoiceResponse` has `name`, `phrase`, `events`.

### I/O Endpoints — File Upload/Download

- **Import:** `POST /v1/io/import-musicxml` and `POST /v1/io/import-midi` accept `multipart/form-data` file upload. Response is the standard `PhraseResponse` or `ScoreResponse` plus a `warnings` list.
- **Export:** `POST /v1/io/export-musicxml` and `POST /v1/io/export-midi` accept `{"phrase": "..."}` (or score equivalent) and return the file as `application/octet-stream` (or `application/xml` for MusicXML). Filename set via `Content-Disposition`.
- MIDI import accepts optional `grid` and `prefer_sharps` params in the form data.
- MIDI export accepts optional `tempo` param.

### Stochastic API — Seed Exposure

All stochastic composition endpoints (`markov_melody`, `probabilistic_melody`, `tendency_mask_melody`, `random_walk`) expose an optional `seed: int | None = null` field in the request schema. `null` = system randomness; integer = reproducible output.

`train_markov` + `markov_melody` follow the existing Python pattern: caller POSTs a phrase to train (gets back a MarkovModel JSON object), then POSTs the model + length + seed to generate. Alternatively, provide a single `POST /v1/composition/markov-generate` that accepts a training phrase + length + seed (trains and generates in one call — simpler for Dorico scripts).

### Async Job Pattern (API-06)

**Which operations are async:** Counterpoint generation only (`generate_first_species` through `generate_multi_voice_counterpoint`). All other operations are synchronous.

**Async route pattern:** Counterpoint endpoints have two variants:
- `POST /v1/counterpoint/{operation}` — synchronous (blocks until done, fine for simple cantus firmi)
- `POST /v1/counterpoint/{operation}/async` — returns job ID immediately

**Job submission response:**
```json
{"job_id": "uuid4-string", "status": "pending"}
```

**Job storage:** In-memory dict keyed by UUID. No external dependencies. Jobs disappear on server restart (acceptable for localhost Dorico integration).

**Polling endpoint:** `GET /v1/jobs/{id}`

Response shape:
```json
{
  "status": "pending" | "running" | "done" | "failed",
  "result": { /* ScoreResponse when done */ } | null,
  "error": { "error": "...", "message": "..." } | null
}
```

**Job execution:** Counterpoint generation runs in a `threading.Thread` (not asyncio — pure CPU-bound Python). Thread updates job dict with result or error on completion.

**Job expiry:** TTL-based, lazy expiry. Jobs survive 5 minutes after reaching `done` or `failed`. First `GET /v1/jobs/{id}` after expiry returns `410 Gone`. Expiry checked on read (no background thread needed).

New job-related routes added to a `src/cadenza/api/routes/jobs.py` file.

### Batch Endpoint (API-09)

**Endpoint:** `POST /v1/batch`

**Request envelope:**
```json
{
  "operations": [
    {"operation": "chromatic-transpose", "params": {"phrase": "...", "interval": "m3"}},
    {"operation": "detect-key", "params": {"phrase": "..."}}
  ]
}
```

Operation name matches the existing endpoint slug (e.g., `"chromatic-transpose"` dispatches the same logic as `POST /v1/transform/chromatic-transpose`).

**Response:**
```json
{
  "results": [
    {"status": "ok", "result": {"phrase": "...", "events": [...]}},
    {"status": "error", "error": {"error": "INVALID_CN", "message": "..."}}
  ]
}
```

**Failure semantics:** Continue on error — all operations run regardless. Each result has its own `status`. HTTP response is always 200.

**Execution:** Sequential (operations run in order). Single-process, no threading needed.

**Cap:** Maximum 50 operations per batch request. Returns 422 `BATCH_TOO_LARGE` if exceeded.

**Dispatcher implementation:** A registry dict mapping operation slugs to handler functions. All existing route handlers are factored to a shared function the batch dispatcher can call directly (no internal HTTP requests).

### OpenAPI Polish

All new endpoints include:
- FastAPI `summary` and `description` strings
- OpenAPI tags matching the module (e.g., `tags=["analysis"]`)
- Inline `Field(description=...)` on every request/response field
- Example values on key fields where helpful

### Claude's Discretion

- Exact Pydantic model names for new request types
- Whether to use `APIRouter(prefix=...)` or manual prefix in route decorators
- Threading model details for async job execution (thread pool vs. new thread per job)
- Whether `markov_melody` gets a combined train+generate endpoint or separate endpoints

</decisions>

<canonical_refs>
## Canonical References

No external specs — requirements fully captured in decisions above.

### Phase requirements
- `.planning/REQUIREMENTS.md` — API-06, API-09

### Prior phase patterns to follow
- `src/cadenza/api/__init__.py` — app factory, router registration pattern
- `src/cadenza/api/routes/transforms.py` — established thin-handler pattern; `_parse_phrase`, `_phrase_response` helpers
- `src/cadenza/api/routes/theory.py` — established pattern for non-phrase responses (pitch tuples, chord data)
- `src/cadenza/api/schemas.py` — existing Pydantic models; `PhraseResponse`, `MultiPhraseResponse`, `ErrorResponse`
- `src/cadenza/api/errors.py` — exception handler pattern; error code constants
- `src/cadenza/analysis/__init__.py` — full public API of analysis module
- `src/cadenza/counterpoint/__init__.py` — counterpoint generators and checker
- `src/cadenza/settheory/__init__.py` — set theory and serial operations
- `src/cadenza/composition/__init__.py` — algorithmic composition functions
- `src/cadenza/patterns/__init__.py` — pattern generation functions
- `src/cadenza/batch/__init__.py` — batch note manipulation functions
- `src/cadenza/io/__init__.py` — I/O import/export functions
- `.planning/phases/04-rest-api-v1/04-CONTEXT.md` — all Phase 4 API decisions (error codes, URL structure, response shapes)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `_parse_phrase(cn_string)` in `transforms.py` — parse CN to phrase tuple; reusable in all new route handlers
- `_phrase_response(phrase)` in `transforms.py` — serialize phrase to `{"phrase": ..., "events": ...}`; reusable
- `cadenza.core.json_codec` — the `events` field format used in all responses
- `cadenza.api.errors.CadenzaAPIError` / `register_exception_handlers` — existing error infrastructure

### Established Patterns
- Thin route handlers: routes call the library function, call `_parse_phrase`, call `_phrase_response`, return dict
- `response_model=None` on all route decorators (lets FastAPI infer from return type)
- `APIRouter(prefix="/v1/{module}", tags=["{module}"])` per route file
- Three-layer exception: `CadenzaAPIError` → error code, `ParseError` → `INVALID_CN`, `ValueError` → `INVALID_INPUT`

### Integration Points
- `create_app()` in `cadenza/api/__init__.py` — add `include_router()` calls for all 7 new routers + jobs router + batch router
- Batch dispatcher needs access to all route handler functions — factor shared helpers out of existing route files if needed
- Async job execution uses `threading.Thread` targeting the existing synchronous counterpoint functions

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 13-api-completion*
*Context gathered: 2026-03-22*
