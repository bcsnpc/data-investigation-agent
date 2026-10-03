# Evaluated-cell delta offline re-renderings

Date: 2026-10-03 America/Chicago. #325 merged as `9f7a86a`; implementation
#326 merged as `80ee496` with six green checks. Final stable local suite passed
1,633 tests in 288.234 seconds. Initial test and CI failures remain recorded on
#326; the unrelated legacy file passed 27 tests independently before the final
suite. No production fix was made to conceal that failure.

## Scope and preservation

One new offline rendering each for the three saved runs. No live investigation,
estate read, diagnostic/guard request, intake/planner/judge/synthesis model call,
retry or replacement. Original classifications, receipt contents and prior
outputs remain unchanged. The only new ledger evidence is three appended
OFFLINE_RESYNTHESIS rows. Historical cell bindings are the previously authorised,
byte-matching one-time migration for these three runs only; both outputs disclose
that cell identity was derived rather than recorded natively. R2/R3 reuse their
prior validated mechanism paragraphs and validate locally; no provider call.

All 18 protected original database records retain their hashes. All 47
protected source/previous-output files are also byte-unchanged. The old ledger is
an unchanged prefix. All three renders completed; each charged zero physical
requests, diagnostic reads, guard requests and model calls.

| Run | New offline rendering ID | Answer | Isolated evaluated delta |
| --- | --- | --- | --- |
| R1 | `offline-cell-delta-f399eb8a-2fb6-48aa-9532-906e0338d8fd` | No verdict: no figure supplied | North row 3,359 versus TOTAL 8,765; row selection alone |
| R2 | `offline-cell-delta-3f5f2e28-8555-4994-b25b-bae4269b36e6` | Saved declared context reproduces fixture-authored EMPTY | Event-day restriction: 92 to BLANK |
| R3 | `offline-cell-delta-2935fd6c-63e4-47ab-98e8-a38e192b4c35` | Saved declared context does not reproduce exact 9 | Event-day restriction: 92 to BLANK |

R1 retains the missing-figure verdict and OBSERVED row addressing. R2 preserves
literal RECEIPT and both slicer defaults, with the weaker saved-default claim.
R3 preserves moved slicer first in the non-reproduction open set. Named secondary
visuals have no numeric suffix. The event-day sentence is derived only from the
completed full-context/page-plus-slicer pair; the control differs by more than
one restriction and receives no such attribution. These remain within-layer,
partially attested observations, not snapshot-aligned or business-correctness
claims. BLANK is a quantity result, not proof of zero rows.

The user's previous illustrative target named the wrong restriction; the prior
renderer was right not to assert it. The evaluated pair isolates event day.

The literal sweep and shrinking debt allowance merged with #326. It records all
18 pre-existing engine files, including the three expected ones; existing debt
is not a neutrality pass. See [implementation](evaluated-cell-deltas.md) for
the complete inventory, scan scope and payload coverage measurements.

No fixture, configuration, approval, policy, cap, allowance, credit or grant
changed. Prior freezes remain invalidated. This is the requested stop after
section 1's re-render, with section 2 merged as well. Section 3 remains pending:
check both rolling windows before the 95-request recollection, then the additive
15-September fixture/context and two independently authored numeric runs.

## Verbatim outputs

### R1 business

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
Cell identity was derived retrospectively from the saved statement and definition, not recorded natively.
```

### R1 technical

```text
You asked: In Inventory Health e1b8e1 I selected warehouse North. Handled Quantity differs from the global total. Check the North selection and explain what report context you can and cannot reproduce.
Answer to your question: No verdict: no figure supplied.

What else was checked: the vertical walk stopped during process walk.
Reason: TOOL_UNAVAILABLE.

