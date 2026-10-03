# Mechanism evidence: two unchanged-ticket repeats

2026-10-03. Part B, KNOWN_DOMAIN_REGRESSION. Engine frozen for this measurement at the merged #336 commit; no formal acceptance freeze or unfamiliar domain. One attempt each; original A7 failures are unchanged. No replacement, limit increase, credits, permission or fixture change.

Starting rolling window: 135/300, 165 available. Diagnostic cap twelve. Part B evaluator refuses before the 151st physical reservation; its accounting is independent of the rolling allowance.

| Family | Session | Outcome | Diagnostics / physical / guards | Intake / exploration / judge / synthesis | Synthesis | Outputs |
|---|---|---|---|---|---|---|
| G | 6640a85f-c54e-4aef-a2a5-96df6194d2d0 | TRANSFORMATION_LOGIC | 4 / 10 / 6 | 1 / 0 / 1 / 1 | COMPLETED | GENERATED / GENERATED |
| A | a9466911-69be-4252-96f2-0afb84b4f468 | TRANSFORMATION_LOGIC | 4 / 10 / 6 | 1 / 0 / 1 / 1 | COMPLETED | GENERATED / GENERATED |

Totals: {'physical_requests': 20, 'diagnostic_reads': 8, 'guard_requests': 12, 'intake_calls': 2, 'investigation_planner_calls': 0, 'judge_calls': 2, 'synthesis_calls': 2}.

Ending rolling window: 155/300; available 145. Part B cumulative physical requests: 20/150.

Procedure and synthesis completion do not establish that the original source entries or intended business rule are correct. Snapshot alignment remains unverified. No new outcome taxonomy or ratio/filtered-lower capability was introduced.

## G

Ticket unchanged: Inventory Health e1b8e1 Handled Quantity may include incorrect source entries. Inspect source stock movements and related inventory adjustments for evidence. Do not assume an adjustment record alone proves the intended business rule.

Intake shape / comparison mode / subject: BUSINESS_QUESTION / NONE / SOURCE_CORRECTNESS

Status / stop: COMPLETED / ENOUGH_DIAGNOSTICS

Reads: 1 DAX, 8 SQL including 6 guards, 1 endpoint metadata. Diagnostics 4/12; phase counts {'REPRODUCTION': 0, 'WALK': 4}. All physical requests remain charged.

### Every original quantity probe

