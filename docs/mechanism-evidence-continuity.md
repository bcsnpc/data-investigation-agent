# Mechanism evidence survives the provider view

2026-10-03. Part B design was committed as `f3523ba` before implementation;
see [the ranked choice and limits](autonomous-round-part-b-design.md).

The A7 synthesis model was given receipt identities and boundary facts, but not
the retained definition operations or completed judge explanation. Three output
attempts restated path facts and included a digit-bearing native identifier,
correctly rejected by the existing mechanism-only prose validator. Those failures
remain failures; this change neither relaxes validation nor regrades them.

The provider spine now carries each complete definition-evidence entry, including
its opaque retained operation text, judgment, provenance and limitations. It uses
a deep copy of the entry, not a second field allowlist. This is a display copy;
the original observations remain the sole validation authority. It is retained
definition evidence, not a claim that the entire transformation file was collected
or that every operation is supported. A definition with too much content is elided
as one named whole unit and triggers the existing deterministic local rendering;
source prose is never silently shortened. Citation preflight still resolves
references against the original completed store before dispatch.

Producer instructions now obtain forbidden path-account and limitation terms
directly from the consumer-owned constants. They explicitly cover digits inside
native identifiers. The provider's schema cannot enforce this regex vocabulary;
local validation remains binding. The instructions do not guarantee model
compliance, and no new retry, fallback classification or permissive repair exists.

Measured wire-payload characters on preserved A7 context:

| Family | Before | After | Evidence | Boundaries | Mechanism entries |
|---|---:|---:|---:|---:|---:|
| A | 3,649 | 7,479 | 8 → 8 | 2 → 2 | 0 → 1 |
| E | 3,704 | 7,570 | 8 → 8 | 2 → 2 | 0 → 1 |
| G | 3,758 | 7,582 | 8 → 8 | 2 → 2 | 0 → 1 |
| I | 3,595 | 7,426 | 8 → 8 | 2 → 2 | 0 → 1 |

No candidate, evidence or boundary was dropped; no unit was elided at the 48,000
character view bound. This seam has no directory or SQL-object directory: both
counts remain zero. The instruction vocabulary adds constant per-call text,
independent of the number of directory entries. Intake and investigation views
are unchanged. The permanent coverage test asserts unchanged evidence and
candidate counts, while another asserts complete future definition fields survive.

Seventeen focused tests passed. The stable full suite reported **1,665 tests, OK**
in 475.782 seconds. Its existing SQLite ResourceWarnings were written through
PowerShell's error stream, so that redirected shell command returned status 1
despite the unittest OK summary; the raw log is preserved. Six-check CI results
are recorded on the PR. No investigation run, estate read or new ledger row for this
implementation. No ratio decomposition, filtered-lower comparison, inferred
binding, latency producer, permission or fixture change. Prior freezes are
invalidated by the engine bytes and changed provider payload. Historical tapes
remain intact and are not byte-exact replays of the new request.
