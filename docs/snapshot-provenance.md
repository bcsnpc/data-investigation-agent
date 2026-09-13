# Run provenance and snapshot gaps

The metric adapters now capture publication-run evidence in the **same aggregate query and filter scope** as Order Count and Net Cash. This prevents a separate, later metadata lookup from being mistaken for the version used by a metric query.

Silver returns its `_silver_run_id`; Gold returns `_silver_run_id` and `_gold_run_id`; Power BI returns the selected Gold run on `FactOrderLine`. Each query also returns its row count, distinct run count and null marker count. The evidence and its hash are retained alongside metric observations in the existing immutable investigation-run records. No new credentials or cloud resources are required.

Run continuity checks compare:

- Silver's observed publication run against Gold's declared Silver input run.
- Gold's observed publication run against the semantic model's declared Gold input run.

`RUN_ALIGNED` requires exactly one valid run ID and no null markers on both sides. Different IDs yield `RUN_MISMATCH`. Multiple runs or null markers yield `MIXED_OR_MISSING`; failed queries, invalid counts/IDs, missing fields and empty scopes yield `UNKNOWN`. Empty results never borrow a run ID from unfiltered rows. These results are additional evidence; they do not change metric comparison or classification automatically.

## Why a run ID is not snapshot proof

Published run IDs identify producer executions. They do not prove that table contents remained immutable after publication. In addition, the current SQL-to-Bronze copy did not record a transactional source extraction snapshot. Bronze SQL endpoint reads are not pinned to Delta versions, and the semantic query cannot independently establish the complete source version set from a row label.

Consequently, the collector still leaves `source_snapshot` null. It never turns aligned run labels or matching totals into snapshot-comparable evidence. Strict metric checks remain NOT_COMPARABLE and classification remains UNRESOLVED. Run mismatches are candidates for investigation, not automatic freshness or technical-defect findings.

## Remaining work for verified common-source snapshots

1. Capture a source extraction identity and its consistency guarantee during ingestion. An audit maximum or timestamp alone is insufficient: changes can occur during a multi-table copy.
2. Retain a manifest mapping the immutable extraction to all destination Delta table versions, including table identities. Pin downstream reads to those versions.
3. Record each transformation's complete input and output version sets and verify them against the versions actually queried. Link the semantic model's consumed data version to that manifest.
4. Admit a common source snapshot only when the evidence chain is complete for every dependency of the requested metric. Old unversioned baseline runs must remain explicitly unverified.

This requires an ingestion/publication contract change; it cannot be reconstructed reliably from equal counts after the fact. This change adds the currently available row evidence without rewriting pipelines, regenerating data or backfilling unsupported snapshot claims.

## Use and tests

Run the existing `scripts/cross_layer_investigation.py` command. Results now include `provenance.checks` and explicit gaps; persisted requests retain the raw marker evidence. `scripts/snapshot_provenance.py` is a pure evaluator for acquired results.

Six tests cover aligned runs, a model on a different Gold run, mixed/null markers, empty scopes, malformed counts/IDs and unavailable or legacy observations. Existing query, business-rule, investigation and generator tests remain applicable.

Live run `9a1976a2-0699-4361-a88c-6509fc36d02b` verified both RUN_ALIGNED boundaries. Silver markers cover 100,000 order rows; Gold and semantic markers cover 286,652 order-line rows. All markers are single-valued with zero nulls. All five layers still return 100,000 orders and USD 64,892,824.49 net cash. Snapshot gaps remain explicit.