- Receipt a2ea7940-e0a6-4b12-94e0-9464a20ed28d; {'connection': '149f8d99-1c66-4a0a-9624-759be002bb60', 'engine': 'OLAP Server', 'identity': 'investigator-reader@skynwhy.com', 'object': '3484a2bc-98c5-4cef-be5c-a6215484075e'}; self-report {'engine': 'OLAP Server', 'identity': 'investigator-reader@skynwhy.com', 'object': '3484a2bc-98c5-4cef-be5c-a6215484075e'}; attestation {'attested_fields': ['engine', 'identity', 'object'], 'consistency': 'MATCHED', 'contradictions': [], 'coverage': 'PARTIAL', 'field_states': {'connection': 'UNATTESTED', 'engine': 'ATTESTED', 'identity': 'ATTESTED', 'object': 'ATTESTED'}, 'missing_required_fields': [], 'reason': None, 'required_fields': ['engine', 'identity', 'object'], 'status': 'PARTIAL', 'unattested_fields': ['connection']}; result [{'[baseline]': {'type': 'decimal', 'value': '8765'}}].
- Receipt 8067739f-0d52-47e7-bbf9-09373b92ed1e; {'connection': 'sql://i4iptx6c5nlundn6llzsrvlxqa-tggz6fdgdqfevfreown6aav3ma.datawarehouse.fabric.microsoft.com', 'engine': 'Microsoft Azure SQL Data Warehouse', 'identity': 'investigator-reader@skynwhy.com', 'object': 'warehouse_gold_e1b8e1'}; self-report {'engine': 'Microsoft Azure SQL Data Warehouse', 'identity': 'investigator-reader@skynwhy.com', 'object': 'warehouse_gold_e1b8e1'}; attestation {'attested_fields': ['engine', 'identity', 'object'], 'consistency': 'MATCHED', 'contradictions': [], 'coverage': 'PARTIAL', 'field_states': {'connection': 'UNATTESTED', 'engine': 'ATTESTED', 'identity': 'ATTESTED', 'object': 'ATTESTED'}, 'missing_required_fields': [], 'reason': None, 'required_fields': ['engine', 'identity', 'object'], 'status': 'PARTIAL', 'unattested_fields': ['connection']}; result [{'quantity': {'type': 'decimal', 'value': '8765'}}].
- Comparison boundary-1-comparison: {'upper_layer': 'fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity', 'lower_layer': 'fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values', 'comparison_status': 'CROSS_SURFACE_VERIFIED', 'values_equal': True, 'surface_difference': {'differing_field': 'engine', 'grade': 'ENGINE_INDEPENDENT', 'lower_value': 'Microsoft Azure SQL Data Warehouse', 'reason': None, 'self_report_kind': 'ENGINE_PRODUCT', 'upper_value': 'OLAP Server'}, 'snapshot_attestation': {'lower': None, 'reason': 'QUERY_BOUND_VERSION_MISSING', 'status': 'SNAPSHOT_UNVERIFIED', 'unverified_sides': ['upper', 'lower'], 'upper': None, 'version': 1}, 'reason': None}
- Receipt 4f08f812-3d30-4a8a-ac60-65d1fa5680fe; {'connection': 'sql://i4iptx6c5nlundn6llzsrvlxqa-tggz6fdgdqfevfreown6aav3ma.datawarehouse.fabric.microsoft.com', 'engine': 'Microsoft Azure SQL Data Warehouse', 'identity': 'investigator-reader@skynwhy.com', 'object': 'warehouse_silver_e1b8e1'}; self-report {'engine': 'Microsoft Azure SQL Data Warehouse', 'identity': 'investigator-reader@skynwhy.com', 'object': 'warehouse_silver_e1b8e1'}; attestation {'attested_fields': ['engine', 'identity', 'object'], 'consistency': 'MATCHED', 'contradictions': [], 'coverage': 'PARTIAL', 'field_states': {'connection': 'UNATTESTED', 'engine': 'ATTESTED', 'identity': 'ATTESTED', 'object': 'ATTESTED'}, 'missing_required_fields': [], 'reason': None, 'required_fields': ['engine', 'identity', 'object'], 'status': 'PARTIAL', 'unattested_fields': ['connection']}; result [{'quantity': {'type': 'decimal', 'value': '7661'}}].
- Comparison boundary-2-comparison: {'upper_layer': 'fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values', 'lower_layer': 'fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1', 'comparison_status': 'CROSS_SURFACE_VERIFIED', 'values_equal': False, 'surface_difference': {'differing_field': 'object', 'grade': 'OBJECT_DISTINCT', 'lower_value': 'warehouse_silver_e1b8e1', 'reason': None, 'self_report_kind': 'DATABASE_CATALOG_NAME', 'upper_value': 'warehouse_gold_e1b8e1'}, 'snapshot_attestation': {'lower': None, 'reason': 'QUERY_BOUND_VERSION_MISSING', 'status': 'SNAPSHOT_UNVERIFIED', 'unverified_sides': ['upper', 'lower'], 'upper': None, 'version': 1}, 'reason': None}

Unchecked boundaries: [{'lower_layer': 'fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1', 'reason': 'Investigation terminated before this boundary', 'upper_layer': 'fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1'}, {'lower_layer': 'unresolved upstream', 'reason': 'No declared upstream read for this quantity (literal initialization or derived/unsupported column)', 'upper_layer': 'fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1'}]

Skipped capabilities: [{'capability': 'presentation_freshness', 'reason': 'Refresh timestamps are unavailable to the diagnostic reader: REST requires dataset Write and XMLA requires administrator; both were tested and refused.', 'step': 1}]

