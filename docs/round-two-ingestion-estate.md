# Round-two isolated application ingestion: estate checkpoint

2026-10-03. Known-domain estate preparation, not an investigation or acceptance
pass. Follows the explicit one-table grant recorded in
[reader scope decision](round-two-reader-scope-grant.md), merged in PR #343.
No historical receipt or failed attempt was changed.

## Estate before and after

The existing empty Copy Job `57e128c3-6ba0-4aaf-9464-81164ecdc782` had no source,
destination or runs. Publisher `admin@skynwhy.com` (object
`23de217f-6e14-49cf-9acd-47dcd83cb82f`) created a separate managed SQL connection,
created an isolated schema-enabled lakehouse, attached a full-copy mapping to
that job, retrieved the served definition, and executed it once. No schedule,
existing report/model/table, permission or configuration changed here.

| Artifact | Published identity / definition |
| --- | --- |
| Source | `sql-orderops-9696025.database.windows.net;ordersops`, `app.stock_movements_round_two_20261003` |
| Managed connection | `3f5891f3-092b-4c26-b838-1d024e989501`, `round_two_movements_read_only_20261003` |
| Destination | Lakehouse `33618b8d-46eb-4fe7-b80b-122c331260a3`, `round_two_bronze_20261003`, `dbo.stock_movements_round_two_20261003` |
| Copy Job | `57e128c3-6ba0-4aaf-9464-81164ecdc782`; Batch, Overwrite, timeout ten minutes, retry zero |
| Run | `0a40d708-af1d-43fd-906b-073b0fda7f75` |

The publisher owned the managed connection; its source credential is the existing
`orderops_investigator` read-only credential. Creating it gave that principal no
new database scope. Passwords remain in the managed connection and local protected
credential reference, never in retained metadata or this PR. The earlier shared
connection was not reused: its safe metadata established server/database and
publisher ownership, but not the credential principal.

The served definition retained the exact `externalReferences.connection` and
workspace/lakehouse destination IDs. Its sole mapping explicitly copies
`movement_id`, `warehouse_id`, `product_id`, `units`, `event_day`, `movement_type`,
`source_modified_at_utc` and `source_row_version` unchanged by column name. This
is a discoverable statement, not name-similarity inference. It is not yet
projected into an approved enterprise context or an executable application layer.

## Positive reader finding and the accounting gap

Reader `investigator-reader@skynwhy.com` used its existing isolated account and
audience, without elevation. All three requests returned HTTP 200:

- generic item job-instance detail;
- Copy Job-specific instance detail;
- generic item history list, now containing the completed instance.

The two details returned the following complete business fields (the receipt
also contains request paths, identities and response hashes):

```json
{
  "id": "0a40d708-af1d-43fd-906b-073b0fda7f75",
  "itemId": "57e128c3-6ba0-4aaf-9464-81164ecdc782",
  "jobType": "CopyJob",
  "invokeType": "Manual",
  "status": "Completed",
  "failureReason": null,
  "rootActivityId": "1770bfe4-82cd-44b0-9817-46a3cba83f8b",
  "startTimeUtc": "2026-10-03T23:46:11.4014224",
  "endTimeUtc": "2026-10-03T23:46:43.9772431"
}
```

Neither detail nor history contains rows-read/written, capture bounds or per-table
activity accounting. Completion is established; delivery completeness is not.
Source publication previously observed 360 movements and 7,661 units. Those are
source observations, **not** this Copy Job's own row accounting; they cannot fill
its missing metrics. No destination quantity or source boundary was compared.

