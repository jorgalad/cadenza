# Domain Pitfalls

**Domain:** Music theory library with notation software integration
**Project:** Cadenza
**Researched:** 2026-03-18

**Source note:** WebFetch, WebSearch, and Brave Search were all unavailable during this research session. Findings draw on training data knowledge of music theory (stable domain), Music21 architecture, Opusmodus/OMN conventions, MusicXML specification, and notation software behavior. Music theory correctness claims are HIGH confidence. Software version-specific claims (Dorico API versions, current library releases) are MEDIUM confidence and flagged for verification.

---

## Critical Pitfalls

Mistakes that cause data corruption, incorrect musical output, or architectural rewrites.

### Pitfall 1: Treating Pitch as an Integer (The Enharmonic Catastrophe)

**What goes wrong:** Representing pitches as MIDI numbers (integers 0-127) destroys enharmonic information. Eb4 and D#4 are both MIDI 63, but they are fundamentally different pitches in tonal music.

**Why it happens:** MIDI numbers are simple. Integer arithmetic is easy. It feels like you can "just convert back later." You cannot -- the information is destroyed.

**Consequences:**
- Transposing C-E-G up a minor third yields Eb-Gb-Bb (correct) or D#-F#-A# (wrong context). Without spelling context, the system guesses wrong.
- Key detection becomes impossible.
- MusicXML export produces wrong accidentals.
- Every downstream consumer (Dorico, Sibelius) displays wrong note names.

**Prevention:**
- Pitch is a compound type: `(name: A-G, accidental: -2 to +2, octave: int)`.
- MIDI number is a derived property, never stored.
- Interval arithmetic operates on `(generic_size, quality)` pairs, not semitone counts.
- Only provide MIDI conversion at I/O boundaries, requiring key context for MIDI-to-pitch.

**Detection:** If any code constructs a Pitch from a single integer without a spelling context, the model is wrong.

### Pitfall 2: Context-Free Interval Naming

**What goes wrong:** A diminished 5th and an augmented 4th span the same semitones (6). If intervals are computed from semitone distance alone, the system cannot distinguish them. Chord identification, voice leading, and counterpoint rules all break.

**Why it happens:** Semitone counting is the obvious first implementation.

**Consequences:**
- C to Gb identified as augmented 4th instead of diminished 5th.
- German augmented 6th chord misidentified.
- Counterpoint rules for diminished intervals applied incorrectly.

**Prevention:**
- Intervals computed from pitch spelling: `generic_size = letter_distance + 1`, quality derived from accidentals.
- Compound intervals (9th, 11th) preserve their compound nature.
- Provide `from_semitones(n, preferred_spelling)` factory requiring a spelling hint.

### Pitfall 3: Duration as Floating Point

**What goes wrong:** Dotted notes, tuplets, and ties produce fractions that accumulate floating-point rounding errors. Measures do not sum to the correct total. MIDI export timing drifts.

**Why it happens:** Floats are the default numeric type. The errors are small initially but accumulate.

**Consequences:**
- Measures that should total 4 beats total 3.9999999997 beats.
- Tuplet grouping validation fails due to epsilon comparisons.
- MIDI timing drifts over long pieces.

**Prevention:**
- Use `fractions.Fraction` for ALL internal duration arithmetic.
- A quarter note = `Fraction(1, 4)` of a whole note.
- Tuplet ratios are explicit fractions: `Fraction(2, 3)` for triplets.
- Never use floats. Convert to float only at MIDI export boundary.

**Detection:** Search for `float` in duration-related code. If found, the arithmetic will eventually break.

### Pitfall 4: Dorico API Assumptions

**What goes wrong:** Building Dorico integration based on the assumption that Dorico has a Python scripting API (stated in PROJECT.md). Based on training data (May 2025), Dorico uses Lua for internal scripting and JSON-RPC over WebSocket for remote control.

