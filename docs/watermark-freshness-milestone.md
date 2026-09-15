# Reviewed watermark freshness evidence

Tracked by [#167](https://github.com/bcsnpc/data-investigation-agent/issues/167), implemented in [PR #168](https://github.com/bcsnpc/data-investigation-agent/pull/168). Builds on merged PR #166. This is a grouped D/F/G implementation slice, not completion of causal investigation or the eight-family acceptance gate.

## Behavior

The investigator can select a `datetime2` column from retained SQL metadata and read its scoped maximum timestamp's age. A reviewed policy can establish whether that observed age exceeds a team-defined limit. Neither a recent timestamp nor an old timestamp proves that ingestion is complete or that a report discrepancy has been explained.

The source operation `watermark_age_microseconds` runs one parameterized SELECT returning the age, scoped row count and non-null timestamp count. It uses SQL's UTC clock and `DATEDIFF_BIG(microsecond, MAX(column), SYSUTCDATETIME())`. The policy explicitly concerns microsecond boundaries: equality is within policy, and strictly greater is exceeded. This follows Microsoft's [DATEDIFF_BIG semantics](https://learn.microsoft.com/en-us/sql/t-sql/functions/datediff-big-transact-sql). No timestamp or metric names are built into the tool.

The same source adapter supplies receipt reservation, timeout uncertainty, connection-only recovery and durable replay. Adaptive source candidates carry the operation, policy reference and resulting condition. Watermark ages are excluded from native metric differences. Shared projections expose the scoped conditions while the overall report cause and delivery eligibility remain unverified.

## Policy authority and lifecycle

An administrator reviews an exact source plan, UTC timestamp meaning, maximum age in whole seconds and an authority reference. Registration binds the policy to model revision, context, catalog, connection and filters. Policies are immutable; changed meaning requires a new review. Revocation blocks new execution and holds a read if the policy is withdrawn before its result is accepted. Historical receipts remain available, with a separate current-policy indicator.

This is an **admin-reviewed assertion**, not independently authenticated business authority. The CLI is a trusted local operator interface; the admin API uses the existing separate admin credential. An LLM cannot register a policy through its admitted tools. Registration does not validate the referenced document, prove timezone correctness or certify the remote schema/data generation.

Missing policy, empty scope, missing timestamps and future watermarks produce gaps. Malformed age/count results fail. Stale or revoked policies block or hold execution. A successful check reports one of:

- `WATERMARK_AGE_EXCEEDED`: the scoped MAX age exceeded the reviewed threshold at SQL observation time.
- `WATERMARK_WITHIN_POLICY`: that observed MAX age was within the threshold; this is not a general data-health certificate.
- `INSUFFICIENT_EVIDENCE`: required policy or usable timestamp evidence is missing.

`condition_verified` applies only to the narrow policy condition. `root_cause_verified` and `delivery_eligible` stay false. A receipt is historical evidence and does not establish freshness at the time someone later opens it.

## Operator usage

Discover objects and column IDs with the existing `run_source_diagnostic.py --catalog-model-id` command. Prepare a source plan with the standard model/revision/context/object/column/filter fields and `operation: "watermark_age_microseconds"`. Only `datetime2` and the existing bounded string filters are supported. Without a policy ID, this is an age diagnostic with a policy gap.

Prepare policy JSON with these fields:

```json
{
  "plan": "Replace with the complete reviewed source-plan object, without freshness_policy_id",
  "max_age_seconds": 3600,
  "timestamp_meaning": "Replace with the team-confirmed UTC meaning",
  "timezone": "UTC",
  "authority_reference": "Replace with the reviewed business policy reference"
}
```

The threshold above is illustrative, not the OrderOps SLA. Register only an actual reviewed policy:

```powershell
python scripts/review_freshness_policy.py --config infra/metadata/development.json --database .local/model-admin-verify/native-diagnostics.sqlite --environment development --model-id <model-id> --register .local/reviewed-policy.json --reviewer <reviewer> --approve
```

Add the returned `id` as `freshness_policy_id` to the exact source plan. It can be used in a durable source action or an adaptive envelope's reviewed `source_tests`. The policy CLI also supports `--show <id>` and `--revoke <id> --reason <reason> --reviewer <reviewer> --approve`.

Admin endpoints under `/api/v2/admin/models/{model}`:

- `POST /freshness-policies`: register the reviewed body; requires configured connection controller.
- `GET /freshness-policies/{id}`: inspect retained authority and revocation.
- `POST /freshness-policies/{id}/revoke`: body `{"reason":"..."}`.

Existing source receipt endpoints expose the assessment. No new browser UI or cloud deployment is included.

## Verification

The full script suite passed: **548 tests**. Twenty focused tests cover boundary values, null/empty/future timestamps, invalid results and types, exact scope, connection drift, tampering, cross-model access, role separation, revocation, timeout uncertainty, durable replay and an adaptive policy-evidence flow. Controlled policy fixtures are deliberately labeled as test authority.

Live development check on 2026-09-15 UTC: run `9dc1b99f-81e5-488b-a7e2-5681c9fa7a65`, receipt `8ee35e10-1baf-42bc-bd1d-7ff3c6f1abd8`. One SQL query, first connection attempt, 100000 rows and 100000 non-null timestamps; observed age `273555017590` microseconds. It returned `REVIEWED_UTC_WATERMARK_POLICY_MISSING`, correctly. We did not create a production policy for `orders.updated_at`. Durable replay returned the same receipt with no cloud dispatch. Evidence remains in ignored `.local/freshness-live-evidence.json`.

The live check used the operator runtime's one-call bound, outside the adaptive daily ledger; no LLM request was made. SQL tier, free-offer and overage settings were unchanged. Query-count bounds do not certify Azure compute consumption.

## Still pending

Complete report/identity/date context, authoritative source equivalence, shared generation proof, pipeline run and ingestion completeness evidence, application-intent verifiers, causal confirmation, impact and ownership remain. The next proof milestone should connect actual published-generation/run evidence and reviewed business intent; it should not turn this narrow watermark check into a general freshness or root-cause claim.

After the remaining B-G proof gates: frozen native eight-family acceptance, the shared business/technical ticket workspace, reviewed v2 handoff and deployed end-to-end verification.
