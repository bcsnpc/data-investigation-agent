# HealthNet final readiness ? 2026-11-26

**READY_SEALED_TEST.** The ordinary business table `hn_billing.app.payer_plan_history` is readable through the engine's unchanged SQL permission guard. Its row count is **14**.

The owner's clarification limits the no-direct-history rule to the five system-versioned temporal history tables. `payer_plan_history` is non-temporal, with no temporal parent; its `_history` suffix does not make it a system history object. The earlier omission was an overbroad suffix exclusion in the smoke helper, not a demonstrated guard refusal. No engine, validator, permission or model change was made for this follow-up.

## Actual engine read

Linux Azure execution `job-dia-worker-bfp6ngi` **Succeeded**, using the already-qualified immutable image `sha256:8018ca9a08c8fdb0527525514cdbe7e0b683723abbc0f326dd4b9c79b235a3e9`, source `b7b3b2c9a562242ef39f422fc974f82c326c73f2`. An execution-only fixed diagnostic called `NativeQueries -> run_source_diagnostic.transport -> managed_sql_worker.execute`, with the real ODBC driver and managed-identity federation to the existing investigator application. There was no injected SQL connector, owner-token substitution, ticket or AI call.

```sql
SELECT COUNT_BIG(*) AS row_count FROM [app].[payer_plan_history]
```

The gateway admitted exactly that database/object, a two-row output bound and a 30-second statement timeout. The worker then established the calling identity, checked effective database permissions and this exact object's permissions before dispatching the count. It returned `read_only_verified=true`, `row_count=14`, database `hn_billing`, and principal `531419ef-1610-415a-b8bf-01a4b6aad751@aeb4d0a9-e637-4a7e-8efc-63cf0c3827df`. Two connection attempts returned serverless-resume SQL 40613; the engine's existing bounded retry succeeded on attempt three. The engine operation took 67.167 seconds including wake delays. These were connection retries, not permission refusals.

Ten individual physical-command slots were prepaid; seven metered slots were used. All ten reservations are SETTLED, zero open/uncertain. The monthly ledger conservatively counts the reserved bound, so all ten remain charged, including three unused slots; no historical counter was reduced. Final physical usage is 19,310/20,500 (INVESTIGATION 16,829/17,905; SCAN 2,430/2,500; RESTORATION 51/95 unchanged). No model spend. The scheduled job template, configuration and identity were read back unchanged.

## Readiness and limits

- `config/estates/healthnet.json` is `READY_SEALED_TEST`; the obsolete ?smoke partial? display name was corrected. Offline `dia estate validate` passes. It remains disabled, without an installation, so this task does not authorize or start sealed ticket execution.
- Source clinical/billing, raw and warehouse connectivity/count checks were completed in the earlier smoke. The previously deferred ordinary table now passes the real Linux engine path too.
- All three model totals matched their saved owner baselines through read-only XMLA: Operations Visits 249,575; Revenue Gross Charges 1,935,995,659.28; Productivity Visits 249,575. The preceding actual Linux engine XMLA proof returned `[ok]=1` and Azure Succeeded. REST Execute Queries remains unsupported for this RLS/service-principal combination; the configured engine transport is XMLA.
- All five active temporal history objects still use current-table `FOR SYSTEM_TIME` reads only. Their unexplained INSERT permission flags remain an open diagnostic item; no direct reads, DENY/REVOKE, exception or guard relaxation was introduced. Their current-table temporal counts passed earlier.
- Viewer-limited definition/refresh-history availability remains recorded in the smoke report; broader metadata completeness is not claimed. This is connectivity/sealed-test readiness, not a demonstrated investigation score.
- The 27 approved sealed HealthNet tickets and encrypted expectations are byte-identical to seal commit `6e800e15`. No sealed contents were opened; no HealthNet ticket, model call or injection was run.

The unchanged engine image has full-suite **6,239 passed / 54 skipped**, all **8 image shards green**, and **123/123 saved classifications unchanged**, as recorded in [the engine proof](healthnet-engine-dax.md). This config/report-only follow-up passed all 16 focused configuration/connection tests; it did not rebuild or alter the engine. [Receipt hashes](healthnet-final-readiness-evidence.json) pin this task's actual result, native execution, unchanged job readback, configuration validation and settled reservations. The earlier smoke receipts and sealed test files remain unchanged. PR #436 stays draft; no merge or tag.