Completed within-layer cells:
Cell fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json (KEYED): WITHIN_LAYER_CHECK (declared-reproduction-d8964b006f1897843e4ab8efa01a1c351f1ed77cc6ac20c25467b12f6edbec3a): undeclared-context value 8765; declared-context value 3359. No reported figure supplied; the produced value has no reproduction verdict. North is a value of fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name; no declared filter restricts this report to it. Resolution OBSERVED, receipt 7bd40167-1c55-46af-affd-ee3e2c8d63dd.
The North row and the total differ by the row selection alone; no other declared report restriction applies.
Other Activity by warehouse (TOTAL, receipt declared-reproduction-3a403b9dd5670b5b82723419ffb22f87864e9370cdf0d9172e634539e5f5724a): declared-context value 8,765; undeclared-context value 8,765.
Other Movement Units (UNGROUPED, receipt declared-reproduction-b2d055eb7ea3ee4125d4b3d59cb6dce26e722852a63f5a5063484faafeefdd2d): declared-context value 8,765; undeclared-context value 8,765.
Limits:
- Assumed: viewer-changeable selections at their saved defaults; their current positions were not established.
- Active user selections, row-level security and a difference further back remain unestablished.
- The checks are not tied to a shared data version; they do not establish currency or business correctness.
Recommended action: Supply the figure or empty state that you saw in the report.
Cell identity was derived retrospectively from the saved statement and definition, not recorded natively.
```

### R2 business

```text
You asked: In Declared predicate fixture 20261001, on Saved predicate selections, the card Handled Quantity - extra visual predicate shows nothing (the visual is empty) for Handled Quantity. I selected warehouse North. Check whether the saved declared report context reproduces what the visual shows and explain what remains unknown about my selections.
Answer to your question: Yes — the saved declared context reproduces the reported figure.

The answering visual "Handled Quantity - extra visual predicate" produced nothing.
The applied selections were event day: 2026-09-14; movement type: RECEIPT; product name: Component 1; warehouse name: North.
These saved restrictions reproduce the reported figure of empty; this explains its reproduction by declared report design, not whether that design is intended.
The same calculation without applying report declarations returned 8,765; this is not an unrestricted total.
Adding the event day restriction takes 92 to nothing.
Other visual "Handled Quantity - page and slicers" produced 92.
Other visual "Handled Quantity - unfiltered" produced 8,765.
Assumed: viewer-changeable selections at their saved defaults; their current positions were not established.
An invoked bookmark or stored alternative was not established.
Active user selections, row-level security and a difference further back remain unestablished.
The checks are not tied to a shared data version; they do not establish currency or business correctness.
Recommended action: If the saved restrictions (event day: 2026-09-14; movement type: RECEIPT; product name: Component 1; warehouse name: North) are unintended, request an enhancement to the report selections, not a change to the data.
Cell identity was derived retrospectively from the saved statement and definition, not recorded natively.
```

### R2 technical

```text
You asked: In Declared predicate fixture 20261001, on Saved predicate selections, the card Handled Quantity - extra visual predicate shows nothing (the visual is empty) for Handled Quantity. I selected warehouse North. Check whether the saved declared report context reproduces what the visual shows and explain what remains unknown about my selections.
Answer to your question: Yes — the saved declared context reproduces the reported figure.

Measure: Handled Quantity.
You described the selected value as "warehouse"; that description was a hint, not a reason to choose a column. Its wording agrees with the resolved column name; this was recorded after resolution and did not affect it.
No independently compared boundary was established.
Cell fabric://149f8d99-1c66-4a0a-9624-759be002bb60/2bc1cb2d-9230-4b8f-b7dc-c9f6b2151995/part/definition%2Fpages%2F8b067ecb975e5af7a39b%2Fvisuals%2Fa32b6a48db655ac8a4f2%2Fvisual.json (UNGROUPED): WITHIN_LAYER_CHECK (declared-reproduction-68005673deb755335aec10d34c484b89530a95e36b2de4332473b622cbdf21f3): undeclared-context value 8765; declared-context value blank. The declared selections reproduce the reported figure of empty; they account for that figure without requiring a difference further back. The stated report declares a restriction carrying North; resolution EVIDENCE.
Adding the event day restriction takes 92 to nothing.
Other Handled Quantity - page and slicers (UNGROUPED, receipt declared-reproduction-1c94ef3abb68f28cd7723d6928e73e6beafc7382d9de1d7633ecb353f5191f45): declared-context value 92; undeclared-context value 8,765.
Other Handled Quantity - unfiltered (UNGROUPED, receipt declared-reproduction-676f93893c17ba42fa2e5d05bd89c671ef7a3f615c58f59df6b9f646188342e6): declared-context value 8,765; undeclared-context value 8,765.

