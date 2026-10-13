# Round Eighteen control and scope ledger

Owner approval: Chaitu, 2026-10-12 America/Chicago; execution 2026-10-13 UTC. Platform controls only; no investigation/model call.

## PostgreSQL worker grant

South Central US, `pg-dia-d5dd7d65`, database `investigator`. Existing managed identity `id-dia-worker`, object `21e3405b-57e9-4581-834e-971b465f80ec`. No password was created. The owner Entra administrator applied the prepared tool-state grant. This is platform-state write access, never permission to write estate data. Worker authentication has not yet been tested from the cloud.

```sql
SELECT rolname,rolsuper,rolcreaterole,rolcreatedb,rolcanlogin FROM pg_roles WHERE rolname=%s
```

Bound parameters: `["id-dia-worker"]`.

Result: `[]`.

```sql
SELECT * FROM pg_catalog.pgaadauth_create_principal_with_oid(%s,%s,%s,false,false)
```

Bound parameters: `["id-dia-worker", "21e3405b-57e9-4581-834e-971b465f80ec", "service"]`.

Result: `[["Created role for \"id-dia-worker\""]]`.

```sql
CREATE SCHEMA IF NOT EXISTS dia_state
```

Result: `{"rowcount": -1}`.

```sql
SELECT version,sha256 FROM dia_state.state_schema_versions ORDER BY version
```

Result: `[[1, "9b56f874eaa2c7cff725d7d9e1684bd81c0c84af7602aaa152be1df348bbc8f7"], [2, "4b505f6329b7425d758b623e2d7f4c9e3179197f89bbf78f67d20faa111b7cc9"]]`.

```sql
SELECT grantee,table_schema,table_name,privilege_type FROM information_schema.role_table_grants WHERE grantee='id-dia-worker' ORDER BY table_schema,table_name,privilege_type
```

Result: `[]`.

```sql
GRANT CONNECT ON DATABASE "investigator" TO "id-dia-worker"
```

Result: `{"rowcount": -1}`.

```sql
GRANT USAGE ON SCHEMA dia_state TO "id-dia-worker"
```

Result: `{"rowcount": -1}`.

```sql
GRANT SELECT ON TABLE
    dia_state.state_schema_versions, dia_state.state_migrations,
    dia_state.state_accounts, dia_state.state_documents,
    dia_state.state_reservations, dia_state.state_usage,
    dia_state.state_read_batches, dia_state.state_read_batch_runs,
    dia_state.state_read_allocations, dia_state.state_usage_acknowledgments
TO "id-dia-worker"
```

Result: `{"rowcount": -1}`.

```sql
GRANT INSERT, UPDATE ON TABLE
    dia_state.state_documents, dia_state.state_reservations, dia_state.state_usage
TO "id-dia-worker"
```

Result: `{"rowcount": -1}`.

```sql
GRANT UPDATE (violated) ON TABLE dia_state.state_accounts TO "id-dia-worker"
```

Result: `{"rowcount": -1}`.

```sql
GRANT INSERT ON TABLE
    dia_state.state_read_batches, dia_state.state_read_batch_runs,
    dia_state.state_read_allocations, dia_state.state_usage_acknowledgments
TO "id-dia-worker"
```

Result: `{"rowcount": -1}`.

```sql
ALTER ROLE "id-dia-worker" IN DATABASE "investigator"
    SET search_path = dia_state, pg_catalog
```

Result: `{"rowcount": -1}`.

```sql
SELECT grantee,table_schema,table_name,privilege_type FROM information_schema.role_table_grants WHERE grantee='id-dia-worker' ORDER BY table_schema,table_name,privilege_type
```

Result: `[["id-dia-worker", "dia_state", "state_accounts", "SELECT"], ["id-dia-worker", "dia_state", "state_documents", "INSERT"], ["id-dia-worker", "dia_state", "state_documents", "SELECT"], ["id-dia-worker", "dia_state", "state_documents", "UPDATE"], ["id-dia-worker", "dia_state", "state_migrations", "SELECT"], ["id-dia-worker", "dia_state", "state_read_allocations", "INSERT"], ["id-dia-worker", "dia_state", "state_read_allocations", "SELECT"], ["id-dia-worker", "dia_state", "state_read_batch_runs", "INSERT"], ["id-dia-worker", "dia_state", "state_read_batch_runs", "SELECT"], ["id-dia-worker", "dia_state", "state_read_batches", "INSERT"], ["id-dia-worker", "dia_state", "state_read_batches", "SELECT"], ["id-dia-worker", "dia_state", "state_reservations", "INSERT"], ["id-dia-worker", "dia_state", "state_reservations", "SELECT"], ["id-dia-worker", "dia_state", "state_reservations", "UPDATE"], ["id-dia-worker", "dia_state", "state_schema_versions", "SELECT"], ["id-dia-worker", "dia_state", "state_usage", "INSERT"], ["id-dia-worker", "dia_state", "state_usage", "SELECT"], ["id-dia-worker", "dia_state", "state_usage", "UPDATE"], ["id-dia-worker", "dia_state", "state_usage_acknowledgments", "INSERT"], ["id-dia-worker", "dia_state", "state_usage_acknowledgments", "SELECT"]]`.

