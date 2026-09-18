> Historical pre-pivot document. Superseded by [the discovery-first architecture](../README.md).

# Contracts, native semantic execution and tools

The [first-class product plan](../../../METADATA_DRIVEN_INVESTIGATOR_FIRST_CLASS_PRODUCT_PLAN.md) governs this revision. All definitions below are **proposed v2 contracts**. Implement them as validated, versioned data models with JSON Schema export; reject unknown fields at external boundaries. Use standard-library dataclasses plus explicit validators initially, or the repository's existing validation dependency if one is selected in A. The important decision is validation and versioning, not a new framework.

## Common representation rules

- IDs are opaque stable references, not display labels. Every persisted object has `schema_version`, an ID and canonical-content hash. Referenced objects must exist and be authorized for the run.
- UTC timestamps require offsets and canonical serialization. Date windows are explicit half-open intervals, with timezone and date-role metadata retained.
- Numeric values are decimal strings, never JSON floating-point approximations. BLANK is a tagged value, distinct from zero, null/missing evidence and an execution error. Units distinguish currency, count, fraction and percentage points.
- Filters are typed operators and catalog column references. Never concatenate a user's column, measure, filter or screenshot text into executable code.
- Asset identity and definition version are separate. Name changes in current name-based source IDs require explicit reconciliation; do not infer identity from a similar name.
- Hashes establish integrity, not truth or authority. Evidence also needs source identity, capture method, permissions, completeness and version provenance.
- Large records live in bounded access-controlled artifacts. API projections contain redacted samples and immutable artifact references, not credentials or unrestricted row dumps.

## Data contracts

