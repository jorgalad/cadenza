---
phase: 08-counterpoint
verified: 2026-03-20T13:30:00Z
status: passed
score: 10/10 must-haves verified
re_verification: false
---

# Phase 8: Counterpoint Verification Report

**Phase Goal:** Users can provide a cantus firmus melody and receive valid species counterpoint lines that follow standard rules
**Verified:** 2026-03-20T13:30:00Z
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| #  | Truth | Status | Evidence |
|----|-------|--------|----------|
| 1  | check_counterpoint detects parallel fifths, parallel octaves, voice crossing, dissonance on beat, and returns CounterpointViolation list sorted by position | VERIFIED | validation.py lines 55-521; test_parallel_fifths_detected, test_parallel_octaves_detected, test_dissonance_on_beat_detected, test_voice_crossing_detected, test_violations_sorted_by_position — all pass |
| 2  | Custom rules dict overrides default severity for individual rules while preserving defaults for unspecified rules | VERIFIED | check_counterpoint builds effective map as `dict(DEFAULT_SEVERITIES); effective.update(rules)` (lines 432-434); test_severity_override_via_rules passes |
| 3  | generate_first_species produces a Phrase where every note is consonant with the corresponding CF note | VERIFIED | generation.py _candidates filters to _CONSONANCES; test_all_notes_consonant passes |
| 4  | First species generation works both above and below the cantus firmus | VERIFIED | above=True/False parameters in generate_first_species; test_above_generates_above_cf and test_below_generates_below_cf pass |
| 5  | Generated first species has no parallel fifths or octaves, begins and ends on perfect consonance, penultimate approaches final by step | VERIFIED | _validate enforces parallel avoidance and perfect boundaries; test_no_parallel_fifths_or_octaves, test_first_note_perfect_consonance, test_last_note_perfect_consonance pass |
| 6  | Second species generates 2 CP notes per CF note, downbeats consonant, offbeats may be passing/neighbor tones | VERIFIED | generate_second_species returns 2x CF length; downbeat constraint in _candidates; test_returns_double_length, test_downbeats_consonant, test_passes_check_counterpoint pass |
| 7  | Third species generates 4 CP notes per CF note, first of four consonant, others may be passing/neighbor/cambiata | VERIFIED | generate_third_species returns 4x CF length; strong beat consonance enforced; test_returns_quadruple_length, test_first_of_four_consonant, test_passes_check_counterpoint pass |
| 8  | Fourth species generates syncopated counterpoint where suspensions resolve stepwise downward | VERIFIED | Held-note suspension model: dissonant pitch must equal previous pitch (preparation), next pitch must be stepwise down (resolution); test_suspensions_resolve_downward, test_passes_check_counterpoint pass |
| 9  | Fifth species generates florid counterpoint mixing rhythmic values from all species | VERIFIED | generate_fifth_species uses per-beat pattern selection (1/2/4 notes) with at least 2 different patterns enforced; test_returns_phrase_with_mixed_durations, test_passes_check_counterpoint pass |
| 10 | Multi-voice generation produces a Score with CF and 1-4 counterpoint voices correctly named | VERIFIED | generate_multi_voice_counterpoint returns Score with ("cf", cf) and ("cp1".."cpN") voices, sorted highest-to-lowest by average MIDI; test_n1_returns_score_with_2_voices, test_n2_returns_score_with_3_voices, test_voices_sorted_highest_to_lowest, test_each_voice_passes_check_counterpoint pass |

