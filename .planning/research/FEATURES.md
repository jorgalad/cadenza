# Feature Landscape: Cadenza

**Domain:** Music analysis, transformation, and algorithmic composition library
**Researched:** 2026-03-18
**Overall confidence:** MEDIUM (based on training data knowledge of Opusmodus and Music21; WebFetch/WebSearch unavailable for live verification against current docs)

---

## Feature Dependency Map

```
1. Notation/Parsing ──────> ALL other categories (foundational)
2. Pitch Model ──────────> Melodic Transforms, Harmonic Analysis, Counterpoint, Voice Leading,
                           Scale/Mode Library, Chord Library, Set Theory, Serial/12-tone
3. Rhythm Model ─────────> Rhythm Operations, Pattern Generation, Batch Operations
4. Scale/Mode Library ───> Harmonic Analysis, Counterpoint, Chord Library
5. Chord Library ────────> Harmonic Analysis, Voice Leading, Counterpoint
6. Interval Model ───────> Set Theory, Serial/12-tone, Melodic Transforms, Voice Leading
7. Harmonic Analysis ────> Counterpoint (needs to know harmonic context)
8. Voice Leading ────────> Counterpoint (voice leading is a subset of counterpoint rules)
9. Set Theory ───────────> Serial/12-tone (row operations use pc-set concepts)
```

**Critical path:** Notation/Parsing -> Pitch/Rhythm Model -> Scale/Mode + Chord Libraries -> Transforms -> Analysis -> Counterpoint -> Algorithmic Composition

---

## 1. Notation / Parsing

### Table Stakes

| Feature | Why Expected | Complexity | Opusmodus Equivalent | Music21 Equivalent |
|---------|-------------|------------|---------------------|-------------------|
| OMN string parser | Core wire format for all API calls | Medium | Native OMN parser | N/A |
| OMN string serializer | Round-trip: parse -> transform -> serialize | Medium | Native OMN output | N/A |
| Pitch representation (scientific notation) | c4, fs5, eb3 -- foundational data type | Low | Pitch symbols (c4, cs4, etc.) | `pitch.Pitch('C4')` |
| Duration representation | Symbolic durations: w, h, q, e, s, plus dots, ties | Low | `w`, `h`, `q`, `e`, `s`, `t` (tied) | `duration.Duration('quarter')` |
| Dynamic representation | pp, p, mp, mf, f, ff, etc. | Low | Dynamic symbols in OMN | `dynamics.Dynamic('f')` |
| Articulation representation | stacc, legato, accent, tenuto, marcato, etc. | Low | Articulation symbols in OMN | `articulations.Articulation` |
| Rest representation | Negative durations or explicit rest symbol | Low | `-q` (negative duration = rest) | `note.Rest('quarter')` |
| Tuplet representation | Triplets, quintuplets, arbitrary subdivisions | Medium | Tuplet notation in OMN | `duration.Tuplet(3, 2)` |
| MusicXML import | Standard interchange format for notation software | Medium | `musicxml-to-omn` | `converter.parse('file.xml')` |
| MusicXML export | Dorico/Sibelius need this for round-trip | Medium | `omn-to-musicxml` | `musicxml.m21ToXml.GeneralObjectExporter` |
| MIDI import | Common interchange format | Medium | `midi-to-omn` | `midi.MidiFile` |
| MIDI export | Playback verification, DAW integration | Medium | `omn-to-midi` | `midi.translate.streamToMidiFile` |
| Multi-voice/multi-staff parsing | Real music has multiple voices | Medium | Lists of OMN lists | `stream.Score`, `stream.Part` |
| Chord notation in OMN | Simultaneous pitches | Low | `(q c4e4g4)` chord syntax | `chord.Chord(['C4','E4','G4'])` |
| Grace note representation | Common in real scores | Low | Grace note attributes in OMN | `note.Note().grace()` |
| Tie handling | Notes spanning barlines | Medium | Tie symbols in OMN | `tie.Tie('start')` |
| Time signature parsing | Essential for rhythmic context | Low | Time signature in score setup | `meter.TimeSignature('4/4')` |
| Key signature parsing | Essential for tonal context | Low | Key signature in score setup | `key.Key('C')`, `key.KeySignature(0)` |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|------------------|------------|-------|
| Bidirectional OMN <-> MusicXML lossless round-trip | No other Python library speaks OMN natively | High | THE differentiator vs Music21 |
| JSON representation of OMN | REST API friendly; every note/phrase serializable as JSON | Medium | Music21 has no native JSON wire format |
| Streaming/incremental parsing | Handle large scores without loading everything to memory | Medium | Relevant for Dorico/Sibelius with long scores |
| OMN shorthand expansion | `(q c4 d4 e4)` expands attributes across notes | Low | Core Opusmodus ergonomic feature |
| Lilypond export | Academic users, engraving | Medium | Music21 has `lily.translate` |

### Key Functions to Implement

**From Opusmodus:**
- `omn` / `make-omn` -- construct OMN from components
- `omn-to-time-signature` -- extract time signature
- `omn-to-midi` -- convert to MIDI
- `omn-replace` -- replace elements in OMN
- `omn-merge` -- merge multiple OMN streams
- `omn-component` -- extract specific component (pitch, duration, velocity, articulation)
- `pitch-to-midi` / `midi-to-pitch` -- conversion
- `pitch-to-hertz` / `hertz-to-pitch` -- conversion
- `length-to-ratio` -- duration to ratio conversion
- `ratio-to-length` -- ratio to duration conversion

**From Music21:**
- `converter.parse()` -- parse any supported format
- `converter.subConverters` -- format detection
- `musicxml.m21ToXml` -- MusicXML serialization
- `midi.translate` -- MIDI I/O
- `stream.Stream.write()` -- export to any format
- `humdrum.spineParser` -- Humdrum **kern import
- `abc.translate` -- ABC notation import
- `romanText.translate` -- Roman numeral text import

**Complexity: MEDIUM overall.** The parser is the foundation. Getting it right (especially OMN shorthand expansion and round-trip fidelity with MusicXML) is critical.

---

## 2. Pitch Operations

### Table Stakes

| Feature | Why Expected | Complexity | Opusmodus Equivalent | Music21 Equivalent |
|---------|-------------|------------|---------------------|-------------------|
| Transposition (chromatic) | Most basic pitch operation | Low | `pitch-transpose` | `note.transpose(interval)` |
| Transposition (diatonic) | Stay within key | Medium | `pitch-transpose-diatonic` | `note.transpose()` with diatonic intervals |
| Inversion (chromatic) | Mirror around axis | Low | `pitch-invert` | `pitch.Pitch.transpose()` with negative |
| Inversion (diatonic) | Stay within scale | Medium | `pitch-invert :type :diatonic` | `stream.Stream.invertDiatonic()` |
| Retrograde | Reverse pitch sequence | Low | `pitch-retrograde` | Manual reverse on stream |
| Enharmonic equivalence | Eb == D# when needed, distinct when not | Medium | Context-dependent in OMN | `pitch.Pitch.getEnharmonic()` |
| Enharmonic respelling | Contextually correct spelling | Medium | `enharmonic` | `pitch.Pitch.simplifyEnharmonic()` |
| Octave shift | Move up/down octaves | Low | `pitch-octave-shift` | `pitch.Pitch.octave` property |
| Pitch sorting | Sort by pitch height | Low | `pitch-sort` | `sorted()` on MIDI number |
| Pitch filtering | Keep/remove pitches matching criteria | Low | `pitch-filter` | List comprehension on stream |
| Ambitus (range) | Find highest/lowest pitch | Low | `ambitus` | `analysis.discrete.Ambitus` |
| Interval calculation | Distance between two pitches | Low | `pitch-interval` | `interval.Interval(noteA, noteB)` |
| Interval sequence | Series of intervals in a melody | Low | `pitch-to-interval` | Manual iteration |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|------------------|------------|-------|
| Pitch quantize to scale/chord | Snap arbitrary pitches to nearest scale tone | Medium | Opusmodus: `tonality-map` |
| Pitch contour extraction and application | Extract contour shape, apply to different pitches | Medium | Opusmodus: `pitch-contour` |
| Pitch orbit / pitch spirals | Cyclic pitch transformations | Medium | Opusmodus-specific |

### Key Functions to Implement

