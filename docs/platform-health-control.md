# Platform-only health control

This is an operator command, separate from investigation and model tools. It
does not discover an estate, send model requests, create resources or roles,
apply migrations, write PostgreSQL, or request secret values.

The bounded control performs one PostgreSQL statement with server-enforced
read-only transactions and a 15-second statement timeout. It reads identity,
database and four tool-state counts. It also performs at most five HTTP
requests: immutable health challenge PUT/GET, one Key Vault metadata page
(`maxresults=1`, no continuation), and immutable complete-result receipt PUT/GET.
There is no application retry. Authentication acquisition is separate from these
six maximum control operations. Count results do not attest migration equality;
Key Vault metadata access does not attest secret-value access.

The receipt is retained even when a health probe fails, provided Blob permission
allows its upload. It contains the PostgreSQL result, each HTTP status/request
ID, and the explicit capability limits. Secret metadata IDs are hashed; values,
bearer tokens and raw exception messages are never written. Receipt publication
is separately reported with byte readback and SHA-256. A failure to publish makes
the command fail. An existing different receipt cannot be overwritten.

## Configuration and exact policy

Supply this closed shape, with installation-owned values:

```json
{
  "version": 1,
  "identity": {"mode": "managed_identity", "client_id": "11111111-1111-4111-8111-111111111111", "tenant_id": "22222222-2222-4222-8222-222222222222", "principal_id": "33333333-3333-4333-8333-333333333333"},
  "state_channel": "worker:state",
  "metadata_channel": "worker:metadata",
  "postgres": {"host": "platform.postgres.database.azure.com", "database": "tool_state", "user": "worker"},
  "blob": {"account_url": "https://platform.blob.core.windows.net", "container": "captures"},
  "key_vault": {"vault_url": "https://platform.vault.azure.net"},
  "nonce": "abcdef0123456789",
  "receipt_key": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
}
```

Run `python scripts/platform_health.py --config <file> --plan` offline to print
the exact methods, endpoints and statement. Install those grants explicitly in
the operator gateway policy; the command never grants itself access. The state
channel has `role: "platform"` and the one `platform_databases` host/database.
The separate metadata channel gets only the printed vault GET endpoint. Both
authenticate as the same declared managed identity, whose audience, tenant and
principal claims are checked. No ambient developer/admin credential fallback exists.

The challenge uses `captures/files/<content-sha256>`. The full-result receipt uses
`captures/health/<receipt_key>.json`: its owner-selected immutable key is known
before the dynamic probe results, so it is deliberately **not** represented as a
content-addressed key. Give each control run a distinct receipt key. Both writes
use `If-None-Match: *`, and both readbacks must match their submitted bytes.

For an Azure job without configuration mounts, set fixed nonsecret environment
variables `DIA_PLATFORM_HEALTH_CONFIG` and `DIA_PLATFORM_GATEWAY_POLICY` to their
JSON objects, then override the offline image entrypoint with:

```text
python /app/scripts/platform_health.py --environment-config
```

The environment policy is used only within this command. It does not change or
write the runtime gateway policy. The operator must explicitly set
`DIA_LIVE_ACCESS_DISABLED=0`; the image's default kill switch remains on. Optional
`--output` retains the same redacted result locally. stdout contains the complete
redacted result, including the receipt URL, and the exit status is nonzero for
any failed check or publication. This document does not claim the control has
executed in Azure.
