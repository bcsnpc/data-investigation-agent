# Bronze: offline diagnosis before the unified runner

2026-10-21. This audit made zero estate, API or model calls and changed no
identity, permission, recorded capture or runtime configuration. The Round Twenty
build-phase decision supersedes the older attempt limit; that older result stays
recorded as it happened.

## What the saved failure establishes

The retained verification tape has SHA-256
`e47da8adbde93ac29737d2498d2466f3052020cfc2c1ae191b1853527bf864a7`.
Event indexes below are zero-based indexes into its `events` array. The adjacent
successful Silver request is event 677; its native result is event 697. The failed
Bronze request is event 720; event 721 returns exactly:

```json
{"error":"ManagedSqlReadFailed","stage":"connect","error_number":18456,"error_kind":"SqlException","sqlstate":"28000"}
```

This failed before the identity query, permission guards or compiled quantity
executed. The different quantity expression cannot explain a connection-stage
failure. The earlier four-request follow-up cannot settle this question: its
result and partial journal were lost during operator capture finalization.

## Field-by-field comparison

| Field | Successful Silver | Failed Bronze |
|---|---|---|
| SQL server | `i4iptx6c5nlundn6llzsrvlxqa-tggz6fdgdqfevfreown6aav3ma.datawarehouse.fabric.microsoft.com` | identical |
| Explicit database / initial catalog | `warehouse_silver_e1b8e1` | `warehouse_bronze_e1b8e1` |
| Lakehouse item | `ba24d52c-fcf9-4f1f-a377-f4d38547d887` | `09ba0ef9-7342-4179-a49e-1fc8adf48d82` |
| SQL endpoint item | `6cabd22c-26ec-4c98-8318-834011c1e0b3` | `7050f705-e595-4708-b62b-1836dac30741` |
| Authentication mode | `federated_reader` | identical |
| Application | `531419ef-1610-415a-b8bf-01a4b6aad751` | identical |
| Resource-tenant principal | `439ceb25-d200-4f02-95cf-4b1318faca62` | identical |
| Resource tenant | `dff91047-ebc2-4657-8dbe-5af328d57780` | identical |
| Managed identity / home tenant | `21e3405b-57e9-4581-834e-971b465f80ec` / `aeb4d0a9-e637-4a7e-8efc-63cf0c3827df` | identical |
| SQL token scope | `https://database.windows.net/.default` | identical code path |
| Driver / port | ODBC Driver 18 / TCP 1433 | identical |
| Encryption / certificate | `Encrypt=yes;TrustServerCertificate=no` | identical |
| Intent / connection | `ApplicationIntent=ReadOnly`, autocommit, pooling disabled | identical |
| Connect / statement / worker timeouts | 30 / 30 / 150 seconds | identical |
| Object allowlist | `[dbo].[stock_movements_e1b8e1]` | identical |
| Parameters | `@p0="1"`, `@p1="360"` | identical |
| Result contract | maximum 21 rows, columns `sum`, `count` | identical |
| Query | Sum and count of the retained movement key range | Additional retained DISTINCT/grouping expression before the same key-range aggregate |

Comparing every top-level field of those two worker payloads produces exactly
two differences: `database` and `query`. All sixteen SQL worker payloads in this
capture use the same federated application; none uses an old SQL login or user
sign-in cache. Silver's native result is `sum=64980`, `count=360`, with
`read_only_verified=true` and a VALUE_QUERY surface report naming
`warehouse_silver_e1b8e1` and the investigator application in the Fabric tenant.
Those values are a key-range witness, not the family A units total.

The worker obtains the SQL token before calling `connect`. The federated provider
checks its `aud` against `https://database.windows.net`, `tid` against the declared
Fabric tenant, `oid` against the resource-tenant principal, and `appid`/`azp`
against the application. A failed check refuses before SQL connection. The
recorded `stage=connect` is evidence that this path reached connection after
those checks; tokens and their raw claims are intentionally not retained, so this
is not an independent historical JWT dump or signature validation claim.

## Database-name uncertainty, explicitly corrected

The endpoint receipt SHA-256 is
`b2705269319477d4e7f52e0ce307d531135af28524218f4ff56decb7b380ccd3`.
Its Lakehouse responses provide `sqlEndpointProperties.connectionString`,
`id` and `provisioningStatus=Success`. They provide **no `databaseName` field**.
The discovered SQLEndpoint metadata supplies a `displayName`, also
`warehouse_bronze_e1b8e1`; it does not independently attest the actual served
database name. The adapter currently selects `matches[0]['name']` as the catalog
in both `code_verification.resolve_objects` and the declared-quantity walk.

Consequently, the previous statement that the Bronze database name was confirmed
by endpoint readback was too strong. Its item identity, server and display name
were confirmed. Silver's same naming convention is validated by its successful
query-bound `DB_NAME()` report. Bronze's is not yet validated. There is no saved
native property justifying a different catalog value, so this audit does not
replace it with a guessed GUID or a different display name.

The October 13 owner control read confirms the investigator already has Viewer
on workspace `149f8d99-1c66-4a0a-9624-759be002bb60`, which contains both items.
No missing role has been established. The application was already initialized
well enough to query Silver and Gold. The saved evidence does not establish
whether Fabric required an additional per-item initialization, a transient
propagation/reachability condition, or a different served catalog for Bronze.
No permission change follows from any of these hypotheses.

## Executable next step

Run the existing compiled Bronze quantity request through the new `dia run`
probe route, using the same federated reader, server and explicit catalog. Its
native query-bound surface report and read-only guards must be preserved. Retry
transient 18456 under the standing build-phase policy, preserving each result.
A successful result settles the database-name and reachability uncertainty; a
new connection failure remains a connection failure, never a finding about data.

Prepared local runner inputs are
`.local/round-twenty/bronze-probe-input.json` (the exact event-720 request and
public connection coordinates) and `bronze-offline-comparison.json` (the two
payloads, adjacent result/error, event indexes and source hashes). These are
preparation artifacts, not newly collected evidence or another one-off launcher.
If connection still fails, the next bounded control is the existing
`fabric_sql_surface.self_report` operation, whose SQL is only
`SELECT SUSER_SNAME() AS login_name, DB_NAME() AS database_name`, followed by a
reader metadata lookup of the exact declared Lakehouse if needed. Do not switch
identity, widen scope, or use the SQL endpoint GUID as a catalog without evidence.

This audit found no justified executable configuration correction and therefore
adds no speculative production patch or artificial regression test. The actual
runner/capture regression tests belong to Part A; the live outcome belongs to
Part B after that runner executes.