**From Opusmodus:**
- `pitch-transpose` -- chromatic transposition
- `pitch-transpose-n` -- transpose by varying intervals
- `pitch-invert` -- inversion around axis
- `pitch-retrograde` -- reverse pitch sequence
- `pitch-rotate` -- circular rotation of pitches
- `pitch-permute` -- permutation
- `pitch-sort` -- sort by pitch
- `pitch-demix` -- separate interleaved pitch streams
- `pitch-mix` -- interleave pitch streams
- `pitch-replace` -- replace specific pitches
- `pitch-fragment` -- extract pitch fragments
- `pitch-ornament` -- add ornamental pitches (trills, turns)
- `pitch-quantize` -- snap to scale
- `pitch-contour` -- extract ascending/descending shape
- `pitch-register` -- constrain to register
- `ambitus` -- range of pitches
- `ambitus-filter` -- filter by range
- `tonality-map` -- map pitches to a tonality
- `tonality-series` -- generate pitch series from tonality

**From Music21:**
- `pitch.Pitch.transpose()` -- transposition
- `pitch.Pitch.getEnharmonic()` -- enharmonic respelling
- `pitch.Pitch.midi` -- MIDI number
- `pitch.Pitch.frequency` -- Hz
- `interval.Interval` -- interval computation
- `interval.Interval.direction` -- ascending/descending
- `interval.Interval.semitones` -- chromatic size
- `interval.Interval.generic` -- diatonic size
- `analysis.discrete.Ambitus` -- range analysis

**Complexity: LOW-MEDIUM.** Pitch operations are well-understood and mostly arithmetic on MIDI numbers + enharmonic spelling logic.

---

## 3. Rhythm Operations

### Table Stakes

| Feature | Why Expected | Complexity | Opusmodus Equivalent | Music21 Equivalent |
|---------|-------------|------------|---------------------|-------------------|
| Augmentation | Double/multiply durations | Low | `length-augmentation` | Manual (multiply duration) |
| Diminution | Halve/divide durations | Low | `length-diminution` | Manual |
| Retrograde (rhythmic) | Reverse rhythm sequence | Low | `length-retrograde` | Manual |
| Rotation | Circular shift of rhythms | Low | `length-rotate` | Manual |
| Dotted rhythm generation | Add dots to durations | Low | Dot notation in OMN | `duration.Duration(dots=1)` |
| Tuplet generation | Create arbitrary tuplets | Medium | Tuplet notation in OMN | `duration.Tuplet` |
| Duration quantization | Snap to nearest standard duration | Medium | `length-quantize` | `stream.Stream.quantize()` |
| Bar fitting | Fit rhythm pattern to time signature | Medium | `length-span` | Manual via `stream.makeNotation()` |
| Rhythm extraction from OMN | Get durations only | Low | `omn :length` | `[n.duration for n in stream.notes]` |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|------------------|------------|-------|
| Metric modulation | Change tempo feel by reinterpreting subdivisions | High | Opusmodus: `metric-modulation` |
| Rhythm interpolation | Gradual transformation between two rhythms | High | Opusmodus: `length-interpolation` |
| Euclidean rhythm generation | Algorithmically distributed onsets (Bjorklund) | Medium | Common in electronic music; not in Music21 |
| Swing quantization | Apply swing feel to straight rhythms | Medium | Useful for notation software |
| Polymetric alignment | Align patterns of different lengths | High | Opusmodus: `length-align` |
| Additive rhythm patterns | Build rhythms from additive cells (e.g., 3+2+2) | Medium | Opusmodus-style |

### Key Functions to Implement

**From Opusmodus:**
- `length-augmentation` -- multiply durations
- `length-diminution` -- divide durations
- `length-retrograde` -- reverse rhythm
- `length-rotate` -- circular rotation
- `length-permute` -- permutation
- `length-invert` -- invert rhythm (long<->short)
- `length-fragment` -- extract rhythm fragments
- `length-rest-merge` -- merge adjacent rests
- `length-rest-remove` -- remove rests
- `length-weight` -- weighted duration distribution
- `length-span` -- fit to a total duration
- `length-legato` -- fill gaps between notes
- `length-staccato` -- shorten with rests
- `length-quantize` -- snap to grid
- `length-rational-quantize` -- quantize to rationals
- `length-divide` -- subdivide durations
- `length-multiply` -- multiply duration values
- `gen-length` -- generate rhythm patterns
- `gen-euclidean` -- Euclidean rhythm generation
- `gen-length-constant` -- constant duration stream
- `gen-length-random` -- random durations
- `gen-length-accumulate` -- accumulative durations

**From Music21:**
- `duration.Duration` -- duration object
- `duration.GraceDuration` -- grace notes
- `duration.Tuplet` -- tuplet handling
- `meter.TimeSignature` -- metrical context
- `meter.MeterSequence` -- hierarchical meter
- `stream.Stream.quantize()` -- quantization

**Complexity: MEDIUM.** Straightforward for basic operations, but metric modulation, interpolation, and polymetric alignment are genuinely complex.

---

## 4. Melodic Transforms

### Table Stakes

| Feature | Why Expected | Complexity | Opusmodus Equivalent | Music21 Equivalent |
|---------|-------------|------------|---------------------|-------------------|
| Retrograde | Reverse entire OMN phrase | Low | `retrograde` | Manual reverse |
| Inversion | Invert pitch contour | Low | `inversion` | Manual |
| Retrograde-inversion | Combined | Low | Composition of functions | Manual |
| Transposition | Shift whole melody | Low | `transpose` | `stream.transpose()` |
| Rotation | Circular shift | Low | `rotate` | Manual |
| Permutation | Reorder notes | Low | `permute` | `itertools.permutations` |
| Augmentation | Stretch durations | Low | `augmentation` | Manual |
| Diminution | Compress durations | Low | `diminution` | Manual |
| Sequence extraction | Get subsequences | Low | `subseq` | Slicing |
| Repetition / Ostinato | Repeat a pattern | Low | `gen-repeat` | Manual |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|------------------|------------|-------|
| Melodic interpolation | Gradual morph between two melodies | High | Opusmodus: `pitch-interpolation` |
| Contour mapping | Apply contour of melody A to pitches of melody B | Medium | Opusmodus: `pitch-contour-map` |
| Melodic ornamentation | Automatically add turns, trills, mordents, passing tones | High | Opusmodus: `pitch-ornament`, style-aware |
| Fragmentation and recombination | Break melody into motifs, recombine | Medium | Opusmodus: `gen-fragment` |
| Interval expansion/compression | Stretch or compress intervals while keeping contour | Medium | Opusmodus: `interval-expansion` |
| Canonic transforms | Generate canon entries (with delay, transposition) | Medium | Opusmodus: `gen-canon` |
| Motivic development | Theme-and-variation engine | High | Combines multiple transforms |
| Melody harmonization | Add chords below/above a melody line | High | Opusmodus: `harmonic-path` / Music21: partial |

### Key Functions to Implement

**From Opusmodus:**
- `retrograde` -- reverse OMN sequence
- `inversion` -- invert melody
- `transpose` -- shift pitch
- `rotate` -- circular rotation of elements
- `permute` -- reorder
- `augmentation` / `diminution` -- temporal scaling
- `gen-fragment` -- fragment extraction
- `gen-repeat` -- repetition
- `gen-trim` -- trim to length
- `gen-join` -- join phrases
- `gen-divide` -- divide phrases
- `gen-swallow` -- merge overlapping notes
- `gen-retrograde` -- retrograde with options
- `gen-invert` -- inversion with options
- `gen-accumulate` -- accumulative transforms
- `pitch-ornament` -- ornamentation
- `pitch-contour` -- contour extraction
- `interval-expansion` -- expand/compress intervals
- `binary-invert` -- binary pattern inversion
- `gen-canon` -- canon generation

**From Music21:**
- `stream.Stream.transpose()` -- transposition
- `stream.Stream.invertDiatonic()` -- diatonic inversion
- `stream.Stream.augmentOrDiminish()` -- temporal scaling
- `analysis.discrete.Ambitus` -- range analysis on melody
- `figuredBass.realizer` -- (partial) harmonization

**Complexity: MEDIUM-HIGH.** Basic transforms are trivial. Ornamentation, interpolation, and harmonization are musically complex.

---

## 5. Harmonic Analysis

### Table Stakes

