# Microsoft runtime facts collector

This is an operator-configured, read-only adapter, not a metadata-only success
claim. `cloud_facts_collector.execute(config)` runs under the existing worker
identity, shared PostgreSQL state and SCAN request accounting. It calls no model,
never runs an estate job or refresh, and never applies migrations.

Invoke through the unified runner's collector handler, or the same existing
worker bootstrap with its gateway policy, shared-state environment and config:

```powershell
python scripts/cloud_facts_collector.py --config <approved-facts-config.json>
```

Required config keys: `estate`, `authentication` (existing federated_reader or
managed_identity declaration), existing Blob `storage`, `receipt_uri_prefix`,
shared `budget` (`environment`), `subjects`, `max_requests`, and owner `approval`.
Optional `sql_configs` maps reader labels to existing fabric/sql_reader config;
`key_tables` names existing graph subject IDs eligible for profiling;
`max_subjects_per_wake` bounds the round-robin selected batch;
`list_interval_seconds` defaults to 21,600. Schedule wake frequency and effective
poll cadence are distinct. A 30-minute job does not promise 30-minute facts when
the shared 1,000-request scan allowance cannot support that cadence.

Each subject is an existing graph node ID, with `{kind,workspace,item}`. Kind is
JOB, MODEL or TABLE. JOB optionally declares `job_type` for schedule retrieval.
JOB/TABLE may declare an `audit` route; TABLE may declare a `profile` route:

```json
{
  "kind": "JOB", "workspace": "<workspace GUID>", "item": "<pipeline GUID>",
  "job_type": "Pipeline",
  "audit": {
    "reader": "<existing reader label>", "connection": "<existing SQL server>",
    "database": "<existing Warehouse database>", "principal": "<expected SQL principal>",
    "schema": "<audit schema>", "table": "<audit table>",
    "columns": {
      "run_id": "<run ID column>", "start": "<start UTC column>",
      "end": "<end UTC column>", "status": "<status column>",
      "rows_read": "<rows read column>", "rows_written": "<rows written column>"
    }
  }
}
```

A profile route has the same reader/connection/database/principal/schema/table
and `key_columns` (1–8 exact configured column names), rather than audit columns.
It compiles COUNT_BIG and an aggregate SHA256-prefix checksum per declared
column. The checksum is labelled collision-prone and **not an equality proof**;
it is a change signal, never a business verdict. It hashes SQL text
representations and does not retain raw column values. Row count and checksums
come from the same query; a read failure is never replaced with a recount or a
job's accounting. Profiles only run once per new observed audit load marker.

Every HTTP request/response and SQL query/response is retained in immutable Blob
CAS through DefinitionSink before a fact can reference it. SQL facts require
query-bound self-reported principal/database and read-only permission checks.
Only exact configured tables/columns compile; no model SQL, external object or
mutation is accepted. Artifact permissions remain the existing application
worker's permissions, separate from read-only estate identities.

Implemented list surfaces:

- [Fabric item job instances](https://learn.microsoft.com/en-us/rest/api/fabric/core/job-scheduler/list-item-job-instances): one recent-run list, not a request per run. Start/end/status/error retained; missing row accounting remains unavailable.
- [Power BI grouped refresh history](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/get-refresh-history-in-group) and [refresh schedule](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/get-refresh-schedule-in-group): 403 is a retained named gap. Supported daily/weekly schedule slots use explicit Windows-to-IANA timezone mapping. Unsupported timezone/ambiguous DST slots remain unavailable; no next-due time is guessed.
- Fabric job schedules when an exact job type is declared. Unsupported recurrence interpretation remains visible; raw returned schedule is retained rather than invented overdue evidence.
- Declared Warehouse audit reads for exact listed run IDs, first. A different run's counts never attach. An audit denial is not permission to try another scope. Without a declared audit, load accounting is unavailable unless a separately implemented and approved monitoring route exists. The existing federated reader's token audience allowlist does not include KQL; this adapter does not add one.
- Table load time derives from successful declared audit rows. SQL object modify dates are never substituted for data-load time. Delta history is unavailable through this SQL endpoint implementation unless a separately approved readable Delta route is built; this is a named gap, not proof of no loads.

Successful empty histories are RUN_HISTORY/OBSERVED_NEGATIVE. Missing/unreadable
histories are UNAVAILABLE. Continuation tokens make coverage partial; they never
establish absence/overdue. Recent successful runs supply observed median
duration. Overdue requires a complete recent listing and a supported declared
schedule slot, with both receipts referenced.

No live coverage is claimed by these offline tests. The operator must publish
actual per-estate collected facts/gaps, physical request totals, schedule cost
and successful worker-role migration test separately.
