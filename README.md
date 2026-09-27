# Self-Discovering Enterprise Data Investigator

Current implementation: [rolling read allowance and expiring credits](docs/rolling-read-budget.md). #278 merged after six green checks. Ordinary read admission now uses a rolling 24-hour window; explicit batch approvals allocate expiring credits to named runs, with restoration credits isolated from investigations. OneLake GETs and SQL self-report/permission/quantity commands are separately admitted and receipted. Existing per-run limits remain. No live grant, policy increase, read or fixture run; prior freezes are invalidated. Validation: 1,302 final local regression tests passed; six implementation CI checks passed. See the evidence document for results and accounting limits.

Previous implementation: [optional snapshot attestation](docs/snapshot-attestation.md). #277 merged. Comparisons default to SNAPSHOT_UNVERIFIED with specific agreement/divergence limits in both outputs. Only query-bound reports for the same dataset/version can verify alignment; separately authenticated Microsoft metadata remains METADATA_ONLY. Snapshot evidence never selects an outcome. At that checkpoint no live identity, cloud read or fixture run was added; budget redesign was pending. Engine changes invalidate prior freezes. Validation: 1,286 regression tests and PowerShell syntax passed; no live or browser run.

Previous documentation milestone: [known platform limits](CLAUDE.md#known-platform-limits-served-snapshot-metadata-2026-09-27) now record the tested refresh/version/fallback metadata refusals and empty SQL result as constraints of the least-privilege reader. #276 merged after all six checks passed. At that checkpoint, snapshot attestation, the optional snapshot capability and the budget redesign were pending. No new cloud reads, engine changes or freshness-fixture run.

Current audit: [snapshot alignment reader probes and budget design](docs/snapshot-alignment-audit.md). #275 merged. Three approved probes completed: SQL accepted the target version query but returned zero rows; DAX Delta-version metadata and fallback mode both required administrator permissions. No served snapshot was established. Usage 78 to 81; temporary ceiling 81 immediately restored to 60. The saved SQL lag lower bound is 53.06 seconds, not a full latency measurement. OneLake access for the reader remains unestablished; current metadata reads use a separate identity. Proposed snapshot and batch-budget changes are design only; engine and refresh rule unchanged.

Current result: [authorised stale-fixture attempt and restoration](docs/stale-fixture-live.md). #274 merged after six green checks. One appended row changed the Gold Delta snapshot from 406 to 407 rows, but the single live investigation read 8,765 from both Power BI and Fabric SQL. It held on its next read admission; no REFRESH_LATENCY or synthesis output. The append was reverted at Delta version 2 and the reader verified the original 8,765 baseline. All eight authorised reads are recorded; the temporary ceiling 78 was restored to 60. No rule change or retry.

Previous work: [comparison-based refresh latency](docs/comparison-refresh-latency.md). #273 merged after six green checks. A positive unchanged declared-source proof now permits REFRESH_LATENCY after a real attested presentation/source divergence; timing is optional, separately attributed metadata and never selects an outcome. Existing refusals and missing-timestamp limits remain. The initial 1,268-test full suite and 61 final targeted tests passed; the live stale-framing scenario and bounded read allowance remain pending. No new live output or freshness pass is claimed.

Previous work: [job completion classification, fixed path facts and refresh probes](docs/job-history-path-and-refresh-probes.md). #272 merged after six green checks. Failed/incomplete retained jobs no longer count as CURRENT; technical path ordering is now engine-rendered and schema-fixed. All 1,260 local regression tests pass. One reader XMLA timing query was refused for administrator metadata access, and one REST refresh-history GET returned403. No grants, latency outcomes or new live investigation were added.

Current result: [two vocabulary-form repeats and read-only latency audit](docs/vocabulary-form-live-and-latency-audit.md). Both runs completed TRANSFORMATION_LOGIC with validated synthesis, evidence-backed movements/rates wording, four reads and one first-attempt judge call each. No live retry was exercised. The approved eight-read batch moved usage62 to70 and immediately restored the ceiling to60. A separately authorized single reader refresh-history request returned HTTP403 Unauthorized. Existing job/Delta metadata contains timestamps but no implemented lateness comparison; no latency code was changed. All 1,253 local tests and six implementation CI checks passed.

Historical checkpoint: [business vocabulary and judge audit](docs/business-vocabulary-and-judge-audit.md). Both recorded repeats completed with valid judge/synthesis prose but failed vocabulary quality: an unrelated table name suppressed the current definition label. Both original outputs and quality corrections are preserved. A scoped correction passes all 1,245 regressions, six implementation CI checks and the real-catalog offline check. Additional live validation awaits read-budget approval. Judge behavior remains unchanged; the raw failed historical response was already incomplete prose inside completed provider JSON, not local truncation or token exhaustion.

Previous result: [complete evidence prose and business substance](docs/complete-evidence-prose.md). Run `f7a016d9` completed TRANSFORMATION_LOGIC with validated synthesis: 8,765 in the report and immediate input, 7,661 earlier, four reads and one definition-judge call. The complete 767-character technical paragraph and business explanation retain both numbers, a possible matching-record mechanism, unknowns and the action. Oversized prose is rejected intact; syntactic completion guards reject unfinished endings without silently cutting them. The first repeat `529249ef` remains a recorded prose-quality failure. Final validation: 1,237 local tests and six implementation CI checks passed. This is one known-domain ticket, not proof of actual duplicate matches, intended behavior or unfamiliar-domain reliability.

Prior result: [contract/accounting/output repeat](docs/contract-ledger-output-rerun.md) `3d2c5bf0` completed TRANSFORMATION_LOGIC with validated synthesis after two real cross-surface comparisons (8,765 = 8,765; 8,765 != 7,661). All four reads are retained. The judge explains a possible join-multiplication mechanism, not proven duplicate matches or intended semantics. Business output now carries the verified number, comparison, limits and action. Technical prose still ends mid-sentence at its bound; it is preserved verbatim. One known-domain ticket, no source-ingestion build or unfamiliar-domain claim.

**Prior depth checkpoint:** declared Silver/Bronze quantity tracing and a
configurable, attested depth ceiling are implemented. One live run compared
Power BI/Gold/Silver at 8,765 / 8,765 / 7,661 and invoked the definition judge.
It then held on a judge/support text-bound mismatch; synthesis did not run and
Bronze was not read. This is divergence evidence, not an end-to-end pass.
[Depth, limits and failed-run evidence](docs/declared-chain-depth.md).

[Source-application ingestion design](docs/source-application-ingestion-plan.md)
is ready for review only: a declared managed connection/copy mapping, new isolated
fixture and current discovery context, plus separate latency/gap evidence work.
No pipeline, Copy Job, connection or ingestion fixture has been built.

**Prior output milestone:** schema-enforced plain business explanations, mandatory
outcome-derived actions, and technical attestation details are implemented and
validated in one live run (BUSINESS_QUESTION). Earlier freezes remain invalidated.
[Output contract](docs/enforced-dual-outputs.md).

**First completed end-to-end investigation, 2026-09-27:** run `c2658c88`
completed intake, one genuine Power BI/Fabric SQL comparison, and validated
synthesis. Both values were 8,765. This is one ticket in one known domain,
**one of four intended boundaries**, no divergence path, no `judge_definition`
invocation, and **0 investigation planner calls**. It does not establish full-chain
correctness or unfamiliar-domain reliability. Five surface fields remain
unattested; freshness was skipped. The original output defects are preserved.
[Milestone and verbatim outputs](docs/first-completed-investigation.md).

The historical [whole-chain audit](docs/whole-chain-investigation.md) found that the engine
already descends on equality, but its adapter emits only presentation and Gold.
Two Silver dependencies are resolved metadata; the Bronze loop is unresolved by
the collector. The deployed notebook seeds Bronze from literals, with no declared
Azure SQL ingestion. Silver/Bronze reader table access passed; the source probe
failed at connection. The later output and depth milestones above supersede its
then-pending implementation work; its original evidence remains unchanged.

The valid-pair intake schema also passed five earlier same-ticket intake/preview
trials. [Intake evidence](docs/intake-valid-pairs-five.md).

An enterprise process debugger for Azure SQL, Microsoft Fabric and Power BI.
It has automatically discovered a newly published model and reports and made them
available for investigation without manual registration. Known-domain trials have
reached source mechanism evidence while preserving unknown business intent.
**Reliable investigation of unfamiliar domains has not passed acceptance.** The
target is to discover an approved environment and debug discrepancies by checking
whether each reachable process stage preserved a scoped quantity, using bounded
read-only queries and saved evidence. It reports implemented behavior and never
decides whether a business rule is correct.
This is an FDE integration with one enterprise environment.

**Historical normalization checkpoint:** shared quantity normalization now excludes only declared
surface-report columns. Saved R2's normalized comparison validates offline;
synthesis then stops on an ingestion-context `metadata` contract gap. No live
run or synthesis success is claimed. [Normalization evidence](docs/quantity-normalization-offline.md).

**Historical surface-key checkpoint, 2026-09-27:** synthesis now compares execution surfaces by
engine, connection and object while retaining identity as evidence. The requested
R2 scenario rerun was held at intake; synthesis did not run. Offline saved-R2
validation exposes a second blocker: raw result aliases differ despite equal
normalized quantities. An audit proves the original three intake requests were
byte-identical; independent schema enums allowed the model's incompatible
`MISMATCH_COMPLAINT` + `NONE` responses. Intake is unchanged pending review.
See [surface fix and intake audit](docs/synthesis-surface-key-intake-audit.md).

The following checkpoint is preserved as the preceding result.

**Historical re-approval checkpoint, 2026-09-27:** discovery was re-approved under the unchanged
current config (88 metadata/catalog operations). Of exactly three new attempts,
two were held for an invalid intake pairing; one reached a real, equal Power BI
DAX-to-Fabric-SQL comparison with the reader identity attested on both sides.
That run returned deterministic `CONSISTENT_TO_BOUNDARY` with incomplete surface
attestation explicitly limited, then **synthesis blocked before its model call**
because the evidence validator rejects the probes' identity field. No engine
change was made and no end-to-end or unfamiliar-domain pass is claimed.
See [re-approval and three-run evidence](docs/discovery-reapproval-three.md).

The earlier checkpoint narrative below is retained as historical evidence.
Statements that no table/comparison read had occurred, or that DAX self-report
was only tested offline, are superseded by this checkpoint; all earlier failed
runs and their original claims remain preserved.

Earlier boundary audit: review of the [correct-context three-run check](docs/correct-context-process-three.md)
found that both apparent semantic-to-Gold comparisons executed inside the same
Power BI model. They are requalified as within-model definition checks; the two
boundary claims and partial-pass statement are withdrawn without rewriting their
historical receipts. Probes now identify their engine, connection and object, and
consistency requires an equal comparison across distinct execution surfaces.
The existing reader cannot currently acquire a SQL-audience token for the Gold
analytics endpoint (`AADSTS65002`), so the active limit is
`NO_INDEPENDENT_LOWER_READ`. No permission was changed, and no freeze or unfamiliar-
domain acceptance pass is claimed.

An [execution-surface inventory](docs/execution-surface-inventory.md) then probed
which surfaces answer today, without changing the engine or any permission. Four
distinct surfaces responded: the Power BI semantic model via DAX, Azure SQL `app`
via the existing SQL reader, OneLake Delta commit metadata, and the first four
bytes of a OneLake data file. The Fabric SQL endpoint was not re-probed. No
lower-layer quantity was compiled or compared. The adapter's SQL reader
(`execute_source`) is still never called, and it can reach only Azure SQL
`app`, not the lakehouse table the process path resolves. The semantic model
is Direct Lake over that lakehouse. Whether a OneLake-file read would count as
independent, and whether the metadata identity may read rows, are open human
decisions.

**Correction, 2026-09-26.** The statement above that the endpoint is blocked on
`AADSTS65002` describes one client, not the endpoint; the original is kept as
written. A SQL-audience token was issued for tenant administrator
`admin@skynwhy.com` through the isolated Azure CLI profile (the one
`scripts/fabric_sql_auth.py` uses), with no app registration.
- **Which endpoint was reached:** the `gold_sql_endpoint` host in
  `infra/fabric/environment.json` accepted the token, and `SELECT 1` returned 1.
  That host belongs to the dev workspace `ws-investigator-dev` (`09cea7db…`),
  endpoint `701ab1fc…`. It is not the workspace investigations run against
  (`149f8d99…`). A connection naming no database opened that workspace's
  `lh_investigator_bronze`.
- **What that establishes:** only that admin can reach the dev workspace's SQL
  endpoint. It says nothing about `77c49180…` (`warehouse_gold_e1b8e1`), the Gold
  endpoint the process path needs. No identity has reached that endpoint over
  SQL, so `NO_INDEPENDENT_LOWER_READ` still stands.

See the
[inventory correction](docs/execution-surface-inventory.md#correction-2026-09-26-fabric-sql-endpoint)
for the three resolved IDs.

**Correction, 2026-09-26 (read at 20:43 UTC).** The statement above that no
identity has reached `77c49180…` is superseded; the original is kept. In a
single read at 20:43:40–20:43:54 UTC, the least-privilege reader `investigator-reader@skynwhy.com` (workspace
`Viewer` in `149f8d99…`) obtained a `database.windows.net` token through the
Azure CLI client (`04b07795…`), from its own isolated profile
`.local/azure-reader-sql`. No new permission was granted and no app registration
was created. The Gold endpoint `77c49180…` accepted it, with database
`warehouse_gold_e1b8e1` named explicitly. `SUSER_SNAME()` returned
`investigator-reader@skynwhy.com` and `DB_NAME()` returned
`warehouse_gold_e1b8e1`, so the server, not the client, confirms both identity
and database.

`NO_INDEPENDENT_LOWER_READ` is therefore no longer forced by authentication.
The engine still reports it, because `evaluate()` has no path that reads this
endpoint.

**Update 2026-09-27 (item 2b).** The statement above, that `evaluate()` has no
path that reads the endpoint, is superseded; the original is kept. `evaluate()`
now reads a faithfully declared `declared_source` layer on the Fabric SQL
endpoint as the reader. See [independent lower read](docs/independent-lower-read.md).

Still not established:
- **No table read:** only `SUSER_SNAME()` and `DB_NAME()` were queried.
- **No `DENY` check:** no explicit T-SQL `DENY` has been checked.
- **Viewer is broader than needed:** it grants ReadData on all 12 SQL endpoints
  in the workspace, including every fixture's Bronze and Silver.
- **Admin still hardcoded:** `scripts/fabric_sql_auth.py` still hardcodes the
  admin account and profile. No code path uses the reader's token.

**Correction, 2026-09-26 (item 2a).** The statement above that
`scripts/fabric_sql_auth.py` hardcodes the admin account and profile is
superseded; the original is kept. Both now come from configuration
(`fabric.sql_session`, `fabric.sql_reader`). See
[surface self-report](docs/surface-self-report.md).

Item 2a adds an engine invariant: **an execution surface is established by the
surface's own answer.** A probe whose surface does not report on itself, or whose
report contradicts the declared surface, is `UNAVAILABLE`, never `OBSERVED`.
- **Fabric SQL:** the Gold endpoint, as the least-privilege reader, reported
  identity and database matching the declaration.
- **DAX:** the DAX self-report (`USERPRINCIPALNAME()`) is verified only in
  tests. During the probe, Power BI rejected even the unchanged baseline query
  (HTTP 400, Analysis Services `0xC1450012`), so live DAX baselines are
  currently `UNAVAILABLE`.

No lower-layer quantity is compiled yet; that is item 2b. See the
[surface self-report record](docs/surface-self-report.md).

The required three-run follow-up was launched after PR #235 merged, but all three
attempts failed before intake because the harness command omitted its required
`--environment` argument. They opened no sessions, made no provider or data calls,
and left usage unchanged. The failures are preserved in the
[checkpoint report](docs/independent-boundary-three.md); no fourth run was launched.

The [process-debugging redesign](docs/process-debugging-redesign.md)
replaces open-ended search as the primary path. Intake distinguishes mismatch
complaints from business questions. A deterministic vertical procedure establishes
the presentation baseline, walks a discovered path of any length, compares only
faithfully translatable quantities, stops at the first evidence-bound explanation,
and always reports its visibility boundary. Thirteen closed outcomes bind claims to
required receipts and recommended actions. The adaptive loop remains the
`NO_KNOWN_PATTERN` fallback. The first three-run smoke established its baseline
and synthesis gates, then exposed an overclaim: zero comparisons cannot support
`CONSISTENT_TO_BOUNDARY`. The [corrected contract](docs/no-comparable-path-correction.md)
adds `NO_COMPARABLE_PATH`, requires real comparison evidence for verification
claims and distinguishes asset lineage from comparable-quantity bindings. Three
corrected runs stopped without a false consistency claim, but #232 later showed
they read the wrong discovery environment. Their missing-binding and structural-
limit conclusions are withdrawn. No freeze or unfamiliar-domain claim follows.

## What works today

- An independent lower-layer read. For a faithfully declared `declared_source`
  layer, the engine compiles the equivalent quantity from the model's
  declarations and reads it on the Fabric SQL endpoint as the least-privilege
  reader, with read-only guard and self-report. Original R2 completed one equal
  DAX-to-Fabric-SQL comparison. Run c2658c88 subsequently completed synthesis;
  declared Silver/Bronze quantity paths are now supported. The latest run
  compared two boundaries and stopped at the Gold-to-Silver divergence;
  Bronze was not read and no application ingestion binding exists.

- Execution-surface self-report is enforced for every process probe. The Fabric
  SQL analytics endpoint and DAX self-reports were verified live in original R2,
  as the least-privilege reader. Unattested surface fields remain explicit limits.

- Related 100,000-order application data, Azure SQL source, deployed order portal,
  Fabric Bronze/Silver/Gold processing and native Power BI model/reports.
- Environment-owned metadata scans, per-surface coverage, versioned changes and
  evidence-backed context graphs. Supported discovered models/reports enter the
  ticket catalog automatically; manual registration remains a compatibility override.
- A deterministic vertical process debugger over adapter-provided discovered paths.
  It establishes a scoped presentation baseline, compares adjacent quantities,
  retains every query verbatim, exits early on an evidence contract and reports
  the deepest reachable layer. The adaptive LLM loop remains a bounded fallback.
- A local workspace with business questions, reviewed screenshot transcription,
  scope review, history, cancellation and shared business/technical evidence.
  Read-only identities, budgets and replay controls remain in place.
- The older bounded-v1 investigator and reviewed routing workflows remain available.

PR #192 is merged. Its count/sum diagnostic captures a native total and supporting
record groups together. Complete, empty and truncated live cases were checked;
this is arithmetic consistency, not general root-cause proof.

## How it works and what changes next

An operator approves a workspace/database profile once. Scans discover supported
models independently of reports and publish technical context without mandatory
business review. Explicit deny and the separate reader policy still govern access.
The complete target flow is:

```text
Approved connections -> recurring discovery -> versioned enterprise context graph
Business question / screenshot -> context resolution -> LLM hypotheses and tests
Policy + read-only tools -> real observations -> revised tests -> qualified outcome
Shared business/technical view -> human-reviewed handoff
```

Power BI remains the DAX engine. The LLM interprets context and chooses tests;
deterministic tools supply facts. New supported assets should require discovery,
not investigator-specific code changes.

## Current milestone and limitations

The declared path extension and divergence repeat are recorded above. Complete
prose guards and substantive business output passed the latest known-domain
repeat. Source-application ingestion remains design-only; actual join multiplicity,
common snapshot and business intent have not been established by that run.
See [current status](docs/current-delivery-status.md) for the active checkpoint.

### Historical milestone evidence

The following release-specific results and proposals preserve their original
checkpoints; their next-step statements are not the current work order.

The redesign implementation passed **1,046 local regression tests**. Focused tests
cover all thirteen evidence contracts, arbitrary path length, early exit, explicit
`NOT_COMPARABLE`, intake triage, an end-to-end known-domain adapter run and all four
#226 synthesis failures. Planner golden payload content and directory coverage are
unchanged; only response schemas changed. The required three corrected recorded
G trials completed after PR #229 merged. All three reproduced 8,765, then stopped
at step 3 as `NO_COMPARABLE_PATH` with zero resolved boundaries, zero comparisons,
one DAX read, no SQL reads and no investigation-planner calls. #232 later proved
they opened `development` rather than the intended warehouse discovery context;
their missing-binding and structural-limit conclusions are withdrawn. All
syntheses validated and all six tapes passed integrity checks. The runs still
validate the false-consistency fix and refusal to name-match, but do not exercise
divergence localization or model judgment over a transformation definition. No
unfamiliar-domain acceptance pass is claimed. The corrected engine passes **1,052
local regression tests**; investigation planner payload content and coverage remain
unchanged.

The capability checkpoint merged with **1,073 tests and six green CI
checks**; the harness correction passed **1,074 local tests**. Its three recorded
runs each reproduced 8,765, but all used the wrong
catalog environment because of a hard-coded evaluator default. They consequently
made zero comparisons and ended at step 3. All failures remain recorded; one of
three syntheses completed, two failed validation, and all six tapes verify. The
harness now requires the exact discovery environment and has an isolation
regression. The later correct-context checkpoint above reached real equal
comparisons in two sessions; definition judgment remains unexercised because no
comparison diverged.

The previous separated-synthesis experiment is complete ([PR #222](https://github.com/bcsnpc/data-investigation-agent/pull/222)).
Three corrected known-domain G trials produced **3/3 receipt-supported uncertainty
assessments**, versus 0/3 in #221 arm A; one already had an assessment before
synthesis. No cause was verified. Two support fields were clipped, so explanation
quality remains incomplete. Three larger-input controls produced **0/3 assessments**:
two hit the planner-call limit and one stopped for no progress, with input available.
This small sample does not establish general reliability or rule out other bounds.

Synthesis uses one independently metered call over a deterministic frozen digest,
without the trajectory, directory or raw query-result rows. An initial metadata
excerpt defect was fixed; both initial completed attempts and the cancelled third
attempt remain recorded. Final validation: **1,026 local tests and six corrected
implementation CI checks passed**. The corrected batch's reference token cost was
**USD 4.08**, excluding intake/cloud costs; original daily policy was restored
without refunds. See [results, limitations and proposal](docs/separated-evidence-synthesis.md).

The earlier pooled G result remains **1 qualified conclusion in 15 runs** across
#220/#221, not a reliability foothold. Three independent synthesis passes were
**proposed only** and are deferred. Support preservation and the
nine-run calibration are complete; the next proposals await review.
Typed dependency traversal remains a later candidate, not implemented. Larger input
is an experimental control, not a new default. No freeze or unfamiliar-domain claim.

The following describes the completed #221 milestone:

The controlled twelve-run G experiment is complete. The
[offline trajectory audit](docs/g-trajectory-audit.md) showed genuine hypothesis
revision, with read admission preventing a final synthesis turn in prior G2/G3.
A once-per-connection registry preserves all 53 historical directory views:
F stays at **28 entries / 11 SQL objects**, with **477 added pre-wire characters**.
Saturated prompts omit the optional registry without evicting evidence. Dynamic
runs default to 15 reads; the experiment compared 6/15 reads and medium 8,000/high
16,000 output profiles while keeping other run limits fixed.

All twelve known-domain runs ended UNRESOLVED: **124 planner calls, 62 SQL + four
native reads, eight query rejections, zero provider errors and no qualified final
assessment**. Input admission stopped every higher-read run; two also exceeded the
per-call protected-context limit. No arm establishes improved conclusion
reliability. Reference-priced planner tokens cost **USD 8.86**, excluding intake
and cloud costs; this is not Azure billing. Original daily policy was restored
without resetting usage. SQL free-tier settings and provider capacity are unchanged.

Validation: **1,016 local regression tests and six implementation CI checks passed**.
See [results, context limits and concurrency proposal](docs/g-read-reasoning-experiment.md)
and [PR #221](https://github.com/bcsnpc/data-investigation-agent/pull/221) for final CI.
That milestone's input-sizing proposal has since been tested as a temporary control;
two-process investigation concurrency remains proposed only. The stopping
contract remains evaluated and not adopted. No freeze, new variant or unfamiliar-domain claim.
[Original #219 results](docs/physical-binding-reliability.md),
[negative stopping result](docs/stopping-criteria-review.md) and
[original nine-family SQL audit](docs/baseline-sql-proposals.md) remain historical evidence.

Item 1 of the ordered offline reliability plan merged in PR #209: opt-in exact
planner request/response recordings and loadable local fixtures. Recordings include
runtime context, budget and reservation metadata; credentials and headers are
excluded. Transport tests use no live LLM calls. See the
[recording runbook](docs/planner-call-recordings.md).
Item 2 merged in PR #210: planner-view goldens, counted omissions, preserved
links and deterministic fitting; 968 regression tests passed.
Item 3 merged in [PR #211](https://github.com/bcsnpc/data-investigation-agent/pull/211): a recorded-provider session simulator runs the actual
runtime over isolated database copies with network access blocked. Five focused
tests cover complete replay, malformed proposals at each step, prerequisite
rejections, recorded timeouts and input/configuration safeguards. Saved completed
query receipts are reused; no fresh SQL/DAX execution or business correctness is
claimed. All 973 local regression tests passed. See [replay evidence](docs/offline-session-replay.md).
Item 4 merged in [PR #212](https://github.com/bcsnpc/data-investigation-agent/pull/212): identical duplicate updates and descriptive text bounds
are repaired locally; missing approved SQL schemas are fetched before dispatch.
Repairs have separate events and do not change executable query text or authority.
Six repair and five replay tests passed; all 979 regression tests passed. See
[local repair evidence](docs/local-proposal-repairs.md).
Item 5 merged ([PR #213](https://github.com/bcsnpc/data-investigation-agent/pull/213)):
compiled SQL/DAX duplicates reuse sealed receipts without another data read.
Eleven focused checks cover alias normalization and admission of distinct reads;
result equality is a reporting-only metric. Recording exclusions no longer abort
provider calls. All 994 regression tests and six CI checks passed.
F-paced remains failed for test selection and is no longer the duplicate gate.
See [redundancy evidence](docs/conservative-read-redundancy.md).
Item 6 merged ([PR #214](https://github.com/bcsnpc/data-investigation-agent/pull/214)) separates retrieval allowance from two protected test-planning turns
within the existing total. Five focused checks include four lookups and two mock
reads in six calls with exact offline replay. Session metrics report reads and the
retrieval/test ratio. All 999 regression tests and six CI checks passed. See
[budget evidence](docs/retrieval-test-budgets.md).
Item 7 merged in [PR #215](https://github.com/bcsnpc/data-investigation-agent/pull/215), adding twelve synthetic intake captures covering nine ticket families
and three specific missing user facts. All nine reach reviewed investigation and
a mock read; negative probes reject unnecessary metadata clarification. Four tests
passed; all 1,003 regression tests and six CI checks passed. This checks admission and replay of
controlled responses, not live LLM judgment. See [intake evidence](docs/intake-family-regressions.md).
Item 8's [capacity report](docs/provider-capacity-readiness.md) recorded the original
10,000 TPM / 100 RPM allocation. The approved increase now reads back as 100,000 TPM
and 1,000 RPM. The known-domain baseline gate precedes any freeze or publication.
V4 remains invalidated. See [current status](docs/current-delivery-status.md).

Current reliability work makes conclusion support explicit: a proposed mechanism,
its evidence, dependency on business intent, and remaining useful tests. The
validator rejects a defect/expected-behavior label that explicitly depends on an
unknown intended rule. This catches structural contradictions, not semantic truth;
interpretations remain LLM_INFERRED. Targeted search and discriminating-test guidance
are under known-domain evaluation. See [conclusion quality](docs/conclusion-quality.md).
The previous [provider response milestone](docs/provider-response-reliability.md)
added safe failure categories, retained numeric usage and aggregate-query admission
checks; its 943 regression tests passed. Default model settings remain unchanged.

Structural-discovery work added automatic structural hypotheses to discovered
model context, SQL/DAX capability descriptions from the validators, and autonomous
structural experiments during relevant tickets. Keys, grain, join behavior,
functional dependencies and freshness can be tested through the existing bounded
read-only tools. Metadata guesses remain distinct from measured evidence and
business intent. Scans do not launch background data profiling. See
[structural discovery](docs/structural-discovery.md). The frozen unfamiliar-domain
challenge remains the main acceptance gate; these additions do not replace it.
Earlier known-domain transformation runs timed out or stopped at business-context
questions without measuring source join behavior. A discovered compaction bug
removed retrieved transformation text from later planner prompts; bounded evidence
retention now preserves recent excerpts and their provenance. That milestone passed
939 local regression tests. Its final known-domain trial reached both source schemas
without proposal rejections or repeated lookups, but a provider-response error
stopped it before SQL execution. A separate quality-profile ratio trial completed
the requested value/component explanation in two planner calls and one native read,
while the default model asked an unnecessary clarification. General reliability
and unfamiliar-domain acceptance remain unproven.


**Discovery-to-ticket (Stages 2–3)** merged in PR #196. **Dynamic reasoning and
governed tools (Stages 4–5)** merged in PR #198. The v4 attempt remains historical discovery evidence. The preceding v3 attempt discovered its new model
and reports automatically, then exposed excessive planner-profile truncation.
The generic correction required a fresh freeze and variant. The first nine-family trial recorded partial reads,
reasoning failures and provider rate-limit blocks; it has **not passed**.
[Challenge acceptance](docs/unknown-domain-challenge.md) remains in progress.
[Current delivery status](docs/current-delivery-status.md) owns
implementation and verification claims; [stages 1–9](docs/architecture/phases-and-acceptance.md)
define remaining work.

Discovery currently uses one approved workspace and SQL database/schema per profile.
Finite repeat scans support an external scheduler; no persistent scheduler is installed.
Denied/unsupported metadata is explicit. Warehouse catalogs require an approved
endpoint adapter. Search exposes context but does not grant query authority.

Generated queries support explicit grammar subsets; SQL views are not yet admitted.
Practical assessments are evidence-qualified LLM interpretations, not verified causes.
Frozen unknown-domain acceptance remains pending. The legacy manual
catalog retains its review gates. Runtime report filters/RLS and cross-system
comparability remain explicit limits. V2 is local and single-operator; enterprise
hosting/authentication is pending. The earlier context/query recovery revision passed
920 local regression tests and 10 dynamic browser checks. The structural-discovery
revision passed 929 regression tests; its ten browser checks preceded the final
profile projection correction. Structured definitions, parent-qualified asset search, missing-schema
recovery, actionable query feedback and remaining-time context are implemented.

A GPT-5.4 known-domain trial completed a qualified join-multiplication diagnosis:
one Power BI read and two SQL reads reproduced 57,043 and linked it to the inspected
notebook logic. It preserved uncertainty about the intended rate-selection rule
and corrected total. Earlier trials remained unresolved; one successful case does
not establish model superiority or unfamiliar-domain generality. The default model
is unchanged. SQL firewall error 40615 was resolved by a user-approved single-IP
rule; free-limit AutoPause remains.
See [context/query recovery](docs/context-query-recovery.md) and
[quality engineering research](docs/investigation-quality-engineering.md).
These checks do not establish unfamiliar-domain acceptance or retest every
deployed application.

## Run and demo

- [Local v2 workspace setup](docs/investigation-workspace-milestone.md#local-runbook)
  and [reviewed screenshot intake](docs/screenshot-intake-milestone.md).
  Install `scripts/requirements-workspace.txt` in your development environment.
  Keep provider credentials and workspace token outside Git. Execution requires an eligible discovered or enabled legacy catalog and
  configured provider access. Discovered execution requires a separate reader.
- [Environment discovery runbook](docs/enterprise-discovery-milestone.md).
- [Dynamic investigation behavior and limits](docs/dynamic-investigation-milestone.md).
- [Model admin fallback](docs/model-onboarding.md) and
  [metadata scan worker](docs/catalog-scans-and-semantics.md).
- [Bounded-v1 presenter runbook](docs/demo-runbook.md): historical demonstrations,
  not proof of unfamiliar-domain self-discovery.
- [Order portal setup](docs/order-portal.md), [synthetic data/loading](docs/synthetic-data.md)
  and [runtime identities](docs/runtime-identities.md).

Development order portal: https://orderops-portal-9696025.azurewebsites.net

## Engineering and plan

[Controlling mission](SELF_DISCOVERING_ENTERPRISE_INVESTIGATOR_PLAN.md) |
[Architecture and audit](docs/architecture/README.md) |
[Current status](docs/current-delivery-status.md) |
[Progress history](docs/progress.md) |
[Handoff](PROJECT_STATE_AND_NEXT_STEPS.md) | [Contributing](CONTRIBUTING.md)

Keep SQL free-overage settings unchanged. Query/result limits do not guarantee zero
resource cost. Automatic production repairs, deployments and data mutations are
outside the investigation product boundary.
