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

## Corrected cloud replay and preparation, 2026-10-13 04:15 UTC

Corrected shard4 execution `job-dia-worker-mftupru` succeeded,04:07:23--04:08:18 UTC. Its private result SHA256 `c0aaf438f7f0ea78e8e068102d884eb5758fa9de5d3f9654f5e6ec32c0db1d83` reports1/1 exact historical replay, zero child network/estate/model requests. All eight selected tapes now have a passing cloud replay; the original simultaneous cohort remains7/8. The initial result fetch was early (404 BlobNotFound); the later result succeeded. The optional diagnostics blob was absent because no failure occurred, and its404 is retained as a fetch error, not a replay failure. No original or expected bytes changed.

The frozen334c3ac full regression passed **4,047 tests**,46 skipped and1,414 subtests in489.22 seconds with four workers. Subsequent trusted configuration bootstrap/model-key-channel fixes have34 focused tests and32 subtests; a first invocation named a missing test module and ran nothing, followed by the successful corrected selection. Image548cc57 passed all eight network-disabled CI shards and was published by workflow38345093002.

Prepare-only cloud execution `job-dia-worker-3togv38` started04:11:51 UTC on that immutable image. It downloads audited definitions, prepares a private approval candidate and scans output; it cannot publish the catalog, query estates or call a model. Temporary2vCPU/4GiB supplies scratch headroom; the default job size remains unchanged. At its1800-second maximum this is USD0.108 before free allowances, within the recorded monthly compute envelope. Verify must use the same image and the reviewed candidate hash. No investigation is claimed from preparation.

Preparation completed04:14:29 UTC, status PREPARED_NOT_PUBLISHED_NOT_READY. Its output ZIP SHA256 `d3a4edd4c83b70f16f986fe47b88486d4f70bbbbf96e3cbf0ad69501524dd4fa` was read back,104,559,651 compressed bytes/928,334,409 expanded. Review confirmed825 retained asset IDs/content hashes unchanged, prior model context history preserved, and the same model/workspace/native target. Candidate SHA256 `c7983de8a98d2c2128d4dee56e2a6faa387148ac7f7f221f21e4a794a3057c97` explicitly re-enables only the original model for fresh cloud verification. This is an operator application of the owner's migration/demo instruction, not a new estate permission or a readiness declaration.

New scan approval `ff93899e-2679-4fe4-8c16-37715a2054be`, context hash `b7d99f84fe511a84f8f9a756abe4de852db4fcba59d1e03a3e0e324831a38c10`; selected model context `1f1a4292-9866-48ce-a9ee-7161a28aff1c`; config hash `f75badf78fb5bea38308c990f17b2e39fb7251355fb3ae82371ef6cb980f3888`; image-local engine hash `740c166cf95256e71bcd56c5527586c34c33cf1fe18e8bea17aff8bf6bf28be9`. No metadata recollection occurred. At04:16:06 UTC, `job-dia-worker-974nsjk` was admitted with the exact reviewed candidate and same548cc57 image, at most40 verification probes, followed by one demo only if readiness and exact replay pass. Diagnostic12, pot4000, reserve95 and monetary bounds are unchanged.

## Live verification completed; replay gate refused, 2026-10-13 04:38 UTC

Execution `job-dia-worker-974nsjk` ran04:16:08--04:32:29 UTC. All18/18 binding witnesses were VERIFIED,40/40 verification probes used,89 physical requests settled,0 investigation diagnostics,0 model calls and0 pending reservations. The declared native boundary also compared equal on distinct surfaces; connection remains unattested and SNAPSHOT_UNVERIFIED remains. This establishes bounded reader witnesses, not the requested divergent demo finding.

