# Roadmap: Cadenza

## Overview

Cadenza delivers a comprehensive Python music analysis, transformation, and generation library in 13 phases. The critical path flows from the immutable data model and OMN parser (Phase 1), through pitch/rhythm/melodic transforms (Phase 2), theory libraries (Phase 3), and an early REST API (Phase 4), into harmonic analysis (Phase 5), batch/analysis operations (Phase 6), voice leading (Phase 7), counterpoint (Phase 8), set theory and serial techniques (Phase 9), pattern generation (Phase 10), algorithmic composition (Phase 11), I/O formats (Phase 12), and API completion (Phase 13). Each phase delivers a coherent, testable capability that builds on its predecessors.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Foundation** - Core data model (Pitch, Duration, Interval, Note, Rest, Phrase, Score) + OMN parser/serializer + project scaffolding (completed 2026-03-19)
- [x] **Phase 2: Transforms** - Pitch operations, rhythm operations, and melodic transforms on phrases (completed 2026-03-19)
- [x] **Phase 3: Theory Libraries** - Scale/mode library (80+ scales) and chord library (all standard types) (completed 2026-03-19)
- [x] **Phase 4: REST API v1** - FastAPI server wrapping all Phase 1-3 functionality with versioned endpoints (completed 2026-03-19)
- [x] **Phase 5: Harmonic Analysis** - Chord identification, key detection, Roman numeral analysis, functional harmony (completed 2026-03-19)
- [ ] **Phase 6: Batch Operations & Analysis** - Batch note manipulation and melodic/rhythmic analysis tools
- [x] **Phase 7: Voice Leading** - Voice leading rules, parallel detection, smooth voicing generation (completed 2026-03-20)
- [ ] **Phase 8: Counterpoint** - Species I-V generation and validation from cantus firmus
- [ ] **Phase 9: Set Theory & Serial** - Pitch class sets, Forte numbers, 12-tone rows and matrices
- [ ] **Phase 10: Pattern Generation** - Isorhythm, ostinato, hocket, Euclidean rhythms, rhythmic canons
- [ ] **Phase 11: Algorithmic Composition** - Markov chains, L-systems, tendency masks, variation generation
- [ ] **Phase 12: I/O Expansion** - MusicXML import/export and MIDI import/export
- [ ] **Phase 13: API Completion** - Async job pattern for expensive operations + batch endpoint + OpenAPI polish

## Phase Details

