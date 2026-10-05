Dated Round Six C offline checkpoint, 2026-10-05: fifteen sealed proposals audited: thirteen outside the sampled quantity, one string-deduplication equivalence unavailable, one source worker failure. Only the separate application copy is manifest-declared; its compiler round-trip matches the sealed requests and 7,661/7,661 observations offline. A's scoped outcome was correct, not a regression. Offline compiler/verifier and explicit unbound output infrastructure are separated from #406 runtime activation, which remains draft. No live read, scope change, cap change or fixture mutation here. Archived producer replay passed 15/15 with zero reads; 1,974 integrated-branch regression tests passed, and the independent offline compiler/verifier/rendering tests passed. CI is tracked on #407; prior freezes invalid. See docs/round-six-unverified-audit.md.

Dated explicit code-identity decision, 2026-10-05: Round Six B supersedes the
read-only code-fetch stop below only for a separate investigator-code-reader.
App 2dd2f5c3-f7af-4804-b79e-6019e63efa60; principal
dc89155f-9a9a-4daa-9c20-7eff55818ccd. Contributor on fixture workspace
149f8d99-1c66-4a0a-9624-759be002bb60 only; both fixture publications declare
that same workspace. Code-definition API only, never investigation execution.
Existing investigation identities unchanged; DPAPI credential local only.
CODE_READ_REQUIRES_WRITE_SCOPE remains a platform limitation; Git read-only
and local export sources avoid that scope. Definition fetched and scanned clean;
full transformation-reader verification remains pending. Pot14/400, reserve60.
See docs/round-six-code-sources.md for human decision and before/after.

# data-investigation-agent — charter for AI implementers

Dated documented route constraint, 2026-10-05 America/Chicago: Fabric Notebook,
Data Pipeline and generic Item Get Definition APIs require item read AND write
permission according to Microsoft Learn. Round Six approved read only and
explicitly forbade write, so its reader-fetched transformation section stopped.
No reader probe or grant was attempted; this is documentation evidence, not a
tested HTTP403. Do not substitute publisher-fetched code for reader evidence.
See docs/round-six-transformation-reader.md for links and the contract audit.

Dated hosted gate delivery, 2026-10-05 America/Chicago: #376 merged as f4378df
with six ordinary checks and the real hosted fifteen-tape check green. The
actual main merge commit also passed15/15 in run37278367358. Archived producer
replay is distinct from current-engine or unfamiliar-domain acceptance.
Round Six spent0/400 estate physical requests;60 reserved, rolling386/1500.
The reader/inferred-column sections remain blocked, not implemented or verified.

Dated Round Three finding, 2026-10-04 UTC: the approved ops Warehouse audit
producer independently retrieved own copy 361/361 and 360/360 counters and
activity timestamps matching the reader's pipeline activity-output response.
Qualified INGESTION_GAP and LOAD_LATENCY executions completed. Matching counters
do not prove individual delivery or aligned snapshots. Two subsequent consistency
tickets returned NO_COMPARABLE_PATH after intake added grouping; no source
consistency claim was earned or expected absence backfilled from fixture truth.
Original failures/outputs preserved. Reader restoration: isolated application,
landing/model 7,661; original model 8,765. Part B 466/500, rolling last observed
590/1,000, diagnostics 12 unchanged. See docs/round-three-source-scenarios.md.

Dated audit-surface finding, 2026-10-04 UTC: administrator direct Delta reads
establish that both newer audit rows committed, with own 361/361 and 360/360
copy counters. The earlier reader SQL receipt omitted the first at least 6m20s
after commit; later SQL exposes both. This establishes lakehouse SQL audit sync
lag, not writer failure. Investigator-reader direct OneLake returned HTTP403;
no new scope was granted. Audit guidance: Warehouse or authorised direct Delta,
never infer last-run currency from a lakehouse SQL endpoint. The prepared
table-only read role awaits human decision under section 8. See
[audit evidence](docs/audit-row-validation.md).

Dated supersession, 2026-10-04 UTC: the human declined the OneLake audit grant
and approved the Warehouse route. Audit tables live in a Warehouse, never
behind a lakehouse SQL endpoint. LAKEHOUSE_SQL_AUDIT_SYNC_LAG observed at least
6m20.259836s, receipts preserved. An isolated ops Warehouse now holds the audit;
investigator-reader received SELECT on that table only by explicit human decision.
The first reader audit row matches own copy 360/360 counters and times. No
OneLake grant. See docs/audit-row-validation.md and the adapter known limits.
The earlier pending OneLake proposal above is historical.

Read this before changing anything. It is not style guidance. Every rule below
exists because breaking it previously produced a false conclusion that survived
review.

