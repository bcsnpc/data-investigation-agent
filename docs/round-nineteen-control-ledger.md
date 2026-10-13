# Round Nineteen authority and control record

2026-10-13, America/Chicago. Owner supplied round-nineteen-lineage-graph.md and prioritized the dedicated reader while available for 30 minutes. Starting point: draft #424, 6b5adf2. No merge is authorized.

## Explicit owner decision under CLAUDE.md section 8

Create one dedicated read-only investigator application identity, with its service principal in the Fabric tenant. Approved scopes: test-workspace Viewer, semantic model Read and Build, fixture/billing SQL db_datareader and VIEW DEFINITION including application sources, and read-only metadata APIs. Tenant settings may be enabled for a group containing only this principal. No write/admin investigator permissions or RLS impersonation. Preserve the existing cache until the replacement passes end to end.

Microsoft requires an app trusting managed identity to share its home tenant. The implementation uses one multitenant app in the platform tenant, a Fabric-tenant service principal, and its home principal for application SQL. The existing id-dia-worker is the sole federated subject. No client secret or Graph application permissions. [Microsoft requirements](https://learn.microsoft.com/en-us/entra/workload-id/workload-identity-federation-config-app-trust-managed-identity).

Both existing administrator sessions passed Graph identity lookup: admin@skynwhy.com (23de217f-6e14-49cf-9acd-47dcd83cb82f, Fabric tenant dff91047-ebc2-4657-8dbe-5af328d57780), and platform owner leelamounika14@gmail.com (c22c5e9b-5005-4a48-af98-51d614e6021a, tenant aeb4d0a9-e637-4a7e-8efc-63cf0c3827df). No new sign-in required at opening.

Fresh round physical allowance 1,500; cumulative usage informational. Rolling 3,000, restoration reserve 95 and diagnostic 12 unchanged. New model spend at most USD15 above the shared opening total; USD10 protected margin retained. Exact opening read and policy update pending; no estate/model probe admitted before them. No counters reset.

Existing platform only, estimated total at most USD20/month. Archive cleanup requires SHA-256 proof before local deletion; both legacy export copies require one verified private archived copy first. Shared keys may be disabled only after callers use identity. Part D permits one build-script controlled change and reversal.

Private exact control receipts: .local/round-nineteen/identity-controls.json. Tokens are held in memory, never recorded. A combined documentation command was rejected by automatic policy before execution; no changes resulted.

## Identity and authentication changes applied, 2026-10-13

| Identity | ID |
|---|---|
| app_id | `531419ef-1610-415a-b8bf-01a4b6aad751` |
| app_object_id | `74f4529f-76b3-4d39-9eb9-31983f216e29` |
| home_sp_id | `248525da-278c-4a6c-b5c3-cc3e7728d3ce` |
| fabric_sp_id | `439ceb25-d200-4f02-95cf-4b1318faca62` |
| group_id | `79c75be9-d8c3-4824-91c2-fc945041a8c3` |
| name | `dia-investigator-round19` |
| credential | `federated id-dia-worker; no secret or certificate` |

Application creation and federation succeeded without a secret. Initial cross-tenant SP creation returned HTTP400 `NoBackingApplicationObject`; application GET confirmed it existed, and the bounded retry succeeded. The dedicated security group has this principal alone. Existing tenant settings were preserved; the group was appended only to `AllowServicePrincipalsUseReadAdminAPIs`, `AdminApisIncludeDetailedMetadata` and `AdminApisIncludeExpressions`. Public API and ExecuteQueries settings already enabled; write-admin/global-update groups unchanged.

Viewer assigned and independently listed on `149f8d99-1c66-4a0a-9624-759be002bb60`, `d028fa2b-0d1b-4dd8-b423-37dd161cd5d0`, `7d67bb36-04f6-4182-95aa-da5d515248fa`. Before: no assignment for the new principal. Exact request for each workspace:

```json
{
  "principal": {
    "id": "439ceb25-d200-4f02-95cf-4b1318faca62",
    "type": "ServicePrincipal"
  },
  "role": "Viewer"
}
```

Model API refused App grants with HTTP400 `API supported only for User or Group principal types`. The documented Group route granted `ReadExplore` to the new single-member group, with before/after listings. No Reshare or Write. Models:

- `https://api.powerbi.com/v1.0/myorg/groups/149f8d99-1c66-4a0a-9624-759be002bb60/datasets/5f2afb96-157e-46ab-9fcb-b56a2bb37fba/users`: `{"datasetUserAccessRight": "ReadExplore", "identifier": "79c75be9-d8c3-4824-91c2-fc945041a8c3", "principalType": "Group"}`, HTTP200.
- `https://api.powerbi.com/v1.0/myorg/groups/149f8d99-1c66-4a0a-9624-759be002bb60/datasets/c463921e-64b2-488e-b8b1-e0239980c79c/users`: `{"datasetUserAccessRight": "ReadExplore", "identifier": "79c75be9-d8c3-4824-91c2-fc945041a8c3", "principalType": "Group"}`, HTTP200.
- `https://api.powerbi.com/v1.0/myorg/groups/149f8d99-1c66-4a0a-9624-759be002bb60/datasets/3484a2bc-98c5-4cef-be5c-a6215484075e/users`: `{"datasetUserAccessRight": "ReadExplore", "identifier": "79c75be9-d8c3-4824-91c2-fc945041a8c3", "principalType": "Group"}`, HTTP200.
- `https://api.powerbi.com/v1.0/myorg/groups/149f8d99-1c66-4a0a-9624-759be002bb60/datasets/8e434350-7100-47b7-a0de-2c5732385dbb/users`: `{"datasetUserAccessRight": "ReadExplore", "identifier": "79c75be9-d8c3-4824-91c2-fc945041a8c3", "principalType": "Group"}`, HTTP200.
- `https://api.powerbi.com/v1.0/myorg/groups/149f8d99-1c66-4a0a-9624-759be002bb60/datasets/163ce520-ec47-4824-975c-96f5c749205f/users`: `{"datasetUserAccessRight": "ReadExplore", "identifier": "79c75be9-d8c3-4824-91c2-fc945041a8c3", "principalType": "Group"}`, HTTP200.
- `https://api.powerbi.com/v1.0/myorg/groups/149f8d99-1c66-4a0a-9624-759be002bb60/datasets/0c89889c-6fe6-49ab-91e9-4b00a51070e6/users`: `{"datasetUserAccessRight": "ReadExplore", "identifier": "79c75be9-d8c3-4824-91c2-fc945041a8c3", "principalType": "Group"}`, HTTP200.
- `https://api.powerbi.com/v1.0/myorg/groups/d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/datasets/ade205fe-52b1-43b5-980a-773b7b1de538/users`: `{"datasetUserAccessRight": "ReadExplore", "identifier": "79c75be9-d8c3-4824-91c2-fc945041a8c3", "principalType": "Group"}`, HTTP200.
- `https://api.powerbi.com/v1.0/myorg/groups/d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/datasets/46687aa6-13d7-40ff-9c78-02f7bfd4e73a/users`: `{"datasetUserAccessRight": "ReadExplore", "identifier": "79c75be9-d8c3-4824-91c2-fc945041a8c3", "principalType": "Group"}`, HTTP200.
- `https://api.powerbi.com/v1.0/myorg/groups/7d67bb36-04f6-4182-95aa-da5d515248fa/datasets/c6c1091c-3bde-46ca-94fc-58f62d1e4188/users`: `{"datasetUserAccessRight": "ReadExplore", "identifier": "79c75be9-d8c3-4824-91c2-fc945041a8c3", "principalType": "Group"}`, HTTP200.

### Additional explicit owner decision: SQL server Entra administrator

Owner approved existing `leelamounika14@gmail.com` as server Entra administrator, conditioned on keeping SQL authentication enabled. The account was accepted; no fallback group created. Before: Entra administrator list `[]`, server administrators absent. The attempted before/after `ad-only-auth get -s` used an invalid CLI flag and returned no setting; that failed command remains in the receipt. Corrected after read using `-n` returned `azureAdOnlyAuthentication: false`. We did not call enable/disable Entra-only authentication. No password or existing login changed.

Exact owner-control command:

```powershell
az sql server ad-admin create -g rg-investigator-dev -s sql-orderops-9696025 --display-name leelamounika14@gmail.com --object-id c22c5e9b-5005-4a48-af98-51d614e6021a
```

Both source databases initially returned unavailable during serverless resume. Failures preserved, no grants in those attempts. After resume, `ordersops` and `billingapp` each had no matching contained user before, and only `db_datareader` membership plus CONNECT and VIEW DEFINITION afterward. Exact approved grant, independently executed in each database:

```sql
CREATE USER [dia-investigator-round19] WITH SID = 0xEF19145310165A41B8BF01A4B6AAD751, TYPE = E; ALTER ROLE [db_datareader] ADD MEMBER [dia-investigator-round19]; GRANT VIEW DEFINITION TO [dia-investigator-round19];
```

Application ID SID is explicitly bound to the new principal; no directory write/read role was added to the server. Authentication and query proof as the service principal are still pending; grants alone do not prove execution.

## Budget decision applied

Opening shared charge USD107.957725; ceiling USD127.957725 -> USD132.957725, protected USD10 unchanged, so maximum new model charge USD15. Fresh ROUND_NINETEEN pot1500 begins 1791871715.9976459; reserve95, rolling3000, diagnostic12 unchanged. Historical10,200 rows and5,032 physical charges preserved. A pre-update unit assertion initially refused because the account stores MICRODOLLARS; transaction rolled back before mutation. Corrected integer-unit update committed with an owner-decision document. No run/model call yet.

## Local control receipt hashes

### Additional owner storage decision applied, 2026-10-13

Owner answer: **Approve platform-storage scope only**. At 06:21:55 UTC the existing owner `leelamounika14@gmail.com` (`c22c5e9b-5005-4a48-af98-51d614e6021a`) received Storage Blob Data Contributor on `diaplatformd5dd7d65` only, to upload the approved archives using identity before disabling account-key access. Before: inherited Owner and Foundry User, no Blob data role. After: those unchanged roles plus this one account-scoped data role. No estate-storage role changed.

```powershell
az role assignment create --assignee-object-id c22c5e9b-5005-4a48-af98-51d614e6021a --assignee-principal-type User --role "Storage Blob Data Contributor" --scope /subscriptions/d5dd7d65-1b61-4025-b9f1-5f7b2f8d1ef9/resourceGroups/rg-dia-platform/providers/Microsoft.Storage/storageAccounts/diaplatformd5dd7d65
```

Before/after: `az role assignment list --assignee c22c5e9b-5005-4a48-af98-51d614e6021a --scope <the exact account scope above> --include-inherited`; both succeeded. Assignment `6ef84b9e-b6c0-44d4-b9de-83c3dbb8be67`. Full local receipt `owner-storage-grant.json`, SHA-256 `2662f76aa1669bf23bd93ac9089365cbafbf4452b129452ee99a67ae3b625931`. Archive verification and shared-key disablement are separate, still pending controls.

- `budget-opening.json`: `e4ce1e647a9a18e913932873a26bf9ef32947d5e789de737c811897d78918e11`.
- `identity-controls.json`: `6bc89504cb1e1591ffa06d167360547a8d7c6ce033cd2fa839553958e99e02c7`.
- `model-controls.json`: `77029d3f145fa1df7914c4a3bd1bebd422ccbe172c2bc44bd05ee54c609da153`.
- `model-group-controls.json`: `ad05598167e5677cc2737b3fc37ae47cae79e5ddf6e8edd5fbe286ca8af55b8d`.
- `reader-identity.json`: `85244617bfb9674b82f2621d8c03b5597ed792716ca4265e09f2ba9bea25435f`.
- `sql-admin-controls.json`: `b9615d5b76d27b0bd835ac07268ba639c927bd8d2abaac9a926dec8bf78fd295`.
- `sql-auth-after.json`: `f47e72cf5b6a43965338a9443a98105e2f14980ff27e1dfbc07b75d330c713b4`.
- `sql-reader-grants-attempt01.json`: `e6023f824484396984c40d94cb272e8754df42880dd214e1756194277a2f3857`.
- `sql-reader-grants-billing-retry.json`: `b6540cbf627d2c239ace57fa30da631da3d726f30d063a3bba32fdb2e44348ac`.
- `sql-reader-grants.json`: `789453119e163dd0698c64e3c162db6d934a4f5f28d8bf403008ad4f9b7d015c`.

## Authentication controls, 2026-10-13

Dated correction at06:48UTC: the 6614146 workflow completed its tests, but its publish job was skipped for a pull-request event. Public registry lookup returned HTTP404 for that commit tag. Executions evy5kkz and qs3ev65 were waiting before container start, not hung in authentication; evy5kkz was stopped at06:43:49. Its operator stop receipt's timeout diagnosis is superseded by this observed replica/registry evidence. These executions performed no authentication, estate or model call. Publication will be explicitly dispatched before the next start, with a registry manifest check. Old failures are retained.

Integrated offline foundation: static graph/history/bounded API, shared application authority and case writer, Blob screenshot retention controls, identity-only resumable archive. Combined targeted regression passed86 tests and6 subtests. This does not establish a live migration, graph scan or end-to-end verification. Source export archive verified; local deletion blocked by policy, owner script retained in source-export-archive/cleanup-verified.ps1.

First check sagxfam failed four audiences without a safe stage. Diagnostic htkjvt8 at06:30:19UTC failed all four at MANAGED_ASSERTION_BINDING. Separate 7f737qu control established expected tenant/oid and audience `fb60f99c-7a34-4190-8149-302f77469936`, issuer `https://login.microsoftonline.com/aeb4d0a9-e637-4a7e-8efc-63cf0c3827df/v2.0`. Only these public claims retained, never tokens. Local start receipts and logs retained; 60-second hold allowed log capture. Zero estate requests/model calls; not estate permission tests.

Microsoft documents the resource ID [here](https://learn.microsoft.com/entra/identity/conditional-access/agent-id); its [federation guide](https://learn.microsoft.com/entra/workload-id/workload-identity-federation-config-app-trust-managed-identity) uses the URI form. Adapter accepts these two exact representations only, preserving tenant/principal validation. Nine focused tests pass. Live exchange pending; no grant or trust change. A combined documentation/commit shell call was blocked by policy; none of it executed. README contains historical non-UTF8 bytes, so new text was prepended without changing those bytes.
