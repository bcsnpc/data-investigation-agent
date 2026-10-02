# Quote-provenance reruns: new stops after offset arithmetic moved to code

2026-10-02, America/Chicago. #305 merged as `7018b2f`; #306 merged as `cabb98c`
after 1,499 local regressions and six exact-head CI checks passed. No run occurred
in the implementation PR. This report preserves three new live attempts.

## Conditions and budget

All three tickets are byte-identical to the first [runs round](declared-context-runs-round.md).
New request keys and intake IDs distinguish these attempts; no previous artifact,
response or ledger row is replaced. The existing model context is
`3ae7607b-5a5e-46c6-8e1b-195dbabc9cae`; whole-config hash is
`19e2ef0b0b5cb6bfd8df38c5fded6c1eaac40718b3926248ac62c61abf0cf8b6`.
No reapproval, recollection, fixture change, permission change, policy increase,
refund, retry or credit grant. The ordinary rolling allowance stayed 21/60 charged
with 39 available. All attempts made zero estate requests against unchanged
per-run diagnostic cap four. Recollection's estimated 95 requests cannot fit39;
the fixture mutation also explicitly waits for this report.

Deployment investigator-quality-54, 1,500 output tokens, no explicit intake
reasoning request, same existing conditions. Three HTTP200 completed responses,
no provider error or incomplete-details, no model-supplied offsets. Exact requests,
responses, local logs, terminal intakes and before/after usage snapshots remain
preserved. This is three attempted tickets, not three investigations completed.

| Rerun | Intake ID | Actual stop | Intake / investigation planner / synthesis calls | Diagnostic / physical / guard reads |
| --- | --- | --- | --- | --- |
| R1 | fc63e1c1-44bd-43e8-8606-9f745cdcc3e3 | HELD / INVALID_OR_STALE_PROPOSAL; extraction refused NON_SCALAR_VISUAL_CONTEXT | 1 / 0 / 0 | 0 / 0 / 0 |
| R2 | 6f5f5da5-9c2d-4bd3-b5a2-770472560cc6 | NEEDS_INPUT / quote occurs 2 times | 1 / 0 / 0 | 0 / 0 / 0 |
| R3 | f3e0a668-2946-49bc-8b6b-006e64400f14 | NEEDS_INPUT / quote occurs 2 times | 1 / 0 / 0 | 0 / 0 / 0 |

## R1: valid computed provenance, then a native extraction refusal

The provider quoted `warehouse North`. Code located it exactly at38-53 in the
unchanged Family D ticket; no offset arithmetic failure occurred. The resolver
returned a PROPOSE with UNSPECIFIED reported figure. Intake then invoked the
adapter's retained candidate-visual extraction and HELD, recording the exact
error `INVALID_OR_STALE_PROPOSAL`. Local inspection of the same pinned context,
without cloud calls, reproduced the underlying refusal:

> Declared-context reproduction unavailable: NON_SCALAR_VISUAL_CONTEXT.

The stack is targets() -> _extract() -> scalar-visual guard requiring exactly one
Values projection. Enumeration visits measure-bearing retained visuals before
inventory lookup and encountered a visual it cannot compile as scalar. No new
support for that form was added, no check weakened and no replacement run made.
The stored generic HELD label hides that reason; this report records the recovered
reason separately rather than editing the original intake.

The extracted phrase is also not the literal `North`. Exact inventory-value
lookup never ran, so this is a separately observed translation issue, not an
observed zero-match refusal. Even a valid span is provenance, not proof of a
correctly extracted selection. EVIDENCE was not produced.

## R2 and R3: exact repeated quote refusal

Both model responses quote `Handled Quantity` as metric provenance. That text
occurs twice in each saved ticket. The locator refuses rather than choosing an
occurrence. The user-visible question in both intakes is verbatim:

> Provenance quote occurs 2 times in the ticket; supply a longer unique quote.

The figure and target quotes occur exactly once, but metric uniqueness fails
before a validated proposal or inventory lookup. R2 quotes the empty visual
wording; R3 quotes `shows 9 for Handled Quantity`. They were not accepted as
procedure evidence. A longer metric quote could locate uniquely, as the offline
tests establish; no second provider extraction or ticket modification was made.
The requested longer-quote option is not an automatic retry mechanism.

## Independent derivation and authored figures

