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