Dated Round Four finding, 2026-10-04 UTC: a fixture-authored follow-up earned
CONSISTENT_TO_SOURCE with equal 7,661 quantities and independently observed
expected-record absence through semantic, landing and application. The first
attempt's application quantity failed SQL 40613, while membership succeeded;
it remains CONSISTENT_TO_BOUNDARY, not retrospectively upgraded. Configured
unreachable stopped at landing and retained own Warehouse load accounting.
All three synthesized; PARTIAL connection coverage and SNAPSHOT_UNVERIFIED
remain. Source-consistency business prose repeats timing; keep that finding.
Round Four 51/300; rolling last observed 641/1000; Part B closed at 466/500.
Original baselines 7,661/8,765 verified, reachability restored. No new grants.
See docs/round-four-source-scenarios.md. Prior freezes remain invalid.

## What this system is

A technical debugger for reported number discrepancies across a data stack.
Given a complaint that a number is wrong, it traces that number through the
layers that produce it, locates where behaviour explains the difference, and
classifies what it found.

It reports whether behaviour is **by design, latency, failure, or defect**.

## What it is NOT

**It never judges whether a number is business-correct.** This is the governing
non-goal. The system states the mechanism and its category; the user decides
whether the design is right. A filter in a transformation is not a bug and not a
non-bug — it is a design choice, reported as such, with an enhancement request
as the available action.

It also does not explain business causation. "Why did discounts rise" is not
answerable from pipeline evidence.

## Non-negotiables

1. **Evidence must be produced by the thing it claims to be evidence about.**
   Where it cannot be, the output is an explicit unavailability, never a
   plausible substitute. A stub that returns `{'status': 'UNAVAILABLE'}` is not
   a finding and must never be consumed as one.

2. **Eligibility to run is not eligibility to conclude.** A procedure may be
   applicable and still be barred from an outcome because the evidence contract
   for that outcome was not satisfied. Capability gating enforces this; do not
   route around it.

3. **Cross-surface invariant.** Two quantities compared across a boundary must
   come from different execution surfaces. Same engine, same connection, same
   object is a within-layer check and must be labelled
   `WITHIN_LAYER_CHECK` / `NO_INDEPENDENT_LOWER_READ`. It is never a boundary
   comparison, however the values come out.

4. **Faithful equivalence or nothing.** If a quantity cannot be expressed
   faithfully at a lower surface, the boundary is `NOT_COMPARABLE`. Never
   approximate, never guess an equivalence, never infer a binding from name
   similarity.

5. **Platform neutrality above the adapter layer.** Nothing in the engine,
   prompts or configuration may name a platform, product, layer convention,
   domain table, metric formula, expected value, or required investigation
   route. Whether a layer is a Delta table, a Snowflake view, a dbt model or a
   semantic model is the adapter's concern alone.

6. **Provenance is explicit.** `DECLARED_BY_DEFINITION`, `INFERRED_FROM_CODE`
   and discovered bindings are distinct and must stay visibly distinct to the
   planner. An inferred binding is a hypothesis about the estate, not a fact.

7. **No credentials, keys or tokens in source.** Local run artifacts stay under
   `.local/` and are not committed.

8. **No app registration is created or amended, and no identity gains a new
   audience or scope, without an explicit human decision.** Report what would be
   required and stop.

## Known platform limits: served-snapshot metadata (2026-09-27)

These are tested limits of the current least-privilege Fabric/Power BI reader,
not a to-do to acquire elevated execution permissions. The reader can read
values but cannot establish which data version those reads served through the
tested routes.

| Route | Tested reader result | Constraint |
| --- | --- | --- |
| Power BI REST refresh history | HTTP403 | Requires dataset Write. |
| XMLA TMSCHEMA partition refresh metadata | Refused | Requires administrator metadata access. |
| DAX `INFO.DELTATABLEMETADATASTORAGES()` | Refused | Requires administrator; no framed Delta version returned. |
| DAX `TABLETRAITS()` | Refused | Requires administrator; no fallback-mode indicator returned. |
| Fabric SQL `sys.dm_db_external_tables_log_status` filtered to the source table | Accepted, zero rows | No Delta version returned. Empty results do not establish a permission denial or identify why the row was absent. |
| Fabric Copy Job run history and completed-instance detail (2026-10-03) | HTTP 200 for the least-privilege reader: generic and Copy Job-specific detail returned Completed with start/end times; history listed that instance | Positive capability without elevation, unlike dataset refresh history. These responses contain no capture cuts or rows-read/written; do not substitute quantity counts for load accounting. The earlier empty-history probe is preserved. See docs/round-two-ingestion-estate.md. |
| Fabric Copy Job monitoring KQL accounting attempt (2026-10-03) | accounting unavailable from this surface; no KQL query occurred | Authorized enablement was blocked by unavailable browser UI; before/after listings expose no monitoring database. SQL served orderops_investigator as contained SQL_USER / DATABASE; KQL needs an Entra principal. Documented RowsRead/RowsWritten are not observed counts. No reader substitution, elevation or grant. See docs/round-two-workspace-monitoring.md. |