```sql
SELECT has_schema_privilege('id-dia-worker','dia_state','USAGE'),has_schema_privilege('id-dia-worker','dia_state','CREATE'),has_schema_privilege('id-dia-worker','public','CREATE'),has_database_privilege('id-dia-worker',current_database(),'CREATE')
```

Result: `[[true, false, false, false]]`.

```sql
SELECT rolname,rolsuper,rolcreaterole,rolcreatedb,rolcanlogin FROM pg_roles WHERE rolname='id-dia-worker'
```

Result: `[["id-dia-worker", false, false, false, true]]`.

Control receipt SHA-256: `6c03e0c34590245c657e106d5b3b35b0ba9ed909878c7004fab8af30ee25f44c`. Original receipt remains local. Before: no worker role or table grant. After: login without superuser, role-creation or database-creation rights; state usage true, state/public/database CREATE false. No other database received an explicit grant. Existing PostgreSQL PUBLIC defaults are not an explicit worker grant.

## Owner credential-location and vault-role decisions, 2026-10-12

Chaitu approved keeping the test-estate identities unchanged and moving their existing credentials to the platform Key Vault. Client deployments belong in the same Entra tenant as Fabric so managed identity can be used directly. The existing quantity reader is an Entra user, `investigator-reader@skynwhy.com`, object `8a582d2a-ecb4-4320-bf72-75a529a0d382`, not a service principal. The owner then explicitly approved migrating only its scoped existing sign-in cache and using it in memory in the worker, with the same tenant, object ID and audiences. `investigator-code-reader` has Contributor for definitions and is never substituted for quantity reads. No new estate role or audience is authorized by this migration.

The first interactive `az login` did not open a browser. Device-code login was attempted; the owner supplied a screen saying authentication succeeded but resource access was denied. This is not evidence of a wrong password. The separate, retained Key Vault request establishes the actionable denial: `ForbiddenByRbac`, action `Microsoft.KeyVault/vaults/secrets/readMetadata/action`, owner object `c22c5e9b-5005-4a48-af98-51d614e6021a`, assignment not found, deny assignment null.

The owner explicitly approved Key Vault Secrets Officer for `leelamounika14@gmail.com` on `kv-dia-d5dd7d65` only if that data-plane permission was missing. The repeated request confirmed it. Applied at 2026-10-13T02:41:15Z (2026-10-12 America/Chicago):

```powershell
az role assignment create --assignee-object-id c22c5e9b-5005-4a48-af98-51d614e6021a --assignee-principal-type User --role b86a8fe4-44ce-4948-aee5-eccb2c155cd7 --scope /subscriptions/d5dd7d65-1b61-4025-b9f1-5f7b2f8d1ef9/resourceGroups/rg-dia-platform/providers/Microsoft.KeyVault/vaults/kv-dia-d5dd7d65
```

Before: no vault-scoped data-plane assignment; inherited Owner (two historic assignments) and Foundry User only. After: those unchanged plus Key Vault Secrets Officer on the exact vault, assignment `33e291aa-b860-41c4-9888-225c0ecda672`. Worker remains Secrets User, not Officer. Subsequent secret metadata listing succeeded and returned `[]`; this establishes owner metadata access, not that any credential has already migrated. Before/after local receipts contain metadata only.

## Credential relocation completed, 2026-10-13 UTC / October 12 owner date

The scoped reader caches were migrated at 02:47:32 UTC. Only Account, RefreshToken and AppMetadata sections were copied; each source contained exactly the declared reader account, tenant and client. AccessToken and IdToken were excluded. Original DPAPI files were unchanged. No credential value was printed, stored in a new local file, or included in a tape. The existing model provider key was copied in memory at 02:55:59 UTC; it was not regenerated. These one-time owner provisioning writes are separate from worker gateway reads.

| Secret | Immutable version | Existing purpose |
|---|---|---|
| `reader-pbi-existing-session` | `2d14a40d063c42f79cb57baa774f5943` | https://analysis.windows.net/powerbi/api/.default |
| `reader-sql-existing-session` | `d158c9c5f31a468b996f580aacc4a083` | https://database.windows.net/.default |
| `existing-model-provider-key` | `ad19c73a9041471abd06950224aba505` | Existing model provider, aoai-investigator-9696025 |

