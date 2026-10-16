# First completed live agent fixture attempt

2026-10-11 UTC. Original family A, integration attempt A7; not a paired scoring slot.

Ticket `0e1bf971-d36a-414d-87a1-3e1d8c097592`; session `37272838-7954-4a6f-a42e-c2c8f58158ef`. Agent and synthesis completed with TRANSFORMATION_LOGIC. Fifteen model calls (thirteen decisions, one definition judge and one synthesis), 527,736 input characters, USD0.576608, elapsed792.516s. Twelve physical requests; six diagnostic operations, cap12 unchanged. Pot2001 ->2013/2500, restoration95 protected, rolling859 ->871/3000.

The target was fixed by the submitted form. Reproduction was unavailable because no reported figure was supplied; retained within-layer reads do not create a reproduction verdict. The application tool returned UNDECLARED. Two comparisons: model/declared-input equal8765, ENGINE_INDEPENDENT; refined/input7661 vs serving/output8765, OBJECT_DISTINCT. Both SNAPSHOT_UNVERIFIED. No application read or source-consistency claim.

Root review: outcome matches, full contract does not. Role labels were lost between the resolved path and agent support. The output applies the global NO_LINEAGE stopping reason at L2 even though the resolved L2-to-L3 boundary was not checked. These are retained output defects; neither original output nor tape was rewritten. No general hard-zero, repeat-stability or agent-default gate is earned.

## Full step transcript

### STARTED

receipt_id: agent-progress:d2556a34d2acfb84e2d4260abc5da50e22ca199f727263b4422a586e98034f8f

### DECISION 1

summary: Resolve the ticket span to admit the declared target and scope before investigation.
tool: resolve_ticket
receipt_id: agent-progress:0073a4b5e4810fec57848956c275a32e82495aa615f69dc66c3249020bbf3d30
Arguments: `{"extraction": {"comparisons": ["source stock movements total"], "contexts": ["current global value", "observed difference"], "dates": [], "figures": [], "groupings": [], "identifiers": [], "kind": "FIGURE_DIFFERENCE", "measures": [{"quote": "Handled Quantity", "role": "PRIMARY"}, {"quote": "source stock movements total", "role": "COMPARISON"}], "pages": [], "primary": "Handled Quantity appears higher than the source stock movements total", "reports": [{"quote": "Inventory Health e1b8e1", "role": "PRIMARY"}], "selections": [], "triage": "MISMATCH_COMPLAINT:HORIZONTAL", "visuals": []}}`

### TOOL_RESULT 1

tool: resolve_ticket
receipt_id: agent-progress:1cde1916e7c38ffc91ce8e2e43ae085db0d1bf39866f7dd7cbdd9f6d1f375139
Arguments: `{"extraction": {"comparisons": ["source stock movements total"], "contexts": ["current global value", "observed difference"], "dates": [], "figures": [], "groupings": [], "identifiers": [], "kind": "FIGURE_DIFFERENCE", "measures": [{"quote": "Handled Quantity", "role": "PRIMARY"}, {"quote": "source stock movements total", "role": "COMPARISON"}], "pages": [], "primary": "Handled Quantity appears higher than the source stock movements total", "reports": [{"quote": "Inventory Health e1b8e1", "role": "PRIMARY"}], "selections": [], "triage": "MISMATCH_COMPLAINT:HORIZONTAL", "visuals": []}}`
Result status: INTAKE_ADMITTED
Result IDs: `["agent-progress:94a615ff4c888c909b23f0f7cc5fcb27b94f15765f48125737c41ab6bf40060e"]`

### DECISION 2

summary: Inspect the declared quantity path for the admitted target and scope before comparing it to source.
tool: lineage
receipt_id: agent-progress:3dad76133e53e95e50218e5472d97c8d216fe2af162ad821cc08280bf8549195
Arguments: `{"target_id": "resolved-target:8c863f082edbe1294cb5b5a67003372fb3ee8f470d2447c57a41822d3f08ef33"}`

