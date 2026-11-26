# Investigator SQL permission diagnosis — 2026-11-26

**No ordinary write-grant source was found. The exact reason Azure SQL reports
INSERT on active temporal history objects remains unestablished.** It would be
incorrect to name db_owner, public, schema ownership or the server administrator
as its source: the native readbacks rule those out on the accessible databases.
Direct history counts remain unrun, and no permission fix was applied
after the owner's diagnose-first steer. The later owner-approved temporal path
successfully measured five historical-version counts through their current tables.

| Database | Own role/token readback | Effective object INSERT / UPDATE / DELETE | Current audit status |
| --- | --- | --- | --- |
| hn_clinical | user + public + db_datareader; no owner/writer/admin | INSERT=1 on its 3 active temporal history tables; all other table DML=0 | Grant/ownership audit complete; unexplained history permission report |
| hn_billing | user + public + db_datareader; no owner/writer/admin | INSERT=1 on charge_history and claim_history; all other table DML=0 | Same anomaly on its 2 active temporal history tables |
| billingapp | user + public + db_datareader; no owner/writer/admin | All 7 table DML=0; no active temporal history tables | No effective-write issue found |
| ordersops | Current session refused with SQL 42119 | Not measurable now | November free allowance exhausted; owner instruction to wait until Dec 1 retained |

`hn_billing.app.payer_plan_history` is an ordinary NON_TEMPORAL_TABLE and its
write flags are 0. It was deferred with the blocked history-count cohort, not
individually proven write-capable. Its count remains unrun under the owner's
instruction: it has no native temporal parent to use for the approved alternative.

## Sources checked

1. **Actual identity.** Own sessions are
   `531419ef-1610-415a-b8bf-01a4b6aad751@aeb4d0a9-e637-4a7e-8efc-63cf0c3827df`,
   contained user `dia-investigator-round19`. Token claims were checked in memory;
   only aud/tid/oid/appid coordinates were retained, never the token.
2. **Role memberships, including inheritance.** Complete native role-member
   relations and own `sys.user_token` show only public + db_datareader for the
   investigator. Own `IS_MEMBER('db_owner')=0`, `db_datawriter=0`,
   `IS_SRVROLEMEMBER('sysadmin')=0`. No intermediate/custom role is present.
3. **Database, schema, object and column grants.** Explicit investigator grants
   are CONNECT and VIEW DEFINITION. Cataloged public permissions are system
   metadata SELECT/EXECUTE permissions, not INSERT/UPDATE/DELETE/CONTROL on the
   application tables. No applicable higher-scope write grant or column-level
   write grant exists. Own database permissions contain CONNECT, SELECT and
   definition visibility only; own app/dbo schema INSERT and CONTROL flags are 0.
4. **Ownership.** app/dbo schemas are owned by dbo; the investigator owns no user
   object. Database owner SID differs from its application SID in all three
   accessible databases. No ownership path supplies its reported INSERT.
5. **Server administration.** ARM readback names
   `leelamounika14@gmail.com`, object `c22c5e9b-5005-4a48-af98-51d614e6021a`,
   as Entra administrator, not the investigator. Home-tenant investigator
   `transitiveMemberOf` returns an empty list. SQL authentication remains enabled
   (`azureADOnlyAuthentication=false`). Master server-role and matching login
   catalog queries returned no rows. `sys.server_permissions` is unavailable on
   this Azure SQL surface; that failed query is preserved, not claimed successful.
6. **Temporal status.** The five positive INSERT flags coincide exactly with
   active HISTORY_TABLE objects linked from system-versioned current tables.
   There are no explicit history GRANT rows for any principal. Clinical's only
   explicit history permission rows are the three earlier DENY INSERTs, which
   still do not change the effective INSERT result.

Ordersops' historical approved scope was db_datareader + VIEW DEFINITION, as
recorded in [the Round 19 control ledger](round-nineteen-control-ledger.md).
That is historical evidence, **not** a fresh verification of its current state.
No business data was read from ordersops or billingapp in this diagnostic.

The first owner query used `SUSER_SNAME(owner_sid)`, which Azure SQL rejects;
the follow-up successfully read `owner_sid` directly. Initial pytds connection
failures on billingapp were followed by successful native SqlClient metadata
reads. Both original failures and successful follow-ups are retained.

## Interpretation and least-privilege solution — no permission change

The evidence points to a **temporal-history permission-reporting peculiarity**,
not an elevated role or an explicit write grant. This is an inference: read-only
metadata cannot establish the internal implementation of that permission check,
and no actual DML experiment was authorized or attempted. Microsoft's
[temporal security documentation](https://learn.microsoft.com/en-us/sql/relational-databases/tables/temporal/security)
states that direct history changes are prohibited while system-versioning is on.
That does not by itself explain `HAS_PERMS_BY_NAME=1` despite DENY.

There is therefore **no identified excessive grant that can honestly be revoked
as a proven fix**. Do not remove public/system grants, change ownership, disable
history, elevate the investigator, or weaken the guard.

The owner subsequently approved the least-privilege query-path solution:
**read temporal history through the current table using FOR SYSTEM_TIME ALL**.
The normal guard still requires the current table to be read-only; Azure SQL
uses the existing SELECT access to execute the temporal read. All five temporal
pairs passed with 0 historical versions. No new permission, DENY, REVOKE or role
was needed. The earlier considered db_denydatawriter experiment was never run
and is unnecessary for this approved read path.

Permission metadata still reports INSERT=1 on those five history objects after
the reads. That discrepancy remains unexplained; it was not silently relabeled
as a proven harmless permission. Direct history-object reads remain blocked by
the unchanged guard. No change to ordersops or billingapp is justified by current
evidence; ordersops needs a fresh metadata audit once its allowance resumes.

Original receipts are pinned in [healthnet-smoke-evidence.json](healthnet-smoke-evidence.json);
the compact readback is [healthnet-permission-audit.json](healthnet-permission-audit.json).
