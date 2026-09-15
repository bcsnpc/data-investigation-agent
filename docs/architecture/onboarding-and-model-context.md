# Model onboarding and reusable context

Live prerequisite status: the [native proof preflight](../native-proof-preflight-milestone.md) completed on 2026-09-15. D/H live acceptance remains **blocked** on enforceable publication control, shared-generation/fixture evidence and effective identity/context. Definition/role/refresh observations do not satisfy those gates.

Implemented: [aggregate-to-record reconciliation](../record-aggregate-reconciliation-milestone.md) connects supported direct counts/sums to sealed captures and reviewed record projections. This is arithmetic consistency; shared-generation and effective-context proof remain open.

Implemented: [reviewed record discovery](../reviewed-record-discovery-milestone.md) reuses model-level record projections across tickets with complete scope, typed catalog validation, revocation and paired adaptive evidence. Review remains intent, not causal or semantic proof.

Proposed implementation of sections 3–12 and 30 of the [product plan](../../METADATA_DRIVEN_INVESTIGATOR_FIRST_CLASS_PRODUCT_PLAN.md). Onboarding is an admin workflow, not a metadata script users must rerun for every ticket.

**Implemented mapping reuse:** [Reviewed source discovery and typed scopes](../reviewed-source-scopes-milestone.md) derives source tests from confirmed model mappings and complete ticket filters. Missing/ambiguous/stale reviews remain gaps; mapping intent is not equivalent-calculation proof.

## Lifecycle

`REGISTERED → CONNECTED → SCANNING → DISCOVERED → SEMANTICALLY_ANALYZED → BUSINESS_CONTEXT_REVIEW → CAPABILITY_EVALUATED → INVESTIGATION_READY → ENABLED`

Persist stage separately from coverage conditions (`PARTIAL`, `NEEDS_CONTEXT`, `UNSUPPORTED`, `STALE_SCAN`) and enablement. An admin can enable a partially supported model for explicitly declared capabilities without labeling every metric fully ready. Disablement removes its reports from new ticket selection and prevents new dispatch; preserve saved evidence and reconcile any already-running remote read.

Transitions record actor, time, old/new revision, scan/context references and reasons. Only authorized admins confirm definitions, configure connections/policies and enable models. Control-plane metadata writes do not grant source writes. Read-only source identities remain mandatory.

Connection failures retain the last good context and expose unavailability. Partial scans do not erase assets or infer deletions. A disconnected model cannot be advertised as currently executable.

## Entities and persistence

Normalize control-plane entities and reference existing raw inventory/lineage artifacts by immutable IDs/hashes.

| Entity | Key fields and constraints |
| --- | --- |
| Organization / Environment | IDs, display name, policy scope; every model, connection and run belongs to one environment |
| Connection | Connector, approved endpoint reference, identity reference, asset allowlist, permission check/status/time; no secrets in records |
| SemanticModel | Native/workspace IDs, connections, registration stage, enabled policy, active context version, owner |
| Report / Page / Visual | Native IDs, exact model binding and context version; no cross-model name guessing |
| Metric / MetricDependency | Stable identity, definition hash/version, model/table refs, operation classes, evidence-backed dependencies |
| BusinessDefinition | Structured definition, grain, date basis, source, tolerance/unit, SLA, exclusions, calendar, authority, effective period and reviewer |
| Owner / Policy | Authoritative team/destination mappings, scope/version/effective dates, query/delivery/retention policies |
| MetadataScan | Type, times, coverage/permissions, connector outcomes, changed/deleted/unknown assets and inventory ref |
| ModelContextVersion | Immutable manifest: scan, semantic graph, lineage snapshot, business revisions, capability evaluation, hashes, parent version and publication status |
| Capability / Readiness | Operation support by asset/scope, reasons, prerequisites/evidence, context version and expiry policy |
| ContextChange | Before/after refs, change type, affected closure, review requirement and new context version |

Runtime Ticket, Investigation, InvestigationState, Hypothesis, Observation, ToolReceipt, Evidence, Outcome, Impact, RoutingDraft and DeliveryReceipt reference a specific context version. Never read an old run against the current model context implicitly.

## Deep scan

Reuse inventory/connectors, native report bundles, lineage and scan comparison; add projections and per-feature coverage.

| Surface | Capture and limitations |
| --- | --- |
| Model | Tables/columns/types, DAX/dependencies, active/inactive relationships/direction, hierarchies, supported calculation metadata, source bindings and execution/storage mode |
| Reports | Pages/visuals/bindings, filters at all levels, slicers, drillthrough and available interactions; runtime selections/bookmarks/RLS remain unknown unless actually captured |
| Fabric | Lakehouses/warehouses/tables, SQL/notebooks/pipelines, native/source-target lineage, refresh/run/deployment evidence where exposed |
| SQL/application | Schemas/tables/views/definitions, keys/identifiers, timestamp/watermark columns and audit/event structures; existence does not prove business meaning |

