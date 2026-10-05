# Round Five F: worker boundary, replay compatibility and resumed list

2026-10-05 UTC. Known-domain work; no unfamiliar-domain acceptance claim.

## Worker boundary

PR #395 merged 26b6277 after six green checks. Native worker configuration is a
consumer-owned projection of the declared reachable semantic layer and configured
reader; its allowlist is narrowed to the requested model after checking existing
scope. Runtime _estate, budgets, roles and arbitrary future metadata cannot enter
the child config.22reader,9rejection,19manifest and33adaptive focused tests passed.
The extra-manifest-key and actual serialized transport tests pass worker load_config.
No grant or relaxed general manifest validation. Prior freezes invalidated.

## Why blocked meant different things

The twelve current-engine blocks from the prior gate were not twelve schema
failures. Every envelope is v1; G/H fail stronger budget-conservation validation,
not the format version. The other ten apply a new intake producer to historical
input. Their first sealed provider input lacks value_roles and is insertion-order
serialized; current wire_contract adds value_roles and current serialization sorts
keys. The provider byte mismatch is masked by the following finally-block budget
settlement, yielding TAPE_EVENT_DIFFERS:BUDGET:PROVIDER_RESPONSE. That late error
does not establish a provider outage or a bad historical response.

The attempted serializer-only diagnostic was discarded: it correctly detected a
structural /value_roles difference. Both failed offline attempts and the successful
pinned A smoke are separately recorded, zero requests. No current payload field
was removed to force compatibility.

| Prior blocked ticket | What its prior block means |
| --- | --- |
| family-A | Current intake/request producer differs from sealed historical input; later settlement masks the earlier byte mismatch. |
| family-B | Current intake/request producer differs from sealed historical input; later settlement masks the earlier byte mismatch. |
| family-C | Current intake/request producer differs from sealed historical input; later settlement masks the earlier byte mismatch. |
| family-E | Current intake/request producer differs from sealed historical input; later settlement masks the earlier byte mismatch. |
| family-G | Incomplete recording: external budget input absent; no checkpoint can be invented. |
| family-H | Incomplete recording: external budget input absent; no checkpoint can be invented. |
| reproduction-16 | Current intake/request producer differs from sealed historical input; later settlement masks the earlier byte mismatch. |
| reproduction-empty | Current intake/request producer differs from sealed historical input; later settlement masks the earlier byte mismatch. |
| source-consistent | Current intake/request producer differs from sealed historical input; later settlement masks the earlier byte mismatch. |
| source-gap | Current intake/request producer differs from sealed historical input; later settlement masks the earlier byte mismatch. |
| source-latency | Current intake/request producer differs from sealed historical input; later settlement masks the earlier byte mismatch. |
| source-unreachable | Current intake/request producer differs from sealed historical input; later settlement masks the earlier byte mismatch. |

PR #396 merged9079039 after six green checks. v2 envelopes seal a committed Git
engine revision and refuse recording uncommitted engine bytes. v1 remains
readable; the N?N+1 test replays its unchanged sealed bytes. The isolated helper
executes a pinned Git revision with sockets blocked and exact request/final matching.
Legacy compatibility revisions are separate annotations bound to run/tape hashes,
not a claim that those exact commits were originally recorded. Recorded engine
hash, executed revision and tape version remain separate evidence. No response,
missing budget event or final prose is substituted.25tape and4decoder focused
tests passed; context coverage2entries/1SQL/7540characters stayed unchanged.

Historical replay answers whether the original decisions/outputs reproduce under
that compatible historical producer. It does not requalify the current engine.
The current-engine2/15 finding is preserved; this regrade is a distinct column.

## Fixture-state correction before the resumed list

Local read-only approval inspection found D/G/H current. EMPTY is report-14sep,
not report-15sep as the earlier stopped-batch table incorrectly said. That earlier
row described a run never attempted; this is an appended correction, not altered
evidence. EMPTY and source-baseline lacked current state approval at inspection.
A state cannot be inferred from a context ID or silently approved from a name.
No fixture or permission changed during this inspection.

The full fifteen regrade must finish before pre-warm or any live investigation.
The stop rule remains first unmet expectation; no cap raise, counter reset,
replacement attempt or missing-record backfill is authorised.

## Complete offline regrade before live work: 10/15

Zero estate requests and model calls. Ten pass, one faithful replay fails grading, four block. Original rows, tapes and outputs untouched.

