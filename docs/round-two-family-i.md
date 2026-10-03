# Round two: original family I repeat

2026-10-03. Part A4, KNOWN_DOMAIN_REGRESSION. Engine fixed for this measurement at merged #338; no formal acceptance freeze or unfamiliar domain. One attempt; original A7 failures are unchanged. No replacement, limit increase, credits, permission or fixture change.

Starting rolling window: 155/300, 145 available. Diagnostic cap twelve; no budget, credit or fixture change.

| Family | Session | Outcome | Diagnostics / physical / guards | Intake / exploration / judge / synthesis | Synthesis | Outputs |
|---|---|---|---|---|---|---|
| I | 39b84dd1-5227-4db2-88c6-0b4bca19f51b | TRANSFORMATION_LOGIC | 4 / 10 / 6 | 1 / 0 / 1 / 1 | COMPLETED | GENERATED / GENERATED |

Totals: {'physical_requests': 10, 'diagnostic_reads': 4, 'guard_requests': 6, 'intake_calls': 1, 'investigation_planner_calls': 0, 'judge_calls': 1, 'synthesis_calls': 1}.

Ending rolling window: 165/300; available 135. Part A cumulative physical requests: 10.

Procedure and synthesis completion do not establish that the original source entries or intended business rule are correct. Snapshot alignment remains unverified. No new outcome taxonomy or ratio/filtered-lower capability was introduced.

## I

Ticket unchanged: For Inventory Health e1b8e1 Handled Quantity, what does adjustment reason Q49 mean, and should those adjustments affect this metric?

Intake shape / comparison mode / subject: BUSINESS_QUESTION / NONE / BUSINESS_MEANING

Status / stop: COMPLETED / ENOUGH_DIAGNOSTICS

Reads: 1 DAX, 8 SQL including 6 guards, 1 endpoint metadata. Diagnostics 4/12; phase counts {'REPRODUCTION': 0, 'WALK': 4}. All physical requests remain charged.

### Every original quantity probe

