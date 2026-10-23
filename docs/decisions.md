# Decisions

## 2026-10-22 - refresh facts use the existing scanner, not the investigator

Owner approval carried forward from Round 21 permits these two refresh-fact
calls only, for a workspace/model explicitly declared in the scanner policy:

- `GET https://api.powerbi.com/v1.0/myorg/groups/{workspace}/datasets/{model}/refreshes?$top=20`
- `GET https://api.powerbi.com/v1.0/myorg/groups/{workspace}/datasets/{model}/refreshSchedule`

The investigator remains Viewer. No new identity or permission grant is made.
History requires dataset Write permission, which the existing scanner already
holds; the investigator's original 403 remains evidence. Schedule GET has a
separate receipt; the old history failure did not establish a schedule failure.
The scanner's pre-existing definition/metadata reads remain unchanged.

`adapters/scanner_policy.py` enforces the two closed refresh URL forms, method,
query, no body and declared scope. `adapters/scanner_refresh.py` binds the exact
two URLs and permits scanner credentials only inside the scanner job context.
Refresh triggers and other writes are refused. Any widening of these refresh
calls requires a new entry here before code changes; a new audience or identity
scope additionally requires the explicit human decision required by CLAUDE.md.

## 2026-10-22 - collector enclosing runtime: 60 to 180 seconds

Owner direction: establish the outer-limit cause if both recorded executions
exceed60s, then correct the envelope and confirm Azure success once. The original
Round21 execution began21:00:00Z and published its final immutable capture at
21:01:09Z (at least69s). Round22's probe began03:29:02Z and published its seal
at03:30:12Z (at least70s). Azure omitted endTime; these are publication-based
duration lower bounds, not invented Azure completion times. The live child's
exit was0, with deadline_expired=false.

Change only job-dia-collectors replicaTimeout from60 to180 seconds. This gives
110s above the observed70s lower bound and permits more than twice that runtime.
Keep image604867fc, CPU0.25/memory0.5Gi, retry0, */30 schedule, identities,
permissions and six-hour listing interval unchanged. The preflight must be
called with an explicit180s pin; it rejects the stale60s envelope. The legacy
new-resource planner remains unchanged and cannot silently infer this approval.

Runtime is a ceiling, not billed duration. Using existing no-free-grant rates,
1488 wakes/month at70s add USD0.781200 compute, giving USD19.878333 including
the prior USD19.077133 platform and USD0.02 storage estimates. At180s on every
wake the sensitivity would be USD21.105933: not an approved budget increase or
a claim that worst-case cost fitsUSD20. Retain theUSD20 actual monthly guard;
observe durations rather than bill the full timeout as expected usage.

Manual confirmation retains max_requests=4. Its FETCH limitation remains a
probe limitation; do not widen it or claim new load facts. The existing
six-hour scheduled collector is the real collector test. Record deployment
readback and confirmation outcome separately. Section1e remains binding.

Applied/read back: replicaTimeout180; other configuration/template/identity
byte-equivalent as structured values. PATCH SHA-256
a0d114ee6403c180a896c056540f55f8a8045e26092a381423617a97705f00f1.
One confirmation execution job-dia-collectors-ue92850: Azure Succeeded in56s,
child exit0 and enclosing exit intent0. max_requests stayed4. No fresh load
fact was appended (UNCHANGED_MARKER); original FETCH limitation retained.
Preflight regression11/11PASS. Full suite is running on ec59eef; three daily
smokes are still required before section2.

## 2026-10-22 amendment - new engine and recording modes

Owner's amended Round22 prompt makes the ledger investigator the default.
`dia run` investigation dispatch now selects it; legacy execution is named
`legacy-baseline` and used only for the requested comparison. A file submission
requires the deployment's pinned investigator_spec; no silent legacy fallback
or invented graph/native scope. The ticket reference changes only the ticket,
not the spec's permitted path or identities.

Real tickets default NORMAL: safe local audit journal, batched immutable audit
uploads/index, queries and retained evidence, answer and bundle. Logical audit
IDs are labelled; they are not Blob URLs or byte-exact tapes. TEST is explicit
and retains full native/provider recording. Existing exact tapes stay unchanged;
NORMAL results cannot be labelled exact replay. The current model context and
one current enterprise context are materialized into a fresh session catalog;
historical scans, observations and other model rows are not copied.

The corrected daily smoke will use the new ledger route. Its result vocabulary
is `as designed` (technical implementation only), rather than the legacy
TRANSFORMATION_LOGIC top-level field. Keep TRANSFORMATION_LOGIC as a required
retained native definition assessment, plus the exact Gold8765/Silver7661 reads
on the same named nodes and a checked non-business DESIGN_CHECK for that pair.
This is a taxonomy adapter and a stronger smoke assertion, not a looser outcome
expectation. A label alone, missing definition, equal operands, unavailable
result or wrong native classification fails. Old smoke captures are unchanged.