All claim limits: ['Checked through fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1; stopped because reached.', 'Unattested surface field connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity: the surface did not report it.', 'Unattested surface field connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values: the surface did not report it.', 'Unattested surface field connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1: the surface did not report it.', 'Comparison 1: SNAPSHOT_UNVERIFIED; the upper and lower served data version is not attested to its quantity read; agreement does not establish that either value is current.', 'Comparison 2: SNAPSHOT_UNVERIFIED; the upper and lower served data version is not attested to its quantity read; different update timing was not excluded as a cause of the difference.', 'Unchecked fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1 -> fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1: Investigation terminated before this boundary.', 'Unchecked fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1 -> unresolved upstream: No declared upstream read for this quantity (literal initialization or derived/unsupported column).', 'Quantities trace unchanged integral columns; joins may multiply rows and whole-row deduplication may remove them. Key uniqueness and intended grain are not established.', 'The definition shows a mechanism that can change the total, but it does not establish the actual match counts, key uniqueness, or a shared snapshot, so it cannot prove that this join produced exactly the observed difference.']

Synthesis validation / error: COMPLETED / None

### business_output

```text
You asked: Inventory Health e1b8e1 Handled Quantity may include incorrect source entries. Inspect source stock movements and related inventory adjustments for evidence. Do not assume an adjustment record alone proves the intended business rule.
Answer to your question: Not answered.
Regarding business meaning and intended treatment: No authoritative business meaning or intended rule was established; a technical finding cannot supply it.
What was found instead:

The declared selections could not be tested with the available evidence. The report showed 8,765 for movements, matching the total used to prepare it. An earlier check of movements returned 7,661; the difference appears in the step that matches movements with rates. Several matching rates can cause an entry to contribute more than once. We have not confirmed the repeated matches, whether the checks describe the same moment, whether this matching rule is intended, or how movements were first entered. The two checks used different calculation engines. The checks read different data sources; different calculation engines were not established, so a shared calculation fault could affect both. Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.
```

### technical_output

```text
You asked: Inventory Health e1b8e1 Handled Quantity may include incorrect source entries. Inspect source stock movements and related inventory adjustments for evidence. Do not assume an adjustment record alone proves the intended business rule.
Answer to your question: Not answered.
Regarding business meaning and intended treatment: No authoritative business meaning or intended rule was established; a technical finding cannot supply it.
What was found instead:

Measure: Handled Quantity.
B2 diverges: L2 (stock movements e1b8e1 in warehouse silver e1b8e1, upstream input) 7,661 -> L1 (movement values in warehouse gold e1b8e1, downstream output) 8,765.
B1 agrees: L1 (movement values in warehouse gold e1b8e1, upstream input) 8,765 -> L0 (Activity in Warehouse Operations e1b8e1, downstream output) 8,765.
ENGINE_INDEPENDENT: comparable quantity-bound engine self-reports differ; this is an engine-independent cross-surface comparison. (receipt boundary-1-comparison).
OBJECT_DISTINCT: comparable quantity-bound object self-reports differ; this verifies a data-path boundary, not engine-level independence. Shared computation faults are not excluded. (receipt boundary-2-comparison).
Declared-context reproduction unavailable: Declared-context reproduction is undeclared for question kind SOURCE_CORRECTNESS.

A left join matches stock movement rows with rate rows by product key before a derived value column is created. The retained definition states that matching rows may multiply when that key is not unique, so movement rows can be repeated and the additive quantity can increase between the stock movement table and the later table.

Layers:
L0 - Activity in Warehouse Operations e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity
L1 - movement values in warehouse gold e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values
L2 - stock movements e1b8e1 in warehouse silver e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1
L3 - stock movements e1b8e1 in warehouse bronze e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1

Limits:
- Unattested connection on L0 (receipt a2ea7940-e0a6-4b12-94e0-9464a20ed28d).
- Unattested connection on L1 (receipt 8067739f-0d52-47e7-bbf9-09373b92ed1e).
- Unattested connection on L2 (receipt 4f08f812-3d30-4a8a-ac60-65d1fa5680fe).
- SNAPSHOT_UNVERIFIED for B1, B2: the reads cannot be tied to matching data versions; agreement does not prove currency, and different update timing was not excluded as a cause of divergence.
- Checked through L2; stopped because reached.
- Unchecked L2 -> L3: Investigation terminated before this boundary.
- Unchecked L3 -> unresolved upstream: No declared upstream read for this quantity (literal initialization or derived/unsupported column).
- Quantities trace unchanged integral columns; joins may multiply rows and whole-row deduplication may remove them. Key uniqueness and intended grain are not established.
- The definition shows a mechanism that can change the total, but it does not establish the actual match counts, key uniqueness, or a shared snapshot, so it cannot prove that this join produced exactly the observed difference.

Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.
```

