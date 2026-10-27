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

2026-10-23 DECIDED WITHOUT REVIEW: fix observedSQL529 by schema type, never a column-name exception. The existing SQLprofile compiler takes an optional complete declared type map; binary values use hex after varbinary conversion, normal scalar/untyped request bytes stay unchanged. Schema evidence is required for typed profile production. Unknown types refuse before SQL; profiles explicitly remain NOT_EQUALITY_PROOF. Rejected alternative: drop source_row_version from this fixture to conceal the compiler defect.57focusedtestsPASS; cloud typed-query confirmation pending.

2026-10-23 DECIDED WITHOUT REVIEW: restrict build-phase shared physical admission SQL to its already-governing month/adoption interval, allocations joined on all three identity keys; retain the same transaction, owner checks and physical_status guard. Old/model history outside this period cannot affect this monthly decision. Rejected: increasing PGtimeouts, bypassing reservation or releasing another owner's reservation. Connection error is not claimed diagnosed.32focusedtestsPASS.

Owner standing approval under section8, 2026-10-23: whenever the laptop public IP changes, replace only the existing laptop /32 firewall rules on sql-orderops-9696025 (investigator-client-20260918) and pg-dia-d5dd7d65 (OwnerCurrentIp) with the independently confirmed current IP, then read back. Never add a rule or widen a range; do not change AllowAzureServices or any identity/permission. Record before/after for every replacement. PostgreSQL diagnostic read today already matches184.105.12.85/32, so no PostgreSQL mutation was made. Receipt docs/runs/round-twenty-two-postgres-diagnosis.json.

2026-10-23 DECIDED WITHOUT REVIEW: apply the standing two-transient-retry policy to untaped control budget reservations only. Retry the same immutable owner/key/request, not the mutation. Recognized errors are connection loss/timeout and explicit PGtransport/admin-shutdown/idle-timeout classes; SQL query, authentication, permission and usage-policy errors refuse immediately. Preserve short retry metadata without SQL arguments. Rejected: blindly retry publisher mutations, bypass budgets, widen timeouts, or claim an unproved firewall cause.

2026-10-23 owner PostgreSQL steer implemented: central connector enforces keepalives1/idle30s/interval10s/count3, connect timeout15s. Shared transactions get fresh connections and close before external work; test verifies closure before the next operation. Safe document reads/list/account snapshots reconnect once; untaped control reservations reconnect once using the same owner/key/request. General writes are not automatically replayed; authentication/permission/query/budget errors are not transport retries. Connect acquisition has one retry and is marked to avoid a second nested operation retry. Each failed SQL/commit/cursor request records client-observed idle-before-request, failed-request duration and connection age, without query text/arguments. No claim that this client interval proves server idle. Historical failures had no idle interval; do not invent one.70tests total:56PASS/14opt-in skips. Fresh live read-only ledger snapshot succeeded with zero connection failures, using the corrected laptop connector:1453/6000(INV675/SCAN778/REST0),modelUSD4.080700/40; emergency95untouched. No tier, network, role or budget changed.

2026-10-23 PostgreSQL owner steer completion: the single safe reconnect policy also covers keyed control settlement (lost commit ACK reconciled before returning the original estate result) and safe current-period budget reports. An exact same-key settlement test proves one estate call/one charge. General mutations and model/estate requests are never automatically replayed by this layer. Persist numeric idle/request-duration metadata in the publisher control journal, not only traceback notes; cursor context-manager contract preserved.48focusedtestsPASS.

2026-10-23 DECIDED WITHOUT REVIEW: make the fixture observation SELECT composable inside the existing query-bound attestation wrapper with TOP(n+1). Preserve parameterized IDs, read-only object scope and overflow detection. Rejected: weakening/removing attestation or copying owner-read rows into diagnostic evidence. No new connector, role, permission, query limit or engine verdict rule.58focusedtestsPASS.

