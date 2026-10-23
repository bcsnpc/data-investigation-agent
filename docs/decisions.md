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

The amended soft-gate/source-availability rule applies to access preflight too:
new investigations and daily smokes retain a failed source-access table as a
warning and inspect reachable layers. Standalone probes keep their failed
access report. Gateway, scope, identity, read-only and secret guards still run
on every native read and still propagate hard stops. No owner/alternate-reader
fallback or permission is added; the inaccessible layer becomes blocked in
the delivered result. Regression preserves this distinction.


### Status refresh owner steer ? 2026-10-23 (owner instruction 2026-10-22)
Status questions now attempt `refresh_facts` on stale/missing admitted-path facts before answering. A missing collector is a failed route, classified QUERY_ERROR, rather than permission to return a stale status. Refresh permission/network failures retain the source-availability class, observation time and owner; hard guardrail/budget failures still propagate. Fresh ledger facts require no top-up. On-demand force now reaches the underlying incremental collector, so an unchanged run marker cannot prevent renewing stale observations. The cloud status spec will bind only the fixture pipeline's existing metadata route (no audit SQL, no off-path subjects); existing scheduled/manual audit limits remain unchanged.
The first NORMAL status execution job-dia-worker-rgjhvlg took 38s Azure start-to-end, with 1.793382s admission/path and 1.839225s investigation (engine loop 0.360824s, inclusive). This missed the <30s total target. Startup was not separately recorded in that old sidecar; remaining time is not falsely labelled startup. New observational sidecars include UTC worker timing start for comparison with Azure's execution start, separately from investigation and publication. No old capture or receipt changed.
Full corrected-image 5c25dc6 suite: 5,050 PASS / 48 skipped, no errors, 683.078s. New-engine smoke job-dia-worker-hu1s138 finished Azure Succeeded in 288s but smoke FAIL (family-A check); not a passing smoke. Its sealed capture remains unchanged. Three consecutive new-engine smoke passes are not yet earned.


### Owner status-job timing target ? 2026-10-23
For this round only, accept job-based status runs below60s total and record startup/investigation/publication separately. Do not optimize container startup; a future warm service is deferred. Full-investigation target remains below120s. The measured52s status run therefore meets the amended target; original measurements and the prior30s target are retained in its receipt. No runtime budget, quota or resource configuration changed.

2026-10-23 owner steer before first Section3 dev score: successful exact calls now reuse the stored case result; verdict rejection transfers next-step selection to code; phase progress limits advance or end honestly. Initial exploratory no-progress limit3; each deterministic frontier action is attempted once before advancing. Budgets, comparison context and evidence requirements unchanged. This explicitly amends the earlier prohibition on adding per-phase limits for this behaviour; it adds no expense authority. Old captures and the18-call not-found result remain unchanged.

2026-10-23 DECIDED WITHOUT REVIEW ? Round22 fairness: preserve both independent reviews and include all12original R17questions unchanged. Rejected alternative: remove tickets9/11 merely because the second model returnedfalse. R17-09 relies on unprovided label relationships, and11false contradicts its ownfair conclusion. These do not establish unfairness. Missing essentials may yield one legitimate question; inclusion does not promise an immediate verdict. No expected answer or engine behavior changed. Receipts docs/runs/round-twenty-two-fairness-first-review.json and round-twenty-two-fairness-clarified-review.json.

2026-10-23 DECIDED WITHOUT REVIEW ? Round22 raw-ticket wiring exposes an operational referent gap: the existing four-field FACTrequest only selected the latest run even when the quoted ticket named an earlier starttime. Add optional consumer-validated run_selector inside that existing request, with quoted source and stated timestamp precision; never pass it beside the contract. Select only a unique record from current retained history; missing, ambiguous, contradictory or finer-than-retained references refuse without latest substitution. Remove the original fact hash from the derived selected view and retain its source_fact_id. Adapter preserves producer timestamps through9fractional digits, refuses finer input instead of truncating it, and old ledger rows remain unchanged. Rejected alternative: manually fill targets from expected answers or reinterpret a historical question as latest. Eight new selector tests and existing fact/consumer/frontier regressions pass; no estate/model call during the fix.

