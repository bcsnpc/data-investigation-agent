# Round Two: preserved source attempt and family E

2026-10-04. All attempts are known-domain regressions; prior freezes remain invalid.

## Independent authored source figure

A purpose-written Python script parsed only the retained notebook's embedded
seed literal and summed units, without calling the engine's compiler or query.
360 rows: warehouse subtotals 2,948 + 2,084 + 2,629 = **7,661**. These are authored
fixture figures, not a real user's observed number. Served application/model
state can differ; omission, duplication, mapping, scope, source changes or timing
could defeat this independently derived match. Aggregates do not prove the
absence of a particular expected record.

The first helper attempt failed before a call or read with a reservation-wrapper
TypeError. Its null-ID ledger row remains unchanged. The subsequent execution,
intake `bda61715-ec03-4156-92ba-6954a8720345`, made one intake call and zero reads,
then refused `Report unavailable: UNNAMED; candidates:`. No source comparison,
synthesis or outcome was produced. The reportless-model intake defect is being
fixed separately; these failures are not replaced.

## Unchanged family E

Session `44dabc8c-4c9c-4639-9532-31217f2453be` completed TRANSFORMATION_LOGIC with
validated synthesis: 10 physical requests, four diagnostic operations, six guards,
zero guard reuses. One DAX quantity, two SQL quantities and one other diagnostic;
the ledger's eight SQL requests include the six guards. One intake, one definition
judge, one synthesis, **zero investigation-planner calls**. Diagnostic cap 12;
Part B 272 -> 282 of the then-300 cap; rolling observed 424 -> 434 of 600.

The model/source boundary agreed at 8,765 (ENGINE_INDEPENDENT); the next boundary
diverged from 7,661 input to 8,765 output (OBJECT_DISTINCT). Each value query
reported identity, engine and object; connection remained unattested. Both
comparisons are SNAPSHOT_UNVERIFIED. The left join can explain the increase;
the requested currency question remains unanswered. Processing history was not
assessed before termination; no latency classification or application read occurred.
The older Silver/Bronze and unresolved-upstream boundaries remain unchecked.

### Business output (verbatim)

```text
You asked: Inventory Health e1b8e1 Handled Quantity may be stale. Inspect the available refresh and processing history and explain whether freshness can be established. I have not supplied a freshness SLA.
Answer to your question: Not answered.
Regarding whether the reported information is current: No completed currency check establishes whether the reported information is current. Refresh history was unavailable to the diagnostic reader. Processing history was not assessed before the investigation stopped.
What was found instead:

The report showed 8,765 for movements, matching the total used to prepare it. The table it is built from contained 7,661 for movements; the difference appears in the step that matches movements with rates. Several matching rates can cause an entry to contribute more than once. We have not confirmed the repeated matches, whether the checks describe the same moment, whether this matching rule is intended, or how movements were first entered. For the report and the table used to prepare it, the two checks used different calculation engines. For the table used to prepare the report and the table it is built from, the checks read different data sources; different calculation engines were not established, so a shared calculation fault could affect both. Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.
```

### Technical output (verbatim)

```text
You asked: Inventory Health e1b8e1 Handled Quantity may be stale. Inspect the available refresh and processing history and explain whether freshness can be established. I have not supplied a freshness SLA.
Answer to your question: Not answered.
Regarding whether the reported information is current: No completed currency check establishes whether the reported information is current. Refresh history was unavailable to the diagnostic reader. Processing history was not assessed before the investigation stopped.
What was found instead:

Measure: Handled Quantity.
B2 diverges: L2 (stock movements e1b8e1 in warehouse silver e1b8e1, upstream input) 7,661 -> L1 (movement values in warehouse gold e1b8e1, downstream output) 8,765.
B1 agrees: L1 (movement values in warehouse gold e1b8e1, upstream input) 8,765 -> L0 (Activity in Warehouse Operations e1b8e1, downstream output) 8,765.
ENGINE_INDEPENDENT: comparable quantity-bound engine self-reports differ; this is an engine-independent cross-surface comparison. (receipt boundary-1-comparison).
OBJECT_DISTINCT: comparable quantity-bound object self-reports differ; this verifies a data-path boundary, not engine-level independence. Shared computation faults are not excluded. (receipt boundary-2-comparison).
Declared-context reproduction unavailable: Declared-context reproduction is undeclared for question kind FRESHNESS.

A left join on product_id with rates occurs before movement_value is derived. The retained quantity column is carried through that join, and the definition states matching rows may multiply because uniqueness is not assumed. That operation can repeat unchanged units across joined rows, which aligns with the rise between the compared layers while the later comparison remains equal.

Layers:
L0 - Activity in Warehouse Operations e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity
L1 - movement values in warehouse gold e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values
L2 - stock movements e1b8e1 in warehouse silver e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1
L3 - stock movements e1b8e1 in warehouse bronze e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1

Limits:
- Unattested connection on L0 (receipt b8006c45-809b-4c94-bb1a-8d0a1e6d84b1).
- Unattested connection on L1 (receipt 0a14f9e1-6ee3-4385-a731-adc87cb71beb).
- Unattested connection on L2 (receipt dcb8e92d-6b2e-436a-9752-925d45771250).
- SNAPSHOT_UNVERIFIED for B1, B2: the reads cannot be tied to matching data versions; agreement does not prove currency, and different update timing was not excluded as a cause of divergence.
- Checked through L2; stopped because reached.
- Unchecked L2 -> L3: Investigation terminated before this boundary.
- Unchecked L3 -> unresolved upstream: No declared upstream read for this quantity (literal initialization or derived/unsupported column).
- Quantities trace unchanged integral columns; joins may multiply rows and whole-row deduplication may remove them. Key uniqueness and intended grain are not established.
- This explains the difference only through join-driven row multiplication visible in the definition. It does not establish which product_id values caused the increase.

Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.
```
