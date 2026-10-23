# Round 22 reversible scenario controls

2026-10-23. Status: three failed-job controls were applied, observed as real failures, and restored on2026-10-23. None is a scored engine pass. Expectations and the dev/held-out split must be sealed before engine admissions.

## Failed-job controls

Use the existing publisher, existing pipeline, existing Script connection and database. The existing fixture builder now exposes `PipelineFailureScenario`: it saves the exact served definition, adds one fixed `THROW 51022` Script before all original root activities, and reads back the served definition. All original roots require that activity to succeed, so their data work cannot start. No SQL data, permissions, identity or connection is changed. A real triggered job's retained failed status/error, not an inserted ledger row, establishes the scenario.

| Planned case | Estate | Existing pipeline | Current evidence | Restoration |
|---|---|---|---|---|
| failed-fixture-load | fixture | b4871498-bd35-45be-916c-9a642568012c | Real failure and reader collection confirmed; original definition restored | Restore exact original definition; read back semantic hash |
| failed-billing-transform | billing | 76c60248-b830-433b-9880-90593da28e7e | Real failure and reader collection confirmed; original definition restored | Same |
| failed-billing-load | billing | fc8438fd-2c18-4196-9191-33e26481e2e0 | Real failure and reader collection confirmed; original definition restored | Same |

The fourth retained pipeline, billing continuation62eb1a7f-19c2-466f-85ec-cda6bc231fb9, is metadata readiness only. No fault is planned there yet.

Before applying: retain original bytes/hash, target scope, publisher identity, journal keys, and a durable restoration recipe. After an uncertain mutation, inspect the same operation/journal; never dispatch a blind retry. Restoration refuses an unexpected concurrent definition. Failed job history remains; it is never erased or rewritten. A normal baseline run, if required after restoration, is a separate recorded control.

Use ordinary remaining monthly requests for planned controls/restorations, reported as controls rather than diagnostic probes; do not consume the protected95-request emergency reserve. Every physical dispatch still goes through the existing shared governor. The investigator and scanner perform no mutation.

Four offline regression tests cover root blocking, unchanged connection/input, exact restoration and no-op restoration, concurrent-change refusal, and refusal to invent a Script connection. The broader existing fixture-control/apply/rebuild suite also passed21tests during preparation.

## Other classes

Missing data, stale refresh, waiting on a job, insufficient history, access mismatch, design-consistent differences, not-found and blocked-source controls are still pending. There is no claim of three real cases per class,60 independent tickets, or a sealed scored set. No synthetic runtime proof or fabricated job history may fill this gap.

## Documented control surface

Microsoft documents [getting a pipeline definition](https://learn.microsoft.com/en-us/rest/api/fabric/datapipeline/items/get-data-pipeline-definition), [updating it](https://learn.microsoft.com/en-us/rest/api/fabric/datapipeline/items/update-data-pipeline-definition), and the [definition parts](https://learn.microsoft.com/en-us/rest/api/fabric/articles/item-management/definitions/datapipeline-definition). These are publisher controls, not additions to the investigator allowlist. Long-running operations retain their original operation identity.

## Observed failed-job receipts

All three fixed faults returned the named controlled error2011. Existing investigator collected matching FAILED job IDs and error messages into the fact ledger: fixture2physical requests; billing4physical requests, each within the unchanged manual4request allowance. Full exact job errors, fact IDs, reader provenance, seals and original/restored hashes are in docs/runs/round-twenty-two-failure-controls.json. Original data activities were blocked; no history was removed. Two local control-reporting stalls were preserved and recovered; one conservatively charged original reservation remains RESERVED, not released or silently settled by another worker. No fault definition remains applied. Other verdict controls remain pending.