| Ticket | Versioned historical result | Remaining reason |
| --- | --- | --- |
| family-A | PASSED | Byte-exact replay, structured match and invariants pass |
| family-B | PASSED | Byte-exact replay, structured match and invariants pass |
| family-C | PASSED | Byte-exact replay, structured match and invariants pass |
| family-D | BLOCKED | TAPE_UNRECORDED_IDENTITY:10543e9a-8a9e-4ac2-9596-e9cc127c209e |
| family-E | PASSED | Byte-exact replay, structured match and invariants pass |
| family-F | PASSED | Byte-exact replay, structured match and invariants pass |
| family-G | BLOCKED | TAPE_UNRECORDED_BUDGET_INPUT |
| family-H | BLOCKED | TAPE_UNRECORDED_BUDGET_INPUT |
| family-I | PASSED | Byte-exact replay, structured match and invariants pass |
| reproduction-16 | PASSED | Byte-exact replay, structured match and invariants pass |
| reproduction-empty | BLOCKED | TAPE_EVENT_DIFFERS:BUDGET:PROVIDER_RESPONSE |
| source-consistent | FAILED | OUTPUT_INVARIANT_FAILED |
| source-gap | PASSED | Byte-exact replay, structured match and invariants pass |
| source-latency | PASSED | Byte-exact replay, structured match and invariants pass |
| source-unreachable | PASSED | Byte-exact replay, structured match and invariants pass |

All tapes remain v1; passing compatibility engines are5c3daad or7abaabf, separately hash-bound. Source consistency remains CONSISTENT_TO_BOUNDARY, not upgraded. New failed D33e5be52 is also preserved and remains an unsuccessful acceptance attempt. Pot221/400 unchanged before the resumed list.

## Resumed controls and successful new recordings

Pre-warm connected on its second attempt: first connection returned SQL 40613,
then a recorded five-second resume wait. Two physical CONTROL requests, zero
diagnostic reads, zero model calls. Pot 221 -> 223/400; rolling 420 -> 422/1500.
No source setting, permission or data changed. Engine revision 9079039.

### family-D: 7c23cadc-e788-483e-8fbf-0a14b46182d5

Fixture inventory-baseline; outcome NO_COMPARABLE_PATH; synthesis COMPLETED. V2 recording and byte-exact replay PASSED, followed by structured grading and output invariants. Intake calls 1; investigation planner calls 0; judge calls 0; synthesis calls 1. Diagnostic reads 6/12, guard requests 0, physical requests 6. Pot 223 -> 229/400; rolling after 428/1500.

Six DAX probes completed on the model. Identity, engine and model matched; connection remained unattested (PARTIAL). Within-layer row North 3,359 and undeclared-context 8,765; total/whole-visual 8,765. No supplied reported figure, so NO_REPORTED_FIGURE, no reproduction verdict. No lower boundary verified; faithful filtered-scope refusal unchanged. North is a row address, not a declared filter.

#### Business Output (verbatim)

```text
You asked: In Inventory Health e1b8e1 I selected warehouse North. Handled Quantity differs from the global total. Check the North selection and explain what report context you can and cannot reproduce.
Answer to your question: No verdict: no figure supplied.

The selected row "Activity by warehouse" produced 3,359.
The applied selections were warehouse name: North.
No reported figure supplied; the produced value has no reproduction verdict.
The same calculation without applying report declarations returned 8,765; this is not an unrestricted total.
The North row and the total differ by the row selection alone; no other declared report restriction applies.
North was observed as a value addressing the displayed row, not declared as a report filter.
Other displayed total row "Activity by warehouse" produced 8,765.
Other visual "Movement Units" produced 8,765.
Assumed: viewer-changeable selections at their saved defaults; their current positions were not established.
Active user selections, row-level security and a difference further back remain unestablished.
The checks are not tied to a shared data version; they do not establish currency or business correctness.
Recommended action: Supply the figure or empty state that you saw in the report.
```

#### Technical Output (verbatim)