### TOOL_RESULT 2

tool: lineage
receipt_id: agent-progress:6a1f03b42d90b5dd9012e67ba52fcb83b13e479ffec1db7b0b5ffdd3fe21c797
Arguments: `{"target_id": "resolved-target:8c863f082edbe1294cb5b5a67003372fb3ee8f470d2447c57a41822d3f08ef33"}`
Result status: AVAILABLE
Result IDs: `["agent-tool:9a447b4a-e29a-45b6-b3d4-5279055669ca", "path-e65d7ea0-4c1a-4fe4-9df8-ca1d3b923cce"]`

### DECISION 3

summary: Measure the admitted report target in its declared scope to get the current global Handled Quantity before comparing layers.
tool: reproduce
receipt_id: agent-progress:d3ba3ac3338175172d61ca6da55e2cbeec9a112abc6781288e690410313b206f
Arguments: `{"target_id": "resolved-target:8c863f082edbe1294cb5b5a67003372fb3ee8f470d2447c57a41822d3f08ef33"}`

### TOOL_RESULT 3

tool: reproduce
receipt_id: agent-progress:6c1699f61bcf7f834bb08df1843c951e7522920a26e4f1f3defdae685d64a0dd
Arguments: `{"target_id": "resolved-target:8c863f082edbe1294cb5b5a67003372fb3ee8f470d2447c57a41822d3f08ef33"}`
Result status: UNAVAILABLE
Result IDs: `["agent-tool:d677c49f-faa8-41ce-bbec-284009f99775", "declared-context-25da22e0-faae-44c9-bd51-e9fdf206314e", "b41896ed-e11e-4f00-aeaf-4398c6931d44", "dacd2fb4-f942-4b52-95f6-a233f60ad4f3", "declared-reproduction-b2d055eb7ea3ee4125d4b3d59cb6dce26e722852a63f5a5063484faafeefdd2d"]`

### DECISION 4

summary: Measure the registered quantity at the declared Activity layer to establish the current global Handled Quantity.
tool: probe_layer
receipt_id: agent-progress:35e7272a7417d167e154d68348eba2b903170581cd2065ee4e940e17c811a695
Arguments: `{"layer_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity", "scope_id": "admitted-scope:2a590ba730a145987f80c2c16ad1f1bd85d6ec2da7d1eca0ebb9881f272a531f", "target_id": "resolved-target:8c863f082edbe1294cb5b5a67003372fb3ee8f470d2447c57a41822d3f08ef33"}`

### TOOL_RESULT 4

tool: probe_layer
receipt_id: agent-progress:5c4227870a025b6d22a5f3382a90cb9fbd0ae116c7ec690f55e8946f8459aad3
Arguments: `{"layer_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity", "scope_id": "admitted-scope:2a590ba730a145987f80c2c16ad1f1bd85d6ec2da7d1eca0ebb9881f272a531f", "target_id": "resolved-target:8c863f082edbe1294cb5b5a67003372fb3ee8f470d2447c57a41822d3f08ef33"}`
Result status: AVAILABLE
Result IDs: `["agent-tool:81fd484e-e8e4-4903-94c5-f8267e53d826", "452f1910-9f79-4b3d-acd1-24f60850e688"]`

### DECISION 5

summary: Read the registered quantity at the declared reachable source layer to compare current Handled Quantity against the source stock movements total.
tool: query_source
receipt_id: agent-progress:4e41e02c4ee30209feda571987fbbe2377fe940494606ba550bbeeaa7eb4cea3
Arguments: `{"scope_id": "admitted-scope:2a590ba730a145987f80c2c16ad1f1bd85d6ec2da7d1eca0ebb9881f272a531f", "target_id": "resolved-target:8c863f082edbe1294cb5b5a67003372fb3ee8f470d2447c57a41822d3f08ef33"}`