| Contract | Required fields and meaning | Invariants |
| --- | --- | --- |
| `AssetReference` | `asset_id`, `kind`, `connector_id`, `tenant_id`, `workspace_or_database_id`, `native_id`, `display_name`, `scan_id`, `definition_hash`, `observed_at`; optional parent reference | All resolution uses configured estate boundaries and explicit bindings. Hash/scan mismatch requires re-resolution, not latest-name substitution. |
| `MetricDefinition` | `metric_id`, semantic-model and measure `AssetReference`s, `expression_text_ref`, `expression_hash`, `dependency_ids`, `expression_ir` or unsupported reason, `unit`, `aggregation_kind`, `grain`, `date_roles`, `filter_dependencies`, `relationship_refs`, `source_bindings`, `definition_authority` | Raw collected expression is untrusted input to parsing. A source binding includes its transformation/contract evidence; a table-name match is not semantic equivalence. `aggregation_kind` includes additive/count/distinct_count/ratio/nonadditive/unknown. |
| `ResolvedScope` | `ticket_id`, `revision`, report/page/visual refs when supplied, `metric_ids`, typed `filters`, `time_window`, `date_role`, `currency`, `comparison_reference`, `runtime_context`, `identity_context_hash`, `model_context_version`, `business_context_revision`, `metadata_scan_id`, `lineage_version`, `scope_hash`, `resolution_status`, `gaps`, `approval_ref` | Each dimension is explicit or `not_applicable` with a reason. Unknown never means unfiltered. Reference may be an approved definition, another period, or user expectation; label authority. Runtime filters/RLS must be known for a report-level conclusion. |
| `Capability` | `capability_id`, `version`, `operation`, `asset_refs`, supported IR operators/types/grains/filter shapes/relationship modes, `permission_requirements`, `evidence_requirements`, `cost_profile`, `support_state`, `eligibility` and reasons | Support: SUPPORTED/PARTIAL/UNSUPPORTED/UNKNOWN/TEMPORARILY_UNAVAILABLE. Eligibility: eligible/needs_context/unsupported/unavailable. Evaluate per run and recheck permission before execution. Queryable does not imply comparable or replayable. |
| `ToolRequest` | `request_id`, `run_id`, `state_revision`, `engine_version`, `tool_name`, `tool_version`, `capability_id`, `scope_hash`, `asset_refs`, typed `arguments`, `input_evidence_ids`, `hypothesis_id` if testing one, `purpose_code`, `budget_reservation`, `deadline`, `idempotency_key` | Policy derives admissible assets/arguments from approved scope. LLM cannot supply a host, token, filesystem path or enlarged budget. Diagnostic query intent becomes a validated bounded plan; no unrestricted query-text pass-through. |
| `ToolResult` | request ID, start/end, `status`, `observation_ids`, `evidence_ids`, `error_code`, `retryable`, actual resource usage, completeness, execution identity/version references | Status: succeeded/partial/unsupported/unavailable/failed/cancelled. Success with zero rows is different from unavailable. A timeout never becomes zero. |
| `Observation` | `observation_id`, request ID, asset/metric refs, `scope_hash`, `kind`, tagged `value`, `unit`, `grain`, `captured_at`, `snapshot_ref`, `identity_context_hash`, `completeness`, `evidence_ids` | Represents what was observed, not why. Query results, definitions, freshness and record membership are distinct kinds. |
| `Evidence` | `evidence_id`, `kind`, `producer`, `source_refs`, `captured_at`, `artifact_ref`, `content_hash`, `query_or_ir_hash`, `snapshot_proof_refs`, `scope_hash`, `completeness`, `limitations`, `redaction_policy`, `authority` | Immutable. Integrity revalidated on use; no overwriting stale evidence. Samples cannot prove full-set equality or affected count. |
| `Hypothesis` | `hypothesis_id`, concise `claim`, `claim_type`, affected boundary/assets, `predicted_observation`, `test_request_ids`, supporting/refuting evidence IDs, `status`, `reason_code`, `revision` | Status: open/supported/rejected/untestable. This is a testable external claim, not hidden reasoning. Supported is not automatically a verified cause. |
| `InvestigationState` | `run_id`, engine/schema versions, scope ref/hash, model_context_version, business_context refs, relevant asset/lineage refs, tested assets, attempted/completed/failed tests, unresolved questions, stopping reason, approval ref, state revision, workflow status, capability decisions, hypothesis refs, observation/evidence refs, outstanding request, step count, budget ledger, lease/fencing token, timestamps, gaps, outcome ref | Append events plus compare-and-swap state checkpoint atomically. Only one outstanding tool in the first implementation. Scope changes require a new approved revision. |
| `InvestigationOutcome` | run/revision/scope, `execution_status`, `classification`, `comparison_status`, `findings` with evidence refs, verified cause or null, first observed/verified boundary separately, `evidence_strength`, `impact`, `limitations`, `next_actions`, `routing_eligibility`, outcome hash | Terminal execution is not proof of resolution. Classification and delivery status are independent. Every numeric and causal claim must resolve to validated evidence. |

`ResolvedScope.filters` entries have `column_ref`, `operator` (`eq`, `in`, `gt`, `gte`, `lt`, `lte`, `is_blank` initially), typed values, origin (user/report/measure), and precedence/context semantics. A measure's internal CALCULATE filter is not merged casually with the external report filter: implement and test DAX replacement/intersection behavior for the admitted subset.

`runtime_context` records supplied report/page/visual filters, slicer selections, bookmarks, drillthrough and effective identity/RLS coverage. Each has known/absent_proven/unknown/unsupported status and evidence. Captured native definition and current runtime selection are different sources.

`evidence_strength` is a vector: identity, scope, semantics, lineage, completeness, provenance, reproducibility and causality. Each is verified/partial/missing/contradicted with evidence IDs. Do not collapse it into an invented percentage.

### Example fragments for the unseen ratio

```json
{
  "expression_ir": {
    "op": "divide",
    "numerator": {"op": "measure_ref", "id": "measure-refunded-orders"},
    "denominator": {"op": "measure_ref", "id": "measure-delivered-orders"},
    "zero_denominator": "blank"
  },
  "unit": "fraction",
  "aggregation_kind": "ratio"
}
```

```json
{
  "kind": "metric_value",
  "value": {"type": "decimal", "value": "0.25"},
  "components": {"numerator": "2", "denominator": "8"},
  "comparison_reference": "0.20",
  "difference": {"fraction": "0.05", "percentage_points": "5"}
}
```

