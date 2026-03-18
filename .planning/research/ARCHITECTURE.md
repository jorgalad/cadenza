# Architecture Patterns

**Domain:** Music theory analysis, transformation, and generation library
**Researched:** 2026-03-18

## Recommended Architecture

Cadenza is a **layered library with an optional API shell**. The core is a pure Python library with no framework dependencies. The API layer (FastAPI) is an optional wrapper.

```
+------------------------------------------------------------------+
|                        REST API (FastAPI)                          |
|  Endpoints: /transform, /analyze, /generate, /io/midi, /io/xml   |
+------------------------------------------------------------------+
|                     API Schema Layer (Pydantic)                    |
|  Request/Response models, OMN string <-> model conversion         |
+------------------------------------------------------------------+
|                                                                    |
|  +------------------+  +------------------+  +------------------+ |
|  | Transformations  |  | Analysis         |  | Generation       | |
|  | - retrograde     |  | - key detection  |  | - counterpoint   | |
|  | - inversion      |  | - chord ID       |  | - voice leading  | |
|  | - transposition  |  | - roman numerals |  | - Euclidean      | |
|  | - augmentation   |  | - interval vec   |  | - serial/12-tone | |
|  | - rotation       |  | - ambitus        |  | - isorhythm      | |
|  | - batch ops      |  | - contour        |  | - ostinato       | |
|  +------------------+  +------------------+  +------------------+ |
|                                                                    |
|  +--------------------------------------------------------------+ |
|  |              Core Music Theory Engine                         | |
|  |  Pitch | Interval | Scale | Key | Chord | Duration | Meter   | |
|  +--------------------------------------------------------------+ |
|                                                                    |
|  +------------------+  +------------------+  +------------------+ |
|  | OMN Parser       |  | MIDI I/O (mido)  |  | MusicXML (lxml)  | |
|  | (Lark grammar)   |  |                  |  |                  | |
|  +------------------+  +------------------+  +------------------+ |
|                                                                    |
|  +--------------------------------------------------------------+ |
|  |              Data Model (Pydantic frozen models)              | |
|  |  Pitch | Duration | Note | Rest | Chord | Phrase | Key | ... | |
|  +--------------------------------------------------------------+ |
+------------------------------------------------------------------+
```

### Component Boundaries

| Component | Responsibility | Communicates With | Dependencies |
|-----------|---------------|-------------------|--------------|
| `cadenza.core.model` | Data model definitions (Pitch, Note, etc.) | Everything imports this | pydantic only |
| `cadenza.core.pitch` | Pitch arithmetic, enharmonic logic, MIDI mapping | model | None (pure logic) |
| `cadenza.core.interval` | Interval computation, classification | model, pitch | None |
| `cadenza.core.scale` | Scale definitions, scale-degree operations | model, pitch, interval | None |
| `cadenza.core.key` | Key signatures, key relationships | model, scale | None |
| `cadenza.core.chord` | Chord construction, identification, voicing | model, pitch, interval | None |
| `cadenza.core.duration` | Duration arithmetic, tuplet handling | model | fractions (stdlib) |
| `cadenza.core.meter` | Time signatures, beat strength | model, duration | None |
| `cadenza.parser` | OMN parsing and serialization | model | lark |
| `cadenza.transforms` | All transformation functions | model, core.* | None |
| `cadenza.analysis` | All analysis functions | model, core.* | None |
| `cadenza.generation` | Counterpoint, pattern generation | model, core.*, analysis | None |
| `cadenza.io.midi` | MIDI read/write | model | mido |
| `cadenza.io.musicxml` | MusicXML read/write | model | lxml |
| `cadenza.api` | FastAPI application, routes, schemas | Everything above | fastapi, uvicorn |
| `cadenza.compat.music21` | Music21 object conversion | model | music21 (optional) |

### Data Flow

**Typical API request (transform a phrase):**

