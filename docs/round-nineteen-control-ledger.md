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

## Foundation controls completed, 2026-10-13 06:49?06:51 UTC

The dedicated application successfully exchanged the worker assertion for all four configured tokens: Fabric-tenant Power BI, Fabric API and SQL, plus application-tenant SQL. Execution `job-dia-worker-d2wyaef` used tested image `d01700abb7163fdd9a4c7e13183c8d542ccedaa3`, registry manifest `46f55a7455c689600100a643a8010422dde8815dd2b17fd93de403036b26d5ff`. Exact public tenant/client/principal/audience checks passed. This establishes authentication only; query permissions and end-to-end readiness remain pending. No token was retained. Earlier failed controls remain unchanged.

Storage hardening applied after caller audit: `allowSharedKeyAccess` changed from true to false on `diaplatformd5dd7d65` only; public Blob access remains false. Six control operations include before/after and creation of three 30-day screenshot lifecycle prefix rules (fixture-example, billing-example, unknown-domain-v4). Owner token-authenticated immutable PUT/GET after disablement passed, byte-exact. Subsequent archive batch02 also passed with keys disabled. No investigator or estate-storage scope changed. Worker storage confirmation awaits its next job.

Local controls and their hashes:
- `federated-auth-06-results.log`: `1ae02508ce4840ef6e4e5a5c4e91c1cead9c0e2ce6dfa95c432d77bbf51ab074`.
- `federated-auth-06-start-receipt.json`: `03d9464e74712a932c4f5a65f62684a4f15f9cb34408751f6b4045067fd4c51c`.
- `auth-06-image-proof.json`: `6f0526a3d7de89224ed396efad8590056496587d32a203f9e7d1f2238c4b2bbe`.
- `storage-hardening.json`: `45f0caaea2cd2ad5f4f078bd3a989bfad1d22cb2c57bf3ef6008569cbeb7cdd8`.
- `screenshot-lifecycle-policy.json`: `d14b5aab56c66f9ebbe306669d36b71ab76639d345464c095201a40b0a713033`.
- `storage-identity-proof.json`: `cfbc26efff20de1fd72679ff93a5fd05218e57a77bb944a5721b640685437661`.

## Exact application-state migration, 2026-10-13

Original catalog migrated to PostgreSQL: 23568 rows across 20 tables, every source/target table hash equal. Source hash `5add459c65263cccf64b10a4ab1175be732e03146ee17440a13d1639be8cfe14`. Production case sections were published in the same transaction. Historical isolated claim catalogs are separate and not yet claimed migrated. No estate or model reads. Receipt `application-migration-applied.json`, SHA256 `6db21e3c0a69737b4eb03f4a6f422bf3078960b730b20feffb39db750bac2764`.

| Table | Rows before | Rows after | Exact match |
|---|---:|---:|---|
| adaptive_events | 11456 | 11456 | yes |
| adaptive_sessions | 438 | 438 | yes |
| adaptive_syntheses | 317 | 317 | yes |
| agent_progress | 3832 | 3832 | yes |
| aggregate_receipt_seals | 1422 | 1422 | yes |
| comparison_assessments | 0 | 0 | yes |
| flexible_diagnostics | 1420 | 1420 | yes |
| native_capability_decisions | 3 | 3 | yes |
| native_diagnostics | 3 | 3 | yes |
| v2_cancellations | 0 | 0 | yes |
| v2_run_events | 1124 | 1124 | yes |
| v2_runs | 281 | 281 | yes |
| v2_steps | 281 | 281 | yes |
| workspace_form_controls | 0 | 0 | yes |
| workspace_image_reads | 0 | 0 | yes |
| workspace_image_reviews | 0 | 0 | yes |
| workspace_images | 0 | 0 | yes |
| workspace_intakes | 2365 | 2365 | yes |
| workspace_jobs | 163 | 163 | yes |
| workspace_previews | 463 | 463 | yes |


## Graph Parts B/C, 2026-10-13

Retained v3 graph readback: fixture1163nodes/1696edges; billing388/759. Exact receipt `graph-v3-receipt.json` SHA256 `3ee6169eb37258b1b38d4c3c468a6e08182b93dd7fe3250692fd86ab19b681d0`. The asset-catalog manifest seed rewrote no graph record; SHA256 `4541617a5c03757f3bc56c041dc996ef06ba479b628955423da543a31caa6977`. All historical snapshots retained.

Reader scan execution bbgkydh:26fixture+6billing physical requests, no diagnostic/model reads. Both item lists succeeded; all67owner refreshes unavailable. Exact statuses and provider codes are in `round-nineteen-live-metadata-scan.json`; private full readback SHA256 `4bb4dbb619f0cbe42b7588670a83592a0bb613edf2fe03e225fa5eb9c2ec599b`. These calls consume the existing round pot (36total with prior4). No owner was deleted on absence or access failure. No investigator scope broadened.

