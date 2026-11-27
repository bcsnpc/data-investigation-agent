# Scan benchmark

Owner approval: 2026-11-26, `scan-benchmark-estates.md`. Branch starts at PR #437
head `892be5612a855e7848b0566bbcd84d108b0c97b3`.

IN PROGRESS. No live scan score has been earned. Planned manifests are not
observations and are never used as discovery inputs.

Only new `sb_*` databases and `Scan Benchmark *` workspaces may be created.
No existing estate, frozen image, sealed test or remaining control is changed.
No model calls, new paid resource, merge or tag is authorized by this task.
New SQL databases must have `useFreeLimit=true`, exhaustion `AutoPause`,
inactivity auto-pause, and no paid continuation. Owner build identity is separate
from the investigator; grants are limited to these new estates and logged with
their revoke steps. Build and score one estate at a time.

Disk at start: C 74.0 GB, D 195.9 GB (decimal); floors 40/80 GB.
Cloud ledger at start: SCAN 2,430/2,500; investigation 17,701/17,905;
restoration 82/95; total 20,213/20,500. No limits changed. The small remaining
SCAN allocation bounds discovery; exhausted live work stops while offline work
continues. Owner metadata provisioning is not represented as an investigator
scan or an evidence-backed discovery result.

## Scores

| Estate | Deployment | Objects / columns | Lineage | Traps / permission gaps |
|---|---|---|---|---|
| A Wholesale | building | NOT SCORED | NOT SCORED | NOT SCORED |
| B P&C insurance | not started | NOT SCORED | NOT SCORED | NOT SCORED |
| C ERP | not started | NOT SCORED | NOT SCORED | NOT SCORED |
| D Education | not started | NOT SCORED | NOT SCORED | NOT SCORED |

## Sources and licences

- A: Microsoft's WideWorldImporters SQL sample, MIT, copyright Microsoft.
  Upstream: https://github.com/microsoft/sql-server-samples/tree/master/samples/databases/wide-world-importers .
  Record the exact source revision and any adaptations before deploying schema.
- B: owner amendment 2026-11-26 replaces Berka with independently generated
  property-and-casualty insurance. No downloaded data. Policies, versions and
  endorsements, coverages, premiums, claims, reserves, payments, agents and customers;
  uppercase cryptic SQL, four-level views, loading procedures including dynamic SQL,
  backups and a summary table beside transactions. No native lineage metadata beyond SQL.
- C/D: independently authored synthetic SQL and data; no SALT dataset or patient,
  student, employee or client records.

## Owner actions

Later clean-install test: a second Azure account and Fabric capacity, requiring
separate approval. Databricks estate E is outside this benchmark.

## First native SQL result (Estate A, SQL scope only)

On the same captured investigator metadata, schema scope repair changes objects from0/42 to42/42 and columns from0/451 to451/451. Generic static SQL analysis resolves17/17 parseable table/column edges with17/17 precision. Two build-time copy edges remain inferable-only and are NOT asserted as facts. There are89 remaining non-permission misses in this SQL-scope scorer, principally missing layer/authority/trap assertions; no overall PASS is claimed. Fabric definitions are published but not refreshed. Viewer definition reads return404 EntityNotFound on generic and typed paths while owner typed getDefinition succeeds, and refresh history returns403. No permission escalation or owner-metadata substitution. First harness TypeError was setup-only and is not scored as an engine defect; all15 native reads from the original plus repaired reader attempt remain charged, plus2 typed checks.

A resource IDs: workspace9e1701f5-da55-4f01-b2a6-6f211a36043b, modelc75215a8-b869-4072-82a0-20b5c7c69fe3, reportd50d6e77-e390-4eac-b159-3d5373100c87. SQLsb_wholesale uses free offer, AutoPause at free limit and60minute inactivity pause. Model refresh/connection and full Fabric manifest remain work in progress.

Source pin: Microsoft SQL samples26dc1258b431470f515775b8c98ae77e1d66e39a, MIT.37non-archive source table column shapes,1600seeded rows before copies and ETL. Adaptations: synthetic rows; original defaults/indexes/FKs/temporal generation omitted; computed sample columns materialized; no original load simulation. This is a small schema adaptation, not an untouched WWI install or a benchmark of every upstream procedure.
