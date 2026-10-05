# Round Five C: preserved output transcripts

2026-10-05 UTC. Known-domain regressions, one authorised attempt per ticket.

## reproduction-empty

Session/intake: `e2add075-3677-4aef-9fe7-0ea6e0b915db`. Outcome: None.

No investigation narrative generated. Intake held with RESOLUTION_UNCERTAIN before a data read. Original refusal preserved.

## family-I

Session/intake: `e726e66c-17d1-4171-a6d3-ccb978aa800c`. Outcome: TRANSFORMATION_LOGIC.

### business_output

```text
You asked: For Inventory Health e1b8e1 Handled Quantity, what does adjustment reason Q49 mean, and should those adjustments affect this metric?
Answer to your question: Not answered.
Regarding business meaning and intended treatment: Technical flow evidence cannot establish authoritative business meaning; the remaining question requires a domain specialist.
What was found instead:

The declared layer showed 8,765 for movements, matching its declared input. The declared layer contained 7,661 for movements; the difference appears between the declared layer and the declared layer, in the step that matches movements with rates. Several matching rates can cause an entry to contribute more than once. We have not confirmed the repeated matches, whether the checks describe the same moment, whether this matching rule is intended, or how movements were first entered. For the declared layer and the declared layer, the two checks used different calculation engines. For the declared layer and the declared layer, the checks read different data sources; different calculation engines were not established, so a shared calculation fault could affect both. Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.
```

### technical_output

```text
You asked: For Inventory Health e1b8e1 Handled Quantity, what does adjustment reason Q49 mean, and should those adjustments affect this metric?
Answer to your question: Not answered.
Regarding business meaning and intended treatment: Technical flow evidence cannot establish authoritative business meaning; the remaining question requires a domain specialist.
What was found instead:

Measure: Handled Quantity.
B2 diverges: L2 (stock movements e1b8e1 in warehouse silver e1b8e1, upstream input) 7,661 -> L1 (movement values in warehouse gold e1b8e1, downstream output) 8,765.
B1 agrees: L1 (movement values in warehouse gold e1b8e1, upstream input) 8,765 -> L0 (Activity in Warehouse Operations e1b8e1, downstream output) 8,765.
ENGINE_INDEPENDENT: comparable quantity-bound engine self-reports differ; this is an engine-independent cross-surface comparison. (receipt boundary-1-comparison).
OBJECT_DISTINCT: comparable quantity-bound object self-reports differ; this verifies a data-path boundary, not engine-level independence. Shared computation faults are not excluded. (receipt boundary-2-comparison).
Declared-context reproduction unavailable: Declared-context reproduction is undeclared for question kind BUSINESS_MEANING.

The retained definition shows a left join from movements to rates on product_id with matching rows allowed to multiply, then carries units into the produced table while also deriving a value column. When more than one rates row matches a movements row, the carried units total can rise in the produced table relative to the source side of the checked boundary.

Layers:
L0 - Activity in Warehouse Operations e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity
L1 - movement values in warehouse gold e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values
L2 - stock movements e1b8e1 in warehouse silver e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1
L3 - stock movements e1b8e1 in warehouse bronze e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1

Limits:
- Unattested connection on L0 (receipt 20328d47-756b-47ce-94d8-f74b0751f7a3).
- Unattested connection on L1 (receipt 8cbf5283-ba10-43be-ba95-b0f2d8daacd8).
- Unattested connection on L2 (receipt 42f4b5ef-eca9-4aaa-8177-f9f3d4240798).
- SNAPSHOT_UNVERIFIED for B1, B2: the reads cannot be tied to matching data versions; agreement does not prove currency, and different update timing was not excluded as a cause of divergence.
- Checked through L2; stopped because reached.
- Unchecked L2 -> L3: Investigation terminated before this boundary.
- Unchecked L3 -> unresolved upstream: No declared upstream read for this quantity (literal initialization or derived/unsupported column).
- Quantities trace unchanged integral columns; joins may multiply rows and whole-row deduplication may remove them. Key uniqueness and intended grain are not established.
- This only explains the difference through join-driven row multiplication visible in the supplied definition; it does not establish whether duplicate matches actually occurred, whether other business rules exist.

Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.
```

## source-consistent

Session/intake: `1d60bd89-6b92-4f86-9e98-b5622adfa27d`. Outcome: CONSISTENT_TO_BOUNDARY.

### business_output

```text
You asked: In Application load fixture 20261003, Movement Units shows 7,661 units. I expected a movement numbered 900099 that is absent from the authored application fixture. Please trace the displayed total to the application so I know whether this is a pipeline question or an application question.
Answer to your question: Partly answered.
Regarding the requested comparison: The compared path agreed through the named checked depth; the application beyond it was not read, so the remaining question belongs to the application owner.
What the investigation established:

The checked reported calculation value was 7,661. The reported number agrees with the information checked so far. This does not establish whether the original entries or business rules are correct. The application itself was not read; the remaining question belongs with the application owner. The record you named was absent at every checked layer: reported calculation, landing table and application. The checks do not establish whether they describe the same moment; different update timing remains possible. For the reported calculation and the landing table, the two checks used different calculation engines. Recommended action: Ask the owner of the unchecked part of the process to investigate the remaining gap.
```