| Feature | Why Expected | Complexity | Opusmodus Equivalent | Music21 Equivalent |
|---------|-------------|------------|---------------------|-------------------|
| Chord identification from notes | Given {C,E,G} -> "C major" | Medium | `chord-name` | `chord.Chord.pitchedCommonName` |
| Roman numeral analysis | Label chords in key context | High | Limited | `roman.RomanNumeral`, `analysis.floatingKey` |
| Key detection | Determine key of a passage | High | `key-signature` (manual) | `analysis.discrete.KrumhanslSchmuckler` and 4 other algorithms |
| Harmonic rhythm extraction | When do chords change? | Medium | Manual | Partial via analysis module |
| Chord progression identification | Detect common progressions (ii-V-I etc.) | High | Manual | `roman.RomanNumeral` chains |
| Figured bass realization | Given bass + figures -> full chords | High | Limited | `figuredBass.realizer` |
| Secondary dominant detection | V/V, V/vi etc. | High | Manual | `roman.RomanNumeral.secondaryRomanNumeral` |
| Chord inversion detection | Root position, 1st, 2nd, 3rd inversion | Medium | `chord-inversion` | `chord.Chord.inversion()` |
| Chord quality detection | Major, minor, dim, aug, dom7, etc. | Medium | `chord-quality` | `chord.Chord.quality` |
| Non-chord tone identification | Passing tones, neighbor tones, suspensions | High | Manual | Partial via analysis module |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|------------------|------------|-------|
| Functional harmony labeling | T, PD, D functions, not just Roman numerals | High | Goes beyond both source libraries |
| Modulation detection | Where does the key change? | High | Music21: `analysis.floatingKey` is basic |
| Neo-Riemannian operations | P, L, R transforms between triads | Medium | Neither library has comprehensive support |
| Harmonic tension curve | Quantify tension over time | High | Novel feature for Cadenza |
| Jazz chord symbol parsing | Cmaj7#11, G7b9 etc. | Medium | Music21: `harmony.ChordSymbol` |
| Lead sheet realization | Chord symbols -> voiced chords | High | Music21: `harmony.ChordSymbol.realize()` partial |

### Key Functions to Implement

**From Opusmodus:**
- `chord-name` -- identify chord
- `chord-inversion` -- detect/set inversion
- `chord-quality` -- major/minor/dim/aug
- `harmonic-path` -- generate harmonic progressions
- `harmonic-progression` -- build progressions from Roman numerals
- `chord-interval-add` -- add intervals to chords
- `chord-interval-remove` -- remove intervals
- `tonality-map` -- constrain pitches to harmony

**From Music21:**
- `analysis.discrete.KrumhanslSchmuckler` -- key detection (Krumhansl-Schmuckler algorithm)
- `analysis.discrete.BellmanBudge` -- key detection (Bellman-Budge)
- `analysis.discrete.TemperleyKostkaPayne` -- key detection
- `analysis.discrete.SimpleWeights` -- key detection
- `analysis.discrete.AardenEssen` -- key detection
- `analysis.floatingKey.KeyAnalyzer` -- windowed key detection
- `roman.RomanNumeral` -- Roman numeral representation
- `roman.romanNumeralFromChord` -- chord to Roman numeral
- `figuredBass.realizer.FiguredBassLine` -- figured bass realization
- `figuredBass.rules.Rules` -- voice leading rules for realization
- `harmony.ChordSymbol` -- jazz/pop chord symbols
- `chord.Chord.pitchedCommonName` -- chord naming
- `chord.Chord.root()` -- root detection
- `chord.Chord.bass()` -- bass note
- `chord.Chord.inversion()` -- inversion number
- `chord.Chord.closedPosition()` -- close voicing
- `chord.Chord.quality` -- chord quality string

**Complexity: HIGH.** Key detection algorithms, Roman numeral analysis, and modulation detection are research-level problems. Music21's implementations are the gold standard in Python.

---

## 6. Counterpoint

### Table Stakes

| Feature | Why Expected | Complexity | Opusmodus Equivalent | Music21 Equivalent |
|---------|-------------|------------|---------------------|-------------------|
| First species counterpoint | Note-against-note, consonant intervals only | High | Limited built-in | Limited |
| Second species counterpoint | Two notes against one, passing tones allowed | High | Limited built-in | Limited |
| Third species counterpoint | Four notes against one, more ornamental | High | Limited built-in | Limited |
| Fourth species counterpoint | Syncopation, suspensions, tied notes | High | Limited built-in | Limited |
| Fifth species counterpoint | Free/florid, combining all species | Very High | Limited built-in | Limited |
| Parallel 5ths/octaves detection | Must catch these violations | Medium | Manual | `voiceLeading.VoiceLeadingQuartet.parallelFifth()` |
| Direct/hidden 5ths/octaves detection | Must catch these too | Medium | Manual | `voiceLeading.VoiceLeadingQuartet.hiddenFifth()` |
| Voice crossing detection | Voices should not cross | Low | Manual | `voiceLeading.VoiceLeadingQuartet.voiceCrossing()` |
| Counterpoint rule validation | Check if a counterpoint follows rules | High | Manual | Partial |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|------------------|------------|-------|
| Automatic counterpoint generation | Given cantus firmus, generate valid counterpoint | Very High | This is the killer feature for Cadenza |
| Style-configurable rules | Strict Fux vs free vs Renaissance vs Baroque | High | Rule engine with configurable profiles |
| Multi-voice counterpoint (3+ voices) | Beyond two-part writing | Very High | Exponentially harder constraint satisfaction |
| Imitative counterpoint / fugue exposition | Generate entries of a subject in sequence | Very High | Canon/fugue generation |
| Invertible counterpoint | Counterpoint that works when voices swap | Very High | Double/triple counterpoint at the octave, 10th, 12th |

### Detailed Counterpoint Rules (must be formally encoded)

**First Species Rules:**
1. Begin and end on perfect consonance (unison, 5th, octave)
2. Contrary motion preferred over similar, parallel, or oblique
3. No parallel 5ths or octaves (consecutive perfect consonances of same type)
4. No direct/hidden 5ths or octaves (approaching perfect consonance by similar motion)
5. No voice crossing (upper voice goes below lower, or vice versa)
6. No unisons except at beginning and end
7. Only consonant intervals: unison, 3rd, 5th, 6th, octave (imperfect consonances preferred)
8. No augmented or diminished intervals melodically (no tritone leaps)
9. Climax: single highest point in the counterpoint line
10. Stepwise motion preferred; leaps of 4th or 5th acceptable, octave rare
11. Leaps larger than a 3rd should be followed by stepwise motion in opposite direction
12. No more than 3 consecutive parallel 3rds or 6ths (monotony)
13. Variety of motion types required
14. Range should not exceed a 10th (for vocal counterpoint)
15. Penultimate bar: leading tone in upper voice, 2nd scale degree in lower voice

**Second Species Additional Rules:**
16. Strong beats must be consonant with the cantus firmus
17. Weak beats may be dissonant IF approached and left by step (passing tones)
18. No unison on strong beats except first and last bars
19. Variety of rhythmic figures (not all the same pattern)
20. The first note of the counterpoint may be a half rest followed by a half note

**Third Species Additional Rules:**
21. First note of each bar must be consonant
22. Neighbor tones allowed (approach by step, leave by step returning to same note)
23. Cambiata (changing tones) allowed: consonance -> step down (dissonant) -> leap of 3rd down -> stepwise resolution
24. Double neighbor figures allowed (upper and lower neighbor in sequence)
25. No more than 4-5 notes in the same direction before changing

**Fourth Species Additional Rules:**
26. Syncopated rhythm (tied notes across barlines)
27. Suspensions: prepared consonance -> held over barline (becomes dissonant) -> resolves down by step
28. Suspension types allowed: 7-6, 4-3, 9-8 (upper voice); 2-3 (lower voice)
29. Chain suspensions create characteristic descending patterns
30. If suspension not possible, revert to first species for that bar

**Fifth Species (free counterpoint):**
31. Combines elements of all four previous species
32. Variety of rhythmic motion required (quarter notes, half notes, whole notes, suspensions)
33. Musical coherence and phrase shape required
34. May begin with any species
35. Suspensions should resolve properly even in mixed context

### Key Functions to Implement

**New (neither Opusmodus nor Music21 has comprehensive implementations):**
- `counterpoint.validate(cantus_firmus, counterpoint, species=1)` -- validate against species rules
- `counterpoint.generate(cantus_firmus, species=1, position='above')` -- generate counterpoint
- `counterpoint.violations(cantus_firmus, counterpoint)` -- list all rule violations with explanations
- `counterpoint.suggest_next_note(cantus_firmus, partial_counterpoint)` -- step-by-step helper
- `counterpoint.generate_cantus_firmus(length=12, mode='dorian')` -- generate a valid cantus firmus
- `counterpoint.Species` -- enum for species selection
- `counterpoint.RuleSet` -- configurable rule profile (Fux strict, Renaissance, free)
- `counterpoint.analyze_motion(voice_a, voice_b)` -- classify motion between each pair of notes

