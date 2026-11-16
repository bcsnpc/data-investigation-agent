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





## Round 25: renew the native Azure cost observation



Run before 2026-10-29 10:26 UTC, then repeat within24hours while these static observations are used. Reason: the existing runner requires a fresh native cost response to enforce the unchanged USD20 platform cap; changing an old timestamp is not renewal.



```powershell

Set-Location 'C:\temp\dia-r25-quality'

& '.local\llm-env\Scripts\python.exe' 'scripts\renew_platform_cost_observation.py' --apply --publish-schedules --output '.local\round-twenty-five\cost-maintenance'

```



Uses only the existing owner Azure CLI sign-in. Financial response stays local; stdout contains timestamps, hashes and readback status only. Patches only existing cost-observation fields on the three existing jobs, retaining image, schedules, resources, identity and all scopes. A throttled read backs off; a failed read never invents an observation. If it lapses, Round25 measurement continues as owner-directed, with the lapse recorded; no budget cap or permission is widened.



Round25 checkpoint2026-10-28: no new identity, scope or resource approval is required for the prepared November continuation. The existing native model account and physical policy were read back (150USD;9000total,2500SCAN/6405INV/95REST). October has37INV requests remaining versus the40-request case bound. Retain the previously documented cost-observation renewal command; the current observation expires2026-10-29T15:42UTC and a lapse is recorded, not a live-quality gate, under the owner prompt.



### Round25 stale-control UI follow-up, 2026-10-31

Browser control stopped before input because Edge's current URL could not be verified. No setting changed. If the stale cohorts are still pending, use the existing Fabric owner session: fixture workspace ? semantic model **Application load fixture 20261003** (`0c89889c-6fe6-49ab-91e9-4b00a51070e6`) ? Settings ? Direct Lake ? **Keep your Direct Lake data up to date**. The controlled cohort needs an actual fresh OFF observation, then its real +31 copy and scoped admissions; afterwards restore ON, refresh this same model and verify 7,661. Do not turn it off while another fault cohort is active. The existing publisher's SDK-derived settings POST previously returned401; this is not permission to add a role or fabricate UI evidence. No owner action has been executed by this entry.



2026-10-31 Round25 browser follow-up: the owner left the fixture workspace loaded in Edge. Computer Use reached the existing Application load fixture20261003 settings; automatic updates were natively readON, temporarily setOFF for the approved G2 stale cohort and independently readOFF after closing/reopening the panel. No additional owner sign-in, credential or permission was needed. The earlier browser-navigation action is no longer blocking G2; final ON/refresh restoration remains operator-owned until the cohort closes. This does not resolve or supersede any separate HealthNet owner actions.



2026-10-31 follow-up: G2 automatic-update restoration is now complete. Same model readOn, native own refreshCompleted, model7661 verified; originalsourcehash/realcopyrestored. No owner browser action remains for G2. See docs/runs/round25-g2-stale-final-restoration.json. G3/G4 still require their own approved reversible stale controls if admitted; they have not run yet.

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





### HealthNet source connection setup ? 2026-10-30



Owner-side source loading works with the existing Azure owner Entra sign-in (verified hn_clinical, CURRENT_USER=dbo). Fabric has no existing connection for either new database. The Fabric connection API does not create OAuth2 credentials, and browser automation stopped because it could not determine the browser URL for policy checks; no browser setting was bypassed. To create the two owner connections: Fabric Settings > Manage connections and gateways > New > Cloud > SQL Server; server sql-orderops-9696025.database.windows.net, database hn_clinical (then hn_billing); use the existing Azure owner Entra account leelamounika14@gmail.com, privacy Organizational. Name connections HealthNet Clinical Owner and HealthNet Billing Owner. Do not use DIA investigator/scanner or grant them access. Record the returned connection IDs; no password/token should be shared in chat. Also create the HealthNet warehouse owner OAuth connection after the warehouse endpoint is read back. This is a deployment blocker, not permission to substitute a new identity or persist an admin secret.



### HealthNet later DIA access ? NOT APPLIED



A separate owner decision is required later for the existing DIA investigator: workspace Viewer on HealthNet Analytics; contained db_datareader in hn_clinical and hn_billing; read-only warehouse access on hn_dw. Scanner needs only its established metadata/definition-read pattern for this workspace, with no data-write or broad tenant role. These are future requested scopes, not grants made by this build. The exact object IDs and native before-listings must be collected when that later decision is considered. No investigator or scanner has been added to this workspace or the new databases.

Hospital connection checkpoint, 2026-10-30: Edge control recovered and the owner completed OAuth sign-in, but saving HealthNet Clinical Owner returned a refresh-token-expired error. No connection success is claimed. Owner reauthentication/save requested; no admin credential migration, grant or identity change. Other build work continues.



### HealthNet owner-build completion, 2026-10-30 (America/Chicago)



The owner-approved two SQL free-offer databases and HealthNet Analytics on the existing FTL4 trial capacity are built. All five owner connections were saved/verified; the earlier connection-creation blockers are resolved. No DIA identity was granted access. Native source/raw/marts, nightly integration, models, rendered reports,12role simulations,2bookmarks and drill-through have recorded checks. Temporary OLS page was restored by matching the exact original definition hash.



Future-only access remains unapplied: existing DIA investigator workspaceViewer and modelRead+Build as needed, db_datareader in hn_clinical and hn_billing and hn_dw, scanner definition-read permissions on the explicitly selected HealthNet items, and appropriate model-role mapping/membership for each actual reader. Read+Build/Viewer must not be described as bypassing model RLS. No account, permission, secret or tenant setting is changed by this note. Exact future principals/scopes require their own approval before execution.



Cost boundary:SQLuseFreeLimit=true,mandatoryAutoPauseatfreeceiling,60minuteinactivitypause; currentOneLake~0.8GB (~$0.02/monthillustrative), approvedincrementalstorage<= $1/month; existingcapacityunchanged. Trialhas9daysleft:owner must choose future capacity before expiry if continued availability is needed. No paid fallback authorized or provisioned. Daily pipelines beginNov1UTC; fullImportrefreshesRevenue0430/Productivity0500. Incremental model refresh is not enabled; fixed historical seed uses full refresh to avoid silently aging rows out.





## Round 25 closeout — 2026-11-01



