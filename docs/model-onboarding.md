> Release-specific implementation/runbook. Its old roadmap and next-step statements
> are historical. [Current status](current-delivery-status.md) and the
> [discovery-first plan](architecture/README.md) govern new work.

# Model onboarding: implemented control-plane slice

Delivered in the existing [PR #148](https://github.com/bcsnpc/data-investigation-agent/pull/148), together with the bounded-v1 baseline and product roadmap. This is the first combined B/C slice, not completion of every B/C requirement.

## Working behavior

- Basic admin browser interface for registration, metadata import, business-context confirmation, readiness and enable/disable controls.
- Model identities scoped to the configured environment; duplicate native registrations rejected within that environment.
- Retained scan import uses the existing hash-validated report/model bundle and explicit native model bindings. All discovered measures are retained, with no metric whitelist.
- Immutable context history, request revision checks and audit events. Newer changed definitions invalidate enablement and review; identical definitions can carry the reviewed context forward with an event.
- Older scans and partial-scan removals cannot replace current context. Invalid imports preserve the prior context.
- Separate admin and catalog-reader credentials. The reader endpoint exposes enabled report choices without raw definitions or business context.
- Enablement is **catalog-only**. Live execution remains unavailable and query capabilities remain UNKNOWN. Existing bounded-v1 ticket execution is unchanged.

The retained OrderOps inventory was imported locally: **25 measures and three reports**. No cloud scan, data query or remote mutation was needed for that check.

## Start locally

Set distinct random values of at least 32 ASCII characters for `INVESTIGATOR_ADMIN_TOKEN` and `INVESTIGATOR_READER_TOKEN` in the current PowerShell session. Keep them outside source control. Then run:

```powershell
python scripts/serve_model_admin.py --database .local/model-admin/catalog.sqlite --inventory .local/metadata/inventory.sqlite --environment development --port 8774
```

Open `http://127.0.0.1:8774`. Enter the admin token, register native workspace/model/report IDs and import a completed retained scan ID. Review business context, then enable catalog visibility. Explicit “Unknown” values are allowed as descriptive context; this slice does not treat prose SLAs/tolerances as executable policy.

The launcher is loopback-only. The inventory path is operator configuration, never an API argument. Tokens stay in browser memory, not browser persistent storage. This is a local pilot with shared role tokens, not a multi-user production authentication service.

## API

All paths use bearer authentication; `/api/v2/admin/*` requires the admin credential.

| Method/path | Body or result |
| --- | --- |
| GET/POST `/api/v2/admin/models` | List or register `{name,workspace,model_id,report_ids}` |
| GET `/api/v2/admin/models/{id}` | Context, measures, readiness, business review, events and versions |
| POST `/api/v2/admin/models/{id}/import` | `{revision,scan_id}`; import existing retained metadata |
| POST `/api/v2/admin/models/{id}/review` | `{revision,business}`; definition, owner, date_basis, refresh_expectation, tolerance, exceptions |
| POST `/api/v2/admin/models/{id}/enable` | `{revision,enabled}`; review current context first |
| GET `/api/v2/admin/models/{id}/contexts/{version}` | Immutable prior context belonging to that model |
| GET `/api/v2/reports` | Enabled catalog choices; `execution_available:false` |

JSON writes are limited to 16 KiB. Stale revisions return 409. Environment/model ownership checks reject cross-scope context access. This implementation deliberately names the action `import`, not `scan`: it does not pretend a new cloud scan ran.

## Follow-on scan and semantic delivery

[Catalog scans and reference analysis](catalog-scans-and-semantics.md) adds durable scan requests, explicit worker dispatch, connection receipts, dependency/operation analysis and affected-measure propagation. This extends the original retained-import slice; native model querying is still unverified.

## Remaining work in the same product milestone

- Rich connection registration and fine-grained permission probes; configured-connection metadata scans now have a queued lifecycle.
- Scheduled/triggered scans, affected-subgraph invalidation and scan failure history.
- Full semantic/context analysis and richer per-metric readiness beyond conservative reference discovery.
- Structured per-metric business definitions, provenance enrichment and policy enforcement.
- Versioned context packs attached to v2 investigations; native query tools and adaptive execution.

These remain tracked as B/C work followed by D–H, not new tiny PR milestones. Existing definitions and reports can be inspected now; this UI does not claim to investigate them yet.

## Verification

Full Python suite: 375 passed. Focused onboarding tests cover binding/hash rejection, environment ownership, immutable history, review invalidation, partial removal, roles and input limits. Browser workflow completed registration/import/review/enablement without reported errors. Real retained OrderOps metadata yielded 25 measures and three reports. JavaScript syntax check passed. No live cloud query was run.
