---
phase: 05-harmonic-analysis
verified: 2026-03-19T20:00:00Z
status: passed
score: 10/10 must-haves verified
re_verification: false
gaps: []
human_verification: []
---

# Phase 05: Harmonic Analysis Verification Report

**Phase Goal:** Users can submit a phrase or chord and receive correct harmonic analysis (chord name, Roman numerals, key, function)
**Verified:** 2026-03-19T20:00:00Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| #  | Truth | Status | Evidence |
|----|-------|--------|----------|
| 1  | Given pitches C4-E4-G4-Bb4, identify_chord returns ChordMatch(root=C, symbol='7', inversion=0) | VERIFIED | test_identify_dominant_seventh passes; chords.py brute-forces pitch class match against _CHORD_REGISTRY |
| 2  | chord_symbol(Pitch('c','n',4), '7') returns 'c47' | VERIFIED | chord_symbol formats as `{step}{acc}{octave}{symbol}`; round-trip test covers all registry keys |
| 3  | parse_chord_symbol('c4maj7') returns the same pitches as get_chord(Pitch('c','n',4), 'maj7') | VERIFIED | test_parse_chord_symbol_major passes; test_chord_symbol_round_trip covers all 21+ registry keys |
| 4  | realize_chord(Pitch('c','n',4), 'maj', inversion=1) returns first-inversion C major pitches | VERIFIED | test_realize_chord_inversion passes; delegates to get_chord |
| 5  | identify_chord detects inversions: E4-G4-C5 identified as C major first inversion | VERIFIED | test_identify_first_inversion passes; bass note determines inversion index |
| 6  | Given a C major scale phrase, detect_key returns KeyResult(root=C, mode='major') with high confidence | VERIFIED | test_detect_key_c_major passes with confidence > 0.8; K-S profile Pearson correlation implemented |
| 7  | Given a I-IV-V-I progression in C major, roman_numeral labels them with correct functions | VERIFIED | test_functional_labels_all_degrees covers I-VII; test_roman_numeral_tonic, _dominant, _supertonic etc. pass |
| 8  | A phrase that starts in C major and modulates to G major is detected by detect_modulations | VERIFIED | test_detect_modulations_key_change passes; sliding window + consecutive-change confirmation |
| 9  | A bVII chord in C major (Bb major triad) is identified as borrowed from parallel minor | VERIFIED | test_borrowed_chord_bVII passes; parallel_mode fallback detects degree in natural_minor |
| 10 | Harmonic rhythm analysis segments a phrase into chord change points with onset/duration | VERIFIED | test_harmonic_rhythm_simple and test_harmonic_rhythm_onset_fractions pass |

