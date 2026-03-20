---
phase: 09-set-theory-serial
verified: 2026-03-20T00:00:00Z
status: passed
score: 15/15 must-haves verified
re_verification: false
---

# Phase 9: Set Theory & Serial Verification Report

**Phase Goal:** Users can perform pitch class set analysis and generate/manipulate 12-tone rows and matrices
**Verified:** 2026-03-20
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `prime_form({0,1,4,6})` returns `(0,1,4,6)` (4-Z15) per Forte | VERIFIED | Test passes; `prime_form(frozenset({0,1,4,6})) == (0,1,4,6)` confirmed |
| 2 | `prime_form({0,1,3,7})` returns `(0,1,3,7)` (4-Z29) per Forte | VERIFIED | Plan had incorrect expectation (conflated Z-pair members); summary documents fix; test passes |
| 3 | `forte_number({0,3,7})` returns `'3-11'` (major/minor triad) | VERIFIED | `forte_number(frozenset({0,3,7})) == '3-11'` confirmed |
| 4 | `interval_vector({0,1,3,7})` returns `(1,1,1,1,1,1)` (all-interval tetrachord) | VERIFIED | Returns `(1,1,1,1,1,1)` confirmed |
| 5 | Z-related sets 4-Z15 and 4-Z29 share interval vector but differ in prime form | VERIFIED | `is_z_related` returns `True`; both have IV `(1,1,1,1,1,1)` |
| 6 | `complement({0,1,2})` returns the 9-element frozenset of remaining PCs | VERIFIED | Returns `frozenset({3,4,5,6,7,8,9,10,11})` confirmed |
| 7 | Similarity measures Rp, R0, R1, R2 return correct boolean results | VERIFIED | All 7 similarity tests pass in test_pcset.py |
| 8 | Webern Op. 21 row `(9,10,3,11,4,8,2,7,0,5,6,1)` constructs successfully | VERIFIED | `ToneRow(pcs=(9,10,3,11,4,8,2,7,0,5,6,1))` creates without error |
| 9 | 12x12 matrix has 0 along the diagonal | VERIFIED | All 12 diagonal entries are 0; top-left is 0 |
| 10 | `P(0)` of any row starts on pitch class 0 | VERIFIED | `webern.prime(0)[0] == 0` confirmed |
| 11 | `R(n)` is the reverse of `P(n)` | VERIFIED | `retrograde(0) == prime(0)[::-1]` confirmed |
| 12 | `RI(n)` is the reverse of `I(n)` | VERIFIED | `retrograde_inversion(0) == inversion(0)[::-1]` confirmed |
| 13 | All-interval row detected correctly; chromatic row is not | VERIFIED | `is_all_interval((0,1,4,2,9,5,11,3,8,10,7,6)) == True`; chromatic `== False` |
| 14 | `realize_row` converts pitch classes to `Pitch` objects in specified octave | VERIFIED | Returns 12 `Pitch` objects; first is `Pitch(step='c', accidental='n', octave=4)` |
| 15 | `segment_row` and `derive_row` work correctly | VERIFIED | Trichord split returns 4 groups of 3; derivation from `{0,3,6,9}` produces valid ToneRow |