No new identity, permission, secret or paid-resource decision is needed to finish this measurement release. All requested cohorts completed and temporary fixtures were restored. Next-round design priorities, not changes made here: free-text intake and target preservation first; evidence-grounded history conclusions; supported native query syntax; complete automatic-update triage facts. Existing owner-action backlog remains. Quality is not established by release success: G2 headline 36/60 and G3 3/60, with five retained harmful answers across G1/G3. See [quality report](quality-report-v0.24.md).


## Round 26 OpenAI key — owner action, 2026-11-01

1. Sign in to https://platform.openai.com/api-keys in the intended funded project and create a project API key. Check the credit expiry and available balance in Billing before testing.
2. In your existing Azure-owner PowerShell session, run `powershell -ExecutionPolicy Bypass -File C:\temp\dia-r26-build\scripts\store_openai_key.ps1`. Enter the key only at its hidden prompt. The script restricts a random temporary file to your Windows account, uploads it with `az keyvault secret set --vault-name kv-dia-d5dd7d65 --name openai-api-key --file <temporary-file> --output none`, and removes the temporary file in `finally`.
3. Tell the agent the key is stored; never paste it into chat. The agent will perform a model-list request before any paid call. No new identity or permission is requested. Offline implementation continues meanwhile.

# Round 26 physical-request planning decision needed (2026-11-01)

The latest authoritative read is investigation 2,300/6,405, leaving 4,105. There are 91 unsaved benchmark outcomes, plus the required 80-ticket dev pass and 40-ticket v5 held-out pass. Their existing 40-request per-run bounds total 8,440. Three existing 100-request release-smoke bounds add 300; allow 800 for native-fact verification and reversible fault controls. This yields a conservative remaining bound of 9,540, a **5,435-request shortfall** against current investigation headroom. This is a planning upper bound, not a forecast of actual charges; saved results and subsequent actual consumption may reduce it. Further fix-loop passes and optional regressions are excluded.

Owner decision requested: add 5,500 investigation requests (monthly total 14,500; investigation 11,905; SCAN 2,500 and restoration 95 unchanged), or retain the current ceilings and record work that cannot fit as not run. No cap has been raised. The active benchmark uses the existing native limits and protects 1,900 investigation requests locally for held-out/release. Model caps and identity scopes remain unchanged.



Resolved 2026-11-01: owner approved the pending +5,500 investigation-request request. November cloud policy and source configuration updated and read back: total14,500 / INV11,905, unchanged SCAN2,500 / REST95 and model caps. See round-twenty-six-request-increase.json.


Round26 AWS: the approved owner CLI sign-in is open; only that sign-in is pending. Setup commands (no values): aws login --region us-east-1 --profile dia-owner-setup; aws iam create-policy --policy-name dia-bedrock-invoke --policy-document <Nova-only document>; aws iam create-user --user-name dia-bedrock; aws iam attach-user-policy --user-name dia-bedrock --policy-arn <created policy ARN>; aws iam create-access-key --user-name dia-bedrock (captured only in memory, never terminal output). Owner-authorized script PUTs values directly to KeyVault HTTPS in memory, then verifies aws sts get-caller-identity with only the ARN printed, calls aws logout, and verifies its isolated cache is cleared. Do not run create-access-key manually to the terminal. Claude provider balance remains unverified with the workspace key; no admin credential or new scope requested. The applied envelope uses the conservative owner29USD upper bound and3USDmargin.


SupersedesAWSsigninpending above: owneralready supplied approveddia-bedrockKeyVaultcredentials; STS andsingleNovaMicrosmokePASS. NoAWSowneractionpending; agentcreatednoIAMobject/key. Noownerlogincachepresent. IAMpermissionmembershipwasnotlistedwiththeinvocation-onlykey; noadditionalintrospectionrolewasrequested.

Bedrock Haiku credit coverage: 24 hours after the UTC time in docs/round-twenty-six-haiku-credit-test.json, check AWS Billing -> Bills for the Claude Haiku charge and credit application. Invocation success alone does not establish promotional credit eligibility. Do not enable further Claude Bedrock calls; guard remains on.

Final Haiku billing-check time supersedes the pre-dispatch attempt: after 2026-11-03T03:35:38.730142+00:00, AWS Billing -> Bills, check whether any Haiku charge exists and whether credits covered it. Single dispatched test returned HTTP404 ResourceNotFoundException, no successful inference; do not infer a charge or credit coverage. Claude Bedrock guard remains on.

After Round26, review public v2-warehouse-scope-v2 report-address typo against native catalog. Existing input/expectation and this round score remain unchanged; do not silently repair it during measurement. Native/input receipt in dev01/invalid-form-address-finding.json.


Round26 owner credit addition, 2026-11-02: owner reports about $74 Anthropic credit, exclusively for gated Opus calibration and v5, with $3 reserved and auto-reload off. Exact Console verification is pending: native computer-use pipe returned os error 2; browser inventory returned no connected browsers and "The browser access host is unavailable." Existing workspace API credential is not billing/Admin scoped. The owner was asked for the exact displayed balance while implementation continues. No extra identity, credential, permission or auto-reload was requested or changed. Existing conservative Anthropic ceiling remains until the exact usable balance is reconciled; gates remain unchanged.


## Owner disk recovery ? 2026-11-10

Removed 3,538 `__pycache__` folders containing only regenerable `.pyc`/`.pyo` files (0.753 GiB logical), pip cache artifacts (674 files, 135.2 MB reported), and npm content-cache artifacts through its own purge command. The npm `_npx`, `_prebuilds` and `_logs` directories remain; the earlier 193,445-file / 2.861 GiB count described the entire cache before purging and is not claimed as space freed. Raw AppData folder deletion was rejected by automatic review; the narrower package-manager purges succeeded. No Docker executable was available. No old worktree was removed: dirty or unpushed trees were excluded.

Preserved all evidence: moved cold `.local/round-thirteen` and `.local/round-nineteen-b` to `C:/temp/dia-r26-cold-evidence/`, verified all 2,164 + 640 file SHA-256 hashes, and restored both original D: paths as junctions. This is reversible same-machine storage movement, not Blob publication or evidence disposal. Round 26 captures/logs/grades, sealed sets/seals, ledgers, RESUME files, current worktree and pinned images were untouched.

D: free space increased from 5.88 to 15.36 GiB (net 9.48 GiB recovered). Local path-level deletion list: `.local/round-twenty-six/resume-20261110/pycache-removed.json`; move manifests include every original file hash. Public aggregate: `docs/round-twenty-six-resume-disk-cleanup.json`. New ticket admissions require at least 15 GiB free.