### TOOL_RESULT 5

tool: query_source
receipt_id: agent-progress:31442eff8ff48e780df6d0299557b1f8fff9fc92110ba4f62154ee6026bfc800
Arguments: `{"scope_id": "admitted-scope:2a590ba730a145987f80c2c16ad1f1bd85d6ec2da7d1eca0ebb9881f272a531f", "target_id": "resolved-target:8c863f082edbe1294cb5b5a67003372fb3ee8f470d2447c57a41822d3f08ef33"}`
Result status: UNDECLARED
Result IDs: `["agent-tool:13653316-cda1-47e4-a16e-513ae6e8a56f"]`

### DECISION 6

summary: Fetch the retained lineage details to identify which resolved stock_movements layer is the declared source before probing it.
tool: get_evidence
receipt_id: agent-progress:55bd5947c2eb98869058c3804867fc78617f96e95f3394f7daa34e58b0fab1c8
Arguments: `{"id": "path-e65d7ea0-4c1a-4fe4-9df8-ca1d3b923cce"}`

### EVIDENCE_FETCH 6

receipt_id: agent-progress:45e01a5e3918f49c9eb5ee057e96a45583cc1c60781121c774f5c42aab0076d4
evidence_id: path-e65d7ea0-4c1a-4fe4-9df8-ca1d3b923cce
Full original retained evidence fetched; original receipt: agent-progress:6a1f03b42d90b5dd9012e67ba52fcb83b13e479ffec1db7b0b5ffdd3fe21c797

### DECISION 7

summary: Measure the declared stock_movements quantity at the refined layer to compare its current global total against the 8765 report-layer value.
tool: probe_layer
receipt_id: agent-progress:09e19366f13bb89f4d6384490eb70febad8e3f7e8c22464d3a0eb0a6be048c3d
Arguments: `{"layer_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1", "scope_id": "admitted-scope:2a590ba730a145987f80c2c16ad1f1bd85d6ec2da7d1eca0ebb9881f272a531f", "target_id": "resolved-target:8c863f082edbe1294cb5b5a67003372fb3ee8f470d2447c57a41822d3f08ef33"}`

### TOOL_RESULT 7

tool: probe_layer
receipt_id: agent-progress:411bd1ae6d46ccd3a93c96b1b541a95c863bad17f51124a65664259f14133907
Arguments: `{"layer_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1", "scope_id": "admitted-scope:2a590ba730a145987f80c2c16ad1f1bd85d6ec2da7d1eca0ebb9881f272a531f", "target_id": "resolved-target:8c863f082edbe1294cb5b5a67003372fb3ee8f470d2447c57a41822d3f08ef33"}`
Result status: AVAILABLE
Result IDs: `["agent-tool:3bb33210-5d9e-468d-bf4f-170d6177fbc3", "d2cc0fa9-50a4-4ee3-9d7a-e2d7c8d7f2f5"]`

### DECISION 8

summary: Measure the registered quantity at the intermediate movement_values layer to locate where the current 8765 vs 7661 difference first appears.
tool: probe_layer
receipt_id: agent-progress:c56e42d7e106c218d62c76fbae38cf6fc0b7f45688f0d6f8b61a3042de1469b6
Arguments: `{"layer_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values", "scope_id": "admitted-scope:2a590ba730a145987f80c2c16ad1f1bd85d6ec2da7d1eca0ebb9881f272a531f", "target_id": "resolved-target:8c863f082edbe1294cb5b5a67003372fb3ee8f470d2447c57a41822d3f08ef33"}`

### TOOL_RESULT 8

tool: probe_layer
receipt_id: agent-progress:ea2c74c07312a61e3f75e8d6444ba9672d7be4d80626e2633f94fd5f01dc4ff9
Arguments: `{"layer_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values", "scope_id": "admitted-scope:2a590ba730a145987f80c2c16ad1f1bd85d6ec2da7d1eca0ebb9881f272a531f", "target_id": "resolved-target:8c863f082edbe1294cb5b5a67003372fb3ee8f470d2447c57a41822d3f08ef33"}`
Result status: AVAILABLE
Result IDs: `["agent-tool:e1738d50-c7cb-4179-a836-9efd8b3f3b3d", "71673b49-5534-4253-8c43-901fd0b19882"]`

