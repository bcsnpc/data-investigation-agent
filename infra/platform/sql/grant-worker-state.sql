-- PREPARED ONLY. Run as the approved Entra database administrator, using psql.
-- Replace these explicit placeholders; no password is created or written.
-- Managed identity uses its OBJECT ID, not its client/application ID.
-- Reference: https://learn.microsoft.com/en-us/azure/postgresql/security/security-manage-entra-users
\set ON_ERROR_STOP on
\set worker_role 'dia-worker'
\set worker_oid '<DEPLOYED-MANAGED-IDENTITY-OBJECT-ID>'
\set tool_database 'investigator'

-- Section A: connect to postgres only for the Azure principal-binding function.
-- This creates a non-admin server authentication role, not a grant on postgres.
\connect postgres
SELECT rolname, rolsuper, rolcreaterole, rolcreatedb, rolcanlogin
FROM pg_roles WHERE rolname = :'worker_role';
SELECT * FROM pg_catalog.pgaadauth_create_principal_with_oid(
    :'worker_role', :'worker_oid', 'service', false, false);

-- Section B: only the one approved tool database receives data privileges.
\connect :tool_database
SELECT current_database(), current_user;
CREATE SCHEMA IF NOT EXISTS dia_state;
-- Apply the versioned SharedState migrations as the migration owner with
-- SET search_path = dia_state, pg_catalog before executing Section C.
-- Do not let the worker create tables or run migrations.

-- Section C: fail if migrations were not applied in the dedicated schema.
SELECT version, sha256 FROM dia_state.state_schema_versions ORDER BY version;
SELECT grantee, table_schema, table_name, privilege_type
FROM information_schema.role_table_grants
WHERE grantee = :'worker_role' ORDER BY table_schema, table_name, privilege_type;
GRANT CONNECT ON DATABASE :"tool_database" TO :"worker_role";
GRANT USAGE ON SCHEMA dia_state TO :"worker_role";
GRANT SELECT ON TABLE
    dia_state.state_schema_versions, dia_state.state_migrations,
    dia_state.state_accounts, dia_state.state_documents,
    dia_state.state_reservations, dia_state.state_usage,
    dia_state.state_read_batches, dia_state.state_read_batch_runs,
    dia_state.state_read_allocations, dia_state.state_usage_acknowledgments
TO :"worker_role";
GRANT INSERT, UPDATE ON TABLE
    dia_state.state_documents, dia_state.state_reservations, dia_state.state_usage
TO :"worker_role";
GRANT UPDATE (violated) ON TABLE dia_state.state_accounts TO :"worker_role";
GRANT INSERT ON TABLE
    dia_state.state_read_batches, dia_state.state_read_batch_runs,
    dia_state.state_read_allocations, dia_state.state_usage_acknowledgments
TO :"worker_role";
ALTER ROLE :"worker_role" IN DATABASE :"tool_database"
    SET search_path = dia_state, pg_catalog;

-- No CREATE, DELETE, TRUNCATE, ownership, default-table grants, public-schema
-- rights, graph writes, admin membership, or grants on any other database.
-- Existing PUBLIC grants are inherited PostgreSQL defaults: audit them below;
-- this script neither widens them nor alters rights belonging to other users.
SELECT rolname, rolsuper, rolcreaterole, rolcreatedb, rolcanlogin
FROM pg_roles WHERE rolname = :'worker_role';
SELECT grantee, table_schema, table_name, privilege_type
FROM information_schema.role_table_grants
WHERE grantee = :'worker_role' ORDER BY table_schema, table_name, privilege_type;
SELECT has_schema_privilege(:'worker_role', 'dia_state', 'USAGE') AS state_usage,
       has_schema_privilege(:'worker_role', 'dia_state', 'CREATE') AS state_create,
       has_schema_privilege(:'worker_role', 'public', 'CREATE') AS public_create,
       has_database_privilege(:'worker_role', current_database(), 'CREATE') AS database_create;
-- The last three fields must be false before the worker is admitted. If any
-- is true through an inherited/default grant, stop and request a scoped fix.
