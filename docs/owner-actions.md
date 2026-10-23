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