**Score:** 15/15 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/cadenza/settheory/_forte_table.py` | FORTE_TABLE dict (208 entries) and PRIME_TO_FORTE reverse index | VERIFIED | 208 entries in both dicts; 230 lines |
| `src/cadenza/settheory/pcset.py` | 14 pure functions for SETTH-01 through SETTH-09 | VERIFIED | All 14 functions present; 181 lines; substantive implementations |
| `src/cadenza/settheory/serial.py` | ToneRow dataclass + 5 standalone functions | VERIFIED | ToneRow with P/I/R/RI/matrix methods; all 5 functions present; 255 lines |
| `src/cadenza/settheory/__init__.py` | Re-exports all 20 public symbols | VERIFIED | Exports all 14 pcset functions + 6 serial symbols in `__all__` |
| `tests/settheory/test_pcset.py` | Unit tests for all 9 SETTH requirements | VERIFIED | 351 lines; 57 tests covering all requirements |
| `tests/settheory/test_serial.py` | Unit tests for all 6 SERI requirements | VERIFIED | 271 lines; 36 tests covering all requirements |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `src/cadenza/settheory/pcset.py` | `src/cadenza/settheory/_forte_table.py` | `from cadenza.settheory._forte_table import FORTE_TABLE, PRIME_TO_FORTE` | WIRED | Import at line 11 of pcset.py; both names used in forte_number and prime_form |
| `src/cadenza/settheory/__init__.py` | `src/cadenza/settheory/pcset.py` | re-export all 14 public functions | WIRED | Lines 3-18 of `__init__.py`; all 14 names imported and in `__all__` |
| `src/cadenza/settheory/serial.py` | `src/cadenza/transforms/pitch.py` | `from cadenza.transforms.pitch import from_midi` | WIRED | Line 13 of serial.py; `from_midi` used in `realize_row` |
| `src/cadenza/settheory/serial.py` | `src/cadenza/settheory/pcset.py` | `from cadenza.settheory.pcset import prime_form` | WIRED | Line 12 of serial.py; `prime_form` used in `derive_row` |
| `src/cadenza/settheory/__init__.py` | `src/cadenza/settheory/serial.py` | re-export ToneRow and serial functions | WIRED | Lines 19-26 of `__init__.py`; all 6 serial symbols imported and in `__all__` |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| SETTH-01 | 09-01 | Compute prime form of a pitch class set | SATISFIED | `prime_form()` in pcset.py; Forte (1973) algorithm; 7 tests pass |
| SETTH-02 | 09-01 | Compute interval vector | SATISFIED | `interval_vector()` in pcset.py; 4 tests pass |
| SETTH-03 | 09-01 | Determine Forte number | SATISFIED | `forte_number()` in pcset.py; 4 tests pass |
| SETTH-04 | 09-01 | Look up pitch class set by Forte number | SATISFIED | `lookup_by_forte()` in pcset.py; 4 tests pass |
| SETTH-05 | 09-01 | Compute complement | SATISFIED | `complement()` in pcset.py; 4 tests pass |
| SETTH-06 | 09-01 | Compute inversion | SATISFIED | `invert_pcs()` in pcset.py; 3 tests pass |
| SETTH-07 | 09-01 | Compute transposition | SATISFIED | `transpose_pcs()` in pcset.py; 4 tests pass |
| SETTH-08 | 09-01 | Test set relationship: subset, superset, Z-relation | SATISFIED | `is_subset`, `is_superset`, `is_z_related` in pcset.py; 6 tests pass |
| SETTH-09 | 09-01 | Similarity measures (Rp, R0, R1, R2) | SATISFIED | `rp_relation`, `r0`, `r1`, `r2` in pcset.py; 7 tests pass |
| SERI-01 | 09-02 | Define a 12-tone row from a list of pitch classes | SATISFIED | `ToneRow` frozen dataclass; validates 12 unique PCs; 4 tests pass |
| SERI-02 | 09-02 | Generate the complete 48-form matrix (P, I, R, RI) | SATISFIED | `prime`, `inversion`, `retrograde`, `retrograde_inversion`, `matrix` methods; 11 tests pass |
| SERI-03 | 09-02 | Detect special row properties (all-interval, combinatoriality) | SATISFIED | `is_all_interval`, `is_combinatorial` functions; 6 tests pass |
| SERI-04 | 09-02 | Realize a row form as pitched notes | SATISFIED | `realize_row` with fixed-octave and nearest-note modes; 4 tests pass |
| SERI-05 | 09-02 | Segmentation of a row into trichords/tetrachords/hexachords | SATISFIED | `segment_row` with arbitrary sizes tuple; 3 tests pass |
| SERI-06 | 09-02 | Row derivation from a smaller set | SATISFIED | `derive_row` from frozenset seed; 3 tests pass |

All 15 phase requirements satisfied. REQUIREMENTS.md traceability table already marks all 15 as Complete under Phase 9.

---

### Anti-Patterns Found

None. No TODO/FIXME/HACK/PLACEHOLDER comments found in any implementation or test file. No stub return values. All functions have substantive implementations.

---

### Human Verification Required

None required. All behaviors are programmatically verifiable and confirmed by the test suite.

---

### Regression Check

Full test suite: **799 passed in 4.03s** — no regressions introduced by this phase.

---

### Notes on Plan Deviations

The PLAN frontmatter for 09-01 specified `prime_form({0,1,3,7}) returns (0,1,4,6)` as a must-have truth. This was incorrect — `{0,1,3,7}` is set class 4-Z29 with prime form `(0,1,3,7)`, not `(0,1,4,6)` (which is 4-Z15). The implementation correctly produces `(0,1,3,7)` per Forte, and the SUMMARY documents this as a test data bug that was fixed. The plan's underlying intent (that Z-related sets are handled correctly) is fully satisfied.

---

_Verified: 2026-03-20_
_Verifier: Claude (gsd-verifier)_