Recovery UI check, 2026-11-10: native computer control reconnected, but the owner stopped it with physical Escape before the Direct Lake automatic-update setting could be read. No UI setting was changed. Today's native source/schema hashes and model7,661 pass; automatic updates ON remains a prior owner report, not a fresh UI verification. No scored admission follows this incomplete check.


## Round26 closing review items (2026-11-11 UTC)

- OpenAI credit expiry is still not established by the earlier placeholder reply; check the funded project expiry in Console. No key or billing credential is needed in chat.
- The single approved Haiku credit test was already made (404, no retry); check AWS Billing → Bills for coverage after24hours. Claude-on-Bedrock remains disabled.
- Next round: review the unchanged stale named-cause expectation against Round26 PartD's API-limitation fallback. Saved answers can establish the model/data gap and timestamps without observing the automatic-update switch. No score or expectation was changed.
- The Round27 code-blind review lists25every-graded-appearance failures. Seven expectations were established by those packets; eighteen remained unverifiable, not declared wrong. Review the evidence gaps and the retained unknown legacy warehouse-form address before proposing any future expectation change.
- PostgreSQL capacity was not established as the cause; do not infer a tier change from laptop CLI startup timeouts. No tier or permission increase was taken.


Owner-approved disk cleanup and post-release archive direction, 2026-11-10 (Chicago; execution UTC2026-11-11): remove only named regenerable npm/uv/VSCode-installer caches, split_loop_v1 build/.dart_tool, dependencies/build outputs in portfolio/nifty/quiz/Vilsem/semantic_app, and obsolete Codex runtimes while retaining the active one. No evidence deletion during Round26. Initial npm _npx removal is logged privately; remaining deletions and measured drive deltas will be filled from completion receipts. VSCode installer target is active in CodeSetup and retained. Conditional semantic_app/cache contains QA screenshots/logs, scripts and report artifacts; D:/cache contains release-check/staging directories whose provenance and current use are not established; Temp/claude contains scratchpad scripts/output and package cache mixed together. All three retained rather than treating their folder names as proof of disposability. Current runtime path is C:/Users/chait/.cache/codex-runtimes/codex-primary-runtime; its node process was observed in use.
After merge and v0.26 tag only: inventory references from current tests/scripts/runtime to process-tapes and old round folders, retain all referenced/protected files (ledgers, RESUME, seals, held-out, current captures), losslessly compress eligible unreferenced evidence, upload to existing private Blob via service-validated Content-MD5 and client SHA256, verify the stored upload checksum before setting Archive tier, and only then remove each verified local file. No readback download and no new resource/permission/identity. This is a queued post-release task, not a claim that archives or deletions are complete.

Cleanup completion receipt (owner2026-11-10): approved npm/uv caches, seven obsolete runtime directories, Flutter build/.dart_tool and the named projects' dependency/build outputs removed; the active runtime and installer plus the locked previous runtime remain. All52 source/configuration/lockfile SHA256 checks match. The standalone D cleanup interval gained9,616,830,464 bytes net (8.96GiB); this excludes earlier partial Flutter removal. C free-space deltas varied with concurrent paging and are not asserted as cleanup-only savings. Full removed-path list and current drive observations: docs/round-twenty-six-owner-cleanup.json. No evidence folder was deleted or archived; the owner-approved archive task remains gated on merge and v0.26 tagging.


Round26 final calibration,2026-11-11: Final calibration quality gate failed2/10,harm2; held-out v5 is intentionally not run and needs no credit top-up this round. Keep it sealed. No further dev loop is authorised. Continue release checks. Post-release evidence archive work remains gated on merged/tagged round and dependency/hash checks; no evidence was cleaned during Round26.



## Full disk cleanup — owner instruction 2026-11-13, executed from 2026-11-15

Round 26 was paused throughout cleanup; no ticket or model run was admitted. Existing release smoke captures were recovered without resubmitting their runs.

| Drive | Initial free GB | Final free GB | Net recovered GB | Target GB |
|---|---:|---:|---:|---:|
| C: | 14.65 | 73.87 | 59.22 | 60 |
| D: | 23.18 | 197.80 | 174.61 | 120 |

GB is decimal. Free space is the authoritative volume measurement. File sizes below are logical or allocated bytes as labelled; they are not additive estimates of exact space freed. Paging, running applications, sparse/compressed files, hard links and temporary archive staging affect volume deltas.

| Step | Completed work / measured amount |
|---|---|
| Processes | No abandoned DIA controller/poller/grader was found initially. Active Codex and user apps were retained. Only this cleanup’s own metadata scans/preparation were stopped or paused to avoid redundant disk traffic. No Azure execution was killed. |
| Caches/build outputs | 1,346 project paths removed; 18 tracked-content paths retained. Removed paths total 15.35 GB of reported allocated pre-removal bytes. Cache roots are recorded separately and may overlap this amount. |
| Unused Python environments | 10 removed, after package/rebuild inventories and process checks. Current DIA and Azure CLI environments retained. |
| Duplicate replay copies | 2.98 GB logical removed only after exact hash match with retained canonical originals. |
| Historical evidence | 41,881 eligible files; 441.82 GB logical originals removed after verified upload; 248 immutable Archive batches. [Blob paths and checksums](evidence-archive.md). |
| Git duplicates | 13 clean, pushed worktrees and one redundant clone removed; canonical repositories, unique or unpushed work, dirty worktrees and protected ignored data retained. No forced git removal. |
| Docker / WSL | Docker installation/CLI absent; WSL reports not installed. No prune or VHDX compaction claimed. Claude app-state virtual disks retained because they are unrelated application data. |
| System | D: Recycle Bin cleared; C: returned path-not-found. DISM error740 required elevation; the approved elevation attempt was canceled. DISM/cleanmgr did not run. Page-file/hibernation settings unchanged. |

Removed cache categories: npm including `_npx`, pip, Electron/electron-builder, Dart Pub, Flutter SDK regenerable cache, Dart analysis cache, node-gyp, obsolete Codex runtime/installer versions, browser cache/code-cache/GPU/shader cache, identified temporary Node/Playwright outputs, and dependency/build/cache folders across DIA, vilsem, semantic_app, SplitLoop, portfolio, nifty, quiz and other projects. Source and lockfiles were excluded. Gradle locked/partial failures were retained and logged. Browser credentials, cookies and profiles were not cleared.