### DECISION 9

summary: Read the declared transformation for the step where the value changes from 8765 to 7661 to explain the observed difference.
tool: read_transformation
receipt_id: agent-progress:245e1c12d2192def8366f5399fbc832c68ceead760268667daa70b403cbb6d38
Arguments: `{"step": 2, "target_id": "resolved-target:8c863f082edbe1294cb5b5a67003372fb3ee8f470d2447c57a41822d3f08ef33"}`

### TOOL_RESULT 9

tool: read_transformation
receipt_id: agent-progress:5127244524dbfaf42d89b53bd3f1b79ed3d03934e7e92f96b0aadd39b3d56cf7
Arguments: `{"step": 2, "target_id": "resolved-target:8c863f082edbe1294cb5b5a67003372fb3ee8f470d2447c57a41822d3f08ef33"}`
Result status: AVAILABLE
Result IDs: `["agent-tool:f0d35164-78e8-4c6c-9802-61bec70028ea", "transformation-definition-23fb25c7-fa90-4333-9acc-13e5aecf12de"]`

### DECISION 10

summary: Fetch the retained transformation details for the step where the value drops from 8765 to 7661 so the observed difference can be explained from evidence.
tool: get_evidence
receipt_id: agent-progress:94a20cbf8dee70bc36cfe7c7a5fdeb82699e41bd4a2c54fbeae71958f1e67004
Arguments: `{"id": "transformation-definition-23fb25c7-fa90-4333-9acc-13e5aecf12de"}`

### EVIDENCE_FETCH 10

receipt_id: agent-progress:6f35d9ff68bbfc7abe07eaf1841499b70054cfd7ba7c2c85f3bb2ab7fd7d6e02
evidence_id: transformation-definition-23fb25c7-fa90-4333-9acc-13e5aecf12de
Full original retained evidence fetched; original receipt: agent-progress:5127244524dbfaf42d89b53bd3f1b79ed3d03934e7e92f96b0aadd39b3d56cf7

### DECISION 11

summary: Report the current global Handled Quantity and explain the observed difference from stock movements using the declared path evidence.
outcome: TRANSFORMATION_LOGIC
receipt_id: agent-progress:3c31f67d0bd88872b68e56aa14a985dc3fea6c9cd72144fafeeeac2e4b223c9c
Proposed claims: `[{"evidence_ids": ["agent-progress:94a615ff4c888c909b23f0f7cc5fcb27b94f15765f48125737c41ab6bf40060e", "452f1910-9f79-4b3d-acd1-24f60850e688"], "text": "In the admitted ungrouped global scope for the declared target, Handled Quantity currently measures 8765 at the Activity layer."}, {"evidence_ids": ["agent-progress:94a615ff4c888c909b23f0f7cc5fcb27b94f15765f48125737c41ab6bf40060e", "d2cc0fa9-50a4-4ee3-9d7a-e2d7c8d7f2f5"], "text": "At the declared stock_movements_e1b8e1 layer on the same registered path and scope, the measured total is 7661."}, {"evidence_ids": ["452f1910-9f79-4b3d-acd1-24f60850e688", "71673b49-5534-4253-8c43-901fd0b19882"], "text": "The intermediate movement_values layer also measures 8765, matching Activity, so the 8765 vs 7661 difference is already present above the stock_movements layer rather than being introduced between movement_values and Activity."}, {"evidence_ids": ["transformation-definition-23fb25c7-fa90-4333-9acc-13e5aecf12de", "d2cc0fa9-50a4-4ee3-9d7a-e2d7c8d7f2f5", "71673b49-5534-4253-8c43-901fd0b19882"], "text": "The retained transformation definition for that step includes a left join on product_id where matching rows may multiply because uniqueness is not assumed; the retained explanation says this can duplicate stock movement rows and can explain an increase from 7661 to 8765. Its stated limitation is that this shows a mechanism present in the definition, not proof that duplicate matches actually occurred in the current data."}]`

