# Current delivery status

Updated 2026-09-25. Tracking: [#193](https://github.com/bcsnpc/data-investigation-agent/issues/193).
Direction: [Self-Discovering Enterprise Data Investigator](../SELF_DISCOVERING_ENTERPRISE_INVESTIGATOR_PLAN.md).
This is the authoritative current status; milestone pages retain historical evidence.

## Current milestone

**Correction, 2026-09-26: the Fabric SQL endpoint is reachable.** Earlier text
on this page says the endpoint is blocked on `AADSTS65002` and that the
independent lower read is unavailable under the current authentication
transport. That text is kept as written, but the blocker it describes no longer
holds.
- **What was established:** a SQL-audience token was issued through the
  isolated Azure CLI profile that `scripts/fabric_sql_auth.py` uses, with no app
  registration. The `gold_sql_endpoint` host accepted it and `SELECT 1` returned
  1. `AADSTS65002` is specific to the Fabric CLI's MSAL client.
- **Identity:** this was established only as tenant administrator
  `admin@skynwhy.com`, not as a least-privilege reader. No table permission is
  established.
- **Database:** a connection naming no database opened `lh_investigator_bronze`,
  not Gold.
- **Endpoint IDs:** `701ab1fc…` and `77c49180…` remain unreconciled, and neither
  has been reconciled with the earlier endpoint-comparison run `1cae5e66…`.

**The open question is now which identity should hold this access, not whether
the endpoint is reachable.** No engine change, permission change or new probe
set followed. See the
[inventory correction](execution-surface-inventory.md#correction-2026-09-26-fabric-sql-endpoint-reachable).

**Current checkpoint: execution-surface inventory (work item 1).** Updated
2026-09-26. The adapter stores `execute_source` but never calls it; this is
confirmed from the code. A committed probe set
(`scripts/probe_execution_surfaces.py`, `scripts/read_onelake_header.py`) found
four distinct reachable surfaces:
- Power BI DAX, through the adapter's own `evaluate()`.
- Azure SQL `app`, through `bounded_sql` admission and the source transport.
- OneLake Delta commit metadata, through the adapter's own `ingestion()`.
- A 4-byte OneLake data-file header, read with the isolated metadata identity.

The Fabric SQL endpoint was not re-probed; its recorded `AADSTS65002` stands.
The first committed attempt failed on a harness defect (`ModuleNotFoundError`
before any network call) and is preserved. An earlier unledgered OneLake probe
is now recorded with its original timestamp.

**Not established:** no lower-layer quantity was compiled or compared. The SQL
reader serves only Azure SQL `app` user tables, while the resolved
`declared_source` layer is a lakehouse table. OneLake table data was not read as
a table: no Delta log replay, no decoded row, no aggregate. The semantic model is
`directLake` over that lakehouse.

Engine bytes unchanged (`unfrozen-e3b2724a5c50`); no freeze is invalidated. Usage:
10 cloud reservations, 0 planner calls. See the
[inventory](execution-surface-inventory.md) and
[machine result](runs/execution-surface-inventory.json).

### Previous checkpoint: same-surface boundary claim retracted; independent read unavailable

PR #233 merged the #230 retraction, incomplete-definition guard and silent-fallback
fixes after 1,078 local tests and six green CI checks. No planner context was added:
recorded coverage remains 28 directory entries / 11 SQL objects / 15,971 characters.

Exactly three `unknown-domain-v4` regressions remain preserved. C1 failed before
intake. C2 and C3 each executed two DAX queries against the same semantic model,
plus one Delta-metadata read and no SQL read. Their 8,765 = 8,765 result checked the
measure definition within one execution surface; it did not cross into Gold. The
two `CONSISTENT_TO_BOUNDARY` claims, resolved-boundary counts and partial-pass
statement are retracted in an appended correction and machine-readable
qualification. Historical sessions, ledger rows and receipts are unchanged.

Every process probe now records engine, connection and object. A verified boundary
requires distinct execution surfaces, and consistency requires at least one such
equal comparison. Same-surface checks are retained as `WITHIN_LAYER_CHECK` and
report `NO_INDEPENDENT_LOWER_READ`. Derived process observations now have a bounded
synthesis receipt shape whose references, equality and surfaces are validated.

The configured investigator reader was probed against the discovered Gold SQL
analytics endpoint without a permission change. Its existing MSAL client failed
at token acquisition with `AADSTS65002` because that client is not preauthorized
for `database.windows.net`; no connection or data query occurred, so table
permission remains unestablished. The independent lower read is therefore not
implemented under the current authentication transport.

After PR #235 merged with six green CI checks, exactly three follow-up attempts
were launched and the batch stopped. All three failed before intake because the
harness command omitted the now-required `--environment` argument. No session,
provider call, data read, execution surface, comparison or synthesis was produced;
all usage counters remained unchanged. These are three preserved infrastructure
failures and provide no runtime acceptance evidence. No fourth run, freeze,
variant or unfamiliar-domain claim followed. See the
[three-run checkpoint](independent-boundary-three.md),
[corrected #234 record](correct-context-process-three.md#2026-09-25-correction-after-review-of-234),
and [machine results](runs/independent-boundary-three.json).

### Previous checkpoint: declared-scope integration and harness correction

**Historical checkpoint: declared-scope integration failure isolated and harness corrected.**
The review of the prior smoke found that five adapter methods were constant stubs,
while the vertical procedure called them and consumed their returns as findings.
Those runs therefore measured unfinished wiring, not limitations of the Fabric
environment. They remain preserved, but their zero-planner-call result cannot
support a conclusion about available platform evidence.

Every procedure step now has a named adapter capability. Undeclared methods are
never called; the answer records `CAPABILITY_NOT_IMPLEMENTED` and names skipped
steps in both business and technical output. Outcome validation makes
`REFRESH_LATENCY`, `PRESENTATION_LOGIC`, `TRANSFORMATION_LOGIC`, `LOAD_LATENCY`,
`INGESTION_GAP` and `DEFECT` unreachable without their declared checks. A minimal
path/evaluation adapter is covered by a negative outcome regression.

A platform-neutral declared-pointer resolver now accepts an exact name and stable
connection scope from a retained definition. It searches only descendants of that
scope, never widens by name, rejects ambiguity with all candidates, distinguishes
missing scope, no in-scope match and access denial, and retains
`DECLARED_BY_DEFINITION` with definition, offset and connection identities. The
Microsoft adapter applies it to semantic partition metadata and cross-checks the
model endpoint/lakehouse scope against the exact beta Fabric item-relation type.
Gold-to-Silver definition edges are retained as declared pointers; no quantity
equivalence is invented. Silver-to-Azure SQL inspection is not implemented on this
path, so it reports `CAPABILITY_NOT_IMPLEMENTED` rather than absence.

The adapter now retrieves static report/filter/slicer context with its runtime
selection/RLS limitation, retrieves the exact retained definition at a divergent
boundary and invokes one governed judgment call, consumes retained Fabric job
history, and reads only the latest bounded Delta commit metadata through the
separate metadata identity. Presentation refresh history remains undeclared because
the execution reader receives HTTP 403; no permission elevation is made. **1,073
local regression tests passed before the run.** PR #231 merged with six green CI
checks. See
[implementation and validation](process-capability-declared-scope.md).

The prescribed three-run known-domain batch is complete and stopped after three.
All runs reproduced 8,765 with one DAX read, declared six implemented capabilities,
and listed unavailable presentation refresh in both outputs. All three then ended
`NO_COMPARABLE_PATH` at step 3 with zero resolved boundaries, zero comparisons,
no SQL/other read and no process-planner call. One synthesis completed and two
failed validation. All six tapes passed hash/length verification.

This batch exposed an evaluator integration defect: discovery refreshed
`unknown-domain-v4`, but `run_ticket.py` opened the catalog with a hard-coded
`development` environment. The older snapshot lacked the new native
endpoint-to-lakehouse relation, producing stable `SCOPE_NOT_DISCOVERED` results.
The live and replay harnesses now require an explicit environment and regression
coverage proves it is preserved; **1,074 local regression tests pass**. No live
retest followed within that checkpoint; the current checkpoint above later ran in
the corrected context. The historical checkpoint **did not reach a real comparison or transformation-definition
judgment and did not pass**. No freeze, variant or unfamiliar-domain claim was made.
See the [machine-readable three-run result](runs/declared-scope-process-three.json).

**Completed checkpoint: zero-comparison correction and exactly three G reruns.**
The accepted first smoke proved baseline establishment, synthesis validation and
visibility reporting, but also showed that `CONSISTENT_TO_BOUNDARY` was admitted
after zero comparisons. `NO_COMPARABLE_PATH` now represents an established baseline
whose path cannot be resolved into any adjacent comparable quantity. Consistency,
ingestion and business-flow outcomes require at least one successful equal boundary
comparison; divergence outcomes require an observed unequal comparison.

Tape and #224 review established the asset/quantity distinction. `measure_path` was
called and returned Handled Quantity, Activity, `units`, partition source labels
and identity-backed semantic edges. The historical runs did not establish a stable
binding, but #232 later showed they had opened the wrong discovery environment.
Their estate-level missing-binding conclusion is withdrawn. It remains true that
the adapter did not infer a source object by name. The binding design was
proposal-only. **1,052 local regression tests passed** on that corrected engine,
with unchanged investigation planner payload content and coverage. PR #229 merged
after all six CI checks passed.

Exactly three corrected recorded G trials then completed and the batch stopped.
Each reproduced 8,765 with one DAX baseline, made no SQL read and used no
investigation-planner call. Each terminated at step 3 as `NO_COMPARABLE_PATH` with
zero resolved boundaries and zero comparisons. No `NOT_COMPARABLE` event occurred.
The first adjacent boundary appeared unresolved in the wrongly selected context,
so the explicit stop was `CAPABILITY_UNAVAILABLE`. That is preserved run behavior,
not a fact about the intended estate. All three syntheses validated and all six
tapes passed length/hash verification without exclusion or provider error. Daily
reservations moved from 121/35/3,722,694/890,000 to
127/38/3,860,454/918,500; all 165 records are settled. No permission, policy or
capacity changed.

This checkpoint corrected the false consistency claim, but its former structural-
limit conclusion is withdrawn because the runs opened the wrong discovery
environment. The receipts still prove that zero comparisons cannot support
consistency and that the engine did not name-match across scope. They do not prove
the intended estate lacks a binding or that zero planner calls are structural. The
next accepted batch must use the explicit environment and reach a real comparison.
No freeze, fresh variant or unfamiliar-domain claim follows. See
[correction, proposal and results](no-comparable-path-correction.md) and the
[machine-readable review](runs/no-comparable-path-corrected-smoke.json).

### Previous checkpoint

**Deterministic process-debugging redesign and first three-run smoke.**
The accepted #226 result changed the primary target from open-ended data forensics
to debugging a discovered data process. The implementation now triages mismatch
complaints and business questions, establishes a presentation baseline under the
declared scope, walks adapter-provided paths of arbitrary length, compares only
faithfully translatable quantities and exits on the first evidence-bound outcome.
Every technical output retains its queries verbatim and names the deepest layer
checked plus the access, lineage, comparability or budget boundary that stopped it.

The current taxonomy is closed at thirteen outcomes: REFRESH_LATENCY, LOAD_LATENCY,
PRESENTATION_LOGIC, TRANSFORMATION_LOGIC, INGESTION_GAP, DEFECT,
CONSISTENT_TO_BOUNDARY, NO_COMPARABLE_PATH, DEFINITION_DIFFERENCE, SCOPE_DIFFERENCE,
DIFFERENT_SUBJECT, BUSINESS_QUESTION and NO_KNOWN_PATTERN. Each has a deterministic
evidence contract and fixed recommended action. All thirteen have a negative test.
Boundary attribution without a baseline above it or a specific establishment
barrier is rejected. Historical labels remain stored and map forward only on read.
The adaptive loop remains available solely as the NO_KNOWN_PATTERN fallback.

`REPRODUCE_MEASURE` is now presented as `ESTABLISH_BASELINE`: an independent
presentation read that makes lower-layer differences attributable to the process
rather than translation error. Legacy observations remain readable. The Microsoft
adapter is isolated below the platform-neutral engine and uses the existing parser,
reader, typed scope and receipts. With unresolved external binding it establishes
the presentation value and reports the real lineage boundary rather than joining
assets by name.

The four #226 synthesis failures (M2/M3/M4/M9) now validate in offline regressions.
All support citation groups are assembled into the outer list and overlong published
text receives an explicit labelled truncation at the existing bound. Missing support
still fails. The frozen synthesis digest includes the deterministic process finding,
and synthesis cannot substitute a different outcome.

Offline behavior covers three layers, a report reading the only reachable layer,
an unreachable source, and a four-layer path with one NOT_COMPARABLE boundary.
An injected known-domain runtime completed end to end in one native read and zero
planner calls. Planner golden payloads retain identical entry counts, SQL-object
counts and payload characters; the existing initial directory remains 28 / 11.
Only response schemas changed. **1,046 local regression tests passed**, and all six
CI checks passed before PR #227 merged as `c52673a`.

Exactly three recorded known-domain G trials then completed. Each terminated at
step 6 as `CONSISTENT_TO_BOUNDARY`, established the presentation baseline with one
DAX read, made zero SQL reads and zero investigation-planner calls, and named the
Activity semantic table as the deepest checked layer with `NO_LINEAGE` below it.
All three syntheses validated; their deterministic digests were 3,308 characters
each. All six intake/synthesis tapes passed integrity checks. Daily reservations
moved from 115/32/3,585,333/861,500 to 121/35/3,722,694/890,000 for planner calls,
cloud reads, input characters and output tokens; all 156 records are settled.
No policy, permission or reader setting changed. Compared with #226's nine runs,
this smoke used 0 versus 97 investigation calls, 0 versus 25 SQL reads, 3 versus
7 DAX reads, established 3 versus 0 explicit baselines, and validated 3/3 versus
5/9 syntheses. It did not test a source mechanism because discovery exposes no
identity-backed lineage below the semantic table. No freeze, fresh variant or
unfamiliar-domain claim is authorized. See
[implementation, contracts and proposals](process-debugging-redesign.md).

Horizontal comparison, the recurrence store, declared business context and a
known-issues register are designed in that document and remain proposal-only.

### Previous milestone

**Faithful evidence transfer and measure-path audit.**
Post-#223 work preserves full validated query text, two explicitly bounded result
rows, group keys/counts and explicit definition excerpts in synthesis. Citation
assembly now includes valid support citations in the outer assessment list before
the unchanged validators run. Offline rebuilds of all nine G digests use
17,571-29,230 of the 48,000-character cap (36.6-60.9%); none silently clips.
Initial investigation coverage remains 28 directory entries, 11 SQL objects and
15,067 characters.

The e1b8e1 audit finds Handled Quantity's DAX in initial planner context; existing
semantic graph and asset/content tools reach Activity[units], its Direct Lake Gold
partition, notebook and Silver inputs. The Silver-to-Azure-SQL identity-backed edge
is absent and must not be guessed by name. A compact `measure_path` lookup,
`reproduce_measure`/`test_contribution` capabilities and progress signals are
proposed only. The previously completed eight item-relation probes are compared
against derived lineage, and separate metadata-collector options preserve execution
reader isolation. No Write grant, runtime measure-path change, adapter, dependency
map, live run, freeze or unfamiliar-domain claim. See
[the review](measure-path-and-metadata-collector-review.md).
Validation: **1,029 local regression tests**, two required generator tests and the
local documentation-link audit passed. Exact offline replay of S7's recorded
response now validates with its omitted support citation assembled into the outer list.

### Previous milestone

**Completed: synthesis calibration and Microsoft capability evaluation ([PR #223](https://github.com/bcsnpc/data-investigation-agent/pull/223)).**
Nine corrected known-domain G trials yielded **6/9 accepted synthesis outputs**,
**5/9 receipt-grounded qualified outputs** including historical clipping, and
**3/9 intact receipt-grounded synthesis outputs**. Three new syntheses failed a
citation-subset check; one retained its prior investigation assessment. One accepted
answer overstated a comparison; another lost useful negative evidence in the digest.
The original three were correctly uncertain about a source defect from the evidence
they actually obtained. No support guard demonstrably suppressed a supported cause.
The remaining gap is test selection and faithful evidence transfer, not a reason
to relax intent requirements. Support repair no longer silently truncates text.

**1,027 local tests passed.** All 62 new tapes verified, failures preserved, six
ledger rows appended, and original daily limits restored without resetting usage.
Eighteen bounded Microsoft probes found useful typed item relations, job history
and Delta commit metadata; reader INFO/refresh and SQL dependency catalog access
were unavailable. Time-travel/Query Insights execution remains untested without an
approved Fabric reader connection. No write grant or adapter was added.

That report proposed preserving query predicates and composing citation lists
consistently; those two items are delivered in the active milestone above. Optional
native metadata feeds remained proposal-only. No dependency map, parallel synthesis,
Microsoft adapter, freeze/new variant or unfamiliar-domain acceptance claim. See
[calibration](synthesis-calibration.md) and
[Microsoft capability review](microsoft-native-capability-review.md).

### Previous milestone

**Completed milestone: separated evidence synthesis and input controls.**
[PR #222](https://github.com/bcsnpc/data-investigation-agent/pull/222) adds opt-in,
independently metered synthesis over a deterministic frozen receipt digest.
Investigation context is unchanged: 28 initial directory entries / 11 SQL objects /
15,067 recorded payload characters. No trajectory, directory or raw query-result
rows enter synthesis. Unstructured metadata is omitted after an initial notebook
excerpt exposed embedded rows; two completed attempts and one interrupted attempt
remain preserved separately from the corrected comparison.

Corrected arm-A trials produced **3/3 receipt-supported uncertainty assessments**,
not verified causes. Two gained an assessment after their budget stop; the third
already concluded before synthesis. S1/S3 support text was clipped at the existing
bound, so only one answer had no observed support-text clipping. The three
larger-input arm-B controls produced **0/3 assessments**, stopping at twelve planner
calls twice and NO_PROGRESS once, with input still available. More input alone did
not solve these trials; the remaining call cap prevents claiming that every
resource constraint has been ruled out. The historical #220/#221 pooled result
remains 1/15 under different protocols, not a reliability foothold.

Corrected totals: 62 investigation calls, three synthesis calls, 35 SQL reads,
zero native reads, four query rejections and zero provider errors. Live synthesis
digests measured 14,590-15,488 characters. Reference token cost was USD 4.077090,
including USD 0.148939 for synthesis; intake/cloud costs are excluded and this is
not Azure billing. All 65 corrected tapes verified. Nine ledger rows preserve all
initial/corrected attempts; usage history grew 751 -> 787 -> 893 without reset or
refund. Original daily policy is restored, no active reservations remain, and
Azure capacity/SQL free-tier settings read back unchanged.

Validation: **1,026 final local tests and six corrected implementation CI checks
passed**. See [per-run comparison, support review and costs](separated-evidence-synthesis.md).
At that milestone, parallel synthesis was deferred pending calibration and the
nine-run evaluation, now completed above. It remains **not implemented or
authorized for live execution here**. The support-text correction is delivered above. Typed dependency
traversal remains a later candidate only. Larger input is not adopted as a default;
the stopping contract remains unadopted. No freeze, fresh variant or unfamiliar-domain claim.

### Previous milestone: guarded registry and four-arm experiment


**Completed milestone: guarded ownership registry and twelve-run G evaluation.**
The [offline G1/G2/G3 audit](g-trajectory-audit.md) found genuine hypothesis revision,
with the sixth read preventing another synthesis turn in G2/G3. The approved
connection registry preserves all 53 recorded directories: F remains 28 entries /
11 SQL objects at +477 pre-wire characters. Saturated prompts omit the registry.
Dynamic runs now default to 15 reads; six-read controls and a separate high/16,000
experimental profile support the comparison. Default generation settings remain.

The twelve recorded known-domain trials completed with **124 planner calls,
62 SQL + 4 native reads, eight local query rejections, zero provider errors and
zero qualified final assessments**. Every run ended UNRESOLVED / BUDGET_LIMIT.
Neither raised reads nor high effort/output converted evidence into a conclusion
under these controls. Input admission censored all higher-read runs; D2/D3 also
exceeded the per-call protected-context limit. Small overlapping samples and the
combined effort/output change do not establish a superior model setting.

Measured planner-token reference cost was **USD 8.86**, excluding intake/cloud
costs and not an Azure invoice. All 124 tapes verified, twelve ledger rows were
appended, and usage history grew 549 → 751 without reset/refund. The temporary
126-read / 2,000,000-output daily policy was restored to its original limits;
Azure capacity, SQL free limit and AutoPause read back unchanged.

Validation: **1,016 local regression tests and six implementation CI checks passed**.
[PR #221](https://github.com/bcsnpc/data-investigation-agent/pull/221) contains the
implementation and final results; its checks track the documentation head.
See [per-arm results, stop audit, costs and proposals](g-read-reasoning-experiment.md).
This milestone's input-sizing proposal was subsequently evaluated as the temporary
control above. Two-process investigation concurrency remains proposed only.

Previous #220 evidence remains in [ownership revert evaluation](ownership-revert-evaluation.md),
including its one qualified G conclusion. Pooled with #221, that is 1/15;
it is not a reliability foothold.
All failed/partial/blocked results remain. No freeze, new variant or unfamiliar-domain
claim. The stopping contract stays evaluated and not adopted.

### Previous milestone: #219 compiler/context evaluation

**Completed milestone: compiler binding, physical context and six-run re-baseline.**
The stopping-contract proposal is **evaluated and not adopted**; its negative result
remains in [the review record](stopping-criteria-review.md). Repeated typed SQL
literals now share bindings, fixing the saved G SELECT/GROUP BY defect offline.
SQL rejections report measured complexity/caps and approved connection/schema with
scoped catalog targets. That historical engine labelled physical ownership per entry (now reverted above). No query rewrite,
permission expansion, cross-system adapter or experimental stopping field was added.
**All 1,008 regression tests passed.**
[PR #219](https://github.com/bcsnpc/data-investigation-agent/pull/219) tracks implementation,
evidence and final CI/merge state.

The authorized E/F/G/I plus two G repeats completed with **53 planner calls, seven
native reads and zero successful SQL reads**. E repeated the denied registry read;
F remained unresolved and did **not** establish the source mechanism. G trials made
1/2/0 reads in 12/10/5 calls, with 4/1/2 DAX rejections; all were unresolved (two
BUDGET_LIMIT, one NO_PROGRESS). I reached BUSINESS_CONTEXT_REQUIRED while preserving
unknown Q49 meaning and intended rules. It had one charged connection recovery and
an unexplained host-wait delay, so its wall time is not a clean latency comparison.

The matched four-family baseline had 34 calls and 3 SQL / 4 native reads; the new
first four had 38 calls and 0 SQL / 5 native reads. All ten local rejections across
six trials were DAX member-binding limitations; no live complexity rejection tested
the new SQL feedback. Offline replay retains the measured 9/8 SELECT and 3/4 join
counts. Repairs, redundancy refusals and result-equality overlap were zero.
Explicit labels also reduced initial F directory coverage from 28 to 11 entries
(SQL objects 11 to 3) under the unchanged cap. This is a measured tradeoff, not
proven causality for action selection. **Source-investigation reliability did not
improve in this batch.** See [full metrics, receipts and variance](physical-binding-reliability.md).

All 53 planner recordings load; the prior 111 ledger rows are intact and six new
rows identify KNOWN_DOMAIN_REGRESSION. Usage records rose from 399 to 466 with no
reset/refund. Before/after deployment reads retain GPT-5.4 2026-03-05, GlobalStandard
100, 100,000 TPM / 1,000 RPM. Profile, serial 65-second pacing, daily policy and run
deadlines stayed unchanged. Final daily reservations: 129 planner / 24 cloud calls,
3,856,655 input characters / 934,500 output tokens, within the existing
240 / 60 / 8,000,000 / 1,500,000 limits. No active reservation or usage violation.

Work stops at the requested report. Virtual DAX references/feedback, retrieval
coverage and repeated failed test selection remain findings for review. F-paced and
baseline F remain failed. No freeze, fresh variant or unfamiliar acceptance claim.

### Previous milestone: item 7 - intake regressions (merged PR #215)

**Completed item 7: intake family regressions.**
Twelve fixed synthetic captures cover all nine ticket families and three material
scope questions. All nine proceed through real scope-review/start admission and
one mock native read. Negative grading probes reject unnecessary metadata
clarification and missing-fact questions for facts already supplied. Four focused
tests passed, plus a retained nine-case flow proof. These controlled responses do
not establish live LLM judgment or nine solved investigations. All 1,003 regression
tests and six CI checks passed; merged in PR #215. See [intake evidence](intake-family-regressions.md).
No investigator runtime behavior changed. Next: item 8 capacity report; no live
run/tape, freeze or new variant before all ordered items are merged.

### Previous milestone: item 6 - retrieval/test budgets (merged PR #214)

**Completed item 6: retrieval/test budgets.**
New dynamic sessions reserve two planning turns for tests inside the existing total;
LOOKUP has a separate cap and is removed from the wire schema when exhausted.
Local validation independently enforces it. Every session reports successful reads,
retrieval/test proposals and their ratio. No cloud/daily/token limit increased.
Five focused tests passed, including a recorded mock-provider run with four
lookups and two reads in six calls, followed by exact offline replay. Material
ambiguity/deadline holds still permit zero reads; the reserve does not manufacture
successful tests. All 999 regression tests passed; five focused tests passed again
after clarifying the missing-date fixture. Six CI checks passed and the change merged in
[PR #214](https://github.com/bcsnpc/data-investigation-agent/pull/214).
See [budget evidence](retrieval-test-budgets.md). Next: intake regressions (7), then
capacity report (8), each separately. No live run/tape, freeze or new variant.

### Previous milestone: item 5 - compiled read reuse (merged PR #213)

**Completed item 5: compiled read redundancy.**
The user clarified the acceptance gate: compiled candidates, not semantic
containment. SQL/DAX compiler identities now normalize bound aliases while
preserving calculations, filters, parameters, scope and limits. Repeats reuse sealed
receipts without another data-read reservation. Distinct equal-result reads remain
admitted; equality is reported only afterward, alongside schema-prefetch repairs
and SQL rejection rate. F-paced remains FAILED and is not this item's gate.
Eleven focused checks, 13 recording checks, 36 flexible-query checks and seven repair
checks passed. All 994 regression tests passed after the sort-alias correction;
secret scanning and local links passed. Six CI checks passed; merged in
[PR #213](https://github.com/bcsnpc/data-investigation-agent/pull/213).
Shared text bounds and nonfatal secret-excluding recording address the carry-over
review. See [redundancy evidence](conservative-read-redundancy.md).
Follow-up, in separate PRs: retrieval/test budgets (6), intake regressions (7), capacity
report (8). No live run/tape, new freeze or variant before these are merged.
Engine bytes change; v4 remains invalidated. No acceptance pass is claimed.

### Previous milestone: item 4 - local proposal repairs (merged PR #212)

**Completed milestone: offline reliability, item 4: local proposal repairs.**
Identical duplicate hypothesis updates and overlong descriptive fields are repaired
before validation. Conflicting updates and executable text are not rewritten.
Missing approved SQL schemas are fetched locally without another planner call,
then normal admission runs again. Every repair is recorded separately.
Six repair tests, five replay tests, 36 flexible-query tests and nine projection
tests passed. A synthetic three-rejection failure shape now completes three mock
reads and a final question in four planner calls, with matching offline replay.
This is not the exact unrecorded v2 trajectory or an unfamiliar-domain pass.
All 979 regression tests passed. No live calls, new freeze or variant were used.
Engine bytes change; v4 remains invalidated. See [repair evidence](local-proposal-repairs.md).
[PR #212](https://github.com/bcsnpc/data-investigation-agent/pull/212) tracks final CI and merge state. Next: conservative read redundancy, in a separate PR.

### Previous milestone: item 3 - recorded-provider replay (merged PR #211)

**Completed milestone: offline reliability, item 3: recorded-provider session replay.**
The simulator rebuilds planner context through the actual runtime, validates exact
request bytes, decodes recorded provider responses and repeats rejection, lookup,
compaction, budget and stop behavior in disposable database copies. Completed
child receipts are reused; network and uncached tool execution are blocked.
Five focused tests passed, including malformed proposals injected at every step
and a recorded timeout without a fabricated response. Full regression passed 973 tests; secret scanning and changed-document local links passed.
This is engineering replay, not unfamiliar-domain acceptance or business grading.
Recording now includes runtime profile/policy and return timing; older recordings
without those fields explicitly cannot bootstrap full-session replay. Engine bytes
change, so v4 remains invalidated. No new freeze, variant or live LLM call was used.
See [offline replay evidence](offline-session-replay.md) and [PR #211](https://github.com/bcsnpc/data-investigation-agent/pull/211) for final CI and merge state. Next: local repairs.

### Previous milestone: item 2: planner-view goldens (merged PR #210)

**Completed milestone: offline reliability, item 2 — planner-view golden tests.**
Exact synthetic projected/wire snapshots cover dense profiles, definition children,
paged older content and assembled input exceeding the per-call ceiling. Omissions
are counted and distinguished from catalog removal. Deterministic fitting occurs
before reservation/dispatch; protected scope and schemas remain admitted or fail
closed. A realistic offline fixture exposed compaction that enlarged metadata;
the correction avoids that inflation. Nine focused projection tests and 968 full
regression tests passed, with six green implementation CI checks. Final-head checks
and merge state are in [PR #210](https://github.com/bcsnpc/data-investigation-agent/pull/210).
See [projection evidence](planner-view-goldens.md).
No live LLM call, new freeze or new variant was used. Engine bytes change, so v4
remains invalidated for further frozen grading. Item 3 follows above.

### Previous milestone: item 1 — exact planner recordings (merged PR #209)

Operator-enabled recording captures HTTP request bodies after wire conversion,
raw response bodies before decoding, context version, state, budget and reservation.
Fixtures stay under `.local/`; default operation does not record content. Tests use
mock transport, including failures and credential exclusion. This engine change
invalidates v4 for further frozen grading; frozen artifacts and previous receipts
remain untouched. No new variant, freeze, permission grant or live LLM call is part
of this item. See [recording runbook and verification](planner-call-recordings.md).
Verification: 959 regression tests, ten focused recording tests,
31 runtime-governance tests, PowerShell syntax, six portal tests and build passed.
The implementation has six green CI checks; final-head verification and
merge state are recorded in [PR #209](https://github.com/bcsnpc/data-investigation-agent/pull/209).

The required order is one item per PR: recordings; projected-context golden tests;
offline session simulation; deterministic repairs; conservative read redundancy;
retrieval/test budget separation; nine-family intake regressions; operator capacity
assessment. Only after these gates pass may a new freeze and fresh variant proceed.
The append-only [run ledger](runs/ledger.jsonl) begins with this work; earlier run
evidence remains in its original milestone documents.

### Historical checkpoint: v4 publication and discovery (2026-09-19)

**v4 frozen unfamiliar-domain acceptance checkpoint.**
Conclusion-quality PR #207 merged with 949 local regression tests and six green
CI checks. The corrected known-domain transformation repeat reached source
mechanism evidence and preserved unknown intended semantics. The engine is now
frozen at `981bec80b53ec17d01dfa7f02c3fc470257dbfe0`, tag
`unknown-domain-v4-engine`, covering 382 engine files plus connection/usage policy.
The v4 catalog retains all 313 prior usage records; publisher truth was not copied.
Pre-publication discovery completed with 66 operations and no assets matching
fresh variant `23619e`. Its six isolated SQL tables, three lakehouses and notebook
are published and the notebook completed. Model
`163ce520-ec47-4824-975c-96f5c749205f` and two reports are published. The complete
81-operation rescan discovered them and automatically projected the model into
the enabled ticket catalog without runtime ID registration. Exact model Read + Build and six table SELECT requests are
prepared and awaiting user approval. No write/admin access is requested. No
unfamiliar-domain acceptance pass is claimed.

### Previous milestone: conclusion quality (merged PR #207)

**Discriminating tests and explicit conclusion support.**
The current provider contract requires the proposed mechanism, its receipts,
dependency on intended business rules and the best remaining test. Contradictory
defect/expected-behavior labels with explicitly unknown intent are rejected;
reference validation does not certify semantic truth. Historical assessments
remain readable. Planner guidance prioritizes discriminating tests and targeted
source search without a domain-specific route. Research and evaluation criteria
are in [conclusion quality](conclusion-quality.md). Validation: 949 local
regression tests passed after the provider-decoding and classification corrections. Two known-domain transformation trials reached source mechanism evidence.
The corrected-engine repeat completed BUSINESS_CONTEXT_REQUIRED in 11 planner
calls and three reads, reproducing 53,145 and explicitly treating 50,109 as a
counterfactual, not a corrected total. It recovered from SQL complexity and citation
rejections. Retrieval efficiency remains limited. Original daily allowances were
restored without resetting usage. This milestone led to the v4 freeze above;
no unfamiliar-domain acceptance pass is claimed.

### Previous milestone: provider response reliability (merged PR #206)

**Provider response reliability and conclusion quality.**
Provider failures now retain safe categories and numeric usage without retaining
response content. Four source-ready replays at 4,000 output tokens produced three
structured proposals and one observed OUTPUT_TOKEN_LIMIT. The experimental profile
now allows 8,000 output tokens; default settings remain unchanged. A narrow SQL
AST check rejects mixed aggregate/nonaggregate projections without GROUP BY.
**943 local regression tests passed.** See [research and evaluation](provider-response-reliability.md).

The next full known-domain transformation run completed without a provider error:
eight planner calls, two native reads, five metadata lookups and no SQL reads.
It reproduced 53,145 but proposed a sign-handling diagnosis whose business premise
was not established, while leaving join duplication untested. This is **partial
investigation evidence, not a correctness or frozen-acceptance pass**. Increased
output room alone has not resolved test selection or conclusion qualification.
The ambiguity run completed with BUSINESS_CONTEXT_REQUIRED after seven planner
calls, two native reads and four context lookups, preserving unknown code meaning
and intended rules. The original daily policy was restored without resetting
usage. The fresh freeze remains pending while transformation test selection and
claim qualification are improved. No permissions or SQL limits changed.

### Previous milestone: planner reliability and evidence continuity (merged PR #205)

**Planner reliability and evidence continuity.**
Research and live evaluations led to bounded retention of retrieved transformation
text, keyed hypothesis updates, response-schema field limits, governed reasoning/
output/timeout settings, and one optional metered planner connection recovery.
The experimental quality profile allows 48,000 input characters per call; default
settings, cumulative bounds, reader permissions and SQL free-tier policy remain.
No domain-specific route, metric branch or scenario mapping was added.

The final known-domain transformation trial made **nine planner calls, one native
read and seven metadata lookups**, reproducing 53,145 and reaching the actual
notebook join plus both source schemas. It had no rejected proposal or repeated
lookup, but **ended UNRESOLVED before SQL execution** on a provider-response
`ValueError`. The saved category does not identify whether the response was
incomplete or otherwise invalid. This is not an end-to-end reliability pass.
Earlier timeout, contract, payload-limit and interrupted experiments remain recorded.

A final quality-profile ratio trial completed its requested calculation in **two
planner calls and one native read**: 6,432 / 8,580 = 0.7496503496503496. It explained
the actual measure definitions and preserved the missing business benchmark.
The default-model trial instead asked for confirmation already supplied in the
ticket; that task-completion failure is recorded. Neither establishes generality.
The original daily LLM policy was restored after testing without resetting usage.

**939 local regression tests passed** on the final engine. Six CI checks passed
on the implementation commit; final PR checks track the documentation head.
No dedicated browser session was rerun locally. See [research, trials and limits](planner-runtime-quality.md).

The follow-up above distinguishes provider response failures and continues
transformation and ambiguity evaluations before freezing a new engine to publish
a fresh domain for the full acceptance matrix. The unknown-domain challenge
remains the priority and has not passed. Broader discovery, hosted authentication
and integrated handoff remain pending.

### Previous milestone: structural discovery (merged PR #204)

**Structural discovery within the existing reliability work.**
New model contexts now include bounded metadata-derived role/key/date/measure
hypotheses and explicit unknown semantics. SQL/DAX adapters advertise supported
operations, prerequisites and limits; runtime eligibility does not grant execution.
Relevant tickets can choose bounded uniqueness, grain, functional-dependency,
join, freshness and native measure-behavior experiments with existing query receipts.
There is no new architecture layer, mandatory tool sequence or domain mapping.
Data profiling is ticket-driven, not an automatic scan-time sweep. The fresh engine
freeze and unfamiliar-domain challenge remain next, with no acceptance pass claimed.
Validation: 929 regression tests passed after the dense-profile correction; ten injected-transport browser checks
passed before the final profile-size adjustment. A ratio trial reproduced native
components in one read; an ambiguity trial requested business meaning without
inventing it, but did not exhaust available documentation. These are known-domain
checks. Attempt v3 froze `05348d0` and published variant `0fd86f`, retaining prior
usage and applying explicitly approved reader grants. Its complete 63-operation
scan discovered the model and reports automatically, but exposed a planner profile
projection that discarded all table hints for dense scoped IDs. A generic correction
now retains selected-table member hints with explicit truncation. This engine
change ends v3 frozen acceptance; further v3 runs are known-domain regressions.
A fresh freeze and variant are required; no acceptance pass is claimed.
The post-correction known-domain transformation run ended UNRESOLVED after an
API timeout: ten planner calls, five native reads, four metadata lookups and no
SQL reads. It reproduced 53,145 but did not test the upstream join mechanism.
Overlapping tests and timeout behavior need quality evaluation before another
freeze. Original daily limits were restored without resetting usage.
See [structural discovery evidence](structural-discovery.md).


**Investigation quality before a fresh unfamiliar-domain challenge.** Discovery,
dynamic queries and earlier reliability work merged in PRs #194, #196, #198,
#200, #201 and #202. The v1/v2 frozen attempts are historical failed/partial
attempts; changed engine code cannot use them as acceptance evidence.

[PR #203](https://github.com/bcsnpc/data-investigation-agent/pull/203) implements
structured large-asset context, parent-qualified search, exact missing-schema
recovery targets, SQL alias feedback and safe connection-error receipts. Dynamic
runs allow 384,000 cumulative input characters under the user-approved increase;
12 planner calls, per-call output of 1,500 tokens and existing SQL/cloud limits
remain bounded. No domain-specific investigation route or expected answer was added.

The final GPT-5.4 known-domain trial completed with **LIKELY_TECHNICAL_DEFECT**:
nine planner calls, one Power BI read, two SQL reads and five distinct metadata
lookups. It reproduced 57,043 in Power BI and the source join, connected the result
to the notebook's product-only join against versioned rates, and explicitly left
the intended rate-selection rule and corrected total unknown. No query rejection
or repeated lookup occurred. This is a qualified mechanism explanation in one
known case, not verified business intent or unfamiliar-domain acceptance.

Earlier GPT-4.1 and GPT-5.4 runs ended unresolved; their failures remain recorded.
The final generic changes expose unsupported SQL constructs and remaining dispatch
time, with a 1,800-second dynamic-run ceiling. A prior failure exposed firewall
error 40615; the user-approved single-IP rule restored reader access. SQL
useFreeLimit=true and AutoPause remain unchanged. The original daily LLM policy
was restored after testing without resetting usage. The default mini model is unchanged.

Validation: **920 regression tests and 10 dynamic browser checks passed** after
the final backend changes. Browser checks used injected transport, with no live
cloud calls. [Context/query recovery evidence](context-query-recovery.md) records
trial IDs, failures, query observations, budget changes and limits. CI and merge
state are available on PR #203.

PR #203 follow-up is now the structural-discovery extension and frozen v3 attempt
above. Further repeated evaluations and unfamiliar-domain acceptance remain required. The nine-family challenge, broader
discovery, hosted authentication and integrated handoff remain pending. Earlier
[reasoning reliability](reasoning-reliability.md) and [quality engineering](investigation-quality-engineering.md)
retain their release-specific evidence.

Dynamic reasoning and governed tools merged in PR #198 after all six CI checks passed.
[Issue #197](https://github.com/bcsnpc/data-investigation-agent/issues/197) tracks
this grouped change. Architecture PR #194 and discovery PR #196 are merged.
Discovery merged at `af6a0523db3d2e9e6c308f98b01d1e5a3745fcf4`.

The planner can retrieve discovered definitions/lineage, propose parser-governed
SQL/DAX, use typed diagnostics and revise hypotheses from observations. The local
workspace enables this path for discovered models, including budgeted global
questions. Suggested explanations are LLM_INFERRED, not verified causes or confirmed
business intent. Reader isolation, budgets, receipts, cancellation and replay remain.

Earlier dynamic-tool milestone validation: **891 regression tests and 40 browser checks passed**. Live generated
DAX returned a ratio of 0.2 with its component values in one native query. A separate
context-first SQL investigation returned 20,000 total and distinct customer IDs.
Both completed with the isolated reader. Earlier contract/Decimal failures and
their fixes are recorded in [dynamic milestone evidence](dynamic-investigation-milestone.md).
These are existing-domain checks, not frozen unfamiliar-domain acceptance.

Discovery's business-environment repeat scan completed with **567 assets and 69
operations**, resolving the initial lakehouse-listing gap through bounded OneLake
fallback. An isolated workspace scan and two finite repeat scans completed with
nine operations each; repeat scans recorded zero changes. A discovered native
query returned 8. No permanent scheduler was installed.
See [discovery runbook/evidence](enterprise-discovery-milestone.md).

The earlier discovery/tools milestones changed no production data or SQL quota.
The challenge publishes isolated fixtures and uses separately approved Read + Build
grants on its models. SQL free-overage settings remain unchanged. SQL TOP limits
returned rows, not work scanned.

## Working foundation and limits

| Area | Delivered behavior | Current limit |
| --- | --- | --- |
| Business platform | Related 100,000-order SQL application, deployed portal, Fabric transformations and Power BI reports | Historical platform deployment; not every application retested this milestone |
| Discovery/context | Workspace enumeration, definitions, SQL catalogs, lakehouse tables, lineage, immutable versions/diffs, automatic ticket projection | One approved workspace/database/schema per profile; warehouse endpoint adapter and permanent scheduler pending |
| Catalog | Independent model context, graph search, reportless models, optional business enrichment, persistent explicit deny | Selected model anchor; bounded initial ticket catalog still limits large estates |
| Diagnostics | Typed native/source tools and parser-governed proposed SQL/DAX with actual reader execution | Explicit grammar subsets; SQL views/computed columns excluded; hidden report context and cross-system equivalence remain uncertain |
| Adaptive runtime | Context lookup, hypotheses, proposed tests, observation-led revision and qualified outcomes | Generality unproven; no VERIFIED_TECHNICAL_DEFECT classification |
| Workspace | Text/reviewed screenshot intake, scope review, history, cancellation, business/technical evidence | Local single operator; hosted enterprise authentication/deployment pending |
| Handoff | Older reviewed issue/notification workflows | Integrated v2 impact/ownership/routing pending |

## Remaining roadmap

| Stage | Status |
| --- | --- |
| 1 Architecture pivot | Merged #194 |
| 2 Enterprise discovery | Merged #196; coverage/diffs and finite repeat validation |
| 3 Automatic context graph | Merged #196; independent context, graph/search and ticket visibility |
| 4 Expanded LLM reasoning | Merged #198; dynamic context/tests and qualified assessments |
| 5 Flexible governed tools | Merged #198; parser-governed SQL/DAX and isolated execution |
| 6 General engine freeze | v4 invalidated; synthesis comparison complete; no new freeze authorized |
| 7 Unknown Domain Challenge | v4 discovery preserved; source reads recovered in known-domain repeats; conclusion reliability pending; no fresh variant |
| 8 UX consolidation | Dynamic local flow works; broader effective-context and hosted delivery remain |
| 9 Support-engine-ready core/handoff | Generic boundaries partly established; integrated v2 impact/ownership/triage remains |

Current: **zero-comparison correction and three-run regression complete; comparable divergence remains unexercised; no freeze**. Prior
attempts froze the engine before publication; changed code cannot reuse their acceptance. See [live acceptance evidence](unknown-domain-challenge.md). Keep evaluator truth
outside runtime context. Record failed/partial/blocked outcomes, and invalidate and
repeat the freeze with a fresh variant if engine behavior must change.

See [stage exits](architecture/phases-and-acceptance.md),
[challenge contract](architecture/enterprise-discovery-pivot.md#h-frozen-unknown-domain-challenge)
and [historical pre-pivot status](delivery-status-before-discovery-pivot.md).
