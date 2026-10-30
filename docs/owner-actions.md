# Owner actions and deferred options

## Round Nineteen verified archive cleanup (2026-10-13)

The source export has a SHA-verified private Blob archive, but automatic approval review rejected the local cleanup command before launch with `blocked by policy`. Original files remain. Prepared owner command: `powershell -NoProfile -File D:\data_investigation_agent\.local\round-nineteen\source-export-archive\cleanup-verified.ps1`. It checks hashes and path containment before removal. No alternative deletion was attempted. See round-nineteen-archive-storage.md for manifest/receipt hashes. This does not block independent graph/state work.

## Current authority record

The prior Key Vault data-plane refusal is resolved as an authority decision:
the owner explicitly approved Key Vault Secrets Officer on the one installation
vault on 2026-10-12. The operator applied it at 02:41:15 UTC; the subsequent
secret-metadata listing passed and returned `[]`. This does not prove worker
secret retrieval or authorize any other vault. The detailed execution receipts
and scope record remain in the round's owner-controlled delivery record.

The owner also approved moving the existing read-only user's delegated cache to
that vault for this cross-tenant test. It remains the same user and existing
scope. The platform managed identity fetches the secret; the user performs the
estate read. Definition-only Contributor credentials must not serve quantities.
There is no automatic CLI/operator fallback. Platform managed-identity health subsequently passed for PostgreSQL, Blob and
Key Vault; the existing delegated reader authenticated separately for its Power
BI and SQL audiences. These are platform/authentication facts, not estate route
readiness. No further owner approval is requested at this checkpoint. The
application SQL workstation credential has not been made a cloud route and stays
explicitly unreachable; any future migration or new scope needs its own recorded
authority decision. Current bounded cloud verification and demo remain operator
work, not an unexplained owner action.

## Future option only: secretless cross-tenant estate access

No app registration, federation or permission change is performed by this guide.
For a future client installation, deploy in the Fabric tenant and use direct
managed identity where the particular API supports it and access is approved.

