# Durable v2 diagnostic backend milestone

This typed-runtime milestone is merged in PR #162. The next [adaptive session milestone](adaptive-investigation-milestone.md) builds on it; descriptions below apply to the original operator-supplied action runtime.

Tracked by [#161](https://github.com/bcsnpc/data-investigation-agent/issues/161), following merged PR #160. This is one grouped delivery across aggregate analysis, execution, recovery, SQL connection handling and acceptance tests. It does not close every D/E/F exit gate or introduce the adaptive LLM planner.

## Delivered together

| Component | Result |
| --- | --- |
| Aggregate semantics | Metadata-resolved direct SUM and COUNTROWS shapes, explicit reviewed native input IDs, recursive dependency inspection for complex parents |
| Proof readiness | Machine-readable missing semantic/version/readback/write-boundary requirements, derived from current adapters rather than client proof flags |
| Typed tool registry | Native reads, source reads and comparisons; validated action lists with explicit prior-step references, no fixed layer order |
| Durable runtime | Pinned code/Python/config/context/request hashes; idempotency keys, persistent call reservations, reserved receipt IDs, fenced workers and event history |
| Recovery | Adoption of matching completed orphan receipts; safe replay of missing local assessments; uncertain cloud completion remains held |
| SQL connection recovery | Existing bounded 40613 connection-only retry policy reused, with structured connection-attempt evidence |
| Interfaces | Operator CLI for create/execute/reconcile/status; admin-only registry, run, aggregate/dependency and proof-readiness APIs |

## What a run does

An operator supplies a validated action plan. The registry resolves all read requests against one enabled model context and checks the budget before creating the run. Each cloud action reserves its call and receipt ID before dispatch. Native DAX remains evaluated by Power BI; source aggregates remain parameterized SELECTs. Comparison actions refer to specific earlier native/source steps, so multiple observations cannot accidentally overwrite one another.

Source-first, native-first, standalone observations and multiple-native-observation plans are supported. The earlier native/source/comparison request shape is retained as a convenience recipe. This is flexible execution of an approved plan, **not evidence-led choice of the next action**. The future planner must supply and revise actions through a scoped orchestration contract; this milestone does not pretend a static operator plan is an AI investigation.

Completion means the admitted actions finished. It does not mean healthy data or verified cause. Without the missing proof adapters, comparison outcomes remain INSUFFICIENT_EVIDENCE. An observation-only plan also finishes with an insufficient-evidence outcome rather than inventing a comparison.

## Plan and commands

Use IDs/revisions from the current catalog. This example deliberately puts source first:

```json
{
  "model_id": "registered-model-id",
  "call_budget": 2,
  "actions": [
    {
      "tool": "source",
      "input": {
        "model_id": "registered-model-id", "revision": 5, "context_id": "context-id",
        "object_id": "sql-object-id", "operation": "count_rows", "column_id": null,
        "filters": [{"column_id": "sql-currency-column-id", "values": ["USD"]}]
      }
    },
    {
      "tool": "native",
      "input": {
        "model_id": "registered-model-id", "revision": 5, "context_id": "context-id",
        "measure_ids": ["measure-id"],
        "filters": [{"column_id": "native-currency-column-id", "values": ["USD"]}],
        "dimension_id": null, "include_dependencies": false
      }
    },
    {
      "tool": "compare",
      "input": {"native_step": 1, "source_step": 0, "measure_id": "measure-id", "mapping_id": null}
    }
  ]
}
```

Native/source input contracts remain documented in [native diagnostics](native-catalog-diagnostics.md), [typed scope](typed-diagnostic-scope.md) and [source diagnostics](source-catalog-diagnostics.md). A reviewed comparison can reference a mapping registered through the existing admin API; no real business mapping is auto-confirmed by the executor.

```powershell
python scripts/run_investigation_v2.py --config infra/metadata/development.json --database .local/catalog.sqlite --environment development --request .local/run.json --request-key first-check-001 --approve
```

Reusing a completed request key or executing its run ID returns its saved result without more queries. A key with changed input is rejected. A new key authorizes a new run; it is not a hidden retry.

```powershell
python scripts/run_investigation_v2.py --config infra/metadata/development.json --database .local/catalog.sqlite --environment development --run-id SAVED_RUN_ID --status-only
python scripts/run_investigation_v2.py --config infra/metadata/development.json --database .local/catalog.sqlite --environment development --run-id SAVED_RUN_ID --reconcile --approve
```

## Recovery and boundaries

| Interruption | Behavior |
| --- | --- |
| Before dispatch reservation | Explicit reconciliation fences the old worker and can resume if admission is still current |
| After a read receipt completes, before run commit | Adopt only the reserved receipt ID with matching model/request hash; do not resend the query |
| After local comparison persistence | Adopt the matching assessment |
| Before local assessment persistence | Fence and replay the local-only assessment; no new cloud calls |
| Missing/RUNNING/INTERRUPTED cloud receipt | Keep uncertainty and the reserved call; no automatic resend or expiry-based assumption |
| Model disablement/context change after a completed read | Retain the terminal historical receipt and hold the run; do not resume stale actions |
| Failed query | Stop the run; no automatic query retry |
| Completed run | Return saved history without dispatch |

Only one dispatched action is admitted across this catalog database at a time. Worker tokens fence run-state commits; tokens are not exposed in API projections. There is no automatic lease expiry or distributed queue. Unknown remote completion can block later dispatch until trustworthy completion/cancellation evidence exists; an elapsed timeout is not proof. A general remote-cancellation reconciliation provider is still missing.

The engine fingerprint covers investigator modules, driver/helper files and the executing Python version. It is not the full dependency/provider freeze required by Phase H. Completed history remains readable after code changes, but an incomplete run cannot silently migrate to new code/configuration/context.

The budget allows 1-10 cloud-read actions and at most 20 total actions. Reserved calls survive restart and are not refunded on failure. It is an execution budget, not a billing guarantee or Azure free-quota measurement. No SQL tier, overage setting or data/schema is changed by this milestone.

## SQL 40613 handling

The source worker now records whether a failure happened during connection or query execution. The existing `sql_connect_retry.read_with_retry` helper retries only SQL error 40613 at the **connect** stage, up to three connection attempts with 10/20-second waits. Query-stage errors, authentication failures, unknown stages and worker timeouts are not retried. Structured attempts are retained with the source receipt.

Each worker attempt is capped at 90 seconds; the source action can therefore take up to roughly 300 seconds including backoff. The call reservation stays occupied throughout. This does not replay a submitted query or change the SQL service configuration. A 40613 code alone does not establish that auto-pause caused the incident.

## Proof readiness and semantic limits

Direct SUM(exact numeric column) and COUNTROWS(table) can be identified without metric-name rules. Renamed tables/columns, escaped identifiers and immutable definition changes are tested. Calculated columns, distinct counts, context-changing expressions and complex parents are not falsely flattened into direct aggregates. Complex parents retain their recursively discovered children and continue to use native Power BI evaluation.

These are operator/input shapes and reviewed declarations, not full upstream equivalence. The real retained model uses Direct Lake. Current providers do not establish:

- A shared source/native input generation and complete native key/value readback.
- Stable remote definitions throughout capture.
- An enforced exclusive remote publication/write boundary.
- Certified effective identities, relationship/filter propagation, date roles and materialization grain.

`GET /api/v2/admin/models/{id}/proof-readiness` exposes these requirements with `live_acceptance_ready=false`. The controlled live healthy/defect acceptance gate is not ready. It requires implementation and an appropriate isolated test estate, not an API checkbox.

## Admin interfaces

`GET /api/v2/admin/tools` exposes tool names and call costs. Under `/api/v2/admin/models/{id}`:

- `GET /investigations/{run_id}` returns shared run/step/event history without lease tokens.
- `GET /aggregate-semantics` returns the retained measures' direct aggregate shapes.
- `POST /aggregate-semantics` with `{"measure_id":"..."}` returns dependency shapes.
- `GET /proof-readiness` returns the current proof requirements.

These routes use existing admin and environment/model boundaries. They do not dispatch cloud queries. No new browser workflow or Azure deployment is claimed.

## Verification

Focused coverage includes source-first plans, multiple explicit native dependencies, standalone reads, unknown tools/forward-reference rejection, budget persistence, concurrent workers, stale admission, orphan/tampered receipts, interrupted queries and local-only replay. Aggregate and connection-recovery suites cover supported/unsupported shapes and query-stage retry rejection. **All 472 script tests passed**; the three new suites are included in CI. PowerShell syntax validation passed.

Live evidence in `.local/model-admin-verify/native-diagnostics.sqlite`:

- `63b06107-7e26-45ae-8eaf-ff24a979db0d`: native read completed, SQL returned 40613, run held without comparison. This receipt predates stage logging, so its exact failure stage and auto-pause cause were not proven.
- `bfa1ff35-b84c-49fe-a552-37bed24a5cd3`: native and source each returned **100000**; two calls reserved; comparison finished as **INSUFFICIENT_EVIDENCE** with mapping/version/context gaps. SQL succeeded on its first connection attempt; the retry branch is validated with simulated failures, not claimed as a live retry success.
- Re-executing the completed run ID produced no additional native/source receipts or runtime events. Evidence is in `.local/v2-live-repeat.json`.

The successful cloud run preceded the final local-only replay refinement; transport behavior was unchanged by that refinement. No LLM calls or new cloud resources were used. This is a durable diagnostic backend milestone, not proof that the general investigator or all eight product acceptance families are complete.
