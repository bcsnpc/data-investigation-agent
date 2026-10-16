# Two-phase cloud-stage launch configuration

Build each job's public environment offline. This command does not create a job,
acquire a token, change a budget or approve a configuration:

```text
python scripts/cloud_stage_environment.py --stage <phase.json> --gateway <exact-policy.json> --platform <platform.json> --slim <slim.json> --worker-id <unique-execution-id> --ceiling-microdollars <existing-shared-ceiling> --margin-microdollars <existing-protected-margin> --output <new-job-environment.json>
```

The output contains the command and environment entries for the existing job's
container override. Use the same immutable reviewed image for prepare and verify.
`phase.json` is the `cloud_stage_worker` declaration: input/output capture URLs,
input SHA-256, compressed/expanded limits, worker identity and platform channel;
verify additionally pins the reviewed candidate SHA-256, unique verification
session and deadline. Each phase has its own output URL and worker ID.

The builder checks the explicit account/container CAS grants, exact input GET and
output PUT grants, PostgreSQL route and identical worker identities. It copies
the supplied dollar ceiling and protected margin unchanged. Shared PostgreSQL
rejects a mismatch against its imported authority; these values cannot create or
increase an allowance. All estate pot/reserve limits remain in the approved
manifest and shared ledger.

At startup, trusted public JSON from `DIA_PLATFORM_GATEWAY_POLICY` and
`DIA_CLOUD_SLIM_RECORDING_JSON` is validated and written to
`/work/gateway-policy.json` and `/work/slim-recording.json`. The corresponding
file environment variables are then inherited by every child worker. Existing
different files are refused. No credential values enter those files. The
bootstrap does not override the kill switch.

Required policy channels:

* `worker:state`: platform role, exact PostgreSQL host/database, stage input GET
  and stage output PUT with purpose `platform_blob`.
* The slim declaration's snapshot/tape channels: platform role and the exact
  account/container `platform_cas` declaration. Their names must match the slim
  schema (`worker-snapshots` and `worker-tapes` are examples; colons are not
  accepted by that schema).
* `user-cache:<public-client-id>:powerbi` and `user-cache:<public-client-id>:sql`:
  each exact versioned cache GET, tenant OIDC metadata GET and tenant token POST
  with its own `auth_refresh` client/scope fields. These authentication channels
  never serve quantity queries.
* `investigation`: exact Power BI executeQueries URL and required SQL
  connection/object grants. Bounded catalog batches require explicit CATALOG
  control, row cap 251 or higher and timeout 30 or higher. These are gateway
  bounds, not permission or budget increases.
* `model`: exact model request endpoint and exact versioned model-key GET. The
  model credential fetch uses this channel, never the investigation channel.

The builder sets PostgreSQL host/database/user and explicit MI client ID, gateway
channel selectors, protected dollar guard, unique worker ID, EXACT recording,
and private control/denial journals under `/work`. It does not set a local
SQLite dollar ledger. General Fabric/OneLake scanner and local DPAPI application
credentials remain unavailable; do not add audiences or substitute identities
to satisfy the launch. Ready routes require their fresh governed verification.

Prepare downloads the reviewed inputs and creates a candidate without publishing
or spending estate/model requests. Review its retained output and pin the
candidate before launching verify. Verify publishes that exact candidate, runs
the bounded verification and admits one demo only if fresh readiness is earned.
Failures and partial captures stay in the phase output archive.
