# Reviewed evidence handoff and the first two round probes

Date: 2026-10-03. Autonomous judgment: fix a discovered handoff defect before completing A7. Prior freezes invalidated. No fixture, permission, cap or policy change.

E and G both returned TRANSFORMATION_LOGIC with validated synthesis, zero reproduction reads and four diagnostic operations each. They do not yet demonstrate the new subject wiring: intake classified FRESHNESS / SOURCE_CORRECTNESS, but Intake.review reconstructed a partial proposal and discarded question_kind. The procedure therefore recorded UNCLASSIFIED. Both original runs and rows remain unchanged. Further batch work paused after G, with no active run during the fix.

The review now deep-copies the complete validated proposal rather than selecting fields again. Preview and procedure_scope use the same consumer-owned PROCEDURE_EVIDENCE_FIELDS declaration through server_evidence. A future declared consumer field cannot silently disappear between these two handoffs. Tests exercise the real intake/review/preview/procedure path, deep-copy isolation, complete proposal preservation, and a hostile future-field extension. Current wire semantics and all admission refusals remain unchanged.

These two runs are preliminary evidence under the pre-handoff-fix engine, not the final matched nine-family map. A fresh recorded nine-family batch will use the corrected handoff, unchanged tickets and the same approved limits. No earlier artifact is overwritten or used as a substitute for that measurement.

The initial window was 60/300; these probes used 20 physical requests and end at 80/300. Each used 4/12 diagnostic operations: one semantic value read, two SQL quantity reads, one metadata request, and six SQL guards. Each had one intake call, one definition judgment, zero investigation-planner calls and one synthesis call. The runtime planner_calls field counts the metered judge; the original ledger judge_calls incorrectly tested an event name that is never emitted. Append-only corrections record one PROCESS_JUDGMENT_RESERVED per run and zero exploration calls.

Adding the forwarded subject changes the saved E procedure envelope by the character count recorded below; it adds no directory, SQL object, measure, column or report entry. The preview/catalog coverage is unchanged. This is a single quoted proof field, not a per-entry annotation.

## E — 44d222b3-0743-47ce-b903-f8865aa16e2f

Outcome TRANSFORMATION_LOGIC; synthesis COMPLETED. Intake subject FRESHNESS; procedure subject absent. Envelope characters 1086 → 1282 when the existing subject is forwarded. No directory or SQL-object directory is present in this envelope; investigation planner payload unchanged.

### Business output (verbatim)

You asked: Inventory Health e1b8e1 Handled Quantity may be stale. Inspect the available refresh and processing history and explain whether freshness can be established. I have not supplied a freshness SLA.
Answer to your question: Not answered.
Regarding whether the reported information is current: No completed currency check establishes whether the reported information is current. Refresh history was unavailable to the diagnostic reader. Processing history was not assessed before the investigation stopped.
What was found instead:

The declared selections could not be tested with the available evidence. The report showed 8,765 for movements, matching the total used to prepare it. An earlier check of movements returned 7,661; the difference appears in the step that matches movements with rates. Several matching rates can cause an entry to contribute more than once. We have not confirmed the repeated matches, whether the checks describe the same moment, whether this matching rule is intended, or how movements were first entered. The two checks used different calculation engines. The checks read different data sources; different calculation engines were not established, so a shared calculation fault could affect both. Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.

### Technical output (verbatim)

You asked: Inventory Health e1b8e1 Handled Quantity may be stale. Inspect the available refresh and processing history and explain whether freshness can be established. I have not supplied a freshness SLA.
Answer to your question: Not answered.
Regarding whether the reported information is current: No completed currency check establishes whether the reported information is current. Refresh history was unavailable to the diagnostic reader. Processing history was not assessed before the investigation stopped.
What was found instead:

Measure: Handled Quantity.
B2 diverges: L2 (stock movements e1b8e1 in warehouse silver e1b8e1, upstream input) 7,661 -> L1 (movement values in warehouse gold e1b8e1, downstream output) 8,765.
B1 agrees: L1 (movement values in warehouse gold e1b8e1, upstream input) 8,765 -> L0 (Activity in Warehouse Operations e1b8e1, downstream output) 8,765.
ENGINE_INDEPENDENT: comparable quantity-bound engine self-reports differ; this is an engine-independent cross-surface comparison. (receipt boundary-1-comparison).
OBJECT_DISTINCT: comparable quantity-bound object self-reports differ; this verifies a data-path boundary, not engine-level independence. Shared computation faults are not excluded. (receipt boundary-2-comparison).
Declared-context reproduction unavailable: Declared-context reproduction is undeclared for question kind UNCLASSIFIED.

The checked chain shows the measure quantity matching the intermediate relation at one boundary, while the next checked boundary shows a different quantity between the lower relation and that intermediate relation. That pattern attributes the observed gap to logic applied between those checked layers rather than to a preserved value carried unchanged through the full checked chain.

Layers:
L0 - Activity in Warehouse Operations e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity
L1 - movement values in warehouse gold e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values
L2 - stock movements e1b8e1 in warehouse silver e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1
L3 - stock movements e1b8e1 in warehouse bronze e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1