```
Client sends: POST /v1/transform/retrograde
  Body: {"omn": "(q c4 mp stacc) (e d4 mf) (q e4 f ten)"}

1. FastAPI deserializes JSON -> Pydantic request model
2. OMN parser converts string -> tuple[Note, Note, Note]
3. Transform function (retrograde) operates on tuple -> new tuple
4. OMN serializer converts result tuple -> OMN string
5. FastAPI serializes Pydantic response model -> JSON

Client receives:
  Body: {"omn": "(q e4 f ten) (e d4 mf) (q c4 mp stacc)",
         "events": [...]}  // Optional JSON representation
```

**Typical API request (analyze a phrase):**

```
Client sends: POST /v1/analyze/key
  Body: {"omn": "(q c4) (q e4) (q g4) (q c5) ..."}

1. Parse OMN -> Phrase
2. Analysis function extracts pitch classes, applies Krumhansl-Kessler
3. Returns ranked key candidates

Client receives:
  Body: {"results": [
    {"key": "C", "mode": "major", "confidence": 0.92},
    {"key": "A", "mode": "minor", "confidence": 0.78}
  ]}
```

**MusicXML round-trip:**

```
POST /v1/io/from-musicxml  (upload MusicXML file)
  -> Parse XML with lxml -> Cadenza Phrase model -> return OMN + JSON

POST /v1/io/to-musicxml    (provide OMN or JSON phrase)
  -> Build XML with lxml -> Return MusicXML file
```

## Patterns to Follow

### Pattern 1: Pure Functions on Immutable Data

**What:** Every transformation/analysis function takes immutable data in, returns new immutable data out. No side effects.

**When:** Always. This is the core design principle.

**Why:**
- Thread-safe by default (API handles concurrent requests without locks).
- Composable (chain transformations without worrying about state).
- Testable (input -> output, no setup/teardown).
- Matches the Lisp/functional heritage of OMN.

**Example:**
```python
def retrograde(phrase: Phrase) -> Phrase:
    """Reverse the order of events in a phrase."""
    return tuple(reversed(phrase))

def transpose(phrase: Phrase, interval: Interval) -> Phrase:
    """Transpose all pitches by the given interval."""
    return tuple(_transpose_event(event, interval) for event in phrase)

# Composition:
result = transpose(retrograde(phrase), Interval.minor_third())
```

### Pattern 2: Separate Parse/Serialize Boundary

**What:** OMN parsing and serialization happen ONLY at the API boundary. Internal functions work with typed data model objects, never with raw strings.

**When:** Always. No function deeper than the API layer should accept or return OMN strings.

**Why:**
- Type safety. A `Pitch` object is always valid; an OMN string might not be.
- Testability. Functions can be tested with constructed objects, no parsing needed.
- Performance. Parse once, operate many times.

**Example:**
```python
# GOOD: API layer parses, passes typed objects to transform
@router.post("/v1/transform/retrograde")
async def api_retrograde(request: OmnRequest) -> OmnResponse:
    phrase = parse_omn(request.omn)       # Parse at boundary
    result = retrograde(phrase)            # Typed operation
    return OmnResponse(omn=to_omn(result)) # Serialize at boundary

# BAD: Transform function accepts raw strings
def retrograde(omn_string: str) -> str:  # NO -- mixing concerns
    ...
```

### Pattern 3: Registry Pattern for Scales, Chords, Articulations

**What:** Use dictionaries/registries for extensible catalogues rather than hard-coding.

**When:** Any enumerable set of music theory entities that users might want to extend.

**Example:**
```python
SCALE_REGISTRY: dict[str, tuple[int, ...]] = {
    "major": (0, 2, 4, 5, 7, 9, 11),
    "natural_minor": (0, 2, 3, 5, 7, 8, 10),
    "harmonic_minor": (0, 2, 3, 5, 7, 8, 11),
    "dorian": (0, 2, 3, 5, 7, 9, 10),
    # ... 50+ scales
}

def get_scale(root: Pitch, scale_name: str) -> tuple[Pitch, ...]:
    intervals = SCALE_REGISTRY[scale_name]
    return tuple(transpose_pitch(root, i) for i in intervals)

def register_scale(name: str, intervals: tuple[int, ...]) -> None:
    SCALE_REGISTRY[name] = intervals
```