### CLAIM_REJECTED 11

reason: DELIVERY_VALIDATION_FAILED
receipt_id: agent-progress:15801c81db563b0835e608312e66213298b0751d96d66b4d990bab4333dd38cc

### DECISION 12

summary: Fetch the retained transformation details so the observed 8765 versus 7661 difference can be explained with direct evidence.
tool: get_evidence
receipt_id: agent-progress:5af9d20c2dd76321b1a74e39bd8f8f5374d9c37c7cfeb9a14e7693478b8680c3
Arguments: `{"id": "transformation-definition-23fb25c7-fa90-4333-9acc-13e5aecf12de"}`

### EVIDENCE_FETCH 12

receipt_id: agent-progress:5e40e4031bbbb75951b59a2d06e94a2be83f8ca5b2036da3d543d6750c809a5e
evidence_id: transformation-definition-23fb25c7-fa90-4333-9acc-13e5aecf12de
Full original retained evidence fetched; original receipt: agent-progress:5127244524dbfaf42d89b53bd3f1b79ed3d03934e7e92f96b0aadd39b3d56cf7

### DECISION 13

summary: Reported the current global Handled Quantity, compared it to the declared stock_movements path total, and explained the observed increase from the transformation definition.
outcome: TRANSFORMATION_LOGIC
receipt_id: agent-progress:e9c2dab8d969b19c75e7f0d0fc3e357604e9c5aed2c9f19b9bc159bdf6029fee
Proposed claims: `[{"evidence_ids": ["452f1910-9f79-4b3d-acd1-24f60850e688", "agent-tool:81fd484e-e8e4-4903-94c5-f8267e53d826"], "text": "The current global Handled Quantity for the admitted target measures 8765 at the report path's Activity layer."}, {"evidence_ids": ["452f1910-9f79-4b3d-acd1-24f60850e688", "d2cc0fa9-50a4-4ee3-9d7a-e2d7c8d7f2f5", "agent-tool:81fd484e-e8e4-4903-94c5-f8267e53d826", "agent-tool:3bb33210-5d9e-468d-bf4f-170d6177fbc3"], "text": "The declared stock_movements_e1b8e1 layer on that same registered quantity path measures 7661, which is 1104 lower than the 8765 report-path value."}, {"evidence_ids": ["path-e65d7ea0-4c1a-4fe4-9df8-ca1d3b923cce", "agent-tool:9a447b4a-e29a-45b6-b3d4-5279055669ca", "71673b49-5534-4253-8c43-901fd0b19882", "agent-tool:e1738d50-c7cb-4179-a836-9efd8b3f3b3d", "d2cc0fa9-50a4-4ee3-9d7a-e2d7c8d7f2f5"], "text": "Lineage places the path as Activity -> movement_values -> stock_movements_e1b8e1, and the intermediate movement_values layer also measures 8765, so the increase is already present between stock_movements_e1b8e1 and movement_values rather than being introduced at the final Activity layer."}, {"evidence_ids": ["transformation-definition-23fb25c7-fa90-4333-9acc-13e5aecf12de", "agent-tool:f0d35164-78e8-4c6c-9802-61bec70028ea"], "text": "The retained transformation definition for that step includes a left join on product_id where matching rows may multiply because uniqueness is not assumed. The evidence says this can explain the rise from 7661 to 8765, but it does not establish that duplicate matches actually occurred or prove business correctness."}]`

### DELIVERED 13

receipt_id: agent-progress:92f1a627d01d6efc0bc6cb0783cb9bac524010dcd5d5d978b25cdb1ff7ebb57d

