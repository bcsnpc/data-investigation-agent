# Enterprise connection, discovery and reusable context

This is the discovery-first target. See [status](../current-delivery-status.md)
for implementation and [review sections B-D](enterprise-discovery-pivot.md) for
exact code changes and graph schema.

```text
ENTERPRISE_CONNECTED -> DISCOVERY_SCAN -> ASSETS_DISCOVERED -> CONTEXT_GRAPH_BUILT
-> SEMANTIC_ENRICHMENT -> CAPABILITIES_EVALUATED -> AVAILABLE_FOR_INVESTIGATION
-> CONTINUOUS_CHANGE_DETECTION
```

Approve connection roots, read-only identities, policy and cadence once. New
models/reports/tables inside those roots are enumerated and projected automatically.
Explicit deny overrides admission. Missing business definitions do not block basic
technical reads. Existing manual registration/review/enable APIs remain fallback.

Persist per-surface coverage, immutable versions and ADDED, CHANGED, REMOVED,
UNKNOWN_DUE_TO_PARTIAL_SCAN changes. Permission failure/incomplete pagination are
not deletion. Retain last-known assets with unavailable/stale status. Report/model
binding uses IDs/definition evidence, not names. Models exist independently of reports.

Graph edges retain source definitions/receipts, scans and derivation version.
Provenance: DISCOVERED, DETERMINISTICALLY_DERIVED, LLM_INFERRED, TEAM_CONFIRMED.
Owners, fiscal rules, SLAs, tolerances and business meanings are optional enrichment;
only authoritative fields support conclusions requiring that meaning.

Separate queryability, definitions, dependencies, visual reproduction, lineage,
source access and comparability. A native-queryable measure need not translate to
SQL. Static filters do not capture runtime selections/bookmarks/RLS. Definition
denial limits context, not all model reads. Recheck source policy before dispatch.

Changed context invalidates affected capabilities/plans. Preserve prior context
for historical runs. Recurring jobs have bounded calls/time, visible last-success
and explicit recovery. A once-run CLI alone does not establish continuous discovery.

Acceptance publishes models/reports and SQL/Fabric/semantic tables after engine
freeze, then resolves questions without ID registration. Include denied/partial
scans, duplicate names, relationship changes and missing business context.