### Pattern 4: Context Objects for Key/Meter-Aware Operations

**What:** Operations that depend on musical context (key, meter, tempo) accept an explicit context parameter rather than global state.

**Example:**
```python
class MusicalContext(BaseModel):
    model_config = ConfigDict(frozen=True)
    key: Key
    time_signature: TimeSignature
    tempo: int = 120

def analyze_roman_numerals(
    phrase: Phrase,
    context: MusicalContext
) -> tuple[RomanNumeral, ...]:
    ...

# Context-aware transposition (preserves spelling in key)
def transpose_diatonic(
    phrase: Phrase,
    degrees: int,
    context: MusicalContext
) -> Phrase:
    ...
```

### Pattern 5: API Versioning from Day One

**What:** All API routes use `/v1/` prefix. Schema evolution uses Pydantic model versioning.

**Why:** Dorico/Sibelius integrations cannot be updated quickly. Breaking the API breaks the DAW bridge.

**Example:**
```python
app = FastAPI(title="Cadenza", version="1.0.0")
v1 = APIRouter(prefix="/v1")
v1.include_router(transform_router, prefix="/transform")
v1.include_router(analyze_router, prefix="/analyze")
v1.include_router(generate_router, prefix="/generate")
v1.include_router(io_router, prefix="/io")
app.include_router(v1)
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Mutable Shared State

**What:** Global mutable configuration, singleton music theory objects that accumulate state.
**Why bad:** Thread safety issues under concurrent API requests. Hard to test. Surprising behavior.
**Instead:** Pass context explicitly. Use frozen models. Return new objects.

### Anti-Pattern 2: God Object for Musical Events

**What:** A single `Event` class with dozens of optional fields for every possible attribute.
**Why bad:** Most fields are None most of the time. Validation becomes complex. Hard to pattern-match.
**Instead:** Separate `Note`, `Rest`, `Chord` types. Use union type: `MusicalEvent = Note | Rest | Chord`.

### Anti-Pattern 3: String-Based Music Theory

**What:** Representing pitches as strings ("C#4"), doing string manipulation for transposition.
**Why bad:** No validation, easy to create invalid states ("H#13"), hard to do arithmetic.
**Instead:** Typed Pitch objects with validated fields. Arithmetic operations on the model.

### Anti-Pattern 4: Over-Abstracting the I/O Layer

**What:** Building a generic "format adapter" framework before you need it.
**Why bad:** MusicXML, MIDI, and OMN are fundamentally different. Forcing them through one abstraction loses fidelity.
**Instead:** Dedicated reader/writer per format. Shared data model is the abstraction point.

### Anti-Pattern 5: API-Driven Library Design

**What:** Designing the core library around what FastAPI can serialize/deserialize rather than what music theory requires.
**Why bad:** The library should be usable without the API. API serialization is a presentation concern.
**Instead:** Design the core library for correctness. Add serialization adapters at the API boundary.

## Scalability Considerations

| Concern | Single User (dev) | Notation Plugin (1 user) | Server (100 concurrent) |
|---------|-------------------|--------------------------|------------------------|
| Latency | Not important | <200ms per operation | <200ms per operation |
| Throughput | N/A | 1 req/sec | 100 req/sec |
| Memory | N/A | <100MB | <500MB (no corpus in RAM) |
| State | None (pure functions) | None (stateless API) | None (stateless API) |
| Concurrency | N/A | Single-threaded OK | uvicorn workers, async I/O |

Cadenza's stateless, pure-function design means horizontal scaling is trivial: run more uvicorn workers. No shared state, no database, no session management.

**The bottleneck will be:** Complex generation operations (counterpoint, voice leading search) which are CPU-bound. For these:
- `asyncio` with `run_in_executor` for CPU-bound work
- Job queue pattern (POST starts job, GET polls for result) for operations > 5 seconds
- Caching of scale/chord lookups (pure functions of their inputs -- memoizable)

## Sources

- FastAPI architectural patterns (training data, well-established)
- Pydantic v2 frozen model patterns (training data)
- Functional programming patterns for music (academic literature)
- Opusmodus design philosophy (functional, immutable, composable)
