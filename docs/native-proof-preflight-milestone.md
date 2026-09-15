# Native acceptance proof preflight

Review: [PR #178](https://github.com/bcsnpc/data-investigation-agent/pull/178).

Tracked by [#177](https://github.com/bcsnpc/data-investigation-agent/issues/177), following merged PR #176. This completes a repeatable feasibility check for the D/H version-proof prerequisite; it does not pass the H acceptance experiment.

## Why this was the next step

The investigator now has native/source aggregate and record evidence and can reconcile supported arithmetic. The next acceptance gate needs shared-generation, effective-context and exclusive-publication evidence. More matching totals cannot establish these conditions. The architecture explicitly requires this feasibility check before proceeding with the live healthy/defect experiment.

The new collector saves metadata observations and produces an explicit blocked-gate report. It cannot accept an operator-provided `verified` flag or upgrade an observation into remote exclusivity.

## What is implemented

`scripts/run_proof_preflight.py` runs a bounded collector against the registered model:

1. Fabric semantic-model identity.
2. Power BI dataset identity and available effective-identity requirement flags.
3. Workspace role-assignment counts; pagination is marked incomplete, not silently treated as a complete permission inventory.
4. Five recent refresh-history entries, summarized by status.
5. Two separately fetched TMSL definition snapshots, hashed and summarized for storage mode, table count and role count.

Up to 12 HTTP calls are reserved before dispatch. Definition long-running operations allow at most two polls each, with validated operation IDs and bounded Retry-After. New calls stop after the 240-second admission deadline; a request already in progress can finish later under the 105-second worker timeout. Denial, timeout, malformed responses, partial pages and local context changes remain explicit gaps. No mutation API, SQL/DAX query or refresh execution is used.

The catalog stores request progress and hash-checked historical reports in `proof_preflights`. Account names, role members, definition bodies and connection strings are not retained; only counts, selected booleans, hashes, sizes and sanitized errors are saved. An interrupted run remains visible and is not automatically repeated. Reading history makes no HTTP calls.

Admin-only history APIs:

- `GET /api/v2/admin/models/{model_id}/proof-preflights`
- `GET /api/v2/admin/models/{model_id}/proof-preflights/{preflight_id}`

The API does not expose a background network execution endpoint; collection is currently an operator CLI task.

## Run and enforce the prerequisite

```powershell
python scripts/run_proof_preflight.py `
  --config infra/metadata/development.json `
  --database .local/model-admin-verify/native-diagnostics.sqlite `
  --environment development `
  --model-id 3cd8a115-fc8d-4c98-9d27-c71a79410e0f `
  --output .local/proof-preflight-live.json `
  --require-ready
```

`--require-ready` exits **2** when the acceptance gate is blocked. Without it, successful collection exits normally even when its assessment is blocked. Add `--preflight-id <id>` to inspect a saved report without new requests. No current adapter can certify all prerequisites, so this version never reports the live acceptance gate ready. Normal bounded diagnostic use remains available.

## Live findings: 2026-09-15

Preflight **`35fa5f41-505b-4736-8401-c67e49a66718`** completed all six observations in **10 metadata HTTP calls**:

| Observation | Actual result | What it does not prove |
| --- | --- | --- |
| Registered model | Both identity endpoints matched | A stable input generation |
| Workspace access | One Admin assignment, no continuation returned | All indirect/item/tenant permissions or the investigator's effective identity |
| Refresh history | Five sampled entries completed | Which exact immutable input artifacts were published |
| Definition | Direct Lake; six tables; zero model roles observed | Absence of all effective security/context differences |
| Two definition snapshots | Equal hashes; three parts, 44,375 bytes each | No change-and-revert between probes, or an enforced write boundary |

The saved history read made zero HTTP calls. The CLI gate returned exit 2 as designed. No SQL quota/tier changes, data writes, model refreshes, permission changes or UI deployment occurred.

**The live acceptance gate is blocked by:**

- No implemented exclusive-publication control provider.
- Native/source evidence not bound to an immutable published input generation.
- Effective runtime identity and context not jointly verified.
- No complete isolated-fixture contents proof.
- A write-capable workspace role is present.

This means the current tooling cannot certify the required boundary. It is not a claim that Azure/Fabric can never support a controlled acceptance estate.

## Documented permission constraints

Fabric's semantic-model definition API requires both read and write model permissions. Treat this as a collector capability, separate from a readonly investigator credential. [Microsoft API reference](https://learn.microsoft.com/en-us/rest/api/fabric/semanticmodel/items/get-semantic-model-definition)

Workspace role enumeration requires Member or higher and can be paginated. Its output is an observed workspace-role list, not complete effective-identity proof. [Microsoft API reference](https://learn.microsoft.com/en-us/rest/api/fabric/core/workspaces/list-workspace-role-assignments)

Model permissions can also arise from workspace roles, so permission evidence must account for inherited access. [Microsoft permission documentation](https://learn.microsoft.com/en-us/power-bi/connect-data/service-datasets-permissions)

## Concrete next work

1. Design and enforce an isolated fixture publication boundary with separate publisher/metadata collector and readonly investigator identities. Prove the relevant write controls; a local lock or a role-list snapshot is insufficient.
2. Bind exact model/input hashes to publication receipts and complete readbacks. Use the small isolated Import fixture specified by the architecture; leave the working Direct Lake estate intact. Import mode alone is not proof.
3. Verify effective identity and supported scope/relationship/date semantics across the native and upstream captures.
4. Only after those prerequisites pass, freeze the runtime and run the eight acceptance families, including the required live ratio healthy/defect/gap repetitions.

Actual business reviews and unified v2 user workflow/routing/deployment also remain. This finding is recorded before investing in acceptance claims or UI completion that would conceal the proof gap.

## Tests

**694 regression tests passed**, including 26 focused tests. The focused tests cover matching/changed definitions, Import-mode non-proof, permission gaps, redaction, malformed/oversized responses, bounded asynchronous polling, deadlines, context invalidation, durable reservation/history, interrupted collectors, hash tampering, role-separated API access and worker failures. The full suite includes the generator and earlier runtime/evidence regressions.