**From Music21 (partial support only):**
- `voiceLeading.VoiceLeadingQuartet` -- analyze intervals between voice pairs
- `voiceLeading.VoiceLeadingQuartet.parallelFifth()`
- `voiceLeading.VoiceLeadingQuartet.parallelOctave()`
- `voiceLeading.VoiceLeadingQuartet.hiddenFifth()`
- `voiceLeading.VoiceLeadingQuartet.hiddenOctave()`
- `voiceLeading.VoiceLeadingQuartet.antiParallelMotion()`
- `voiceLeading.VoiceLeadingQuartet.obliqueMotion()`
- `voiceLeading.VoiceLeadingQuartet.contraryMotion()`
- `voiceLeading.VoiceLeadingQuartet.similarMotion()`
- `voiceLeading.VoiceLeadingQuartet.parallelMotion()`

**Complexity: VERY HIGH.** This is the hardest category. Counterpoint generation is a constraint-satisfaction problem. Fifth species is open-ended. Multi-voice writing is exponentially harder. This is a core differentiator and worth the investment.

---

## 7. Voice Leading

### Table Stakes

| Feature | Why Expected | Complexity | Opusmodus Equivalent | Music21 Equivalent |
|---------|-------------|------------|---------------------|-------------------|
| Smooth voice leading | Minimize total movement between chords | Medium | `chord-closest-path` | `voiceLeading.VoiceLeadingQuartet` |
| Parallel motion detection | Detect parallel 3rds, 5ths, 6ths, octaves | Low | Manual | `voiceLeading.VoiceLeadingQuartet.parallelMotion()` |
| Contrary motion detection | Detect voices moving in opposite directions | Low | Manual | `voiceLeading.VoiceLeadingQuartet.contraryMotion()` |
| Oblique motion detection | One voice stationary | Low | Manual | `voiceLeading.VoiceLeadingQuartet.obliqueMotion()` |
| Similar motion detection | Same direction, different intervals | Low | Manual | `voiceLeading.VoiceLeadingQuartet.similarMotion()` |
| Voice crossing detection | Check if voices cross | Low | Manual | `voiceLeading.VoiceLeadingQuartet.voiceCrossing()` |
| Voice overlap detection | Voice moves past previous position of another | Low | Manual | Partial |
| Common tone retention | Hold common tones between chords | Medium | `chord-common-tone` | Manual |
| Part writing rules (SATB) | Four-part voice leading | High | Limited | `figuredBass.rules.Rules` |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|------------------|------------|-------|
| Automatic chord voicing | Given chord symbol + previous voicing -> optimal next voicing | High | Key for notation software integration |
| SATB realization from Roman numerals | Full four-part writing | Very High | Music21 figuredBass is partial |
| Neo-Riemannian voice leading | P, L, R transformations with minimal pitch motion | Medium | Valued in academia and contemporary composition |
| Voice leading distance metric | Quantify "smoothness" of a progression numerically | Medium | Useful for algorithmic composition |
| Optimal voice leading solver | Find minimal-motion voicing path for entire progression | High | Constraint optimization problem |

### Key Functions to Implement

**From Music21:**
- `voiceLeading.VoiceLeadingQuartet` -- core two-voice analysis object
- `voiceLeading.ThreeNoteLinearSegment` -- three-note melodic patterns
- `voiceLeading.Verticality` -- simultaneous notes analysis
- `figuredBass.realizer` -- realize figured bass (includes voice leading rules)
- `figuredBass.rules.Rules` -- configurable rules for realization

**From Opusmodus:**
- `chord-closest-path` -- minimal voice motion between chords
- `chord-voice-leading` -- explicit voice leading connections
- `chord-inversion-voice-leading` -- use inversions for smoother leading
- `chord-common-tone` -- retain common tones

**New:**
- `voiceleading.smooth_connect(chord_a, chord_b, voices=4)` -- smoothest connection
- `voiceleading.realize_progression(roman_numerals, key, soprano=None)` -- SATB realization
- `voiceleading.analyze_motion(voice_a, voice_b)` -- classify motion type at each point
- `voiceleading.score_smoothness(progression)` -- numeric smoothness metric
- `voiceleading.find_violations(score, rules)` -- check all voice leading rules
- `voiceleading.neo_riemannian(chord, operation)` -- P, L, R transforms

**Complexity: HIGH.** Smooth voice leading is well-understood in theory. Implementing it as a general solver that handles all edge cases (doubled roots, resolution of 7ths, cross-relations, spacing rules) is hard engineering.

---

## 8. Scale / Mode Library

### Table Stakes

| Feature | Why Expected | Complexity | Opusmodus Equivalent | Music21 Equivalent |
|---------|-------------|------------|---------------------|-------------------|
| Major scale | Foundational | Low | Built-in | `scale.MajorScale` |
| Natural minor scale | Foundational | Low | Built-in | `scale.MinorScale` |
| Harmonic minor | Common | Low | Built-in | `scale.HarmonicMinorScale` |
| Melodic minor (asc/desc) | Common | Low | Built-in | `scale.MelodicMinorScale` |
| Church modes (all 7) | Ionian through Locrian | Low | Built-in | `scale.DorianScale`, etc. |
| Pentatonic (major/minor) | Very common | Low | Built-in | `scale.MajorPentatonicScale` |
| Blues scale | Common | Low | Built-in | Custom or built-in |
| Chromatic scale | All 12 tones | Low | Built-in | `scale.ChromaticScale` |
| Whole tone scale | Common in impressionist music | Low | Built-in | `scale.WholeToneScale` |
| Octatonic (diminished) scale | Common in 20th century music | Low | Built-in | `scale.OctatonicScale` |
| Scale degree lookup | "3rd degree of D major" -> F# | Low | `scale-degree` | `scale.Scale.pitchFromDegree()` |
| Scale membership test | "Is F# in G major?" -> yes | Low | `scale-member?` | `pitch in scale.pitches` |
| Scale from pitches | Identify scale given pitches | Medium | Manual | `scale.Scale.match()` (partial) |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|------------------|------------|-------|
| Non-Western scales | Maqamat, ragas, gamelan pelog/slendro | Medium | Opusmodus has some; Music21 limited |
| Messiaen modes of limited transposition | All 7 modes | Low | Well-defined mathematically |
| All modes of melodic/harmonic minor | Full rotation sets | Medium | Opusmodus strength |
| Scale interpolation | Blend between two scales | High | Novel |
| Bebop scales | Dominant, major, minor, Dorian | Low | Jazz theory standard |

### Comprehensive Scale Inventory (target: 100+ scales)

**Standard Western (7):** Major, Natural Minor, Harmonic Minor, Melodic Minor (asc), Melodic Minor (desc), Chromatic, Whole Tone

**Modes of Major (7):** Ionian, Dorian, Phrygian, Lydian, Mixolydian, Aeolian, Locrian