## A

Ticket unchanged: In Inventory Health e1b8e1, Handled Quantity appears higher than the source stock movements total. Investigate the current global value and explain any observed difference.

Intake shape / comparison mode / subject: MISMATCH_COMPLAINT / VERTICAL / FIGURE_DIFFERENCE

Status / stop: COMPLETED / ENOUGH_DIAGNOSTICS

Reads: 1 DAX, 8 SQL including 6 guards, 1 endpoint metadata. Diagnostics 4/12; phase counts {'REPRODUCTION': 0, 'WALK': 4}. All physical requests remain charged.

### Every original quantity probe

- Receipt d15e128c-2740-48c6-ab11-623fc4f68cf7; {'connection': '149f8d99-1c66-4a0a-9624-759be002bb60', 'engine': 'OLAP Server', 'identity': 'investigator-reader@skynwhy.com', 'object': '3484a2bc-98c5-4cef-be5c-a6215484075e'}; self-report {'engine': 'OLAP Server', 'identity': 'investigator-reader@skynwhy.com', 'object': '3484a2bc-98c5-4cef-be5c-a6215484075e'}; attestation {'attested_fields': ['engine', 'identity', 'object'], 'consistency': 'MATCHED', 'contradictions': [], 'coverage': 'PARTIAL', 'field_states': {'connection': 'UNATTESTED', 'engine': 'ATTESTED', 'identity': 'ATTESTED', 'object': 'ATTESTED'}, 'missing_required_fields': [], 'reason': None, 'required_fields': ['engine', 'identity', 'object'], 'status': 'PARTIAL', 'unattested_fields': ['connection']}; result [{'[baseline]': {'type': 'decimal', 'value': '8765'}}].
- Receipt d3ab2166-4f65-48e4-a0c0-009b2eeb602c; {'connection': 'sql://i4iptx6c5nlundn6llzsrvlxqa-tggz6fdgdqfevfreown6aav3ma.datawarehouse.fabric.microsoft.com', 'engine': 'Microsoft Azure SQL Data Warehouse', 'identity': 'investigator-reader@skynwhy.com', 'object': 'warehouse_gold_e1b8e1'}; self-report {'engine': 'Microsoft Azure SQL Data Warehouse', 'identity': 'investigator-reader@skynwhy.com', 'object': 'warehouse_gold_e1b8e1'}; attestation {'attested_fields': ['engine', 'identity', 'object'], 'consistency': 'MATCHED', 'contradictions': [], 'coverage': 'PARTIAL', 'field_states': {'connection': 'UNATTESTED', 'engine': 'ATTESTED', 'identity': 'ATTESTED', 'object': 'ATTESTED'}, 'missing_required_fields': [], 'reason': None, 'required_fields': ['engine', 'identity', 'object'], 'status': 'PARTIAL', 'unattested_fields': ['connection']}; result [{'quantity': {'type': 'decimal', 'value': '8765'}}].
- Comparison boundary-1-comparison: {'upper_layer': 'fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity', 'lower_layer': 'fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values', 'comparison_status': 'CROSS_SURFACE_VERIFIED', 'values_equal': True, 'surface_difference': {'differing_field': 'engine', 'grade': 'ENGINE_INDEPENDENT', 'lower_value': 'Microsoft Azure SQL Data Warehouse', 'reason': None, 'self_report_kind': 'ENGINE_PRODUCT', 'upper_value': 'OLAP Server'}, 'snapshot_attestation': {'lower': None, 'reason': 'QUERY_BOUND_VERSION_MISSING', 'status': 'SNAPSHOT_UNVERIFIED', 'unverified_sides': ['upper', 'lower'], 'upper': None, 'version': 1}, 'reason': None}
- Receipt 1acbf451-6b66-4112-89c0-7a54d76eb7e4; {'connection': 'sql://i4iptx6c5nlundn6llzsrvlxqa-tggz6fdgdqfevfreown6aav3ma.datawarehouse.fabric.microsoft.com', 'engine': 'Microsoft Azure SQL Data Warehouse', 'identity': 'investigator-reader@skynwhy.com', 'object': 'warehouse_silver_e1b8e1'}; self-report {'engine': 'Microsoft Azure SQL Data Warehouse', 'identity': 'investigator-reader@skynwhy.com', 'object': 'warehouse_silver_e1b8e1'}; attestation {'attested_fields': ['engine', 'identity', 'object'], 'consistency': 'MATCHED', 'contradictions': [], 'coverage': 'PARTIAL', 'field_states': {'connection': 'UNATTESTED', 'engine': 'ATTESTED', 'identity': 'ATTESTED', 'object': 'ATTESTED'}, 'missing_required_fields': [], 'reason': None, 'required_fields': ['engine', 'identity', 'object'], 'status': 'PARTIAL', 'unattested_fields': ['connection']}; result [{'quantity': {'type': 'decimal', 'value': '7661'}}].
- Comparison boundary-2-comparison: {'upper_layer': 'fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values', 'lower_layer': 'fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1', 'comparison_status': 'CROSS_SURFACE_VERIFIED', 'values_equal': False, 'surface_difference': {'differing_field': 'object', 'grade': 'OBJECT_DISTINCT', 'lower_value': 'warehouse_silver_e1b8e1', 'reason': None, 'self_report_kind': 'DATABASE_CATALOG_NAME', 'upper_value': 'warehouse_gold_e1b8e1'}, 'snapshot_attestation': {'lower': None, 'reason': 'QUERY_BOUND_VERSION_MISSING', 'status': 'SNAPSHOT_UNVERIFIED', 'unverified_sides': ['upper', 'lower'], 'upper': None, 'version': 1}, 'reason': None}

