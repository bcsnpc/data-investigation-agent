# Dedicated monitoring reader: creation succeeded, database absent

2026-10-03 America/Chicago (2026-10-04 UTC). This is an identity/control-plane
checkpoint, not an investigation or an accounting-query result.

## Explicit human decision and identity result

> The authorized reader for the KQL surface is a new dedicated Entra service
> principal named dia-reader. Create the app registration and service principal,
> store its credential in the project's existing secret mechanism, and grant
> database viewer on the fixture monitoring KQL database only. No write, admin,
> ingest, workspace role, or change/reuse of orderops_investigator.

The isolated publisher session authenticated as admin@skynwhy.com, object
23de217f-6e14-49cf-9acd-47dcd83cb82f, in tenant
dff91047-ebc2-4657-8dbe-5af328d57780. Its existing Graph authorization was used;
no publisher consent or scope amendment was made. A complete exact-name
application preflight returned zero entries. The following requests succeeded:

```http
GET https://graph.microsoft.com/v1.0/applications?$filter=displayName%20eq%20'dia-reader'&$select=id,appId,displayName
POST https://graph.microsoft.com/v1.0/applications
{"displayName":"dia-reader","signInAudience":"AzureADMyOrg","requiredResourceAccess":[]}
POST https://graph.microsoft.com/v1.0/servicePrincipals
{"appId":"ddd4d3cf-9cfd-440e-ac5b-be127caa46ea"}
POST https://graph.microsoft.com/v1.0/applications/5e1eae9f-9f66-4b06-b389-8f8b1b3f6c8a/addPassword
{"passwordCredential":{"displayName":"dia-reader-local-dpapi-20261004","endDateTime":"2026-11-03T00:20:47.398866+00:00"}}
```

| Identifier | Value |
| --- | --- |
| Client/app ID | ddd4d3cf-9cfd-440e-ac5b-be127caa46ea |
| Application object ID | 5e1eae9f-9f66-4b06-b389-8f8b1b3f6c8a |
| Service principal object ID | 59dd402b-1510-4289-96fb-f1d34d4494c5 |

Responses were HTTP 200, 201, 201 and 200 respectively. Registration is
single-tenant with no requested API permissions, redirects or workspace role.
The generated secret was removed before saving response evidence, passed only
in memory/stdin, and stored as a DPAPI-encrypted PSCredential via Export-Clixml
in ignored `.local/runtime-credentials/dia-reader.credential.xml`. Import/decrypt
round-trip equality was verified without printing the secret. Expiry is
2026-11-03T00:20:47.398866Z. No plaintext credential is in git or an audit file.
This identity has not authenticated a KQL query and has no new database grant.

Two earlier authentication attempts remain sealed and recorded: the default
Azure CLI profile failed with AADSTS50020 (its live.com account was not in this
tenant); the Fabric CLI could not acquire the Graph token. Neither issued a
Graph request or created anything. The next attempt explicitly used the isolated
publisher profile and checked tenant and publisher object ID before any request.
Its local label initially stopped because it searched the tenant-setting title
for the old wording; the saved HTTP 200 settings response already held the
renamed setting. The next checkpoint resolved that saved response, without
recreating the principal or rewriting the earlier result.

## Tenant setting and hard stop at workspace listing

Publisher `GET https://api.fabric.microsoft.com/v1/admin/tenantsettings` returned
HTTP 200, complete/unpaginated. The current setting is:

```json
{"settingName":"ServicePrincipalAccessPermissionAPIs",
 "title":"Service principals can call Fabric public APIs",
 "enabled":true,"canSpecifySecurityGroups":true,
 "tenantSettingGroup":"Developer settings"}
```

