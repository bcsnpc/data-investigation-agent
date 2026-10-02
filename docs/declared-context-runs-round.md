# Declared-context runs round: intake provenance failures

2026-10-02, America/Chicago. Engine: main `1503c01` (#304), fingerprint
`3d32d0d3cf812cf1cfce6deb0fc22c10d0e94b06fe689e2044cb3d0561860fc8`.
This is three attempted live known-domain tickets, not three completed investigations.

## Budget and conditions

Before the batch, the rolling ordinary allowance was 21/60 charged, with 39
available. All three attempts made zero estate requests, leaving 21/60 and 39
available immediately after the batch. No credits, cap changes, resets, refunds,
retries or replacement runs. Diagnostic cap four remains unchanged.
The estimated 95 physical requests for recollection cannot fit this window.
The user's final instruction also explicitly stops this round before fixture change.

The existing model context remains `3ae7607b-5a5e-46c6-8e1b-195dbabc9cae`.
Whole-config hash remains
`19e2ef0b0b5cb6bfd8df38c5fded6c1eaac40718b3926248ac62c61abf0cf8b6`.
No recollection or re-approval was performed. The catalog/config/engine snapshots
in all three intakes agree. Preview never ran, so approval eligibility was not
retested live by this batch.

All calls used deployment investigator-quality-54, the existing intake contract
at 1,500 output tokens, with no explicit reasoning request. Each provider response
was HTTP 200, completed, with no incomplete_details or provider error. Recording
captured each exact request and response; no investigation session was admitted.

| Run | Intake ID | Intake result | Intake / investigation planner / synthesis calls | Diagnostic / physical / guard reads |
| --- | --- | --- | --- | --- |
| R1 | 6cbd873a-4fcc-48ec-9996-08eea0f85dd2 | HELD: RESOLUTION_UNCERTAIN | 1 / 0 / 0 | 0 / 0 / 0 |
| R2 | 26eacd71-5aac-45a9-ae7a-a1aea823fdd1 | HELD: RESOLUTION_UNCERTAIN | 1 / 0 / 0 | 0 / 0 / 0 |
| R3 | 4fee3350-f131-4e11-9ff3-e4293f91ba69 | HELD: RESOLUTION_UNCERTAIN | 1 / 0 / 0 | 0 / 0 / 0 |

## Independent fixture arithmetic and authored tickets

R1 uses Family D's original ticket unchanged:

> In Inventory Health e1b8e1 I selected warehouse North. Handled Quantity differs from the global total. Check the North selection and explain what report context you can and cannot reproduce.

R2 and R3 are fixture-authored, not observations from a user. R2 says the visual
shows nothing; R3 reports NUMBER 9. Their rationale is evaluator-only and was
not supplied to intake.

The retained notebook seed source is
`fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7ccafe59-0460-4c8a-a691-bfdfa75a2b25/part/notebook-content.py`,
content hash `3a980c4bd1920343202174c26b357be6233c6db267409d226d6a95fca4694273`.
Independent row selection, not an engine query, applies every active restriction:

- Page filter: movement_type IN RECEIPT.
- Visual filter: event_day IN 2026-09-14.
- ACTIVE saved warehouse slicer default: warehouse_name IN North.
- ACTIVE saved product slicer default: product_name IN Component 1.

Warehouse/product seed lookups resolve North and Component 1 to IDs 1/1.
Before the page's RECEIPT condition, exactly one movement matches the date and
both slicers: movement 300, warehouse 1, product 1, units 9, 2026-09-14, ISSUE.
RECEIPT excludes it. No selected movement remains. Exact-row deduplication and
rate-join multiplicity cannot introduce a selected movement where there are none.
The measure is SUM without COALESCE or +0, so its independently expected result
is BLANK, not numeric zero. EMPTY is therefore the authored reproduction state;
9 is the excluded ISSUE movement's quantity, chosen as a plausible different
selection's figure. This arithmetic does not certify the live query or estate.

## What actually stopped each attempt

The stored intake error is verbatim `RESOLUTION_UNCERTAIN` in every run. The
provider completed a PROPOSE, but returned invalid exact ticket spans. The
existing provenance validator correctly refused those spans. Offline inspection
of the preserved responses establishes the slices below without another provider
or estate call. Its exact diagnostic is
`Reported figure provenance differs from the ticket` (the shared validator is
also used for target spans).

| Run | Field | Claimed quote and span | Actual ticket slice | Correct quote start |
| --- | --- | --- | --- | --- |
| R1 | target | 'North', 54?59 | ' Hand' | 48 |
| R2 | target | 'North', 219?224 | 'er th' | 201 |
| R2 | figure | 'nothing', 132?139 | 'ing (th' | 128 |
| R3 | target | 'warehouse North', 168?183 | 'ouse North. Che' | 163 |
| R3 | figure | '9', 118?119 | 'a' | 128 |

R1 fails the target span before deterministic lookup. R2 and R3 fail the reported
figure span first; their target spans are independently invalid too. R3 also
quotes the compound phrase "warehouse North" rather than only the literal
selection value; that additional translation issue was not reached by lookup
and is not presented as a measured lookup failure.

No invalid span was corrected, substituted or retried. These are intake
translation failures, not proof that the adapter cannot handle a live native
predicate form. No engine/adapter patch is included.

## Required per-run evidence: not reached

For **each** of R1/R2/R3, there is no probe, execution surface, surface self-report,
attestation grade, inventory build, engine conservation result, ACTIVE-set
selection, target resolution, declared or undeclared-context measured quantity,
validated reported state/precision, comparison, outcome, or synthesis. Those
fields are NOT_REACHED, not zero declarations or a passed conservation check.
The authored states are R1 UNSPECIFIED, R2 EMPTY and R3 exact NUMBER 9; the model
responses did not validate them into procedure evidence.

**R1 business output:** Not generated; intake HELD.

**R1 technical output:** Not generated; intake HELD.

**R2 business output:** Not generated; intake HELD.

**R2 technical output:** Not generated; intake HELD.

**R3 business output:** Not generated; intake HELD.

**R3 technical output:** Not generated; intake HELD.

Consequently there is no reproduced-empty finding, moved-slicer open-set output,
saved-default qualification, or new surface attestation to quote. It would be
false to replace those absent outputs with the independently predicted answers.
The no-reported-figure attribution is still not live-verified. Separately, the
current no-figure procedure returns before reproduction probes; even a valid R1
intake would not by itself guarantee the requested computed value or inventory
verification. That code fact is reported, not changed here.

## Usage, preserved evidence and honesty check

Three charged intake reservations; zero investigation planner and synthesis calls.
Captured provider usage totals 44,378 input and 285 output tokens. The governor
retains all three uncertain reservations (4,500 reserved output tokens), because
validation failed before resolver usage returned. No retrospective settlement or
refund was made. Recorded reasoning-token usage is zero on all three responses.

| Run | Recording ID | Provider input / output tokens | Result artifact SHA-256 |
| --- | --- | --- | --- |
| R1 | 677942e9-88e0-4e43-95a2-4e7f6e598f45 | 14777 / 86 | 82ee81189308ca9c4d707cecf2efe246b6c4f9338d8bf8c1576523dccf41a35f |
| R2 | 4f708ec2-2ce7-4316-a8d2-43d81d37324c | 14803 / 99 | 458220bedad8af67410f67507a48c06dae594265c793fe4630f1891c0c5cce77 |
| R3 | 266152b9-e558-459b-8357-6b071ce32d88 | 14798 / 100 | ee7df92c34972fd54bd7b385ec089e7d5c416d9d43a47129bc8f47a4b15f7ebd |

Exact original artifacts, tickets, budgets and provider tapes remain in the local
runs-round/recordings folders; one ledger row is appended per attempted run.
The laptop restart happened after all three terminal artifacts were saved and
caused no replacement attempt. Historical Family D artifacts are unchanged.
Draft #297 is superseded by this PR with its existing evidence retained.

None of the three runs produced its expected procedure result, so no expected
success merits a guarantee claim. Independent arithmetic could disagree with a
live read if retained seed/definitions differed from served data, predicate
compilation differed, BLANK were mishandled, native query admission failed, or
surface evidence failed. The current failures precede those tests entirely.
No implementation or derivation guaranteed a successful live reproduction.

README/current status now record these failures, not a capability pass. Engine,
adapter, fixtures, config, permissions and budgets are unchanged; prior freezes
remain invalidated by earlier implementation changes. Stop before fixture change.

## Preserved provider proposals

Verbatim function-call arguments from each completed response, not corrected
proposals and not accepted procedure evidence:

R1:

```json
{"action":"PROPOSE","model_id":"m2","measure_id":"m2v3","metric_quote":"Handled Quantity","question":null,"filters":[],"dimension_ids":[],"target_request":{"source":{"start":54,"end":59,"quote":"North"}},"reported_candidates":[],"triage":"MISMATCH_COMPLAINT:VERTICAL"}
```

R2:

```json
{"action":"PROPOSE","model_id":"m2","measure_id":"m2v3","metric_quote":"Handled Quantity","question":null,"filters":[],"dimension_ids":[],"target_request":{"source":{"start":219,"end":224,"quote":"North"}},"reported_candidates":[{"start":132,"end":139,"quote":"nothing"}],"triage":"MISMATCH_COMPLAINT:VERTICAL"}
```

R3:

```json
{"action":"PROPOSE","model_id":"m2","measure_id":"m2v3","metric_quote":"Handled Quantity","question":null,"filters":[],"dimension_ids":[],"target_request":{"source":{"start":168,"end":183,"quote":"warehouse North"}},"reported_candidates":[{"start":118,"end":119,"quote":"9"}],"triage":"MISMATCH_COMPLAINT:VERTICAL"}
```
