# Scan benchmark access — owner approval 2026-11-26

Only newly created benchmark estates may receive these grants. Existing estates,
identities, secrets, server authentication, firewall rules and capacity are unchanged.

## Estate A applied

New Azure SQL `sb_wholesale` on `sql-orderops-9696025.database.windows.net`:
before, no contained investigator. After, existing application
`dia-investigator-round19` has a contained external user, `db_datareader` only,
and `VIEW DEFINITION`. Native role and permission readbacks are retained locally
in `.local/scan-benchmark/A-grants.json`. No write role/grant was added.

Revoke, in this database only:

```sql
REVOKE VIEW DEFINITION FROM [dia-investigator-round19];
ALTER ROLE [db_datareader] DROP MEMBER [dia-investigator-round19];
DROP USER [dia-investigator-round19];
```

New Fabric workspace `9e1701f5-da55-4f01-b2a6-6f211a36043b`:
before, no investigator assignment. After, Fabric-tenant principal
`439ceb25-d200-4f02-95cf-4b1318faca62` is Viewer only, verified by role readback.
Revoke with owner `DELETE /v1/workspaces/9e1701f5-da55-4f01-b2a6-6f211a36043b/roleAssignments/439ceb25-d200-4f02-95cf-4b1318faca62`.
No model Build, group membership or write permission has been changed.