The stage preserved `TapeError: TAPE_EVENT_DIFFERS:FINAL:AUTH_STATE`; its recomputed final identifies the earlier `TAPE_BUDGET_DECISION_DIFFERS`. The first is a secondary finalization mismatch. The stage is FAILED despite its successful artifact-publishing container exit. Exact replay did not pass, readiness was not published, and the one demo was not admitted. Original capture SHA256 `0e32b3a73c15385a302ad1c8595d5da68a73794836c5e7a5a601810a0499243e`; output ZIP SHA256 `40e000c724a210eae3b3769653baafce33c6b77a43b2b598c29e872c7e0980bf` (340,481,895 bytes) read back and retained unchanged. Offline diagnosis follows; no replacement reads or relaxed comparison are inferred.

Read-only PostgreSQL counter check at04:39:32 UTC: pot2,928/4,000, restoration95 remaining, rolling287/3,000, all89 new cloud reservations SETTLED. Shared model charge remains107,957,725 microdollars, zero new reservations or model spend. Historical reserved row remains unchanged. First local report command used the wrong Python environment and failed importing psycopg before any request; corrected existing llm-env report succeeded.

## Budget replay defect and new producer contract, 2026-10-13 04:47 UTC

The first mismatching operation is not a count serialization difference. PostgreSQL SharedUsage.reserve consumed one recorded clock; legacy SQLite reserve requested another CLOCK where the next sealed event was BUDGET_INPUT. Finally blocks obscured that with the budget/final mismatches. New captures explicitly declare FRESH_SHARED_USAGE_V1 and replay the actual SharedUsage algorithm against a private in-memory repository, recalculating every decision and retaining all original comparison rules. Changed decisions and session ownership still refuse. The old548 capture is not relabelled, amended or approved under the new engine. Fresh preparation and reader witnesses are required.

Integrated focused check:39 PASS,26 inherited opt-in backend tests skipped,4 subtests. A separate first-error/ordinary-capture/stage check passed6 tests and2 subtests. The frozen60c741a full suite is running. Engine bytes changed; previous freeze invalid. Fresh input package865c52999c3c4c5de2a6cc5fa9107525f4678ae3796f34eefee98e0389d702c0 (52,309,820 compressed bytes) reuses the audited retained definitions and latest published-model catalog from immutable verify01 output; no previous verification approval transfers. Private upload/readback passed at04:43:48 UTC, zero estate/model calls.

The same backend mismatch applied to future workspace tapes. New OWNED_SHARED_USAGE_V1 captures seal worker ownership and baseline reservation owners, preserve initial nonzero counters, and journal external deltas for snapshots as well as admission. Marked replay constructs its governor under the active tape to prevent contacting live state. An actual synthetic workspace sequence covers intake, preview, creation, investigation and synthesis; foreign reservations remain unowned. Old workspace tapes retain their original contract. These are recording corrections, not intake behavior changes.

Frozen60c741a complete regression:4,055 PASS,46 skipped,1,416 subtests in538.67seconds. Subsequent workspace changes have separate focused verification. Cloud image CI now includes the new shared-backend and first-error tests with networking disabled. The first sharding test failed because it assumed exactly eight modules; corrected conservation asserts all ten modules appear once across eight nonempty shards. Corrected worker/shared tests:8 PASS,2 subtests.


## Fresh preparation and bounded verification, 2026-10-13 05:08 UTC

Image `e646f7ecf948985f19351506f3c5a9ed75efea6c` passed all eight network-disabled cloud CI shards (workflow38349022027). The complete synthetic shared workspace regression explicitly forbids acquiring configured live state during replay:1 PASS,39 deselected; earlier integrated selection71 PASS,26 opt-in backend skips,10 subtests. This fixes controller bootstrap as well as governor construction; no old capture changes.

