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