Microsoft documents the row metrics in the
[Copy Job monitoring panel](https://learn.microsoft.com/en-us/fabric/data-factory/monitor-copy-job)
and in `CopyJobActivityRunDetailsLogs` in a
[workspace monitoring eventhouse](https://learn.microsoft.com/en-us/fabric/data-factory/copy-job-workspace-monitoring).
Publisher workspace listing at this checkpoint contained no Eventhouse or KQL
Database. Portal-panel metrics have not been tested here; absence from these
three REST responses is not a claim that the reader cannot access them anywhere.
The current plan says not to silently provision a monitoring database. No such
resource or new KQL audience was created. The fourth scenario's required load
accounting therefore remains a specific unresolved prerequisite, not an invented
or substituted finding.

## Native relation and metadata coverage

Publisher item relations returned HTTP 200 with exactly one Association from the
Copy Job to its destination lakehouse. The response contained no Datasource or
Azure SQL source relation. The binding's authority will therefore come from the
served definition plus exact managed-connection description, not a fabricated
native Datasource edge.

The destination SQL endpoint subsequently reported provisioning Success, ID
`fbbccea4-d943-4f58-b91f-e6cbcb912620`. That is provisioning metadata, not a
successful reader query or a served-snapshot report. The ordinary lakehouse table
listing returned HTTP 400, `UnsupportedOperationForSchemasEnabledLakehouse`,
`isRetriable: false`. Preserve it as a listing gap; use the existing bounded
OneLake schema-listing route in discovery rather than treating an empty listing
as a successful collection or retrying this operation.

## Cost, scope and recording

This checkpoint added 16 charged admissions: 12 metadata requests and four
estate mutations (managed connection, lakehouse, definition update, one load).
There were five POSTs, one of which was the read-only getDefinition operation.
The publication ledger helper originally classified non-GET requests as
`mutation_requests`; an appended accounting correction records the semantic
split without editing that row.

Part B: 17 to **33 of 120** charged admissions. Ordinary rolling window observed
181 to **197 of 300**. Counters, allowance, diagnostic cap and credits unchanged;
failed preparations from earlier checkpoints remain charged. Zero investigation
planner, intake, judge or synthesis calls; zero diagnostic reads in this checkpoint.
Every request is governed before dispatch; responses and failures are sealed locally.

One Copy Job executed for **32.5758207 seconds** between its reported start/end.
These times do not expose billable optimization resources or capacity charge.
At the documented full-copy rate, cost is `1.5 ? optimization-resource hours`,
plus SQL/storage/transfer work. If one resource were billable for that entire
elapsed interval, it would be about 0.01357 CU-hours; resource count and actual
billable duration are not established, so that is not an actual charge or a
cash estimate. See [Copy Job pricing](https://learn.microsoft.com/en-us/fabric/data-factory/pricing-copy-job).
Only one isolated destination was written, with no downstream Spark work or
new schedule in this checkpoint.

The config raw hash remained
`4362a6c7d6bb3ed7ebd58aa78e9bb0159790b42edd76c6ae30320c4beb0e4c5e`;
its normalized approval digest remains
`19e2ef0b0b5cb6bfd8df38c5fded6c1eaac40718b3926248ac62c61abf0cf8b6`.
No new context or re-approval happened here. The prior 94-operation broad scan
predates these artifacts; it cannot certify them. A new scan must fit the
remaining 87 Part-B admissions alongside probes/runs, use honest scoped coverage,
or receive a separately reviewed budget decision. Do not bypass the approval gate.

## Remaining Part B

Integrate bounded connection/producer metadata, faithfully compile the application
quantity and its self-report, record approved context/configuration, implement
source capture/delivery producers with their evidence gates, and author four
scenarios plus the unchanged family E. No B3 run has been attempted. The declared
but unreachable source must stop at named Bronze, show actual load accounting
if obtained and hand off to the application owner; it cannot claim latency/gap
without an application read. Equal aggregates alone cannot establish an individual
expected record's presence or absence.

No engine bytes changed in this evidence PR; prior freezes remain invalid.
The existing literal-seeded baseline and historical runs remain unchanged.

## Sealed local artifacts

Artifacts under `.local/round-two-20261003/` are not committed.

| File | SHA-256 |
| --- | --- |
| ingestion-estate-preflight.json | `880f1062796c31c4a416c3574d0a4f472b83f03ccfe6379888b5e58e6d26fa16` |
| managed-source-connection.json | `a30d8322b8a9ebd51f39112f179e446f6b5a3862f79a7162139486b229038aef` |
| copy-job-publication.json | `ed97b19c86ebe0d5211b3b4aba4b0aea762f44de7b45a0bdaafe786150e27c78` |
| copy-job-first-load.json | `6a3deab0fc4fd386a04ee3ce7c7810fd7316d300752a2e1c81580333fac2e3b0` |
| copy-job-post-load-metadata.json | `c2a6853299dccbf03b05865283fc0c99597daa1135d4140a35819c51f86bf482` |