2026-10-23 owner decision: use option(b) for source-changed-history scoring: native SQL system-versioned temporal history on app.stock_movements_round_two_20261003, named history app.stock_movements_round22_history, two hidden generated datetime2(7) period columns. Microsoft documents [enabling it on an existing table](https://learn.microsoft.com/en-us/sql/relational-databases/tables/creating-a-system-versioned-temporal-table); [change tracking does not retain changed values](https://learn.microsoft.com/en-us/sql/relational-databases/track-changes/track-data-changes-sql-server), so reject change tracking as insufficient for before/after proof. Native rollback probe succeeded and preserved original row/schema hashes. Existing source has a primary key, no triggers, no prior temporal feature/history. No identity or permission grant, new paid service, SKU or free-limit change. Initial payload is5760additional current-row bytes; bounded100historyversions under50KiB raw, with native page allocation to be measured. All SQL mutation remains publisher-only through fixture plans and journal. History persists through every dependent dev/held-out score; cleanup requires captured native history count+SHA256+object relationship and restored original source preimage, then disables versioning, removes only the owned hidden columns/defaults/history, and hash-verifies. Do not execute cleanup before scoring. If the engine cannot read the history, record that gap; never copy owner control receipts into diagnostic evidence. No scored ticket has run.

2026-10-23 owner option(b) applied: native system-versioning ON for existing practice source1938105945, owned history510624862/app.stock_movements_round22_history. Two hidden generated period columns; complete original360rows/7661units and original eight-column schema hashes match. Native initialhistory0rows; current+history reservedallocation204800bytes (total, not incremental/monthly billed cost). Three publisherSQLcontrols, zeroPGdrops/retries, no grants, identities, tier or free-limit changes. Feature intentionally remains enabled through dependent scored dev/held-out runs; no scored history ticket admitted yet. Native empty-history digest returnedNULL, so cleanup compiler now normalizes emptyJSON to[] before hashing; keep original receipt unchanged. Temporal observation converts datetime2(7) periods to native text, preserving seventh fractional digit. Focused fixture/gateway42testsPASS after removing duplicate imported fixture-test discovery; prior47/48 counts included those duplicate executions. Prior freeze invalid.

2026-10-23 owner history-evidence lifetime enforced in the case plan: retain native temporal history until all dependent dev and held-out cases have completed. Scored history admission must execute its bounded native history/time-window check against that database, require available native versions and requested times within retained coverage, and record it; no receipt from a removed injection substitutes. Missing history means invalid fixture preparation to restore before admission, never an invented before-value or a changed expectation. New007writer input was prepared before this steer but never submitted; retain it unused and author any history wording from the new native temporal case instead. No API request or provider charge for007.

2026-10-23 owner steer, implemented 2026-10-24 UTC: `TemporalSourceScenario.admit` invokes a fresh bounded native read before a dependent scored submission. It refuses missing versions, a time preceding retained coverage, a metadata-only/unattested result, and empty-result/zero conflation. It checks fixture availability without supplying expected quantities to the investigator. The scored harness must use this admission callback; the investigator must obtain its own evidence. The harness regression first admits present history, removes it in the test read port, then proves the next ticket is never submitted. Native temporal history remains enabled; cleanup is deferred until all dependent scores finish. The fixture is approximately 200 KiB allocated, with no new service, SKU or permission. Targeted temporal/fixture/harness validation: 33 tests passed. An initial command named a nonexistent test module; corrected to the discovered `test_fixture_failure_scenarios`, with no code or guard change to make the command pass. Final scored cohort has not started.

2026-10-24 UTC follow-through: the generic submit/poll harness now seals any returned admission observation as an ADMISSION event before SUBMIT_ATTEMPT, and logs admission failures without submitting. It never treats an earlier admission event as permission for a new submission: each not-yet-submitted case rechecks its callback. Resuming an already submitted execution still polls that same execution rather than creating another. Fixture history regression asserts the nullable native before-result survives unchanged in the case log, while removed history produces an ADMISSION block and no submit attempt. Combined fixture, harness and gateway tests: 51 passed; no scored ticket, expectation change or estate mutation in this validation. Prior freeze invalidated.

2026-10-24 UTC refresh-control choice: Microsoft's published SDK supplies a single-property `directLakeAutoSync` POST, but our proposed settings GET returned405. Use an explicitly labelled publisher-portal preimage and readback instead of pretending the GET worked. The fixture builder requires the exact approved model/workspace URL, the named switch, its boolean state, and an observation no older than120seconds; it never treats that UI observation as query-bound investigator attestation or server-side CAS. The operator owns the isolated control window, journals each native POST with a durable mutation key, and reads the same switch back before restoration. The first proof will toggle the already fixed-connection main fixture model off and back on without changing data, identities, grants or refresh schedules. No setting has changed at this commit. Twelve fixture/control tests passed, including mismatched model, stale/future/naive timestamps, changed state and the actual405 refusal. This is a practice-estate control plan, not a new investigation connector.

2026-10-23 access-difference preparation: native billingapp metadata confirms existing dia-investigator-round19(EXTERNAL_USER) and orderops_investigator(SQL_USER,DATABASE) both have db_datareader, proposed isolated access objects absent, app schema exists. First metadata readSQL40613, separate retry33seconds later succeeded; no firewall/tier/permission changed, and no quota-exhaustion cause inferred. Existing protected SQL-reader file was checked by username only; no secret printed/copied. Plan uses app.round22_access_rows(6syntheticrows), app.round22_access_readers(3data mappings), app.round22_access_export: CURRENT_USER chooses visible data; this is not a security policy and not an actual permission difference. Same native group query, separate real sign-ins, no impersonation. Existing role scope supplies SELECT; no grant planned. Independent synthetic sums: SQLreader10/20/30, investigatorSP25/45/65. Four new fixture/closed-scope testsPASS. No objects created yet; native paired observations/scoring pending. Prior freeze invalid.

2026-10-23 owner date / 2026-10-24 UTC access controls completed: existing SQL reader observed10/20/30, existing investigator SP observed25/45/65, each through the identical business SELECT on billingapp.app.round22_access_export. Native query-bound identity/database and read-only guards passed; snapshot remains unverified. Data-backed CURRENT_USER mapping, not real security RLS or new permission. First create returnedSQL40613; separate reconciliation proved all objects absent before successful create-only control. Original failure retained; both db_datareader roles unchanged. Keep all three owned fixture objects through dependent scores; cleanup prepared, not run. Zero models; no scored ACCESS_CHECK claim. Receipt docs/runs/round-twenty-two-access-pair.json.

2026-10-24UTC framing-control proof refused: existingpublisher GETmodelmetadata succeeded, SDKderivedPOST metadata/models/6992510/settings bodydirectLakeAutoSync=false returned401. Reloadedpublisherportal stillshowsON, so no restorePOSTneeded and no retry/escalation. Exactrequest/response/preimage/readback: docs/runs/round-twenty-two-autosync-control-refusal.json. Twoownercontrolphysicalrequests, zero models. Causeunestablished; notcalledexpiredcredentialormissingrole. No stale-state case earned.

2026-10-24 UTC not-found preparation: use three original movement records and questions about their values before native tracking began. This differs from the proven source-changed-history cases: no artifact for the earlier requested date was ever retained or removed for these original records. Observe the current values and earliest native temporal epoch without evaluating an unsupported past date as zero. The expected split is the application's historical-evidence boundary; the supported answer is not found, with that retention limit named, not a claim that the source changed. This exercises a real epistemic limit rather than defining not-found from the current engine's missing route. The native coverage observation is read-only and bounded to three IDs; 27 temporal/gateway tests passed. Values and coverage still require a native reader observation before authoring these cases. No scored ticket or new source mutation.

2026-10-24 UTC future-load control plan: use the documented Fabric item schedule API on the existing audited application-load pipeline, only when its complete native schedule list is empty. A prototype schedule starts at least one hour and at most48hours ahead, ends one minute after that start, and has a60-minute interval, so it cannot start immediately or create an open-ended recurring job. Read back the owned schedule, then delete only that native ID after confirming its configuration is unchanged; preserve every other schedule. This prototype will be removed before it can fire. Any later scored latency case must stage its own live source change and enabled future schedule, not reuse an already deleted prototype. Existing four-request collector allowance stays unchanged. The publisher control now correctly accepts native HTTP204 for successful cleanup instead of misreporting it as an error. Twelve schedule/control tests and the combined39 schedule/control/temporal/gateway tests passed. No schedule has been created at this commit. [Microsoft schedule contract](https://learn.microsoft.com/en-us/rest/api/fabric/core/job-scheduler/create-item-schedule).

2026-10-23 owner date / 2026-10-24 UTC: third native blocked-record control qg5qqdr failed before its DAX request with LockNotAvailable: "canceling statement due to lock timeout". Original 44 partial capture files retained unchanged, not a sealed run and not an access result. Concurrent schedule control overlapped, but the exact lock holder is not established. Code inspection found read-only budget snapshots taking the global reservation writer lock. Read snapshots now use database-enforced read-only repeatable-read transactions; reservation mutations retain READ COMMITTED, the exclusive advisory lock and both lease checks. Replay uses the same read-only contract. No broad lock-timeout/write retry, counter release, limit or permission change. This establishes an avoidable contention path, not the cause of earlier idle drops. Focused core41PASS; clean replay/full regression follows.

2026-10-23 owner decision (UTC2026-10-24): monthly scan/collector allocation1000 ->2000 inside unchanged6000 total, so investigation4905 ->3905 and restoration95 unchanged. Effective clock2026-10-24T01:24:00Z; historical tape clocks retain original allocations. Counters, reservation ownership and model/platform ceilings are unchanged. Reason: keep collectors running through October31 while scoring. Code and regression tests enforce both new category ceilings and the original replay-time policy; deployment/readback follows the tested image.

2026-10-23 owner approval applied (UTCOctober24): Application load fixture20261003 model0c89889c-6fe6-49ab-91e9-4b00a51070e6 automatic DirectLake updates ON ->OFF using existing publisher portal. OriginalON01:21:45.627, ApplyOFF01:22:14.535, reloadedOFF01:23:28.322. Chosen because original Copy Jobb4871498 targets this model's isolated Bronze source; no unrelated mainA lakehouse is claimed updated. Owner model refresh25e695e2 completed01:27:55.313, followed by real copy9869fbd1 Completed01:28:49.6055106-01:31:14.56. Native read-only investigator audit row matches run:360read/360written,OBSERVED_COPY_OUTPUT, no recount. Source/pipeline definition, identities and permissions unchanged. OFF remains intentionally through dependent scored tickets; then restoreON, trigger this model's own refresh and verify native completion. No numerical staleness or scored verdict claimed; existing SP DAX401 remains separate. Both fixture preimage and live retained-state obligations in docs/runs/round-twenty-two-stale-refresh-control.json.

2026-10-23 owner date /October24UTC: scan allocation2000/INV3905/REST95 within6000 is deployed on tested a883706/imageea772843 to daily06UTC(3600s), graph0*/6(1800s), collectors*/30(180s). Native before/after readback preserves configuration, identity and resources on all3jobs. No counters reset, no new paid resource. At01:33:54UTC total1816/6000 (INV999,SCAN817,REST0), reserve95, modelUSD4.080700/40. Native receipt docs/runs/round-twenty-two-scan-allocation.json. Freeze invalid; Section3 preparation, no scored run or release claim.

2026-10-23 owner resume after laptop power loss (UTC24October): clean pushed efbb18b recovered. All5recent cloud worker executions plus01:30collector Succeeded; no cloud operation remained in flight at01:53UTC. Local5227test final rerun interrupted; original partial logs hashed/preserved, not a pass or failure. Affected51tests re-runPASS. No open model/enrichment reservations; interrupted publisher refresh-historyGET remains fully charged1request and is nowUNCERTAIN, originals unchanged. Five older physical reservations are unchanged and conservatively counted; historical orphan is immutable. Current1840/6000 (INV1023,SCAN817,REST0), reserve95; modelUSD4.080700/40. Owner now approves source-correct fixed identity for Appmodel and actual reversible new source rows: prior equal-data loads prove timing only, never a numeric stale discrepancy. Existing blocked-case401captures remain historical and cannot be scored against an accessible model without fresh failure staging.

2026-10-23 owner approval executed (UTC24October): isolated Appmodel0c89889c-6fe6-49ab-91e9-4b00a51070e6 changed from Automatic/SSO to source-correct ShareableCloud connectionb1a57512-f71a-41a3-b868-4ee2999c42b9, singleSignOnType=None, ServicePrincipal, Encrypted, testConnection enabled. Existing fixed fixture connection points at another database, so a source-specific connection reuses the same existing read-only investigator and active KeyVault credential; no identity, credential rotation or permission grant. Native before/after model permission listings byte-equivalent. First create refused400/AADSTS7000215 using retired Round20 secret version; original retained, continuation used completed Round21 rotation's existing active version. Cloud reader nowHTTP200,MovementUnits7661, model self-reporttenant-only warning retained, no snapshot attestation invented. Native settings/requests/hashes and read seal: docs/runs/round-twenty-two-app-fixed-binding.json. Original401 blocked cases are historical; need fresh state at scoring. Six unmetered preflight GETs conservatively reconciled as actual controls after dispatch, no admission-before-read claim. Numeric stale gap not yet earned; approved31-unit source insertion/load follows.

2026-10-23 owner steer implemented (UTC24October): native stale DATA gap now exists, not timing alone. Existing SQL owner inserted only900401/900402/900403,warehouse3/product1/Oct23,units7+11+13=31; original360row hash unchanged. Independent arithmetic7661+31=7692. Real copyaada99f6 completed02:11:18.0376314-02:12:55.33. Investigator Bronze read:363rows/7692; same investigator DAX afterload:HTTP200/7661. Matching native audit row:363read/363written,OBSERVED_COPY_OUTPUT; actual copy activity timestamps02:11:45.5812408-02:12:07.6538988 differ from outer pipeline, correctly retained. No recount substituted. Source363/7692 and modelOFF intentionally retained through dependent scored tickets; guarded delete/reload/automaticON/ownrefresh+verify recipe is prepared, not executed. Browser unavailable after restart, so no fresh portal-toggle readback claimed; actual stale numerical gap verified. Tenant-only DAX and SNAPSHOT_UNVERIFIED warnings remain. Original equal-data controls stay historical; no scored investigator verdict claimed. Receipt docs/runs/round-twenty-two-stale-refresh-data-proof.json.
# Owner latency evidence-lifetime steer, 2026-10-23

Restored prototypes establish control feasibility only. Each scored latency ticket requires live source-ahead-of-Bronze admission and an enabled future load schedule, kept through that ticket. The fixture helper has read-only ports only; publisher controls own staging and guarded restoration. Invalid fixture admission is recorded before submission, separately from engine outcomes. No expectation, scope, permission, identity or budget change. Five new latency tests prove fresh reads, NULL distinction, native schedule checks and non-submission; six harness, nine temporal-history and five image-staging tests pass. Actual scores have not started.



2026-10-24 owner focus steer: remaining Round22 work is calculation intake, deterministic answer detail and investigation reasoning. Dev remains NORMAL only; no scored-dev byte-exact replay gate. Attestation is a warning, not a dev admission condition. Non-safety blockers are logged and bypassed for dev without changing read-only/secret/monthly-cap enforcement or sealed held-out/independent grading. No new guard/receipt/attestation/admission framework is authorized.

### Owner resume steer: native comparison before questions, 2026-10-24
A missing comparison number now starts the existing code-owned frontier across the admitted declared native path. It never creates a GIVEN_COMPARISON value. A native finding remains explicitly separate from an unmeasured external comparison; a comparison question is emitted only after multiple equal reads, no outstanding measured layer and no recorded path gap. An unavailable native route remains a route gap, not a query failure. No golden or held-out expectation changes. Failed-job answers lead with the exact recorded name, run, end/start time and error. Definition answers reuse the exact retained measure expression and its native provenance, with a retained-not-recollected label.

2026-10-24 owner speed decision: focused tests between dev passes; broad suites only pre-heldout/premerge/postmerge; smoke3onlypremerge; static concurrency3 with automatic transient backoff, serial native fault cohorts. Legacy closed34/40, remaining6notrun (two latency,two stale,two waiting), no new baseline grading/model calls. Normal investigations disable only private budget-report mirrors, including model and nested path-collector mirrors; existing PostgreSQL admission/settlement and all limits remain. TEST accounting stays available only for tests that require it.

Owner speed implementation, 2026-10-24: draft cloud-image builds and explicit dev_focus dispatches run the focused changed-module tests, while default non-draft/full dispatch and main retain all eight shards. Publication requires one selected test path to succeed. This removes the automatic draft full-suite repetition; final full-suite checks remain before held-out, before merge and after merge. No estate read, model call, guardrail scope or acceptance expectation changed. The existing cloud packaging/health tests pass11/11.


### Round22 dev-only location repair, owner date2026-10-25

Pass4 zero-score analysis and the first unchanged-image pass5 capture show missing/tied targets despite explicit report/page/model names. Preserve exact catalog names in explicit current-location phrases even when the extraction omits them; exclude negated names and comparison spans/targets. A named model constrains its measures through declared containment, and its report visual only through its declared measure edge. A model alone does not turn a measure-level question into a visual-level question. No value matching, guessed path or selected filter is added. Four new synthetic regressions plus all existing calculation tests pass(42); visual-target18, intake-extraction45, same-referent7 and graph-verification16 also pass. The initial new test incorrectly expected RESOLVED rather than READY, then exposed model-only admission being promoted to a visual; both test typo and the actual promotion were corrected. No golden/expected record changed. This local batch is for the next image; pass5 remains immutable f6b3d3d1/sourcebf00824.


Pre-admission follow-up to the same location batch: an exact catalog name following an explicit comparison cue must remain a comparator even if extraction omitted its comparison metadata. Added the omitted-metadata regression and excluded comparison phrases in current-location detection. Calculation42tests(including this extra subcase) and visual-target18 pass. The already published fe17218c image has not run a scored ticket and is superseded before admission; the final next-pass image will include this correction. Existing pass5 stays unchanged. The extra build is recorded as a pre-admission correction, not a second scored image or an expectation change.


Round22 next batch also fixes the pass5 native DEFINITION/comparison contract crash. Keep the kind invariant; fix its producer rather than bypassing it. Only COMPARE requests can carry comparison_pending/comparison objects. Other request kinds preserve the extracted comparison mention as context. No invented comparator value. This newly exposed defect requires one additional pre-admission image; previous prepared images were never used for scored runs.


Round22 held-out preparation finding (no held-out read yet): installation specs are equal within each estate except graph search visibility: one fixture dev case has one extra candidate; one billing dev case has two extra candidates and one allowed object. Keep all frozen dev inputs unchanged. The generic post-freeze held-out input builder will use the union of these already admitted estate graph candidates/objects identically for every ticket in that estate; it will not choose visibility by ticket ID, expected target or result. No native identity or permission changes. The builder is prepared but unexecuted, and requires the recorded engine freeze and pre-held-out full suite before reading the sealed ticket file. No expected record enters its worker archive.

2026-10-26 UTC ? DECIDED WITHOUT REVIEW: stop additional full dev admissions after pass6 at the request-budget planning boundary. INV3302/3905 leaves603 before final Wait polls/restore; observed full-pass cost is already361. A further40 would leave242, below the280-request planning allowance for required20held-out tickets, fresh controls and3smokes. Keep the95RESTORATION reserve separate. Rejected spending the remaining category headroom on dev and stranding the once-only headline test. This does not claim the overall6000 pot orUSD40 model line is exhausted, or that two flat passes occurred. Freeze still waits for independent harmful review. Receipt: `docs/runs/round-twenty-two-dev-budget-boundary.json`.


2026-10-26: freeze canonical engine3c5935a/image802d8508 after fresh5325-test full suite (49skipped,0failures/errors). Owner fixes dev6 at14/40,harmful0 and forbids pass7/regrading; mandatory20once-only held-out proceeds with original sealed expectations. Each held-out installation receives the same union of already approved graph objects for its estate; no expected target, quantity, route or verdict is supplied. SSO refusal control follows its sealed reversible section3b setup and restores the approved working connection; no scopes or credentials change.


DECIDED WITHOUT REVIEW,2026-10-26: final restoration-only value checks omit the optional broad permission-inventory preflight, retaining its explicit NOT_TESTABLE admission warning. The same frozen image, read-only identities, gateway policy, token/connection validation, per-query read-only enforcement and shared caps remain. Native DAX and SQL supply their own results. Alternative rejected: spend33 additional off-path inventory reads (11 per launch) or raise the95 restoration allocation. This follows the owner path-only/focus steer and changes no engine or permission; scored held-out inputs and runs are unchanged.

Correction2026-10-26: the preceding optional-preflight-omission plan was NOT APPLIED. The local launch was rejected before dispatch because the frozen runner contract does not expose INVESTIGATOR_BUDGET_CATEGORY. Keep the original full preflight and all guards. Final standalone native checks use the existing runner classification (preflightINV, native probeSCAN); publisher restoration actions remainRESTORATION. Report those actual categories, no manual reclassification or limit change. Original failed local config/intent is retained; zero estate/model calls from it.


2026-10-26 closure: retain system-versioned temporal history ON as the owner directs, while restoring original current business rows and schema projection. Keep the owner-approved working fixed connection; do not reinstate SSO except the now-reverted test control. Existing native standalone checks keep their runner budget classification; publisher restoration actions use RESTORATION. No cap, identity, role, secret or expectation changed. Dev6 remains14/40; held-out remains the once-only independent5/20. No further fix loop.


2026-10-26 smoke calendar correction: frozen-image job-dia-worker-847ed9b AzureSucceeded and familyA passed with the original7661/8765 witness, but smoke INCOMPLETE because check-access unconditionally appends a next-month NOT_TESTABLE reminder on/after day25. November already exists; there is no configuration confirmation flag (the initial config hypothesis was disproved). Smoke now reads that exact account from the authoritative platform ledger and resolves only this reminder when identity/unit match. Original access table is retained; missing/wrong account or any other untestable/failed probe still prevents green. No account is created, no identity/grant/budget changes, no smoke numerical expectation changes. Three focused regression tests added. Original31-test focused run had30pass and1TAPE_UNCOMMITTED_ENGINE error because the tree was dirty; rerun after commit. Only daily_smoke and its tests change after held-out; investigation engine3c/image802 and all original scores remain frozen. A new smoke/release image is separately labelled, not presented as the image that earned the held-out score. Original incomplete smoke is preserved; next three form a new consecutive sequence.


## Round 23 owner decision ? 2026-10-26 (?8)

Owner-approved 2026-10-26: investigator model USD150/month (was USD40),
warning at 80%; per-ticket USD1 with warning at USD0.50. Enrichment USD25,
platform USD20, estate6,000/month, scan2,000 and restoration95 unchanged.
Counters, settled charges and uncertain reservations are not reset or refunded.
Source policy is updated; existing owner-managed PostgreSQL account ceilings
require an explicit migration and remain authoritative until applied.

Before 2026-11-01: build and offline tests only. No Round23 live model or
estate passes before the November counter is active. No new identity, grant,
paid resource or provider credential is authorized by this budget decision.

The Round23 prompt supersedes the earlier model-use rule for the new
investigator: AI chooses investigative steps and writes SQL/DAX; code supplies
path facts, parser-based read-only validation, request/model budgets, timeouts,
evidence and checkpoints. Ready-made query templates remain for triage only.
Historical engines and their sealed expectations are unchanged. Attestation,
snapshot and output-format limitations are warnings, not safety refusals.
DIA reports what happened, never suggests fixes. Prior engine freeze invalid
for Round23 development; Round22 scored freeze remains its historical record.


### Round 23 offline implementation decisions ? 2026-10-26

Reuse existing SQLGlot and DAX parsers as safety validators; retire code-owned
query writing only in the new investigator. DEFINE is opt-in there, preserving
legacy parser behavior. Graph catalog metadata has its own complete admitted
scope; it is not truncated to the ticket path's 200-node limit. Short PG
transactions and NORMAL-mode mirror suppression are reused from Round22.

Model protocol and published rates were researched in official Anthropic docs
on 2026-10-26; workspace availability has NOT been queried. Actual model choice
and its rate policy remain pending `/v1/models` discovery in the live window.
No enrichment-only budget or batch capability is silently repurposed. The new
reasoning channel uses the existing workspace key and investigator account;
its exact gateway endpoint configuration must be reviewed before activation.
No live gateway, identity, role, credential or resource was changed.


### Owner-approved 2026-10-26: Round23 requests effective immediately
Monthly physical requests 6,000 -> 9,000 for October and every subsequent month: scan/collectors 2,000; investigation 6,905; restoration 95 (restores only). This supersedes the November1 wait: live work may proceed now after safety checks. Preserve all usage, uncertain charges and reservations; do not reset counters or borrow restoration capacity. Update the authoritative cloud ledger policy as well as source/config. Model USD150/month; Azure remains <=USD20/month. No identity, role, credential or resource change is authorized. Historical dated policy decisions remain recorded.

Executed owner decision (observed UTC2026-10-27, owner date2026-10-26): PostgreSQL build_phase_policy/monthly-physical now9000 with6905/2000/95; October and pre-provisioned November model ceilings40->150USD. Exact before/after and unchanged accounting hash: docs/runs/round-twenty-three-budget-increase.json. October5471requests includes70historicalrestoration (25remaining); no reserve reset. New source consults cloud ceiling under the admission transaction. Older scheduled images retain earlier source ceiling until deployment. No identity/role/secret/resource changes.

Round23 budget validation2026-10-27UTC: focused291PASS/15SKIP/114subtestsPASS; staged1349tracked executable/policy files with0privateartifacts, package-completeness checkPASS. Separate committed PostgreSQL readback matched source/config9000 and October/November150USD. No Round23 scored model/estate call admitted by this change; live investigator assembly remains pending.


Owner-approved2026-10-26: reset October restoration allowance to a fresh95 for Round23. The70 Round22 cleanup requests stay in original ledger rows and gross monthly physical usage; no request refunded or deleted. Cloud policy records the one-time October baseline, source/config applies it only from the recorded decision time, and investigation/scan cannot consume the remaining restoration reserve inside unchanged9000gross monthly limit. Applied via existing owner, separate committed readback matched: docs/runs/round-twenty-three-restoration-reset.json. No roles, identities, secrets or resources changed. Round23 continues through live validation, independent scoring and release; no stop after this allocation update.


Round23 model discovery, owner date2026-10-26: GET /v1/models with existing versioned workspace key returned claude-fable-5-1, opus5.5 and other IDs. Selected Fable5.1 as the accessible demanding-reasoning model, per owner strongest-model instruction; no forced tool choice (unsupported on Fable5.1), thinking blocks retained unchanged. Official overview https://platform.claude.com/docs/en/models/fable-5-1/overview and pricing https://platform.claude.com/docs/en/about-claude/pricing checked: USD/MTok input10, output50, 5-minute cache-write12.50, cache-hit0.25. Reservations use upper input rate12.50; settlement separates native usage components. Discovery0paidmodelcalls/0estatequantityreads; KV value stayed in memory, no identity/scope change. Receipts docs/runs/round-twenty-three-model-discovery.json and round-twenty-three-reasoning-rate.json.

Round23 integration finding: live fixture catalog1144nodes exceeded the old1000-ID policy catalog ceiling; actual ticket paths remain limited200nodes/500edges. Allow named catalog lists to10000 and authorize in batches<=1000; every requested ID still must be explicitly in the trusted estate policy, no wildcard/new role. Guided requests with optional visual now enumerate actual contained visual candidates, rather than calling a visual-only graph path with a report ID. Native schema top-ups reuse the existing exact-object catalog control, loaded only for opened path objects, with guard/read-only enforcement and attestation warnings. No investigative query compiler writes a native query in this route.

2026-10-26 DECIDED WITHOUT REVIEW, Round23: the first paid unscored harness used one model call (USD0.400925), then its DAX read timed out at30seconds and the next conservative reservation exceeded the unchanged USD1 case cap. Fix the native context to open only path tables and related schema (it previously opened every model table, contrary to D1), retaining original native definitions unchanged and labelling the model.bim projection. Fit the requested output reservation inside the remaining cap, with a512-token minimum and final atomic admission unchanged. Rejected raising the cap or assuming a cache hit. Do not replace the recorded harness failure with an invented finding.

2026-10-26 DECIDED WITHOUT REVIEW, Round23: add Application Load Support, a practice report over the existing Application load fixture20261003 model, because guided tickets require a report and that model had none. Existing publisher created only the report; six control requests; no model setting, identity or grant changed. Native definition readback and existing static graph extractor added only its five nodes/four edges; existing owner partitions unchanged. This is a fixture addition, not a fault injection; preserve it for reproducible guided tests.

2026-10-26 Round23 A06: two native DAX checks succeeded (unfiltered quantity8765), but the model never reached a lower-layer query before its unchanged USD1 reservation cap. Four model calls cost USD0.468016, three physical reads,68.742worker seconds. Preserve as an unscored blocked harness. The cloud handler had discarded the pinned context native endpoint-ownership relations. Carry these existing witnesses into native route metadata and expose only exact literal DirectLake continuations as DECLARED (not verified); no same-name container binding, model query writer or compiler is introduced.

2026-10-26 Round23 screenshot controls: API export refused403 InvalidRequest, Export report to image is disabled on tenant level. No tenant setting changed. Existing publisher browser sign-in renders Application Load Support/card7661. The newly authored record table initially referenced absent event_day/movement_type fields; native model columns and rendered error established this build defect. Correct only the new practice visual to explicit existing warehouse_id/product_id/units columns; model and grants unchanged. Capture genuine filtered browser views with application movement_id absent from the visible columns. These are publisher-view fixture images, not an investigator RLS attestation.