Dated supersession, 2026-10-03: the user authorized a separate Entra monitoring reader, `dia-reader` (client ID `ddd4d3cf-9cfd-440e-ac5b-be127caa46ea`, service principal object ID `59dd402b-1510-4289-96fb-f1d34d4494c5`). Registration and local DPAPI credential storage succeeded; the SQL `orderops_investigator` remains unchanged. Fabric public APIs are enabled with no group restrictions returned. The complete fixture listing still has no monitoring Eventhouse/KQL database; stop before viewer grant, KQL probes or an extra load. Accounting remains unavailable from this surface because it was not queried, not because the table was empty. No workspace role or elevation. See [dedicated reader record](docs/round-two-dia-reader-monitoring.md). Earlier blocked entry remains historical.

Dated authorized resume, 2026-10-03: monitoring enablement was authorized for the fixture only. The documented monitoring/Fabric-item tenant prerequisites return enabled and capacity assignment Completed, but no UI can be operated: browser unavailable; native automation pipe missing. Both complete item listings still lack monitoring resources. No setting, identity, grant or load changed; existing dia-reader retained. Accounting remains blocked before query, not an empty-table result. See [resume checkpoint](docs/round-two-monitoring-resume.md). Enablement and viewer-only database-grant verification remain pending.

Dated monitoring access finding, 2026-10-03: monitoring Eventhouse/KQL/Eventstream now exist in the fixture. As the existing publisher, the exact dia-reader database-viewer grant returned 403; principal listings before/after contain no dia-reader entry. Both dia-reader history queries returned 403 before schema/data evaluation. No refresh-history capability correction is established; this is a new route refusal, not absence of logged events. No workspace role or new successful permission. FTL4 trial capacity Active; Eventhouse minimum consumption 0 CUs, actual UpTime/storage unmeasured. See [exact statements and receipts](docs/round-two-monitoring-history-cost.md). Earlier resource-absence claims are historical.

Dated renewed viewer attempt, 2026-10-03: exact prepared grant again returned 403, with dia-reader absent before/after; Copy Job and semantic-refresh reader probes refused. Publisher effective roles are Viewer/Monitor (plus cluster viewer/monitor), not Database Admin. Human approval does not supply server grant authority; do not elevate or substitute a broader role. No presentation_freshness capability established. See [renewed receipt record](docs/round-two-viewer-grant-repeat.md) and [estate reader manifest seed](docs/estate-reader-manifest.md).

Evidence: [refresh-history/partition probes](docs/job-history-path-and-refresh-probes.md)
and [snapshot-version/fallback probes](docs/snapshot-alignment-audit.md), including
exact requests, responses and identity provenance. These results constrain the
current reader; they do not assert that every identity or estate lacks the APIs.

Do not elevate the execution reader or keep retrying these routes to make a
comparison appear verified. Distinct execution surfaces do not establish aligned
snapshots. Equal values do not establish currency; different values do not exclude
timing as the reason for the difference. A latest OneLake commit observed by the
separate metadata/fixture-owner identity is not the version served by a SQL or DAX
quantity read and must never be represented as reader attestation.

Snapshot attestation now defaults to SNAPSHOT_UNVERIFIED; see
[the implementation and limits](docs/snapshot-attestation.md). A separately
configured metadata identity may enrich the record, but a standalone metadata
query does not attest which version a quantity read served. Only genuinely
query-bound, aligned reports can produce SNAPSHOT_VERIFIED. No live verification
or freshness-fixture success is implied.

SNAPSHOT_VERIFIED is expected to be unreachable on the Microsoft adapter: neither metadata route binds its version to the value query (DAX is admin-gated; SQL returned no rows for the reader); other platforms can satisfy the contract by returning value and version in one statement.

## Refresh timing permission finding (2026-09-27)

The least-privilege reader was tested and refused by both routes: Power BI REST
refresh history requires dataset Write, and XMLA TMSCHEMA partition metadata
requires administrator. See docs/job-history-path-and-refresh-probes.md for exact
receipts. Do not elevate the execution reader or keep probing these routes.
The engine does not rely on refresh timestamps. A positively established unchanged
declared-source boundary may support comparison-based REFRESH_LATENCY after two
independent, attested quantities diverge. Missing timestamps and non-shared read
snapshots limit that claim. Optional estate-configured metadata timing uses its own
explicit identity provenance, never substitutes for quantity-reader evidence and
never selects an outcome.

## Comparison-based freshness context (2026-10-01)

Dated correction, 2026-10-02: surface consistency and coverage are separate.
MATCHED now means full coverage; PARTIAL means the reported fields match but
other declared fields remain unattested. Identity-only partial evidence may
support a qualified within-layer reproduction on the same declared route and
account, never verified cross-surface boundary evidence. Both sides of a verified
boundary must report the complete declared surface. The current Microsoft
Execute Queries route is permanently partial under its documented response
contract: USERPRINCIPALNAME reports identity; engine, workspace connection and
model object are not self-reported, and INFO/DMV queries are unsupported on that
route. This is a limit of the adapter/route, not every possible future platform
interface. Prior recorded MATCHED labels are preserved unchanged and do not
retroactively establish full coverage. See docs/explicit-absence-contract.md.