### technical_output

```text
You asked: In Application load fixture 20261003, Movement Units shows 7,661 units. I expected a movement numbered 900099 that is absent from the authored application fixture. Please trace the displayed total to the application so I know whether this is a pipeline question or an application question.
Answer to your question: Partly answered.
Regarding the requested comparison: The compared path agreed through the named checked depth; the application beyond it was not read, so the remaining question belongs to the application owner.
What the investigation established:

Measure: Movement Units.
B1 agrees: L1 (dbo.stock movements round two 20261003 in round two bronze 20261003; role LANDING, upstream input) 7,661 -> L0 (Movements in Application load fixture 20261003; role SEMANTIC, downstream output) 7,661.
ENGINE_INDEPENDENT: comparable quantity-bound engine self-reports differ; this is an engine-independent cross-surface comparison. (receipt boundary-1-comparison).
Declared-context reproduction unavailable: Declared-context reproduction is undeclared for model-only or layer-only named context.

The quantity for the measure at L0 (SEMANTIC) matches the quantity read at L1 (LANDING). The recorded trace carries that quantity unchanged across the checked boundary between those layers.

Presence checks: the record you named was absent in L0 (SEMANTIC, reported calculation); the record you named was absent in L1 (LANDING, landing table); the record you named was absent in L2 (APPLICATION, application).

Layers:
L0 - Movements in Application load fixture 20261003; role SEMANTIC: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements
L1 - dbo.stock movements round two 20261003 in round two bronze 20261003; role LANDING: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003
L2 - app.stock movements round two 20261003 in ordersops; role APPLICATION: sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945

Limits:
- Unattested connection on L0 (receipt 8db8b4f3-c834-41f0-8466-96c7028d8231).
- Unattested connection on L1 (receipt 9356b1d2-e2e3-4b36-b994-23b1600efae0).
- SNAPSHOT_UNVERIFIED for B1: the reads cannot be tied to matching data versions; agreement does not prove currency, and different update timing was not excluded as a cause of divergence.
- Checked through L1; stopped because not comparable.
- Unchecked L1 -> L2: Application quantity was not established; the original receipt records the failure..
- Quantities trace unchanged integral columns; joins may multiply rows and whole-row deduplication may remove them. Key uniqueness and intended grain are not established.

Recommended action: Ask the owner of the unchecked part of the process to investigate the remaining gap.
```

## family-F

Session/intake: `ae3436f4-3f72-4b7d-9e60-823a69ad83b0`. Outcome: CONSISTENT_TO_BOUNDARY.

### business_output

```text
You asked: Inventory Health e1b8e1 Extended Value seems overstated. Investigate the current total, the upstream data and available transformation definitions to identify a supported explanation.
Answer to your question: Partly answered.
Regarding the requested comparison: The compared path agreed through the named checked depth; the application beyond it was not read, so the remaining question belongs to the application owner.
What the investigation established:

The checked declared layer value was 57,043. A separate check of the declared layer agreed. This rules out a difference at that checked boundary, but does not prove the original records are correct. The original entries, unchecked selections, update timing and intended business rules remain outside what these comparisons establish. For the declared layer and the declared layer, the two checks used different calculation engines. Recommended action: Ask the owner of the unchecked part of the process to investigate the remaining gap.
```

### technical_output

```text
You asked: Inventory Health e1b8e1 Extended Value seems overstated. Investigate the current total, the upstream data and available transformation definitions to identify a supported explanation.
Answer to your question: Partly answered.
Regarding the requested comparison: The compared path agreed through the named checked depth; the application beyond it was not read, so the remaining question belongs to the application owner.
What the investigation established:

Measure: Extended Value.
B1 agrees: L1 (movement values in warehouse gold e1b8e1, upstream input) 57,043 -> L0 (Activity in Warehouse Operations e1b8e1, downstream output) 57,043.
ENGINE_INDEPENDENT: comparable quantity-bound engine self-reports differ; this is an engine-independent cross-surface comparison. (receipt boundary-1-comparison).
Declared-context reproduction unavailable: Declared-context reproduction is undeclared for question kind FIGURE_DIFFERENCE.

The recorded check compares the quantity read on Activity with the quantity read on movement_values and records equality for that checked step.

Layers:
L0 - Activity in Warehouse Operations e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity
L1 - movement values in warehouse gold e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values

Limits:
- Unattested connection on L0 (receipt 5008bf57-de23-4208-8f1a-940c7726d5fe).
- Unattested connection on L1 (receipt fee4965c-755d-4fa6-ace7-c6192bb70c22).
- SNAPSHOT_UNVERIFIED for B1: the reads cannot be tied to matching data versions; agreement does not prove currency, and different update timing was not excluded as a cause of divergence.
- Checked through L1; stopped because no lineage.
- Unchecked L1 -> unresolved upstream: No declared upstream read for this quantity (literal initialization or derived/unsupported column).

Recommended action: Ask the owner of the unchecked part of the process to investigate the remaining gap.
```