A possible cross-tenant alternative is a multitenant Entra application, a service
principal provisioned/consented in the resource tenant, and an application
federated identity credential trusting the worker's user-assigned managed
identity. The application and managed identity belong to the same home tenant;
the trust identifies the MI principal, tenant issuer and token-exchange audience.
This removes a stored app secret but does not grant target-resource access or
override Fabric API limitations. It needs a separately reviewed application,
consent and scope decision before implementation. See the
[Microsoft Learn configuration requirements](https://learn.microsoft.com/en-us/entra/workload-id/workload-identity-federation-config-app-trust-managed-identity)
and the [general-availability announcement](https://devblogs.microsoft.com/identity/access-cloud-resources-across-tenants-without-secrets-ga/).


## Round Eighteen close (2026-10-13)

No new owner permission is requested to explain the unfinished demo. Both fresh cloud verifications passed their reader probes but failed exact replay; no demo was admitted. The request-normalization fix is implemented offline, but a subsequent operator session must prepare new engine/context pins, earn exact verification, and then attempt the demo. Old witnesses cannot be transferred. Full claim-first/case-file shared persistence, complete client preflight, archive conversion and retention enforcement are engineering work, not missing human approval. Source-application cloud authentication and cross-tenant federation remain separately governed future decisions.

## Round Nineteen remaining boundaries (2026-10-13)

The dedicated federated investigator exists and authenticates; this supersedes the Round Eighteen future-identity wording above, not its historical results. The former user-cache secrets are retained until the replacement passes end to end. No broader reader grant is requested or applied.

The actual reader can list both workspaces but cannot refresh the configured native definitions. Exact per-item 401 Unauthorized / 404 EntityNotFound and unsupported-kind results: `round-nineteen-live-metadata-scan.json`. The controlled fixture report's read returned 404, so no live filter mutation was admitted. A future collection route must establish that baseline before changing the fixture. Report/generic definition APIs document item write requirements; INFO.CALCDEPENDENCY documents model write requirements. Those are incompatible with this reader's approved scope. Do not solve them by silently adding write or substituting publisher reads. A separately declared retained-definition/Git source would need explicit provenance, while the missing engine dependency remains a named gap.

The archive is partial and all originals remain. Checkpoint04 proves 1,308 paths in private storage, not all rounds five-seventeen. The previously prepared owner cleanup command remains the only deletion route; no alternate tool deletion was attempted. Resume further bounded batches from checkpoint04 after inspecting the live-state/opaque-container exclusions.

Historical pipeline and handoff claim catalogs remain distinct because the primary runtime migration lacks two referenced sessions. `claim-catalog-migration-plan.md` records exact hashes and the missing references. Complete isolated namespace migration with the full runtime histories is engineering work; do not import dangling claim rows or claim the local SQLite dependency is eliminated.

## 2026-10-13: cloud Bronze proof remains unearned

The single owner-approved SQL check consumed4settled requests but its operator capture header failed finalization before upload; the native result is unavailable. No additional full verification/demo was admitted. No permissions were changed: investigator already has Viewer and the endpoint matches. Any future check needs separate bounded approval, a successfully tested capture wrapper (including failure upload), fresh immutable image and offline admission. Original18456 and both operator failures remain recorded in docs/round-nineteen-b-bronze-diagnosis.md. Schedule restored; lease released; no further SQL attempt authorized in this round.


## Post-round platform reachability and remaining cloud proof (2026-10-16)

The read-only closing PostgreSQL snapshot failed with `psycopg.errors.ConnectionTimeout: connection timeout expired` connecting to `pg-dia-d5dd7d65.postgres.database.azure.com:5432`. The cause is not established; no server setting, firewall, identity or permission was changed. Last verified counters remain dated2026-10-13T19:23:28Z. Future read-only checks: `Test-NetConnection pg-dia-d5dd7d65.postgres.database.azure.com -Port 5432`; `az postgres flexible-server show --resource-group rg-dia-platform --name pg-dia-d5dd7d65 --output json`. A fresh successful readback is needed before another live admission.

The sole approved Bronze probe was consumed and its result was lost by operator finalization; no further probe/demo was admitted. Any later attempt needs a fresh owner decision and a valid capture header with independent failure-safe upload, followed by the unchanged read-only, runtime, lease, budget and exact-replay requirements. The source-path/compiler gaps and partial archive are detailed in round-nineteen-b-summary.md. Existing local worktrees and the pinned cleanup helper remain.

## 2026-10-21: Power BI Execute Queries 401 — owner inspection, no grant applied

Both fresh cloud requests (original and without INFO.PROPERTIES) return HTTP401 PowerBINotAuthorizedException. Audience/tenant match, investigator group membership and model ReadExplore grant are present, and both relevant tenant settings are enabled without returned group exclusions. See round-twenty-dax-authorization.md. No specific missing grant is established, so no permission or setting was changed.

Owner checks in the Fabric tenant: (1) select workspace149f8d99-1c66-4a0a-9624-759be002bb60/model3484a2bc-98c5-4cef-be5c-a6215484075e, open Manage permissions, confirm dia-investigator-round19-api-readers has Read and Build; (2) Fabric Admin portal ? Tenant settings ? Service principals can use Fabric/Power BI APIs and Dataset Execute Queries REST API, confirm enabled and no security-group exclusion of79c75be9-d8c3-4824-91c2-fc945041a8c3; (3) inspect model Security and data-source SSO configuration: Microsoft does not support Execute Queries by service principal for RLS/SSO datasets. Report the actual setting before proposing a change. Do not disable RLS/SSO, add write, impersonate a user, or broaden workspace scope to obtain a demonstration. If all agree, retain the request IDs/service error for Microsoft support; the remaining cause is not established by HTTP401 alone. Continue unrelated engineering meanwhile.

Specific remaining model inspection: Settings ? Gateway and cloud connections ? mapped cloud connection ? Authentication method and “Use SSO via Microsoft Entra ID for DirectQuery and Direct Lake queries.” Record connection ID and SSO checkbox value, without toggling/rebinding it. DirectLake defaults to SSO; Automatic is consistent with an implicit connection but is not an actual singleSignOnType readback. https://learn.microsoft.com/en-us/fabric/fundamentals/direct-lake-security-integration and https://learn.microsoft.com/en-us/rest/api/fabric/core/connections/get-connection .


### 2026-10-21: provision approved monthly model policy without elevating worker

Demo04 final catalog retains InsufficientPrivilege at build_phase.ensure_model_account INSERT into state_accounts. Worker intentionally has SELECT and column-level UPDATE, not INSERT. Monthly-budget code wrongly assumed it could create policy. Fix: explicit MONTHLY_MODEL_ACCOUNT_NOT_PROVISIONED hold. Do not grant account INSERT to worker.

Existing owner migration connection timed out on three attempts. Current outward IP184.105.12.85 differs from existing OwnerCurrentIp firewall209.240.14.44. This supports a network cause, not proof of a password/role defect. No firewall, role, identity or server setting changed; no account was created by failed attempts.

From an already allowed owner host, or Azure Cloud Shell using existing AllowAzureServices, sign in as the existing subscription owner and run:

```powershell
$env:PYTHONPATH='scripts'
python scripts/provision_model_month.py --host pg-dia-d5dd7d65.postgres.database.azure.com --database investigator --owner leelamounika14@gmail.com
```

Uses existing owner Entra token in memory; creates only current UTC month's approved $40 account and opening audit if absent. Preserves all history; prints bounded counters, no token. No permission grant or credential storage. Repeat as owner setup at month boundary; automated least-privilege rollover is future work. A firewall update, if chosen, needs a separate owner network decision; do not widen automatically.


### 2026-10-22 00:10UTC (owner date October21): confirmed demo-model SSO blocker

The browser now confirms Maps to = Default: Single Sign-On (Entra ID) for Warehouse Operations e1b8e1, model3484a2bc-98c5-4cef-be5c-a6215484075e. This replaces the earlier request to inspect whether SSO is present; it is present. Token/grants/two API settings are already correct. No extra tenant setting or wider reader role fixes Execute Queries' documented service-principal/SSO incompatibility.

Owner-controlled connection-change path, NOT APPLIED:
1. Open the exact model settings URL in docs/runs/round-twenty-dax-sso-setting.json, Gateway and cloud connections. Inspect model Security separately; RLS is another service-principal REST exclusion and must not be disabled for this demo.
2. If owner chooses fixed-identity access, approve the exact existing read-only data-source identity and supported authentication method first. No new identity, secret, role or credential is authorized by this note.
3. In Cloud connections, Maps to, choose Create a connection (the current menu has no existing fixed-identity connection). Retain the current Gold server and database77c49180-2ef9-4558-837c-f50fdb1df8de. Configure the owner-approved fixed identity with SSO off; do not impersonate a user or grant write. If the platform requires a new credential or scope, that is a separate section8 decision.
4. After owner creates it, select that named connection under Maps to and Apply. Record before/after binding, authentication identity, affected model and approval. Re-run a bounded native authorization check as the unchanged investigator before another technical investigation.

Alternative engineering path: evaluate a supported read-only XMLA query adapter without changing this model's SSO. That protocol is not implemented or authorized by the current REST receipt; do not silently substitute it. Until a path is chosen, native REST remains blocked. Documentation: https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/execute-queries-in-group .


## 2026-10-21 owner unblock: PostgreSQL completed; model connection needs browser action

The earlier PostgreSQL owner action is completed: current single-IP firewall replacement and October/November $40 policy accounts verified, worker role unchanged. December onward still requires the owner monthly provisioning step above. Exact connection click steps and portal authentication error: [round-twenty-owner-unblock.md](round-twenty-owner-unblock.md). The owner has approved fixed identity; the remaining action is performing the supported OAuth connection flow, not another permission approval. No rerun or merge has occurred behind this prerequisite.


## 2026-10-21 fixed connection action completed; credential expires November21UTC

The earlier interactive-reader connection steps are superseded: owner explicitly approved a30-day secret on the existing investigator application, and both fixed connections are now bound/readback verified via documented APIs. No interactive reader password is needed. See round-twenty-fixed-identity-controls.json. The connection credential expires2026-11-21T00:59:55Z (November20,18:59Central). Before expiry, owner must decide whether to rotate this same-purpose credential or replace it with a supported secretless connection. No automatic new credential or permission grant is authorized. Existing worker federation is unchanged.


Round Twenty owner-action status,2026-10-21/UTC22: fixed-identity fixture/billing connections, approved30-day credential in existing KeyVault, current single-IP PostgreSQL firewall, and October/November budget accounts are COMPLETE; do not repeat older unblock/grant instructions above. No immediate owner action is needed. Rotate the approved fixed-connection credential before2026-11-21T00:59:55Z (Nov20,18:59Central), with a new explicit credential decision. Remaining engineering: outer job finalization failure (no exit reason retained), current-image replay confirmation after accounting repair, practical path-proof attachment and billing SUMX/RELATED graph attachment. No permission broadening is proposed for these.


Round Twenty release clarification, UTC2026-10-22: the approved fixed-connection credential expires2026-11-21T00:59:55Z. Any authorised rotation must update the existing app credential, its Key Vault secret and both Fabric connection credentials; Key Vault rotation alone does not update the encrypted Fabric connections. No rotation or extra permission was performed at release.


## RoundTwenty-One enrichment key, owner2026-10-22

Create an Anthropic API key in Anthropic Console using existing credit, then run: `az keyvault secret set --vault-name kv-dia-d5dd7d65 --name anthropic-api-key --file <path-to-a-file-with-the-key>`. Delete that owner-created file afterwards. Do not paste the key into chat or repository. Enrichment remains recorded-stub only until the key is present; existing investigator provider does not change. Approved enrichment spendUSD25 separately tracked.


## Round22 source-control firewall, 2026-10-23

No source mutation occurred. The existing SQL owner control first returned40613 while ordersops was unavailable; Azure then reported Online/resumed18:40:18UTC. The next control returned40615: client184.105.12.85 is not allowed. Current investigator-client-20260918 permits only50.172.159.187/32. This is a network rule, not a SQL role failure. A new network scope is not inferred from reversible fault authority. If the owner approves replacing that existing laptop rule only, the prepared command is:

`powershell
az sql server firewall-rule update --resource-group rg-investigator-dev --server sql-orderops-9696025 --name investigator-client-20260918 --start-ip-address 184.105.12.85 --end-ip-address 184.105.12.85
`

Not executed. Do not change AllowAllWindowsAzureIps or the separate QueryEditor rule. Readback and current outward-IP confirmation are required before an approved update; the address can change. Continue cloud-reader and offline work meanwhile. Both original SQL errors and their charges remain in the run ledger. No identity, role, credential or firewall was changed.


Round22 firewall action completed2026-10-23 after explicit owner approval: only investigator-client-20260918 replaced50.172.159.187/32 with confirmed184.105.12.85/32. Exact before/after and approval in runs/round-twenty-two-approved-source-firewall.json; other rules unchanged. Do not repeat the prepared command above.

## Round23 security metadata gaps, 2026-10-26

BLOCKED_PENDING_OWNER: live role membership/effective-user security metadata has no read-only installed route. Provide a dated export of model roles, group/role membership and any security mapping table under an approved read-only collection route. Do not grant investigator Write. Microsoft documents [List item connections](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/list-item-connections) as requiring item read and write, and [Get dataset users](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/get-dataset-users-in-group) as requiring ReadWriteReshare; neither is a reason to elevate the reader. Retained RLS/OLS definitions are available as snapshots, not fresh memberships. Exact current-reader connection probes will be recorded separately.

Fixture controllers: existing cloud investigator identity is read-only, so it cannot apply or restore data, model SSO/automatic-update settings or pipeline definitions. No owner/publisher credential is migrated to the cloud. Those controls remain local under the existing publisher/fixture owner for this round; scoped cloud controller authority needs a separate owner decision.


Round23 billing bootstrap rerun issue, 2026-10-27: existing pipeline76c60248-b830-433b-9880-90593da28e7e original BuildSilverAndGold starts with CREATE SCHEMA [bronze]. Its ordinary cleanup run5253b628-a8df-4586-831c-f41b169bb3f8 failed because that schema exists. Original definition is restored; no idempotency edit or expectation change was made. Owner/reviewer should decide whether this is a one-time bootstrap or a repeatable transform before any permanent fixture change. Round23 continues; this is not a role or secret request.


Round23 configuration finding,2026-10-27: the retained billing installation from the prior value-check has no APPLICATION layer or declared system_of_record. The checked graph likewise has no system_of_record declaration. Native source queries are readable under the existing grant, but equality must not manufacture a source-of-truth declaration. Billing whole-source consistency remains unestablished under this configuration. No role change or expectation edit was made; any explicit application-source declaration must be recorded separately from measured value agreement.


## Round23 dev audit review,2026-10-27

Review the five disagreements in grading-audit.md, especially the borderline harmful assertion that an earlier temporal version exists. Official scores unchanged; no further history diagnostic admitted. Resolve warehouse-scope-v2 unknown literal report ID before future runs without changing this round tickets/expectations. Sixteen complete dev causes remain unverified, not disproved. Prioritize route/identifier/query/completion issues in failure-backtrack.md. No new permission requested.


Round23 Azure model route issue,2026-10-27: aoai-investigator-9696025 (rg-investigator-dev), deployment investigator-quality-54 and alternate existing investigator-intake-f-55 both list Running/Succeeded with Responses support, but POST https://aoai-investigator-9696025.openai.azure.com/openai/v1/responses returned404 DeploymentNotFound on both. The same exact54 request failed in Azure smoke and laptop health control; no role, key, deployment or quota changed. Investigate the resource data-plane routing with Azure support or confirm a working existing deployment before relying on the legacy ledger demo. Do not redeploy or rotate credentials from this note. Exact errors/receipts: runs/round-twenty-three-azure-model-route-failure.json. Round23 build-phase release continues with the failed smoke reported; no green-smoke claim.


Round24: optional, owner only: delete the unused Azure OpenAI deployments after reviewing dependencies. No deletion or deployment change was performed. Practice injection controllers still use the existing local publisher/SQL-owner where cloud identity lacks mutation scope; no new cloud role inferred.


Round24 optional warm-worker proposal, not provisioned (2026-10-28UTC): at South Central US Standard consumption retail rates, a0.25vCPU/0.5GiB minimum replica costs aboutUSD5.832 per30-day month if entirely idle, orUSD19.44 if continuously active, before any remaining free grant and request/storage costs. Existing platform estimateUSD19.077 means even the gross idle addition would exceed theUSD20 platform cap. Keep current jobs scaling to zero; an owner decision is required before creating a warm service. Do not label all job/body timing difference as container startup: access audit and capture work also contribute. Official pricing: https://azure.microsoft.com/en-us/pricing/details/container-apps/ ; saved SouthCentralUS RetailAPI rate receipt is local round-twenty-four/aca-retail-prices.json.


## Round24 remaining owner/design decisions,2026-10-28

- Review the absent-record verdict terminology: observational source consistency versus not-found is not a judgment of business intent. Primary/secondary both18/20,harm0; their cause flag differs on that case. No v3expectation or score changed. Fix before-retention reasoning on future dev data, not by altering this held-out oracle.
- Native external application provenance is absent for the largest inline-seeded fixture notebook group; declare an actual source/binding only with native evidence. Legacy sample report interaction/filter semantics and missing physical columns remain open.
- Mutation controllers cannot move to the read-only cloud investigator without a separately approved control identity/scope. Existing local owner/publisher was used; no credential migration or extra grant performed.
- Measured held-out startup median25.41s,route/schema45.13s,triage28.01s. Prioritize lazy schema/job-only initialization and independent reads. Warm-worker gross idle5.832USD/month plus current19.878333estimate=25.710333USD before free grants, above20; no warm resource created.
- The old billing-account budget address's GET returned404; this does not establish absence at the current scope. Check current portal scope if confirming Azure alert delivery. No budget or role was changed. Native Cost Management query later succeeded and the existing platform cap remained in force.
- Optional unused Azure OpenAI deletion remains owner-only; nothing deleted. Existing billing bootstrap CREATE_SCHEMA2011 still needs an owner decision on idempotent reruns; no unplanned estate repair was performed.


Round24 later CI option: a hosted live Anthropic intake-quality job would need an explicitly scoped Key Vault/gateway/shared-budget installation. None was provisioned. Current hosted intake check is offline contracts only; sealed independently graded live results are recorded separately. The retired Azure-profile workflow is no longer dispatched.


<!-- ROUND24-COST-OBSERVATION-MAINTENANCE -->
Round24 scheduled-runner maintenance: the native owner Cost Management observation copied into the existing runner configurations reaches its24-hour freshness bound at 2026-10-29T10:26:13.778590+00:00. Refresh it from a new native response with the existing owner authority and publish that observation to the same jobs before later runs. Do not restamp the old observation, bypass the USD20cap or grant a wider role. Static cost-observation renewal remains an operational limitation; three immediate green smokes are not a multi-day stability claim. Financial response bodies remain local. No resource/identity/permission was changed for this item.


## HealthNet estate cost approval requested ? 2026-10-30

The owner-supplied hospital-estate-build.md section0.6 requires item-specific approval before provisioning. None of these items has been created. Offline generator/definition/test work continues; no DIA access, scan, or AI spend.

| Item | Configuration | Estimated incremental monthly USD | Pause/stop |
|---|---|---:|---|
| hn_clinical | Existing sql-orderops-9696025, Central US; GeneralPurpose Gen5 serverless max2/min0.5vCore,32GB, free-limit offer REQUIRED |0, conditional on native eligibility|Auto-pause60min, freeLimitExhaustionBehavior=AutoPause; no paid fallback|
| hn_billing | Same existing server; separate database with identical free-offer limits |0, same condition|Same; daily batched load and close sessions|
| HealthNet Analytics Fabric items | Existing capacity only; hn_raw, hn_dw, pipelines, Dataflow Gen2, notebook,3models/reports. No new capacity, scale-up or autoscale billing; project <=20GB including retained versions |0.46 storage estimate(20GB x0.023); request <=1/month for regional variation|Storage does not auto-pause. Clinical4-hourly/billingnightly batch; stop deployment if new paid SKU or >20GB projection needed|

The existing ordersops and billingapp databases native-readback useFreeLimit=true, exhaustion AutoPause and inactivity60; only2non-system databases currently exist. This does not establish new database eligibility: verify native settings individually before loading and refuse paid fallback.

Sources: [SQL free tier](https://learn.microsoft.com/en-us/azure/azure-sql/database/free-tier?view=azuresql), [serverless](https://learn.microsoft.com/en-us/azure/azure-sql/database/serverless-tier-overview?view=azuresql), [OneLake tiers](https://learn.microsoft.com/en-us/fabric/onelake/onelake-storage-tiers), [OneLake billing](https://learn.microsoft.com/en-us/fabric/onelake/onelake-consumption).

Approval requested for these3items and bounds only; no new identity, DIA grants, capacity change or paid SQL overage. Existing owner sign-ins only. Any additional connection-identity scope decision is recorded separately before applying it.


### HealthNet approval applied ? 2026-10-30

Owner decision: "Approve all three within these bounds" (the two $0 free-offer databases and HealthNet items on the existing capacity, incremental storage <=$1/month). Before: hn_clinical and hn_billing absent. Owner CLI created both on sql-orderops-9696025 in Central US. Fresh Azure readback: each Online, GP_S_Gen5 GeneralPurpose serverless, max 2/min 0.5 vCore, 32 GiB, autoPauseDelay 60, useFreeLimit=true, freeLimitExhaustionBehavior=AutoPause. No paid-overage fallback, capacity change, identity or DIA grant. Native receipts are local under .local/hospital-estate/. Fabric provisioning and storage verification remain pending.
