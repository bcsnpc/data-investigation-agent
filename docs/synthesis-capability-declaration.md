# Canonical capability declarations

2026-09-27 UTC. Known-domain regression. Tracking #193.

## Cause and change

PR #260 merged after six green checks as
`beae4210c53685fdac3e99338dbc2f64e756e3ef`.

The deterministic procedure already converted the adapter capability set with
`sorted(set(capabilities))` in both its process support and technical output.
The prior failure was the synthesis model's new declaration: its response listed
POWER_BI_DAX baseline query before FABRIC_SQL aggregate query, followed by process
and ingestion descriptions. That list was unordered. It was not a direct leak of
the adapter set. The original response remains unchanged in its tape.

A shared declaration helper now emits sorted, unique string names at both the
deterministic producer and synthesis response-admission boundary, before local
validation or assessment persistence. It preserves names exactly. It does not
invent capabilities, copy an approved list over the response, default a missing
field, change case, retry the model or weaken the validator. Malformed types fail;
missing fields remain missing and strict validation still rejects them.
The validator retains its canonical-form requirement unchanged.

Tests assert that unordered and repeated names produce the same declarations in
both deterministic outputs and through the actual synthesis runtime. A separate
test proves that the validator still rejects an unordered declaration; malformed
and missing fields are not silently repaired. No provider request, directory,
SQL-object coverage or prompt changed. Eleven planner golden projection tests
and the synthesis payload-invariance test passed.

## One live same-ticket run

Session `27b56ba4-d762-4bec-9e3a-01b524a54ed8`, engine
`99b9fbbeba3a1ed402bf035db35c20521274fd97`. Same G ticket and discovered context,
GPT-5.4 medium/8,000 output/120-second profile, read limit 6, input limit 384,000,
65-second pacing, recording enabled. No policy, permission, quota, configuration,
deadline or scope change. One attempt; no retry. Intake passed.

| Probe | Execution surface | Self-attestation | Result |
| --- | --- | --- | --- |
| Baseline | POWER_BI_DAX, workspace `149f8d99-1c66-4a0a-9624-759be002bb60`, model `3484a2bc-98c5-4cef-be5c-a6215484075e` | MATCHED identity; connection, engine and object unattested | Handled Quantity = 8,765 |
| Declared lower source | FABRIC_SQL, endpoint in linked machine report, database `warehouse_gold_e1b8e1`, `dbo.movement_values` | MATCHED identity and database/object; connection and engine unattested | SUM(units) = 8,765 |
| Ingestion metadata | OneLake Delta log for Gold movement_values in lakehouse `b0ab76f7-20c7-410e-90e4-2c4eb104059a` | Existing metadata identity/transport; receipt has no independent identity attestation | AVAILABLE WRITE metadata, 406 output rows; not a row-content verification |

Both compared probes attest `investigator-reader@skynwhy.com`. Receipts:
`34f204d8-3935-4f76-b94c-0003c3e2029a` (DAX) and
`1b9947bb-5497-41e9-b927-ab6405cc856a` (SQL). All exact connection triples,
attestation fields and limits are in the [per-run report](runs/synthesis-capability-live.json).

One genuinely cross-surface equal comparison: semantic Activity -> Gold
movement_values, `DECLARED_BY_DEFINITION`, classified CROSS_SURFACE_VERIFIED.
Zero within-layer comparisons; no non-adjacent jumps or NOT_COMPARABLE boundaries.
Five surface fields are not self-attested; verification does not mean complete
surface attestation or business correctness. No deeper source boundary was
compared: investigation stopped at Gold with CAPABILITY_UNAVAILABLE. Application
source declaration inspection remains unimplemented, not proof of absent lineage.
Presentation freshness was skipped because isolated-reader refresh history is
unavailable. Equal values did not trigger transformation-definition judgment.

Reads: one DAX, one Fabric SQL, one OneLake metadata invocation (two HTTP reads:
listing and commit). Three reserved cloud operations; four data/metadata requests,
excluding authentication. No Azure SQL source query. Two context observations:
local path lookup and ingestion metadata. Zero investigation planner calls, one
intake call, one synthesis call. Two tapes retained. Wall time 112.052 seconds.

## Synthesis and actual outputs

**Synthesis ran, but did not validate.** Its unordered four-name declaration was
sorted successfully, preserving all names. The next validation failure was:
`Only capability-gap outcomes carry a missing capability`.
The response classified CONSISTENT_TO_BOUNDARY while setting missing_capability to:

> No displayed capability or receipt exposes the lower-level stock movement and related inventory adjustment records beneath [movement_values] for direct inspection in this digest.

Offline validation of the recorded response, applying only the new declaration
canonicalization, reproduces this first failure. No retry or further fix. Its
raw declaration, canonical declaration and rejection are preserved in the
[diagnostic](runs/synthesis-capability-validation.json). No assertion is made that
later validation would pass. The synthesis assessment is null; its prose is not
promoted to a validated answer.

The actual returned business and technical outputs therefore remain the
**deterministic outputs**, not the rejected model response. They are retained
verbatim in [actual output JSON](runs/synthesis-capability-outputs.json).

The business conclusion says exactly:

> Every comparable reachable layer agreed through fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values.

Its accompanying fields list no probe failures, the declared binding, all five
unattested surface fields, and the skipped refresh-history step. This is a scoped
aggregate agreement through Gold; it says nothing about the correctness of source
entries or adjustment intent.

The technical output contains these executed queries:

```dax
EVALUATE ROW("baseline", [Handled Quantity],"surface_identity",USERPRINCIPALNAME())
```

```sql
SELECT SUM([units]) AS [quantity] FROM [dbo].[movement_values]
```

It reports one resolved/executed boundary, zero within-layer checks, no
not-comparable boundaries, no probe failures, and visibility ending at Gold due
to CAPABILITY_UNAVAILABLE. It repeats the skipped freshness step, binding and
attestation gaps, and lists the eight sorted deterministic capabilities. Those
capabilities differ from the model's descriptive labels; this change does not
claim to verify model-declared names against adapter membership.

Final deterministic outcome: CONSISTENT_TO_BOUNDARY, observed aggregate scope
only. No validated synthesis, end-to-end pass, source correctness claim, freeze
or unfamiliar-domain acceptance.

## Usage and validation

Daily reservations before -> after: planner 14 -> 16, cloud 10 -> 13,
input characters 558,525 -> 607,302, output tokens 27,500 -> 37,000.
All 29 daily reservations settled; no resets or refunds. Measured provider usage:
17,456 input tokens (14,848 cached), 1,924 output (516 reasoning included).
Reference token cost $0.039092, not an Azure billing measurement.

All 219 previous ledger rows remain byte-identical; one new row appended.
Original run, provider tapes and failed response remain intact under
`.local/synthesis-capability-declaration-20260927/` and the linked source paths.
Eighty-two focused tests passed, including eleven golden projection checks and
two generator tests. Full regression: **1,201 tests passed** in 255.708 seconds, Python exit 0.
ResourceWarnings remain in the log. All 297 local document targets resolved;
`git diff --check` passed.