These are illustrative fragments, not full valid records. Production objects must carry the asset, scope and provenance fields above. Display percentages by unit; never sum daily refund rates to obtain a weekly rate.

## Native semantic execution and semantic IR

**Power BI executes DAX. We do not build a second DAX engine.** A deployed measure can be evaluated even when its internals cannot be translated upstream. Separate queryability, dependency resolution, decomposition, context replay and reconciliation capabilities.

IR records SUM/COUNT/DISTINCT_COUNT/RATIO/DERIVED_ARITHMETIC/FILTERED_MEASURE/MEASURE_DEPENDENCY/DIMENSIONAL_SLICE operation classes, grain, references, filter modifiers and relationship context. TIME_SHIFT and RELATIONSHIP_SWITCH can be discovered with partial analysis; they do not imply upstream support. Cycles, ambiguous references and unsupported nodes carry explicit reasons. Complex combinations of supported operations are required now.

For a ratio or derived expression, evaluate the parent **and each relevant child in Power BI under the same captured context**. Preserve native BLANK and data types. Do not assume a child evaluated outside an enclosing CALCULATE/time/relationship modifier has the parent's context. Carry supported effective context to child requests, or return a decomposition gap while retaining the parent result. Querying an existing measure does not require locally implementing DISTINCTCOUNT, IF or DAX blank-row semantics.

The SQL/relational IR is only for supported upstream equivalents and bounded replay. It requires an authoritative source mapping, grain, keys, date basis, types, blank handling, relationship/filter semantics and provenance. Local arithmetic may explain a ratio's observed components; it does not replace its native semantic result. Compare equivalent operations with explicit tolerances/units from confirmed context, never by measure name.

Report reproduction combines supported report/page/visual filters, slicers, drillthrough, date/currency and effective identity. Missing bookmarks, interactions or RLS prevent claims of exact visual reproduction. A global or broadened diagnostic slice is a **derived scope** authorized by the review envelope; never overwrite ticket scope or broaden data access. Mark how it differs from the user's view.

## Tool registry and delivery order

Each tool uses the contracts above, records query/plan hashes and identity, limits results and charges every underlying call. Tools are generic; the planner chooses their sequence. Implement foundational wrappers in D, evaluate precise semantic support in E and exercise adaptive use in G/H. Names below are proposed API capabilities, not claims that these functions already exist.