Unchecked boundaries: [{'lower_layer': 'fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1', 'reason': 'Investigation terminated before this boundary', 'upper_layer': 'fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1'}, {'lower_layer': 'unresolved upstream', 'reason': 'No declared upstream read for this quantity (literal initialization or derived/unsupported column)', 'upper_layer': 'fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1'}]

Skipped capabilities: [{'capability': 'presentation_freshness', 'reason': 'Refresh timestamps are unavailable to the diagnostic reader: REST requires dataset Write and XMLA requires administrator; both were tested and refused.', 'step': 1}]

All claim limits: ['Checked through fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1; stopped because reached.', 'Unattested surface field connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity: the surface did not report it.', 'Unattested surface field connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values: the surface did not report it.', 'Unattested surface field connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1: the surface did not report it.', 'Comparison 1: SNAPSHOT_UNVERIFIED; the upper and lower served data version is not attested to its quantity read; agreement does not establish that either value is current.', 'Comparison 2: SNAPSHOT_UNVERIFIED; the upper and lower served data version is not attested to its quantity read; different update timing was not excluded as a cause of the difference.', 'Unchecked fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1 -> fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1: Investigation terminated before this boundary.', 'Unchecked fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1 -> unresolved upstream: No declared upstream read for this quantity (literal initialization or derived/unsupported column).', 'Quantities trace unchanged integral columns; joins may multiply rows and whole-row deduplication may remove them. Key uniqueness and intended grain are not established.', 'The definition shows a mechanism that can cause the increase, but it does not establish that duplicate matches actually occurred for this run or that both sides use the same snapshot.']