- Receipt c042fdb7-251f-45f4-8c2b-4599abeba608; {'connection': '149f8d99-1c66-4a0a-9624-759be002bb60', 'engine': 'OLAP Server', 'identity': 'investigator-reader@skynwhy.com', 'object': '3484a2bc-98c5-4cef-be5c-a6215484075e'}; self-report {'engine': 'OLAP Server', 'identity': 'investigator-reader@skynwhy.com', 'object': '3484a2bc-98c5-4cef-be5c-a6215484075e'}; attestation {'attested_fields': ['engine', 'identity', 'object'], 'consistency': 'MATCHED', 'contradictions': [], 'coverage': 'PARTIAL', 'field_states': {'connection': 'UNATTESTED', 'engine': 'ATTESTED', 'identity': 'ATTESTED', 'object': 'ATTESTED'}, 'missing_required_fields': [], 'reason': None, 'required_fields': ['engine', 'identity', 'object'], 'status': 'PARTIAL', 'unattested_fields': ['connection']}; result [{'[baseline]': {'type': 'decimal', 'value': '8765'}}].
- Receipt 85350bb2-e18a-43a6-80d4-96a027a21694; {'connection': 'sql://i4iptx6c5nlundn6llzsrvlxqa-tggz6fdgdqfevfreown6aav3ma.datawarehouse.fabric.microsoft.com', 'engine': 'Microsoft Azure SQL Data Warehouse', 'identity': 'investigator-reader@skynwhy.com', 'object': 'warehouse_gold_e1b8e1'}; self-report {'engine': 'Microsoft Azure SQL Data Warehouse', 'identity': 'investigator-reader@skynwhy.com', 'object': 'warehouse_gold_e1b8e1'}; attestation {'attested_fields': ['engine', 'identity', 'object'], 'consistency': 'MATCHED', 'contradictions': [], 'coverage': 'PARTIAL', 'field_states': {'connection': 'UNATTESTED', 'engine': 'ATTESTED', 'identity': 'ATTESTED', 'object': 'ATTESTED'}, 'missing_required_fields': [], 'reason': None, 'required_fields': ['engine', 'identity', 'object'], 'status': 'PARTIAL', 'unattested_fields': ['connection']}; result [{'quantity': {'type': 'decimal', 'value': '8765'}}].
- Comparison boundary-1-comparison: {'upper_layer': 'fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity', 'lower_layer': 'fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values', 'comparison_status': 'CROSS_SURFACE_VERIFIED', 'values_equal': True, 'surface_difference': {'differing_field': 'engine', 'grade': 'ENGINE_INDEPENDENT', 'lower_value': 'Microsoft Azure SQL Data Warehouse', 'reason': None, 'self_report_kind': 'ENGINE_PRODUCT', 'upper_value': 'OLAP Server'}, 'snapshot_attestation': {'lower': None, 'reason': 'QUERY_BOUND_VERSION_MISSING', 'status': 'SNAPSHOT_UNVERIFIED', 'unverified_sides': ['upper', 'lower'], 'upper': None, 'version': 1}, 'reason': None}
- Receipt 4f624fdd-84d5-491f-bc10-1df21678f57c; {'connection': 'sql://i4iptx6c5nlundn6llzsrvlxqa-tggz6fdgdqfevfreown6aav3ma.datawarehouse.fabric.microsoft.com', 'engine': 'Microsoft Azure SQL Data Warehouse', 'identity': 'investigator-reader@skynwhy.com', 'object': 'warehouse_silver_e1b8e1'}; self-report {'engine': 'Microsoft Azure SQL Data Warehouse', 'identity': 'investigator-reader@skynwhy.com', 'object': 'warehouse_silver_e1b8e1'}; attestation {'attested_fields': ['engine', 'identity', 'object'], 'consistency': 'MATCHED', 'contradictions': [], 'coverage': 'PARTIAL', 'field_states': {'connection': 'UNATTESTED', 'engine': 'ATTESTED', 'identity': 'ATTESTED', 'object': 'ATTESTED'}, 'missing_required_fields': [], 'reason': None, 'required_fields': ['engine', 'identity', 'object'], 'status': 'PARTIAL', 'unattested_fields': ['connection']}; result [{'quantity': {'type': 'decimal', 'value': '7661'}}].
- Comparison boundary-2-comparison: {'upper_layer': 'fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values', 'lower_layer': 'fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1', 'comparison_status': 'CROSS_SURFACE_VERIFIED', 'values_equal': False, 'surface_difference': {'differing_field': 'object', 'grade': 'OBJECT_DISTINCT', 'lower_value': 'warehouse_silver_e1b8e1', 'reason': None, 'self_report_kind': 'DATABASE_CATALOG_NAME', 'upper_value': 'warehouse_gold_e1b8e1'}, 'snapshot_attestation': {'lower': None, 'reason': 'QUERY_BOUND_VERSION_MISSING', 'status': 'SNAPSHOT_UNVERIFIED', 'unverified_sides': ['upper', 'lower'], 'upper': None, 'version': 1}, 'reason': None}

Unchecked boundaries: [{'lower_layer': 'fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1', 'reason': 'Investigation terminated before this boundary', 'upper_layer': 'fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1'}, {'lower_layer': 'unresolved upstream', 'reason': 'No declared upstream read for this quantity (literal initialization or derived/unsupported column)', 'upper_layer': 'fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1'}]

Skipped capabilities: [{'capability': 'presentation_freshness', 'reason': 'Refresh timestamps are unavailable to the diagnostic reader: REST requires dataset Write and XMLA requires administrator; both were tested and refused.', 'step': 1}]

All claim limits: ['Checked through fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1; stopped because reached.', 'Unattested surface field connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity: the surface did not report it.', 'Unattested surface field connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values: the surface did not report it.', 'Unattested surface field connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1: the surface did not report it.', 'Comparison 1: SNAPSHOT_UNVERIFIED; the upper and lower served data version is not attested to its quantity read; agreement does not establish that either value is current.', 'Comparison 2: SNAPSHOT_UNVERIFIED; the upper and lower served data version is not attested to its quantity read; different update timing was not excluded as a cause of the difference.', 'Unchecked fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1 -> fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1: Investigation terminated before this boundary.', 'Unchecked fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1 -> unresolved upstream: No declared upstream read for this quantity (literal initialization or derived/unsupported column).', 'Quantities trace unchanged integral columns; joins may multiply rows and whole-row deduplication may remove them. Key uniqueness and intended grain are not established.', 'This only shows a concrete mechanism that can create the difference. It does not establish that duplicate matches actually occurred for these data or that both sides use the same snapshot.']

