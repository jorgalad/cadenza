---
phase: 11-algorithmic-composition
verified: 2026-03-22T17:00:00Z
status: passed
score: 10/10 must-haves verified
re_verification: false
---

# Phase 11: Algorithmic Composition Verification Report

**Phase Goal:** Users can generate new musical material using algorithmic techniques trained on or constrained by existing phrases
**Verified:** 2026-03-22
**Status:** PASSED
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| #  | Truth | Status | Evidence |
|----|-------|--------|----------|
| 1  | A first-order Markov chain trained on a phrase generates melodies whose consecutive pitch transitions all appear in the training phrase | VERIFIED | `test_markov_melody_transitions_valid` in `test_markov.py` passes; `markov_melody` uses look-ahead to guarantee valid pairs; 40 tests pass |
| 2  | A higher-order (order=2+) Markov chain produces different results than order=1 on same training data with same seed | VERIFIED | `test_higher_order_differs` asserts `r1 != r2`; passes |
| 3  | An L-system with rules {'A': 'AB', 'B': 'A'} and 3 generations expands axiom 'A' to 'ABAAB' and translates via alphabet to a 5-note Phrase | VERIFIED | `test_lsystem_expansion` asserts `len(result) == 5` and `result == (c4_q, e4_q, c4_q, c4_q, e4_q)`; passes |
| 4  | `probabilistic_melody` with seed produces identical output on repeated calls | VERIFIED | `test_probabilistic_melody_seeded` asserts two calls with `seed=42` are equal; passes |
| 5  | `tendency_mask_melody` generates notes biased toward low pitches at position 0.0 and high pitches at position 1.0 when given a rising mask | VERIFIED | `test_tendency_mask_low_to_high` asserts first-half average MIDI is lower than second-half; passes |
| 6  | `random_walk` stays within the given scale — every generated pitch belongs to the scale | VERIFIED | `test_random_walk_stays_in_scale` checks pitch class membership for every event; passes |
| 7  | `generate_variations(phrase, 3)` returns exactly 3 distinct Phrases | VERIFIED | `test_generate_variations_count` asserts `len(result) == 3`; passes |
| 8  | First variation is `chromatic_transpose(phrase, +1 semitone)` | VERIFIED | `test_first_variation_is_transpose_up_1` asserts `result[0] == chromatic_transpose(phrase, Interval("m", 2, 1))`; passes |
| 9  | Variations follow the locked priority order: transpositions, invert, retrograde, augment, diminish, rotations | VERIFIED | Tests at indices 11 (invert), 12 (retrograde), 13 (augment), 14 (diminish), 15 (rotate 1) all pass |
| 10 | Requesting more variations than unique transforms causes cycling back to the start | VERIFIED | `test_variations_cycle` asserts `result[0] == result[total_unique]`; passes |

