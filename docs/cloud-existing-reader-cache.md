# Existing delegated reader credentials on cloud workers

This adapter relocates an already-authorized user's scoped refresh cache. It
does not create an identity, consent, sign-in or estate permission. Provisioning
and uploading the secret require the separately recorded owner decision. No
credential is committed by this implementation.

Each public-client/audience pair has a separate immutable Key Vault secret
version. The secret text is JSON with exactly:

```json
{"version":1,"cache":{"Account":{},"RefreshToken":{},"AppMetadata":{}}}
```

The dictionaries contain the selected existing MSAL records. There must be
exactly one Account. Its `realm`, `local_account_id`, `username` and
`environment` must match the declared tenant, object ID, account and
`login.microsoftonline.com`. RefreshToken entries must have that same
`home_account_id` and environment and the declared client ID. AppMetadata must
match client and environment. AccessToken and IdToken sections are refused.
Retain MSAL's ordinary record fields and keys (including `authority_type`);
this is not a new cache format inside those three sections.

The public credential configuration is:

```json
{
  "mode":"key_vault_user_cache",
  "tenant_id":"<existing-reader-tenant-uuid>",
  "client_id":"<existing-public-client-uuid>",
  "principal_id":"<existing-reader-object-uuid>",
  "account":"<existing-reader-account>",
  "scope":"https://analysis.windows.net/powerbi/api/.default",
  "reference":{
    "vault_url":"https://<vault>.vault.azure.net",
    "secret_name":"<scoped-cache>","secret_version":"<32-hex-version>",
    "identity":{"mode":"managed_identity","tenant_id":"<worker-tenant>",
                "client_id":"<worker-client>","principal_id":"<worker-object>"}
  }
}
```

`fabric.auth` carries this declaration plus `python`. `fabric.native_reader`
remains the existing `isolated_reader` profile with the same user and model or
workspace allowlist. `fabric.sql_reader` carries the separate SQL declaration
(scope `https://database.windows.net/.default`) plus `server`. Its manifest
credential reference is the exact versioned vault URL without query string.
The worker MI retrieves the secret; it does not become the quantity identity.

The configured gateway HTTP identity needs these exact entries, never a wildcard:

* GET the versioned vault URL with `?api-version=7.4`, purpose `metadata`.
* GET `https://login.microsoftonline.com/<tenant>/v2.0/.well-known/openid-configuration`, purpose `metadata`.
* POST `https://login.microsoftonline.com/<tenant>/oauth2/v2.0/token`, purpose
  `auth_refresh`, with `tenant_id`, `client_id` and `scope` fields matching this
  declaration. This accepts only the refresh-token grant for that client and
  scope, with the usual OIDC scopes. A second client/scope on the same token
  endpoint uses a separate logical gateway identity/session policy (duplicate
  exact endpoint grants are ambiguous and refused).
* The existing exact query endpoint or SQL object/control allowance.

KV access and refresh requests carry credentials only in memory. MSAL uses an
in-memory cache and `acquire_token_silent`; no updated cache is serialized to
disk. Redirects, interactive authentication, device-code flow, CLI fallback,
new consent and undeclared audiences are refused. Only generic failures leave
the authentication boundary. Expiry or conditional access requiring interaction
is a refusal requiring an owner-managed credential renewal, never a fallback.

Native DAX, existing-reader report lists and guarded Fabric SQL are wired.
General Fabric/OneLake discovery is explicitly unavailable through this
one-audience declaration; it must not silently use an operator CLI session.
SQL permission checks, object allowlists, physical accounting and surface
attestation remain the same. Tokens and refresh values never enter tapes.
Tests use fabricated cache records and mock transports, including the real
MSAL cache/refresh path, without any cloud or estate call.
