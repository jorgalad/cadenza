---
phase: 03-theory-libraries
verified: 2026-03-19T00:00:00Z
status: passed
score: 17/17 must-haves verified
re_verification: false
---

# Phase 3: Theory Libraries Verification Report

**Phase Goal:** Users can look up any standard scale or chord by name and root, and the library returns correctly spelled pitches
**Verified:** 2026-03-19
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| #  | Truth | Status | Evidence |
|----|-------|--------|----------|
| 1  | `get_scale(Pitch('d','n',4), 'dorian')` returns `(D4, E4, F4, G4, A4, B4, C5)` with all naturals | VERIFIED | Direct execution confirms exact match; TestChurchModes::test_dorian passes |
| 2  | All 7 church modes are retrievable by name | VERIFIED | dorian, phrygian, lydian, mixolydian, locrian in registry; ionian/aeolian as aliases; 5 tests pass |
| 3  | Major, natural_minor, harmonic_minor, melodic_minor are retrievable | VERIFIED | All 4 in `_SCALE_REGISTRY`; TestMinorScales and TestMajorScales pass |
| 4  | Pentatonic, blues, symmetric, bebop, and non-Western scales are all retrievable | VERIFIED | major_pentatonic, minor_pentatonic, blues, whole_tone, diminished, augmented, bebop_dominant/major/minor, 16 non-Western scales all in registry |
| 5  | `register_scale` adds a custom scale that `get_scale` can retrieve | VERIFIED | TestRegisterScale::test_register_and_retrieve passes; duplicate raises ValueError |
| 6  | `scales_for_pitches` finds matching (root, scale_name) pairs | VERIFIED | TestScalesForPitches all pass; empty input returns [] |
| 7  | `scale_degree` returns 1-based degree for pitches in a scale | VERIFIED | TestScaleDegree passes; out-of-scale pitch raises ValueError |
| 8  | `relative_key` and `parallel_key` return correct Scale objects | VERIFIED | C major relative = A natural_minor; C major parallel = C natural_minor |
| 9  | Phase 2 stubs (diatonic_transpose, pitch_in_scale, nearest_in_scale) are completed | VERIFIED | No NotImplementedError in transforms/pitch.py; 9 stub tests pass |
| 10 | `get_chord(Pitch('c','n',4), 'maj')` returns `(C4, E4, G4)` | VERIFIED | TestTriads::test_major_triad passes; direct execution confirms |
| 11 | `get_chord(Pitch('c','n',4), '7')` returns `(C4, E4, G4, Bb4)` — dominant seventh | VERIFIED | TestSeventhChords::test_dom7 passes |
| 12 | `get_chord(Pitch('c','n',4), 'maj', inversion=1)` returns `(E4, G4, C5)` | VERIFIED | TestInversions::test_first_inversion passes |
| 13 | `diatonic_chords(Pitch('c','n',4), 'major', 'triad')` returns 7 chords: C, Dm, Em, F, G, Am, Bdim | VERIFIED | TestDiatonicChords::test_diatonic_triads_c_major passes all 7 assertions |
| 14 | `secondary_dominant(5, Pitch('c','n',4), 'major')` returns D7 chord (D-F#-A-C) | VERIFIED | TestSecondaryDominants::test_secondary_dominant_V_of_V passes |
| 15 | `aug6_chord('italian', Pitch('c','n',4), 'major')` returns `(Ab4, C5, F#5)` | VERIFIED | TestAugmentedSixth::test_italian_sixth passes — actual: `(Pitch(a,b,4), Pitch(c,n,5), Pitch(f,s,5))` |
| 16 | `neapolitan_chord(Pitch('c','n',4), 'major')` returns `(Db, F, Ab)` — bII chord | VERIFIED | TestNeapolitan::test_neapolitan passes — actual: `(Pitch(d,b,4), Pitch(f,n,4), Pitch(a,b,4))` |
| 17 | `register_chord` allows custom chord definition | VERIFIED | TestAliasesAndRegistry::test_register_chord passes |

**Score:** 17/17 truths verified

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/cadenza/theory/scales.py` | Scale type, registry, get_scale, query functions | VERIFIED | 282 lines; `@dataclass(frozen=True, slots=True) class Scale`; 35 built-in scales; all 7 public functions present |
| `src/cadenza/theory/chords.py` | Chord registry, get_chord, diatonic_chords, secondary_dominant, aug6_chord, neapolitan_chord, register_chord | VERIFIED | 286 lines; 22 chord types in registry; all 6 public functions present |
| `src/cadenza/theory/__init__.py` | Public API re-exports for theory package | VERIFIED | Re-exports all 13 symbols (Scale + 6 scale functions + 6 chord functions) with `__all__` |
| `tests/theory/test_scales.py` | Tests for SCAL-01 through SCAL-12 | VERIFIED | 45 tests covering all 12 SCAL requirements; 386 lines |
| `tests/theory/test_chords.py` | Tests for CHRD-01 through CHRD-09 | VERIFIED | 45 tests covering all 9 CHRD requirements; 339 lines |
| `tests/theory/__init__.py` | Test package init | VERIFIED | Exists |
| `tests/transforms/test_pitch_stubs.py` | Tests for completed Phase 2 stubs | VERIFIED | 9 tests for diatonic_transpose, pitch_in_scale, nearest_in_scale |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `src/cadenza/theory/scales.py` | `src/cadenza/core/pitch.py` | `from cadenza.core.pitch import ACCIDENTAL_SEMITONES, STEP_INDEX, STEP_SEMITONES, Pitch` | WIRED | Import confirmed at line 11; all 4 symbols used in `_build_pitch` and `get_scale` |
| `src/cadenza/theory/chords.py` | `src/cadenza/theory/scales.py` | `from cadenza.theory.scales import get_scale` | WIRED | Import confirmed at line 16; used in `diatonic_chords` and `secondary_dominant` |
| `src/cadenza/theory/chords.py` | `src/cadenza/core/pitch.py` | `from cadenza.core.pitch import ACCIDENTAL_SEMITONES, STEP_INDEX, STEP_SEMITONES, Pitch` | WIRED | Import confirmed at line 10; used in `_build_pitch` |
| `src/cadenza/transforms/pitch.py` | `src/cadenza/theory/scales.py` | `from cadenza.theory.scales import Scale` | WIRED | Import confirmed at line 13; `Scale` used in `diatonic_transpose`, `pitch_in_scale`, `nearest_in_scale` signatures |

---

## Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| SCAL-01 | 03-01 | Major, natural/harmonic/melodic minor | SATISFIED | All 4 scales in registry; TestMajorScales + TestMinorScales pass |
| SCAL-02 | 03-01 | All 7 church modes | SATISFIED | dorian, phrygian, lydian, mixolydian, locrian in registry; ionian/aeolian aliases; TestChurchModes + TestAliases pass |
| SCAL-03 | 03-01 | Pentatonic scales (major, minor, blues pentatonic) | SATISFIED* | major_pentatonic and minor_pentatonic in registry; tests pass. Note: `blues_pentatonic` is not a distinct registry entry — minor_pentatonic (0,3,5,7,10) is the standard "blues pentatonic"; REQUIREMENTS.md marks this [x] complete |
| SCAL-04 | 03-01 | Blues scale (hexatonic) | SATISFIED | `blues: (0, 3, 5, 6, 7, 10)` in registry; TestBlues passes |
| SCAL-05 | 03-01 | Symmetric scales: whole tone, diminished, augmented | SATISFIED | All 3 in registry plus diminished_half_whole; TestSymmetric passes |
| SCAL-06 | 03-01 | Bebop scales | SATISFIED | bebop_dominant, bebop_major, bebop_minor in registry; TestBebop passes |
| SCAL-07 | 03-01 | Non-Western scales (16 entries) | SATISFIED | 16 non-Western scales in registry including hijaz, hungarian_minor, persian, hirajoshi, etc.; TestNonWestern passes |
| SCAL-08 | 03-01 | User-defined scale from interval pattern | SATISFIED | `register_scale` implemented; raises ValueError on duplicate; TestRegisterScale passes |
| SCAL-09 | 03-01 | Given root + scale name, return all pitches | SATISFIED | `get_scale` returns `Scale.pitches` tuple; all spelling tests pass |
| SCAL-10 | 03-01 | Determine what scale(s) a pitch set belongs to | SATISFIED | `scales_for_pitches` implemented; TestScalesForPitches passes |
| SCAL-11 | 03-01 | Return degree of a pitch within a scale | SATISFIED | `scale_degree` returns 1-based int; raises ValueError if not in scale; TestScaleDegree passes |
| SCAL-12 | 03-01 | Relative and parallel major/minor | SATISFIED | `relative_key` and `parallel_key` implemented; TestRelativeKey + TestParallelKey pass |
| CHRD-01 | 03-02 | All triads: major, minor, diminished, augmented | SATISFIED | All 4 in registry; TestTriads passes |
| CHRD-02 | 03-02 | All seventh chords | SATISFIED | 7 seventh chord types in registry; TestSeventhChords passes |
| CHRD-03 | 03-02 | Extended chords: 9th, 11th, 13th | SATISFIED | 9, maj9, m9, 11, maj11, 13, maj13 in registry; TestExtendedChords passes |
| CHRD-04 | 03-02 | Added-note chords: add9, add11, sus2, sus4 | SATISFIED | All 4 in registry; TestAddedSuspended passes |
| CHRD-05 | 03-02 | All inversions of any chord | SATISFIED | `_apply_inversion` rotates pitches up one octave; out-of-range raises ValueError; TestInversions passes |
| CHRD-06 | 03-02 | Diatonic chords of a scale | SATISFIED | `diatonic_chords` builds triads or sevenths per degree; TestDiatonicChords passes |
| CHRD-07 | 03-02 | Secondary dominants (V/ii, V/iii, etc.) | SATISFIED | `secondary_dominant` builds V7 of target degree; degrees 2-7 only; TestSecondaryDominants passes |
| CHRD-08 | 03-02 | Neapolitan and augmented sixth chords | SATISFIED | `aug6_chord` (italian/french/german) and `neapolitan_chord` implemented; TestAugmentedSixth + TestNeapolitan pass |
| CHRD-09 | 03-02 | User-defined chord from interval stack | SATISFIED | `register_chord(name, intervals, degree_steps)` implemented; raises ValueError on duplicate; TestAliasesAndRegistry::test_register_chord passes |

*SCAL-03 note: "blues pentatonic" is widely treated as equivalent to "minor pentatonic" in theory literature. The registry has `minor_pentatonic: (0, 3, 5, 7, 10)` which is the standard blues pentatonic. A separate `blues_pentatonic` entry does not exist, but REQUIREMENTS.md marks SCAL-03 [x] complete.

---

## Anti-Patterns Found

No blockers or stubs detected.

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `scales.py` | 229 | `return []` | Info | Legitimate early-return guard: `if not pitches: return []` in `scales_for_pitches`. Not a stub. |

---

## Registry Counts

| Registry | Expected | Actual | Status |
|----------|----------|--------|--------|
| `_SCALE_REGISTRY` | 30+ (plan acceptance criteria) | 35 | VERIFIED |
| `_CHORD_REGISTRY` | 21+ (plan acceptance criteria) | 22 | VERIFIED |

Note: Plan and summary refer to "40+ built-in scales" and "36 built-in scales" in different places; actual count is 35. This is above the plan acceptance criterion of 30+, and all categories required by SCAL-01 through SCAL-07 are present.

---

## Human Verification Required

None. All behaviors are programmatically verifiable and tests pass.

---

## Test Suite Results

| Test File | Tests | Result |
|-----------|-------|--------|
| `tests/theory/test_scales.py` | 45 | All pass |
| `tests/theory/test_chords.py` | 45 | All pass |
| `tests/transforms/test_pitch_stubs.py` | 9 | All pass |
| Full suite (`tests/`) | 425 | All pass |

---

## Commits Verified

All 8 task commits from summaries exist in git history:
- `6e09756` test(03-01): RED — scale type and registry tests
- `6c174b2` feat(03-01): GREEN — Scale type, 35 built-in scales, get_scale
- `3206e23` test(03-01): RED — query function tests
- `46c31d3` feat(03-01): GREEN — query functions + Phase 2 stub completion
- `06b7e5c` test(03-02): RED — chord registry and get_chord tests
- `990fa44` feat(03-02): GREEN — chord registry, get_chord, inversions
- `e92bba1` test(03-02): RED — diatonic chords, secondary dominants, aug6, neapolitan tests
- `11274d8` feat(03-02): GREEN — all chord construction functions

---

## Summary

Phase 3 goal is fully achieved. All 21 requirements (SCAL-01 through SCAL-12, CHRD-01 through CHRD-09) are satisfied by substantive, wired implementations. The library correctly spells pitches for any root using the degree-steps + semitone-offset dual-encoding approach. The critical Phase 2 stubs (diatonic_transpose, pitch_in_scale, nearest_in_scale) are completed with real Scale-aware logic. The full test suite of 425 tests is green.

---

_Verified: 2026-03-19_
_Verifier: Claude (gsd-verifier)_