**Score:** 10/10 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/cadenza/composition/__init__.py` | Package init with re-exports of all composition functions | VERIFIED | 22 lines; exports `MarkovModel`, `train_markov`, `markov_melody`, `lsystem_melody`, `probabilistic_melody`, `tendency_mask_melody`, `random_walk`, `generate_variations` in `__all__` |
| `src/cadenza/composition/markov.py` | `MarkovModel` frozen dataclass, `train_markov`, `markov_melody` | VERIFIED | 148 lines; `@dataclass(frozen=True, slots=True)`, full train/generate logic, look-ahead dead-end avoidance |
| `src/cadenza/composition/lsystem.py` | `lsystem_melody` | VERIFIED | 43 lines; string-rewriting loop with alphabet translation |
| `src/cadenza/composition/stochastic.py` | `probabilistic_melody`, `tendency_mask_melody`, `random_walk` | VERIFIED | 160 lines; all three functions with instance-based RNG |
| `src/cadenza/composition/variation.py` | `generate_variations` and `_chromatic_interval` helper | VERIFIED | 94 lines; deterministic transform list with modular cycling; lambda default-arg capture |
| `tests/composition/test_markov.py` | Tests for ALGO-01, ALGO-02 | VERIFIED | 9 tests: train_markov (4) and markov_melody (5) |
| `tests/composition/test_lsystem.py` | Tests for ALGO-03 | VERIFIED | 5 tests covering expansion, zero generations, unknown symbols, negative generations, empty alphabet |
| `tests/composition/test_stochastic.py` | Tests for ALGO-04, ALGO-05, ALGO-06 | VERIFIED | 14 tests (confirmed by test run count) |
| `tests/composition/test_variation.py` | Tests for ALGO-07 | VERIFIED | 12 tests covering count, priority order at all indices, cycling, edge cases |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `src/cadenza/composition/markov.py` | `cadenza.transforms.pitch.from_midi` | import | WIRED | Line 15: `from cadenza.transforms.pitch import from_midi`; used on line 146 in `markov_melody` |
| `src/cadenza/composition/stochastic.py` | `cadenza.transforms.pitch.nearest_in_scale` | import | WIRED | Line 18: `from cadenza.transforms.pitch import from_midi, nearest_in_scale`; used in `random_walk` on lines 131, 145 |
| `src/cadenza/composition/stochastic.py` | `cadenza.theory.scales.Scale` | import | WIRED | Line 17: `from cadenza.theory.scales import Scale`; used as type annotation in `random_walk` signature |
| `src/cadenza/composition/__init__.py` | `cadenza.composition.markov` | re-export | WIRED | Line 4: `from cadenza.composition.markov import MarkovModel, markov_melody, train_markov` |
| `src/cadenza/composition/variation.py` | `cadenza.transforms.pitch.chromatic_transpose` | import | WIRED | Line 14: `from cadenza.transforms.pitch import chromatic_transpose, invert`; used in transform list |
| `src/cadenza/composition/variation.py` | `cadenza.transforms.melodic.pitch_retrograde` | import | WIRED | Line 13: `from cadenza.transforms.melodic import pitch_retrograde, rotate`; used in transform list |
| `src/cadenza/composition/variation.py` | `cadenza.transforms.rhythm.augment` | import | WIRED | Line 15: `from cadenza.transforms.rhythm import augment, diminish`; used in transform list |
| `src/cadenza/composition/__init__.py` | `cadenza.composition.variation` | re-export | WIRED | Line 10: `from cadenza.composition.variation import generate_variations` |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| ALGO-01 | 11-01 | First-order Markov chain melody generation from a trained phrase | SATISFIED | `train_markov(phrase, order=1)` + `markov_melody`; 5 dedicated tests pass |
| ALGO-02 | 11-01 | Higher-order Markov chain generation (configurable order) | SATISFIED | `train_markov(phrase, order=2)` verified; `test_higher_order_differs` confirms distinct output |
| ALGO-03 | 11-01 | L-system melody/rhythm generation with configurable rules | SATISFIED | `lsystem_melody`; 5 tests including Fibonacci expansion verification |
| ALGO-04 | 11-01 | Probabilistic note selection from a weighted pitch set | SATISFIED | `probabilistic_melody`; reproducibility + weight bias + length + error tests pass |
| ALGO-05 | 11-01 | Tendency mask application (pitch probability varies over time) | SATISFIED | `tendency_mask_melody`; time-varying `t = i / max(length-1, 1)` formula verified |
| ALGO-06 | 11-01 | Random walk melody generation within scale/interval constraints | SATISFIED | `random_walk`; scale membership and step-size tests pass |
| ALGO-07 | 11-02 | Generate variations on a theme (systematic application of transforms) | SATISFIED | `generate_variations`; full priority order tested at every index including cycling |

**No orphaned requirements.** All 7 ALGO-01 through ALGO-07 IDs were claimed by the plans and confirmed satisfied. REQUIREMENTS.md tracker shows all 7 as `Complete` under Phase 11.

---

### Anti-Patterns Found

None. Scan of all 5 source files in `src/cadenza/composition/` found no TODO/FIXME/HACK/PLACEHOLDER comments, no empty returns (`return null`, `return {}`, `return []`), and no stub implementations. Every function has substantive logic.

---

### Human Verification Required

None. All behavioral claims are testable via the automated suite (40 tests, all passing). There are no UI components, external service integrations, or real-time behaviors requiring human observation.

---

### Summary

Phase 11 is fully achieved. All 7 algorithmic composition requirements (ALGO-01 through ALGO-07) are implemented in substantive, well-tested code:

- **Plan 11-01** delivered 6 generative algorithms: Markov chain (orders 1 and 2+), L-system, and three stochastic generators (probabilistic, tendency mask, random walk). 28 tests cover all code paths including error cases.
- **Plan 11-02** delivered the deterministic variation generator with a locked 15+ transform priority order and modular cycling. 12 tests verify exact output at every priority position.

All 40 composition tests pass. All key wiring links are present and active (not dead imports). No anti-patterns found. The phase goal — users can generate new musical material using algorithmic techniques trained on or constrained by existing phrases — is achieved end-to-end.

---

_Verified: 2026-03-22_
_Verifier: Claude (gsd-verifier)_
