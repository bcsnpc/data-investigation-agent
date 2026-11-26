# HealthNet access record — 2026-11-26 (§8)

Owner approved `healthnet-access-and-smoke.md`, the subsequent bounded aggregate
reads, and the three model Read + Build grants. Existing identity only:
`dia-investigator-round19`, application `531419ef-1610-415a-b8bf-01a4b6aad751`.
Home-tenant principal: `248525da-278c-4a6c-b5c3-cc3e7728d3ce`;
Fabric-tenant principal: `439ceb25-d200-4f02-95cf-4b1318faca62`.
No new identity, credential, write grant, server setting or firewall change.

## Applied grants and removal steps

### Azure SQL: hn_clinical and hn_billing

Server: `sql-orderops-9696025.database.windows.net`. Before: no contained user.
Executed separately in each database, using the existing owner sign-in:

```sql
CREATE USER [dia-investigator-round19] FROM EXTERNAL PROVIDER;
ALTER ROLE [db_datareader] ADD MEMBER [dia-investigator-round19];
GRANT VIEW DEFINITION TO [dia-investigator-round19];
```

Readback: EXTERNAL_USER / EXTERNAL, application SID
`0xEF19145310165A41B8BF01A4B6AAD751`; only `db_datareader` membership,
explicit `CONNECT` and `VIEW DEFINITION`. Own investigator session reports
`db_owner=0`, `db_datareader=1`, `db_datawriter=0`, `sysadmin=0`.
These are role/grant checks, **not a clean effective-write certificate**:
the history-table anomaly below remains open.

Removal, in each named database only (review before executing):

```sql
REVOKE VIEW DEFINITION FROM [dia-investigator-round19];
ALTER ROLE [db_datareader] DROP MEMBER [dia-investigator-round19];
DROP USER [dia-investigator-round19];
```

### Fabric Viewer

Workspace `HealthNet Analytics`, `d237966c-b0b6-4123-bc89-e69643f4bf1f`.
Before: no investigator assignment. Existing Fabric owner submitted:

```http
POST https://api.fabric.microsoft.com/v1/workspaces/d237966c-b0b6-4123-bc89-e69643f4bf1f/roleAssignments
{"principal":{"id":"439ceb25-d200-4f02-95cf-4b1318faca62","type":"ServicePrincipal"},"role":"Viewer"}
```

Readback: role `Viewer`, assignment ID `439ceb25-d200-4f02-95cf-4b1318faca62`.
Reports and native SQL-endpoint metadata/counts are readable. No Contributor,
Member or Admin grant to the investigator. Viewer is the available workspace
read role; it includes all HealthNet items, not other workspaces.

Removal:

```http
DELETE https://api.fabric.microsoft.com/v1/workspaces/d237966c-b0b6-4123-bc89-e69643f4bf1f/roleAssignments/439ceb25-d200-4f02-95cf-4b1318faca62
```

### Semantic model Build

| Model | Model ID | Before | After |
| --- | --- | --- | --- |
| HealthNet Operations | `85e662ed-c4e6-41fb-9e43-be0c5a6aeeae` | Read | ReadExplore |
| HealthNet Revenue | `df6e3f67-deb6-4cb8-b15a-353176931679` | Read | ReadExplore |
| HealthNet Productivity | `0ef2b1a3-c6b7-4623-b962-39fe12c84d06` | Read | ReadExplore |

On each model, owner-authenticated Edge: **Manage permissions → existing
dia-investigator-round19 row → More options → Add build**. Independent API
`GET /groups/{workspace}/datasets/{model}/users` readback returned App principal
`439ceb25-d200-4f02-95cf-4b1318faca62`, `ReadExplore` only. Workspace readback
remains Viewer. No Share/Reshare/Write added. Remove on each model with
**Manage permissions → same existing row → More options → Remove build**;
retain inherited Read/Viewer unless separately revoking workspace access.

The public dataset-users grant API rejected App principals with HTTP 400,
`InvalidRequest`, “API supported only for User or Group principal types”.
Playwright Edge worked after the owner signed in as `admin@skynwhy.com`.
The Computer Use runtime module was unavailable (`ERR_MODULE_NOT_FOUND`);
the original signed-in Edge was not restarted. No group fallback was used.

## Earlier restrictive DENYs: applied but did not resolve the anomaly