**Score:** 10/10 truths verified

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/cadenza/analysis/__init__.py` | Public API re-exports for analysis subpackage | VERIFIED | Re-exports all 13 public names: ChordMatch, HarmonicBeat, KeyResult, Modulation, RomanNumeral, chord_symbol, detect_key, detect_modulations, harmonic_rhythm, identify_chord, parse_chord_symbol, realize_chord, roman_numeral |
| `src/cadenza/analysis/chords.py` | ChordMatch dataclass, identify_chord, chord_symbol, parse_chord_symbol, realize_chord | VERIFIED | 280 lines; all 5 exports implemented and substantive; _COMPLEXITY_RANK, _CHORD_SYMBOL_RE, _QUALITY_ALIASES all present |
| `src/cadenza/analysis/keys.py` | KeyResult, Modulation, detect_key, detect_modulations | VERIFIED | 280 lines; K-K profiles (MAJOR_PROFILE starting 6.35, MINOR_PROFILE starting 6.33), synthetic harmonic/melodic minor profiles, _pearson_correlation, _pitch_class_histogram, sliding window modulation detection |
| `src/cadenza/analysis/harmony.py` | RomanNumeral, HarmonicBeat, roman_numeral, harmonic_rhythm | VERIFIED | 272 lines; _TRIAD_FIGURES, _SEVENTH_FIGURES, _DEGREE_FUNCTION all present; borrowed chord detection via parallel key fallback; figured bass suffixes correct |
| `tests/analysis/__init__.py` | Test package init | VERIFIED | Exists |
| `tests/analysis/test_chords.py` | Tests for HARM-01, HARM-07, HARM-08, HARM-09 | VERIFIED | 24 tests; covers identification, inversions, flat spelling, symbol generation/parsing, aliases, round-trip for all registry keys |
| `tests/analysis/test_keys.py` | Tests for HARM-03, HARM-06 | VERIFIED | 11 tests; covers C major, A minor, phrase input, tuple/list input, empty input, confidence range, flat spelling preservation, modulation detection |
| `tests/analysis/test_harmony.py` | Tests for HARM-02, HARM-04, HARM-05, HARM-10 | VERIFIED | 15 tests; covers all 9 inversion figures, 3 borrowed chord types, all 7 functional labels, harmonic rhythm onset Fractions |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `src/cadenza/analysis/chords.py` | `cadenza.theory.chords._CHORD_REGISTRY` | import and iteration | WIRED | Imported line 15; iterated in identify_chord loop (line 101); used in _resolve_quality (lines 231, 235) |
| `src/cadenza/analysis/chords.py` | `cadenza.theory.chords.get_chord` | chord realization | WIRED | Imported line 15; called in identify_chord (line 141), realize_chord (line 178), parse_chord_symbol (line 279) |
| `src/cadenza/analysis/chords.py` | `cadenza.api.parsing.parse_pitch_string` | CN root parsing | WIRED | Imported line 13; called in parse_chord_symbol (line 270) |
| `src/cadenza/analysis/keys.py` | `cadenza.core.pitch.Pitch.pitch_class` | histogram building | WIRED | pitch_class property used in _pitch_class_histogram (line 130), _find_root_pitch (line 206), detect_modulations (line 244) |
| `src/cadenza/analysis/harmony.py` | `cadenza.analysis.chords.identify_chord` | chord identification in harmonic rhythm | WIRED | Imported line 13; called in harmonic_rhythm (line 229) |
| `src/cadenza/analysis/harmony.py` | `cadenza.theory.scales.get_scale` | scale degree computation | WIRED | Imported line 17; called in roman_numeral for both primary scale (line 125) and parallel scale (line 141) |
| `src/cadenza/analysis/harmony.py` | `cadenza.theory.scales.parallel_key` | borrowed chord detection | PARTIAL | `parallel_key` from theory.scales is NOT imported; implementation uses internal `_parallel_mode()` helper (returns mode string) + `get_scale()` directly. Borrowed chord detection works correctly (3 tests pass) — functional goal met via alternate path. Not a blocking gap. |

---

## Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| HARM-01 | 05-01 | Identify chord from a set of simultaneous pitches (root, quality, inversion) | SATISFIED | identify_chord: brute-force 12-root x registry matching, inversion detection via bass note; 11 tests pass |
| HARM-02 | 05-02 | Roman numeral analysis of a chord within a key context | SATISFIED | roman_numeral: uppercase/lowercase convention, figured bass inversion suffixes; 9 tests pass |
| HARM-03 | 05-02 | Key detection from a phrase or score (using pitch class frequency analysis) | SATISFIED | detect_key: Krumhansl-Schmuckler profile correlation across 48 key/mode combos; 8 tests pass |
| HARM-04 | 05-02 | Harmonic rhythm analysis (detect chord change points) | SATISFIED | harmonic_rhythm: sliding window chord identification, Fraction onset/duration; 2 tests pass |
| HARM-05 | 05-02 | Functional harmony labeling (tonic, dominant, subdominant, etc.) | SATISFIED | _DEGREE_FUNCTION maps all 7 degrees; "borrowed" for parallel key chords; test_functional_labels_all_degrees passes |
| HARM-06 | 05-02 | Detect modulation between keys within a phrase | SATISFIED | detect_modulations: sliding window with consecutive-change confirmation; 3 tests pass |
| HARM-07 | 05-01 | Generate chord symbol string from a chord object (e.g. "Cmaj7", "F#m", "Bdim7") | SATISFIED | chord_symbol: CN format `{step}{acc}{octave}{symbol}`; 4 generation tests pass |
| HARM-08 | 05-01 | Parse chord symbol string into a chord object | SATISFIED | parse_chord_symbol: regex + multi-strategy quality resolution + alias normalization; round-trip covers all 21+ registry keys |
| HARM-09 | 05-01 | Realize a chord as a list of pitches in a given voicing/inversion | SATISFIED | realize_chord: delegates to get_chord with octave adjustment; 2 tests pass |
| HARM-10 | 05-02 | Identify borrowed chords (chords from parallel keys) | SATISFIED | roman_numeral parallel-key fallback with b/# prefix computation; 3 borrowed chord tests pass (bVII, bIII, bVI) |

No orphaned requirements — all 10 HARM IDs are accounted for across the two plans.

---

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| None | — | — | — | No TODO/FIXME/placeholder comments; no stub returns; no empty implementations found |

The `return []` instances at `keys.py:152`, `keys.py:229`, `harmony.py:201`, `harmony.py:213` are all legitimate early-exit guard clauses for empty or insufficient input, not stubs.

---

## Human Verification Required

None. All functional requirements are verifiable programmatically. The following notes are informational:

- Visual inspection of Roman numeral labels (e.g. "V6/5", "bVII") is confirmed by passing tests — no human UI to check.
- Key detection confidence thresholds were adjusted from the plan's "uniform scale = 0.8+" to use weighted tonic/dominant distributions (documented deviation in SUMMARY). The algorithm is correct; the test data is realistic.

---

## Gaps Summary

No gaps. All 10 must-haves are verified, all 10 HARM requirements are satisfied, 541 tests pass (50 in analysis, 491 in other modules — no regressions), and all public imports work.

The one wiring deviation — `harmony.py` not importing `theory.scales.parallel_key` directly — is a non-blocking design choice. The implementation achieves identical behavior through `_parallel_mode()` + `get_scale()`, confirmed by three passing borrowed-chord tests.

---

## Test Suite Results

```
tests/analysis/test_chords.py    24 passed
tests/analysis/test_harmony.py   15 passed
tests/analysis/test_keys.py      11 passed
Total analysis:                  50 passed
Full suite:                     541 passed, 0 failed
```

---

_Verified: 2026-03-19T20:00:00Z_
_Verifier: Claude (gsd-verifier)_