```text
You asked: In Inventory Health e1b8e1 I selected warehouse North. Handled Quantity differs from the global total. Check the North selection and explain what report context you can and cannot reproduce.
Answer to your question: No verdict: no figure supplied.

Measure: Handled Quantity.
You described the selected value as "warehouse"; that description was a hint, not a reason to choose a column. Its wording agrees with the resolved column name; this was recorded after resolution and did not affect it.
No independently compared boundary was established.
Cell fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json (KEYED): WITHIN_LAYER_CHECK (declared-reproduction-d8964b006f1897843e4ab8efa01a1c351f1ed77cc6ac20c25467b12f6edbec3a): undeclared-context value 8765; declared-context value 3359. No reported figure supplied; the produced value has no reproduction verdict. North is a value of fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name; no declared filter restricts this report to it. Resolution OBSERVED, receipt 6c5bfd10-2eb6-4189-904c-73329797a75f.
The North row and the total differ by the row selection alone; no other declared report restriction applies.
Other Activity by warehouse (TOTAL, receipt declared-reproduction-3a403b9dd5670b5b82723419ffb22f87864e9370cdf0d9172e634539e5f5724a): declared-context value 8,765; undeclared-context value 8,765.
Other Movement Units (UNGROUPED, receipt declared-reproduction-b2d055eb7ea3ee4125d4b3d59cb6dce26e722852a63f5a5063484faafeefdd2d): declared-context value 8,765; undeclared-context value 8,765.
Declared-context reproduction unavailable: No reported figure supplied.

The investigation reproduces the measure within the report layer in three scopes. It matches the measure definition to a warehouse keyed row and to a total row, then evaluates the current warehouse selection for North against the broader total. The warehouse keyed row for North returns a smaller figure, while the total row returns the broader figure, so the visible difference aligns with a warehouse restriction being active in the report context. A separate whole visual read also reproduces the broader figure, showing the same measure is being read across those report scopes.

Layers:
L0 - Activity in Warehouse Operations e1b8e1; role SEMANTIC: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity
L1 - movement values in warehouse gold e1b8e1; role SERVING: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values
L2 - stock movements e1b8e1 in warehouse silver e1b8e1; role REFINED: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1
L3 - stock movements e1b8e1 in warehouse bronze e1b8e1; role LANDING: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1

Limits:
- Unattested connection on L0 (receipts 358b07f3-010e-4fe7-89b3-4b0a1b37c47e, ca82e0f6-bdcc-4705-9641-5fc61c447bcd, 706fd2af-eb40-4900-b4fb-5eaaa7375fe1, 574bbf32-a620-4f60-9799-f485cd2292e5); connection is not self-reportable on this surface for this reader.
- Checked through L0; stopped because capability unavailable.
- Unchecked L0 -> L1: Declared source comparison does not yet translate filtered scope faithfully..
- Unchecked L1 -> L2: Declared quantity trace supports only whole-entity scope without filters or grouping..
- Unchecked L2 -> L3: Declared quantity trace supports only whole-entity scope without filters or grouping..
- Unchecked L3 -> unresolved upstream: No declared upstream read for this quantity (literal initialization or derived/unsupported column).
- Quantities trace unchanged integral columns; joins may multiply rows and whole-row deduplication may remove them. Key uniqueness and intended grain are not established.
- Assumed: viewer-changeable selections at their saved defaults; their current positions were not established.
- Active user selections, row-level security and a difference further back remain unestablished.
- The checks are not tied to a shared data version; they do not establish currency or business correctness.

Recommended action: Supply the figure or empty state that you saw in the report.

What else was checked: vertical path outcome NO_COMPARABLE_PATH.
Separate vertical-path probe a1b41744-376c-4326-a668-502c602ea032: quantity 3359.
```

### family-G: c3be2f05-4af5-4813-85da-2bc7206cd0df

Fixture inventory-baseline; outcome TRANSFORMATION_LOGIC; synthesis COMPLETED. V2 recording and byte-exact replay PASSED, followed by structured grading and output invariants. Intake calls 1; investigation planner calls 0; judge calls 1; synthesis calls 1. Diagnostic reads 4/12, guard requests 6, physical requests 10. Pot 229 -> 239/400; rolling after 438/1500.

One DAX diagnostic, two Fabric SQL quantity diagnostics and one retained transformation definition. Six SQL guard requests (three per object); no reuse or connection retry. Model/serving 8,765 agree across calculation engines; refined input 7,661 differs from serving output 8,765 across objects using the same SQL engine. Connections remain unattested (PARTIAL); every comparison SNAPSHOT_UNVERIFIED. Definition supports possible row multiplication from a left join, not verified duplicate matches or intended business semantics. Landing and application boundaries remain unchecked.

#### Business Output (verbatim)

