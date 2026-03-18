# Cadenza

## What This Is

Cadenza is a comprehensive music analysis, transformation, and generation library designed for integration into professional notation software (Dorico by Steinberg, Sibelius by Avid). It parses a Lisp-inspired OMN-like notation format representing musical events (pitch, duration, dynamic, articulation), and exposes a large catalogue of music-theory-grounded operations — from simple transforms (retrograde, inversion, transposition) through counterpoint generation, harmonic analysis, batch operations, and algorithmic composition tools. The library is implemented in Python, exposed via a REST API, and designed so that notation software companies can embed it as a scripting engine or call it over HTTP.

## Core Value

A notation software user should be able to select any musical phrase, send it to Cadenza, and receive back a musically correct transformation or harmonization — without needing to understand the theory behind it.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] OMN-inspired notation parser and serializer (pitch, duration, dynamic, articulation)
- [ ] Core pitch/interval model with enharmonic awareness (Eb ≠ D# in context)
- [ ] Melodic transformation engine (retrograde, inversion, transposition, augmentation, diminution, rotation, permutation)
- [ ] Rhythmic transformation engine (retrograde, augmentation, diminution, rotation, metric modulation)
- [ ] Counterpoint generation from a single melody (species counterpoint rules, multi-voice)
- [ ] Harmonic analysis (chord identification, Roman numeral analysis, key detection)
- [ ] Batch operation system (apply articulation/dynamic/expression to patterns of notes)
- [ ] Scale and mode library (all common Western + modal + non-Western scales)
- [ ] Chord and chord-progression library
- [ ] Voice leading engine (smooth voice leading, avoid parallel 5ths/8ths)
- [ ] Algorithmic composition tools (12-tone/serial techniques, set theory operations)
- [ ] Pattern generation (Euclidean rhythms, isorhythm, ostinato generation)
- [ ] REST API exposing all operations (JSON in/out, OMN strings)
- [ ] Comprehensive function catalogue matching Opusmodus scope (~600+ functions)
- [ ] Music21-equivalent analysis functions (ambitus, contour, interval vectors, etc.)

### Out of Scope

- Audio playback or synthesis — notation/MIDI only
- GUI or notation rendering — backend library only
- Real-time audio analysis — offline/symbolic music only
- DAW plugin (VST/AU) — REST API is the integration mechanism for v1
- Microtonality / non-12-TET tuning systems — defer to v2

## Context

- **Origin**: Conversations with Steinberg (Dorico) and Avid (Sibelius) about giving users more freedom to transform and generate musical material inside notation software
- **Comparable tools**: Opusmodus (Common Lisp, OMN notation, algorithmic composition) and Music21 (Python, music analysis, academic). Cadenza combines both, implemented in Python for ecosystem compatibility
- **Notation format**: OMN-inspired — events expressed as `(duration pitch dynamic articulation)` e.g. `(e f3 pp stacc)`. Notes use scientific pitch notation (f3 = F in octave 3). Accidentals use `b`/`s` suffix (eb3, fs4). This is the canonical wire format for all API calls
- **Integration target**: Dorico has a Python scripting API — Cadenza can be called natively from Dorico scripts. Sibelius integration via HTTP. Both can use the REST endpoint
- **Music theory correctness**: AI tools frequently confuse note/chord names with English words. The engine must treat pitch, interval, and chord symbols as a formal symbolic system, not text
- **Research sources**: Opusmodus PDF docs (opusmodus.com), Music21 Python library docs, Bach Project for Max (bach-project.net)

## Constraints

- **Language**: Python — aligns with Music21, Dorico scripting API, and the REST ecosystem
- **Data model**: Immutable named tuples representing musical events (Lisp-inspired, structurally equivalent to S-expressions but serializable to JSON and OMN strings)
- **Music theory correctness**: Every function must be validated against established music theory rules; enharmonic equivalence, voice leading rules, and counterpoint rules must be formally encoded, not approximated
- **Integration**: REST API (FastAPI) as primary integration mechanism; pure Python library as secondary (importable without the server)
- **Scope**: Aiming for functional parity with Opusmodus + Music21 combined — this is a multi-week/multi-month project

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Python over Common Lisp | Larger ecosystem, Dorico Python API, Music21 interop, easier REST integration; OMN data structures replicated as named tuples | — Pending |
| OMN-inspired notation as canonical format | Closest to Opusmodus conventions; expressive, compact, human-readable; can round-trip through the API | — Pending |
| REST API as primary integration layer | Language-agnostic; works with any DAW that has HTTP access; can be wrapped as native library later | — Pending |
| Backend only for v1 | Focus on correctness of music theory engine before building any UI or rendering | — Pending |

---
*Last updated: 2026-03-18 after initialization*
