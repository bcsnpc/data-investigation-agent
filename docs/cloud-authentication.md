# Explicit cloud authentication paths

Round Eighteen adds optional managed-identity authentication to the existing
Microsoft adapter configuration. It does not create identities or grant roles.
The local DPAPI/CLI forms remain readable for existing installations and exact
historical replay. There is no automatic fallback from a cloud identity to one
of those local identities.

A managed-identity declaration contains exactly `mode: managed_identity`,
`client_id`, `tenant_id` and `principal_id`. The client ID selects the
user-assigned managed identity. Every token is checked against the declared
tenant, principal and requested service audience before use. A missing identity,
authentication refusal or mismatched token stops that path with a bounded error;
exception bodies, tokens and secrets are not emitted. The supported audiences
are explicit platform endpoints, not user- or model-authored URLs.

The existing estate schema now accepts:

- SQL auth: the managed declaration plus `account` (the contained user's name).
- Fabric auth: the managed declaration plus `python` (the worker executable).
- Native reader: `mode: managed_identity`, tenant/principal/account and the same
  workspace/model allowlist used by the existing reader.
- Fabric SQL reader: managed declaration plus `account` and `server`.
- Model credential: the managed declaration, or `mode: key_vault` with a
  `reference` containing `vault_url`, `secret_name`, `secret_version`, `identity`.
- Estate identity `credential_reference`: `managed-identity://<client_id>`.

All these alternatives pass through the existing closed loader and adapter
projection. A schema-valid credential does **not** establish that a service
supports the principal or that it has been granted any access.

## Implemented execution paths

Native Power BI execution and report listing use the configured managed
principal and retain the same query-bound transport identity receipt. This
receipt remains partial: it does not attest the report viewer, effective RLS,
permissions stability or aligned snapshots. Metadata workers accept the same
explicit credential instead of selecting a local Fabric CLI session.

`local_azure_key` remains the compatibility entrypoint for model bootstrap. For
managed identity or Key Vault modes it enters a task-local `model_session`;
it does not invoke `az ... keys list` or set an environment secret. The model
transport obtains a bearer token/secret in memory using that context. Parallel
worker tasks must each enter their selected model session. Existing request,
reservation, spend and capture handling stays in the shared model transport.

Key Vault reads are exact versioned HTTPS GETs through the external-call
gateway. Configure that exact URL, method and worker identity in the gateway
policy. The secret is not a query-result evidence item and is not written to a
tape, environment or file. The response secret ID must match the requested
version. Managed-identity token issuance uses Azure Identity's local managed
identity endpoint; it is an authentication-plane operation, not estate evidence.

## Explicit remaining dependency

**Managed-identity SQL execution is not yet installed by this change.** The
source and Fabric SQL paths refuse with
`MANAGED_IDENTITY_SQL_GUARDED_TRANSPORT_NOT_INSTALLED`; metadata SQL collection
reports `MANAGED_IDENTITY_SQL_CATALOG_TRANSPORT_NOT_INSTALLED`. They never fall
through to DPAPI, a CLI profile, or a different principal. A Linux SQL port must
preserve the existing object permission checks, read-only connection intent,
row/time bounds, per-request accounting and surface attestation before this
refusal can be removed. A cloud smoke requiring those reads is not earned by
passing the authentication tests.

Optional refresh/XMLA and privacy-key secret readers are not automatically
converted by this schema extension. Preflight must report any still-local path
as unsupported in a cloud installation. No claim is made that an unchanged
Windows example is deployable in a Linux container.

## Validation and sources

Offline tests cover token bindings, exact identity construction, no CLI
fallback or secret error leakage, closed schema/projection, native partial
identity receipts, named SQL refusal, task-local model selection, report-list
binding, metadata credential forwarding and versioned Key Vault reference
validation. The final focused regression passed 152 tests. No real token, secret or estate read was used.

Microsoft documents explicit `client_id` selection and the `get_token` API in
[ManagedIdentityCredential](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.managedidentitycredential?view=azure-python).
The declaration uses that API directly, rather than a broad default credential
chain that could select an operator's developer session.