The report selection evidence identifies the visual and checked measure, and the declared context receipts map that visual state to retrospective cell bindings. One declared context aligns with the empty rendered state, while other declared contexts map to nonempty measure states. Duplicate reads show repeated retrieval of the same report-side state across the checked reproductions.

Layers:
L0 - Activity in Warehouse Operations e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity
L1 - movement values in warehouse gold e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values
L2 - stock movements e1b8e1 in warehouse silver e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1
L3 - stock movements e1b8e1 in warehouse bronze e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1

Limits:
- Unattested connection on L0 (receipts 481b8698-9461-4d25-a2e1-af1e1e7a7d6c, 4c11d5b9-32cd-497c-9620-55d8a1c8aa61, 84f553bd-5200-4724-bf76-3744f1b06ab2); connection is not self-reportable on this surface for this reader.
- Checked through L0; stopped because capability unavailable.
- Unchecked L0 -> L1: Declared source comparison does not yet translate filtered scope faithfully..
- Unchecked L1 -> L2: Declared quantity trace supports only whole-entity scope without filters or grouping..
- Unchecked L2 -> L3: Declared quantity trace supports only whole-entity scope without filters or grouping..
- Unchecked L3 -> unresolved upstream: No declared upstream read for this quantity (literal initialization or derived/unsupported column).
- Quantities trace unchanged integral columns; joins may multiply rows and whole-row deduplication may remove them. Key uniqueness and intended grain are not established.
- Assumed: viewer-changeable selections at their saved defaults; their current positions were not established.
- An invoked bookmark or stored alternative was not established.
- Active user selections, row-level security and a difference further back remain unestablished.
- The checks are not tied to a shared data version; they do not establish currency or business correctness.

Recommended action: If the saved restrictions (event day: 2026-09-14; movement type: RECEIPT; product name: Component 1; warehouse name: North) are unintended, request an enhancement to the report selections, not a change to the data.

What else was checked: vertical path outcome NO_COMPARABLE_PATH.
Separate vertical-path probe 086de50b-c61f-4b86-ae05-c23fe3504b64: quantity 3359.
Cell identity was derived retrospectively from the saved statement and definition, not recorded natively.
```

### R3 business

```text
You asked: In Declared predicate fixture 20261001, on Saved predicate selections, the card Handled Quantity - extra visual predicate shows 9 for Handled Quantity. I selected warehouse North. Check whether the saved declared report context reproduces what the visual shows and explain what remains unknown about my selections.
Answer to your question: No — the saved declared context does not reproduce the reported figure.

The answering visual "Handled Quantity - extra visual predicate" produced nothing.
The applied selections were event day: 2026-09-14; movement type: RECEIPT; product name: Component 1; warehouse name: North.
This is not the reported figure of 9.
The same calculation without applying report declarations returned 8,765; this is not an unrestricted total.
Adding the event day restriction takes 92 to nothing.
Other visual "Handled Quantity - page and slicers" produced 92.
Other visual "Handled Quantity - unfiltered" produced 8,765.
A moved slicer, an invoked bookmark, user selection, row-level security or a genuine difference further back remains possible; none was excluded.
The checks are not tied to a shared data version; they do not establish currency or business correctness.
Recommended action: Supply the current slicer positions, invoked bookmark, other selections and viewing account to narrow the remaining possibilities.
Cell identity was derived retrospectively from the saved statement and definition, not recorded natively.
```

### R3 technical

```text
You asked: In Declared predicate fixture 20261001, on Saved predicate selections, the card Handled Quantity - extra visual predicate shows 9 for Handled Quantity. I selected warehouse North. Check whether the saved declared report context reproduces what the visual shows and explain what remains unknown about my selections.
Answer to your question: No — the saved declared context does not reproduce the reported figure.