## Verbatim business output

You asked: Description supplied by user:
In Inventory Health e1b8e1, Handled Quantity appears higher than the source stock movements total. Investigate the current global value and explain any observed difference.

Comparison selected by user:
The application
Answer to your question: Partly answered.
Regarding the requested comparison: Independent quantities were compared within the checked scope; remaining boundaries, timing and business intent are limited by the recorded evidence.
What the investigation established:

The declared layer showed 8,765 for movements, matching its declared input. The declared layer contained 7,661 for movements; the difference appears between the declared layer and the declared layer, in the step that matches movements with rates. Several matching rates can cause an entry to contribute more than once. We have not confirmed the repeated matches, whether the checks describe the same moment, whether this matching rule is intended, or how movements were first entered. For the declared layer and the declared layer, the two checks used different calculation engines. For the declared layer and the declared layer, the checks read different data sources; different calculation engines were not established, so a shared calculation fault could affect both. Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.

## Verbatim technical output

You asked: Description supplied by user:
In Inventory Health e1b8e1, Handled Quantity appears higher than the source stock movements total. Investigate the current global value and explain any observed difference.

Comparison selected by user:
The application
Answer to your question: Partly answered.
Regarding the requested comparison: Independent quantities were compared within the checked scope; remaining boundaries, timing and business intent are limited by the recorded evidence.
What the investigation established:

Measure: Handled Quantity.
Roles reached in path resolution: L0 (role undeclared), L1 (role undeclared), L2 (role undeclared). These labels do not establish successful reads.
B2 diverges: L2 (stock movements e1b8e1, upstream input) 7,661 -> L1 (movement values, downstream output) 8,765.
B1 agrees: L1 (movement values, upstream input) 8,765 -> L0 (Activity, downstream output) 8,765.
ENGINE_INDEPENDENT: comparable quantity-bound engine self-reports differ; this is an engine-independent cross-surface comparison. (receipt agent-boundary:258e416f19856dac9630bcfbfa0fdd1b18461f557c326caf3c7fd5e2c11b8287).
OBJECT_DISTINCT: comparable quantity-bound object self-reports differ; this verifies a data-path boundary, not engine-level independence. Shared computation faults are not excluded. (receipt agent-boundary:138b610fe82d89485a18e76b27272e3c192f61b61a30cf954347677a8f7466bc).

A left join on product_id combines movements with rates without an asserted unique match on the rates side. When more than one rates row matches a movement row, the join repeats that movement row before the derived value is calculated from units and unit cost. Repeated movement rows raise the whole-entity additive total while the units column itself is otherwise carried through.

Layers:
L0 - Activity: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity
L1 - movement values: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values
L2 - stock movements e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1

Limits:
- Unattested connection on L0 (receipt 452f1910-9f79-4b3d-acd1-24f60850e688).
- Unattested connection on L1 (receipt 71673b49-5534-4253-8c43-901fd0b19882).
- Unattested connection on L2 (receipt d2cc0fa9-50a4-4ee3-9d7a-e2d7c8d7f2f5).
- SNAPSHOT_UNVERIFIED for B1, B2: the reads cannot be tied to matching data versions; agreement does not prove currency, and different update timing was not excluded as a cause of divergence.
- Checked through L2; stopped because no lineage.

Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.

Previous runs: same ticket 288b5c79-de67-483f-835a-7652c66d5da3, 77ffd137-8061-4372-b323-5ee71a521b47, 964c94e9-3daa-4aac-a3e0-9a7351d1e1e3, 9a0cda78-6fb0-43f4-a744-d2d6fca63697, ae42f998-2b2c-4832-9d05-f90cb7b7c233, bc32732d-4fba-46ae-9763-4522a1b3cda4, be3a2e07-66dd-49b6-b07b-4cdf29a83aa4, e938f3eb-a853-4e51-b775-836a66e8a7b4.