```text
You asked: Inventory Health e1b8e1 Handled Quantity may include incorrect source entries. Inspect source stock movements and related inventory adjustments for evidence. Do not assume an adjustment record alone proves the intended business rule.
Answer to your question: Partly answered.
Regarding whether the application information was delivered: Independent quantities were compared within the checked scope; remaining boundaries, timing and business intent are limited by the recorded evidence.
What the investigation established:

The reported calculation showed 8,765 for movements, matching its declared input. The refined data contained 7,661 for movements; the difference appears between the refined data and the serving data, in the step that matches movements with rates. Several matching rates can cause an entry to contribute more than once. We have not confirmed the repeated matches, whether the checks describe the same moment, whether this matching rule is intended, or how movements were first entered. For the reported calculation and the serving data, the two checks used different calculation engines. For the serving data and the refined data, the checks read different data sources; different calculation engines were not established, so a shared calculation fault could affect both. Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.
```

#### Technical Output (verbatim)

```text
You asked: Inventory Health e1b8e1 Handled Quantity may include incorrect source entries. Inspect source stock movements and related inventory adjustments for evidence. Do not assume an adjustment record alone proves the intended business rule.
Answer to your question: Partly answered.
Regarding whether the application information was delivered: Independent quantities were compared within the checked scope; remaining boundaries, timing and business intent are limited by the recorded evidence.
What the investigation established:

Measure: Handled Quantity.
B2 diverges: L2 (stock movements e1b8e1 in warehouse silver e1b8e1; role REFINED, upstream input) 7,661 -> L1 (movement values in warehouse gold e1b8e1; role SERVING, downstream output) 8,765.
B1 agrees: L1 (movement values in warehouse gold e1b8e1; role SERVING, upstream input) 8,765 -> L0 (Activity in Warehouse Operations e1b8e1; role SEMANTIC, downstream output) 8,765.
ENGINE_INDEPENDENT: comparable quantity-bound engine self-reports differ; this is an engine-independent cross-surface comparison. (receipt boundary-1-comparison).
OBJECT_DISTINCT: comparable quantity-bound object self-reports differ; this verifies a data-path boundary, not engine-level independence. Shared computation faults are not excluded. (receipt boundary-2-comparison).
Declared-context reproduction unavailable: Declared-context reproduction is undeclared for question kind SOURCE_CORRECTNESS.

Between L2 (REFINED) and L1 (SERVING), a left join on product_id brings in rates while the traced quantity remains the unchanged units column. When the rates side contains more than one match for a product_id, the join can repeat movement rows, carrying units onto each repeated row and increasing the summed quantity in L1 (SERVING) relative to L2 (REFINED).

Layers:
L0 - Activity in Warehouse Operations e1b8e1; role SEMANTIC: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity
L1 - movement values in warehouse gold e1b8e1; role SERVING: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values
L2 - stock movements e1b8e1 in warehouse silver e1b8e1; role REFINED: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1
L3 - stock movements e1b8e1 in warehouse bronze e1b8e1; role LANDING: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1

Limits:
- Unattested connection on L0 (receipt d0863650-15c2-4efa-85dd-2990b095975c).
- Unattested connection on L1 (receipt a7d4376c-5714-4232-8209-d5482a3c43c7).
- Unattested connection on L2 (receipt 26e1211c-04f0-43d6-94e4-1696deebd87d).
- SNAPSHOT_UNVERIFIED for B1, B2: the reads cannot be tied to matching data versions; agreement does not prove currency, and different update timing was not excluded as a cause of divergence.
- Checked through L2; stopped because reached.
- Unchecked L2 -> L3: Investigation terminated before this boundary.
- Unchecked L3 -> unresolved upstream: No declared upstream read for this quantity (literal initialization or derived/unsupported column).
- Quantities trace unchanged integral columns; joins may multiply rows and whole-row deduplication may remove them. Key uniqueness and intended grain are not established.
- This explains the difference only through possible row multiplication from the join. The payload does not establish whether duplicate matches actually occurred for these data, and it also states that other business rules and a shared snapshot are not established.

Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.
```


### family-H: d93995a9-0e2d-47eb-805b-c4018c4e3b39

Procedure and synthesis COMPLETED, NO_KNOWN_PATTERN. One DAX diagnostic/physical request, zero guards; cap 1/12. Intake one, investigation planner zero, judge zero, synthesis one. Pot 239 -> 240/400; rolling 439/1500. Current inventory-baseline state. Semantic surface PARTIAL: engine, identity and model match, connection unreported. No lower boundary compared. Replay grade recorded below.

#### Business Output (verbatim)

