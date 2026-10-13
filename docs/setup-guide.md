# Deploy and preflight a client installation

This guide covers the Round Eighteen foundation. Route onboarding and successful
investigation are separate gates. A valid configuration, deployed worker, or
HTTP 200 from an unrelated endpoint does not make an estate READY.

## 1. Prerequisites and boundaries

Deploy into the client's Azure tenant and subscription. Use a deployment operator
for infrastructure and grants, a metadata scanner for definitions, and a separate
read-only investigator/worker. The worker never falls back to the operator's CLI
credentials. Impersonation is optional, separately approved, and not implemented
as an automatic fallback.

| Prerequisite | Why it is needed | What fails without it |
|---|---|---|
| Subscription/resource-group deployment rights for the operator | Create the tool's platform resources and the explicitly approved scoped grants | Infrastructure deployment; no additional role is silently requested |
| PostgreSQL access to the tool database for the worker identity | Share tickets, case state and atomic budgets | Live admission refuses; SQLite is not a substitute parallel authority |
| Storage Blob Data Contributor on the one tool storage account | Read/write private recordings, content-addressed snapshots and evidence | Capture/replay publication; no public container fallback |
| Key Vault Secrets User on the one vault | Resolve an approved versioned secret reference in memory when needed | The affected connector is unavailable; no plaintext secret file is created |
| Explicit model deployment and allowed model identity | Make bounded model requests | Model work stops on billing/authentication failure; non-model work can continue |
| SQL SELECT/read-only access and definition access to declared sources | Read values and discover schema/transformations | The corresponding value or definition capability remains unavailable |
| Semantic-model Read + Build for the investigator | Execute the model's DAX value query | Presentation quantities cannot be compared |
| Separate scanner access to read-only metadata APIs | Collect the definitions that determine measures, reports and lineage | Discovery reports incomplete coverage |
| Outbound connectivity from the worker to each declared endpoint | Reach platform and estate services | A local operator success does not establish worker connectivity |