An unchanged declared source expression does not establish equivalent read context.
Comparison-based REFRESH_LATENCY requires explicit matching whole-entity context
on both completed observations, rechecked against the originals at validation.
Missing context is unknown; filtered/grouped scope is unsupported by this narrow
rule. Never infer empty context from an absent field or use differently scoped
quantities as freshness evidence. This states query scope, not the user's active
report selection. See docs/freshness-context-and-filter-fixture-plan.md.

## Evidence discipline

Reachable depth is a property of the estate, not the engine. The operator's
configured boundary depth is a CEILING, never a reachability or completeness
claim. Every lower layer still needs a declared binding, faithful quantity,
successful isolated read and surface attestation. Most estates will not expose
their source application. Early termination is a conclusion scoped to the named
verified depth, with every unchecked boundary and its reason in the limits of
both outputs. Never approximate a quantity to meet the configured depth.

- Preserve every failed, partial, interrupted and rejected run exactly as it
  happened. Never edit a frozen artifact, a stored receipt or recorded run
  evidence to make something pass.
- Corrections are **appended and dated**, never written over the original claim.
  If an earlier document asserted something later found false, add a dated
  correction; do not rewrite the original.
- Never upgrade a partial result into a verified cause, a general capability or
  an acceptance pass. Observed agreement is not proven continuity.

## Where the model is used, and where it is not

**Deterministic:** walking the path, evaluating quantities, comparing values,
locating the divergent boundary, retrieving definitions and run history,
producing the evidence chain.

**Model judgment:** interpreting the ticket into a measure and scope; choosing
vertical versus horizontal; deciding whether a retrieved definition actually
explains the observed difference; naming the mechanism in words; writing both
outputs.

**Never the model:** choosing which layer to look at next, inventing queries to
search with, or deciding whether a design is correct.

The model translates; it does not explore. A required layer order is banned —
requirements live in the support contract, not in an enforced sequence.

## Recording discipline — applies to every PR

A PR that changes behaviour and does not update these is incomplete.

- **`docs/runs/ledger.jsonl`** — exactly one appended line per run, live or
  offline. Never rewrite or delete existing lines, including failures. Counts,
  identifiers and outcomes only; never query text, result values, business data
  or provider message contents.
- **`README.md`** — must be true as of every commit. "What works today" states
  only what is implemented and verified now. Never describe an aspiration, a
  plan or a single successful trial as a current general capability.
- **`docs/current-delivery-status.md`** — owns implementation and verification
  claims.
- Failed, partial and blocked outcomes are recorded with the same detail as
  successes, including the stop reason and what was NOT established.
- If engine bytes changed, state explicitly that the current freeze is
  invalidated.

## Per-PR checklist

- [ ] One work item only
- [ ] Tests added that fail if the item's invariant is removed
- [ ] CI green: Python tests, PowerShell syntax, portal tests, build
- [ ] No domain names, metric formulas, expected values or required route in
      engine code, prompts or configuration
- [ ] No frozen artifact, stored receipt or recorded run evidence modified
- [ ] No secrets added; `.local/` artifacts not committed
- [ ] Ledger row appended for any run performed
- [ ] README true as of this commit
- [ ] `docs/current-delivery-status.md` updated
- [ ] Freeze invalidation stated if engine bytes changed

## Current state (update this section as it changes)

Dated correction, 2026-09-27: the historical statements below about no completed
investigation and no table read are superseded by run c2658c88, the first completed
known-domain investigation through one independently compared boundary and
validated synthesis. It did not exercise divergence or definition judgment.
See docs/current-delivery-status.md for subsequent work and current evidence.

- The outcome taxonomy and the vertical procedure are implemented in
  `scripts/investigator/process_debugging.py`.
- Capability declaration and gating work: `REQUIRED_CAPABILITIES`,
  `OPTIONAL_CAPABILITIES`, `applicability()`, and the pre-`DEFECT` gate that
  refuses a defect claim when competing explanations were not checked.
- The offline replay harness (`acceptance/unknown_domain/session_replay.py`)
  blocks network at socket level and matches requests byte-exactly.
- **The reader's Direct Lake access is restored** (2026-09-27 00:33 UTC).
  - **The fault:** the password reset at 2026-09-26T20:42:20Z left a stale
    service-side grant (`AADSTS50173`), masked by Execute Queries as
    `0xC1450012`.
  - **The fix:** it was cleared only by an interactive sign-in to the Power BI
    portal as the reader. A client MSAL sign-in and OneLake role membership did
    not clear it. No API exposed the remedy.
  - **Current state:** live DAX baselines as the reader are `OBSERVED` again,
    and the DAX self-report attests the reader's identity live. The reader holds
    no OneLake role membership.
- **No investigation has yet completed end to end.** The model's
  `judge_definition` call has never been invoked in a live run.