Before the owner's later instruction to diagnose first, the initial read-only
grant task attempted these restrictions in **hn_clinical only**:

```sql
DENY INSERT ON OBJECT::[app].[encounter_history] TO [dia-investigator-round19];
DENY INSERT ON OBJECT::[app].[order_line_history] TO [dia-investigator-round19];
DENY INSERT ON OBJECT::[app].[patient_history] TO [dia-investigator-round19];
```

The owner catalog now confirms all three explicit DENYs. Nevertheless, the
investigator's own `fn_my_permissions` still lists INSERT, and
`HAS_PERMS_BY_NAME(..., 'OBJECT', 'INSERT')` still returns 1 on those objects.
This attempted restriction is **not a verified fix**. No such DENY was executed
in hn_billing. No actual INSERT/UPDATE/DELETE was sent to any database.

Removal for each corresponding restriction, only if later approved:

```sql
REVOKE INSERT ON OBJECT::[app].[encounter_history] FROM [dia-investigator-round19];
REVOKE INSERT ON OBJECT::[app].[order_line_history] FROM [dia-investigator-round19];
REVOKE INSERT ON OBJECT::[app].[patient_history] FROM [dia-investigator-round19];
```

## Owner decision: diagnose before further SQL permission changes

The subsequent 2026-11-26 owner instruction freezes further SQL permission
changes pending approval. Its audit is [healthnet-permission-diagnosis.md](healthnet-permission-diagnosis.md).
No additional SQL grant, DENY, revoke, role change, ownership change or actual
write probe was made after that instruction. The later owner-approved current-table
temporal reads below resolve five deferred aggregates without a permission change.
Ordersops was not unpaused or switched to paid continuation.

## Initial direct-principal RLS proposal: unsupported member type

