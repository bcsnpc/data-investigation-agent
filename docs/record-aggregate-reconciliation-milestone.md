# Aggregate-to-record reconciliation

Review: [PR #176](https://github.com/bcsnpc/data-investigation-agent/pull/176).

Tracked by [#175](https://github.com/bcsnpc/data-investigation-agent/issues/175), following merged PR #174.

## What changed

An aggregate difference and a set of differing records previously remained separate observations. The investigator can now reconstruct supported direct `SUM(column)` and `COUNTROWS(table)` results from complete bounded record captures, then compare the reconstruction with each system's captured aggregate. It checks SQL row and nonblank counts as well as the value.

This is arithmetic over captured evidence, not a second DAX engine. Power BI still evaluates the measure. The retained definition must match the existing narrow direct-aggregate grammar. Ratios, DISTINCTCOUNT, conditional/time/relationship expressions and unsupported inputs return a specific gap. Their otherwise safe native diagnostics remain available.

Multiplicities contribute to counts and sums. Decimal arithmetic uses a bounded high-precision context. Empty native COUNTROWS remains BLANK while empty SQL COUNT_BIG remains zero; all-blank SUM remains blank, and a nonblank sum of zero remains zero. Arithmetic consistency does not certify key uniqueness.

## Evidence conditions and results

The check requires four saved receipts: native scalar, SQL aggregate, native records and SQL records. The record receipts must pin the same current reviewed mapping. It checks measure/input/table/operation bindings, complete responses, matching full filter scopes, local context/revision and terminal aggregate seals.

| Status | Meaning |
| --- | --- |
| `CAPTURES_RECONCILE` | Each captured scalar equals its corresponding record reconstruction; SQL counts also agree. For numeric values, the captured record totals explain the observed native-minus-source delta. |
| `CAPTURE_INCONSISTENCY` | A captured scalar or source count differs from its record reconstruction. Data drift, differing effective context or another cause remains possible. |
| `NOT_ASSESSED` | A prerequisite is absent, stale, revoked, partial, unsupported or unsealed. No arithmetic conclusion is promoted. |

Every outcome still sets `root_cause_verified: false`, `delivery_eligible: false` and `outcome: INSUFFICIENT_EVIDENCE`. Shared input generation, remote definition stability and effective-context/semantic-equivalence proof remain explicit gaps. Matching arithmetic from separate reads is not a remote snapshot guarantee.

## Integrity and compatibility

New native and SQL aggregate receipts are sealed in the same transaction that saves their terminal result. The seal covers receipt/model identity, creation time, status and exact stored request/result. Evidence readers and recovery reject a mismatch. This is local tamper detection, not a provider signature or defense against an actor who can rewrite both data and seals.

Existing receipts remain readable as `LEGACY_UNSEALED`; the new reconciliation gate refuses to use them as sealed evidence. It never retroactively certifies old results by generating a hash on read. Failed and uncertain terminal observations are sealed too, but remain unavailable for reconciliation.

## Execution and API

The durable registry adds a query-free `reconcile_records` action after four typed reads:

```json
{
  "tool": "reconcile_records",
  "input": {
    "native_step": 0,
    "source_step": 1,
    "native_records_step": 2,
    "source_records_step": 3,
    "measure_id": "catalog-measure-id",
    "record_mapping_id": "confirmed-record-review-id"
  }
}
```

Indices must refer to earlier actions of the required type, and the record reads must pin the selected review. The local assessment is persisted and hash checked. Recovery adopts an already saved assessment without another read, or safely replays only the local computation if no assessment was committed.

Admin APIs:

- `POST /api/v2/admin/models/{id}/record-aggregate-assessments` accepts `native_receipt_id`, `source_receipt_id`, `native_records_id`, `source_records_id`, `measure_id` and `record_mapping_id`.
- `GET /api/v2/admin/models/{id}/record-aggregate-assessments/{assessment_id}` reads the historical assessment.

Adaptive sessions automatically attach `aggregate_reconciliations` when they have an unambiguous scalar/source pair and the corresponding reviewed record pair. The saved result reaches the next planner decision and final projection with zero additional cloud calls. Ambiguous source observations do not get arbitrarily paired. Live source candidate discovery still requires its existing reviewed scalar mapping; this feature does not create business authority automatically.

## Verification

**668 regression tests passed**, including 27 focused tests. The focused tests cover exact arithmetic, multiplicity, decimal cancellation, blanks, zero, native empty counts, partial evidence, wrong scopes/operations, unsupported expressions, stale/revoked/disabled models, tampering, legacy compatibility, source counts, role separation, durable recovery and adaptive consumption. Planner behavior in these tests is injected; no live LLM reliability claim is made.

Live bounded verification used a separate local test catalog, retaining the development estate and its actual business reviews. A test-only proposed mapping associated `FactOrderLine[units_ordered]` with SQL `order_lines.quantity` for order IDs ORD-000001 through ORD-000005. This test review is not a production/team business approval.

- Final run: `d218fab7-87bf-47f0-b9c9-5c27f7db3f95`.
- SQL aggregate: `8b78c66b-401f-41a0-942b-e26b8acd87d0`.
- Native aggregate: `fe708579-1af9-45c7-a720-46ec31beb12f`.
- SQL records: `5a5dc379-c87b-4ad0-8b97-24620e6880bf`.
- Native records: `0469fadd-b6ce-4cde-ae9d-8a721423298f`.
- Local assessment: `85cca329-e604-46e9-834e-6125b45a7119`.

Both systems returned **49 units across 15 lines**. Each complete record capture reconstructed 49; SQL row/nonblank counts were both 15. Status: `CAPTURES_RECONCILE`, delta 0, root cause unverified. Completed-run replay with transports configured to fail if called returned the saved result with zero cloud calls.

An earlier run (`75f4b30f-f924-40bf-b2b1-759d7d0e6ec9`) captured one SQL aggregate but was held because implementation changed after its engine pin. Its SQL connection had one 40613 connection-only retry before succeeding. That run was reconciled and cancelled, retaining its receipt; it is not counted as successful end-to-end verification. Across both runs there were **three SQL data queries and two Power BI data queries**, plus the connection retry. No SQL tier/overage settings, remote data/definitions or deployed UI changed. No LLM calls were needed.

Ignored artifacts: `.local/record-aggregate-live.sqlite`, `.local/record-aggregate-final-result.json`. The existing development catalog was not given a business confirmation.

## Next proof boundary

This closes the arithmetic connection between supported aggregate observations and bounded record evidence. It does not close shared-generation, remote publication exclusivity or effective report/identity context. Those remain prerequisites for broader semantic/causal certification and the frozen eight-family acceptance protocol; unified v2 UI and routing/deployment remain later work.