```text
You asked: Warehouse Performance e1b8e1 Inbound Quantity and Outbound Quantity are different. Explain whether the current observed difference follows their definitions, and state what business intent remains unknown.
Answer to your question: Not answered.
Regarding business meaning and intended treatment: Technical flow evidence cannot establish authoritative business meaning; the remaining question requires a domain specialist.
What was found instead:

The checked declared layer value was 6,425. The available evidence did not establish a boundary comparison with the total used to prepare the report. A difference between the report and its input therefore remains possible. The original entries, unchecked selections, update timing and intended business rules remain outside what these comparisons establish. Recommended action: Ask the responsible owner to review the recorded missing evidence and next step.
```

#### Technical Output (verbatim)

```text
You asked: Warehouse Performance e1b8e1 Inbound Quantity and Outbound Quantity are different. Explain whether the current observed difference follows their definitions, and state what business intent remains unknown.
Answer to your question: Not answered.
Regarding business meaning and intended treatment: Technical flow evidence cannot establish authoritative business meaning; the remaining question requires a domain specialist.
What was found instead:

Measure: Inbound Quantity.
No independently compared boundary was established.
Declared-context reproduction unavailable: Declared-context reproduction is undeclared for question kind BUSINESS_MEANING.

The recorded logic stops at the Activity partition source because the movement values label lacks a stable discovered asset binding, so the engine cannot compile a quantity beneath the declared scope for this measure.

Limits:
- Checked through fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity; stopped because capability unavailable.

Recommended action: Ask the responsible owner to review the recorded missing evidence and next step.
```


## Stop and selected evidence map

H byte-exact replay and structured/output grading PASSED, zero requests.
EMPTY then refused in fixture selection, before intake, without estate reads or model calls:

```text
investigator.onboarding.Conflict: No approved context for fixture state report-14sep
```

That is a fixture-readiness refusal, not an EMPTY reproduction finding. The report
was documented as changed to 15 September in #327; no current report-14sep state
approval exists. The live list stopped; source consistency was not attempted.
No replacement, mutation, hand-pinned context or invented approval was used.
The absent source-baseline approval was also observed in preflight, but no source
consistency run was started. Failed setup has its own ledger row and exact private
console bytes/hash; no investigation session or outputs exist for it.

| Resumed ticket | New result | Physical / diagnostic / guard | Pot | Replay and grading |
| --- | --- | --- | --- | --- |
| D | NO_COMPARABLE_PATH; NO_REPORTED_FIGURE | 6 / 6 / 0 | 223 -> 229 | PASSED |
| G | TRANSFORMATION_LOGIC | 10 / 4 / 6 | 229 -> 239 | PASSED |
| H | NO_KNOWN_PATTERN | 1 / 1 / 0 | 239 -> 240 | PASSED |
| EMPTY | BLOCKED before intake: no approved report-14sep context | 0 / 0 / 0 | 240 -> 240 | No new tape |
| source consistency | NOT RUN under the stop rule | 0 / 0 / 0 | 240 -> 240 | Earlier failed evidence retained |

The complete historical regrade restored10/15 before any live work. Selecting the
three newly passed D/G/H recordings yields13/15, not a repeated all-fifteen current
engine test: ten are historical-engine compatibility replay and three are new
v2 current-engine replay. Original current-engine2/15 results remain preserved.

| Ticket | Selected evidence |
| --- | --- |
| family-A | PASSED |
| family-B | PASSED |
| family-C | PASSED |
| family-D | PASSED |
| family-E | PASSED |
| family-F | PASSED |
| family-G | PASSED |
| family-H | PASSED |
| family-I | PASSED |
| reproduction-16 | PASSED |
| reproduction-empty | BLOCKED: old tape byte mismatch; new fixture setup refused |
| source-consistent | FAILED: retained CONSISTENT_TO_BOUNDARY does not meet CONSISTENT_TO_SOURCE |
| source-gap | PASSED |
| source-latency | PASSED |
| source-unreachable | PASSED |

#376 remains draft;15/15 has not been earned. Its strict CI also lacks private
replay inputs (MISSING_PRIVATE_REPLAY_INPUTS), distinct from local grading.
No ordinary allowance, pot ceiling, diagnostic cap, identity, source or fixture
configuration changed. End pot240/400 including2 pre-warm controls; reserve50
remains, usable pot110. Rolling last observed439/1500. New investigation physical
requests17, diagnostics11, guards6, plus2 physical controls. No refunds or counter
resets. Prior freezes remain invalid.