- The Gold Fabric SQL analytics endpoint the process path needs (`77c49180…`,
  `warehouse_gold_e1b8e1` in workspace `149f8d99…`) is reachable by the
  least-privilege reader `investigator-reader@skynwhy.com` (workspace `Viewer`).
  The reader signs in through its own isolated Azure CLI profile
  (`.local/azure-reader-sql`), with no new permission and no app registration.
  The server confirmed the identity and the database (2026-09-26). Not yet
  established:
  - No table has been read.
  - No explicit `DENY` has been checked.
  - Viewer is broader than needed.

  `evaluate()` reads a faithfully declared `declared_source` layer on this
  endpoint as the reader (item 2b). Otherwise `NO_INDEPENDENT_LOWER_READ` still
  applies. No comparison run has been performed yet. The Fabric CLI client
  still fails with `AADSTS65002`. The "isolated metadata identity" is the tenant
  administrator (`admin@skynwhy.com`), so its receipts are admin receipts.
- **Surface self-report is enforced and consumed** (`process_debugging.attest()`).
  - **Attestation:** a probe that claims a surface is `OBSERVED` only if the
    surface's own answer includes an identity, reports every field the probe
    declares it is able to report, and contradicts nothing declared. Otherwise
    it is `UNAVAILABLE`, with the missing report or the contradiction recorded
    and its prior status kept.
  - **Consumption:** every field a compared surface could not report is named
    in the claim's limits and in both outputs (`unattested_surface_fields`).
    Outcome validation refuses a comparison without a `MATCHED` attestation on
    both sides, or a claim that omits an unattested field.
  - **Fabric SQL:** answers with `SUSER_SNAME()`/`DB_NAME()`. Verified live
    once, as the reader, on `warehouse_gold_e1b8e1`.
  - **DAX:** answers identity only, via `USERPRINCIPALNAME()`; the model object
    is not attested. Not yet verified live: on 2026-09-26 the Power BI surface
    rejected even the unchanged baseline query (HTTP 400, Analysis Services
    `0xC1450012`), so every DAX baseline is currently `UNAVAILABLE`.
  - **SQL sessions:** `scripts/fabric_sql_auth.py` takes its account and profile
    from configuration (`fabric.sql_session`, `fabric.sql_reader`) and never
    falls back between them.
- Horizontal comparison, recurrence learning, declared business context and the
  known-issues register are **proposal-only**. Do not implement them
  opportunistically.

## Known past failures — do not reintroduce

- Adding reader and transport sections to an environment's config changed the
  whole-config digest that discovery approval pins, so every catalog-mediated
  investigation was refused (2026-09-26 onward). Checks that call the adapter
  directly did not notice. After any config change, confirm discovery approval
  still matches before running.
- The engine fingerprint hashed only `scripts/investigator/*.py`, so adapter- and
  transport-only changes left the tag unchanged, and a freeze could certify
  changed behaviour. Fixed: it now covers the package recursively and every
  transport. Every earlier tag is invalidated.
- A surface reported a failure only generically (Execute Queries:
  `DatasetExecuteQueriesError` / `0xC1450012`). A full day went into wrong
  hypotheses while the specific error (`AADSTS50173`) was available from XMLA.
  Fixed by `refine_failure()`: a generic failure is refined through another
  interface to the same surface before it is reported, and the status is never
  upgraded. Verified live on 2026-09-26, when XMLA supplied `AADSTS50173`
  behind the masked error. The refinement is sealed as its own `failure_detail`
  receipt, verified in tests only.
