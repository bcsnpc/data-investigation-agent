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

## Guarded Linux SQL transport

`managed_sql_worker.py` executes admitted record quantities for Azure SQL and
Fabric SQL using ODBC Driver 18 and a token acquired inside the child. No token
crosses a tape, command line, environment variable, or connection-string field.
Gateway admission precedes credential acquisition and connection. Encryption,
certificate validation, read-only intent and ODBC read-only access mode are set.
The SQL guard still checks database and every admitted object's effective
permissions before reading: unexpected write/DDL/administrative permission
refuses. Identity is read separately; Fabric retains query-bound surface fields,
and the application wrapper retains its own query-bound fields. Empty Fabric
results have no fabricated surface attestation.

Identity, database permission, object permission and quantity requests use the
existing physical REQUEST/DONE protocol. Permission reuse requires the parent's
established receipt; reuse itself issues no SQL. The cache identity includes the
public managed-identity declaration. No connection pool survives the worker.
Connect and statement limits are 30 seconds; existing parent worker deadlines
still kill the child. Record responses cap at 251 rows, 16 columns and 1,000
characters per value. Query parameters stay bound values. PREWARM and SELF_REPORT
require explicit gateway control declarations and never act as diagnostic reads.

**SQL catalog collection is not ported.** It still refuses with
`MANAGED_IDENTITY_SQL_CATALOG_TRANSPORT_NOT_INSTALLED`; there is no DPAPI/CLI
fallback. The old non-record three-column source aggregate is also not supported
by the MI worker: it needs the admitted record quantity contract and refuses
missing row/column/object bounds. A cloud smoke is not earned by offline tests.

For a Debian 12 container install `ca-certificates`, `curl`, `unixodbc` and
`unixodbc-dev`, then install Microsoft's signed Debian 12 repository package
from `https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb`.
Run `ACCEPT_EULA=Y apt-get install -y msodbcsql18` after updating package metadata,
then `pip install -r scripts/requirements-cloud-auth.txt`. These are image-build
steps; do not install packages or provision identities during a ticket. Driver
availability is checked by a connection attempt, not silently substituted.
Microsoft's [Linux installation instructions](https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server)
and [access-token ODBC contract](https://learn.microsoft.com/en-us/sql/connect/odbc/using-azure-active-directory)
document the driver setup and length-prefixed UTF-16 token attribute.

## Remaining dependencies

Optional refresh/XMLA and privacy-key secret readers are not automatically
converted by this schema extension. Preflight must report any still-local path
as unsupported in a cloud installation. No claim is made that an unchanged
Windows example is deployable in a Linux container.

## Validation and sources

Offline tests cover token bindings, exact identity construction, no CLI
fallback or secret error leakage, closed schema/projection, native partial
identity receipts, guarded SQL dispatch, task-local model selection, report-list
binding, metadata credential forwarding and versioned Key Vault reference
validation. The final focused regression passed 152 tests. No real token, secret or estate read was used.

Microsoft documents explicit `client_id` selection and the `get_token` API in
[ManagedIdentityCredential](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.managedidentitycredential?view=azure-python).
The declaration uses that API directly, rather than a broad default credential
chain that could select an operator's developer session.