For Fabric/Power BI, an administrator reviews these exact tenant settings for the
scanner security group: **Service principals can access read-only admin APIs**,
**Enhance admin APIs responses with detailed metadata**, and **Enhance admin APIs
responses with DAX and mashup expressions**. Their scope is significant: read-only
admin APIs can reveal tenant metadata. Do not enable the separate update-admin
setting for diagnostics. [Microsoft's admin settings reference](https://learn.microsoft.com/en-us/fabric/admin/service-admin-portal-admin-api-settings)

For the REST query route, **Dataset Execute Queries REST API** must be enabled and
the caller needs model Read + Build. Service-principal access is not supported by
that API for RLS or SSO-enabled models. XMLA is a separate optional read route,
not permission to elevate an investigator to write/admin. Workspace monitoring
is optional and its availability must be tested as the actual reader.
[Execute Queries permissions and limitations](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/execute-queries)

## 2. Configure without estate-specific code

Create a client estate manifest from the examples under `infra/estates/`. Supply
the tenant/workspaces, discovered layer and resource addresses, identity
references, model endpoint/deployment, budgets, retention, glossary and read-only
connection declarations. Validate with the installed manifest/adapter. The example
fixture and billing names are examples, never defaults for a new client.

Create a separate, secret-free platform declaration for preflight:

```json
{
  "worker_identity": {
    "mode": "managed_identity",
    "client_id": "<deployed-client-id>",
    "tenant_id": "<tenant-id>",
    "principal_id": "<deployed-object-id>"
  },
  "scanner_principal": "<scanner-principal>",
  "postgres": {
    "host": "<server>.postgres.database.azure.com",
    "database": "<tool-database>",
    "user": "<database-principal>"
  },
  "gateway_policy": {
    "version": 1,
    "live_enabled": false,
    "identities": {}
  }
}
```

The empty gateway policy deliberately denies live work. Fill exact endpoint and
HTTP-method grants, SQL object grants and the platform database grant from the
approved connector inventory. No wildcard host/object grants. Keep estate query
rights separate from the worker's rights to write its own recordings and state.

Set these worker variables from the deployment outputs, not from copied secrets:

```text
INVESTIGATOR_STATE_BACKEND=postgresql
INVESTIGATOR_PG_HOST=<server>.postgres.database.azure.com
INVESTIGATOR_PG_DATABASE=<tool-database>
INVESTIGATOR_PG_USER=<database-principal>
AZURE_CLIENT_ID=<worker-managed-identity-client-id>
DIA_GATEWAY_STATE_IDENTITY=<platform-state-channel>
DIA_GATEWAY_POLICY=<mounted-exact-allowlist-policy.json>
INVESTIGATOR_WORKER_ID=<unique-job-execution-id>
INVESTIGATOR_MODEL_SPEND_MICRODOLLARS=<approved-shared-ceiling>
INVESTIGATOR_MODEL_SPEND_MARGIN_MICRODOLLARS=<approved-protected-margin>
```

The prepared `infra/platform/sql/grant-worker-state.sql` binds the managed
identity object ID and grants only the tool database's `dia_state` tables. Apply
migrations as the owner with `search_path=dia_state,pg_catalog` first; the worker's
database-specific search path uses that schema. The script is deliberately split
at that migration step and is not an unattended whole-file execution. It grants
no schema CREATE, DELETE, ownership, graph writes or other-database privileges.
PostgreSQL authentication roles exist at server scope; existing PUBLIC defaults
must be checked separately and are not evidence of an explicit grant. The
post-grant checks must show no inherited CREATE before admission.

The PostgreSQL adapter uses the explicit managed identity and TLS certificate
verification. Operator migration instead receives an explicitly supplied owner
connector. It is not a worker authentication fallback.

## 3. Deploy or update in one command

Install the repository's workspace, shared-state, cloud-auth and gateway
dependencies in the deployment environment. Use the existing operator Azure CLI
sign-in. Prepare a local JSON parameter file for `infra/platform/main.bicep`:
`location`, `resourceGroupName`, `storageName`, `vaultName`, `postgresName`,
`identityName`, `environmentName`, `jobName`, `ownerObjectId`,
`ownerPrincipalName`, `ownerIp`, `databaseName`, `deployCompute`, and
`workerImage`. Set the image to the CI-published, immutable GHCR digest.
There is no password parameter. Review the current cost estimate and grant scope
before creation; do not assume a free allowance applies to an arbitrary client.

```powershell
python scripts/deploy_platform.py --az-python <python-with-azure-cli> --parameters .local/client-platform-parameters.json --receipts .local/deploy-001 --deployment-name client-platform-001
```

Use `--what-if` first with a fresh receipt directory. The wrapper records the
account, pre/post resource inventory and deployment response. It does not start a
worker or secretly enable an estate query. Interactive owner sign-in may still be
needed for an Azure control-plane refusal; no alternative identity or scope is
tried automatically.

## 4. Cut over shared state without resetting budgets

Stop admissions and drain workers first. Keep the original SQLite ledgers intact.
Run `scripts/export_shared_state.py` with the existing catalog, dollar ledger,
approved policy/round JSON, exact protected microdollar margin and a new output
directory. The output contains original rows and exact integer/decimal totals.
An active reservation refuses migration. For a specifically audited historical
orphan only, `--preserve-orphans-approval <local-json>` accepts an explicit approval
with `source_sha256`, `approved_by`, `approved_at`, `reason`, `drained_workers: true`
and the exact `reservations` list of `session_id`/`reservation_key` pairs. It
preserves every original field, including RESERVED status and charged amount;
records that approval beside the migration proof; and forbids worker settlement
of the imported orphan. It does not free concurrency or budget. If that reservation
still blocks admission, resolving it needs a separate evidence-backed decision,
not this import option.

Review the emitted hashes and use `scripts/migrate_shared_state.py --source ...
--migration-id ... --expected-sha256 ... --report ...` in plan mode. Add `--apply`
only for the reviewed input. Each migration is immutable and idempotent; it
cannot reset charges when run again. Import the money accounts and the usage
rows/batches/allocations/acknowledgments separately, retaining both proofs.

The document migration has a combined read-only export and offline plan:

```powershell
python scripts/migrate_shared_documents.py export --catalog <drained-catalog.sqlite> --environment <estate-id> --tape-class EXACT --readiness <retained-certificate.json> --output .local/documents.json
python scripts/migrate_shared_documents.py migrate --source .local/documents.json --expected-sha256 <exported-hash> --migration-id <unique-migration-id> --report .local/documents-plan.json
```

Repeat `--readiness` for each certificate; omit it when none is retained. Export
opens SQLite read-only, inside one snapshot. Plan exercises the same imports in
memory with no cloud call. A separate reviewed apply requires a migration owner's
PostgreSQL connection, not the worker's narrower table rights. The Python
`import_documents` API accepts that explicit owner `SharedState`; CLI `--apply`
requires an explicitly configured migration identity. Neither falls back to a
signed-in developer identity. Apply writes separate atomic catalog, ticket and
readiness components, checkpoints each one, and resumes only the same bundle
hash after interruption. It is not one cross-component transaction.

The ticket import preserves all `smart_tickets` rows, their request keys,
revisions, questions, replies, history, embedded evidence and original serialized
JSON. Hash collisions or an already-present key refuse rather than overwrite.
A second import cannot reset newer ticket work. Ticket references to captures
still need those pinned blobs/private snapshots; this is not an import of every
execution/cache table into PostgreSQL. Readiness is retained, not re-earned.
Projected cloud persistence remains unsupported and must not use this EXACT path.

Publish retained catalog contexts with `shared_catalog.export_catalog` and
`import_catalog`, then retain readiness certificates with `publish_readiness`.
Every context retains its hash. Storage does not make a route READY: the existing
readiness assessor still checks the certificate, current pins and evidence.
Model enablement/onboarding changes require a new operator publication; a worker
cannot edit its private snapshot to widen access.

Current limitation: raw discovery inventory and per-job execution/capture state
still use a private SQLite replay image. Published catalog reads and global
accounting use PostgreSQL. This is not a complete migration of every historical
SQLite consumer. Privacy-projected shared PostgreSQL persistence is not yet
implemented and refuses admission, rather than persisting raw values.

## 5. Preflight before onboarding or a live ticket

Run against each estate using only the guide and the client configuration:

```powershell
python scripts/preflight_installation.py --manifest .local/client-estate.json --platform .local/client-platform.json --output .local/preflight-001.json
```

The default command is offline and makes zero estate/model calls. It prints
**PASS**, **FAIL**, or **MISSING** for every prerequisite with an actionable fix.
Configuration PASS and access PASS are separate checks. Exit code 2 means the
required set is not established; it does not mean every missing permission was
actually refused.

From the deployed worker, add `--check-shared-state` to check the tool's own
PostgreSQL schema hashes and retained migration proofs through the exact gateway
and managed identity. It is a control operation, not an estate investigation.

The initial CLI does not automatically query every estate endpoint or tenant
setting. Those entries remain MISSING until an installation-owned guarded probe
is connected and supplies its actual identity and receipt. Do not relabel them
PASS from a manifest or an operator's permissions. SQL/semantic/model probes
require the normal budgets and gateway. If a tenant setting cannot be inspected,
retain MISSING with the administrator action; no admin elevation is implied.

## 6. Start onboarding

Once prerequisites are established, run the normal discovery collector, retain
definition hashes and the coverage report, and explicitly approve the complete
configuration/context. Verify each intended investigation route with the
configured reader. Only admit tickets on earned READY routes. The future estate
graph tables are reserved but empty; this foundation does not claim full graph
discovery, incremental updates, RLS impersonation or the future agent playbook.

## 7. Remove an installation

Stop new admissions with `DIA_LIVE_ACCESS_DISABLED`, let in-flight requests settle,
and seal their captures. Export any evidence the client wants to retain. Revoke
only this installation's worker grants, then delete only its platform resource
group after the owner approves deletion. Do not delete source databases, Fabric
workspaces or reports. Archive-tier evidence may require rehydration before
export, and early deletion/storage charges may apply. Key Vault soft-delete,
Blob retention and PostgreSQL backup retention can outlive a resource deletion;
verify each service's retained copies and the client's legal retention policy.

The deploy command is not a cleanup command. No removal happens as part of
preflight, onboarding or a failed investigation.