**Modes of Melodic Minor (7):** Jazz Minor, Dorian b2 (Phrygian #6), Lydian Augmented, Lydian Dominant (Overtone), Mixolydian b6 (Hindu/Aeolian Dominant), Locrian #2 (Half-Diminished), Altered (Super Locrian)

**Modes of Harmonic Minor (7):** Harmonic Minor, Locrian #6, Ionian #5 (Augmented Major), Dorian #4 (Ukrainian Dorian/Romanian), Phrygian Dominant (Spanish/Jewish), Lydian #2, Ultra Locrian (Altered Diminished)

**Modes of Harmonic Major (7):** Harmonic Major, Dorian b5, Phrygian b4, Lydian b3, Mixolydian b2, Lydian Augmented #2, Locrian bb7

**Pentatonic/Blues (6):** Major Pentatonic, Minor Pentatonic, Blues (minor), Major Blues, Dominant Pentatonic, Suspended Pentatonic

**Symmetric (6):** Whole Tone, Octatonic Half-Whole, Octatonic Whole-Half, Augmented (Whole-Half), Augmented Inverse (Half-Whole), Tritone

**Messiaen Modes (7):** Mode 1 (=Whole Tone), Mode 2 (=Octatonic), Mode 3, Mode 4, Mode 5, Mode 6, Mode 7

**Bebop (4):** Bebop Dominant, Bebop Major, Bebop Minor, Bebop Dorian

**Other Western (15+):** Hungarian Minor, Hungarian Major, Neapolitan Minor, Neapolitan Major, Double Harmonic (Byzantine/Arabic), Enigmatic, Prometheus, Persian, Spanish 8-Tone, Flamenco, Gypsy, Leading Whole Tone, Lydian Minor, Phrygian Major (=Phrygian Dominant), Locrian Major

**Non-Western (10+):** Japanese In, Japanese Yo, Hirajoshi, Kumoi, Iwato, Balinese Pelog, Balinese Slendro, Chinese, Egyptian, Mongolian, Indian raga scales (Bhairav, Yaman, Kafi, etc.)

### Key Functions to Implement

**From Opusmodus:**
- Scale definition system supporting arbitrary interval patterns
- `make-scale` -- create scale from intervals
- `scale-to-pitch` -- generate pitches from scale in a range
- `scale-transpose` -- transpose entire scale
- `scale-degree` -- get specific degree
- `scale-member?` -- membership test
- `scale-chord` -- harmonize a scale degree

**From Music21:**
- `scale.Scale` -- base class
- `scale.ConcreteScale` -- scale rooted on specific pitch
- `scale.AbstractScale` -- scale as interval pattern
- `scale.Scale.getPitches()` -- get all pitches in range
- `scale.Scale.pitchFromDegree()` -- specific degree
- `scale.Scale.getScaleDegreeFromPitch()` -- reverse lookup
- `scale.Scale.next()` / `scale.Scale.nextPitch()` -- next pitch in scale
- `scale.Scale.deriveRanked()` -- find closest matching scale

**Complexity: LOW-MEDIUM.** Scales are fundamentally interval pattern arrays. The library is large but each individual scale is trivial to define. The interesting complexity is in operations ON scales (scale detection, quantization to scale).

---

## 9. Chord Library

### Table Stakes

| Feature | Why Expected | Complexity | Opusmodus Equivalent | Music21 Equivalent |
|---------|-------------|------------|---------------------|-------------------|
| Major/minor triads | Foundational | Low | Built-in | `chord.Chord` |
| Diminished/augmented triads | Common | Low | Built-in | `chord.Chord` |
| Dominant 7th | Foundational harmony | Low | Built-in | `chord.Chord` |
| Major 7th, minor 7th | Common extended chords | Low | Built-in | `chord.Chord` |
| Half-diminished 7th (m7b5) | Common in jazz and classical | Low | Built-in | `chord.Chord` |
| Diminished 7th | Common in classical harmony | Low | Built-in | `chord.Chord` |
| Augmented 7th chords | Less common but expected | Low | Built-in | `chord.Chord` |
| 9th, 11th, 13th chords | Extended harmony | Low | Built-in | `chord.Chord` |
| Suspended chords (sus2, sus4) | Common in pop/rock | Low | Built-in | `chord.Chord` |
| Added tone chords (add9, add11) | Common in pop/jazz | Low | Built-in | `chord.Chord` |
| All inversions | 1st, 2nd, 3rd, etc. | Low | `chord-inversion` | `chord.Chord.inversion()` |
| Chord from Roman numeral | "IV in C major" -> F-A-C | Medium | `harmonic-progression` | `roman.RomanNumeral('IV', 'C')` |
| Chord symbol parsing | "Cmaj7", "Dm7b5", "G7#9" | Medium | Limited | `harmony.ChordSymbol('Cmaj7')` |
| Chord from intervals | Build chord from stacked intervals | Low | `chord-interval` | Manual |
| Root identification | Given notes, find root | Medium | `chord-root` | `chord.Chord.root()` |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|------------------|------------|-------|
| Chord voicing library | Common voicings for each chord type (close, open, spread) | Medium | Useful for auto-arrangement |
| Shell voicings (jazz) | 3rds and 7ths only | Low | Jazz arranging essential |
| Drop voicings (drop-2, drop-3, drop-2-4) | Guitar/big band voicings | Medium | Common in jazz arranging |
| Cluster chords | Seconds-based harmony | Low | 20th century music |
| Quartal/quintal chords | 4ths/5ths-based harmony | Low | Modern/jazz harmony |
| Polychords | Superimposed triads (e.g., C/F#) | Medium | 20th century / Stravinsky |
| Chord substitution engine | Tritone sub, related ii, diatonic sub, etc. | High | Jazz reharmonization |

### Comprehensive Chord Type Inventory

**Triads (6):** Major, Minor, Diminished, Augmented, Suspended 2nd, Suspended 4th

**Seventh chords (8):** Major 7th, Dominant 7th, Minor 7th, Minor-Major 7th, Half-Diminished 7th, Diminished 7th, Augmented 7th, Augmented Major 7th

**Extended chords (9):** Dominant 9th, Major 9th, Minor 9th, Dominant 11th, Major 11th, Minor 11th, Dominant 13th, Major 13th, Minor 13th

**Altered dominants (7):** 7b5 (Lydian Dominant), 7#5 (Augmented Dominant), 7b9, 7#9 (Hendrix chord), 7#11, 7b13, 7alt (all alterations)

**Added tones (6):** add9, add11, add13, 6 (major 6th), minor 6th, 6/9

**Special/classical (5):** Power chord (5th only), Italian Augmented 6th, French Augmented 6th, German Augmented 6th, Neapolitan 6th

**Other (4):** Tristan chord, Mystic chord (Scriabin), Petrushka chord, Elektra chord

### Key Functions to Implement

**From Opusmodus:**
- `make-chord` -- construct chord from pitches
- `chord-interval` -- chord from intervals
- `chord-inversion` -- set/detect inversion
- `chord-root` -- find root
- `chord-quality` -- major/minor/dim/aug quality
- `chord-name` -- full chord name
- `chord-member?` -- pitch membership test
- `chord-transpose` -- transpose chord
- `chord-closest-path` -- voice leading between chords
- `chord-series` -- generate chord sequences
- `chord-interval-add` / `chord-interval-remove` -- modify chord structure
- `chord-voice-leading` -- smooth voice connections

**From Music21:**
- `chord.Chord` -- chord object
- `chord.Chord.root()` -- root detection (Tertian stacking algorithm)
- `chord.Chord.bass()` -- bass note
- `chord.Chord.inversion()` -- inversion number
- `chord.Chord.closedPosition()` -- closed voicing
- `chord.Chord.openPosition()` -- open voicing
- `chord.Chord.commonName` -- common name
- `chord.Chord.pitchedCommonName` -- name with root
- `chord.Chord.quality` -- quality string
- `chord.Chord.forteClass` -- Forte number (set theory crossover)
- `chord.Chord.intervalVector` -- interval vector (set theory crossover)
- `chord.Chord.isTriad()` / `chord.Chord.isSeventh()` -- type checks
- `chord.Chord.isConsonant()` -- consonance test
- `harmony.ChordSymbol` -- pop/jazz chord symbol parsing
- `harmony.ChordSymbol.figure` -- chord symbol string
- `roman.RomanNumeral` -- Roman numeral -> chord mapping

**Complexity: LOW-MEDIUM.** Chord types are data (stacked intervals). The interesting complexity is in root identification (ambiguous cases), voicing algorithms, and substitution logic.

---

## 10. Set Theory (Pitch-Class Set Theory)

### Table Stakes

| Feature | Why Expected | Complexity | Opusmodus Equivalent | Music21 Equivalent |
|---------|-------------|------------|---------------------|-------------------|
| Pitch class representation | 0-11 integer notation (C=0) | Low | `pitch-to-pc` | `pitch.Pitch.pitchClass` |
| Pitch class set (unordered) | Set of PCs: {0, 4, 7} | Low | Sets in Lisp | `chord.Chord.pitchClasses` |
| Normal form | Lexicographically smallest rotation | Medium | `normal-form` | `chord.Chord.normalOrder` |
| Prime form | Most compact transposition/inversion | Medium | `prime-form` | `chord.Chord.primeForm` |
| Interval vector | Six-element vector counting each interval class | Medium | `interval-vector` | `chord.Chord.intervalVector` |
| Forte number | Set-class label (e.g., 3-11 = major/minor triad) | Low | `forte-number` | `chord.Chord.forteClass` |
| Transposition (Tn) | Transpose all PCs by n mod 12 | Low | PC transposition | Manual |
| Inversion (TnI) | Invert then transpose | Low | PC inversion | Manual |
| Set complement | PCs not in the set (mod 12) | Low | `complement` | Manual |
| Set intersection/union/difference | Combine/compare sets | Low | Set operations | Manual |
| Subset/superset relations | Is set A a subset of set B? | Low | `subset?` | Manual |
| Z-relation | Sets sharing interval vector but not prime form | Medium | `z-relation` | `chord.Chord.getZRelation()` |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|------------------|------------|-------|
| Complete Forte table (all 224 set classes) | Full reference lookup from any representation | Medium | One-time data + lookup functions |
| Set class similarity metrics | Rp, R0, R1, R2 relations (Forte) | Medium | Academic analysis tool |
| Inclusion lattice | Graph of which sets contain which subsets | High | Visualization/query structure |
| Set complexes (K and Kh) | Forte's set-complex relations | High | Deep academic feature |
| Atonal voice leading distances | Minimal-distance PC-set mapping (Straus, Callender, Quinn) | High | Contemporary music theory |

### Key Functions to Implement

**From Opusmodus:**
- `integer-to-pitch` / `pitch-to-integer` -- conversion between PC and pitch
- `prime-form` -- compute prime form
- `normal-form` -- compute normal form (Rahn algorithm)
- `interval-vector` -- compute interval vector
- `complement` -- set complement (mod 12)
- `transpose-pc` -- pitch-class transposition
- `invert-pc` -- pitch-class inversion

**From Music21:**
- `chord.Chord.normalOrder` -- normal order
- `chord.Chord.primeForm` -- prime form
- `chord.Chord.intervalVector` -- interval vector
- `chord.Chord.forteClass` -- Forte number string
- `chord.Chord.forteClassNumber` -- numeric Forte number
- `chord.Chord.hasZRelation` -- Z-relation check
- `chord.Chord.getZRelation()` -- get Z-related set

**Complexity: MEDIUM.** Algorithms for normal form and prime form are well-documented (Rahn 1980, Forte 1973). The complete Forte table is a one-time data compilation effort. Similarity metrics and set complexes are the harder parts.

---

## 11. Serial / 12-Tone Techniques

### Table Stakes

| Feature | Why Expected | Complexity | Opusmodus Equivalent | Music21 Equivalent |
|---------|-------------|------------|---------------------|-------------------|
| Tone row creation | Define a 12-tone row (ordered PC set) | Low | `make-tone-row` | `serial.ToneRow` |
| Row transposition (T0-T11) | All 12 transpositions (P0-P11) | Low | `row-transpose` | `serial.ToneRow` methods |
| Row inversion (I0-I11) | Mirror intervals | Low | `row-invert` | `serial.ToneRow` methods |
| Row retrograde (R) | Reverse order | Low | `row-retrograde` | `serial.ToneRow` methods |
| Row retrograde-inversion (RI) | Combined transform | Low | Composition of functions | Composition |
| 12x12 matrix generation | Full P/I/R/RI matrix | Medium | `row-matrix` | `serial.rowToMatrix()` |
| Row form identification | Given notes, identify which form (P3, I7, etc.) | Medium | Manual | Manual |
| Row segmentation | Divide into trichords, tetrachords, hexachords | Low | `row-segment` | Manual |
| All-interval row detection | Does row contain all 11 interval classes? | Low | `all-interval-row?` | `serial.ToneRow.isAllInterval()` |
| Combinatoriality check | Hexachordal combinatoriality (I, R, RI) | Medium | Manual | Manual |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|------------------|------------|-------|
| Row generator from constraints | "Generate a row where the first hexachord is 6-Z44" | High | Constraint solver |
| Rotational arrays | Stravinsky-style rotational technique | Medium | Specialized late Stravinsky |
| Integral serialism | Serialize pitch, rhythm, dynamics, articulation simultaneously | High | Total serialism (Boulez, Babbitt) |
| Multiplicative operations (M5, M7) | Pitch-class multiplication | Low | Mathematical transform |
| Historical row database | Webern Op.21, Berg Violin Concerto, Schoenberg Op.25, etc. | Low | Data compilation |
| Derived rows | Rows built from transpositions of a trichord/tetrachord | Medium | Webern technique |

### Key Functions to Implement

**From Opusmodus:**
- `make-tone-row` -- create row from PC list
- `row-transpose` -- transpose row (Tn)
- `row-invert` -- invert row (TnI)
- `row-retrograde` -- reverse row
- `row-matrix` -- generate 12x12 matrix
- `row-rotation` -- rotate row
- `row-segment` -- extract segments (trichords, tetrachords, hexachords)

**From Music21:**
- `serial.ToneRow` -- tone row object
- `serial.TwelveToneRow` -- specifically 12-tone row
- `serial.HistoricalTwelveToneRow` -- database of famous rows
- `serial.rowToMatrix()` -- matrix generation
- `serial.ToneRow.isAllInterval()` -- all-interval check
- `serial.pcToToneRow()` -- convert PC list to tone row

**Complexity: LOW-MEDIUM.** Most operations are array manipulations mod 12. Matrix generation is a well-defined algorithm. Constraint-based row generation is the only genuinely hard part.

---

## 12. Pattern / Rhythm Generation

### Table Stakes

| Feature | Why Expected | Complexity | Opusmodus Equivalent | Music21 Equivalent |
|---------|-------------|------------|---------------------|-------------------|
| Euclidean rhythm generation | Distribute n onsets evenly in k slots | Medium | `gen-euclidean` | Not built-in |
| Repeat/loop | Repeat a pattern n times | Low | `gen-repeat` | Manual |
| Cycle | Cyclic repetition (wrap around) | Low | `gen-cycle` | `itertools.cycle` |
| Pattern rotation | Circular shift of onset positions | Low | `rotate` | Manual |
| Pattern concatenation | Join patterns sequentially | Low | `gen-join` | List concatenation |
| Ostinato | Repeating pattern with optional variation | Medium | `gen-ostinato` | Manual |
| Isorhythm | Repeating rhythm (talea) with independent repeating pitches (color) | Medium | Talea/color functions | Manual |
| Random generation | Random note/rhythm from weighted pool | Low | `gen-random`, `gen-weighted` | `random.choice` / `random.choices` |
| Pattern transposition | Apply same pattern at different pitch levels | Low | `gen-transpose` | Manual |
| Sequence (melodic) | Repeat pattern at successive scale degrees | Medium | `gen-sequence` | Manual |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|------------------|------------|-------|
| Tala (Indian rhythmic cycles) | Non-Western rhythmic system support | Medium | Unique differentiator |
| Aksak (additive/irregular meters) | 7/8, 11/8, 13/8 Balkan-style patterns | Low | Data + generation |
| Polyrhythm generation | Two independent rhythms (3:4, 5:7, etc.) | Medium | Opusmodus strength |
| Phasing (Reich-style) | Two patterns gradually drifting apart | Medium | Process music technique |
| Rhythmic canons | Time-delayed rhythmic patterns | Medium | Combines canon + rhythm |
| Fibonacci/geometric rhythms | Durations from mathematical sequences | Low | Novel |
| Binary pattern operations | AND, OR, XOR on onset patterns | Low | Novel, useful for rhythm manipulation |

### Key Functions to Implement

**From Opusmodus:**
- `gen-repeat` -- repeat pattern n times
- `gen-cycle` -- cyclic repetition
- `gen-trim` -- trim to specified length
- `gen-join` -- concatenate patterns
- `gen-divide` -- divide pattern into segments
- `gen-random` -- random selection from pool
- `gen-weighted` -- weighted random
- `gen-euclidean` -- Euclidean rhythms (Bjorklund algorithm)
- `gen-binary` -- binary pattern generation
- `gen-binary-invert` -- invert binary pattern
- `gen-binary-rotate` -- rotate binary pattern
- `gen-accumulate` -- accumulate values
- `gen-fibonacci` -- Fibonacci-based generation
- `gen-integer-series` -- integer series (arithmetic, geometric)
- `gen-sine` / `gen-cosine` -- waveform-based parameter curves
- `gen-tendency` -- tendency mask (evolving range over time)
- `gen-walk` -- random walk
- `gen-zigzag` -- alternating direction walk
- `gen-orbit` -- orbital/attractor patterns
- `gen-white-noise` / `gen-pink-noise` / `gen-brown-noise` -- noise distributions applied to musical parameters
- `gen-sort` -- sort values
- `gen-filter` -- filter by predicate
- `gen-merge` -- merge multiple streams

**Complexity: MEDIUM.** Individual algorithms are well-documented. Euclidean rhythm is a single function (Bjorklund). The breadth of generators makes this a significant implementation effort but no single item is very hard.

---

## 13. Batch Operations

### Table Stakes

| Feature | Why Expected | Complexity | Opusmodus Equivalent | Music21 Equivalent |
|---------|-------------|------------|---------------------|-------------------|
| Apply articulation pattern | Every downbeat gets accent, alternating staccato/legato | Medium | OMN attribute assignment | `stream.recurse()` + filter |
| Apply dynamic pattern | Crescendo/diminuendo across phrase | Medium | OMN attribute assignment | `stream.recurse()` + filter |
| Apply expression marks | Add slurs, hairpins by pattern | Medium | OMN attribute assignment | `spanner.Slur`, etc. |
| Map function over notes | Apply any transform to each note | Low | `mapcar` (Lisp native) | Python `map` / list comprehension |
| Filter notes by predicate | Select notes matching criteria | Low | `remove-if` (Lisp native) | List comprehension |
| Replace by pattern | Replace every occurrence of X with Y | Medium | `omn-replace` | `stream.replace()` (partial) |
| Transpose selection | Transpose only selected notes | Low | Combination functions | `stream.transpose()` on subset |
| Velocity/dynamic curve | Apply velocity envelope (linear, exponential) to phrase | Medium | Velocity patterns in OMN | Manual |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|------------------|------------|-------|
| Rule-based batch transform | "Every note above C5 gets staccato" -- DSL for rules | Medium | Notation software killer feature |
| Pattern-aware operations | Recognize motif occurrences, transform all instances | High | Requires motif matching |
| Cross-voice batch ops | Apply rule across all voices simultaneously | Medium | Important for orchestral work |
| Undo/history stack | Track transforms for undo capability | Medium | Important for interactive use from notation software |
| Conditional chaining | "If note is on beat 1 AND in top voice, add accent" | Medium | Composable predicates |

### Key Functions to Implement

**From Opusmodus:**
- `omn-replace` -- replace OMN elements by criteria
- `omn-merge` -- merge multiple OMN streams
- `omn-component` -- extract specific component (pitch, duration, velocity, articulation)
- `assemble-seq` -- assemble sequences from components
- `velocity-map` -- map velocity values
- `articulation-map` -- map articulation values
- `length-map` -- map duration values
- `pitch-map` -- map pitch values

**New (Cadenza-specific):**
- `batch.apply_pattern(phrase, pattern, attribute)` -- apply repeating pattern of attribute values
- `batch.crescendo(phrase, start_dynamic, end_dynamic)` -- apply crescendo
- `batch.diminuendo(phrase, start_dynamic, end_dynamic)` -- apply diminuendo
- `batch.accent_every(phrase, n, offset=0)` -- accent every nth note
- `batch.slur_groups(phrase, group_size)` -- add slurs over groups
- `batch.filter(phrase, predicate)` -- filter notes by predicate
- `batch.transform_if(phrase, predicate, transform)` -- conditional transform
- `batch.map(phrase, transform)` -- apply transform to every note
- `batch.reduce(phrase, combiner)` -- reduce phrase to single value

**Complexity: MEDIUM.** Conceptually straightforward but requires a clean, composable API design. The predicate/rule DSL needs careful thought to be both powerful and usable.

---

## 14. Algorithmic Composition

### Table Stakes

| Feature | Why Expected | Complexity | Opusmodus Equivalent | Music21 Equivalent |
|---------|-------------|------------|---------------------|-------------------|
| Markov chain (1st order) | Generate sequences from transition probability table | Medium | `gen-markov` | Not built-in |
| Markov chain (nth order) | Higher-order chains for more structure | Medium | `gen-markov` with order param | Not built-in |
| L-system string generation | Lindenmayer systems mapped to music | Medium | `gen-l-system` | Not built-in |
| Cellular automata (1D) | Rule-based pattern generation (Wolfram rules) | Medium | `gen-cellular-automata` | Not built-in |
| Probability distributions | Gaussian, uniform, exponential for parameter gen | Low | `gen-random`, `gen-weighted` | Python `random` / `numpy` |
| Constraint-based generation | Generate music satisfying a set of rules | High | Various constrained generators | Not built-in |
| Random walk | Stepwise random motion through pitch/rhythm space | Low | `gen-walk` | Not built-in |
| Tendency masks | Define evolving pitch/dynamic range over time | Medium | `gen-tendency` | Not built-in |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|------------------|------------|-------|
| Genetic algorithms for composition | Evolve phrases toward fitness criteria | Very High | Novel for a notation-focused library |
| Stochastic music (Xenakis-style) | Probability clouds, stochastic distributions | High | Specialized but impressive |
| Process music generation | Phasing, additive, subtractive (Reich, Glass) | Medium | Minimal music techniques |
| Spectral composition tools | Derive pitches from overtone series of a fundamental | High | Spectral music school |
| Fractal/self-similar generation | Self-similar structures at multiple time scales | High | Mathematically interesting |
| Algorithmic orchestration | Distribute a melody across instruments by rules | Very High | Very complex; defer |
| Canon/fugue generation | Generate canonic/fugal entries from subject | Very High | Combines counterpoint + serial |

### Key Functions to Implement

**From Opusmodus (this is Opusmodus's strongest category):**
- `gen-markov` -- Markov chain generation (pitch, rhythm, or any parameter)
- `gen-markov-from-list` -- build Markov chain from example data
- `gen-l-system` -- L-system generation with musical mapping
- `gen-cellular-automata` -- 1D cellular automata (all 256 Wolfram rules)
- `gen-probability` -- probability-based selection
- `gen-tendency` -- tendency mask (min/max range evolving over time)
- `gen-white-noise` / `gen-pink-noise` / `gen-brown-noise` -- noise-shaped distributions
- `gen-sine` / `gen-cosine` -- sinusoidal parameter curves
- `gen-accumulate` -- accumulative generation
- `gen-orbit` -- orbital/attractor-based patterns
- `gen-fibonacci` -- Fibonacci sequence to music
- `gen-integer-series` -- arithmetic, geometric, triangular, etc.
- `gen-walk` -- random walk (constrained or unconstrained)
- `gen-zigzag` -- zigzag walk patterns
- `gen-sort` -- sorted generation
- `gen-trim` -- trim to length
- `gen-swallow` -- merge overlapping values
- `gen-merge` -- merge streams
- `gen-filter` -- filter results
- `gen-eval` -- evaluate arbitrary expressions in generation
- `tonality-map` -- constrain algorithmic output to a key/scale
- `ambitus-map` -- constrain to pitch range
- `velocity-map` -- map to dynamic range
- `do-timeline` -- execute operations along a timeline

**Complexity: MEDIUM-HIGH.** Individual algorithms are well-documented in computer music literature. The challenge is (a) making them compose well together, (b) producing musically useful output rather than random noise, and (c) providing the constraint/mapping tools (tonality-map, ambitus-map) that make raw algorithmic output actually musical.

---

## 15. Analysis

### Table Stakes

| Feature | Why Expected | Complexity | Opusmodus Equivalent | Music21 Equivalent |
|---------|-------------|------------|---------------------|-------------------|
| Ambitus (range) | Highest and lowest pitch in passage | Low | `ambitus` | `analysis.discrete.Ambitus` |
| Contour (melodic) | Ascending/descending/stationary shape | Low | `pitch-contour` | Partial |
| Interval histogram | Distribution of intervals used | Low | Manual | `analysis.pitchAnalysis` |
| Pitch class histogram | Distribution of pitch classes (0-11) | Low | Manual | `analysis.pitchAnalysis.pitchAttributeCount` |
| Duration histogram | Distribution of durations used | Low | Manual | Manual |
| Note density | Notes per unit time | Low | Manual | Manual |
| Key analysis | Detect key of passage | High | Manual | `analysis.discrete.KrumhanslSchmuckler` (+ 4 other algorithms) |
| Windowed analysis | Analyze in overlapping windows | Medium | Manual | `analysis.windowed.WindowedAnalysis` |
| Metrical analysis | Identify strong/weak beat patterns | Medium | Manual | `analysis.metrical` (Lerdahl-Jackendoff) |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|------------------|------------|-------|
| Motivic analysis / pattern search | Find recurring motifs in a score | High | Pattern matching problem |
| Form detection | Sonata, rondo, binary, ternary | Very High | Research-level problem |
| Tension/resolution curve | Quantify musical tension over time | High | Based on harmonic + melodic analysis |
| Rhythmic complexity metric (nPVI) | Quantify syncopation and irregularity | Medium | Patel's nPVI index |
| Voice independence metric | How independently do the voices move? | Medium | Based on motion analysis |
| Melodic similarity metric | Compare two melodies quantitatively | Medium | Edit distance on pitch/rhythm sequences |
| Score search / pattern matching | Find all instances of a pattern in a score | Medium | Music21: `search.segment` |
| Reduction (Schenkerian) | Layer-by-layer reduction to fundamental structure | Very High | Music21: `analysis.reduction` (very partial) |
| Statistical summary | Comprehensive statistics for a passage | Low | Aggregate of individual analyses |

### Key Functions to Implement

**From Music21:**
- `analysis.discrete.Ambitus` -- range analysis
- `analysis.discrete.KrumhanslSchmuckler` -- key detection (probe-tone weights)
- `analysis.discrete.BellmanBudge` -- key detection (Bellman-Budge weights)
- `analysis.discrete.TemperleyKostkaPayne` -- key detection (Temperley weights)
- `analysis.discrete.SimpleWeights` -- key detection (simple weights)
- `analysis.discrete.AardenEssen` -- key detection (Aarden-Essen weights)
- `analysis.windowed.WindowedAnalysis` -- sliding window analysis framework
- `analysis.neoRiemannian` -- neo-Riemannian analysis (P, L, R operations)
- `analysis.reduction` -- Schenkerian reduction (partial implementation)
- `analysis.metrical` -- metrical analysis (Lerdahl-Jackendoff inspired)
- `analysis.patel` -- Patel's nPVI (normalized pairwise variability index)
- `analysis.pitchAnalysis` -- pitch distribution statistics
- `search.segment.indexScoreFilePaths()` -- corpus search by melodic segment
- `search.serial` -- serial pattern search in scores

**From Opusmodus:**
- `ambitus` -- range extraction
- `pitch-contour` -- contour extraction (up/down/same)

**New (Cadenza-specific):**
- `analysis.melodic_similarity(melody_a, melody_b)` -- similarity metric (0.0-1.0)
- `analysis.rhythmic_complexity(phrase)` -- complexity score (nPVI + other metrics)
- `analysis.tension_curve(score, window_size)` -- tension over time
- `analysis.motivic_search(score, motif, threshold=0.8)` -- find approximate motif matches
- `analysis.statistics(score)` -- comprehensive stats dict (pitch distribution, interval distribution, duration distribution, dynamic distribution, range, density, etc.)
- `analysis.voice_independence(score)` -- independence metric for multi-voice texture

**Complexity: MEDIUM-HIGH.** Key detection and windowed analysis are the hardest table-stakes features. Motivic analysis and form detection are open research problems; basic implementations are feasible but perfection is not.

---

## Anti-Features (Features to Explicitly NOT Build)

| Anti-Feature | Why Avoid | What to Do Instead |
|-------------|-----------|-------------------|
| Audio synthesis/playback | Wrong domain; Cadenza is symbolic only | Export MIDI for playback in DAWs |
| Notation rendering/GUI | Not a notation program; already solved by Dorico/Sibelius | Export MusicXML/Lilypond for rendering |
| Audio analysis (FFT, spectral) | Different domain (signal processing, not symbolic music) | Stay score-based; accept MIDI/MusicXML input |
| DAW plugin (VST/AU) | Requires C++ bridge, massive effort | REST API is the integration mechanism for v1 |
| Machine learning models | Too complex, separate concern, unreliable for music theory | Classical algorithmic methods first; ML as optional future layer |
| Microtonality (v1) | Adds complexity to every pitch operation | Design pitch model to be extensible; implement in v2 |
| Real-time MIDI processing | Latency-sensitive, different architecture | Batch/offline symbolic processing only |
| Music OCR / OMR | Computer vision problem, not music theory | Accept MusicXML/MIDI/OMN as input |
| Multi-user / collaboration | Library, not SaaS | Stateless API; concurrency is caller's responsibility |

---

## Feature Dependencies (Critical Build Path)

```
PHASE 1: FOUNDATIONS (everything depends on this)
  OMN Parser + Serializer
  Pitch Model (with enharmonic awareness)
  Duration Model
  Interval Model
  Note / Rest / Chord event types
  Phrase Model (ordered sequence of events)
  Time Signature / Key Signature

PHASE 2: LIBRARIES (data-heavy, enables analysis and generation)
  Scale / Mode Library (8)  -----> depends on Pitch + Interval
  Chord Library (9)         -----> depends on Pitch + Interval + Scale

PHASE 3: TRANSFORMS (core user-facing value)
  Pitch Operations (2)     -----> depends on Pitch Model
  Rhythm Operations (3)    -----> depends on Duration Model
  Melodic Transforms (4)   -----> depends on Pitch Ops + Rhythm Ops
  Set Theory (10)          -----> depends on Pitch Model (independent of scales/chords)

PHASE 4: ANALYSIS + I/O
  Harmonic Analysis (5)    -----> depends on Chord Library + Scale Library
  Analysis (15)            -----> depends on all foundational pieces
  MusicXML I/O             -----> depends on full data model
  MIDI I/O                 -----> depends on Pitch + Duration model
  REST API                 -----> wraps everything above

PHASE 5: ADVANCED MUSIC THEORY
  Serial / 12-Tone (11)   -----> depends on Set Theory + Pitch Operations
  Voice Leading (7)        -----> depends on Chord Library + Interval Model
  Counterpoint (6)         -----> depends on Voice Leading + Harmonic Analysis + Scale Library
  Batch Operations (13)    -----> depends on Notation/Parsing + full data model

PHASE 6: GENERATION
  Pattern Generation (12)  -----> depends on Rhythm Model + Pitch Model
  Algorithmic Comp (14)    -----> depends on Pattern Gen + all transforms + tonality-map
```

---

## MVP Recommendation

**Must ship for notation software to care (Phase 1-3):**
1. OMN parsing/serialization with shorthand expansion
2. Pitch operations (transpose, invert, retrograde, rotate, enharmonic)
3. Rhythm operations (augment, diminish, retrograde, rotate)
4. Scale/mode library (80+ scales, all standard operations)
5. Chord library (all common types, identification, inversions)
6. Basic melodic transforms (retrograde, inversion, rotation, transposition)
7. MusicXML import/export (core subset)
8. MIDI import/export
9. REST API exposing all above

**High value, ship next (Phase 4-5):**
10. Harmonic analysis (chord ID, key detection, Roman numerals)
11. Voice leading engine (smooth voicing, parallel detection)
12. Set theory / serial operations (12-tone matrix, Forte numbers)
13. Batch operations (articulation/dynamic patterns)
14. Counterpoint validation and generation (species I-V)

**Defer to later (Phase 6):**
15. Full algorithmic composition suite (Markov, L-systems, CA)
16. Advanced analysis (motivic search, form detection, Schenkerian reduction)
17. Pattern generation (Euclidean, isorhythm, tendency masks)
18. Advanced differentiators (tension curves, melody interpolation, orchestration)

---

## Estimated Function Count by Category

| Category | Table Stakes Functions | Differentiator Functions | Total |
|----------|----------------------|------------------------|-------|
| 1. Notation/Parsing | ~25 | ~8 | ~33 |
| 2. Pitch Operations | ~20 | ~5 | ~25 |
| 3. Rhythm Operations | ~22 | ~8 | ~30 |
| 4. Melodic Transforms | ~15 | ~10 | ~25 |
| 5. Harmonic Analysis | ~15 | ~8 | ~23 |
| 6. Counterpoint | ~12 | ~8 | ~20 |
| 7. Voice Leading | ~12 | ~6 | ~18 |
| 8. Scale/Mode Library | ~10 + 100 scale defs | ~5 | ~115 |
| 9. Chord Library | ~18 + 45 chord defs | ~8 | ~71 |
| 10. Set Theory | ~14 | ~5 | ~19 |
| 11. Serial/12-Tone | ~12 | ~6 | ~18 |
| 12. Pattern Generation | ~22 | ~8 | ~30 |
| 13. Batch Operations | ~10 | ~6 | ~16 |
| 14. Algorithmic Composition | ~20 | ~8 | ~28 |
| 15. Analysis | ~12 | ~8 | ~20 |
| **TOTAL** | **~239 + 145 defs** | **~107** | **~491** |

This puts the target near the ~600 function goal stated in PROJECT.md when you include all scale definitions, chord type definitions, utility functions, and REST API endpoints.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|-----------|-------|
| Opusmodus function names | MEDIUM | Based on training data; could not fetch current PDFs to verify specific function signatures |
| Music21 module names | MEDIUM-HIGH | Well-known stable library; could not verify latest version but API is stable |
| Counterpoint rules | HIGH | Based on Fux/Jeppesen/Salzer -- centuries-old, not version-dependent |
| Feature categorization | HIGH | Standard music theory domain categories |
| Complexity estimates | MEDIUM | Based on implementation knowledge; actual complexity depends on design choices |
| Dependency graph | HIGH | Follows from logical music theory dependencies |
| Function count estimates | MEDIUM | Approximate; actual count depends on API granularity |

---

## Sources

- Opusmodus documentation (opusmodus.com) -- training data knowledge, not live-verified
- Music21 documentation (web.mit.edu/music21) -- training data knowledge, not live-verified
- Fux, Johann Joseph. *Gradus ad Parnassum* (1725) -- counterpoint rules
- Forte, Allen. *The Structure of Atonal Music* (1973) -- set theory, Forte numbers
- Rahn, John. *Basic Atonal Theory* (1980) -- prime form algorithm
- Toussaint, Godfried. "The Euclidean Algorithm Generates Traditional Musical Rhythms" (2005)
- Krumhansl, Carol. *Cognitive Foundations of Musical Pitch* (1990) -- key detection
- Patel, Aniruddh. *Music, Language, and the Brain* (2008) -- nPVI metric
- Lerdahl, Fred and Jackendoff, Ray. *A Generative Theory of Tonal Music* (1983) -- metrical analysis
- Bach Project for Max (bachproject.net) -- training data knowledge, not live-verified
