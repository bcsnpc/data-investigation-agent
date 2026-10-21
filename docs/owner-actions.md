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
