# Owner actions and deferred options

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
There is no automatic CLI/operator fallback. The platform health demonstration
is pending separate evidence; this page requests no additional owner action
unless that demonstration identifies a new blocker.

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
