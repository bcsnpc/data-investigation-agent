# Unified run path

`python scripts/dia.py run bronze --estate /inputs/runner-estate.json --runtime worker`
is the fixed worker command. The same image digest runs on a laptop with
`--runtime local` (Docker), or in the existing Azure job with `--runtime azure`.
The worker accepts `DIA_RUNNER_ESTATE_JSON` for public configuration hydration;
credentials remain the existing Key Vault references and managed identity.
Existing gateway and PostgreSQL environment configuration is retained.

The versioned `dia-runner-estate-v1` deployment envelope has exactly these
fields: `version`, `manifest`, `image`, `capture`, `checks`, `output_root`.
The runner generates its complete capture header from the deployed plan, current
engine fingerprint and committed revision. Callers do not author engine identity.
It does not change the pinned investigation manifest. `image`
must use `@sha256:`. `checks` maps names to `{kind, options}`; kinds are a
fixed code registry, never a Python module or arbitrary executable. Supported
handlers reuse the normal form investigation, approval verifier, graph scanner,
compiled SQL surface, context preparation, and verification replay. The smoke
handler uses the separately tested daily-smoke implementation.

An optional `run_id` can be pinned in the deployment envelope to prepare exact
gateway grants for immutable capture objects. A subsequent run needs a fresh
identifier; existing capture directories and Blob objects are never overwritten.
The platform gateway's `runner_captures` declaration names only the account,
capture prefix, exact run identifier and maximum object bytes. It permits
GET/HEAD and create-only BlockBlob PUT of numbered JSON entries and the sealed
run manifest. Adjacent runs, encoded traversal, query controls, overwrite PUT
and other methods are refused. This adds no Azure role or identity permission.

Azure deployment options declare the existing job resource ID and a fixed CLI
tuple (`[python-path, -m, azure.cli]`, or `[az]`). The launcher reads the existing
template, preserves environment references/resources, selects the pinned image
and fixed command, and starts a per-execution JSON/YAML template override.
`platform_cost_observation` carries the actual billing amount, timestamp and
source; the monthly platform admission check runs before launch. Optional
hash-pinned `input` configuration retrieves an existing archive through the
gateway and existing bounded extractor, with its header already durable.

The complete seven-field tape bootstrap is checked before any transport or
handler starts. The capture object receives a configured platform Blob sink;
it uses the existing managed-identity transport and gateway. Every step start,
step result and native Tape event is written to a unique immutable Blob name
before returning. Native probe results are independently published before final
Tape sealing. An exception adds a partial failure record. Abrupt termination
leaves its STARTED/partial state and all previously acknowledged objects; it
cannot create a completion marker. A real child-process kill test checks this
against an independent durable fake Blob directory.

Transient connection errors retry at most twice after 30 and 45 seconds, with
separate attempt directories and retained failure records. Billing,
authorisation, guardrail and secret refusals never retry. The runner selects
build-phase monthly accounting before constructing a governor; scans/smoke
select the collector category, while probes and investigations select the
investigation category. Budget and permission guards remain inside the normal
read dispatch. Runtime options and SQL requests are configuration, never inline
launch programs. Historical wrappers remain readable in git and are superseded
for new Round Twenty runs by this registry.

Probe options are `{config, database, request, budget, max_requests}`. The
request is an already compiled/admitted request consumed by
`fabric_sql_surface.read`; the shared Meter counts each SQL identity, permission
guard and quantity read. Verification options name prepared artifacts, the
verification specification and its hash, plus an optional deadline. Neither
handler grants access, publishes a route automatically, or impersonates a user.

Replay is a separate check after live execution. Its result cannot prevent a
live handler from starting. Existing verifier/form internals retain their own
semantic and permission validation: this runner does not reinterpret a refusal
as a successful result.

Replay options have an explicit format: `verification` uses the existing
verification replay; `investigation` uses the existing immutable pinned-engine
driver; `probe` reruns the same native surface reader and physical worker
protocol under the sealed Tape with transport forbidden. `scan-boundary`
validates the completed run's sealed manifest and every immutable per-read
response/result, with the expected image pin. It reports **BOUNDARY_ONLY** and
`graph_recomputed: false`: it does not claim the graph mutations were replayed.
Full scan semantic replay still needs a retained pre-scan graph-state baseline.
New headers record BUILD_PHASE inside the configuration and the image pin in
state; historical Tape bytes and their operating mode are untouched.