Complete collection does not imply universal understanding. Unsupported formats, API coverage and denied permissions are explicit observations. Implementation must verify connector capabilities before advertising them; do not assume every platform exposes every listed field.

## Semantic graph and business authority

Graph nodes represent measures, columns and relationship contexts; edges represent measure/filter dependencies and report usage. Retain source evidence. Detect cycles and ambiguity. A reference edge does not itself prove equivalent upstream arithmetic.

Optional LLM enrichment proposes descriptions, synonyms, likely grain/categories and useful dimensions. Every field carries one of:

- `DISCOVERED`: source and scan.
- `DERIVED_DETERMINISTICALLY`: derivation/version and inputs.
- `LLM_INFERRED`: model/prompt version, input refs and unconfirmed status.
- `TEAM_CONFIRMED`: authorized reviewer, effective scope/time and superseded version.

Inferred synonyms can help search. Inferred grain, tolerance, SLA, exclusion or owner cannot authorize comparisons, verdicts or delivery. Contradictory source/team definitions create review items. Team confirmation establishes intended authority, not proof that deployed code obeys it.

Store business definitions, synonyms, authoritative source, grain, date roles, dimensions, SLA, tolerance, owners, exceptions/exclusions and fiscal/calendar rules once for reuse across tickets. Keep structured policy fields distinct from prose, preserve effective dates and unknowns, and never reinterpret historical runs under a new rule.

## Capability/readiness

Support states: `SUPPORTED`, `PARTIAL`, `UNSUPPORTED`, `UNKNOWN`, `TEMPORARILY_UNAVAILABLE`. Per-request eligibility separately checks scope, current permissions, versions, budget and evidence. Cached support cannot override expired authentication or disablement.

Evaluate these named capabilities:

`MODEL_QUERYABLE`, `REPORT_CONTEXT_AVAILABLE`, `VISUAL_CONTEXT_REPLAYABLE`, `MEASURE_DEFINITION_AVAILABLE`, `MEASURE_DEPENDENCIES_RESOLVED`, `LINEAGE_TRACEABLE`, `UPSTREAM_QUERYABLE`, `FRESHNESS_COMPARABLE`, `ROW_KEY_COMPARABLE`, `AGGREGATE_RECONCILABLE`, `RATIO_DECOMPOSABLE`, `TIME_CONTEXT_SUPPORTED`, `RELATIONSHIP_CONTEXT_SUPPORTED`, `SOURCE_PROVENANCE_VERIFIED`, `IMPACT_TRAVERSAL_AVAILABLE`.

Display state, evidence, missing prerequisite, scope and evaluation time per metric/report/model. Rollups must not assign every metric the strongest member's capabilities. Recheck capture-specific provenance during investigations; onboarding cannot certify future reads.

## Basic admin API/UI

Proposed `/api/v2/admin` endpoints:

- `POST /models`, `GET /models/{id}`: register/inspect authorized identities and connections.
- `POST /models/{id}/scans`, `GET /scans/{id}`: bounded asynchronous scan with idempotency/status.
- `GET /models/{id}/contexts/{version}`: immutable manifest/coverage.
- `PUT /models/{id}/business-context`: expected revision plus fields; creates a draft revision.
- `POST /models/{id}/business-context/{revision}/confirm`: authorized versioned confirmation.
- `GET /models/{id}/readiness`, `GET /models/{id}/changes`: coverage and changes.
- `POST /models/{id}/enable` or `/disable`: expected context/revision and enabled capability policy.

B delivers basic lists/forms/status for Models, Connections, Onboarding, Business Context, Readiness, Scan History, Changes, Ownership and Policies; C–E enrich them. Separate admin/ticket-user authority even in the local pilot. Reject cross-environment references. Source credentials never appear in responses.

## Continuous change detection

1. Scheduled/triggered bounded scans compare definitions/hashes and coverage to the published version.
2. Compute changed closure across dependencies, relationships, filters, report usage, lineage and policies.
3. Rescan affected assets, or perform a bounded full scan if closure is uncertain. Deletion requires a complete authorized listing, not a permissions failure.
4. Recompute affected dependencies/readiness; newly added measures appear without code edits.
5. Atomically publish a consistent new context. Carry unchanged confirmations by explicit reference; material definition/authority changes invalidate affected confirmations. Request review for meaningful changes, not timestamps alone.
6. Pin active investigations to old context; relevant changes hold new dispatch for re-resolution/review. Unrelated changes need not invalidate an unaffected run.

Scan jobs have budgets/receipts, deduplication and connector backoff. Retain the last good version. Detection latency follows configured scan policy; do not promise real-time detection.

## Acceptance

Register models with overlapping metric names, enable one and verify ticket visibility. Confirm context once and reuse across tickets. Add a measure and observe automatic discovery/readiness without runtime edits. Change relationships/definitions and verify affected capability invalidation and run holds. Failed scans must not delete assets. LLM-inferred ownership or tolerance must not alter verdicts or authorize delivery.