Measure: Handled Quantity.
You described the selected value as "warehouse"; that description was a hint, not a reason to choose a column. Its wording agrees with the resolved column name; this was recorded after resolution and did not affect it.
No independently compared boundary was established.
Cell fabric://149f8d99-1c66-4a0a-9624-759be002bb60/2bc1cb2d-9230-4b8f-b7dc-c9f6b2151995/part/definition%2Fpages%2F8b067ecb975e5af7a39b%2Fvisuals%2Fa32b6a48db655ac8a4f2%2Fvisual.json (UNGROUPED): WITHIN_LAYER_CHECK (declared-reproduction-68005673deb755335aec10d34c484b89530a95e36b2de4332473b622cbdf21f3): undeclared-context value 8765; declared-context value blank. The declared selections do not reproduce the reported figure of 9. The stated report declares a restriction carrying North; resolution EVIDENCE.
Adding the event day restriction takes 92 to nothing.
Other Handled Quantity - page and slicers (UNGROUPED, receipt declared-reproduction-1c94ef3abb68f28cd7723d6928e73e6beafc7382d9de1d7633ecb353f5191f45): declared-context value 92; undeclared-context value 8,765.
Other Handled Quantity - unfiltered (UNGROUPED, receipt declared-reproduction-676f93893c17ba42fa2e5d05bd89c671ef7a3f615c58f59df6b9f646188342e6): declared-context value 8,765; undeclared-context value 8,765.

The report reading was paired with declared context definitions and repeated reads, then matched against retrospective cell bindings for each candidate context. Each candidate produced a declared-context result for the visual cell, allowing a direct within-layer comparison between the displayed figure and the reproduced value.

Layers:
L0 - Activity in Warehouse Operations e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity
L1 - movement values in warehouse gold e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values
L2 - stock movements e1b8e1 in warehouse silver e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1
L3 - stock movements e1b8e1 in warehouse bronze e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1

Limits:
- Unattested connection on L0 (receipts a32e71eb-e2e4-4216-93e8-2b0b1b2ceb62, 2dd4e8f9-6329-49ca-8811-dd28f7d7aa64, ba04e8f3-7aac-406c-934e-7ea1d106c56c); connection is not self-reportable on this surface for this reader.
- Checked through L0; stopped because capability unavailable.
- Unchecked L0 -> L1: Declared source comparison does not yet translate filtered scope faithfully..
- Unchecked L1 -> L2: Declared quantity trace supports only whole-entity scope without filters or grouping..
- Unchecked L2 -> L3: Declared quantity trace supports only whole-entity scope without filters or grouping..
- Unchecked L3 -> unresolved upstream: No declared upstream read for this quantity (literal initialization or derived/unsupported column).
- Quantities trace unchanged integral columns; joins may multiply rows and whole-row deduplication may remove them. Key uniqueness and intended grain are not established.
- A moved slicer, an invoked bookmark, user selection, row-level security or a genuine difference further back remains possible; none was excluded.
- The checks are not tied to a shared data version; they do not establish currency or business correctness.

Recommended action: Supply the current slicer positions, invoked bookmark, other selections and viewing account to narrow the remaining possibilities.

What else was checked: vertical path outcome NO_COMPARABLE_PATH.
Separate vertical-path probe 29ff57ce-c9d6-4de4-86a9-649674eaaeaf: quantity 3359.
Cell identity was derived retrospectively from the saved statement and definition, not recorded natively.
```
