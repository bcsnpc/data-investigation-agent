# Runtime SQL identities (DB-002)

Implemented in development on 2026-09-12 for `ordersops`.

| User | Role | Access |
|---|---|---|
| orderops_app | orderops_app_role | SELECT, INSERT, UPDATE on nine business tables; SELECT and INSERT on audit_log |
| orderops_fabric | orderops_fabric_role | SELECT on the ten source tables, including audit_log |
| orderops_investigator | orderops_investigator_role | Same source reads plus VIEW DEFINITION on app schema |

The business tables are customers, products, orders, order_lines, payments,
shipments, shipment_lines, refunds and refund_lines. No runtime user can delete
source records. The app cannot edit/delete existing audit rows. Runtime users
cannot write dataset_runs, create tables/views/procedures, alter users/roles,
alter the app schema or execute procedures in that schema. Runtime roles have
no dbo ownership or fixed administrative role membership. Explicit table grants
do not automatically expose future tables.

These are Azure SQL contained database users, not enterprise Entra app
registrations. Connections must specify the `ordersops` database and use TLS.
Enterprise Fabric API identity/workspace configuration remains separate work.

## Provisioning and credentials

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File infra/scripts/Initialize-RuntimeIdentities.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File infra/scripts/Test-RuntimeIdentities.ps1
```

Provisioning uses the existing admin credential only for DDL and grants. It
generates distinct cryptographic random passwords, writes Windows-user-encrypted
PSCredential files under `.local/runtime-credentials/`, and binds passwords as
SQL parameters. Passwords are not printed or committed. An application lock and
transaction protect role/user setup. Repeating setup reuses saved passwords;
existing users with missing local credentials cause an error instead of silent
rotation. Saved credentials may remain after a failed SQL transaction so a retry
can reuse them. The directory is ignored by Git.

Credential filenames:

```text
.local/runtime-credentials/orderops_app.credential.xml
.local/runtime-credentials/orderops_fabric.credential.xml
.local/runtime-credentials/orderops_investigator.credential.xml
```

`RuntimeSql.Common.ps1` provides `Open-OrderOpsConnection` for local scripts.
It opens an encrypted SQL connection with one of these credential files. Future
hosted services should receive the appropriate credential from a secret store;
these Windows-encrypted files are local to the Windows user/machine.

## Live verification

The test signs in separately as each user and checks:

- Read access to all ten source tables.
- INSERT/UPDATE/DELETE permission matrix for every source table.
- Real app customer/audit inserts and order update, rolled back.
- The same write operations rejected for both readers.
- Audit modifications, deletes and manifest writes rejected.
- CREATE TABLE rejected and administrative/execute permissions absent.
- Investigator schema metadata and order-column discovery available.

All 152 checks passed. Test writes are wrapped in transactions and rolled back,
so the 100,000-order baseline remains intact. A second provisioning run followed
by the same tests verifies credential reuse and repeatable setup.

This is database authorization, not complete application business validation.
The future portal must enforce lifecycle/amount rules and atomically append
audit events. Direct table UPDATE privilege does not itself guarantee that an
audit event is written. Stored-procedure-only writes can be adopted later.

Microsoft references: [contained users](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-user-transact-sql),
[schema permissions](https://learn.microsoft.com/en-us/sql/t-sql/statements/grant-schema-permissions-transact-sql).