Synthesis validation / error: COMPLETED / None

### business_output

```text
You asked: For Inventory Health e1b8e1 Handled Quantity, what does adjustment reason Q49 mean, and should those adjustments affect this metric?
Answer to your question: Not answered.
Regarding business meaning and intended treatment: No authoritative business meaning or intended rule was established; a technical finding cannot supply it.
What was found instead:

The report showed 8,765 for movements, matching the total used to prepare it. The table it is built from contained 7,661 for movements; the difference appears in the step that matches movements with rates. Several matching rates can cause an entry to contribute more than once. We have not confirmed the repeated matches, whether the checks describe the same moment, whether this matching rule is intended, or how movements were first entered. For the report and the table used to prepare it, the two checks used different calculation engines. For the table used to prepare the report and the table it is built from, the checks read different data sources; different calculation engines were not established, so a shared calculation fault could affect both. Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.
```

### technical_output

```text
You asked: For Inventory Health e1b8e1 Handled Quantity, what does adjustment reason Q49 mean, and should those adjustments affect this metric?
Answer to your question: Not answered.
Regarding business meaning and intended treatment: No authoritative business meaning or intended rule was established; a technical finding cannot supply it.
What was found instead:

Measure: Handled Quantity.
B2 diverges: L2 (stock movements e1b8e1 in warehouse silver e1b8e1, upstream input) 7,661 -> L1 (movement values in warehouse gold e1b8e1, downstream output) 8,765.
B1 agrees: L1 (movement values in warehouse gold e1b8e1, upstream input) 8,765 -> L0 (Activity in Warehouse Operations e1b8e1, downstream output) 8,765.
ENGINE_INDEPENDENT: comparable quantity-bound engine self-reports differ; this is an engine-independent cross-surface comparison. (receipt boundary-1-comparison).
OBJECT_DISTINCT: comparable quantity-bound object self-reports differ; this verifies a data-path boundary, not engine-level independence. Shared computation faults are not excluded. (receipt boundary-2-comparison).
Declared-context reproduction unavailable: Declared-context reproduction is undeclared for question kind BUSINESS_MEANING.

The recorded logic takes movement rows and left joins rate rows by product. The definition notes that matching rows may multiply because uniqueness is not assumed. It also derives a value column from units and unit cost while the tracked quantity remains the unchanged additive units column. When a movement row matches several rate rows, that movement row can appear repeatedly after the join, and the repeated units can raise the handled quantity total carried into the next layer.

Layers:
L0 - Activity in Warehouse Operations e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity
L1 - movement values in warehouse gold e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values
L2 - stock movements e1b8e1 in warehouse silver e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1
L3 - stock movements e1b8e1 in warehouse bronze e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1

Limits:
- Unattested connection on L0 (receipt c042fdb7-251f-45f4-8c2b-4599abeba608).
- Unattested connection on L1 (receipt 85350bb2-e18a-43a6-80d4-96a027a21694).
- Unattested connection on L2 (receipt 4f624fdd-84d5-491f-bc10-1df21678f57c).
- SNAPSHOT_UNVERIFIED for B1, B2: the reads cannot be tied to matching data versions; agreement does not prove currency, and different update timing was not excluded as a cause of divergence.
- Checked through L2; stopped because reached.
- Unchecked L2 -> L3: Investigation terminated before this boundary.
- Unchecked L3 -> unresolved upstream: No declared upstream read for this quantity (literal initialization or derived/unsupported column).
- Quantities trace unchanged integral columns; joins may multiply rows and whole-row deduplication may remove them. Key uniqueness and intended grain are not established.
- This only shows a concrete mechanism that can create the difference. It does not establish that duplicate matches actually occurred for these data.

Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.
```

Validation record: the initial full local run exercised 1,667 tests with one failure in the old capitalized standalone-grade assertion. The updated 13-test grading module passed, as did all six CI checks on #338?s final head. No runtime failure was suppressed.