The full independent derivation from the retained notebook seed remains in the
first report and was not obtained from an engine query. All active restrictions:
page RECEIPT; visual2026-09-14; saved warehouse slicer North; saved product slicer
Component1. Warehouse/product lookup selects IDs1/1. The only movement satisfying
date and both slicers is300, units9, ISSUE. RECEIPT excludes it; no row remains.
Deduplication and rate-join multiplicity do not introduce a selected row.
SUM without COALESCE or +0 is BLANK, not0. R2's EMPTY and R3's exact9 remain
fixture-authored figures, never user-observed facts or values transcribed from
compiled queries. Seed content hash
`3a980c4bd1920343202174c26b357be6233c6db267409d226d6a95fca4694273` is unchanged.

## Required run detail and outputs

For **each** rerun: no investigation session admitted; no probe, execution surface,
self-reported engine/identity/object, attestation grade, comparison or measured
quantity. Inventory counts, ACTIVE/CONDITIONAL/UNSUPPORTED dispositions and engine
conservation are NOT_REACHED, not zero or confirmed. Target resolution is not
EVIDENCE/STATED/REFUSED because extraction/quote admission stopped before it.
No restrictions entered a procedure active set; no validated figure precision
was compared. No procedure outcome, declared-context reproduction or synthesis
ran. Business and technical output for every run: **not generated**.

- R1 business output: not generated; intake HELD.
- R1 technical output: not generated; intake HELD.
- R2 business output: not generated; intake NEEDS_INPUT, quoted question above.
- R2 technical output: not generated; intake NEEDS_INPUT.
- R3 business output: not generated; intake NEEDS_INPUT, quoted question above.
- R3 technical output: not generated; intake NEEDS_INPUT.

No assumed-slicer-default qualification or moved-slicer open-set output exists
to grade. The quantity-bound INFO self-description, EMPTY comparison and live
inventory/reproduction remain unverified. The no-figure attribution also remains
unverified live; its early return before reproduction probes has not changed.

## Usage, recording and honesty

Three intake calls, zero estate reads, zero investigation planner/synthesis calls.
Captured provider usage44,372 input/269 output tokens; 4,500 output tokens reserved
without refunds. The two quote refusals now preserve known usage and settle
normally; original #305 uncertain reservations remain untouched. No reasoning
tokens were reported. One new ledger row per attempt; no prior row changed.

| Rerun | Recording ID | Provider input / output tokens | Result SHA-256 |
| --- | --- | --- | --- |
| R1 | 5e772f9f-2163-4a7a-97e3-f0fa0816e2bf | 14775 / 79 | 03d2f82888dbd3ff5d8bbf57c85cfb67e85090d6a9c54136835ffc0b0e4ec61e |
| R2 | 747218b6-2621-45ac-83d9-f3abd0424fc6 | 14801 / 100 | 7c2f603b76b14e73d60341ca3b93381cc4d82df6a2e559cd46079b14543eafa5 |
| R3 | a98d93fe-08eb-42a6-9336-76fb47073174 | 14796 / 90 | 440d97491c8c45ab05f07fcb0c2d97a005ae3c7062672c7119639517442bc569 |

None reached its expected procedure result, so no successful reproduction is
claimed or treated as guaranteed. Correct exact location is demonstrated, but
translation correctness, unique target applicability, supported native visual
shape, faithful predicate compilation, BLANK preservation, served-data agreement
and query-bound attestation could all independently prevent a reproduction.
The independent arithmetic guarantees none of those runtime properties.

This evidence PR changes no engine/adapter/config/fixture/budget. README and current
status updated; earlier freezes remain invalidated. Stop before fixture change.

## Verbatim completed provider proposals

R1:

```json
{"action":"PROPOSE","model_id":"m2","measure_id":"m2v3","metric_quote":"Handled Quantity","question":null,"filters":[],"dimension_ids":[],"target_request":{"source":{"quote":"warehouse North"}},"reported_candidates":[],"triage":"MISMATCH_COMPLAINT:VERTICAL"}
```

R2:

```json
{"action":"PROPOSE","model_id":"m2","measure_id":"m2v3","metric_quote":"Handled Quantity","question":null,"filters":[],"dimension_ids":[],"target_request":{"source":{"quote":"warehouse North"}},"reported_candidates":[{"quote":"the card Handled Quantity - extra visual predicate shows nothing (the visual is empty)"}],"triage":"MISMATCH_COMPLAINT:VERTICAL"}
```

R3:

```json
{"action":"PROPOSE","model_id":"m2","measure_id":"m2v3","metric_quote":"Handled Quantity","question":null,"filters":[],"dimension_ids":[],"target_request":{"source":{"quote":"warehouse North"}},"reported_candidates":[{"quote":"shows 9 for Handled Quantity"}],"triage":"MISMATCH_COMPLAINT:VERTICAL"}
```
