# Billing tester identity scope change ? owner approval 2026-10-09

Chaitu explicitly approved under CLAUDE.md ?8: create a contained Entra user for investigator-reader@skynwhy.com in billingapp on sql-orderops-9696025.database.windows.net; add db_datareader only; no other role, write, DDL, other database, or new admin-credential location. Applied 2026-10-10 UTC (2026-10-09 America/Chicago), using the existing DPAPI SQL-owner path as pocsqladmin. The administrator was used for before/grant/after controls only. Reader verification used the existing isolated Azure CLI profile .local/azure-reader-sql, SQL-audience token in memory/stdin only, account and tenant checked and object ID 8a582d2a-ecb4-4320-bf72-75a529a0d382 matched. No admin credential or token was copied to the tester folder or a new store.

## Exact grant

The existing reader's token establishes its Entra object identity. The contained user uses Microsoft's documented SID/TYPE syntax, avoiding a directory lookup or any additional Graph grant. [CREATE USER documentation](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-user-transact-sql?view=sql-server-ver17).

```sql
SET XACT_ABORT ON; BEGIN TRANSACTION; IF DB_NAME()<>N'billingapp' THROW 50000,'Wrong database',1; CREATE USER [investigator-reader@skynwhy.com] WITH SID = 0x2a2d588ab4ec2043bf7275a529a0d382, TYPE = E; ALTER ROLE [db_datareader] ADD MEMBER [investigator-reader@skynwhy.com]; COMMIT TRANSACTION;
```

Only billingapp was addressed. No server login, server authentication setting, other database or other user's permission was changed. Creation automatically records CONNECT/GRANT for this contained user; that permits connecting, not writing or DDL. Public-role membership is implicit, not a newly assigned role.

## Before and after

Before: no principal, no role memberships, no explicit permissions for the account.
After:
```json
[
  [
    {
      "sid": "0x2A2D588AB4EC2043BF7275A529A0D382",
      "name": "investigator-reader@skynwhy.com",
      "authentication_type_desc": "EXTERNAL",
      "type_desc": "EXTERNAL_USER"
    }
  ],
  [
    {
      "role_name": "db_datareader"
    }
  ],
  [
    {
      "class_desc": "DATABASE",
      "major_id": "0",
      "permission_name": "CONNECT",
      "state_desc": "GRANT"
    }
  ]
]
```

The grant returned COMPLETED. The first before-listing attempt returned SQL40613, database unavailable. It sent no grant and remains preserved. One resumed attempt completed before/grant/after; no counter refund or limit increase. An earlier local timezone preflight failed before dispatch (zero requests), also preserved.

## Actual reader verification ? NOT verified

SELECT attempted:
```sql
SELECT DB_NAME() AS database_name,SUSER_SNAME() AS sign_in,USER_NAME() AS contained_user;
SELECT TOP (1) account_id,account_name FROM app.accounts ORDER BY account_id;
SELECT HAS_PERMS_BY_NAME(N'app.accounts',N'OBJECT',N'SELECT') AS can_select,HAS_PERMS_BY_NAME(N'app.accounts',N'OBJECT',N'INSERT') AS can_insert,HAS_PERMS_BY_NAME(N'app.accounts',N'OBJECT',N'UPDATE') AS can_update,HAS_PERMS_BY_NAME(DB_NAME(),N'DATABASE',N'CREATE TABLE') AS can_create_table,HAS_PERMS_BY_NAME(DB_NAME(),N'DATABASE',N'ALTER') AS can_alter_database,HAS_PERMS_BY_NAME(DB_NAME(),N'DATABASE',N'CONTROL') AS can_control_database;
```
Result: failed at login, SqlException18456: "Login failed for user '<token-identified principal>'. The server is not currently configured to accept this token." No billing row was returned. This does not establish a denied SELECT permission.

UPDATE attempted separately as the same reader:
```sql
SET XACT_ABORT ON; BEGIN TRANSACTION; UPDATE app.accounts SET account_name=account_name WHERE 1=0; ROLLBACK TRANSACTION;
```
Result: same SqlException18456 at login. The statement did not execute. This is not the requested write-permission denial and does not verify read-only operation. WHERE1=0 and rollback ensure no row change even if a future successful connection unexpectedly permits the statement. No data mutation occurred.

The contained grant remains applied. Server authentication configuration was not changed: that is outside this database-only permission decision. The tester README therefore says grant applied but verification blocked, not verified. No admin/owner fallback is offered to the tester.

## Collector compatibility

The existing application-source metadata/quantity path accepts sql.auth.mode=dpapi_file only (scripts/metadata_config.py), and uses the configured orderops_investigator SQL credential. Fabric SQL's separate Entra profile does not change that application-source contract. This new Entra grant does not authorize orderops_investigator. Under the current path, billing source collector verification requires its own separately human-approved read-only billingapp grant for orderops_investigator. No such grant was taken. Alternatively, supporting and configuring Entra for application-source collection would be separate work and still require fixing this sign-in refusal; neither was done. Billing manifest/discovery approval remains pending.

## Receipts and usage

Original preflight: .local/round-ten-20261007/billing/tester-reader-grant-preflight-failure.json.
Initial unavailable connection: tester-reader-grant-receipt.json (one physical request).
Successful grant / blocked SELECT: tester-reader-grant-resume-receipt.json (four physical requests), seal faec7b31cf3bb62bd3e55d41d4dc5526f78876029119c79913b22b51f5faa609.
UPDATE verification: tester-reader-update-verification.json (one physical request), seal b8c7afe4fb520288a6b49b489bf5aa5c2807314ae094a60fe0067849ae08769d.

Total six physical controls, zero diagnostic investigation reads, zero model calls. Pot1117?1123/1500; restoration reserve95 unchanged, ordinary remainder282. Rolling allowance3000 unchanged. Exact receipt files remain local, with per-control ledger entries; no tape/oracle/defect/evidence copied to the isolated tester workspace.