Prepare02 `job-dia-worker-y5z5e5e` completed05:00:52--05:03:38, zero estate/model requests. Output SHA256 `7a6bf35fb2cd29ba34c85cb56322fd2ea4c7bd56c1a8e723211255bc30e854af`,104,773,399 bytes. Reviewed candidate `ce77511e73352173fea7a25a29c2c6ef5544a04b98bb7931747cee36808f56e5` conserves825 retained asset IDs/content hashes and the existing model/context. New engine approval `b58c2daa3266b72f83908d11e4e3e295808f63ce91ff871732f5a97fb23658e5` transfers no prior witnesses. Config hash `f75badf78fb5bea38308c990f17b2e39fb7251355fb3ae82371ef6cb980f3888` is unchanged.

Verify02 `job-dia-worker-ybvd8u6` admitted05:08 UTC on that exact image/candidate. Admission checkpoint pot2,928/4,000, reserve95, rolling287/3,000, new model spend0;40 verification probes and one demo only after exact replay/readiness. Investigation diagnostic12 and all caps stay unchanged. The first failed verification remains immutable. No estate permissions or identities changed. Platform job controls are separate from diagnostic reads.

Frozen9634cef full regression completed:4,056 PASS,1 FAIL,46 skipped,1,416 subtests,771.83seconds. The strengthened replay test caught Ticket controller initialization acquiring live shared state before the replay scope. Fixe646f7e was already independently tested and is the running cloud image; the prior full failure is preserved. Full corrected-source regression is now running separately.


## Broader local content audit, 2026-10-13 05:11 UTC

Offline audit inspected1,146 loose tapes,1,596 inventory schemas/counts and1,959 of1,961 catalog schemas. Of20,121 decoded rows arrays, all9,652 above249 were accounting;141 tapes retain1,813 uninspectable protocol events and two catalog reads refused. This is bounded structural coverage, not universal no-bulk certification. A separate registered legacy ten-table source export contains1,410,699 rows/151,996,446 bytes; an unregistered duplicate matches allten file hashes. Both remain untouched and excluded from ordinary recording publication. Screenshot expiry has no implemented deletion consumer; projected cloud persistence/slim recording still refuse. Dated audit and limitations are committed. No permissions, source data, originals or caps changed; zero estate/model calls. Five audit and seven retention tests passed in the helper worktree.


Dated correction,2026-10-13 05:16 UTC: final code review narrows the earlier shared-state claim. Production SharedTickets persists smart-ticket state in PostgreSQL; claim-first state and runtime/investigation/image tables still write per-job SQLite retained in captures. A generic case-file repository exists but is not wired into a production writer. No successful migration of that full state is claimed. Existing workstation credential caches/mechanisms also remain; the approved cloud copies are in Key Vault, not a wholesale credential deletion/migration. Summary and storage documentation now state these implementation boundaries. Review was offline, zero estate/model calls.


At05:19 UTC, a full invocation accidentally used system Python and repository-wide discovery instead of project llm-env/scripts scope:4,155 passed,2 failed,3 collection errors. Four failures/errors were missing Azure dependencies; the fifth was colliding acceptance check module names. No code is changed for this operator invocation error. The documented suite is running again on the same e646 revision in the existing project environment. Original output retained.

The interim owner read-only budget report failed during SharedUsage.snapshot with `psycopg.OperationalError: consuming input failed: server closed the connection unexpectedly`; rollback then reported `the connection is lost`. It performed no mutations, estate reads or model calls. No counter total is inferred from that failed report; closing counters remain due.


## Part C close, 2026-10-13 05:30 UTC

Verify02 `job-dia-worker-ybvd8u6` ran05:08:29--05:24:53 UTC (984seconds). Live verification again completed18/18 witnesses,40/40 probes and89 physical requests, all settled, with zero investigation diagnostics/model calls. Its immutable tape SHA256 is `c6cad49ae8ab08f066157e3c349513daa5e5857a426c40db74abad6fc0d3998d`. Output ZIP301,321,267 bytes, SHA256 `30edf2399ce391b608f6ffaa8e61e5d5376fc665b8c4f4fc9018cdffc5c55243`, was read back and retained. Native-route limits remain unchanged.

