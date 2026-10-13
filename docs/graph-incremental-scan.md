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
  "budget_accounts": ["existing-round-account", "existing-rolling-account"],
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

Every actual metadata HTTP attempt reserves one request against each configured
existing shared account. Failed requests count. If any account denies admission,
the request is not sent and any other unspent reservation is released. A process
crash leaves its reservation charged conservatively for reconciliation. The
per-scan request cap bounds definition polling as well as listing pages. Existing
account ceilings and protected restoration reserve are not changed.

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

The `SqlSchemaChanges` adapter takes the existing attested exact-object catalog
reader and a scoped definition callback. It compares column fingerprints and an
observed object modify date. Without modify-date evidence it polls definitions,
because unchanged columns do not imply unchanged view/procedure logic. The
Fabric scheduled CLI does **not** configure SQL callbacks automatically: each SQL
route still needs its existing reader/gateway binding. Event/activity-log feeds
and freshness/Delta-history collectors are not implemented here.

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
