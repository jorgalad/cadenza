# Requirements: Cadenza

**Defined:** 2026-03-18
**Core Value:** A notation software user can select any musical phrase, send it to Cadenza, and receive back a musically correct transformation or harmonization — without needing to understand the theory behind it.

---

## v1 Requirements

### Notation & Parsing (NOTA)

- [ ] **NOTA-01**: System parses OMN-style notation strings into internal event objects (`(e f3 pp stacc)` → Event)
- [ ] **NOTA-02**: System serializes internal event objects back to OMN notation strings (round-trip lossless)
- [ ] **NOTA-03**: Parser handles all duration values: whole (w), half (h), quarter (q), eighth (e), sixteenth (s), thirty-second (t), sixty-fourth (x), with dots and ties
- [ ] **NOTA-04**: Parser handles rests (encoded as negative durations or `r` prefix per OMN spec)
- [ ] **NOTA-05**: Parser handles tuplets (triplets, quintuplets, etc.)
- [ ] **NOTA-06**: Parser handles all dynamic markings: ppp, pp, p, mp, mf, f, ff, fff
- [ ] **NOTA-07**: Parser handles articulation markings: staccato, tenuto, accent, legato, marcato, fermata, trill, and others
- [ ] **NOTA-08**: System imports MusicXML files into internal representation
- [ ] **NOTA-09**: System exports internal representation to MusicXML
- [ ] **NOTA-10**: System imports MIDI files into internal representation
- [ ] **NOTA-11**: System exports internal representation to MIDI
- [ ] **NOTA-12**: Parser provides clear error messages with position info for invalid notation

### Core Data Model (CORE)

- [ ] **CORE-01**: Pitch type is a compound immutable value (letter A-G, accidental, octave integer) — never a raw MIDI integer
- [ ] **CORE-02**: Pitch equality is spelling-sensitive: Eb3 ≠ D#3; explicit `enharmonic_equal()` for MIDI-number comparison
- [ ] **CORE-03**: Duration type uses `fractions.Fraction` internally — never float arithmetic
- [ ] **CORE-04**: Interval type encodes both quality (perfect/major/minor/augmented/diminished) and number (unison through compound intervals)
- [ ] **CORE-05**: Note type combines Pitch + Duration + Dynamic + Articulation as immutable frozen dataclass
- [ ] **CORE-06**: Rest type is a distinct type from Note (not a Note with a special pitch)
- [ ] **CORE-07**: Phrase type is an ordered immutable sequence of Notes and Rests
- [ ] **CORE-08**: Score type supports multiple simultaneous Phrases (voices/staves)
- [ ] **CORE-09**: All core types are serializable to/from JSON without information loss
- [ ] **CORE-10**: All core types support equality comparison and hashing (usable in sets/dicts)

### Pitch Operations (PTCH)