2026-10-23 Round22 run-selection follow-up: each timestamp mention is explicitly a run target, a ticket/request/screenshot context, or unresolved. A ticket-created timestamp cannot become the requested run; unresolved roles ask/refuse, never disappear. Consumer re-derives the quoted selector to reject a caller choosing a contextual timestamp. New regression covers latest request plus unrelated logged time. Cloud offline matrix now explicitly includes frontier, controlled-fault, selector and raw-admission tests, with a coverage assertion preventing silent omission. No estate or investigator-model call in this fix; new exact-source validation pending.

2026-10-23 DECIDED WITHOUT REVIEW ? Repeated publisher-control stalls were in SharedUsage.mirror, a private reporting view, after authoritative admission. Add an explicit reporting_mirror=False option for untaped build controls only. It inherits the same SharedUsage reserve/settle implementation and monthly caps; only the unused private display mirror is omitted. Default investigator/scanner behavior is unchanged; TEST/legacy opt-out is refused. Real offline shared-ledger tests prove settlement/charge preservation and that a full1000SCAN ledger refuses before dispatch. Rejected alternatives: bypass or relax admission, discard the orphan charge, or keep accumulating native-control failures because a display mirror stalled. Existing partials remain; no permission, identity or budget ceiling changed.

2026-10-23 DECIDED WITHOUT REVIEW: successful get_evidence repeats return the stored result to code but only reference feedback to the model; resending the saved raw body was rejected because it defeats compact context. Original evidence and case bytes remain retained. Regression plus core/cloud64PASS. Source before-state control40613 then40615 retained; no mutation or network widening. A prepared single existing-rule replacement is in owner-actions, not executed.

2026-10-23 DECIDED WITHOUT REVIEW: untaped publisher controls with reporting_mirror=False now report current shared monthly physical counters directly, rather than reconstruct unused historical daily/model reports first. Two original source preflights lost their PostgreSQL connection inside the full snapshot before estate dispatch (0 source reads/mutations), preserved separately. Shared reserve/settle and monthly cap unchanged; ordinary and TEST meters unchanged. Tests prove pending cross-estate reads remain counted, pre-adoption history excluded, exhausted SCAN still refuses before dispatch, and exact/legacy modes cannot opt out. Focused27PASS. This narrows the failing report; no claim that the underlying network/driver cause is established.

2026-10-23 DECIDED WITHOUT REVIEW: source-history injection plans use insert/delete of new synthetic records instead of updating existing rows, so restoration can preserve every original row and its rowversion. A database-wide rowversion advance is explicitly irreversible metadata, not represented as exact rollback. Plans refuse stale preimages, existing IDs, malformed literals and changed native insert receipts; publisher must journal before dispatch and reconcile uncertainty. No source mutation applied during preparation. Existing cloud reader, not owner control data, will supply diagnostic observations.

2026-10-23 DECIDED WITHOUT REVIEW: database permission guard recognizes VIEW PERFORMANCE DEFINITION and VIEW SECURITY DEFINITION because the served SQL builtin hierarchy covers them under the already-approved VIEW DEFINITION grant. Do not loosen for CONTROL, write/execute/impersonation or unknown names; native predicate tests prove these refuse. Add own-session principal/count/guard name to safe refusal records, preserving original driver-text exclusion. Rejected alternative: change reader roles or silently omit the guard. The original cloud refusal lacks names/count, so causal inference remains pending corrected-image confirmation. No SQL role or identity changed, and the Section1 manual collector cap remains4.

2026-10-23 DECIDED WITHOUT REVIEW: classify numericSQL40613 at connection stage as a transient enclosing-run retry, using existing two retries and30/45second waits. Do not raise runtime, worker or budget limits; do not retry permission229, query-stage40613, model authorization/billing or read-only guard refusal. Preserve each original attempt in its separate directory. Trigger: sourceprofile02 nativeconnect40613 with later observed database resumption.