**Why it happens:** The PROJECT.md states "Dorico has a Python scripting API." This may be outdated, incorrect, or referring to a future/beta feature.

**Consequences:** Building a Python-native Dorico plugin that cannot actually run inside Dorico. Wasted effort.

**Prevention:**
- VERIFY the current Dorico API capabilities from Steinberg documentation BEFORE designing the integration layer.
- Design the REST API as the primary integration mechanism (language-agnostic).
- Build Dorico integration as an external bridge (Python process connecting to Dorico's Remote Control API), not an embedded plugin.

**Detection:** Try to run a Python script inside Dorico. If it does not work, the assumption was wrong.

### Pitfall 5: MusicXML Vendor Divergence

**What goes wrong:** MusicXML is a standard, but Dorico and Sibelius export it differently. Beam grouping, voice numbering, chord symbol encoding, tuplet display, and accidental handling all vary.

**Why it happens:** MusicXML 4.0 has hundreds of optional elements. Each program implements its own subset.

**Consequences:**
- Cadenza works with Dorico exports but crashes on Sibelius exports (or vice versa).
- Round-trip loses information that the user expected to preserve.

**Prevention:**
- Test with REAL MusicXML exports from both Dorico and Sibelius.
- Implement a normalization layer for vendor-specific quirks.
- Be defensive: every element is optional, use sensible defaults.
- Reject unsupported elements with clear error messages rather than silently dropping them.
- Maintain a "known quirks" registry per program.

### Pitfall 6: Scope Explosion

**What goes wrong:** Attempting Music21 (800+ classes) + Opusmodus (600+ functions) parity simultaneously. The project never ships.

**Why it happens:** The project spec says "functional parity with Opusmodus + Music21 combined." This is multi-year scope.

**Consequences:** Years of work with no usable output. Early architectural decisions do not scale.

**Prevention:**
- Tiered implementation:
  - Tier 1 (MVP): OMN parser, pitch/interval model, basic transforms, REST API, MusicXML I/O
  - Tier 2: Harmonic analysis, chord library, scale library, voice leading
  - Tier 3: Counterpoint, algorithmic composition, serial techniques
  - Tier 4: Remaining parity functions
- Ship and test Tier 1 with actual Dorico integration before starting Tier 2.
- Each tier validates the architecture.

---

## Moderate Pitfalls

### Pitfall 7: OMN Sticky State Parsing

**What goes wrong:** In OMN, if a note omits duration, it inherits from the previous note. Same for dynamics. This makes parsing stateful, which conflicts with a pure grammar approach.

**Prevention:**
- Two-pass parsing: Lark grammar handles syntax (produces AST with Optional fields). A second Transformer pass resolves inherited/sticky values.
- Test with real Opusmodus output that relies on sticky values.
- Test edge cases: first event with no duration specified, dynamic resets.

### Pitfall 8: Polyphony in a Monophonic Model

**What goes wrong:** OMN is fundamentally a sequence of events. But music has chords (simultaneous pitches) and multiple voices. If the model is a flat list, chord identification, voice leading, and counterpoint cannot work.

**Prevention:**
- Design polyphony from day one: `Note` (one pitch), `Chord` (multiple pitches), `Voice` (sequence of events), `Part` (one or more voices), `Score` (multiple parts).
- Transformations like retrograde operate at Voice level and preserve internal chord structure.
- OMN chord syntax (pitches concatenated: `c4e4g4`) must be parsed into Chord objects, not kept as strings.

### Pitfall 9: Counterpoint Rule Explosion

**What goes wrong:** Species counterpoint has dozens of interacting rules. Implementing them as boolean gates produces a system that is either too strict or too lenient.

**Prevention:**
- Rules as configurable rulesets with severity levels (ERROR, WARNING, SUGGESTION).
- Provide presets: `StrictSpecies` (Fux), `TonalCounterpoint` (Bach), `FreeCounterpoint`.
- Start with Species I only. Do not attempt Species V until I-IV work.
- Use constraint satisfaction, not imperative generation.

### Pitfall 10: Key Detection Overconfidence

**What goes wrong:** Key detection returns a single key with high confidence. Real music modulates, is modal, or is atonal.

**Prevention:**
- Return a ranked list of candidates with confidence scores.
- Support windowed analysis (key changes over time).
- Include modal detection (not just major/minor).
- Provide an "I know the key" override.
- Document limitations clearly.

### Pitfall 11: MIDI Treated as Lossless

**What goes wrong:** MIDI loses enharmonic spelling, precise notation (dotted vs tied), dynamics beyond velocity, articulation detail, key/time signatures, and tuplet grouping.

**Prevention:**
- MIDI import is explicitly "best effort" with documented limitations.
- Require key context for MIDI import (or default to C major with warning).
- Never use MIDI as an intermediate format internally.
- MIDI export is safe but with documented information loss.

### Pitfall 12: Octave Numbering Convention Mismatch

**What goes wrong:** Middle C is C4 in SPN, but different DAWs and hardware use C3, C4, or C5.

**Prevention:**
- Document convention explicitly: "Middle C = C4 = MIDI 60."
- All I/O boundaries have an `octave_offset` parameter.
- Integration adapters set the appropriate offset per target program.

---

## Minor Pitfalls

### Pitfall 13: Pitch/Dynamic Name Collision in OMN

**What goes wrong:** 'f' is both a pitch name (F) and a dynamic (forte). 'b' is both a pitch (B) and a flat accidental suffix. Parser ambiguity.

**Prevention:** Context-sensitive grammar rules. In pitch position, 'f4' = F octave 4. In dynamic position, 'f' = forte. Lark grammar uses positional rules.

### Pitfall 14: No API Versioning

**What goes wrong:** Changing the API after DAW integrations are built breaks them.

**Prevention:** `/v1/` prefix from day one. Pydantic model versioning for schema evolution.

### Pitfall 15: Music21 Test Oracle Version Drift

**What goes wrong:** Music21 version upgrades change behavior, breaking tests even when Cadenza is correct.

**Prevention:** Pin Music21 version in test dependencies. Review failures on upgrade.

### Pitfall 16: Double Accidentals Omitted

**What goes wrong:** Supporting only sharps/flats ignores double-sharp (##/x) and double-flat (bb), which are required in keys like G# minor (leading tone is Fx).

**Prevention:** Accidental range -2 to +2. Test with keys requiring double accidentals.

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Core Data Model | Pitch as integer (#1) | Compound pitch type from day one |
| Core Data Model | Context-free intervals (#2) | Interval from spelling, not semitones |
| Core Data Model | Float duration (#3) | fractions.Fraction exclusively |
| Core Data Model | Monophonic assumption (#8) | Note/Chord/Voice/Part hierarchy |
| OMN Parser | Sticky state (#7) | Two-pass: grammar + resolver |
| OMN Parser | Name collisions (#13) | Positional grammar rules |
| MusicXML I/O | Vendor divergence (#5) | Test with both Dorico and Sibelius |
| MIDI I/O | Treated as lossless (#11) | Document as lossy, require key context |
| Analysis | Key detection overconfidence (#10) | Ranked results with confidence |
| Counterpoint | Rule explosion (#9) | Configurable rulesets, species I first |
| REST API | No versioning (#14) | /v1/ prefix from day one |
| DAW Integration | Dorico API assumption (#4) | VERIFY before building |
| All Phases | Scope explosion (#6) | Tiered implementation with gates |

## Sources

- Music theory formal rules (centuries-old, stable domain)
- Music21 architecture patterns and known issues
- MusicXML 4.0 specification complexity
- MIDI specification limitations
- Opusmodus OMN documentation conventions
- Counterpoint pedagogy (Fux, common-practice theory)
