---
phase: 07-voice-leading
verified: 2026-03-20T10:00:00Z
status: passed
score: 12/12 must-haves verified
re_verification: false
---

# Phase 7: Voice Leading Verification Report

**Phase Goal:** Users can check any multi-voice passage for voice leading violations and generate smooth voice connections
**Verified:** 2026-03-20T10:00:00Z
**Status:** PASSED
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| #  | Truth                                                                                   | Status     | Evidence                                                                 |
|----|-----------------------------------------------------------------------------------------|------------|--------------------------------------------------------------------------|
| 1  | Two voices moving C-G then D-A are flagged as parallel fifths                           | VERIFIED   | test_parallel_fifths passes; _check_parallels target_semitones=7         |
| 2  | Two voices moving C-C' then D-D' are flagged as parallel octaves                        | VERIFIED   | test_parallel_octaves passes; _check_parallels target_semitones=0        |
| 3  | A lower voice pitch above an upper voice pitch is flagged as voice crossing             | VERIFIED   | test_voice_crossing, test_voice_crossing_uses_score_order both pass      |
| 4  | A voice moving past the previous pitch of an adjacent voice is flagged as voice overlap | VERIFIED   | test_voice_overlap passes; _check_overlap logic at lines 157-201         |
| 5  | Leaps greater than an octave are flagged as large leaps                                 | VERIFIED   | test_large_leap passes; semitones > 12 check in _check_leaps             |
| 6  | Augmented and diminished leaps are flagged with suggestion severity                     | VERIFIED   | test_augmented_leap, test_diminished_leap pass; quality in ("A","d")     |
| 7  | check_voice_leading returns all violations sorted by position                           | VERIFIED   | test_check_voice_leading_returns_sorted passes; .sort(key=lambda v:v.position) |
| 8  | smooth_voice_leading returns the reordering of chord2 minimizing total semitone movement| VERIFIED   | test_smooth_voice_leading_reorder confirms reorder occurs; permutations exhausted |
| 9  | smooth_voice_leading raises ValueError when chord sizes differ                          | VERIFIED   | test_smooth_voice_leading_size_mismatch passes; ValueError at line 267   |
| 10 | generate_inner_voices produces n inner voice Phrases within specified ranges            | VERIFIED   | test_generate_inner_voices_basic, test_generate_inner_voices_custom_ranges pass |
| 11 | Generated inner voices minimize movement from beat to beat (greedy)                     | VERIFIED   | test_generate_inner_voices_minimizes_movement passes (avg <= 4 semitones)|
| 12 | Default SATB ranges are alto C3-G5 and tenor C2-G4                                     | VERIFIED   | _DEFAULT_RANGES at lines 290-293; test_generate_inner_voices_basic verifies midi bounds |

**Score:** 12/12 truths verified

### Required Artifacts

| Artifact                                  | Expected                                        | Status     | Details                                                      |
|-------------------------------------------|-------------------------------------------------|------------|--------------------------------------------------------------|
| `src/cadenza/analysis/voiceleading.py`    | VoiceLeadingViolation dataclass + all detectors | VERIFIED   | 419 lines; all 7 required functions present and substantive  |
| `tests/analysis/test_voiceleading.py`     | 27 tests covering all rules and edge cases      | VERIFIED   | 440 lines; 27 tests, all pass                                |
| `src/cadenza/analysis/__init__.py`        | Re-exports all 4 public symbols                 | VERIFIED   | Lines 22-27 import all 4; all appear in __all__              |

### Key Link Verification

| From                                   | To                                        | Via                                        | Status    | Details                                              |
|----------------------------------------|-------------------------------------------|--------------------------------------------|-----------|------------------------------------------------------|
| `src/cadenza/analysis/voiceleading.py` | `cadenza.core.interval.Interval`          | Interval.between for interval computation  | WIRED     | `Interval.between(...)` called in all detector funcs |
| `src/cadenza/analysis/voiceleading.py` | `cadenza.core.score.Score`                | `score._voices` iteration                 | WIRED     | Lines 385, 390, 396 iterate score._voices            |
| `src/cadenza/analysis/voiceleading.py` | `itertools.permutations`                  | Exhaustive permutation search              | WIRED     | `from itertools import permutations` at line 11; used in smooth_voice_leading line 277 |
| `src/cadenza/analysis/voiceleading.py` | `cadenza.transforms.pitch.from_midi`      | MIDI-to-Pitch in inner voice generation    | WIRED     | `from cadenza.transforms.pitch import from_midi` at line 18; used at lines 329, 350 |

### Requirements Coverage

| Requirement | Source Plan | Description                                                          | Status    | Evidence                                                             |
|-------------|-------------|----------------------------------------------------------------------|-----------|----------------------------------------------------------------------|
| VLEAD-01    | 07-01       | Detect parallel fifths between any two voices                        | SATISFIED | _check_parallels(target=7) + 3 tests (basic, contrary, oblique)      |
| VLEAD-02    | 07-01       | Detect parallel octaves between any two voices                       | SATISFIED | _check_parallels(target=0) + 3 tests (basic, compound, unison)       |
| VLEAD-03    | 07-01       | Detect voice crossing                                                | SATISFIED | _check_crossing + test_voice_crossing, test_voice_crossing_uses_score_order |
| VLEAD-04    | 07-01       | Detect voice overlap                                                 | SATISFIED | _check_overlap + test_voice_overlap                                  |
| VLEAD-05    | 07-02       | Find smoothest voice leading path between two chords                 | SATISFIED | smooth_voice_leading via permutations + 5 tests                      |
| VLEAD-06    | 07-01       | Detect large leaps and augmented/diminished leaps                    | SATISFIED | _check_leaps + test_large_leap, test_augmented_leap, test_diminished_leap |
| VLEAD-07    | 07-01       | Check all standard voice leading rules and return violation list      | SATISFIED | check_voice_leading orchestrator; test_check_voice_leading_returns_sorted, _empty_score, _single_voice |
| VLEAD-08    | 07-02       | Generate smooth inner voice parts given soprano and bass             | SATISFIED | generate_inner_voices greedy + 6 tests covering basic, movement, custom ranges, duration, ordering |

All 8 VLEAD requirements satisfied. No orphaned requirements found — all 8 IDs declared across plans 07-01 and 07-02 map to this phase in REQUIREMENTS.md.

### Anti-Patterns Found

| File                                       | Line | Pattern      | Severity | Impact                                          |
|--------------------------------------------|------|--------------|----------|-------------------------------------------------|
| `src/cadenza/analysis/voiceleading.py`     | 386  | `return []`  | INFO     | Intentional early-return for empty score; covered by test_check_voice_leading_empty_score — NOT a stub |

No blockers or warnings found.

### Human Verification Required

None. All behaviors are deterministic and fully covered by automated tests.

### Gaps Summary

No gaps. All 12 must-haves verified, all 8 requirements satisfied, all 27 tests pass, full suite (646 tests) green.

---

_Verified: 2026-03-20T10:00:00Z_
_Verifier: Claude (gsd-verifier)_