Exact replay failed `TapeError: TAPE_EVENT_DIFFERS:BUDGET_INPUT:WORKER_READ`. Readiness was not published; the one family A cloud demo was NOT_RUN. The first mismatching request is now identified: live gateway normalization adds `require_read_only:true` to SQL worker payloads, while replay skips that live-only gateway branch and omits the field. A later wait/finalization masks the initial byte mismatch. This is a producer/replay payload asymmetry; it establishes neither a wrong value nor a successful replay. Offline correction is underway; neither original tape is amended or relabelled. No third verification/live attempt is admitted in this part.

Full corrected enginee646f7e:4,057 PASS,46 skipped,1,416 subtests in464.88seconds. Later native-pointer export correction has19 focused tests: new capture pointers are copied byte-identically under the stage output, missing/unsealed/unpublished captures listed explicitly, and primary failures retained. No database copy or estate/model request is added. It does not retroactively change either executed image.

Closing read-only repeatable-read PostgreSQL report at05:29:12 UTC:10,200 usage rows, two new sessions of89 SETTLED requests each, shared model opening/charge107,957,725 microdollars with no new monetary reservations. New model spend$0; pot3,017/4,000, restoration95 remaining, rolling376/3,000. The ordinary SharedState status helper stalled and was stopped as a read-only control; the direct consistent SELECT report made no mutations and avoids that advisory-lock path. The earlier connection-loss receipt is retained. All new verification reservations are settled. Part D documentation/audit continues offline.


## Offline correction after Part C, 2026-10-13 05:34 UTC

Committed managed SQL request construction now includes `require_read_only:true` before either live dispatch or replay, while the gateway still validates the statement and scope. Original failure02 begins with `TAPE_REQUEST_BYTES_DIFFER` at worker event12; only that added field differs. Cleanup consumed later events and previously obscured it. Tape now retains the first replay exception through cleanup and settlement.23 focused tests passed, including actual streaming capture/replay with the live gateway and subprocess forbidden during replay, plus rejection of changed request content. This changes engine bytes, invalidates earlier proof, and requires future fresh pinned verification. The originale646 tape stays FAILED. No third live attempt or model call follows.


CI caught an existing test that deliberately continued the same tape after a provider mismatch, then expected a different physical-request error. The new first-error preservation correctly retained the original failure. The test now checks that preservation explicitly and uses an independent replay instance to test physical byte equality; provider canonicalization and byte-exact physical comparison are unchanged. The old CI failures remain. Corrected provider/managed-worker/form/stage selection:29 PASS,3 subtests. No estate/model call or acceptance-file change.

Final-bee326f regression:4,071 PASS,2 obsolete first-error expectations failed,46 skipped,1,416 subtests in446.13seconds. The second expected cleanup to consume a CLOCK event after the first worker mismatch. Corrected test asserts the original failure and unchanged tape cursor instead. Both test corrections retain physical byte equality and forbid continuation after a failed replay. Focused18tests/3subtests pass. The production engine is unchanged by these test-only corrections; final clean suite follows.


## Final close, 2026-10-13 05:48 UTC

Integrated db3bed8 suite:4,073 PASS,46 skipped,1,416 subtests in449.65seconds. All eight cloud CI shards passed and GHCR publication succeeded (workflow38352575331). No live execution uses that corrected image in this round. All22 listed Container Apps executions are stopped. Closing SELECT-only repeatable-read report at05:48:18 preserves pot3,017/4,000, rolling376/3,000, restoration95, new178 physical reservations SETTLED, and zero new monetary reservations/model spend. D: free12,648,144,896 bytes, above10GB. Opening Part D free13,558,284,288; net change -910,139,392 bytes after retaining new evidence/working material, not a net cleanup saving. Reports and fixes are pushed to draft424; neither PR merges. The demo, full state migration, whole-estate onboarding and universal archive-content claim remain unearned as listed in the summary. No more admissions.
