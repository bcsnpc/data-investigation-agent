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