- Stubbed adapter methods were consumed as findings, making a false `DEFECT`
  reachable. Fixed by capability gating (#231).
- Same-engine aggregates were presented as cross-boundary comparisons. Fixed by
  the cross-surface invariant (#235).
- `CONSISTENT_TO_BOUNDARY` was claimable after zero successful comparisons.
  Fixed by requiring at least one, and by adding `NO_COMPARABLE_PATH`.
- An evaluator opened the wrong discovery context, invalidating a "structural
  limitation" conclusion. Fixed by a fail-closed environment requirement (#232).
- An ownership-label change caused a silent context regression (directory
  entries 28 to 11, SQL objects 11 to 3, SQL reads 3 to 0). Any change that adds
  content to planner context must report directory entry counts, SQL-object
  counts and payload characters before and after, with a coverage test.


## Dated correction: surface verification (2026-10-02, America/Chicago)

The historical claims above about verified cross-surface comparisons must not be
read as satisfying the full-coverage standard merged in #299 (`955b3fe`). The
[receipt audit](docs/retrospective-surface-attestation.md) found identity-only DAX self-reports and
identity/database-only SQL self-reports, with engine/connection (and the DAX
model object) unattested. Earlier MATCHED/CROSS_SURFACE_VERIFIED labels admitted
partial coverage; #299 now calls that PARTIAL and refuses verified boundary
eligibility. Snapshot alignment remains unestablished separately.

Run c2658c88 remains the first completed end-to-end **execution**, with two
observed values of 8,765 on independently declared routes; it did not establish
a fully attested verified boundary. Run 3d2c5bf0 observed 8,765, 8,765 and 7,661,
and invoked a judge that identified a compatible join mechanism; neither its
DAX/SQL boundary nor its SQL/SQL boundary satisfies #299. These observations
and the qualified mechanism remain useful, but do not prove actual duplicate
matches, current snapshots, intended semantics or verified transformation
attribution. Other historical comparisons using the same partial self-report
contract are subject to the same qualification. Original prose, outputs,
receipt bodies, counts and outcome labels are preserved, not retrospectively
regraded. Ledger corrections are annotations, not replacement runs.


## Dated finding: reader self-description (2026-10-02, America/Chicago)

The [least-privilege probe set](docs/surface-self-description-probes.md) supersedes the earlier
claim that the Microsoft reader routes cannot report engine/connection/object
metadata. SQL served its engine/version, session ID, network address and
protocol. Both REST/DAX INFO.PROPERTIES and XMLA DISCOVER_PROPERTIES served
OLAP Server, version 17.0.91.20, server name and catalog; REST/DAX returned
the model GUID, XMLA its name. ProductName/ProductVersion filters returned
empty, then property-name enumeration found the actual descriptor names.
XMLA session/connection DMVs were permission-refused; those failures do not
make all property metadata unavailable. Old receipts remain partial because
they never asked for these fields; retrospective corrections merged in #300
remain true. Current #299 FULL-coverage validation is unchanged.

Thirteen metadata query requests were recorded: 3 SQL, 4 REST/DAX, 6 XMLA;
ordinary rolling use 8 to 21 of 60. No retries, credits, cap/policy/config
changes, grants, fixture changes or investigation model calls. The report
proposes demonstrated difference on comparable query-bound self-reported
fields with explicit omissions; this is a proposal, not an implemented
standard or a requalification of any historical outcome. Intake and wiring
remain queued; draft #297 and Family D evidence remain unchanged.


## Dated ruling: graded quantity-bound surfaces (2026-10-02)

The user's ruling supersedes #299's FULL-coverage boundary gate. Coverage remains
recorded; comparable quantity-bound self-report differences now grade as
ENGINE_INDEPENDENT or OBJECT_DISTINCT. Connection-only difference is within-layer;
identity/version-only and incompatible report kinds cannot establish a boundary.
The engine recomputes grades from original quantity observations and renders the
stronger/weaker wording into both outputs. Missing fields stay explicit and
SNAPSHOT_UNVERIFIED is unchanged. The Microsoft adapter's combined quantity and
self-description queries are regression-tested, not yet live-verified.

See [implementation and historical counterfactual](docs/graded-surface-attestation.md). Probe PR #301
merged at 56a1545 with six green checks. Prior runs, corrections and ledger rows
remain unchanged; no investigation run or ledger row here. Engine bytes changed,
invalidating prior freezes. Intake evidence resolution and target/figure wiring
remain next; draft #297 remains open.


## Dated semantic surface ceiling (2026-10-03, America/Chicago)

Current quantity-bound semantic reads report engine, identity and model object. Connection is not self-reportable for this reader through the tested session route (DISCOVER_SESSIONS refused in #300). PARTIAL with those three matching fields is the tested ceiling, sufficient for qualified within-layer reproduction; it is not a gap to pursue with elevation. #302 engine-difference independence grading is unchanged. Connection omission and SNAPSHOT_UNVERIFIED remain explicit. See docs/synthesis-rendered-spine.md. Earlier narrower self-report statements above are historical.

Dated explicit administrator-profile attempt, 2026-10-03: the approved unchanged viewer grant was sent using `.local/azure-fabric-sql`, authenticated as admin@skynwhy.com. Before listing HTTP200, no dia-reader entries; grant HTTP403. Stopped immediately as directed, with no after listing, reader probes or B1 runs. No permissions changed. Part B 64/120; rolling observed 219/300. See [isolated-profile receipt](docs/round-two-admin-profile-grant.md). No engine/config change.

Dated monitoring-route correction, 2026-10-03: investigator-reader@skynwhy.com queried ItemJobEventLogs and SemanticModelLogs successfully (HTTP200) at its existing recorded workspace Viewer scope. Both requested histories were empty; ItemJobEventLogs schema has no rows-read/written fields. Monitoring is readable without new grants; no refresh timestamp or completed-refresh evidence was returned. REST/XMLA refusals remain historically correct for those routes. No more monitoring grants; dia-reader retained unchanged. See [exact probes](docs/round-two-investigator-reader-probes.md).

Dated post-enable accounting checkpoint, 2026-10-03: one additional isolated Copy Job completed; investigator-reader queried CopyJobActivityRunDetailsLogs HTTP200, RowsRead/RowsWritten columns but no matching rows 141.705s after served completion. Accounting unavailable at that observation, no zero-copy or ingestion-gap claim. Four authorized monitoring probes and one additional load consumed. No more grants. See [exact checkpoint](docs/round-two-investigator-reader-probes.md).


Dated pipeline accounting finding, 2026-10-03 America/Chicago: the existing
investigator-reader returned HTTP200 for Data Pipeline queryactivityruns. A
successful isolated InvokeCopyJob exposes its copy activity's own rowsRead and
rowsCopied under value[0].output (360/360 observed), with activity start/end and
null watermarkInfo. This supersedes earlier accounting-unavailable statements
only for this activity-output route; generic Copy Job run details still did not
carry counters, and three delayed KQL probes were empty after 23m39s. The new
isolated audit writer failed on the nested response shape; corrected parser is
not a successful live audit-source integration. No recount, elevated reader or
new grant. See docs/round-two-pipeline-audit.md. The rolling allowance is now 600,
Part B cumulative ceiling 300, diagnostic cap unchanged at 12 by human decision;
all counters and failures remain preserved.


Dated correction and audit verification, 2026-10-03 America/Chicago: earlier HTTP200 monitoring queries established access to the native monitoring database and empty requested histories, not independent proof of active logging. The human now confirms Workspace settings Monitoring ON. Current listing contains a native Monitoring artifact and the same KQL database 7e353019-064f-4aac-9a62-a9770d1399a9 used by every earlier investigator-reader probe; no handmade database/table creation found in implementation scripts. The workspace API omits the toggle; Eventstream definition HTTP401 and no connected browser prevent an independent toggle read. No setting or grant changed. Corrected pipeline 2a3801ae completed; investigator-reader served exactly one audit row with 360/360 own copy counters and matching activity times for that same run. Accounting is available from this audit surface for this run, but its null watermark establishes no source capture cut or snapshot alignment. The earlier failed audit query retained only a generic transport error, so sync lag or permission cannot be named as its cause. See [verification](docs/round-two-audit-verification.md). Part B 140/300, rolling observed 295/600.

Dated Part B result, 2026-10-04 UTC: the existing orderops_investigator reader
successfully served the declared application quantity in two live investigations;
the isolated model, Bronze and application boundaries were independently compared.
No new identity or permission was needed. Both gap/latency trials completed
NO_KNOWN_PATTERN: their audit SQL reads returned the earlier 360/360 successful
row and the preserved null-timestamp/null-counter row, with neither new pipeline
run present. The new runs' own activity output reported 361/361 and 360/360,
but their writer success alone does not establish which audit rows Delta held.
Do not assert SQL synchronization as the cause without that independent evidence,
and do not skip the malformed history to manufacture CURRENT. No load/gap claim
was earned. Source-consistency and configured-unreachable tickets held at intake.
Reader restoration checks returned 7,661 across the isolated application,
Bronze and model, and 8,765 in the original model. Snapshot caveats remain.
Human-approved Part B ceiling is 500; rolling stays 600, diagnostic cap 12.
See [complete preserved round](docs/round-two-source-scenarios.md).


Dated source-fixture platform finding, 2026-10-05 UTC: ordersops is GeneralPurpose Gen5 serverless/free, max2/min0.5, Paused. The authorised disable-idle-auto-pause request was admitted HTTP202 but completed Failed/ProvisioningDisabled: "Only default value for auto pause delay is allowed for Free Limit database with auto pause exhaustion behavior". After GET retains delay60 and free-limit AutoPause. No billing conversion; paid-overage mode cannot be reverted to AutoPause. Prior source OSError is class-only and occurred after completed SQL guards; do not call it a socket-connect error or auto-resume proof. See docs/round-five-offline-machinery.md.

Dated evaluator ruling, 2026-10-05: acceptance binds independently declared
fixture state, not recollection ID. A context may cover several data states;
never infer state from its ID. Historical state associations are separate and
retrospective, tied to sealed run/tape hashes; old receipts are unchanged.
Fixture arithmetic must never enter runtime prompts or quantity contracts.
See docs/round-five-fixture-states.md. No fresh freeze or live requalification.

Dated serverless handling, 2026-10-05 UTC: manifest-declared application source uses a 240-second worker deadline (old failure used90). Connect-stage40613 may wait at most60 seconds of backoff, all attempts admitted/receipted. Pre-warm connections and resume waits are ledger controls, never investigation diagnostic reads. OSError reason/errno/location and actual timer expiry now retained; the historical missing reason remains unknown. No quota, policy, identity or billing change. See docs/serverless-source-controls.md. Prior freezes invalid.

Dated native-worker contract finding, 2026-10-05 UTC: Round Five E D stopped before its value-existence lookup returned. The exact recorded config carries `_estate`; native load_config runs before its exception handler and rejects that key with ValueError: Unexpected or missing configuration fields. Offline reproduction establishes the contract mismatch, not historical stderr or an estate failure. No repair/replacement run. Pre-warm resumed positively via two control connections and five-second wait, no diagnostic reads. Current strict gate2/15, live list stopped, pot221/400. See docs/round-five-e-live-list.md.

Dated Round Five F finding, 2026-10-05 UTC: #395 projects worker configuration
from consumer-owned fields; runtime manifest metadata never enters worker schema.
#396 records v2 tapes with immutable committed engine revisions. Legacy v1
compatibility is explicit and hash-bound; historical producer replay is not
current-engine acceptance and cannot manufacture missing identity/budget events.
Historical replay restored10/15; new D/G/H passed, selected evidence13/15.
EMPTY refused before intake for absent approved report-14sep state; source
consistency was not run under first-unmet stop rule. Pot240/400, rolling last
observed439/1500; prior freezes invalid. See docs/round-five-f-versioned-runs.md.

Dated Round Five G continuation, 2026-10-05 UTC: explicit human approval registered
unchanged context 3ae7607b-5a5e-46c6-8e1b-195dbabc9cae, SHA-256
d6f3841fc02368a066f2de2d2e8bb4c22579b02d3bce3a95e441996091d5784f,
for report-14sep, no recollection. EMPTY reproduced BLANK and synthesized/replayed.
Source pre-warm connected on second attempt; source-consistency intake then
refused a non-verbatim column quote before any application read. No replacement
or repair. Pot 247/400, rolling last observed 440/1500, diagnostic cap 12.
See docs/round-five-g-final-two.md. Prior freezes remain invalid.

Dated fresh-sweep finding, 2026-10-05 UTC: thirteen of fifteen selected proofs
pass. Numeric reproduction now blocks TAPE_EVENT_DIFFERS:BUDGET:PROVIDER_RESPONSE
after an earlier pass, with identical source bytes/tape hash and the same
compatibility revision. Cause unestablished, both attempts preserved; no repair
or replacement. Historical source consistency still replays only to the boundary.
#376 remains draft; local13/15 is distinct from hosted missing-private-inputs CI.

Dated Round Five H finding, 2026-10-05 UTC: #399 adds one metered exact-span
correction; #400 compares budget decisions/counts structurally and records the
#393 accounting version retrospectively. All fifteen preserved tapes graded
13/15 with zero reads. Correction to the earlier numeric cause-unestablished
entry: first mismatch is provider input map key order, not budget arithmetic;
provider bytes remain exact and that proof remains blocked. One new source run
a96e0ca5 completed CONSISTENT_TO_SOURCE, with 7,661 and expected record 900099
absent at semantic, landing and application; synthesis and replay passed. Intake
accepted first response, so live retry not exercised. Selected14/15; #376 draft.
PARTIAL connection and SNAPSHOT_UNVERIFIED limit the claim. Pot263/400, rolling
last observed396/1500, diagnostic12 unchanged. No grants, fixture changes, refunds
or counter resets. See docs/round-five-h-exact-span-budget.md. Prior freezes invalid.

Dated Round Five I result, 2026-10-05 UTC: all fifteen selected sealed tapes
passed one zero-read offline sweep after canonical provider JSON comparison.
Original bytes, earlier grades and failures unchanged; numeric16 passed without
its conditional live re-record. Producer revisions remain pinned; this is not
current-engine/frozen unfamiliar-domain acceptance. #376's hosted gate has no
private inputs and is not merged; local15/15 does not replace the seventh check.
Pot263/400, rolling396/1500 last observed, diagnostic12 unchanged. Encrypted
private CI delivery awaits a human decision; no evidence uploaded. See
[final column and delivery gate](docs/round-five-i-canonical-gate.md).

Dated section8 delivery decision, 2026-10-05 UTC: the human conditionally approved
an immutable encrypted replay release and an Actions-only key. Content audit
found tenant IDs in all sealed bootstraps and connection strings in all pinned
inventory databases. The required absence condition is not satisfied. No key,
secret, release or uploaded artifact was created; estate identities/scopes
unchanged. Original evidence untouched. #376 stays unmerged despite local15/15.
Planned tag/secret and candidate hash are recorded in docs/round-five-i-canonical-gate.md.

Dated section8 amendment, 2026-10-05 America/Chicago: the human permits tenant
IDs and definition connection strings in immutable encrypted evidence; credentials
remain forbidden. All requested credential-pattern counts are0. Fifteen sealed
source/tape sets and30 bootstrap databases plus separate path mapping were
encrypted and published as `known-domain-tapes-1b6d344c8072d8a9e47e4957efeac7ffd6f9e4ed4f3afa500562e41562224174`; ciphertext SHA256
`fb7ac3ef8812c43230641bf90ce77c0f40b79ba9e127b15a8b9f9da883d530f4`. Key only in `KNOWN_DOMAIN_REPLAY_KEY` Actions
secret. No estate credential or reader scope changed. Earlier condition/findings
remain historical. Hosted check/merge pending; no fake CI pass. RoundSix0/400,
reserve60, rolling386/1500. See docs/round-six-transformation-reader.md.