**Score:** 10/10 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/cadenza/counterpoint/rules.py` | Consonance classification, default severity map, species rule constants | VERIFIED | PERFECT_CONSONANCES, IMPERFECT_CONSONANCES, DISSONANCES frozensets; DEFAULT_SEVERITIES dict with 11 rules; classify_interval function — all present and substantive |
| `src/cadenza/counterpoint/validation.py` | check_counterpoint and CounterpointViolation dataclass | VERIFIED | CounterpointViolation frozen dataclass with 5 fields (rule, species, position, interval, severity); check_counterpoint with 7 rule checkers; species-aware for 0-5 |
| `src/cadenza/counterpoint/_engine.py` | Backtracking search engine shared by all species generators | VERIFIED | _backtrack recursive DFS with candidates_fn and validate_fn callables; used by all 7 generators |
| `src/cadenza/counterpoint/generation.py` | All 7 generation functions | VERIFIED | generate_first_species, generate_second_species, generate_third_species, generate_fourth_species, generate_fifth_species, generate_free_counterpoint, generate_multi_voice_counterpoint — all present, substantive, and tested |
| `src/cadenza/counterpoint/__init__.py` | Package re-exports of full public API | VERIFIED | 9 symbols exported: CounterpointViolation, check_counterpoint, and all 7 generate_* functions |
| `tests/counterpoint/test_validation.py` | Validation tests | VERIFIED | 16 tests covering all rule types and severity overrides |
| `tests/counterpoint/test_generation.py` | Generation tests | VERIFIED | 44 tests covering all species, direction, range, multi-voice |
| `tests/counterpoint/conftest.py` | Shared test fixtures | VERIFIED | cf_c_major and make_phrase fixtures present |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `validation.py` | `rules.py` | `from cadenza.counterpoint.rules import` | WIRED | Line 11: imports DEFAULT_SEVERITIES, DISSONANCES, IMPERFECT_CONSONANCES, PERFECT_CONSONANCES, classify_interval — all used in validation logic |
| `generation.py` | `_engine.py` | `from cadenza.counterpoint._engine import _backtrack` | WIRED | Line 14 import; _backtrack called at lines 197, 329, 457, 588, 844 — one per species generator |
| `generation.py` | `cadenza.core.interval.Interval` | Interval used via validation | WIRED | Interval imported from cadenza.core.interval; used transitively via from_midi and validation functions |
| `generation.py` | `cadenza.core.score.Score` | generate_multi_voice_counterpoint returns Score | WIRED | Score imported at line 898 (lazy import inside function); Score(_voices=tuple(voices)) at line 964 |
| `validation.py` | `rules.py` | species 2-5 validation using consonance rules | WIRED | Species-specific branches at lines 134-199 use DISSONANCES, PERFECT_CONSONANCES, _CONSONANCES from rules.py |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| CPTR-01 | 08-01 | Generate first-species counterpoint from cantus firmus | SATISFIED | generate_first_species in generation.py; 10 dedicated tests pass |
| CPTR-02 | 08-02 | Generate second-species counterpoint (2 notes against 1) | SATISFIED | generate_second_species; 2x length, downbeat consonance, passing tones; 5 tests pass |
| CPTR-03 | 08-02 | Generate third-species counterpoint (4 notes against 1) | SATISFIED | generate_third_species; 4x length, strong-beat consonance; 4 tests pass |
| CPTR-04 | 08-02 | Generate fourth-species counterpoint (syncopated, suspensions) | SATISFIED | generate_fourth_species; held-note suspension model, stepwise resolution; 4 tests pass |
| CPTR-05 | 08-02 | Generate fifth-species counterpoint (florid, combining all) | SATISFIED | generate_fifth_species; at least 2 different rhythmic patterns per output; 4 tests pass |
| CPTR-06 | 08-01 | Validate counterpoint line against species rules, return violation list | SATISFIED | check_counterpoint with 7 rule checkers; 16 validation tests pass |
| CPTR-07 | 08-01 | Support counterpoint above and below cantus firmus | SATISFIED | above=True/False parameter on all 6 species generators; above/below direction tests pass for all |
| CPTR-08 | 08-02 | Generate two-voice free counterpoint (tonal, not strict species) | SATISFIED | generate_free_counterpoint; relaxed validation, no strict species ratios; 5 tests pass |
| CPTR-09 | 08-02 | Generate three- and four-voice counterpoint from a single melody | SATISFIED | generate_multi_voice_counterpoint(cf, n=1..4); Score output; inter-voice parallel avoidance; 9 tests pass |
| CPTR-10 | 08-01 | Configurable rule severity (error/warning/suggestion) | SATISFIED | rules dict parameter in check_counterpoint; DEFAULT_SEVERITIES overridden per entry; test_severity_override_via_rules passes |

All 10 CPTR requirements satisfied. No orphaned requirements found.

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `generation.py` | 48 | `Pitch("c", "n", 4)  # placeholder` comment | Info | Not a stub — this is the intentional Rest-handling branch in _extract_cf. Rest events have no pitch; middle C is substituted as a neutral positional anchor. The comment label is misleading but the code is correct and covered by tests. |

No blockers. No warnings.

---

### Human Verification Required

None required for this phase. All correctness requirements are covered by the 60-test suite (structural checks, interval arithmetic, parallel motion, suspension resolution, rhythmic ratios, voice ordering). The algorithms are deterministic within backtracking so their behavior is fully testable programmatically.

---

## Summary

Phase 8 goal is fully achieved. All 10 CPTR requirements are implemented across the `src/cadenza/counterpoint/` subpackage:

- **Rules engine** (`rules.py`): consonance classification and default severity map
- **Validation** (`validation.py`): `check_counterpoint` with 7 rule checkers, species-aware for species 0-5
- **Backtracking engine** (`_engine.py`): shared DFS engine used by all 7 generators
- **Generation** (`generation.py`): all 7 functions — first through fifth species, free counterpoint, and multi-voice Score output

The 60-test suite covers every required behavior. Full suite (706 tests) passes with zero regressions. All 9 public API symbols are correctly exported from `cadenza.counterpoint`.

---

_Verified: 2026-03-20T13:30:00Z_
_Verifier: Claude (gsd-verifier)_