| Family / tool | Input and result | Evidence, safety and failure | Existing reuse |
| --- | --- | --- | --- |
| `get_report_context`, `get_visual_context` | Report/page/visual refs, runtime selections; effective context and gaps | Same-version binding, filter origins and identity; unknown is not unfiltered | Native report bundles, native context, slicer/drillthrough validators |
| `get_measure_definition`, `get_measure_dependencies`, `get_model_relationships` | Catalog refs; definitions, dependency graph, relationships | Definition hashes, graph coverage/cycle checks; partial analysis explicit | Inventory model expansion and lineage references |
| `evaluate_measure` | Resolved measure and scope; native scalar, unit and BLANK | Approved model, bounded DAX, actual capture/provenance; no local semantic substitute | DAX worker, auth, response validation |
| `evaluate_measure_dependencies` | Parent and eligible child refs/effective contexts; native component values | Every child receipt and context retained; budget/cycle/depth limits; unsupported inherited context blocks decomposition | Native query adapter plus catalog graph |
| `evaluate_measure_by_dimension` | Metadata-derived dimension, measure(s), scope, bucket limit; grouped native values | Approved dimensional relationship and access; completeness/tail accounting; nonadditive values never summed blindly | Query adapter plus new generic grouped-query builder |
| `execute_bounded_dax` | Typed model-scoped query plan; tabular result | Allowlisted read-only query grammar, validated refs, result/time/cost limits; no arbitrary text execution | Existing fixed DAX path wrapped, new plan validator |
| `query_asset`, `execute_bounded_sql`, `query_source_record` | Resolved asset/columns/predicates/keys; rows or aggregates | SELECT-only compiler/validator, connection allowlist, parameters, deadlines; unsupported operations rejected | SQL/Fabric workers, restricted identities, resume retry |
| `compare_assets`, `compare_aggregates`, `compare_row_counts` | Eligible observations/contracts; match/mismatch/not-comparable and deltas | Scope/grain/unit/identity/version checks; unknown snapshots never invented | Investigation checks and boundary logic |
| `compare_keys`, `profile_difference` | Eligible bindings/keys or difference evidence; missing/extra/changed counts and bounded breakdown | Complete-set proof distinct from samples; retain duplicates; no unbounded extraction | Complete-key comparison and lab impact patterns |
| `compare_freshness`, `inspect_pipeline_run`, `get_high_watermark` | Asset/run/policy refs; freshness and run/watermark observations | Missing SLA or watermark semantics returns unknown; run success alone is not current data | Freshness checks, connector run history, publication receipts |
| `inspect_transform`, `verify_reconciliation` | Captured transform, authoritative contract and input/output refs; analysis or causal proof | Never execute captured code verbatim; bounded relational replay, hashes, completeness and authority required | Lineage parser, snapshot checks, lab replay invariants |
| `get_app_event`, `get_order_audit`, `compare_application_intent_to_persisted_state` | Authorized business key/event mappings; intent/commit/state evidence | Read-only, sensitive-field minimization; audit absence is not proof of a failed write; independent intent required | Source audit schema and connection adapters; new generic event mapping |
| `find_upstream_lineage`, `find_downstream_lineage`, `find_downstream_impact`, `get_asset_owner` | Resolved asset and bounded traversal; affected/potential assets and owners | Proven edges and ownership version; distinguish reachable from proven impacted | Lineage graph, gap policy, routing mappings |
| `record_observation`, `record_evidence` | Validated tool-produced payloads; immutable references | Orchestrator-owned persistence, not LLM-created factual evidence; integrity/completeness validation | Evidence store and new state transaction |

Application tools use registered entity/event mappings; the `get_order_audit` compatibility name must not introduce order-only logic into general planning. Pipeline/lineage/impact tools are included in D-H, not deferred beyond the first product milestone. Providers beyond existing SQL/Fabric/Power BI and GitHub/email remain later.

## Query policy

Prefer repository-owned builders over arbitrary strings. A bounded SQL plan supports approved projection, predicate, aggregate, grouping and joins with declared keys; DDL/DML, stored procedures, external functions and arbitrary execution are rejected. A bounded DAX plan references deployed measures and validated dimensions/filters. If a future tool accepts candidate query text, parse to the same admitted plan and reject any unrecognized construct before execution; it is not an escape hatch.

No local DAX interpreter is required to admit a native measure evaluation. Conversely, native execution success cannot make an upstream equivalent valid. Parser/renderer tests cover identifier escaping, filter scope, no-write guarantees and malformed results; live semantic tests use the real model.

## Impact

Compute monetary differences by currency, complete affected-key counts, ratio numerator/denominator differences and percentage-point effects from evidence. Dimensional contributions require compatible partitions; retain an explicit remainder when truncated and never extrapolate samples. Downstream graph reachability produces potentially affected assets; proven impact requires binding and scope evidence. Ownership is authoritative context, not an inferred name.

## Additional product contracts

Use [onboarding entities](../onboarding-and-model-context.md) for Organization, Environment, Connection, SemanticModel, Report/Page/Visual, Metric/MetricDependency, BusinessDefinition, Owner, Policy, MetadataScan, ModelContextVersion, ContextChange and Readiness. Add `ContextPack` with context-version/hash, relevant semantic/lineage subgraph, approved business fields, runtime scope and gaps. It is a projection, not a new source of truth.

`ToolReceipt` is the durable execution record containing ToolRequest/ToolResult references, actual adapter attempts, timing, usage, identity and artifact hashes. `Impact`, `RoutingDraft` and `DeliveryReceipt` reference the immutable outcome revision. Every enriched business field records DISCOVERED/DERIVED_DETERMINISTICALLY/LLM_INFERRED/TEAM_CONFIRMED provenance. Saved outcomes cannot silently adopt a newly published context.
