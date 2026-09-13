# Deterministic investigation checks

This first Phase 5A slice supplies backend comparison contracts, report/metric resolution, freshness acquisition and immutable local evidence records. It does not yet execute cross-layer business queries or diagnose tickets. A mismatch is evidence of a difference, not proof of a technical defect.

## Tools

`scripts/investigation_checks.py` provides:

- `resolve_context(database, lineage_run, report_id, metric)`: finds a unique measure among a report's captured upstream dependencies. Missing or ambiguous matches stay unresolved. Returns the captured measure definition/hash and relevant lineage gaps.
- `compare(upstream, downstream, mode)`: exact decimal totals or complete composite-key multisets. Duplicate, missing and extra key counts are retained; samples are capped at 20 distinct keys. Equal duplicate-bearing extracts can match; their duplicate counts remain visible.
- `freshness(observation, as_of, max_age_seconds=None)`: compares successful refresh completion against an explicitly supplied age policy. Without that policy, returns UNKNOWN with the observed age. A refresh timestamp alone cannot establish business-data freshness.
- `run_checks(database, request)`: verifies asset IDs and upstream connectivity against an explicit persisted lineage build, evaluates checks and stores the full request/result atomically in `investigation_runs`. Each execution gets a new ID; existing evidence is retained. Comparisons also return downstream affected asset IDs and relevant lineage gaps. These are potential dependencies, not quantified business impact.

## Evidence contract

Every observation contains `asset`, timezone-aware `captured_at`, a versioned `query_id`, `data`, and `result_hash`. The hash is SHA-256 of `canonical(data)` from this module. This detects payload inconsistency, not authenticity: trusted acquisition adapters remain responsible for query provenance and complete extraction. Do not submit credentials or arbitrary response headers in requests; the local evidence database is ignored by Git.

Comparison observations additionally require identical, nonempty `metric_contract`, `grain`, `currency`, `filters` and `source_snapshot`. Empty filter objects are valid. The snapshot must identify the common upstream extraction or dependency-version set consumed by both layers; independent layer run IDs or acquisition timestamps are insufficient. Missing or different context returns NOT_COMPARABLE, even if values happen to match.

Totals use decimal strings or integers. Floats, nulls, booleans and non-finite numbers are rejected; null is never silently treated as zero. Key payloads are arrays of composite-key arrays, for example `[["ORD-000002", 1]]`; null keys are rejected. Both extracts must explicitly declare `complete: true`. Full key payloads are retained locally, so this in-memory implementation is intended for bounded investigations; server-side key reconciliation is follow-up work.

Freshness data contains `last_success_at`, or null if unavailable. Its acquisition cannot precede the claimed completion. Policy uses nonnegative integer seconds, inclusive at the threshold. The live adapter retains refresh IDs, types, states and timestamps; it does not store API error payloads. Failed latest runs remain visible in the retained history; age evaluation specifically concerns the last successful completion.

## Running

Install the existing lineage requirements first. Evaluate a request containing `lineage_run`, `as_of` and a nonempty `checks` list:

```powershell
python scripts/investigation_checks.py --database .local/metadata/inventory.sqlite --request .local/investigation-request.json
```

Each comparison check has `kind` (`total` or `keys`), `upstream` and `downstream` observations. A freshness check has `kind: "freshness"`, `observation` and optional `max_age_seconds`. Inputs are data only; this command never executes supplied SQL or code.

Acquire current semantic refresh history using the existing configuration and read-only authentication:

```powershell
python scripts/check_model_freshness.py --model a77a8464-06d8-42dc-9ec8-832e813346f4 --lineage-run b5db8886-61e4-49cc-92c5-4f682ab7268f
```

Only set `--max-age-seconds` once an actual freshness policy is agreed. No policy has been configured for this estate.

## Verification and limits

Live refresh check `7b04d9cc-01ed-42e2-be04-d1ad34c774a0` acquired the deployed semantic model's history and persisted it against lineage build `b5db8886-61e4-49cc-92c5-4f682ab7268f`. It returned UNKNOWN because no freshness policy exists. This is the intended result, not a failed connection. Executive Sales / Net Sales resolved to exactly one captured measure with zero relevant lineage gaps.

Twelve offline tests exercise exact large decimals, invalid amounts, incompatible context, tampered hashes, duplicate and composite keys, incomplete extracts, policy thresholds, future timestamps, report ambiguity, unrelated boundaries and atomic persistence. Existing generator, metadata and lineage tests also pass.

Every run remains classified UNRESOLVED. Matching totals do not prove expected business behavior; mismatches do not establish root cause. Subsequent work must add bounded read-only SQL/Fabric/DAX query adapters, reproducible filter and snapshot capture, ordered boundary analysis, and independent evidence for classification. Active report slicers, tickets, automatic bug creation, notifications and defect injection are not implemented by this slice. No cloud data or definitions were changed.