Synthesis validation / error: COMPLETED / None

### business_output

```text
You asked: In Inventory Health e1b8e1, Handled Quantity appears higher than the source stock movements total. Investigate the current global value and explain any observed difference.
Answer to your question: Partly answered.
Regarding the requested comparison: Independent quantities were compared, but unchecked scope or evidence limits prevent a complete answer.
What the investigation established:

The declared selections could not be tested with the available evidence. The report showed 8,765 for movements, matching the total used to prepare it. An earlier check of movements returned 7,661; the difference appears in the step that matches movements with rates. Several matching rates can cause an entry to contribute more than once. We have not confirmed the repeated matches, whether the checks describe the same moment, whether this matching rule is intended, or how movements were first entered. The two checks used different calculation engines. The checks read different data sources; different calculation engines were not established, so a shared calculation fault could affect both. Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.
```

### technical_output

```text
You asked: In Inventory Health e1b8e1, Handled Quantity appears higher than the source stock movements total. Investigate the current global value and explain any observed difference.
Answer to your question: Partly answered.
Regarding the requested comparison: Independent quantities were compared, but unchecked scope or evidence limits prevent a complete answer.
What the investigation established:

Measure: Handled Quantity.
B2 diverges: L2 (stock movements e1b8e1 in warehouse silver e1b8e1, upstream input) 7,661 -> L1 (movement values in warehouse gold e1b8e1, downstream output) 8,765.
B1 agrees: L1 (movement values in warehouse gold e1b8e1, upstream input) 8,765 -> L0 (Activity in Warehouse Operations e1b8e1, downstream output) 8,765.
ENGINE_INDEPENDENT: comparable quantity-bound engine self-reports differ; this is an engine-independent cross-surface comparison. (receipt boundary-1-comparison).
OBJECT_DISTINCT: comparable quantity-bound object self-reports differ; this verifies a data-path boundary, not engine-level independence. Shared computation faults are not excluded. (receipt boundary-2-comparison).
Declared-context reproduction unavailable: Declared-context reproduction is undeclared for question kind FIGURE_DIFFERENCE.

Handled Quantity is carried from units while movement value is created after movements are left joined with rates on product_id. The retained definition states that matching rows may multiply because key uniqueness is not assumed, so a movement row can be repeated in movement_values and the additive quantity can rise there while remaining unchanged from movement_values into Activity.

Layers:
L0 - Activity in Warehouse Operations e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity
L1 - movement values in warehouse gold e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values
L2 - stock movements e1b8e1 in warehouse silver e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1
L3 - stock movements e1b8e1 in warehouse bronze e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1

Limits:
- Unattested connection on L0 (receipt d15e128c-2740-48c6-ab11-623fc4f68cf7).
- Unattested connection on L1 (receipt d3ab2166-4f65-48e4-a0c0-009b2eeb602c).
- Unattested connection on L2 (receipt 1acbf451-6b66-4112-89c0-7a54d76eb7e4).
- SNAPSHOT_UNVERIFIED for B1, B2: the reads cannot be tied to matching data versions; agreement does not prove currency, and different update timing was not excluded as a cause of divergence.
- Checked through L2; stopped because reached.
- Unchecked L2 -> L3: Investigation terminated before this boundary.
- Unchecked L3 -> unresolved upstream: No declared upstream read for this quantity (literal initialization or derived/unsupported column).
- Quantities trace unchanged integral columns; joins may multiply rows and whole-row deduplication may remove them. Key uniqueness and intended grain are not established.
- The definition shows a mechanism that can cause the increase, but it does not establish that duplicate matches actually occurred for this run.

Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.
```
