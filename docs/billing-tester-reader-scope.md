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


# Dated ?8 continuation ? SQL-authentication fallback verified

Owner approval: Chaitu, 2026-10-09 America/Chicago. Execution: 2026-10-10 UTC. The new explicit decision authorizes billing_tester_reader as a contained SQL-authentication user, db_datareader only in billingapp; strong generated password only in Windows Credential Manager target dia-billing-tester-sql; removal of the unusable billingapp Entra user; and existing orderops_investigator in db_datareader in billingapp only. Previous failed Entra verification above remains historical evidence and was not rewritten.

## Diagnosis, read-only

A fresh reader SQL token was requested with resource https://database.windows.net/. Only aud and tid were recorded: aud=https://database.windows.net/, tid=dff91047-ebc2-4657-8dbe-5af328d57780. The existing ARM control identity listed the SQL server's administrators using the documented [List By Server API](https://learn.microsoft.com/en-us/rest/api/sql/server-azure-ad-administrators/list-by-server?view=rest-sql-2023-08-01). HTTP200 body was {"value":[]}, request ID d3a90e42-9263-4d1d-87e6-aca30fe44770. No administrator tenant exists to compare. Cause: no server Entra admin configured; audience is correct, and tenant mismatch is not established. This agrees with retained SQL18456 saying the server is not configured to accept the token. No token or authorization header retained; no server setting changed.

Diagnosis receipt .local/round-ten-20261007/billing/tester-auth-diagnosis.json, seal 7ac6db8bd1b53154d1b056ac1c59c09294ad716709f04bb375d47ffd0cccaeeb.

## Grants and removal

Existing SQL owner pocsqladmin used the unchanged existing DPAPI credential path, only for permission controls and the approved transaction. New tester password generated from 32 cryptographic random bytes with mixed character classes; Windows Credential Manager generic credential, local-machine persistence for the current Windows user, target dia-billing-tester-sql, username billing_tester_reader. Its only persistent local secret location is that Credential Manager entry. Values were loaded in memory as SQL parameters and never in files, logs, README, repository, ledger or reply. Existing admin and agent credentials were neither copied nor rotated.

A read-only existing-owner master.sys.sql_logins query returned no orderops_investigator login. Historical records identify it as a contained SQL account. Therefore the existing contained account username/password was reused in billingapp, with no server CREATE LOGIN, no change to its original database and no new credential. This is the approved existing agent account's database scope extension, not a new server identity.

Exact executed transaction template (parameter values intentionally absent):
```sql
SET XACT_ABORT ON; BEGIN TRANSACTION;
IF DB_NAME()<>N'billingapp' THROW 50000,'Wrong database',1;
DECLARE @new_user_sql nvarchar(max)=N'CREATE USER [billing_tester_reader] WITH PASSWORD = '+QUOTENAME(@tester_password,NCHAR(39))+N';';
EXEC sys.sp_executesql @new_user_sql;
DECLARE @agent_user_sql nvarchar(max)=N'CREATE USER [orderops_investigator] WITH PASSWORD = '+QUOTENAME(@agent_password,NCHAR(39))+N';'; EXEC sys.sp_executesql @agent_user_sql;
ALTER ROLE [db_datareader] ADD MEMBER [billing_tester_reader];
ALTER ROLE [db_datareader] ADD MEMBER [orderops_investigator];
ALTER ROLE [db_datareader] DROP MEMBER [investigator-reader@skynwhy.com];
DROP USER [investigator-reader@skynwhy.com];
COMMIT TRANSACTION;
```

Before: only investigator-reader@skynwhy.com, EXTERNAL_USER / EXTERNAL, db_datareader and CONNECT. Neither new SQL user existed.
After:
```json
[
  [
    {
      "sid": "0x010600000001006400000000000000004A1D8EE0988F9D44BF8146A747101D56",
      "name": "billing_tester_reader",
      "authentication_type_desc": "DATABASE",
      "type_desc": "SQL_USER"
    },
    {
      "sid": "0x0106000000010064000000000000000080493E64694F964BB425286C9C435294",
      "name": "orderops_investigator",
      "authentication_type_desc": "DATABASE",
      "type_desc": "SQL_USER"
    }
  ],
  [
    {
      "user_name": "billing_tester_reader",
      "role_name": "db_datareader"
    },
    {
      "user_name": "orderops_investigator",
      "role_name": "db_datareader"
    }
  ],
  [
    {
      "class_desc": "DATABASE",
      "user_name": "billing_tester_reader",
      "major_id": "0",
      "permission_name": "CONNECT",
      "state_desc": "GRANT"
    },
    {
      "class_desc": "DATABASE",
      "user_name": "orderops_investigator",
      "major_id": "0",
      "permission_name": "CONNECT",
      "state_desc": "GRANT"
    }
  ]
]
```

The Entra contained user is absent after DROP USER, and its db_datareader membership is removed. The Entra account itself and its existing Power BI scopes were not changed. Both SQL users have db_datareader only, plus normal CONNECT permission. No write, DDL, additional role or other database grant.

## Actual verification, each on its own sign-in

The SELECT statements return DB_NAME/SUSER_SNAME/USER_NAME plus TOP1 account_id/account_name from app.accounts and effective permissions. Both readers served account_id1/account_name Aster in billingapp, with their own respective username. SELECT1, INSERT0, UPDATE0, CREATE TABLE0, ALTER DATABASE0 and CONTROL DATABASE0 for each.

Both separately attempted:
```sql
SET XACT_ABORT ON;
BEGIN TRANSACTION;
UPDATE app.accounts SET account_name=account_name WHERE 1=0;
ROLLBACK TRANSACTION;
```

Both returned SqlException229: "The UPDATE permission was denied on the object 'accounts', database 'billingapp', schema 'app'." These are permission failures after successful authentication, not sign-in errors. No rows changed. Both read-only sign-ins are therefore verified for this table, with database-level role and DDL/write checks recorded separately. Credential Manager was read back with matching username/secret before use, without outputting the value.

The agent's existing DPAPI SQL authentication route can now use orderops_investigator against billingapp. Collector/reapproval and manifest configuration still have to target billingapp explicitly; they were not run or modified in this side task. No additional reader grant is needed for that declared database reader route.

## Preserved failures, receipts and cost

Original fallback control attempt failed at connect with SQL40613; resumed permission-check attempt failed SQL40507 because SUSER_SID(name) is unsupported on this Azure SQL version. Both stopped before any password storage/grant/removal. The corrected controls read sys.sql_logins in master and create the approved user explicitly in billingapp. A local quoting preflight also failed before any request and is retained in the tool transcript. None of these failed attempts was erased or refunded.

Successful receipt: .local/round-ten-20261007/billing/tester-sql-auth-grants-corrected.json, seal 55f0f8b6d1c16c1c090c597987fda3694aa9726cd5e4b650f897254444badf4b. Original tester-sql-auth-grants.json and tester-sql-auth-grants-resume.json preserved. Successful attempt8 physical controls; diagnosis1 and earlier2 failures give11 requests for this batch, pot1123?1134/1500, reserve95 unchanged, ordinary remainder271, rolling cap3000 unchanged. Zero model calls or investigation diagnostic reads.

README now refers only to the working tester identity and Credential Manager target. No sealed defects, oracle, expectations, delivery record, tapes, ledgers or engine code were copied to D:\dia-billing-tester. The tester-session instruction file is unchanged from the previous output-path-only copy.

## DECIDED WITHOUT REVIEW

Used the existing contained agent account's credential when the read-only master listing established that no server login exists. Rejected alternative: create a server login or require a server authentication change. Either would exceed the approved database-only change. No existing agent password was changed.
