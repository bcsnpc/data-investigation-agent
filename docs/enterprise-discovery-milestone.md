# Environment discovery through ticket context

Tracking: [#195](https://github.com/bcsnpc/data-investigation-agent/issues/195).
Implementation status is owned by [current delivery status](current-delivery-status.md).
This is discovery acceptance, not the frozen Unknown Domain Challenge.

## Behavior

One approved profile supplies a Fabric workspace and SQL database/schema. The
metadata identity enumerates accessible workspaces but stores only the approved
root. Definitions, report bindings, tables, histories and SQL catalogs each have
coverage. A failed definition does not erase a listed asset. Missing objects are
removed only under complete corresponding listing coverage; failures retain the
last known asset as UNKNOWN_DUE_TO_PARTIAL_SCAN. A narrowed policy removes assets
from the local scope without claiming a remote deletion.

Immutable SQLite scan bodies retain assets, stable definition hashes, changes,
provenance, observations, coverage and graph edges. Containment, explicit report
bindings, measure dependencies, visual references, notebook reads/writes and
pipeline execution reuse the existing lineage parser. Similar names do not prove
cross-system lineage. Missing endpoint/binding evidence remains a graph gap.

Supported models enter the existing workspace catalog automatically. They own
model context independently of reports, including reportless models. Optional
business definitions remain enrichment; discovery never creates team confirmation.
Existing manually registered models are left in legacy override mode. Explicit
operator disable persists across automatic scans.

A distinct read-only native identity is mandatory for discovered execution.
`native_reader.workspace_ids` can replace `model_ids` in the configured reader
profile; exactly one scope form is accepted. Workspace scope never grants remote
permissions. Existing admission, typed query builders, receipts, context fencing,
cancellation and budgets remain in force.

## Runbook

Install the workspace and lineage requirements. Keep local credentials/configs
outside Git. Use a validated metadata profile with approved workspace, SQL schema,
metadata credential references and a separate native reader. The inventory and
catalog paths should be separate SQLite files.

```powershell
python scripts/run_enterprise_discovery.py --config .local/enterprise-config.json --database .local/enterprise-catalog.sqlite --environment development --request-key first-environment-scan
```

The same request key returns the saved scan without remote work. A changed policy
cannot reuse that key. Only one active scan per environment is admitted. An
interrupted process remains RUNNING and requires operator reconciliation; it is
not automatically replayed. Fresh scans use new keys.

Finite scheduled repetition (suitable for an external scheduler):

```powershell
python scripts/run_enterprise_discovery.py --config .local/enterprise-config.json --database .local/enterprise-catalog.sqlite --environment development --cycles 2 --interval-seconds 60
```

The CLI does not install a service or claim perpetual discovery. Its default
collector limits are 160 transport/catalog operations, 20,000 assets, 32 MiB of
response/expanded metadata and a 600-second admission deadline. An in-flight
transport retains its own timeout. SQL catalog collection is one operation with
multiple catalog queries, not one SQL statement. OneLake fallback requests use the
same per-call budget. No business-row queries run during discovery.

Start the existing local workspace with the same catalog/environment/profile.
Eligible discovered models appear in model selection and question intake. Existing
question intake still has bounded catalog size and supported scope restrictions.
The authenticated workspace exposes POST `/api/workspace/context/search` with
`{"text":"keyword","limit":20}` and POST `/api/workspace/context/asset` with
`{"asset_id":"discovered identity"}`. Search/traversal returns metadata and
provenance; it never authorizes query execution.

## Validation and remaining scope

Behavioral tests cover new model/report/semantic/Fabric/SQL assets, reportless
models, repeat diffs, duplicate-name ambiguity, explicit deny, malformed/conflicting
bindings, partial/denied scans, schema-policy narrowing, budgets and no-call replay.
Existing browser regression passed 30 checks with injected transports.

The business workspace scan collected 399 assets using 47 transport/catalog
operations, with 24 complete surfaces and one failed lakehouse-table listing.
Its catalog automatically exposes one model and three reports. A separate isolated
workspace scan also projected its model without manual registration. Native receipt
`922f94e2-627e-4d4b-8691-f69d49495c8b` completed with value 8 and the dedicated reader
principal. This was the existing regression fixture, not a newly invented unknown
domain or causal verification. Local receipts remain under `.local/enterprise-discovery`.
Full regression and repeat-scan acceptance are recorded in current status.

Limits: one workspace/database/schema per profile, no installed recurring service,
no warehouse endpoint catalog adapter, TMSL/PBIR support only, and permission/format
gaps. Models with unavailable definitions are retained but not executable through
this path. Every imported context currently invalidates older scope previews,
even on unchanged scans. Graph search is available to callers; the LLM still needs
dynamic retrieval/proposed diagnostics in the next grouped milestone. V2 remains
local and single-operator. No live asset publication, schema/data mutation,
permission change, quota change or deployment was performed for this milestone.
