# Incremental graph maintenance

`scripts/scan_estate_graph.py` is the scheduled entrypoint. Default invocation is
plan-only; `--apply` performs live metadata reads and shared graph writes. It
creates no resource, permission, budget account or schema. Use the existing
Container Apps Job with `0 */6 * * *` only after the owner-approved deployment
has exact gateway grants, existing shared budget account IDs and migrated graph
tables. No schedule has been deployed by this implementation.

The operator JSON has these exact keys:

```json
{
  "estate": "declared-estate-name",
  "workspace": "workspace-guid",
  "owners": ["approved-item-guid"],
  "authentication": {"mode": "federated_reader", "tenant_id": "tenant-guid", "client_id": "reader-app-guid", "principal_id": "reader-object-guid", "managed_identity": {}},
  "storage": {"account_url": "https://approvedaccount.blob.core.windows.net", "identity": {}, "snapshot_channel": "private-snapshot-channel", "tape_channel": "private-tape-channel"},
  "definition_uri_prefix": "https://approvedaccount.blob.core.windows.net/snapshots",
  "budget": {"environment": "existing-shared-usage-environment", "policy_sha256": "sha256-of-existing-usage-policy-body", "round_id": "ROUND_NINETEEN", "rolling_limit": 3000},
  "max_requests": 40,
  "approval": "Dated owner approval reference for this schedule and scope"
}
```

The placeholders must be replaced with the existing explicit identity and route
declarations. `INVESTIGATOR_STATE_BACKEND=postgresql`, the existing
`INVESTIGATOR_PG_HOST`, `INVESTIGATOR_PG_DATABASE`, `INVESTIGATOR_PG_USER`,
`AZURE_CLIENT_ID`, `DIA_GATEWAY_STATE_IDENTITY`, `DIA_GATEWAY_POLICY` and
`DIA_GATEWAY_HTTP_IDENTITY` retain their existing meanings. The reader does not
receive platform write permissions through the metadata configuration. Raw
definitions use the separately bound existing platform Blob channel. The
scheduled process refuses projected recording until its definition projection
contract exists.

```text
python scripts/scan_estate_graph.py --config <config.json> --receipt <plan.json>
python scripts/scan_estate_graph.py --config <config.json> --receipt <run.json> --apply
```

Every actual metadata HTTP attempt reserves one request through the existing
`SharedUsage` authority, which atomically checks both the current round pot and
rolling window. The approved policy body hash, round ID and rolling limit must
match; no new `state_accounts` request accounts are manufactured. Failed requests
remain charged. A refusal happens before transport and creates no reservation.
A process crash leaves its reservation charged conservatively for reconciliation. The
per-scan request cap bounds definition polling as well as listing pages. Existing
account ceilings and protected restoration reserve are not changed.

`graph_scan_schedule_plan.py` takes a retained ARM response for the existing job,
the scan configuration, exact gateway policy, and a digest-pinned existing worker
image. It emits a PATCH body and URL without sending either. It preserves the
job's identities, platform environment and resource sizes, selects the trusted
`graph_scan_bootstrap.py` entrypoint, limits each run to ten minutes with no
platform retries, and prints the worst-case 30-day compute seconds. Root must
compare that bound with the existing free allowance before deployment. For the
existing two-vCPU/four-GiB job, 120 ten-minute runs imply at most 144,000 vCPU-seconds
and 288,000 GiB-seconds per 30 days; this is a usage bound, not a claim of zero
incremental cost or remaining free allowance.

```text
python scripts/graph_scan_schedule_plan.py --existing-job <job.json> --config <scan.json> --gateway <gateway.json> --image ghcr.io/<existing-image>@sha256:<digest> --output <schedule-plan.json>
```

After reviewing the prepared plan, write only its `body` to an ARM request file
and use `az rest --method patch --url <plan.url> --body @<body.json>`. This updates
the existing job, never creates one. Do not apply while the owner is using that
job for a manual verification; record the existing trigger before changing it.

The live Fabric collector lists at most five pages/1,000 workspace items and
considers at most 100 explicitly configured owners. Each owner is
`fabric://<workspace>/<item>`. Keep that ownership convention for the initial
graph seed as well; this code does not silently reassign legacy catalog-wide
graph ownership. Modified-item fingerprints skip unchanged owner reads. If the
listing supplies no modified timestamp, the collector honestly falls back to
per-owner definition-hash polling: reads may touch every configured owner, but
only definitions whose content changed are extracted and replaced. No entire
owner catalog is re-extracted as an incremental scan.

`getDefinition` is a metadata read even though its API method is POST. A missing
permission or unsupported item kind is recorded as UNAVAILABLE, leaving the
owner's cursor unchanged. Permission is never elevated automatically. Bounded
operation polling remains subject to the exact gateway endpoint grants and
request cap. Permission-sensitive list omissions are **not** deletion proof;
the live collector does not remove an owner merely because it disappears from a
listing. `IncrementalScanner` supports explicit trusted deletion events, or an
explicitly authoritative complete inventory from another collector. Deleted
objects retain graph history and dependent paths gain a named stopping boundary.

The optional `sql` configuration is an array of at most ten groups, each with
`identity` (stable collector name), `config` (the existing explicit Fabric SQL
reader configuration) and `objects` (owner-to-resolved-object map, max 100).
The `FabricSqlChanges` callback uses `fabric_sql_surface.read` with every child
permission/control/query request metered through the same shared usage guard.
It compiles only exact-object sys catalog controls, with the existing CATALOG,
object, row-cap and timeout authority. It never grants arbitrary sys queries.
The poll reads schema columns plus object modify dates; a view/procedure body
is fetched only when its fingerprint changes. A differing modify date between
poll and definition read refuses the non-atomic observation. Missing VIEW
DEFINITION evidence or a body exceeding 262,144 UTF-16 bytes is unavailable.
Direct application SQL callbacks remain unimplemented; no Fabric SQL reader is
silently substituted for them.

The generic `SqlSchemaChanges` adapter remains available for other already
attested callbacks. Without modify-date evidence it polls definitions, because
unchanged columns do not imply unchanged view/procedure logic. Event/activity-log
feeds and freshness/Delta-history collectors are not implemented. Every scheduled
result explicitly names runtime monitoring and refresh/run/Delta history as
UNAVAILABLE; SQL modify dates are never presented as data freshness.

Changed owner snapshots close old graph versions and append change records.
Before a definition fetch, the shared collection history records REFRESHING.
Failure records UNAVAILABLE and does not advance the owner cursor. Graph reads
at that time expose the unavailable owner, downgrade its affected earned proofs
to STALE, and traversal stops at the named gap. A worker crash leaves REFRESHING,
which is also unavailable. Earlier as-of reads retain their earlier status.
Only a successful definition check clears the gap; unchanged listing metadata
does not clear it. The sealed graph history is not rewritten to apply this view.
Previously earned proofs on changed edges remain present but STALE. Unrelated
owners are not fetched or re-extracted. Cursor advancement happens after graph
replacement; a crash between them causes a harmless hash-checked retry. Revision
conflicts refuse rather than silently overwriting a newer scan.

Offline tests cover change/revert against two definition versions, unchanged
timestamp-only updates, absent modified timestamps, explicit deletion/history,
permission failure, page bounds and continuation scope, proof staleness, and
request reservations. They are not a live controlled-change result. The live
test must use the existing estate build script under the owner's recorded
approval, change one fixture definition, scan, then revert through the same
script and scan again. Record both changes and restoration; the scanner itself
never mutates the estate.
