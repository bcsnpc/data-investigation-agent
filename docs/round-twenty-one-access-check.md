# Permission map and reader preflight

`config/permission-map.yaml` is a JSON-compatible YAML declaration, not a grant
or a permission audit. It lists the owner, Fabric publisher, investigator,
scanner, worker, graph scan, smoke and retained historical readers separately.
The graph and smoke jobs share the worker managed identity; their estate reads
still use the investigator. Definition-only Contributor access is never a
quantity-reader fallback. Existing authority comes from the linked historical
identity records, not from this file.

Run `python scripts/dia.py check-access --bindings <deployment-bindings.json>`.
The default map is repository-local. `--scope fixture` or `--scope billing`
limits probes to that ticket's route. Omitting scope reports the complete map.
Every selected row receives PASS, FAIL or NOT_TESTABLE with its reason. A
declaration, a token alone, an absent binding or a successful owner probe cannot
make a reader row pass. Unsupported control actions remain NOT_TESTABLE.

Deployment bindings contain no secret values:

```json
{
  "budget": {"environment": "existing-approved-environment"},
  "identities": {"investigator": {"mode": "federated_reader", "tenant_id": "...", "client_id": "...", "principal_id": "...", "managed_identity": {"mode": "managed_identity", "tenant_id": "...", "client_id": "...", "principal_id": "..."}}},
  "probes": {
    "fixture-dax": {"url": "https://api.powerbi.com/v1.0/myorg/groups/<workspace>/datasets/<model>/executeQueries", "method": "POST", "scope": "https://analysis.windows.net/powerbi/api/.default", "channel": "existing-powerbi-channel"},
    "fixture-bronze-sql": {"server": "<declared endpoint>", "database": "<declared database>", "account": "<expected principal>"},
    "fixture-bronze-select": {"server": "<declared endpoint>", "database": "<declared database>", "account": "<expected principal>", "object": "[dbo].[declared_table]"}
  },
  "secret_metadata": [{"identity": "investigator", "credential_key_id": "<key id>", "expires_at_utc": "2026-11-21T00:59:55Z"}]
}
```

HTTP probes use the actual explicitly bound managed/federated token and existing
gateway. Only GET and constant `EVALUATE ROW("access_check",1)` POST are
implemented. The token provider checks tenant, principal and audience. Response
bodies are discarded after bounded validation; receipts retain status and hash,
not secret values. Use an `expect` mapping of dotted JSON paths to verify actual
connection mode, not merely HTTP 200. Existing model definitions/connections are
never modified. The DAX principal self-report limit stays a warning on results;
this check does not introduce a native identity requirement.

SQL self-report proves the served login/database only. Object SELECT rows use a
constant one-row query over the explicitly bound object through the normal
read-only worker, including its existing permission guards. These rows must not
be aliased to self-report results. PostgreSQL rows accept only worker managed
identity and a read-only `has_table_privilege` query on a `dia_state` table;
owner metadata is not a substitute. Platform-state control reads do not count as
estate diagnostics; HTTP/SQL estate probes use the shared physical request
meter. No independent budget or counter reset is introduced.

Runner configuration gains `access_check: {"map":"<path>",
"bindings":"<path>","scope":"fixture"}`. After input materialization, every
non-replay worker admission records the preflight table before dispatch. Build
phase preflight mismatches warn and continue, as CLAUDE.md requires; gateway
denials remain hard failures. An older configuration without bindings explicitly
reports NOT_TESTABLE rather than silently passing. Daily smoke configuration
supports the same key and reports INCOMPLETE for an untestable map, FAIL for a
failed row. Its top-level result cannot claim PASS by ignoring the preflight.
The parent runner and smoke should use the same route scope to avoid scanning
the entire estate for one ticket. All-map operator audits are separate.

Sanitized credential metadata is the rotation output interface. Seven days
before expiry, the row is PASS with an explicit warning; at expiry it is FAIL.
The metadata is not an authentication receipt. From the 25th, check-access emits
the monthly owner reminder to confirm next month's budget account. The worker
does not gain INSERT rights or silently provision accounts. Owner provisioning
remains a distinct action; a reminder does not assert it happened.

Tests are offline. They prove missing bindings cannot pass, route isolation,
identity mismatches, fixed-mode mismatches, gateway propagation, secret-safe
receipts, expiry boundaries and worker/smoke integration. They establish no new
live grant or successful live route. Live probe counts and results must be
recorded separately by the operator.
