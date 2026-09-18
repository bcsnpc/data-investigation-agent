> Release-specific implementation/runbook. Its old roadmap and next-step statements
> are historical. [Current status](current-delivery-status.md) and the
> [discovery-first plan](architecture/README.md) govern new work.

# Catalog scans and semantic reference analysis

Grouped B/C continuation after merged PR #148, tracked by [#149](https://github.com/bcsnpc/data-investigation-agent/issues/149).

## Implemented

- Durable, idempotent admin scan requests tied to model revision, environment, workspace and connection-profile hash.
- A finite worker claims at most one queued scan per invocation. Scans are serialized within the catalog database; a process interruption never silently replays remote work.
- Operator-owned connection configuration, frozen before collector execution. API clients cannot submit endpoints, credential paths or arbitrary commands.
- A unique collector receipt identifies its exact scan. The worker never imports whichever scan happens to be latest.
- Metadata connectivity results, collection status and imported context are recorded in scan receipts. Failed/partial imports preserve the last good context; stale model/profile requests are held.
- Conservative measure-reference graph, operation labels, cycle/ambiguity gaps, relationship definitions and affected-measure closure across old/new context.
- Admin UI for requesting scans, viewing status and inspecting dependency evidence.

The existing metadata collector performs read-only source discovery. SQL/Fabric metadata access does not prove a semantic model can execute DAX. `MODEL_QUERYABLE` and upstream reconciliation remain UNKNOWN.

## Run

Use the same database/environment in the admin host and worker. Keep admin/reader tokens in environment variables as described in [onboarding](model-onboarding.md).

```powershell
python scripts/serve_model_admin.py --database .local/model-admin/catalog.sqlite --inventory .local/metadata/inventory.sqlite --environment development --scan-config infra/metadata/development.json --port 8774
```

Select a model and request a new metadata scan. The API queues work; it does not execute connectors in the HTTP request. Run one queued job:

```powershell
python scripts/run_catalog_scan.py --database .local/model-admin/catalog.sqlite --environment development --config infra/metadata/development.json
```

The configured workspace and inventory must match the registration/host. Collector timeout is 900 seconds and existing connector timeouts remain in force. No unlimited daemon, automatic retry or OS schedule is installed. A scheduled dispatcher and finer per-connector budgets remain planned.

## States and recovery

`QUEUED → RUNNING → COMPLETED | FAILED | HELD | INTERRUPTED`

COMPLETED means the retained context imported; inspect `scan_status` and connection coverage for partial collection. HELD means model/profile changed. FAILED preserves prior context and records a redacted error type. Timeout is INTERRUPTED because child activity may be uncertain; it blocks another scan. A crashed worker leaves RUNNING with the same blocking behavior.

Do not manually restart a job to hide an uncertain outcome. Inspect the recorded job, inventory and possible collector/child process first. Automated interruption reconciliation is not yet implemented. A context can have committed before the final job receipt; preserve and inspect that context instead of rerunning automatically.

## Semantic-analysis boundary

The analyzer recognizes quoted/escaped references, ignores string/comment contents, records table/column/measure dependencies, identifies operation families and detects cycles. Unsupported functions, variable contexts and unresolved references remain gaps. It does **not** evaluate DAX, validate all DAX syntax, certify filter propagation, or translate arbitrary measures to SQL.

SUPPORTED dependency state means references within the supported analysis were resolved, not that an investigation or cross-system comparison is supported. Actual semantic values must come from Power BI in the next execution milestone. Relationship definitions are retained with execution-context verification false.

Changed source assets propagate through reference edges to affected measures. Context-level enablement remains conservatively invalidated for material changes; fine-grained active-investigation invalidation belongs with the v2 runtime. Changing the analyzer version also invalidates carried review.

## API additions

- Admin GET `/api/v2/admin/connection`: configured workspace/profile reference and explicit connectivity limitation.
- Admin GET/POST `/api/v2/admin/models/{id}/scans`: history or queue `{revision,request_key}`.
- Existing model detail now includes `semantic_graph` and `affected_measures`.

Reader credentials cannot queue scans or read raw connection/definition details. The current connection result is established by collector receipts, not by configuration presence.

## Remaining work

Scheduled dispatch, operator recovery UI, targeted remote subgraph scanning, richer business-context policies, native semantic execution and the evidence-led investigation loop remain open. This implementation uses a bounded full metadata scan followed by context diffing; it does not claim incremental remote scanning or full Phase C completion.

## Verification (2026-09-14 local date)

- Full Python suite: 387 tests passed, process exit 0; JavaScript and Python syntax checks passed.
- Focused tests cover references/comments/escaped names/cycles, affected closure, job deduplication, role separation, configuration freezing, exact receipt selection, failed imports and interrupted dispatch.
- Browser: configured connection shown, scan queued and refreshed, dependencies visible; no reported browser errors. Local browser/server closed after verification.
- Live read-only metadata scan `968f8867-4714-4e49-aad9-35603a747294` completed with SQL and Fabric collection AVAILABLE. Imported context `7ed174c6-3503-4cd4-b55c-d5ccc18f2246`: 25 measures, five relationships and three reports. One measure retains an analysis gap; overall dependency coverage stays PARTIAL.
- Native DAX queryability remains UNKNOWN. No source/model mutation, repair, notification or new cloud infrastructure was performed.