The owner separately approved adding **Investigator**, with no table filters
and only the existing service principal as member, on the three models above.
This cannot be completed as specified: Microsoft documents that
[service principals cannot be added to an RLS role](https://learn.microsoft.com/en-us/fabric/security/service-admin-row-level-security#considerations-and-limitations).
All three native Security pages show existing roles DepartmentHead, Doctor,
Executive and HospitalManager; no Investigator role. The member picker searches
people/groups by email, and searching the principal's name returns only
`dia-investigator-round19-api-readers`, not the service principal.

At that initial checkpoint no role was created with an empty or substitute
membership, and no group was assigned or amended. The subsequent owner-approved
group experiment below supersedes that stopping point. A different authentication
identity or workspace role still requires a separate owner decision.

The pre-group bounded retry through the gateway under the existing investigator token:
all three trivial DAX queries and all three main totals returned HTTP 401
`PowerBINotAuthorizedException`. Actual totals and RLS-related numerical
differences remain **NOT_MEASURABLE**. No owner-query fallback or impersonation.
[Execute Queries documentation](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/execute-queries-in-group)
also excludes service principals on RLS-enabled models. The authorization
response alone does not diagnose every possible contributor to the refusal.

## Owner option A: HealthNet-only group experiment — applied and verified

Owner approved this alternative on 2026-11-26, expressly retaining Viewer and
requiring a stop before any workspace elevation if the reads remain blocked.

1. Created **dia-healthnet-investigator**, security group
   **`18442d42-4646-44cf-9041-5aeaef202cff`**, in the Fabric tenant. Exact request:

```http
POST https://graph.microsoft.com/v1.0/groups
{"displayName":"dia-healthnet-investigator","description":"HealthNet-only Investigator RLS access experiment, owner approved 2026-11-26. No other estate/model/workspace grants.","mailEnabled":false,"mailNickname":"dia-healthnet-investigator","securityEnabled":true}
```

2. Added only the existing Fabric investigator principal:

```http
POST https://graph.microsoft.com/v1.0/groups/18442d42-4646-44cf-9041-5aeaef202cff/members/$ref
{"@odata.id":"https://graph.microsoft.com/v1.0/directoryObjects/439ceb25-d200-4f02-95cf-4b1318faca62"}
```

Expanded native readback confirms exactly that one service-principal member.
The ordinary v1.0 `/members` response initially returned an empty list despite
successful addition. Microsoft's [documented workaround](https://learn.microsoft.com/en-us/graph/api/group-list-members)
is `/groups/{id}?$expand=members` (or beta); expanded readback was used. An empty
ordinary member list is not evidence that a group has no service principals.
The existing global practice-estate group was neither reused nor modified.

3. Created only the new role through owner-authenticated XMLA, separately on
   HealthNet Operations, HealthNet Revenue and HealthNet Productivity:

```json
{"create":{"parentObject":{"database":"HealthNet Operations"},"role":{"name":"Investigator","modelPermission":"read","tablePermissions":[]}}}
```

The other two exact commands substitute `HealthNet Revenue` and
`HealthNet Productivity` for the database name; every other field is identical.
No whole-model replacement or refresh was used. The first owner XMLA connection
using the model GUID failed before command dispatch; the native display-name
connection succeeded. The failed attempt is retained.

4. In each model's native **Security → Investigator** page, added only
   **dia-healthnet-investigator**, then **Save**. Fresh navigation confirms
   `Investigator (1)` / `Members (1)` with that group only. Initial navigation
   before the asynchronous save completed lost one staged edit; it was saved
   again and fresh readback verified. No existing role membership was edited.

5. Fresh owner `getDefinition?format=TMSL` readbacks confirm on **all three**:
   only the unfiltered read role was added; the four existing roles, filters,
   measures, relationships, tables, partitions and all other model fields are
   semantically unchanged. Other definition parts are byte-identical. The new
   role serializes as `{"name":"Investigator","modelPermission":"read"}`,
   with no table permissions/filters. Workspace readback still shows the
   investigator **Viewer** and no workspace grant to the new group.

Removal steps, **not executed**:

- On each model, Security → Investigator → remove
  dia-healthnet-investigator → Save. Then owner XMLA delete **only** that role:
  `{"delete":{"object":{"database":"HealthNet Operations","role":"Investigator"}}}`;
  substitute the other two exact model names for their commands.
- Remove the sole directory membership with
  `DELETE https://graph.microsoft.com/v1.0/groups/18442d42-4646-44cf-9041-5aeaef202cff/members/439ceb25-d200-4f02-95cf-4b1318faca62/$ref`.
  Keep `/$ref`: omitting it has different deletion semantics.
- After model assignments are removed, delete only this new group with
  `DELETE https://graph.microsoft.com/v1.0/groups/18442d42-4646-44cf-9041-5aeaef202cff`.
- These steps do not revoke the separately recorded direct Build or Viewer grants.

### Bounded actual-reader result

Gateway `XMLA_EVALUATE` validates each fixed `EVALUATE ROW("ok", 1, "total", [measure])`
before native ADOMD dispatch. Existing investigator token verified by tenant,
principal and app ID; no owner token, Roles override or EffectiveUserName.

| Model / measure | Owner authoring baseline | Investigator result | Comparison |
| --- | ---: | ---: | --- |
| Operations / Visits | 249,575 | 249,575 | MATCH |
| Revenue / Gross Charges | 1,935,995,659.28 | 1,935,995,659.28 | MATCH |
| Productivity / Visits | 249,575 | 249,575 | MATCH |

All returned `ok=1`. Operations' initial post-change connection was refused;
one bounded propagation retry passed. The original failure remains recorded.
There is **no observed RLS reduction of these three totals** under this identity;
this does not test every filter, measure or business-user role. REST results are
reported separately in the smoke report. No workspace role was changed.

## Owner temporal-path steer — no permission or guard change

Owner approved counting through each **current** table with `FOR SYSTEM_TIME ALL`,
not directly reading history objects. All five native temporal pairs passed the
unchanged database/current-object guards. The fixed aggregate returns total
versions and counts versions whose `valid_to` is below the open-ended sentinel.
Each returned **0 historical versions**. The ordinary `payer_plan_history` has no
temporal parent and remains unrun. A billing serverless-resume SQL 40613 was
retried once successfully; the failed receipt is preserved.

Own permission-metadata readbacks still report INSERT=1 on all five active
history tables; the origin remains unexplained. No DENY/REVOKE or guard change
was applied for these reads. See the detailed counts and distinction from direct
physical history-table counts in [healthnet-smoke-results.json](healthnet-smoke-results.json).

Local original receipts and their hashes are listed in
[healthnet-smoke-evidence.json](healthnet-smoke-evidence.json). No sealed ticket
or expected-answer contents were opened during this access/smoke task.