Limits:
- Unattested connection on L0 (receipt b71a9b6b-3b57-400c-ae6a-a4e4d15da688).
- Unattested connection on L1 (receipt 0655aea2-4679-48e3-8e58-bf5f456fec80).
- Unattested connection on L2 (receipt 3fbfe069-50c0-4369-96c0-8fc32cccbd9f).
- SNAPSHOT_UNVERIFIED for B1, B2: the reads cannot be tied to matching data versions; agreement does not prove currency, and different update timing was not excluded as a cause of divergence.
- Checked through L2; stopped because reached.
- Unchecked L2 -> L3: Investigation terminated before this boundary.
- Unchecked L3 -> unresolved upstream: No declared upstream read for this quantity (literal initialization or derived/unsupported column).
- Quantities trace unchanged integral columns; joins may multiply rows and whole-row deduplication may remove them. Key uniqueness and intended grain are not established.
- This explains the difference only via join-driven row multiplication visible in the definition. It does not establish that duplicate matches actually occurred in the data.

Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.

## G — 542e6507-b7dc-4de3-8209-5713b98c12ac

Outcome TRANSFORMATION_LOGIC; synthesis COMPLETED. Intake subject SOURCE_CORRECTNESS; procedure subject absent. Envelope characters 1125 → 1249 when the existing subject is forwarded. No directory or SQL-object directory is present in this envelope; investigation planner payload unchanged.

### Business output (verbatim)

You asked: Inventory Health e1b8e1 Handled Quantity may include incorrect source entries. Inspect source stock movements and related inventory adjustments for evidence. Do not assume an adjustment record alone proves the intended business rule.
Answer to your question: Not answered.
Regarding business meaning and intended treatment: No authoritative business meaning or intended rule was established; a technical finding cannot supply it.
What was found instead:

The declared selections could not be tested with the available evidence. The report showed 8,765 for movements, matching the total used to prepare it. An earlier check of movements returned 7,661; the difference appears in the step that matches movements with rates. Several matching rates can cause an entry to contribute more than once. We have not confirmed the repeated matches, whether the checks describe the same moment, whether this matching rule is intended, or how movements were first entered. The two checks used different calculation engines. The checks read different data sources; different calculation engines were not established, so a shared calculation fault could affect both. Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.

### Technical output (verbatim)

You asked: Inventory Health e1b8e1 Handled Quantity may include incorrect source entries. Inspect source stock movements and related inventory adjustments for evidence. Do not assume an adjustment record alone proves the intended business rule.
Answer to your question: Not answered.
Regarding business meaning and intended treatment: No authoritative business meaning or intended rule was established; a technical finding cannot supply it.
What was found instead:

Measure: Handled Quantity.
B2 diverges: L2 (stock movements e1b8e1 in warehouse silver e1b8e1, upstream input) 7,661 -> L1 (movement values in warehouse gold e1b8e1, downstream output) 8,765.
B1 agrees: L1 (movement values in warehouse gold e1b8e1, upstream input) 8,765 -> L0 (Activity in Warehouse Operations e1b8e1, downstream output) 8,765.
ENGINE_INDEPENDENT: comparable quantity-bound engine self-reports differ; this is an engine-independent cross-surface comparison. (receipt boundary-1-comparison).
OBJECT_DISTINCT: comparable quantity-bound object self-reports differ; this verifies a data-path boundary, not engine-level independence. Shared computation faults are not excluded. (receipt boundary-2-comparison).
Declared-context reproduction unavailable: Declared-context reproduction is undeclared for question kind UNCLASSIFIED.

The measure takes its traced quantity from movement_values without changing that quantity across the checked boundary. The checked read from stock movements into movement_values shows a larger carried quantity at the later layer, which is consistent with logic in that definition that can duplicate rows through joins while preserving the integral quantity values on each row. Once present in movement_values, that carried quantity passes through unchanged into the measure.

Layers:
L0 - Activity in Warehouse Operations e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity
L1 - movement values in warehouse gold e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values
L2 - stock movements e1b8e1 in warehouse silver e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1
L3 - stock movements e1b8e1 in warehouse bronze e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1

Limits:
- Unattested connection on L0 (receipt 5a271cc1-a733-4f99-aaa1-18e7a6968c11).
- Unattested connection on L1 (receipt 433e1963-e59f-4db1-9739-7861c70ae8f2).
- Unattested connection on L2 (receipt 35d43dac-5032-4539-815d-a7fd594749c4).
- SNAPSHOT_UNVERIFIED for B1, B2: the reads cannot be tied to matching data versions; agreement does not prove currency, and different update timing was not excluded as a cause of divergence.
- Checked through L2; stopped because reached.
- Unchecked L2 -> L3: Investigation terminated before this boundary.
- Unchecked L3 -> unresolved upstream: No declared upstream read for this quantity (literal initialization or derived/unsupported column).
- Quantities trace unchanged integral columns; joins may multiply rows and whole-row deduplication may remove them. Key uniqueness and intended grain are not established.
- This explains the difference only as a join-multiplicity mechanism visible in the definition. The payload does not establish that duplicate matches actually occurred for these data.

Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.