Worker value-read/refresh verification remains a separate pending check. Public configuration carries only these versioned references and identity IDs. Worker Secrets User scope remains the single vault.

## Platform control findings

Compute deployment 02 created the South Central US environment and worker job, both Succeeded. The overall deployment nevertheless failed when reapplying the PostgreSQL owner administrator: `AadAuthOperationCannotBePerformedWhenServerIsNotAccessible`. A subsequent read shows PostgreSQL Ready and the same owner administrator intact. No account or administrator was replaced. The Container Apps provider was still Registering; its CLI precheck refused commands despite the job existing. The documented ARM job-start API accepted the same owner request.

Cloud health execution `job-dia-worker-h44txra` authenticated as `id-dia-worker` to PostgreSQL (database investigator, transaction_read_only=on; two schema versions, five migrations, one account, 2,391 state documents) and Blob (immutable PUT201/GET200). Its Key Vault check failed before HTTP. A separate auth-plane control established the exact same tenant/object ID and Key Vault audience `cfa8b339-82a2-471a-a3c9-0fc0be7a4093`; the checker incorrectly required the URI spelling. The first diagnostic control failed before authentication with `ModuleNotFoundError: No module named investigator`; the corrected control retained only aud/tid/oid, never the token.

The interactive owner device flow was cancelled after the browser denial; CLI retained `AADSTS70016: Authorization is pending`. Existing owner CLI authorization still worked. The vault-specific approved grant resolved the demonstrated ForbiddenByRbac; no tenant/sign-in policy was changed.

## Cloud snapshot publication and local verification, 2026-10-13

At 03:12:18 UTC, the pilot's 237 content-addressed objects (25,200,488 bytes) were published immutably to the private `snapshots` container and all read back byte-for-byte. The exact two-method per-object gateway allowed 474 platform transport requests, zero estate requests and zero model calls. The one-time owner storage bootstrap credential stayed in memory. This is the previously audited four-file pilot, not conversion of all historic recordings. Local receipt: `pilot-cas-cloud-receipt.json`.

The eight selected historic tapes replayed locally with eight workers: 8/8 matched in 198.253 seconds. Their original bytes and historical engine revision were unchanged. The initial transit package was superseded before publication to remove unrelated Git history; cloud replay remains pending. Exact results and timings are local in `cloud-replay-pack/laptop-baseline.json`.

After the shared ticket mirror repair, the document-migration/mirror selection passed 16 tests, including six real PostgreSQL migration variants. Disposable test schemas were isolated from `dia_state`; estate and model usage were zero. The frozen 4377cbf full regression is running separately, not claimed passed yet.

## Durable cloud authentication proof, 2026-10-13

Platform health recheck `job-dia-worker-2oshp00` passed PostgreSQL, immutable Blob PUT/GET and Key Vault metadata. It used six platform controls including receipt publication, zero estate reads/models. Receipt SHA-256 `f0dda1cf92a6406060139761225ecaeeab1f0c5047cd854a26043f6eb4ca03f1`. The earlier failed check remains unchanged.

Auth-only execution `job-dia-worker-wynal6w` exited 0, but log retrieval failed first with `ErrorGeneratingAuthToken`, then `ExecutionReplicaNotFound` after replica cleanup. It is retained as successful execution without retrievable check detail. The repeat `job-dia-worker-5u7s0as` writes its sanitized result to private Blob. At 03:22:54 UTC both PBI and SQL refresh checks PASS: tenant `dff91047-ebc2-4657-8dbe-5af328d57780`, object `8a582d2a-ecb4-4320-bf72-75a529a0d382`, their original audiences. Model-key availability PASS; model API authorization was not tested. No secret values, tokens or updated cache are logged or written to disk. No new consent, identity, audience or estate permission.

