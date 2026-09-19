# Architectural review: self-discovering enterprise investigation

Date: 2026-09-18. Tracking: [#193](https://github.com/bcsnpc/data-investigation-agent/issues/193).
Authority: [the user mission](../../SELF_DISCOVERING_ENTERPRISE_INVESTIGATOR_PLAN.md).
This is the implementation proposal, not evidence that the target already works.

Sections A–B and the Stage 1 validation below preserve the initial audit. They are
not the current implementation status. Discovery and dynamic-query milestones
have since merged; follow [current delivery status](../current-delivery-status.md)
for delivered capabilities, live challenge results and remaining work.

## A. Current-state assessment

Inspected `origin/main` at `3c62be9` and the clean `feature/joint-native-capture`
branch at `3ab39a6`. The only open PR was #192. Its reusable aggregate/record
diagnostic is compatible with this pivot; all six CI checks passed. It was merged
as `d0c7bee`. No other PR stack remains to reconcile. Cloud availability was not
retested for this architecture audit.

| Decision | Existing code and treatment |
| --- | --- |
| KEEP | Azure SQL application and connected data generator; Fabric transformations; actual Power BI model/reports; metadata transports/inventory; lineage evidence; dedicated read-only identity; typed scopes; native/source reads; saved receipts; runtime fencing, replay, budgets and cancellation; question/screenshot intake; shared workspace; reviewed external actions; bounded-v1 regression path. |
| SIMPLIFY | Separate permission to investigate from permission to assert a cause. Replace whole-model business review as a technical-read prerequisite with per-capability eligibility. Keep detailed proof artifacts available without making exclusive publication or shared-generation certification a prerequisite for every useful observation. Consolidate status in one document. |
| REFACTOR | Model-owned scan queue into environment-owned discovery; report-owned model metadata into independent model context; manually enabled catalog into policy-selected discovered assets; precomputed candidate-only planner into context retrieval plus validated proposed tests; fixed single-workspace/single-schema execution profiles into connection policies. |
| REMOVE FROM PRIMARY PATH | Manual model/report ID entry, per-model enablement after ordinary schema changes, mandatory prose business review, candidate-only prohibition on all generated SQL/DAX, proof-preflight-first delivery sequence. Preserve these as fallback/legacy controls where useful. |
| NEW REQUIRED CAPABILITY | Environment connection policy; periodic discovery with per-surface coverage and diffs; enterprise graph/context projection; automatic ticket visibility; broader LLM interpretation and query proposals; parser-enforced read-only diagnostics; practical evidence-qualified outcomes; frozen unknown-domain live acceptance. |

The current investigator is more capable than bounded-v1, but still constrained:
the LLM chooses from precompiled native/source/record candidates. It cannot invent
a new diagnostic query or retrieve unfamiliar transformation context during a run.
`adaptive_runtime.outcome()` always leaves cause/delivery false and normally emits
INSUFFICIENT_EVIDENCE or UNRESOLVED. This is an implementation limit, not a general
causal agent. The local v2 UI works; it is not deployed as a hosted enterprise app.

Audit covered the controlling/handoff/status documents, onboarding and scan docs,
recent dependency/reader/workspace/intake/joint-capture milestone records, metadata
inventory/connectors/protocol/auth, lineage, model store/scan queue/semantic graph,
native/source/record/freshness tools, adaptive candidates/planner/runtime, question
and screenshot intake, and existing metadata/onboarding/adaptive/joint tests.
Older milestone test counts describe their own release, not today's total.

## B. Exact manual-onboarding dependencies

| Location | Current assumption | Minimum change |
| --- | --- | --- |
| `metadata_config.load_config` | One `fabric.workspace_id`, one SQL database and `visibility_schema` | Add environment policy referencing approved connection profiles; allow multiple roots without replacing legacy config. |
| `metadata_inventory.collect_fabric` | Enumerates all items in that workspace; expands TMSL/PBIR and lakehouse tables | Reuse enumeration; record coverage for listing, each definition, table listing and column schema separately. Add workspace discovery and warehouse SQL catalog adapter. |
| `metadata_inventory.collect_sql` / `Get-SqlMetadata.ps1` | Sys catalogs already enumerate visible objects, not a table-name list; schema parameter checks visibility but does not filter every query | Enforce approved schemas in normalization and execution; distinguish visible subset from complete authoritative listing. |
| `ModelStore.register` | Explicit workspace/model UUID and 1-50 report UUIDs | Discovered model upsert independent of reports; manual registration remains override mode. |
| `ModelStore.import_scan` | Bundles only registered reports; requires every bundle complete; obtains model assets from `reports[0]` | Independently normalize model, report and report-model edges; missing report definition must not hide queryable model. |
| `ModelStore.review/enable/get` | Current business confirmation gates enablement; changed scan disables entire model | Optional enrichment; explicit policy deny overrides automatic technical eligibility. Never synthesize TEAM_CONFIRMED. |
| `ScanQueue.request/run_one` / `run_catalog_scan.py` | Queue references existing model/revision; imports only that model although collector enumerates workspace | Environment scan job, scoped connector receipts, then project every supported discovered asset. |
| `question_intake.snapshot` / `workspace.model` | Only enabled models; full catalog capped at 12 models/200 measures/300 columns; assets accessed through first report | Search/retrieve bounded context from allowed discovered graph; preserve ambiguity across models; independent model-assets accessor. |
| `native_diagnostics.build`, record/capability/semantic consumers | Enabled model plus `context.reports[0].model_assets`; explicit filter required | Common context accessor and policy eligibility; allow explicitly budgeted global diagnostics without fake filters. |
| `native_identity.profile`, `adaptive_candidates.catalog`, native worker | Explicit model-ID allowlist and one workspace | Add versioned workspace policy mode; intersect discovered membership with reader permission. Do not populate a publisher fallback. |
| `source_diagnostics.snapshot/build` | Selected model scan, one configured schema, USER_TABLE only, fixed count/sum/watermark operators | Connection/asset context independent of model; validated views and broader relational diagnostics under policy. |
| `source_bindings`, `record_bindings` | Reviewed mappings gate derived source tests | Permit discovered lineage to guide exploratory reads; keep semantic-equivalence claims separate and label inferred mappings. |
| `adaptive_candidates.available`, planner instructions/schema | Parent scalar before child/breakdown; planner can only select candidate IDs | Remove universal ordering; allow metadata retrieval, freshness or source first when useful and permitted. Retain tools as preferred builders. |
| `proof_requirements`, `proof_preflight`, old Phase H | Formal remote exclusivity/generation before acceptance | Retain optional certification workflow; replace primary success gate with unfamiliar-environment behavior and claim-specific evidence. |

Consequently: a new model/report is collected but not made a ticket target; a new
semantic table enters only a later import of its already registered model; a new
lakehouse table is listed but not automatically linked into an investigation;
a new visible SQL table enters inventory but source reads remain limited by the
selected model context/schema/operator/mapping. Warehouse tables have no dedicated
collector in this path. New workspace/database connection approval is legitimate
operator configuration; repeated model/report/table registration is not.

## C. Discovery architecture

Connect an environment once using secret-free connection references, tenant,
approved workspaces/databases/schemas, read-only identity references, scan cadence,
query limits and explicit exclusions. Start with approved workspaces; tenant-wide
visibility is optional and requires appropriate admin API permissions. Enumerated
visibility never enlarges operator-approved scope.

Reuse `Inventory`, `MetadataHttp`, `WorkerTransport`, `metadata_protocol.pages`,
definition expansion, SQL catalog readers and lineage parsers. An environment scan
enumerates workspace items, independently fetches supported definitions/history,
lists lakehouse tables and inspects approved warehouse/SQL endpoint catalogs.
Power BI report listing supplies explicit dataset bindings when available. Never
join report/model/table identities by similar names.

Store coverage for each connection/workspace/listing/definition/schema, not just a
global COMPLETE flag. Permission failure, incomplete pagination, timeout, unsupported
format and unavailable schema retain distinct gaps. Failed deep metadata does not
erase a successfully enumerated asset. Persist bounded redacted error categories.
Cap pages, definitions, bytes, elapsed time and calls; honor throttling within the
remaining budget. No unbounded retry or newly discovered endpoint trust.

Scan once on connection, on operator request, and through a finite scheduled
dispatcher. Deduplicate active jobs; publish one completed context revision with
its coverage. Schedule latency and last successful scan are visible. Do not claim
continuous discovery until the scheduled repeat/change experiment passes.

Platform facts checked against Microsoft documentation on 2026-09-18:

- [List workspaces](https://learn.microsoft.com/en-us/rest/api/fabric/core/workspaces/list-workspaces)
  returns workspaces accessible to the principal, with pagination; it is not an
  inventory of everything in a tenant.
- [List items](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/list-items)
  is the workspace enumeration surface. Retain coverage and permission limits.
- [Get reports in group](https://learn.microsoft.com/en-us/rest/api/power-bi/reports/get-reports-in-group)
  exposes report identities and dataset bindings where available.
- [Semantic-model definition](https://learn.microsoft.com/en-us/rest/api/fabric/semanticmodel/items/get-semantic-model-definition)
  and [report definition](https://learn.microsoft.com/en-us/rest/api/fabric/report/items/get-report-definition)
  require read **and write** permission on the corresponding item, unlike workspace
  item listing, which requires Viewer. Both definition APIs document a restriction
  for encrypted sensitivity labels. The semantic API defaults to TMDL; the current
  collector explicitly requests TMSL and cannot expand arbitrary TMDL. Probe the
  metadata identity separately from the query reader; denied definitions produce
  partial context, not an automatic permission escalation. Existing elevated
  metadata collection can remain explicitly isolated with a metadata-only transport;
  it must never become the investigation execution identity.

First fallback is automatic listing with explicit metadata gaps; then an approved
scanner/XMLA or retained-definition import when supported and authorized. Manual
asset registration is the final restricted-environment fallback and must be labelled.
Static report definitions do not capture a user's current bookmarks, selections or RLS.

## D. Enterprise Context Graph

Use additive SQLite tables first; no graph database migration:

| Entity | Versioned fields |
| --- | --- |
| EnvironmentConnection | Environment, connector/profile reference, scope policy/hash, identity reference, cadence, deny/allow mode |
| DiscoveryScan / Coverage | Scan/parent IDs, connection/surface, start/end, status, page/completeness evidence, calls and gaps |
| Asset / AssetVersion | Environment + provider + native scoped identity, kind, name, parent, normalized definition/hash, raw inventory ref, scan, availability |
| ContextEdge | Source/target, relation, origin, definition/receipt references, derivation version, authority, scan and confidence category |
| ContextChange | ADDED/CHANGED/REMOVED/UNKNOWN_DUE_TO_PARTIAL_SCAN, before/after version, reason and affected closure |
| ContextVersion | Immutable manifest of asset/edge/coverage versions, policy, enrichment references and capabilities |
| ContextEnrichment | Asset/field/value, provenance, source references, reviewer or LLM/prompt version, effective dates, supersession |

Relations include CONTAINS, USES, DEPENDS_ON, REFERENCES, SOURCED_FROM,
DERIVED_FROM, INGESTED_FROM, READS, WRITES, EXECUTES and OWNED_BY. Existing lineage
edges retain their evidence and direction via an adapter. IMPACTED_BY is an
assessment with evidence, not a bare assertion from graph reachability.

Provenance: DISCOVERED, DETERMINISTICALLY_DERIVED, LLM_INFERRED, TEAM_CONFIRMED.
Preserve original labels on historical records; map them only in new projections.
Native stable IDs distinguish rename from deletion. Where only name-derived IDs
exist, record removal/addition and possible rename uncertainty; never guess identity.
Exclude collection timestamps/run-history churn from semantic definition hashes.

Missing assets become REMOVED only when the corresponding authorized listing is
complete and visibility coverage supports absence. Otherwise retain the last known
version with UNKNOWN_DUE_TO_PARTIAL_SCAN. Removal means no longer in the proven
catalog scope, not proof of a remote delete operation. Definition denial does not
remove children. Change invalidation follows old and new dependency closures;
uncertain closure triggers conservative rescanning, not silent stale context use.

## E. LLM responsibilities

Resolve unfamiliar questions against retrieved discovered context; select report,
page, visual, metric, business entity and time/filter intent. Clarify only material
ambiguity. Interpret DAX, SQL, notebook/pipeline text and descriptions; propose
meaning/mappings as LLM_INFERRED, never authoritative business rules.

Allow dynamic metadata retrieval, hypothesis creation/revision, dimension/time
selection and proposed SQL/DAX diagnostics. The next action depends on actual
observations, failed tests, available capabilities and remaining budget. No fixed
Power BI-to-source order. Power BI evaluates DAX; local syntax/reference analysis
does not become a second calculation engine. Unsupported inherited context stays
explicit rather than treating a standalone child read as equivalent.

Persist Hypothesis -> Test -> Observation -> Interpretation -> Next action, with
receipt references. Do not store private chain-of-thought. Enrichment is cached by
definition/prompt version and budgeted; not every scan needs another LLM call.

## F. Deterministic responsibilities and flexible tools

Reuse the existing registry/runtime/receipts. Consolidate discovery/context lookup,
native evaluation, bounded relational diagnostics, lineage/transform inspection
and evidence comparison; avoid a separate wrapper for every business question.

Generated SQL must parse as one read-only SELECT/CTE query in the target dialect.
Reject DDL/DML, SELECT INTO, EXEC, multiple statements, external access, unknown
functions and unauthorized objects. Resolve aliases/CTEs/joins to approved catalog
assets; cap joins, rows, bytes, time and calls. Validate view dependencies and permissions.
Use parameterized values and read-only credentials; TOP is not a scan-cost limit.
Prefer builders, but do not require a new Python template for each diagnostic.

Generated DAX is a bounded read-only query against an approved discovered model,
with parsed query structure, permitted references, result/time limits and no write
commands. Native execution is authoritative. Unknown grammar fails closed with a
specific unsupported reason; a keyword regex alone is not sufficient validation.

All dispatch rechecks policy/identity/context/budget. Untrusted ticket, metadata,
SQL comments and notebook text never authorize tools or endpoints. Deterministic
results supply numbers, completeness and provenance. LLM interpretations cite
them; external actions require a separately reviewed immutable draft.

## G. Simplify evidence requirements without inventing certainty

Use evidence strengths OBSERVED, STRONGLY_SUPPORTED, VERIFIED and
INSUFFICIENT_EVIDENCE on individual claims. Practical outcomes are EXPECTED_BEHAVIOR,
LIKELY_TECHNICAL_DEFECT, VERIFIED_TECHNICAL_DEFECT, SOURCE_OR_APPLICATION_ISSUE,
REFRESH_OR_FRESHNESS_ISSUE, BUSINESS_CONTEXT_REQUIRED, INSUFFICIENT_EVIDENCE,
UNSUPPORTED and UNRESOLVED. Version new outcomes; never relabel old runs as verified.

An observed native value needs a real query receipt, not exclusive publication.
A likely join-duplication diagnosis needs relevant duplicate/key/join observations
and explicit alternatives/limits. A verified defect needs the relevant mechanism
and intended contract demonstrated. Missing shared-generation proof limits claims
that require it, not unrelated metadata reads or useful scoped observations.
Unknown business code X17 remains unknown until documentation/team authority exists.

Retain formal preflight, generation certification and replay verifiers as optional
advanced tools. Stop building milestones around proving every remote property.
Do not weaken read-only access, identity/scope isolation, truncation handling,
replay protection, cancellation or human review of external mutation.

### Targeted structural discovery extension

Within the same runtime, derive tentative domain profiles from discovered metadata,
advertise adapter capabilities and allow bounded structural hypotheses/tests during
relevant tickets. Declared cardinality is not measured uniqueness; observed grain
is not business intent. This is supporting work for the frozen challenge, not a
new platform phase. See [implementation and evidence](../structural-discovery.md).

## H. Frozen Unknown Domain Challenge

Freeze engine code, prompts, validators, tool registry and policy semantics in a
tagged manifest before publishing the new domain. Publisher/evaluator artifacts
are separate from runtime context. No expected values, defect labels, scenario IDs
or executable mapping rules may enter investigator configuration. Changing engine
behavior invalidates that attempt and requires a new freeze and fresh variant.

Use an isolated Inventory/Warehouse Operations domain: related inventory movements,
warehouses/products, purchase orders and adjustments in approved Azure SQL schemas;
Bronze/Silver/Gold entities; a new semantic model with additive, ratio and nested
derived measures; two native Power BI reports. Counts are selected for useful
join/date/late-event behavior within the existing free SQL budget, not volume alone.
The publisher knows ground truth; the reader discovers only ordinary metadata/data.

First scan with no domain, then publish it and rescan without any model/report/table
ID registration. Separately add a SQL table, Fabric table, semantic table, new model
and report; change DAX/relationships, rename an asset and remove a report. Capture
diffs, graph edges/capabilities and ticket visibility. Repeat a permission-denied
and partial scan: they must not produce false removals.

| Ticket family | Required behavior/evidence |
| --- | --- |
| A Simple discrepancy | Resolve unfamiliar measure; reproduce native value; slice relevant dimensions; trace an observed difference or explain it. |
| B Ratio | Inspect numerator/denominator separately under relevant native context; never sum ratios. |
| C Derived measure | Recursively narrow a relevant child; unsupported context remains explicit. |
| D Visual/filter | Distinguish global metric from captured visual/page/filter context; state missing runtime selections/RLS. |
| E Freshness | Inspect runs/watermarks before assuming transform defects; distinguish observed age from authoritative SLA violation. |
| F Transformation | Inspect unfamiliar join/filter/dedupe/date/watermark logic; test the suspected mechanism with real data. |
| G Source/application | Follow downstream agreement upstream; compare authorized intent/audit/state without assuming the audit itself is independent intent. |
| H Expected behavior | Explain a legitimate observed change with supporting context; no invented technical defect. |
| I Missing business context | Identify the unknown rule/field meaning and ask the relevant question; no invented interpretation. |

Use multiple hidden variants and bounded repeated LLM trials for ratio, transform
and ambiguity cases. Report success/failure/partial/blocked separately, call counts,
evidence-path changes, revised hypotheses, freeze hash and unsupported operations.
At least one failed hypothesis must be revised based on observations. An all-gap
agent fails generality; one successful demo does not pass the matrix. Preserve
adversarial tests for ambiguous names, malicious text, timeout, empty/truncated
results, duplicate keys, changed relationships and denied permissions.

## I. Minimum coherent migration and rollback

1. Establish this architecture, accurate README and stages 1-9; reconcile #192.
2. Add environment discovery and versioned coverage/diffs beside raw Inventory.
3. Introduce independent model-assets context and automatically project supported
   discovered models/reports into the existing workspace catalog under connection
   policy. Manual mode retains its prior behavior; explicit deny wins. Adapt all
   `reports[0]` consumers together rather than faking a report for reportless models.
4. Reuse runtime with dynamic context/test proposals and parser-enforced queries.
   Extend practical outcome assessment and evidence-grounded explanations together.
5. Freeze and run the live unknown-domain matrix; then consolidate UX and reviewed
   handoff. Hosting/auth remains explicit delivery work, not implied by discovery.

Use additive schemas and explicit engine/context versions. Old v1 and manual v2
runs remain readable. Rollback selects legacy mode for new runs; it does not rewrite
or resume an existing run under another engine. Preserve current review/revocation
records as enrichment/policy evidence. Never fabricate confirmations to bypass gates.

## J. Documentation and delivery discipline

`docs/current-delivery-status.md` is the sole current milestone/status source.
README summarizes the product, what works, architecture, next milestone, limits
and run/demo links. Review its entire contents after each stage. `docs/progress.md`
keeps chronological receipts; old A-J plans and milestone docs are historical.
Architecture files define target contracts and refer to status for implementation.
The root handoff links current status and preserves a clearly labelled historical
assessment. Do not leave old "next step" paragraphs competing with the new roadmap.

Deliver cohesive milestones: discovery plus catalog/context integration; dynamic
reasoning plus governed tools; freeze plus challenge; UX plus reviewed handoff.
Stage boundaries are acceptance checkpoints, not a requirement for nine small PRs.

## Stage 1 validation

The documentation pivot changes no runtime, source schema, permissions or deployment.
The required generator tests passed (2 tests). A local document-link audit resolved
322 targets before the final review links were added; `git diff --check` passed.
PR #192's six checks were verified before merging. Its recorded 860-test/30-browser
suite and live native observations are prior release evidence, not rerun results
for this documentation change. No SQL, DAX or LLM call was made for this audit.

Stage 1 is ready for review. Stages 2-9 remain implementation/acceptance work; this
proposal does not turn discovery, flexible queries or unknown-domain generality
into delivered capabilities. Next is the grouped discovery-to-ticket refactor.