Source integrity: 52 source/config/lock-file checks; all content preserved: **True**. 50 files remain byte-identical in place; 2 package files belonged to the approved removed clean/pushed vilsem worktree and reconstruct to their exact original Windows CRLF SHA-256 from preserved Git commit 3e3fcc2bf8818d43c38293ef1b857339004bb499 in D:/semantic_app. The removed paths are not described as still present. Previously observed tracked deletions in other repositories were generated `dist` output, including nested renderer outputs; no missing source was inferred from those build artifacts.

The cleanup audit/rebuild manifests, per-file deletion journals, hash receipts and inventories are retained in `D:\data_investigation_agent\.local\round-twenty-six\full-disk-cleanup-20261115\`. Secrets and evidence bodies are not committed. A disposable junction-deletion test was rejected by automatic tool policy and never ran; read-only source integrity checks were used instead.

Administrator work remains optional and unexecuted: `D:\data_investigation_agent\.local\round-twenty-six\full-disk-cleanup-20261115\owner-admin-cleanup.ps1`. It selects Windows component/update/delivery-optimization/thumbnails/error/setup cleanup, excludes Downloads and broad Temp, and restores its cleanmgr selection flags. Page-file allocation observed:12,800MiB. No hibernation file size was established; no hibernation setting was changed.

### Retained evidence and unknown material

| Reason | Remaining logical GB |
|---|---:|
| CURRENT_REFERENCE_ID | 26.52 |
| SEALED_SET_OR_ORACLE_PROTECTED | 9.11 |
| CURRENT_LITERAL_PATH | 7.87 |
| UNIDENTIFIED_OR_CONTAINER_FILE_RETAINED | 6.43 |
| CURRENT_AUDIT_SCRIPT_INPUT | 1.60 |
| LEDGER_OR_ACCOUNTING_PROTECTED | 0.48 |
| SOURCE_OR_LOCKFILE_PROTECTED | 0.05 |
| RESUME_PROTECTED | 0.00 |
| SENSITIVE_PATH | 0.00 |
| CREDENTIAL_PATTERN | 0.00 |

Unidentified/container files were not unpacked or deleted:

| Retained source folder | Files | Logical GB | File types requiring review |
|---|---:|---:|---|
| `D:\data_investigation_agent\.local\round-eighteen` | 547 | 1.45 | (no suffix), .bundle, .gz, .idx, .pack, .rev, .sample, .zip |
| `D:\data_investigation_agent\.local\round-nineteen` | 13 | 1.23 | (no suffix), .gz, .zip |
| `C:\temp\dia-r26-cold-evidence` | 159 | 0.96 | (no suffix), .apply_patch, .before-checksum-02, .before-controller01-0000, .before-controller01-0001, .before-controller02-batch-0003, .before-controller02-batch-0005, .before-enhanced-security-40ce5de02316, .before-enterprise-binding-157b6386a218, .before-enterprise-binding-96a79fde3eae, .bin, .body, .exe, .exit, .partial, .patch, .zip |
| `D:\data_investigation_agent\.local\round-ten-20261007` | 8 | 0.93 | .claim, .gz, .initial-draft |
| `D:\data_investigation_agent\.local\round-twenty` | 1545 | 0.77 | (no suffix), .exit, .interrupted, .zip |
| `D:\data_investigation_agent\.local\round-seven-20261005` | 1 | 0.32 | .gz |
| `D:\data_investigation_agent\.local\round-six-20261005` | 2 | 0.25 | (no suffix), .aesgcm |
| `D:\data_investigation_agent\.local\round-five-i-20261005` | 1 | 0.25 | .gz |
| `D:\data_investigation_agent\.local\round-sixteen` | 19 | 0.18 | .bim, .patch, .pbir, .pbism, .zip |
| `C:\Users\chait\.codex\dia-round-thirteen-captures` | 16 | 0.04 | (no suffix), .bin, .dia2, .sqlite-journal |
| `D:\data_investigation_agent\.local\round-twenty-three` | 22 | 0.02 | .pid, .zip |
| `D:\data_investigation_agent\.local\round-twenty-five` | 11 | 0.01 | .pyc, .zip |
| `C:\temp\dia-hospital-estate\.local\hospital-estate` | 23 | 0.01 | .dll, .pbir, .pyc, .sqlite-journal |
| `D:\data_investigation_agent\.local\round-fourteen` | 5 | 0.01 | .patch, .prof, .sqlite-journal |
| `D:\data_investigation_agent\.local\round-twenty-four` | 1016 | 0.00 | (no suffix), .zip |
| `D:\dia-r18-final-tests\.local` | 409 | 0.00 | .body, .exit |
| `D:\data_investigation_agent\.local\process-tapes` | 3 | 0.00 | .bin, .sqlite-journal |
| `D:\data_investigation_agent\.local\round-nine-20261006` | 23 | 0.00 | (no suffix), .pyd, .pyi, .typed |
| `D:\data_investigation_agent\.local\round-twenty-one` | 968 | 0.00 | (no suffix), .exit, .superseded |
| `D:\dia-r14-ports-validation\.local` | 144 | 0.00 | .body |
| `D:\dia-r14-hybrid-capture\.local` | 96 | 0.00 | .body |
| `D:\dia-r14-empty-contract-validation\.local` | 96 | 0.00 | .body |
| `D:\dia-r14-hybrid-build\.local` | 96 | 0.00 | .body |
| `D:\dia-round-thirteen-regression\.local` | 68 | 0.00 | .body |
| `C:\temp\dia-r22-4d7-validation\.local` | 66 | 0.00 | .body |
| `C:\temp\dia-r22-temporal-validation\.local` | 66 | 0.00 | .body |
| `D:\dia-r18-validation-4377\.local` | 54 | 0.00 | .body |
| `D:\dia-r14-git-launch-validation\.local` | 48 | 0.00 | .body |
| `D:\dia-r14-punctuation-validation\.local` | 48 | 0.00 | .body |
| `D:\dia-r14-causal-validation\.local` | 34 | 0.00 | .body |
| `D:\dia-r14-final-validation\.local` | 34 | 0.00 | .body |
| `D:\dia-r14-regression-a985774\.local` | 34 | 0.00 | .body |
| `D:\dia-r14-rollback-validation\.local` | 34 | 0.00 | .body |
| `D:\dia-round-nine-validation-8de0e84\.local` | 16 | 0.00 | .body |
| `D:\dia-estate-manifest\.local` | 12 | 0.00 | .body |
| `D:\dia-round-five-manifest\.local` | 12 | 0.00 | .body |
| `D:\data_investigation_agent\.local\round-five-h-20261005` | 7 | 0.00 | (no suffix), .bim, .pbir, .pbism |
| `D:\data_investigation_agent\.local\round-seventeen` | 6 | 0.00 | (no suffix), .bim, .pbir, .pbism |
| `D:\data_investigation_agent\.local\round-five-e-live-20261005` | 1 | 0.00 | (no suffix) |
| `D:\data_investigation_agent\.local\round-six-g-20261005` | 3 | 0.00 | .claim |
| `D:\data_investigation_agent\.local\round-five-g-live-20261005` | 1 | 0.00 | (no suffix) |
| `D:\data_investigation_agent\.local\round-six-c-20261005` | 1 | 0.00 | (no suffix) |
| `D:\data_investigation_agent\.local\round-five-f-live-20261005` | 1 | 0.00 | (no suffix) |
| `D:\data_investigation_agent\.local\round-fifteen` | 2 | 0.00 | (no suffix), .exit |
| `D:\data_investigation_agent\.local\round-twelve-d` | 6 | 0.00 | .exit |
| `D:\data_investigation_agent\.local\round-twelve-e` | 6 | 0.00 | .exit |

These are surviving paths from the retention journal, deduplicated by path; they are not a claim that every remaining file was eligible for deletion. Unknown `semantic_app/cache`, `D:/cache` and `Temp/claude` contents were retained beyond positively identified regenerable dependencies. Unpushed demo work, current test/runtime inputs, all ledgers/seals/RESUME, and unrelated app state remain. No blanket deletion of Temp, Windows, or installed applications was attempted. Automatic tool policy rejected deletion of the identified remaining D:/pub-cache/hosted, hosted-hashes and _temp cache folders before execution, giving only blocked by policy; those folders remain and the action was not retried through another route.

### Personal folders — untouched

| Folder | Actual path | Logical GB |
|---|---|---:|
| Pictures | `C:\Users\chait\OneDrive\Pictures` | 3.74 |
| Documents | `C:\Users\chait\OneDrive\Documents` | 1.25 |
| Desktop | `C:\Users\chait\OneDrive\Desktop` | 0.09 |
| Downloads | `C:\Users\chait\Downloads` | 5.16 |
| Documents_unredirected | `C:\Users\chait\Documents` | 4.16 |

### Repository/worktree audit

The audit covered all discovered repository groups and worktrees; remote URLs and credential material are omitted. Pushed status is the recorded audit observation, not a guarantee about future remote retention. Installed plugins, unique projects, personal locations, unpushed work and protected ignored data were retained.

| Repository / worktree | HEAD | Pushed containing ref found | Disposition |
|---|---|---|---|
| `C:\Users\chait\.cache\plugins\.install-staging\3acb3ccb010bd3190b85841d8c364b5eb9541225\claude-code\repo` | `8db97f0ce511` | yes | Retained: working changes or generated-output deletions |
| `C:\Users\chait\.cache\plugins\github.com-vercel-vercel-plugin` | `8db97f0ce511` | yes | Retained: unique project, installed plugin or canonical repository |
| `C:\Users\chait\.claude\plugins\cache\vercel\vercel-plugin\8db97f0ce511` | `8db97f0ce511` | yes | Retained: working changes or generated-output deletions |
| `C:\Users\chait\.claude\plugins\marketplaces\vercel` | `8db97f0ce511` | yes | Retained: working changes or generated-output deletions |
| `C:\Users\chait\.codex\vendor_imports\skills` | `49f948faa925` | yes | Retained: unique project, installed plugin or canonical repository |
| `C:\Users\chait\AppData\Local\Temp\claude\c9570c89b2196cc7\aed82cb6-84a9-4dd3-bab9-e9ad69ead511\scratchpad\awesome` | `48dff43c3f7c` | no | Retained: pushed containing ref not confirmed |
| `C:\Users\chait\AppData\Local\Temp\claude\c9570c89b2196cc7\aed82cb6-84a9-4dd3-bab9-e9ad69ead511\scratchpad\sec\vilsem-app` | `db44ceb63cf5` | yes | Retained: unique project, installed plugin or canonical repository |
| `C:\Users\chait\AppData\Local\Temp\claude\c9570c89b2196cc7\aed82cb6-84a9-4dd3-bab9-e9ad69ead511\scratchpad\sec\vilsem-mcp` | `029a577307b8` | yes | Removed after clean/pushed/ignored-file checks |
| `C:\Users\chait\develop\flutter` | `2c9eb20739df` | yes | Retained: ignored source, protected or unidentified files |
| `D:\data_investigation_agent` | `1e702289a320` | yes | Retained: working changes or generated-output deletions |
| `C:\dia-r21-capture` | `8a18884e2738` | no | Retained: pushed containing ref not confirmed |
| `C:\dia-r21-facts-ledger` | `aa0f5aa6c805` | no | Retained: pushed containing ref not confirmed |
| `C:\temp\dia-hospital-estate` | `ee8b6bb37447` | yes | Retained: ignored source, protected or unidentified files |
| `C:\temp\dia-r21-access` | `886708fbd21d` | no | Retained: pushed containing ref not confirmed |
| `C:\temp\dia-r21-ask` | `4786b7a1cfe5` | no | Retained: pushed containing ref not confirmed |
| `C:\temp\dia-r21-collector-build` | `ce57e18c1529` | yes | Retained: working changes or generated-output deletions |
| `C:\temp\dia-r21-final-validation` | `8ae02f162850` | yes | Retained: ignored source, protected or unidentified files |
| `C:\temp\dia-r22-4d7-validation` | `4d7cac322808` | yes | Retained: ignored source, protected or unidentified files |
| `C:\temp\dia-r22-owner-steer` | `47b8f148a73b` | yes | Retained: working changes or generated-output deletions |
| `C:\temp\dia-r22-temporal-validation` | `fcce8061e451` | yes | Retained: ignored source, protected or unidentified files |
| `C:\temp\dia-r23-build` | `3dcb8ec379a2` | yes | Retained: ignored source, protected or unidentified files |
| `C:\temp\dia-r24-build` | `18b8859ddf6c` | yes | Retained: ignored source, protected or unidentified files |
| `C:\temp\dia-r24-main` | `edb04fd5bc0d` | yes | Retained: ignored source, protected or unidentified files |
| `C:\temp\dia-r25-main-release` | `188077989737` | yes | Retained: ignored source, protected or unidentified files |
| `C:\temp\dia-r25-quality` | `9c5e3026e599` | yes | Retained: ignored source, protected or unidentified files |
| `C:\temp\dia-r26-build` | `fafa046886fb` | yes | Current Round26 worktree; protected |
| `C:\temp\dia-round-twenty-two` | `9c770d322f2e` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-budget-inputs` | `9c32f42af81b` | yes | Retained: working changes or generated-output deletions |
| `D:\dia-declaration-contract` | `5f73e492b4e7` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-estate-manifest` | `b9b8be9781e0` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-fifteen-source-09ad` | `09ad88be0523` | yes | Retained: working changes or generated-output deletions |
| `D:\dia-fifteen-source-515` | `515bb1c1b536` | yes | Retained: working changes or generated-output deletions |
| `D:\dia-r14-catalog-guard` | `179ebe554f69` | no | Retained: working changes or generated-output deletions |
| `D:\dia-r14-causal-validation` | `2e7fde66fa60` | yes | Retained: working changes or generated-output deletions |
| `D:\dia-r14-clock-replay` | `bfea0318ea5f` | no | Retained: working changes or generated-output deletions |
| `D:\dia-r14-comment-clock` | `cc184f1bc2d6` | no | Retained: working changes or generated-output deletions |
| `D:\dia-r14-empty-contract-validation` | `4257bf4c2b0e` | yes | Retained: working changes or generated-output deletions |
| `D:\dia-r14-final-validation` | `8fa21616378d` | yes | Retained: working changes or generated-output deletions |
| `D:\dia-r14-git-launch-validation` | `ce0de1e7db84` | yes | Retained: working changes or generated-output deletions |
| `D:\dia-r14-hybrid-build` | `f9f360dd0736` | yes | Retained: working changes or generated-output deletions |
| `D:\dia-r14-hybrid-capture` | `8b5608ff1a5c` | yes | Retained: working changes or generated-output deletions |
| `D:\dia-r14-loop-clock` | `9ddad5b1fd01` | no | Retained: pushed containing ref not confirmed |
| `D:\dia-r14-ports-validation` | `29fefe890aa5` | yes | Retained: working changes or generated-output deletions |
| `D:\dia-r14-punctuation-validation` | `5b7796264067` | yes | Retained: working changes or generated-output deletions |
| `D:\dia-r14-regression-a985774` | `a985774dff87` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-r14-replay-9c` | `9c87b2a7755d` | yes | Retained: working changes or generated-output deletions |
| `D:\dia-r14-replay-bc0` | `bc0d671deeae` | yes | Retained: working changes or generated-output deletions |
| `D:\dia-r14-resolver-delivery` | `7763fa3d68cf` | no | Retained: working changes or generated-output deletions |
| `D:\dia-r14-result-reuse` | `39671813f23a` | no | Retained: pushed containing ref not confirmed |
| `D:\dia-r14-rollback-validation` | `551a04991b75` | yes | Retained: working changes or generated-output deletions |
| `D:\dia-r15-metadata-replay` | `9f7b42b7aee6` | yes | Retained: working changes or generated-output deletions |
| `D:\dia-r18-capture-export` | `63aa7569c2e0` | no | Retained: pushed containing ref not confirmed |
| `D:\dia-r18-estates` | `2bf05308e850` | no | Retained: pushed containing ref not confirmed |
| `D:\dia-r18-final-tests` | `db3bed8905c9` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-r18-guardrails` | `0c303661024b` | no | Retained: working changes or generated-output deletions |
| `D:\dia-r18-resume-stage` | `b8da799360af` | no | Retained: working changes or generated-output deletions |
| `D:\dia-r18-storage` | `32e65d3db196` | no | Retained: pushed containing ref not confirmed |
| `D:\dia-r18-validation-4377` | `4377cbfb7a0e` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-r19-graph` | `a14cfd2ab8d4` | no | Retained: working changes or generated-output deletions |
| `D:\dia-r19-main` | `44c1c60192a6` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-r19-state` | `892ae3c4cf84` | no | Retained: working changes or generated-output deletions |
| `D:\dia-r19-storage` | `196a9df36f0d` | no | Retained: pushed containing ref not confirmed |
| `D:\dia-r20-bronze` | `bad6f57b08c1` | no | Retained: working changes or generated-output deletions |
| `D:\dia-r20-confidence` | `a8740e4ed482` | no | Retained: pushed containing ref not confirmed |
| `D:\dia-r20-directlake` | `422fd5451c57` | no | Retained: pushed containing ref not confirmed |
| `D:\dia-r20-runner` | `d77c4ffd672e` | no | Retained: pushed containing ref not confirmed |
| `D:\dia-r20-schedules` | `e4838fbe7dfc` | no | Retained: pushed containing ref not confirmed |
| `D:\dia-r20-state` | `a186ced764ee` | no | Retained: pushed containing ref not confirmed |
| `D:\dia-r20-value-route` | `7f7ad1a7282a` | no | Retained: pushed containing ref not confirmed |
| `D:\dia-round-eight-offline` | `c23673d7cbc4` | yes | Retained: working changes or generated-output deletions |
| `D:\dia-round-eight-proposers` | `6a5551d3b805` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-round-eleven-demo` | `d4e420d89b18` | no | Retained: pushed containing ref not confirmed |
| `D:\dia-round-eleven-eval` | `9422f43a5390` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-round-eleven-final` | `44490b49315e` | yes | Retained: working changes or generated-output deletions |
| `D:\dia-round-eleven-intake` | `cc8b0d79380d` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-round-eleven-links` | `141991296962` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-round-fifteen-budget` | `518b59e0a4d3` | no | Retained: pushed containing ref not confirmed |
| `D:\dia-round-fifteen-demo` | `978f3b8f54fc` | no | Retained: pushed containing ref not confirmed |
| `D:\dia-round-five-manifest` | `ec5b8439bf09` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-round-nine-translation` | `feb0cc84c47f` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-round-nine-validation-4e61a5e` | `4e61a5eb7f57` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-round-nine-validation-55469a3` | `55469a39b907` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-round-nine-validation-5907162` | `59071626a503` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-round-nine-validation-5f09cec` | `5f09cec8da48` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-round-nine-validation-624ca67` | `624ca671290c` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-round-nine-validation-8de0e84` | `8de0e8473dac` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-round-nine-validation-review` | `bb3d27b8f24d` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-round-nine-validation-review-final` | `382cb1b54d61` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-round-nine-validation-v4` | `fa830490f5fb` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-round-seven-freshness` | `bfa6e920cba2` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-round-seven-gate` | `4539bac58290` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-round-seven-history` | `909a5af311eb` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-round-seven-install` | `d80792b9ecb9` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-round-seven-neutrality` | `edd5177bc1c2` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-round-seven-record` | `b244928e5e4d` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-round-six-c-main` | `78218b2c5668` | yes | Retained: working changes or generated-output deletions |
| `D:\dia-round-sixteen-smoke-source` | `a4654045e05d` | yes | Retained: working changes or generated-output deletions |
| `D:\dia-round-ten-e-baseline` | `45958a0d4f80` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-round-ten-filter-effects` | `5ae814cd8793` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-round-ten-intake-rules` | `4b6161ec5902` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-round-thirteen-regression` | `6af19177f40b` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-round-twelve-questionnaire` | `51070af3f778` | no | Retained: pushed containing ref not confirmed |
| `D:\dia-round-twenty` | `a9b54f23d8ca` | yes | Retained: working changes or generated-output deletions |
| `D:\dia-round-twenty-one` | `32f15e143d7f` | yes | Retained: ignored source, protected or unidentified files |
| `D:\dia-surface-inventory` | `54da37d7b5b1` | yes | Retained: ignored source, protected or unidentified files |
| `C:\temp\skynwhy-site-dia` | `41d54c227a35` | yes | Retained: unique project, installed plugin or canonical repository |
| `D:\Projects\dashboard-ai-desinger` | `000000000000` | no | Retained: working changes or generated-output deletions |
| `D:\Projects\semanticui` | `492038bf7573` | yes | Retained: working changes or generated-output deletions |
| `D:\cricfab` | `8574679a8187` | no | Retained: pushed containing ref not confirmed |
| `D:\nifty-predictor` | `7f79654753f5` | yes | Retained: working changes or generated-output deletions |
| `D:\nifty-predictor-temp` | `989598ab870c` | no | Retained: pushed containing ref not confirmed |
| `D:\portffolio_website` | `fbf527420ba3` | yes | Retained: working changes or generated-output deletions |
| `D:\portfolio-prompt-book-preview` | `92ad5859323d` | yes | Retained: ignored source, protected or unidentified files |
| `D:\semantic_app` | `147536d26386` | yes | Retained: working changes or generated-output deletions |
| `D:\semantic_app\cache\public-release-beta3` | `efddb3c9e746` | yes | Removed after clean/pushed/ignored-file checks |
| `D:\semantic_app\cache\release-beta3` | `a22aaa415aef` | yes | Retained: working changes or generated-output deletions |
| `D:\vilsem-core-release-040` | `3e3fcc2bf881` | yes | Removed after clean/pushed/ignored-file checks |
| `D:\vilsem-core-release-050` | `db44ceb63cf5` | yes | Retained: working changes or generated-output deletions |
| `D:\vilsem-public-core` | `713c4bc2fc62` | yes | Retained: working changes or generated-output deletions |
| `D:\vilsem-security-private` | `40f9e51dd832` | yes | Retained: working changes or generated-output deletions |
| `D:\vilsem-security-public` | `cdf72938fb46` | yes | Retained: ignored source, protected or unidentified files |
| `D:\semantic_test` | `a403b7e4fc15` | yes | Retained: unique project, installed plugin or canonical repository |
| `D:\skynwhy\mvp` | `8bd6760101bb` | yes | Retained: unique project, installed plugin or canonical repository |
| `D:\split_loop\splitloop` | `192905721509` | yes | Retained: working changes or generated-output deletions |
| `D:\split_loop_v1` | `070572574275` | no | Retained: working changes or generated-output deletions |
| `D:\vilsem-mcp` | `029a577307b8` | yes | Retained: working changes or generated-output deletions |
| `D:\vilsem-mcp-docs` | `4169f0af958b` | yes | Retained: ignored source, protected or unidentified files |
| `C:\temp\dia-hospital-release-20261031` | `1bf6261bb4c0` | yes | Removed after clean/pushed/ignored-file checks |
| `C:\temp\dia-r21-map-audit` | `d649e93d0813` | yes | Removed after clean/pushed/ignored-file checks |
| `D:\dia-r19-merge424` | `df422e4ed548` | yes | Removed after clean/pushed/ignored-file checks |
| `D:\dia-r19-merge425` | `9b30ce8a213b` | yes | Removed after clean/pushed/ignored-file checks |
| `D:\dia-r19b-attempt03-replay` | `ff0347dba28f` | yes | Removed after clean/pushed/ignored-file checks |
| `D:\dia-round-eight-blind-estate` | `bcc759ea3baa` | yes | Removed after clean/pushed/ignored-file checks |
| `D:\dia-round-five-gate` | `bb2d2ca95c38` | yes | Removed after clean/pushed/ignored-file checks |
| `D:\dia-round-five-recorded-engine` | `5c3daad78f29` | yes | Removed after clean/pushed/ignored-file checks |
| `D:\dia-round-five-regrade` | `2d6d67f2f537` | yes | Removed after clean/pushed/ignored-file checks |
| `D:\dia-round-four-test-baseline` | `59c89c5e4871` | yes | Removed after clean/pushed/ignored-file checks |
| `D:\dia-round-twelve-form` | `6497abbf535d` | yes | Removed after clean/pushed/ignored-file checks |

These sizes were obtained from metadata only; file contents were not read or modified. Redirected OneDrive folders and the separate nonredirected Documents folder are listed separately.

### Largest 20 remaining folders per drive

Common system/profile/repository containers are expanded so these are non-overlapping folder groups, rather than twenty nested names for the same data. Sizes are logical metadata totals, not exact occupied disk; hard links and compression still affect physical occupancy. These are retained items for owner review, not deletion recommendations.

**C:** (metadata snapshot 2026-11-16T07:22:40.351035+00:00; inaccessible entries: 1040)

| Folder | Logical GB | What it is |
|---|---:|---|
| `C:/Windows\WinSxS` | 26.15 | Windows component store; admin cleanup was not completed |
| `C:/Windows\System32` | 10.98 | Windows system files; not manually removed |
| `C:/Users\chait\AppData\Local\Claude-Data` | 9.93 | Claude application state/runtime; not a Docker or WSL cleanup target |
| `C:/Users\chait\AppData\Local\Google` | 7.38 | User application data; only identified caches were removed |
| `C:/Users\chait\AppData\Local\Android` | 6.67 | User application data; only identified caches were removed |
| `C:/Program Files (x86)\Microsoft` | 6.65 | Installed applications; no uninstall authorized |
| `C:/Users\chait\AppData\Local\Packages` | 5.12 | User application data; only identified caches were removed |
| `C:/Program Files\Microsoft Office` | 4.95 | Installed applications; no uninstall authorized |
| `C:/Users\chait\Downloads` | 4.79 | Protected personal files / OneDrive |
| `C:/Users\chait\anaconda3` | 4.77 | Python base distribution used by the current DIA environment; retained |
| `C:/Users\chait\.codex` | 4.35 | Active Codex state and installations; protected |
| `C:/Users\chait\AppData\Local\Microsoft` | 4.24 | User application data; only identified caches were removed |
| `C:/Users\chait\Documents` | 4.16 | Protected personal files / OneDrive |
| `C:/Program Files\JetBrains` | 3.67 | Installed applications; no uninstall authorized |
| `C:/Users\chait\AppData\Local\CapCut` | 3.55 | User application data; only identified caches were removed |
| `C:/Users\chait\Videos` | 3.48 | User profiles, application state and personal files |
| `C:/Users\chait\.vscode` | 3.44 | User profiles, application state and personal files |
| `C:/android-sdk` | 3.09 | Retained installed tool, project or unidentified data; inspect before deletion |
| `C:/Users\chait\AppData\Local\Programs` | 2.71 | User application data; only identified caches were removed |
| `C:/Users\chait\AppData\Roaming\Code` | 2.52 | User application data; only identified caches were removed |

**D:** (metadata snapshot 2026-11-16T07:05:24.557677+00:00; inaccessible entries: 1)

| Folder | Logical GB | What it is |
|---|---:|---|
| `D:/data_investigation_agent\.local\process-tapes` | 17.48 | DIA captures; current/referenced/protected members retained |
| `D:/data_investigation_agent\.local\round-seventeen` | 11.50 | Historical DIA evidence with protected/referenced/unknown members |
| `D:/semantic_app` | 9.90 | Project source, models or unidentified cache data; retained |
| `D:/dia-round-fifteen-demo` | 7.39 | DIA worktree/local data; unique or protected contents retained |
| `D:/data_investigation_agent\.local\round-eleven` | 4.41 | Historical DIA evidence with protected/referenced/unknown members |
| `D:/data_investigation_agent\.local\round-sixteen` | 4.02 | Historical DIA evidence with protected/referenced/unknown members |
| `D:/data_investigation_agent\.local\round-ten-20261007` | 3.82 | Historical DIA evidence with protected/referenced/unknown members |
| `D:/data_investigation_agent\.local\round-eighteen` | 3.51 | Historical DIA evidence with protected/referenced/unknown members |
| `D:/data_investigation_agent\.local\round-twenty` | 3.02 | Historical DIA evidence with protected/referenced/unknown members |
| `D:/data_investigation_agent\.local\round-nineteen` | 1.61 | Historical DIA evidence with protected/referenced/unknown members |
| `D:/split_loop` | 1.27 | Retained installed tool, project or unidentified data; inspect before deletion |
| `D:/data_investigation_agent\.local\planner-recordings` | 0.75 | DIA local environments, captures, ledgers and protected evidence |
| `D:/data_investigation_agent\.local\round-twenty-six` | 0.75 | Current Round26 evidence and maintenance records; protected |
| `D:/vilsem-core-release-050` | 0.74 | Retained installed tool, project or unidentified data; inspect before deletion |
| `D:/data_investigation_agent\.local\round-seven-20261005` | 0.65 | Historical DIA evidence with protected/referenced/unknown members |
| `D:/vilsem-fresh-test` | 0.55 | Retained installed tool, project or unidentified data; inspect before deletion |
| `D:/vilsem-copilot-test2` | 0.55 | Retained installed tool, project or unidentified data; inspect before deletion |
| `D:/vilsem-copilot-test` | 0.55 | Retained installed tool, project or unidentified data; inspect before deletion |
| `D:/data_investigation_agent\.local\unknown-domain-v4` | 0.48 | DIA local environments, captures, ledgers and protected evidence |
| `D:/dia-r18-guardrails` | 0.40 | DIA worktree/local data; unique or protected contents retained |

### Mixed caches retained for owner review

Only identified dependencies/build products within these locations were removed. Remaining material is not assumed regenerable.

| Folder | Remaining logical GB | Disposition |
|---|---:|---|
| `D:/semantic_app/cache` | 3.43 | Remaining contents retained; no blanket deletion |
| `D:/cache` | 0.00 | Remaining contents retained; no blanket deletion |
| `C:/Users/chait/AppData/Local/Temp/claude` | 0.40 | Remaining contents retained; no blanket deletion |
| `C:/temp/claude` | absent | Remaining contents retained; no blanket deletion |

### Process check

No obsolete Python ticket or grader worker was found in the closing process inventory. The archive launcher/worker completed and exited. The closing snapshot contained only the active Node support process, with no Python workers; subsequent metadata checks are short-lived maintenance. Active shell/Node support processes and unidentified application state are retained; no arbitrary application termination is claimed. Sanitized process snapshots are in the private maintenance directory.

### Result and next step

Both owner free-space targets were reached. Protected data remains; reaching the target did not authorize deletion of unknown or unpushed material.
Owner overnight steer2026-11-16: skip every administrative prompt, UAC or sign-in task; leave it for the morning, without retrying through another route. The existing owner-admin-cleanup.ps1 remains unexecuted. Standing hygiene is recorded in CLAUDE.md; laptop admission requires decimal40GB C:/80GB D:. Current source includes a tested host-only admission check; frozen cloud investigation image and recorded measurements are unchanged.
Next: verify the preserved Round26 environment/image/fixture/infrastructure, then resume release closure from saved results. Calibration is final2/10 with two harmful answers, so v5 stays sealed/unadmitted. Do not repeat stale cohorts, calibration or the three already-passed release smokes.


### Round26 end-of-round hygiene — 2026-11-16

Release closure reused the existing C:/temp/dia-r26-build worktree; dirty D: main edits remain untouched. No new duplicate raw capture copy or worktree was created. The disk admission check passes both40GB C:/80GB D: floors; verified archive staging is empty, Docker/WSL absent, and maintenance Python workers exited. Current protected evidence and small qualification records remain; sealed cloud captures remain in Blob. The earlier admin/policy/unknown-material exceptions remain owner actions, not silent deletions.