The eight cloud historical replays completed at 7/8 exact matches; shard4 is a retained mismatch, not a pass. The initial wrapper retained counts but omitted private failure details; a diagnostic-only rerun of that shard will retain them. Every replay child reports zero network/estate/model requests; platform download/publication controls are separate. Each job temporarily used1vCPU/2GiB so the2.5GB estimated scratch fits [documented4GiB ephemeral storage](https://learn.microsoft.com/en-us/azure/container-apps/storage-mounts). The default job remains0.5vCPU/1GiB, no persistent scale change. Eight1800-second maximum executions bound compute at USD0.432 before free allowances, inside the existing40vCPU-hour monthly envelope.


## Storage and compute checkpoint, 2026-10-13 03:42 UTC

The frozen 4377cbf regression passed 3,983 tests, with 46 skipped and 1,407 passing subtests, in 796.43 seconds. The later catalog/cloud-reader and portable-worker changes passed 18 focused tests; this is a separate revision, not a claim that the old full run tested them.

Eight further tapes converted: all 32 reconstructed files byte-identical, all eight actual pinned-engine replays MATCHED. Their 1,958,359,736 original bytes add 23,394,768 bytes to the shared CAS; its total is now 48,595,256 bytes. Originals are preserved. Broad history conversion remains incomplete.

The diagnostic cloud replay still failed 0/1: `TapeError: TAPE_EVENT_DIFFERS:CLOCK:WORKER_SEND`. Investigation found Windows executable paths normalized differently on Linux, causing an earlier worker descriptor mismatch masked by error handling. The lexical-path fix changes no recorded events, statement bytes or expectations. Linux recheck is pending; original 7/8 and diagnostic 0/1 remain recorded.

Compute-only deployment `dia-platform-compute-only-03` succeeded after an explicit existing-PostgreSQL-host parameter prevented reapplying its administrator. Earlier deployment failure remains. Machine-readable What-If needed `--no-pretty-print`; its first wrapper parse failure changed no resource.

The separate 32-file archive batch failed on upload with `ServiceResponseError: ConnectionResetError(10054, An existing connection was forcibly closed by the remote host)`. No complete verified receipt was produced, and none of those originals was removed. The earlier 45-file verified archive and cleanup remain valid. Owner SDK hook auditing is in progress; do not infer exact transport counts from logical operations.

Read-only platform verification found graph nodes=0 and edges=0. The PostgreSQL model account retains opening107,957,725 microdollars, ceiling127,957,725 and protected10,000,000, violation0, no new reservations. This is platform state, not an estate query. The historical reserved usage row remains preserved. No new estate reads or model calls in this checkpoint; pot2,839/4,000, reserve95.

## Transport-accounting correction and archive completion, 2026-10-13 04:05 UTC

Dated correction to the pilot publication entry: Azure Storage SDK ignored the supplied per-call policy. Its 474 figure was inferred from logical operations, not a measured transport count. Content hashes and readback checks remain valid. The replacement transport wrapper gates and journals every physical dispatch, including range GETs, before sending. The next 228 CAS objects (23,394,768 bytes) produced **460 dispatched / 460 responses / 0 errors**, rather than the logical estimate of456. A nonfatal SDK streaming warning was retained; every object passed its readback check. See `docs/storage-sdk-transport-correction.md`.

The retried archive batch verified32 objects, 1,958,359,736 original bytes /201,505,574 compressed bytes, with192 dispatched/192 responses/0 errors. Manifest SHA256 `fec218210297fab73e25b04911603ae3065fb37a082a983f5a689c10d203259a`; receipt SHA256 `ab63bc1be01953c19e760c3dcd3ae4753a683ddc0cce2e5adc05e70d610e7389`. The approved PowerShell cleanup rechecked workspace containment, reparse points, sizes and hashes before removing only those32 files. Removal log retained; logical bytes removed1,958,359,736, not a claim about allocated disk bytes. D: free after cleanup14,078,382,080 bytes. The first connection-reset failure remains recorded.

Cloud shard4 portable-path attempt `job-dia-worker-9ns32l0` and first-error diagnostic `job-dia-worker-nuthqb3` each remained0/1. Private diagnostics exposed `TAPE_REQUEST_BYTES_DIFFER`: Linux configuration loading prefixed absolute Windows paths with the extracted repository path. Replay-only Windows path semantics now preserve those paths before request construction; no sealed event or comparison was weakened. A corrected Linux recheck remains due.

Audited cloud input package SHA256 `998d0203aa82498277e41ccd1d4a25c8c1dfc9d2a05928992afa0919a9430323` (47,305,616 compressed bytes,461,153,892 expanded,9 members) was published privately and read back at03:58:43 UTC. It contains retained definitions and bounded historical evidence, not credentials; credential caches remain memory-only. Cloud preparation and verification are separate, with candidate review before publication.

Offline retained-receipt preflight: fixture8 PASS/0 FAIL/24 MISSING; billing8 PASS/0 FAIL/13 MISSING. The first billing candidate failed schema validation and is retained; the corrected candidate uses the same approved reader and versioned credential reference. Neither estate is declared fully ready from these controls. Source334c3ac focused stage/path/capture/source checks passed13 tests and2 subtests. A first test invocation named a nonexistent file and ran no tests; corrected invocation above. Estate and model admissions remain zero, pot2,839/4,000, reserve95 unchanged.
