# Synthesis validation against original evidence

2026-09-27 UTC. Tracking #193. Known-domain regression only.

## Structural decision

Validation now uses complete original observations from the frozen investigation,
not observations reconstructed from the provider digest. The digest remains the
bounded provider presentation and restricts which receipt IDs may be cited.
For those IDs, validation receives deep copies of whole original records,
including nested and future fields. Missing, duplicate or non-completed original
receipts fail explicitly. The deterministic classification also comes from the
original assessment. There is no projected-evidence fallback.

The alternative, asserting a list of fields read by validators, was rejected:
a manually maintained field list repeats the coupling that caused this failure.
A downstream validator can add a field without requiring a synthesis projection
update. Source and digest hashes are checked again before committing synthesis;
changes to a field omitted from the provider digest still invalidate the run.
The provider never receives the complete private source state.

The regression test exercises the actual synthesis runtime, adds an arbitrary
future nested validation fact absent from the digest, and asserts that the entire
original observation reaches downstream validation unchanged. Further tests cover
hidden citation rejection, original-source mutation fencing, genuine process
comparison/attestation validation and contradictory digest fields. Existing receipt
verification and the equal cross-surface requirement remain in force.

## Saved R2 offline

Session `54509912-5e30-4850-afd7-ed26b5bc56aa` now passes digest construction and
response validation as `CONSISTENT_TO_BOUNDARY`. No next validation failure was
observed. The source file remains unchanged. There were zero network/provider
calls and no modifications to the original session or usage.

There is no saved LLM synthesis response: R2 originally stopped before dispatch.
This offline check uses its original deterministic assessment projected to the
response schema. It demonstrates contract completion, not a model-response replay.
The live run below tests actual provider synthesis.

Before and after, the synthesis digest has five evidence entries and 6,298
characters, hash `219639d7b982e51bc34c4643fba54036cdad2c8ddc70e5f0aba5f466b956aa61`.
No provider/planner payload shaping changed. Investigation directory and SQL-object
coverage are unchanged; eleven golden projection tests passed, alongside the
runtime assertion that synthesis leaves the investigation payload identical.

[Offline result](runs/synthesis-original-evidence-offline.json).

## Live run and validation

One attempt, session `3f8a7318-edfa-4bee-9760-76e183ac04e7`, engine commit
`be1cfd7db7ec21803ed43eebd2dc924a6ea8bfe6`. Same G ticket, model, context,
read limit 6, cumulative input limit 384,000, GPT-5.4 medium/8,000 output/120-second
profile and 65-second evaluator pacing. Recording enabled; no retry or setting,
permission, quota, approval or discovery change. Intake passed as a mismatch
complaint with vertical scope.

| Probe | Execution surface | Attestation | Result |
| --- | --- | --- | --- |
| Power BI baseline | POWER_BI_DAX; workspace `149f8d99-1c66-4a0a-9624-759be002bb60`; model `3484a2bc-98c5-4cef-be5c-a6215484075e` | MATCHED reader identity; engine, connection and object not self-reported | Handled Quantity = 8,765 |
| Gold comparison | FABRIC_SQL; SQL endpoint listed in the machine report; database `warehouse_gold_e1b8e1`, `dbo.movement_values` | MATCHED reader identity and database/object; engine and connection not self-reported | SUM(units) = 8,765 |
| Ingestion metadata | OneLake Delta log for Gold `movement_values`, lakehouse `b0ab76f7-20c7-410e-90e4-2c4eb104059a` | Existing metadata identity/transport, no independent identity attestation in this receipt | AVAILABLE commit WRITE, 406 output rows; no row data or semantic verification |

Both compared data probes attest `investigator-reader@skynwhy.com`. Their receipt
IDs are `d52d962b-9c74-4237-a0f9-88c59775754c` and
`7a7f1706-3abf-4b53-846f-71472f6dc8ab`. Full connection/object triples and attestation
fields are preserved in the machine report and ledger.

**One genuinely cross-surface equal comparison, zero within-layer checks.**
Semantic Activity to Gold movement_values follows `DECLARED_BY_DEFINITION`.
The procedure labels it `CROSS_SURFACE_VERIFIED`; this does not certify all surface
fields or business correctness. Five surface-field attestation gaps remain.
No non-adjacent jump, skipped intermediate comparison or NOT_COMPARABLE receipt
was recorded. Investigation stopped at Gold with CAPABILITY_UNAVAILABLE: deeper
source comparisons were not executed. Source application declaration inspection
remains CAPABILITY_NOT_IMPLEMENTED; it is not evidence that no declaration exists.
Presentation freshness was skipped because refresh history is unavailable to the
isolated reader. Equal values did not trigger a transformation-definition judgment.
No stock-movement/adjustment row investigation or upstream correctness is claimed.

Reads: **one Power BI DAX, one Fabric SQL, one OneLake metadata invocation**.
The successful OneLake path performs two HTTP reads (listing and commit), so the
three reserved cloud operations represent four data/metadata requests, excluding
authentication. Two context observations comprise local path retrieval and that
OneLake report. No Azure SQL source read. Investigation planner calls: **zero**;
intake calls: **one**; synthesis calls: **one**. Two provider tapes were retained.
Wall time: 88.177 seconds.

**Synthesis ran but did not validate.** The provider proposed
CONSISTENT_TO_BOUNDARY, but local validation rejected its unsorted
`capabilities_declared` list with **`Declared capabilities must be a sorted unique list`**.
The stored runtime error is the safe ValueError category. Offline validation of
the unmodified recorded response reproduces the exact first failure; there was no
second provider call or response repair. This check stops at that first rejection
and makes no claim that later validation would succeed.

The deterministic outcome remains CONSISTENT_TO_BOUNDARY, limited to the observed
aggregate through Gold, the five unattested surface fields and unavailable deeper
capability. There is no validated synthesis assessment and no end-to-end or
unfamiliar-domain acceptance pass. The model's rejected response is preserved,
not promoted to a supported conclusion.

Usage reservations before -> after: planner 12 -> 14; cloud 7 -> 10;
input characters 509,748 -> 558,525; output tokens 18,000 -> 27,500. All 24 daily
reservations are settled. Measured provider usage: 17,455 input and 2,187 output
tokens (516 reasoning tokens included in output). Reference token cost $0.076442,
not an Azure billing measurement. Limits and counters were not reset or changed.

All 218 earlier ledger rows remain byte-identical; exactly one live row was
appended. Saved R2 and prior failures remain unchanged. Artifacts are under
`.local/synthesis-original-evidence-20260927/`; the new original run is retained
under `.local/unknown-domain-v4/runs/G-original-evidence-R2-repeat-20260927.json`.

[Per-run machine report](runs/synthesis-original-evidence-live.json) and
[recorded-response validation diagnostic](runs/synthesis-original-evidence-validation.json).

## Delivery

PR #259 merged after six successful checks as
`5dd5aef4f2926cedb1ec3f3509b2f24ff937d556`. This fix chooses original-evidence
validation for the structural reason above. Eighty focused tests passed, including
the generator and eleven planner projection checks. Full regression: **1,199 tests passed** in 257.343 seconds, Python exit 0.
ResourceWarnings remain in the preserved log. All 295 local document targets
resolved and `git diff --check` passed.
The run is preserved as failed synthesis; no further fixes or runs were attempted.