- [ ] **PTCH-01**: Transpose a note or phrase by a given interval (diatonic and chromatic)
- [ ] **PTCH-02**: Invert a phrase around a given pitch axis (melodic inversion)
- [ ] **PTCH-03**: Compute the interval between any two pitches (with correct spelling)
- [ ] **PTCH-04**: Enharmonic respelling of a pitch (Eb3 ↔ D#3)
- [ ] **PTCH-05**: Pitch class reduction (pitch → pitch class 0–11)
- [ ] **PTCH-06**: MIDI note number to/from Pitch conversion (with enharmonic disambiguation)
- [ ] **PTCH-07**: Frequency (Hz) to/from Pitch conversion (A440 reference)
- [ ] **PTCH-08**: Determine whether a pitch belongs to a given scale or chord
- [ ] **PTCH-09**: Find the nearest pitch(es) in a given scale to an arbitrary pitch

### Rhythm Operations (RHYT)

- [ ] **RHYT-01**: Rhythmic retrograde of a phrase (reverse duration sequence)
- [ ] **RHYT-02**: Rhythmic augmentation (multiply all durations by a ratio)
- [ ] **RHYT-03**: Rhythmic diminution (divide all durations by a ratio)
- [ ] **RHYT-04**: Rhythmic rotation (cyclic shift of durations)
- [ ] **RHYT-05**: Metric modulation (reinterpret a duration unit as a new tempo reference)
- [ ] **RHYT-06**: Euclidean rhythm generation (distribute N beats over M slots)
- [ ] **RHYT-07**: Rhythmic pattern extraction from a phrase
- [ ] **RHYT-08**: Quantize a phrase to a given rhythmic grid
- [ ] **RHYT-09**: Compute total duration of a phrase

### Melodic Transforms (MELO)

- [ ] **MELO-01**: Melodic retrograde (reverse pitch sequence, keep original rhythm)
- [ ] **MELO-02**: Retrograde-inversion (reverse and invert)
- [ ] **MELO-03**: Rotation (cyclic permutation of notes in a phrase)
- [ ] **MELO-04**: Permutation (reorder notes by index list)
- [ ] **MELO-05**: Interpolation (insert passing notes between existing notes)
- [ ] **MELO-06**: Omission (remove every Nth note or notes matching a predicate)
- [ ] **MELO-07**: Repetition (repeat a phrase N times, with optional variation)
- [ ] **MELO-08**: Mirror (palindrome: phrase + retrograde of phrase)
- [ ] **MELO-09**: Fragmentation (split a phrase into sub-phrases of given lengths)
- [ ] **MELO-10**: Concatenation (join two or more phrases)
- [ ] **MELO-11**: Interleave (alternate notes from two phrases)
- [ ] **MELO-12**: Apply a pitch mapping function to every note in a phrase

### Harmonic Analysis (HARM)

- [ ] **HARM-01**: Identify chord from a set of simultaneous pitches (root, quality, inversion)
- [ ] **HARM-02**: Roman numeral analysis of a chord within a key context
- [ ] **HARM-03**: Key detection from a phrase or score (using pitch class frequency analysis)
- [ ] **HARM-04**: Harmonic rhythm analysis (detect chord change points)
- [ ] **HARM-05**: Functional harmony labeling (tonic, dominant, subdominant, etc.)
- [ ] **HARM-06**: Detect modulation between keys within a phrase
- [ ] **HARM-07**: Generate chord symbol string from a chord object (e.g. "Cmaj7", "F#m", "Bdim7")
- [ ] **HARM-08**: Parse chord symbol string into a chord object
- [ ] **HARM-09**: Realize a chord as a list of pitches in a given voicing/inversion
- [ ] **HARM-10**: Identify borrowed chords (chords from parallel keys)

### Scale & Mode Library (SCAL)

- [ ] **SCAL-01**: Define and retrieve all common Western scales: major, natural/harmonic/melodic minor
- [ ] **SCAL-02**: All church modes: Ionian, Dorian, Phrygian, Lydian, Mixolydian, Aeolian, Locrian
- [ ] **SCAL-03**: Pentatonic scales (major, minor, blues pentatonic)
- [ ] **SCAL-04**: Blues scale (hexatonic)
- [ ] **SCAL-05**: Symmetric scales: whole tone, diminished (octatonic), augmented
- [ ] **SCAL-06**: Bebop scales (dominant, major, minor)
- [ ] **SCAL-07**: Non-Western scales: Arabic maqam modes, Hungarian minor, Neapolitan, etc.
- [ ] **SCAL-08**: User-defined scale from interval pattern
- [ ] **SCAL-09**: Given a root pitch and scale name, return all pitches in the scale (all octaves or single octave)
- [ ] **SCAL-10**: Determine what scale(s) a given set of pitches belongs to
- [ ] **SCAL-11**: Return the degree of a pitch within a scale (scale degree 1–7 + chromatic)
- [ ] **SCAL-12**: Return the relative and parallel major/minor of any scale

### Chord Library (CHRD)

- [ ] **CHRD-01**: All triads: major, minor, diminished, augmented
- [ ] **CHRD-02**: All seventh chords: maj7, dom7, min7, half-dim7, dim7, min-maj7, aug7
- [ ] **CHRD-03**: Extended chords: 9th, 11th, 13th (dominant and other qualities)
- [ ] **CHRD-04**: Added-note chords: add9, add11, sus2, sus4
- [ ] **CHRD-05**: All inversions of any chord (1st, 2nd, 3rd inversion)
- [ ] **CHRD-06**: Diatonic chords of a scale (returns all triads/sevenths built on each scale degree)
- [ ] **CHRD-07**: Secondary dominants (V/ii, V/iii, etc.)
- [ ] **CHRD-08**: Neapolitan and augmented sixth chords (Italian, French, German)
- [ ] **CHRD-09**: User-defined chord from interval stack

### Voice Leading (VLEAD)

- [ ] **VLEAD-01**: Detect parallel fifths between any two voices
- [ ] **VLEAD-02**: Detect parallel octaves between any two voices
- [ ] **VLEAD-03**: Detect voice crossing (lower voice exceeds upper voice in pitch)
- [ ] **VLEAD-04**: Detect voice overlap (voice moves to a pitch beyond the previous pitch of adjacent voice)
- [ ] **VLEAD-05**: Find smoothest voice leading path between two chords (minimize total voice movement)
- [ ] **VLEAD-06**: Detect large leaps and suggest resolutions (leaps > octave, augmented/diminished leaps)
- [ ] **VLEAD-07**: Check all standard voice leading rules for a chord progression and return violation list
- [ ] **VLEAD-08**: Generate smooth inner voice parts given soprano and bass lines

### Counterpoint (CPTR)

- [ ] **CPTR-01**: Given a cantus firmus (melody), generate a correct first-species counterpoint (note-against-note)
- [ ] **CPTR-02**: Generate second-species counterpoint (two notes against one)
- [ ] **CPTR-03**: Generate third-species counterpoint (four notes against one)
- [ ] **CPTR-04**: Generate fourth-species counterpoint (syncopated, suspensions)
- [ ] **CPTR-05**: Generate fifth-species counterpoint (florid, combining all species)
- [ ] **CPTR-06**: Validate an existing counterpoint line against species rules and return violation list
- [ ] **CPTR-07**: Support counterpoint above and below the cantus firmus
- [ ] **CPTR-08**: Generate two-voice free counterpoint (tonal, not strict species)
- [ ] **CPTR-09**: Generate three- and four-voice counterpoint from a single melodic line
- [ ] **CPTR-10**: Configurable rule severity (error/warning/suggestion) for stylistic flexibility

### Set Theory (SETTH)

- [ ] **SETTH-01**: Compute prime form of a pitch class set
- [ ] **SETTH-02**: Compute interval vector (interval class vector) of a pitch class set
- [ ] **SETTH-03**: Determine Forte number for a pitch class set
- [ ] **SETTH-04**: Look up pitch class set by Forte number
- [ ] **SETTH-05**: Compute complement of a pitch class set
- [ ] **SETTH-06**: Compute inversion of a pitch class set
- [ ] **SETTH-07**: Compute transposition of a pitch class set
- [ ] **SETTH-08**: Test set relationship: subset, superset, Z-relation
- [ ] **SETTH-09**: Similarity measures between pitch class sets (Rp, R0, R1, R2)

### Serial / 12-Tone (SERI)

- [ ] **SERI-01**: Define a 12-tone row from a list of pitch classes
- [ ] **SERI-02**: Generate the complete 48-form matrix (P, I, R, RI in all transpositions)
- [ ] **SERI-03**: Detect if a row has special properties (all-interval row, combinatoriality)
- [ ] **SERI-04**: Realize a row form as a sequence of pitched notes
- [ ] **SERI-05**: Segmentation of a row into trichords, tetrachords, hexachords
- [ ] **SERI-06**: Row derivation (generating a row from a smaller set by operations)

### Pattern & Rhythm Generation (PATT)

- [ ] **PATT-01**: Generate isorhythmic patterns (talea + color)
- [ ] **PATT-02**: Generate ostinato from a phrase (loop with optional variation)
- [ ] **PATT-03**: Apply a rhythmic pattern to a pitch sequence (separate rhythm from pitch)
- [ ] **PATT-04**: Generate binary rhythm patterns (from integer representation)
- [ ] **PATT-05**: Rhythmic canon generation (phrase + offset voices)
- [ ] **PATT-06**: Hocket generation (distribute notes of a phrase across multiple voices)
- [ ] **PATT-07**: Generate accent patterns (every Nth note accented)

### Batch Operations (BATCH)

- [ ] **BATCH-01**: Set articulation on every Nth note in a phrase
- [ ] **BATCH-02**: Set dynamic on every Nth note in a phrase
- [ ] **BATCH-03**: Apply a crescendo or decrescendo across a phrase (gradual dynamic change)
- [ ] **BATCH-04**: Add/remove articulation from all notes matching a predicate (e.g. all notes on beat 1)
- [ ] **BATCH-05**: Quantize all note lengths to a given grid
- [ ] **BATCH-06**: Humanize: apply small random perturbations to timing and velocity
- [ ] **BATCH-07**: Replace all instances of a pitch (or pitch class) with another pitch
- [ ] **BATCH-08**: Filter phrase: keep only notes matching a predicate
- [ ] **BATCH-09**: Apply any transform function to a sliding window over a phrase

### Algorithmic Composition (ALGO)

- [ ] **ALGO-01**: First-order Markov chain melody generation from a trained phrase
- [ ] **ALGO-02**: Higher-order Markov chain generation (configurable order)
- [ ] **ALGO-03**: L-system (Lindenmayer system) melody/rhythm generation with configurable rules
- [ ] **ALGO-04**: Probabilistic note selection from a weighted pitch set
- [ ] **ALGO-05**: Tendency mask application (pitch probability varies over time)
- [ ] **ALGO-06**: Random walk melody generation within scale/interval constraints
- [ ] **ALGO-07**: Generate variations on a theme (systematic application of transforms)

### Analysis (ANAL)

- [ ] **ANAL-01**: Ambitus: highest and lowest pitch in a phrase
- [ ] **ANAL-02**: Melodic contour analysis (up/down/same direction sequence)
- [ ] **ANAL-03**: Interval sequence extraction from a phrase
- [ ] **ANAL-04**: Pitch class histogram (frequency of each pitch class)
- [ ] **ANAL-05**: Rhythmic density analysis (notes per beat over time)
- [ ] **ANAL-06**: Melodic complexity score (based on interval variety, rhythm variety, contour changes)
- [ ] **ANAL-07**: Identify repeated motifs within a phrase
- [ ] **ANAL-08**: Compare two phrases for similarity (pitch, rhythm, contour)
- [ ] **ANAL-09**: Detect sequence/imitation between phrases

### REST API (API)

- [ ] **API-01**: FastAPI server exposing all transform, analysis, and generation operations as HTTP endpoints
- [ ] **API-02**: All endpoints accept OMN notation strings as input
- [ ] **API-03**: All endpoints return both OMN string and JSON event list in every response
- [ ] **API-04**: Versioned API (`/v1/` prefix) from day one
- [ ] **API-05**: Comprehensive OpenAPI/Swagger documentation auto-generated
- [ ] **API-06**: Async job pattern for expensive operations (counterpoint generation)
- [ ] **API-07**: Structured error responses with music-theory-aware error codes
- [ ] **API-08**: Health check endpoint for DAW integration probing
- [ ] **API-09**: Batch endpoint: apply multiple operations in a single request

---

## v2 Requirements

### Advanced Generation
- **ALGO-08**: Cellular automaton melody generation
- **ALGO-09**: Genetic algorithm composition (fitness function based on music theory rules)
- **ALGO-10**: Style imitation from a corpus of analyzed phrases

### Extended Analysis
- **ANAL-10**: Schenkerian reduction (identify structural tones)
- **ANAL-11**: Neo-Riemannian transformations (P, L, R, N, S)
- **ANAL-12**: Windowed harmonic analysis (track harmonic changes over time)

### Extended I/O
- **NOTA-13**: LilyPond export
- **NOTA-14**: ABC notation import/export
- **NOTA-15**: MEI (Music Encoding Initiative) import/export

### DAW Integration Bridges
- **DAW-01**: Dorico-specific integration (verify and implement against current Dorico API)
- **DAW-02**: Sibelius-specific integration (HTTP plugin bridge)
- **DAW-03**: Python package installable into Dorico's embedded Python environment

### Microtonality
- **MICRO-01**: Support for non-12-TET tuning systems (quarter tones, just intonation)

---

## Out of Scope

| Feature | Reason |
|---------|--------|
| Audio synthesis / playback | Symbolic music only; audio is a separate domain |
| Notation rendering / score display | Backend library; rendering is the DAW's job |
| Real-time audio analysis | Offline symbolic processing only for v1 |
| VST / AU plugin format | REST API is the integration mechanism; native plugins are v3+ |
| Machine learning training | No training pipelines; Markov/probabilistic only |
| Microtonality (non-12-TET) | Deferred to v2 to keep pitch model tractable |
| GUI of any kind | Backend only |

---

## Traceability

*Populated during roadmap creation.*

| Requirement | Phase | Status |
|-------------|-------|--------|
| NOTA-01 through NOTA-12 | Phase 1 | Pending |
| CORE-01 through CORE-10 | Phase 1 | Pending |
| PTCH-01 through PTCH-09 | Phase 2 | Pending |
| RHYT-01 through RHYT-09 | Phase 2 | Pending |
| MELO-01 through MELO-12 | Phase 2 | Pending |
| SCAL-01 through SCAL-12 | Phase 2 | Pending |
| CHRD-01 through CHRD-09 | Phase 2 | Pending |
| API-01 through API-09 | Phase 2 | Pending |
| HARM-01 through HARM-10 | Phase 3 | Pending |
| SETTH-01 through SETTH-09 | Phase 3 | Pending |
| BATCH-01 through BATCH-09 | Phase 3 | Pending |
| ANAL-01 through ANAL-09 | Phase 3 | Pending |
| VLEAD-01 through VLEAD-08 | Phase 4 | Pending |
| CPTR-01 through CPTR-10 | Phase 4 | Pending |
| SERI-01 through SERI-06 | Phase 5 | Pending |
| PATT-01 through PATT-07 | Phase 5 | Pending |
| ALGO-01 through ALGO-07 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 140 total
- Mapped to phases: 140
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-18*
*Last updated: 2026-03-18 after initial definition*