Interpreter execution r5na9t8 stopped before provider dispatch because the recording path was read-only. One planner reservation remains conservatively UNCERTAIN/settled, no dollar reservation or provider charge. Original result CAS `289ab6bbc51f5526f1a3555efead41c686515ce3ff1e7a79954d0b3a0949e13e`; original three remaining tasks not run. Fixed caller-owned recording directory is offline-tested; no original result overwritten.

DECIDED WITHOUT REVIEW: do not mutate the proposed controlled-change report while the actual graph reader cannot fetch its baseline definition (HTTP404 EntityNotFound). Rejected alternative: use publisher credentials to make the reader test pass. Continue offline change/revert tests and scheduling with explicit gaps.

Four retained input databases were losslessly NTFS-compressed; SHA256 before/after matched for each, originals not deleted. Free bytes10,825,805,824 ->11,392,466,944. Receipt `retained-inputs-ntfs-compression.json` is local. This changes filesystem allocation only, not evidence bytes.

## Part D interpreter result, 2026-10-13

Execution `job-dia-worker-x9fz5t9` used the tested `ef31595` image (all eight hosted shards green). It attempted only two of the three previously unattempted inputs: the first returned seven exact-span-validated INFERRED proposals; the second failed `GRAPH_INTERPRETER_SPAN_DIFFERS`. The batch stopped and the final input was not attempted. Both complete request/response captures are retained in private hash-addressed Blob storage, alongside the failed result. No retries, estate reads or graph mutations were performed. Result SHA-256: `eb43be7af0b67102dc4eeae0871e3ed13f204a7963cee5053be2e3418ba0d3e1`. Shared-ledger model charge: USD0.088833.

The seven proposals remain reviewable evidence, not published graph truth. Exact span validity does not prove semantic correctness or deployment; these fixture-authoring procedure declarations explicitly do not establish deployment. End-to-end procedure verification remains unavailable. The earlier pre-provider failure and its conservatively charged planner reservation remain unchanged.

## Terminal results, 08:47 UTC

Final retry `job-dia-worker-62ij1pe` ran08:34:15?08:42:43 UTC and returned **VERIFICATION_STOPPED** with `ValueError: VERIFICATION_PREWARM_SOURCE_NOT_DECLARED`. Zero physical/control/verification/diagnostic/model requests were made, and no reservation remains open. Result ZIP SHA256 `00ab7e48ee015de1ffe975e6d4c39694eee61c6d5256c63d89f53fe07a4b52e0`; tapeSHA256 `a6bc6e8c131f693000f7fe4cc7f00685fc6b72a55b60632ffa5cd0c4a0ceb67a`. The successful container status means it packaged its failure, not that verification passed. Exact verification replay/readiness/demo were not reached. No replacement attempt.

Cause: the operator selected the manifest's serverless application asset for prewarm, but none of the18 binding proposals uses that application source. Their four source locations are retained OneLake Bronze/Silver movement/rate tables. The guard correctly refused an out-of-batch source; no application connection was attempted. The offline admission plan checked prewarm shape but missed that cross-reference. This is an input/preflight defect, not a permission or Azure outage finding. Original input/spec/capture stay unchanged.

The existing job now reads back **Schedule**, cron `0 */6 * * *`, timeout600seconds, retry0, .5vCPU/1GiB, same managed identity; provisioning **Succeeded**. No new resource or role. Exact proposed template matches the returned template. Azure adds null inactive manual/event trigger fields; every declared configuration field matches exactly. The PATCH CLI returned exit0 with no JSON body, causing the operator decoder to raise; the PATCH was **not repeated**. An independent GET established applied state. Both the initial strict representation mismatch and the final semantic readback are retained. Final receipt `schedule-final-readback.json`; beforeSHA256 `d1bd23cb08526751f1070390a9bbd8ac69608124a7f9a4e4525a2c44a6964fe0`, afterSHA256 `1c87845f4dc2ecd18cef80da0dbacb4528a46a1f490eb4bd67ce053263590cf3`. First timed execution has not occurred; the equivalent two-estate manual scan is the live evidence.

At08:47:05UTC: round36/1500physical (6SETTLED,30UNCERTAIN retained provider failures), rolling312/3000, reserve95untouched. Two actual model calls costUSD0.088833; one additional pre-dispatch planner reservation remains conservatively UNCERTAIN but settled, with no model charge. Shared modelUSD108.046558, ceilingUSD132.957725, protectedUSD10. No open reservation. Archive controller exited afterfour bounded batches; all original receipts retained.

Offline correction after the terminal failure: retained-source preflight now runs before PostgreSQL candidate publication and before capture/usage reservation. A prewarm request cannot be admitted without its source scope being resolved, and unrelated manifest assets still refuse. The actual failed inputs reproduce the refusal offline; a separate in-memory prospective spec omitting the unrelated prewarm field plans 18 bindings/40 probes. No new input was published and no live retry was run. See `round-nineteen-prewarm-admission.md`. Engine changes require new pins for any future verification; the scheduled scanner remains on the separately tested ef31595 digest.