No enabledSecurityGroups or excludedSecurityGroups were returned for it. No
membership restriction was exposed by this control-plane response; no setting
or group membership was changed. Other admin/global API settings are scoped to
Semantica-Admin-API; dia-reader was not added to that group and did not receive
those capabilities. This settings finding does not assert successful KQL access.
[Microsoft's current developer settings](https://learn.microsoft.com/en-us/fabric/admin/service-admin-portal-developer)
name this public-API setting; it is distinct from admin/global API settings.

The next publisher request was:

```http
GET https://api.fabric.microsoft.com/v1/workspaces/149f8d99-1c66-4a0a-9624-759be002bb60/items
```

It returned HTTP 200 with 45 items, no continuation, and **zero Eventhouse,
KQLDatabase, Eventstream or WorkspaceMonitoring items**. Therefore this attempt
stopped exactly at user step 3. The workspace monitoring toggle itself was not
read, so this is an absent-resource finding, not a confirmed Disabled flag.
Nothing was enabled or provisioned as a substitute.

## Viewer grant record, probes and accounting result

| #343-style scope field | Actual result |
| --- | --- |
| Approved target | Fixture monitoring KQL database only; viewer only |
| Before permission read | Not performed: no database ID/query endpoint exists in the listing |
| Exact grant command | Not executable; target database absent. No grant command sent |
| After permission read | Not performed: no grant or target |
| Workspace/admin/write/ingest grants | None |
| SQL reader | orderops_investigator unchanged |

No fake database name or broad workspace role was used to complete the grant.
Zero accounting probes, zero additional isolated loads, no observed ingestion
delay and **no RowsRead/RowsWritten values**. The documented table and fields
remain available as a design route, not an observed capability:
[Copy Job monitoring](https://learn.microsoft.com/en-us/fabric/data-factory/copy-job-workspace-monitoring).

Dated supersession of #345's blocked entry: the identity prerequisite is now
satisfied by the authorized dedicated Entra principal. The monitoring-resource
prerequisite remains unsatisfied. **Accounting unavailable from this surface:
not queried because the monitoring database is absent.** Prior evidence and
ledger rows are unchanged; this does not turn a blocked probe into an empty
query result. The job's successful REST history finding remains true.

## Budget, preservation and deferred cleanup

Six physical request admissions: three Graph mutations, one Graph metadata GET,
one Fabric tenant-settings GET and one Fabric workspace-items GET. Zero
diagnostics, SQL guards, model calls or accounting probes. Authentication token
acquisition is not an estate data/metadata read. Part B **37 -> 43 / 120**.
Rolling allowance **192 -> 198 / 300** at these checkpoints; earlier 200/201
observations naturally aged out, without a counter reset or refund. No policy,
credit, cap, fixture, engine, approval hash or discovery context change.

All four attempt/checkpoint rows are appended; all 393 prior ledger rows are
unchanged. Documentation-only release; prior freezes remain invalid. Deferred
monitoring disable/removal instructions in
[the earlier record](round-two-workspace-monitoring.md#deferred-disableremoval-instructions-no-cleanup-executed)
remain in force. No cleanup or removal occurred, and no existing monitoring
resource was disabled. To resume, enable collection through the fixture's
workspace-admin UI and expose the generated monitoring database; this attempt
has no authority to enable it. Then viewer-grant support must still be tested.

## Sealed local evidence

| File under .local/round-two-20261003 | SHA-256 |
| --- | --- |
| dia-reader-monitoring-preflight.json | `0b8d1920d4a1dd7da65174871e49a12c9f003b9e0ce4e05400809c2cc5a9a6e6` |
| dia-reader-setup-isolated-publisher.json | `b39a30c903d4a6221f7d3aefb9cba5e07c9ed09b48f5a47774e403daeed40b19` |
| dia-reader-setup-publisher-profile.json | `34975ba22b524d6e3b0f0aea9406a8faccc740af0ac5ff7b771543b6f3c7c146` |
| dia-reader-setup.json | `faa389cdc37b8981cb89c62767db032f5d692b132e9f6cfeb9d3ebd06a4be889` |
