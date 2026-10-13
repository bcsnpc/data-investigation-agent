# Live-access gateway

The live runtime requires an operator-owned JSON policy. Missing policy refuses
before any governed network request. This is separate from budgets and never
raises a diagnostic, physical, model, or dollar cap.

Set `DIA_GATEWAY_POLICY` to its path. Set `DIA_GATEWAY_HTTP_IDENTITY`,
`DIA_GATEWAY_SQL_IDENTITY`, and `DIA_GATEWAY_MODEL_IDENTITY` to the corresponding
explicit identity keys. Credentials remain with their existing authenticator;
these labels neither create an identity nor grant access. `DIA_LIVE_ACCESS_DISABLED=1`
stops subsequent governed live accesses, including model calls. The durable local denial journal defaults to `.local/gateway-denials.jsonl`;
override it with `DIA_GATEWAY_AUDIT_FILE`. Only a target hash and rejection
reason are logged, never SQL literals, tokens, ticket text, or request bodies.

Example, with synthetic values only:

```json
{
  "version": 1,
  "live_enabled": true,
  "identities": {
    "reader": {
      "http": [{
        "method": "POST",
        "url": "https://api.powerbi.com/v1.0/myorg/groups/WORKSPACE/datasets/MODEL/executeQueries",
        "purpose": "dax"
      }],
      "sql": [{
        "server": "configured-server",
        "database": "configured-database",
        "objects": ["dbo.DiscoveredTable"],
        "read_only": true,
        "row_cap": 251,
        "timeout_seconds": 30,
        "controls": ["PREWARM", "SELF_REPORT", "CATALOG"]
      }]
    }
  }
}
```

HTTP permissions are exact identity, method, and complete URL (including query
parameters), without wildcards or prefix authority. Metadata permits GET/HEAD
and empty-body getDefinition POST only. DAX permits one EVALUATE in one
executeQueries request, without impersonation. Model traffic permits only
explicit responses/completions POST endpoints. Blob reads are GET/HEAD. KQL is
fail-closed until its read grammar is implemented. A service-returned continuation
URL does not grant itself permission: the operator must add the exact endpoint.

SQL is parsed by SQLGlot, using the existing bounded compiler's AST vocabulary.
It rejects writes, multiple statements, SELECT INTO, comments, unknown functions,
external/temporary objects and references outside the policy's catalog objects.
A request's graph/catalog slice can only narrow that set. Read-only connection
intent, effective-permission checks, query timeout and row caps remain mandatory
in the native workers. TOP limits output, not scan work; timeouts still bound work.

The gateway is integrated at metadata HTTP, native DAX HTTP, OneLake reads,
source/Fabric SQL physical dispatch, SQL catalog/self-report controls, and model
HTTP. Recorded offline replay consumes the original sealed bytes without live
policy checks, so this enforcement does not rewrite old tapes.

Authentication acquisition (the configured MSAL/Azure CLI/managed-identity token
provider) is a control-plane prerequisite, not model-owned HTTP. Deployment and
fixture-authoring administrator commands are not exposed as investigation tools
and are outside this read-only runtime gateway. Legacy directly invoked
PowerShell scripts are not an OS sandbox: a human running those scripts manually
can bypass the Python dispatcher. Do not describe this as a network firewall.
The deployment must expose only governed worker entrypoints and preserve
least-privilege principals independently of this application guard.

Platform persistence is separately scoped: an identity with `role: "platform"`
may declare only `platform_blob` HTTP grants (GET/HEAD/PUT; never DELETE) and
`platform_databases: [{"host": "exact-host", "database": "tool-state-db"}]`.
It cannot also declare estate SQL or model/metadata endpoints. Blob SDK adapters
must call `current().http(identity, method, exact_url)` before each send, including
block uploads/commit URLs. PostgreSQL adapters call
`authorize_platform_database(identity, host, database)` before connecting.
These are internal application persistence operations, never model-facing tools;
estate queries cannot request platform authority or supply those identity labels.

The identity keys are *logical authority channels*, not a requirement for distinct
Entra principals. The approved managed identity can authenticate both
`id-dia-worker:state` and `id-dia-worker:investigation`. Their policy entries stay
separate, and internal code selects the state channel; model-facing tools cannot.
Actual tenant/principal verification remains with the authenticator.

Optional native helpers require exact `native_controls` grants per channel:
`XMLA_EVALUATE` plus workspace/model, or `SNAPSHOT_SQL_METADATA` plus
server/database, or `SNAPSHOT_XMLA_METADATA` plus workspace/model. XMLA query
text passes the same EVALUATE-only guard. Snapshot helpers accept no caller query;
their fixed bounded metadata query remains separately identified and cannot
establish query-bound snapshot attestation. No native control is inferred from
an HTTP or SQL grant. Legacy fixed-template SQL diagnostics without catalog
binding now refuse with `LEGACY_SQL_TRANSPORT_NOT_GATEWAY_BOUND`.
