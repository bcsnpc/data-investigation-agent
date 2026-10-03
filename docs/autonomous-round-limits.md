# Approved autonomous-round limits

2026-10-03, Part A1. #330 merged as `5de52ba` after all six checks passed.
The user's autonomous-round instruction authorises 300 rolling physical requests
and 12 diagnostic reads per new run. These are not the routing/evidence fixes.

The secret-free operator profile is `infra/runtime/autonomous-round-limits.json`.
It applies only to the existing approved environment. Its local usage policy now
uses 300 for the rolling physical allowance; subsequent round harnesses read 12
from this profile when constructing their workspace. Application defaults and
other environments are unchanged. No in-progress run was present at the change.

| Control-plane read | Before | After |
| --- | --- | --- |
| Rolling physical allowance | 60 | 300 |
| Ordinary physical reservations charged | 60 | 60 |
| Available ordinary requests | 0 | 240 |
| Per-run diagnostic cap | 4, previous batch | 12, new round profile |
| Policy hash | `db0c9b6110a4c7f09bd872fdc65e544f883ee2215d000eb4abe20b5409d384fa` | `25aee49071b772a2ee8bfce68c01e94c2f0a2d6e1e5d74ac9f50c56934d51ce4` |

Before/after JSON reads are retained separately under
`.local/autonomous-round-20261003/limits-before.json` and `limits-after.json`.
Every existing usage row was compared unchanged. No counters were reset,
reservations refunded, credits granted or old run envelopes rewritten. A distinct
CONTROL_PLANE_CHANGE ledger entry records which limits subsequent rows use;
it is not an investigation run. No estate read or model call occurred.

The ordinary allowance bounds physical requests against the estate over a rolling
24 hours, including guards and failed requests. The diagnostic cap bounds useful
investigation operations per run; guard overhead remains separately counted.
Both limits refuse before additional work is sent. Existing batch-credit rules,
restoration reservation rules, model limits and discovery approval are unchanged.
Configuration here is the experiment ceiling, not evidence of reachability.

The regression test loads the approved profile, fills the previous window,
changes the limit without changing its reservations, then proves the new boundary
refuses the next request. This configuration/test change does not change engine
bytes; previous freezes remain invalidated by earlier work. A2 must still be
tested under a four-read cap. No live investigation in this PR.