### Phase 1: Foundation
**Goal**: Users can represent any musical phrase as typed Python objects and convert losslessly between OMN notation strings and internal representation
**Depends on**: Nothing (first phase)
**Requirements**: CORE-01, CORE-02, CORE-03, CORE-04, CORE-05, CORE-06, CORE-07, CORE-08, CORE-09, CORE-10, NOTA-01, NOTA-02, NOTA-03, NOTA-04, NOTA-05, NOTA-06, NOTA-07, NOTA-12
**Success Criteria** (what must be TRUE):
  1. A Pitch object preserves spelling (Eb3 and D#3 are distinct objects that compare unequal, but enharmonic_equal() returns True)
  2. Duration arithmetic using Fraction never loses precision -- a measure of dotted-quarter + eighth + half sums to exactly Fraction(1, 1)
  3. An OMN string like `(e f3 pp stacc)` round-trips through parse then serialize and produces an identical string
  4. The parser rejects malformed input with a clear error message including the position of the problem
  5. All core types (Pitch, Duration, Note, Rest, Phrase, Score) are hashable, comparable, and JSON-serializable without information loss
**Plans**: 3 plans

Plans:
- [ ] 01-01-PLAN.md -- Project scaffolding + core data model (Pitch, Duration, Interval, Note, Rest, Phrase, Score, JSON codec)
- [ ] 01-02-PLAN.md -- OMN tokenizer, recursive descent parser with sticky state, and compact serializer
- [ ] 01-03-PLAN.md -- Integration tests, property-based round-trip tests, ROADMAP success criteria verification

### Phase 2: Transforms
**Goal**: Users can apply all standard melodic, rhythmic, and pitch transformations to phrases and receive musically correct results
**Depends on**: Phase 1
**Requirements**: PTCH-01, PTCH-02, PTCH-03, PTCH-04, PTCH-05, PTCH-06, PTCH-07, PTCH-08, PTCH-09, RHYT-01, RHYT-02, RHYT-03, RHYT-04, RHYT-05, RHYT-07, RHYT-08, RHYT-09, MELO-01, MELO-02, MELO-03, MELO-04, MELO-05, MELO-06, MELO-07, MELO-08, MELO-09, MELO-10, MELO-11, MELO-12
**Success Criteria** (what must be TRUE):
  1. Transposing a C major scale up by a minor third produces Eb major (not D# major) -- enharmonic spelling is preserved through transforms
  2. Retrograde of a phrase reverses pitch order while keeping the original rhythm sequence intact
  3. Rhythmic augmentation by 2x doubles every duration exactly (no floating-point drift)
  4. All melodic transforms (retrograde, inversion, rotation, permutation, interpolation, omission, mirror, fragmentation, concatenation, interleave) produce valid Phrases with correct Note/Rest types
  5. A user can chain transforms: transpose, then invert, then retrograde a phrase and get a correct compound result
**Plans**: 3 plans

Plans:
- [ ] 02-01-PLAN.md -- Pitch operations: chromatic transpose, invert, interval, enharmonic respell, MIDI/frequency conversion, scale stubs (PTCH-01..09)
- [ ] 02-02-PLAN.md -- Rhythm operations: retrograde, augmentation, diminution, rotation, metric modulation, extract, quantize, total duration (RHYT-01..05,07..09)
- [ ] 02-03-PLAN.md -- Melodic transforms: pitch retrograde, retrograde-inversion, full retrograde, rotation, permutation, interpolation, omission, repetition, mirror, fragmentation, concatenation, interleave, pitch map (MELO-01..12)

### Phase 3: Theory Libraries
**Goal**: Users can look up any standard scale or chord by name and root, and the library returns correctly spelled pitches
**Depends on**: Phase 1
**Requirements**: SCAL-01, SCAL-02, SCAL-03, SCAL-04, SCAL-05, SCAL-06, SCAL-07, SCAL-08, SCAL-09, SCAL-10, SCAL-11, SCAL-12, CHRD-01, CHRD-02, CHRD-03, CHRD-04, CHRD-05, CHRD-06, CHRD-07, CHRD-08, CHRD-09
**Success Criteria** (what must be TRUE):
  1. Requesting "D dorian" returns D, E, F, G, A, B, C with correct spelling (no enharmonic errors)
  2. All 7 church modes, pentatonic/blues scales, symmetric scales, bebop scales, and non-Western scales are available by name
  3. Given a root and chord type (e.g., "Cmaj7"), the library returns the correct pitches in any requested inversion
  4. Diatonic chords of any scale are generated correctly (e.g., C major yields C, Dm, Em, F, G, Am, Bdim for triads)
  5. A user can define a custom scale from an interval pattern and use it in all scale-aware operations
**Plans**: 2 plans

Plans:
- [ ] 03-01-PLAN.md -- Scale/mode registry, Scale type, all built-in scales, query functions, Phase 2 stub completion
- [ ] 03-02-PLAN.md -- Chord library, inversions, diatonic chords, secondary dominants, augmented sixths, Neapolitan

### Phase 4: REST API v1
**Goal**: All Phase 1-3 functionality is callable over HTTP with CN (Cadenza Notation) strings as the primary wire format
**Depends on**: Phases 1, 2, 3
**Requirements**: API-01, API-02, API-03, API-04, API-05, API-07, API-08
**Success Criteria** (what must be TRUE):
  1. A POST to `/v1/transform/chromatic-transpose` with a CN string and interval returns both a CN string and a JSON event list in the response
  2. All transform, scale, and chord endpoints are accessible under the `/v1/` prefix
  3. The `/v1/health` endpoint returns a 200 response suitable for DAW integration probing
  4. Invalid CN input returns a structured error response with a music-theory-aware error code (not a generic 500)
  5. Auto-generated OpenAPI/Swagger documentation accurately describes all available endpoints
**Plans**: 2 plans

Plans:
- [ ] 04-01-PLAN.md -- FastAPI app factory, Pydantic schemas, error handling, CN string parsing utilities, health endpoint, test infrastructure
- [ ] 04-02-PLAN.md -- All transform and theory route endpoints with dual CN+JSON responses, OpenAPI verification

### Phase 5: Harmonic Analysis
**Goal**: Users can submit a phrase or chord and receive correct harmonic analysis (chord name, Roman numerals, key, function)
**Depends on**: Phases 1, 3
**Requirements**: HARM-01, HARM-02, HARM-03, HARM-04, HARM-05, HARM-06, HARM-07, HARM-08, HARM-09, HARM-10
**Success Criteria** (what must be TRUE):
  1. Given simultaneous pitches C4-E4-G4-Bb4, the system identifies "C dominant 7th, root position"
  2. Given a phrase in C major, the system detects the key as C major using pitch class frequency analysis
  3. A chord progression I-IV-V-I in any key produces correct Roman numeral labels with functional harmony tags (tonic, subdominant, dominant)
  4. The system detects modulations -- a phrase that starts in C major and moves to G major is identified as such
  5. Chord symbols round-trip: "Cmaj7" parses to a chord object that serializes back to "Cmaj7"
**Plans**: 2 plans

Plans:
- [ ] 05-01-PLAN.md -- Chord identification engine, chord symbol parsing/generation, chord realization (HARM-01, HARM-07, HARM-08, HARM-09)
- [ ] 05-02-PLAN.md -- Key detection (K-S), Roman numeral analysis, functional harmony, modulation detection, borrowed chords (HARM-02, HARM-03, HARM-04, HARM-05, HARM-06, HARM-10)

### Phase 6: Batch Operations & Analysis
**Goal**: Users can apply bulk modifications to phrases and analyze melodic/rhythmic properties of any phrase
**Depends on**: Phases 1, 2
**Requirements**: BATCH-01, BATCH-02, BATCH-03, BATCH-04, BATCH-05, BATCH-06, BATCH-07, BATCH-08, BATCH-09, ANAL-01, ANAL-02, ANAL-03, ANAL-04, ANAL-05, ANAL-06, ANAL-07, ANAL-08, ANAL-09
**Success Criteria** (what must be TRUE):
  1. Setting staccato on every 3rd note of a 12-note phrase produces exactly 4 staccato notes at positions 3, 6, 9, 12
  2. Applying a crescendo from pp to ff across a phrase produces a smooth dynamic progression
  3. Ambitus analysis of a phrase returns the correct lowest and highest pitches
  4. Melodic contour analysis produces an accurate up/down/same direction sequence matching the intervals
  5. The system identifies repeated motifs within a phrase and reports their positions
**Plans**: 2 plans

Plans:
- [ ] 06-01-PLAN.md -- Batch operations: articulation/dynamic nth-note, crescendo/decrescendo, predicate-based articulation, pitch replacement, filtering, quantize, humanize, windowed transforms (BATCH-01..09)
- [ ] 06-02-PLAN.md -- Analysis tools: ambitus, contour, interval sequence, histogram, density, complexity, motif detection, similarity, sequence detection (ANAL-01..09)

### Phase 7: Voice Leading
**Goal**: Users can check any multi-voice passage for voice leading violations and generate smooth voice connections
**Depends on**: Phases 1, 3, 5
**Requirements**: VLEAD-01, VLEAD-02, VLEAD-03, VLEAD-04, VLEAD-05, VLEAD-06, VLEAD-07, VLEAD-08
**Success Criteria** (what must be TRUE):
  1. Two voices moving C-G then D-A are flagged as parallel fifths
  2. Voice crossing (lower voice above upper voice) and voice overlap are detected and reported with specific positions
  3. Given two chords, the system finds the smoothest voice leading path (minimum total semitone movement)
  4. A complete voice leading check on a Bach chorale progression returns a structured list of all violations by type and position
**Plans**: 2 plans

Plans:
- [ ] 07-01-PLAN.md -- VoiceLeadingViolation dataclass, parallel fifths/octaves, crossing, overlap, leaps, check_voice_leading orchestrator
- [ ] 07-02-PLAN.md -- smooth_voice_leading permutation search and generate_inner_voices greedy generation

### Phase 8: Counterpoint
**Goal**: Users can provide a cantus firmus melody and receive valid species counterpoint lines that follow standard rules
**Depends on**: Phases 1, 7
**Requirements**: CPTR-01, CPTR-02, CPTR-03, CPTR-04, CPTR-05, CPTR-06, CPTR-07, CPTR-08, CPTR-09, CPTR-10
**Success Criteria** (what must be TRUE):
  1. Given a cantus firmus, the system generates a first-species counterpoint line with no parallel fifths, no parallel octaves, and correct consonant intervals on every beat
  2. Species II through V each produce increasingly complex counterpoint that follows the specific rules of that species (two-against-one, four-against-one, syncopated suspensions, florid combination)
  3. An existing counterpoint line can be validated against species rules, returning a structured violation list with severity levels (error/warning/suggestion)
  4. Counterpoint generation works both above and below the cantus firmus
  5. Three- and four-voice counterpoint can be generated from a single melodic line
**Plans**: 2 plans

Plans:
- [ ] 08-01: Species I-III counterpoint generation and validation
- [ ] 08-02: Species IV-V, free counterpoint, multi-voice generation, configurable rules

### Phase 9: Set Theory & Serial
**Goal**: Users can perform pitch class set analysis and generate/manipulate 12-tone rows and matrices
**Depends on**: Phase 1
**Requirements**: SETTH-01, SETTH-02, SETTH-03, SETTH-04, SETTH-05, SETTH-06, SETTH-07, SETTH-08, SETTH-09, SERI-01, SERI-02, SERI-03, SERI-04, SERI-05, SERI-06
**Success Criteria** (what must be TRUE):
  1. The pitch class set {0, 1, 3, 7} is correctly reduced to prime form [0, 1, 3, 7] with Forte number 4-Z15 and interval vector [1,1,1,1,1,1]
  2. A 12-tone row generates the complete 48-form matrix (12 primes, 12 inversions, 12 retrogrades, 12 retrograde-inversions)
  3. Set relationships (subset, superset, Z-relation, complement) are correctly computed between any two pitch class sets
  4. A 12-tone row can be realized as a sequence of pitched notes in a given register with correct octave placement
**Plans**: 2 plans

Plans:
- [ ] 09-01: Pitch class set operations, prime form, Forte numbers, set relationships
- [ ] 09-02: 12-tone row definition, matrix generation, row properties, segmentation

### Phase 10: Pattern Generation
**Goal**: Users can generate rhythmic and melodic patterns using established compositional techniques
**Depends on**: Phases 1, 2
**Requirements**: RHYT-06, PATT-01, PATT-02, PATT-03, PATT-04, PATT-05, PATT-06, PATT-07
**Success Criteria** (what must be TRUE):
  1. Euclidean rhythm generation distributes N beats over M slots correctly (e.g., E(3,8) produces the tresillo pattern [x..x..x.])
  2. An isorhythmic pattern applies a talea (rhythm) and color (pitch sequence) that cycle independently, producing correct medieval-style isorhythm
  3. Hocket generation distributes a single phrase across multiple voices such that no two voices sound simultaneously
  4. A rhythmic canon offsets a phrase by a specified duration across multiple voices with correct alignment
**Plans**: 2 plans

Plans:
- [ ] 10-01: Euclidean rhythms, isorhythm, ostinato, binary patterns, accent patterns
- [ ] 10-02: Rhythmic canon, hocket, rhythm-pitch separation/application

### Phase 11: Algorithmic Composition
**Goal**: Users can generate new musical material using algorithmic techniques trained on or constrained by existing phrases
**Depends on**: Phases 1, 2, 3
**Requirements**: ALGO-01, ALGO-02, ALGO-03, ALGO-04, ALGO-05, ALGO-06, ALGO-07
**Success Criteria** (what must be TRUE):
  1. A Markov chain trained on a Bach chorale melody generates new melodies that follow similar interval/rhythm patterns
  2. An L-system with user-defined production rules generates a phrase that expands deterministically across generations
  3. A tendency mask constrains pitch selection over time -- notes at the start cluster near C4, notes at the end cluster near C6
  4. Generating variations on a theme produces multiple distinct but recognizably related phrases through systematic transform application
**Plans**: 2 plans

Plans:
- [ ] 11-01: Markov chains (first and higher order), probabilistic selection, random walk
- [ ] 11-02: L-systems, tendency masks, variation generation

### Phase 12: I/O Expansion
**Goal**: Users can import from and export to standard music interchange formats (MusicXML, MIDI)
**Depends on**: Phase 1
**Requirements**: NOTA-08, NOTA-09, NOTA-10, NOTA-11
**Success Criteria** (what must be TRUE):
  1. A MusicXML file exported from Dorico or Sibelius imports into Cadenza with pitches, durations, dynamics, and articulations preserved
  2. Cadenza's internal representation exports to MusicXML that opens correctly in Dorico and Sibelius
  3. A MIDI file imports into Cadenza with correct pitch and duration mapping (quantized to the nearest rhythmic grid)
  4. Cadenza exports to MIDI with correct note-on/off events, velocities mapped from dynamics, and tempo metadata
**Plans**: 2 plans

Plans:
- [ ] 12-01: MusicXML import/export (lxml)
- [ ] 12-02: MIDI import/export (mido)

### Phase 13: API Completion
**Goal**: The REST API handles expensive operations asynchronously and supports multi-operation batch requests
**Depends on**: Phases 4, 5, 6, 7, 8, 9, 10, 11, 12
**Requirements**: API-06, API-09
**Success Criteria** (what must be TRUE):
  1. A counterpoint generation request returns a job ID immediately; polling the job endpoint eventually returns the completed result
  2. A batch endpoint accepts multiple operations in a single request and returns all results in one response
  3. All new endpoints (analysis, counterpoint, generation, I/O) added since Phase 4 are documented in OpenAPI and follow the same dual CN+JSON response pattern
**Plans**: 2 plans

Plans:
- [ ] 13-01: Async job pattern, batch endpoint, final API integration for all phases

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9 -> 10 -> 11 -> 12 -> 13

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 2/3 | Complete    | 2026-03-19 |
| 2. Transforms | 1/3 | Complete    | 2026-03-19 |
| 3. Theory Libraries | 0/2 | Complete    | 2026-03-19 |
| 4. REST API v1 | 0/2 | Complete    | 2026-03-19 |
| 5. Harmonic Analysis | 2/2 | Complete   | 2026-03-19 |
| 6. Batch & Analysis | 1/2 | In Progress|  |
| 7. Voice Leading | 2/2 | Complete   | 2026-03-20 |
| 8. Counterpoint | 0/2 | Not started | - |
| 9. Set Theory & Serial | 0/2 | Not started | - |
| 10. Pattern Generation | 0/2 | Not started | - |
| 11. Algorithmic Composition | 0/2 | Not started | - |
| 12. I/O Expansion | 0/2 | Not started | - |
| 13. API Completion | 0/1 | Not started | - |
