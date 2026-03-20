# Phase 8: Counterpoint - Context

**Gathered:** 2026-03-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 8 delivers counterpoint generation and validation operating on `Phrase` objects:

1. **Species generation (CPTR-01..05, CPTR-07)** — generate a counterpoint line for a given cantus firmus, for species I–V, above or below the CF.
2. **Validation (CPTR-06, CPTR-10)** — validate an existing counterpoint line against species rules, returning a structured violation list with configurable severity.
3. **Free counterpoint (CPTR-08)** — generate two-voice tonal counterpoint (not strict species).
4. **Multi-voice (CPTR-09)** — generate 2–4 counterpoint voices from a single melodic line, returning a `Score`.

New module: `src/cadenza/counterpoint/` or `src/cadenza/analysis/counterpoint.py`. Depends on Phase 1 (`Pitch`, `Interval`, `Phrase`, `Score`) and Phase 7 (`check_voice_leading` for shared voice-leading rules).

</domain>

<decisions>
## Implementation Decisions

### Area 1: Generation Output Structure

- **Return type:** All generation functions return a plain `Phrase` — composable with all existing transforms and analysis functions.
- **No rich result type:** Caller runs `check_counterpoint()` separately if they want violations. Single responsibility.
- **One function per species:**
  ```
  generate_first_species(cf: Phrase, above: bool = True, range: tuple[Pitch, Pitch] | None = None) -> Phrase
  generate_second_species(cf: Phrase, above: bool = True, range: tuple[Pitch, Pitch] | None = None) -> Phrase
  generate_third_species(cf: Phrase, above: bool = True, range: tuple[Pitch, Pitch] | None = None) -> Phrase
  generate_fourth_species(cf: Phrase, above: bool = True, range: tuple[Pitch, Pitch] | None = None) -> Phrase
  generate_fifth_species(cf: Phrase, above: bool = True, range: tuple[Pitch, Pitch] | None = None) -> Phrase
  ```
- **`above: bool = True`** — `True` generates the counterpoint voice above the CF, `False` below.
- **`range: tuple[Pitch, Pitch] | None = None`** — optional `(low, high)` pitch constraint; `None` means unconstrained. Same pattern as `generate_inner_voices` from Phase 7.
- **Free counterpoint:**
  ```
  generate_free_counterpoint(cf: Phrase, above: bool = True, range: tuple[Pitch, Pitch] | None = None) -> Phrase
  ```
  Tonal voice-leading conventions (no parallel 5ths/8ths, consonant beat emphasis) but no strict species rhythmic ratios.
- **Generation is always strict:** Generation functions never accept a `rules` param — they always produce counterpoint satisfying the strict default rule set.

### Area 2: Species Violation Report

- **New dataclass** — `CounterpointViolation` (not reusing `VoiceLeadingViolation` from Phase 7):
  ```python
  @dataclass(frozen=True, slots=True)
  class CounterpointViolation:
      rule: str        # snake_case, e.g. 'parallel_fifth'
      species: int     # 1-5 (or 0 for free counterpoint)
      position: int    # 0-based note index in CF
      interval: Interval
      severity: str    # 'error' / 'warning' / 'suggestion'
  ```
- **Validation function:**
  ```python
  def check_counterpoint(
      cf: Phrase,
      counterpoint: Phrase,
      species: int,          # 1-5, or 0 for free counterpoint
      rules: dict[str, str] | None = None,
  ) -> list[CounterpointViolation]: ...
  ```
  Returns all violations sorted by position.
- **Default severity assignments:**
  - `'error'`: `parallel_fifth`, `parallel_octave`, `direct_octave`, `dissonance_on_beat`, `voice_crossing`, `unresolved_suspension`
  - `'warning'`: `large_leap`, `repeated_note`, `voice_overlap`
  - `'suggestion'`: `augmented_leap`, `climax_placement`

### Area 3: Configurable Rule Severity (CPTR-10)

- **`rules: dict[str, str] | None = None`** on `check_counterpoint` only.
  - `None` = use default severity assignments.
  - Dict overrides: `{'parallel_fifth': 'warning', 'large_leap': 'suggestion'}` — only specified rules are overridden; unspecified rules keep their defaults.
- **Generation functions are not configurable** — they always apply the strict rule set.

### Area 4: Multi-Voice Generation (CPTR-09)

- **Signature:**
  ```python
  def generate_multi_voice_counterpoint(
      cf: Phrase,
      n: int = 2,                       # number of counterpoint voices (1-4)
      species: int = 1,                 # species for all generated voices
      above: int | None = None,         # how many voices go above CF (None = all above)
  ) -> Score: ...
  ```
- **Return type:** `Score` — existing `cadenza.core.Score` with named voice pairs.
  - CF is included as `('cf', cf_phrase)`.
  - Generated voices are `('cp1', phrase1)`, `('cp2', phrase2)`, etc., ordered from highest to lowest.
- **ValueError:** Raised for `n > 4` or empty CF. These are the only validated error conditions.
- **All voices use the same species** (`species=1` default).

### Claude's Discretion

- Algorithm for generating each species (backtracking, greedy, or weighted random — whatever produces valid counterpoint reliably).
- How to handle `above` param when `n=2` — if `above=None`, both voices above CF by default.
- Rule names beyond those listed in defaults (additional species-specific rules Claude identifies during implementation).
- Module location: `src/cadenza/counterpoint/` package or `src/cadenza/analysis/counterpoint.py` file (follow scope guidance from research).

</decisions>

<canonical_refs>
## Canonical References

No external specs — requirements fully captured in decisions above.

### Phase requirements
- `.planning/REQUIREMENTS.md` — CPTR-01 through CPTR-10 (full spec for each species and operation)

### Prior phase patterns to follow
- `src/cadenza/analysis/voiceleading.py` — `VoiceLeadingViolation` frozen dataclass + pure functions pattern; `check_voice_leading` as model for `check_counterpoint`; `generate_inner_voices` as model for multi-voice generation
- `src/cadenza/core/score.py` — `Score` type (return type for multi-voice generation)
- `src/cadenza/core/phrase.py` — `Phrase` type (CF input and counterpoint output)
- `src/cadenza/core/interval.py` — `Interval.between` for consonance/dissonance checking

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `cadenza.analysis.voiceleading.check_voice_leading(score)` — already checks parallel 5ths/8ths, crossing, overlap; counterpoint validation can delegate shared checks here rather than reimplementing
- `cadenza.analysis.voiceleading.VoiceLeadingViolation` — reference for CounterpointViolation field structure
- `Interval.between(p1, p2)` (`cadenza.core.interval`) — semitone and interval quality; central to consonance checking on each beat
- `cadenza.transforms.pitch.from_midi` — needed in generation to build Pitch objects from MIDI numbers

### Established Patterns
- Frozen dataclasses: `@dataclass(frozen=True, slots=True)` for all result types
- `ValueError` for invalid inputs (size mismatches, n > 4, empty inputs)
- Module in `cadenza.analysis.*` or new `cadenza.counterpoint.*` subpackage — planner decides based on scope
- Snake_case string constants for rule names

### Integration Points
- New module: `src/cadenza/counterpoint/` or `src/cadenza/analysis/counterpoint.py`
- `cadenza.__init__` re-exports need updating with `CounterpointViolation`, `check_counterpoint`, all 7 generation functions
- Tests: `tests/counterpoint/` or `tests/analysis/test_counterpoint.py`

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 08-counterpoint*
*Context gathered: 2026-03-20*
