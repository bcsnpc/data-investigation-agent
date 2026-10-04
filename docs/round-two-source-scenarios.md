# Part B: source-boundary scenarios and retained failures

2026-10-04 UTC. Known-domain regressions only. All original artifacts, failed
runs and receipts remain unchanged. No freeze or unfamiliar-domain acceptance.

## Ordered implementation and measurement

- #357 merged `8e21b4a`: human-approved Part B ceiling 300 to 500, rolling
  unchanged at 600, diagnostic cap 12; full current binding/recollection and
  earlier E/intake failures recorded. Configuration before/after and ledger.
- #358 merged `411f084`: model-only source questions no longer require a report
  merely because a number is present. Explicit report/selection requirements
  remain. 82 focused tests and six green checks. The runs below expose that a
  model can still mislabel a model name as a report binding; do not claim this
  fixed all reportless intake failures.
- #359 merged `b4e5152`: audit-first source delivery with explicit discovered
  key/version/UTC semantics, bounded compiled pages and original-receipt
  revalidation; declared unreachable authority. 142 focused tests followed by
  55 source/audit/flexible tests, six green checks. Strict failed/malformed audit
  refusal, mixed timing and incomplete enumeration tests. Two audit integration
  defects fixed: endpoint nesting and typed cells. Existing planner golden
  projection unchanged at 28 entries / 11 SQL objects / 5,543 characters.
- This measurement records all runs, fixture controls, configuration approvals,
  restoration and the Part C design. No engine changes during these four cases.

## Independent fixture arithmetic and exact state changes

The retained literal seed, not a compiled engine query, supplied 360 rows.
Plain Python summed the `units` elements by warehouse: **2,948 + 2,084 +
2,629 = 7,661**. Retained definition hash:
`5f61cd4e0cdac7801df4bfdd0ca74f053fed0ef143a66b6eab4f2d0a3616f011`.
All four tickets/figures are fixture-authored, never user-observed.

- Gap: add movement **900002**, warehouse 1, product 1, **11** units,
  `2026-10-04`, `RECEIPT`, server UTC modification
  `2026-10-04T05:25:02.2725388Z`, server version **30001**. Source arithmetic
  **7,661 + 11 = 7,672**, 361 rows. Copy completes with own counters **361/361**.
  A separately published isolated fixture notebook removes only that row from
  the destination. Its served exit value attests Delta **9 -> 10**, rows
  **361 -> 360**, units **7,672 -> 7,661**. This is intentional post-copy loss,
  not evidence that the Copy Job omitted it. Source row removed afterwards.
- Latency: after the baseline restoration pipeline completes, add movement
  **900001**, same warehouse/product/day/type, **17** units, server UTC
  modification `2026-10-04T05:39:49.5973752Z`, version **30002**. Arithmetic
  **7,661 + 17 = 7,678**, source 361 rows/destination 360. No subsequent load.
  Remove this authored source row after the run; destination remained baseline.
- Consistency: unchanged seed **7,661** on each intended surface; record **900099**
  intentionally absent from the authored source. Agreement would establish only
  the quantity's pipeline continuity, not whether the application contains all
  expected business records. Intake refused before testing this condition.
- Unreachable: same **7,661** baseline, declared authority configured
  `reachable: false`. Intake refused before testing the configured termination.
  Restore `reachable: true` and approve that full configuration afterwards.

The existing original model/data/report definitions were not edited. Final
reader checks returned **7,661** from the application, isolated Bronze SQL
endpoint and isolated semantic model, and **8,765** from the original model.
The application contains 360 rows after both authored-row deletions, verified
by the fixture owner control read. No refresh, reframe, permission or schedule
change in these scenarios. The new fixture utility notebook is retained with
its definition and completed run, not reused as investigation evidence.

Notebook exit-value retrieval used the documented
[Notebook job API](https://learn.microsoft.com/en-us/fabric/data-engineering/notebook-public-api).
Its evidence is fixture-publisher evidence; it is not reader snapshot attestation.

## Configuration and metadata provenance

Source-role configuration supplies discovered column identities for the key,
copied version token and UTC last-modified semantics. It contains no expected
figure or per-family route. SQL/Fabric connections, credentials, permissions and
workspace scopes are unchanged. Full policy hashes are retained; no narrowing.
These semantic-only approvals republish exact retained metadata, not newly
acquired cloud metadata. They preserve acquisition time
2026-10-04T03:33:48.312811+00:00 and its completed responses, reuse seven catalog
commands with **zero executions**, and retain original runs/tapes byte-for-byte.
The full live acquisition was already recorded in #357. No current-content
freshness claim is inferred from these policy-approval timestamps.

- discovery-roles-approval-resume: policy `ea0b4c2f99fc41fb857d6aa38422aa67e21bb458a0fbb883792887db1137d959`, discovery `2effdf9d-d28e-48f1-b5bd-eaca002bb7cc`, inventory `7770404f-33dc-4f42-939b-f46afa247eab`, model revision 3, context `c1efd94a-eff1-4fde-9973-0b436ad27952`; zero new physical requests, historical artifacts unchanged.

- discovery-unreachable-approval: policy `eb5f988d28fe22cd35a93d6245a1a4032081501874ec3c1cc648973de237ceb2`, discovery `738ff5a8-0de7-4e44-94bf-a82a2b55615c`, inventory `063d24e8-ee34-4551-b5e8-99d3c68dd59e`, model revision 4, context `22a22d75-7f31-4df9-9c3d-f8f3df002fd5`; zero new physical requests, historical artifacts unchanged.

- discovery-reachable-approval: policy `7b2677e91d490ecce5ad3f6ba2cf9484014a789f50fea799b1bf4193535ae3e8`, discovery `b7389853-37a8-4a72-88a8-1fa8fe1fcf08`, inventory `0ee702d8-5dcd-40e3-8907-34c2ca0d0b32`, model revision 5, context `c1cd5dff-3814-412b-ad45-df07f248fbaf`; zero new physical requests, historical artifacts unchanged.

## Preserved preparation failures and accounting corrections

- The earlier source investigation after #358 reached Bronze but its actual
  application query failed with SQL **40613**, source connection unavailable.
  It spent six physical requests, three diagnostics and three guards, then
  completed CONSISTENT_TO_BOUNDARY with validated synthesis. It does not earn
  source consistency. Both outputs follow below.
- A fixture-owner baseline connection also failed 40613; no mutation occurred.
  A subsequent read-only control-plane result reported Online, resumed at
  05:23:22.927 UTC, `useFreeLimit: true`, `AutoPause`, delay 60. No SQL policy
  changed. The errors are not rewritten as proven cold-start diagnoses.
- Source gap preparation failed SQL156 on an unquoted `identity` alias before
  mutation; corrected control-script preparation succeeded separately. Original
  failure preserved, no refund or investigation replacement.
- Role re-approval preflight failed on raw-versus-normalized path digest;
  a resume helper failed FileExistsError before collection. Corrected exact
  retained-response publication succeeded separately; zero cloud requests.
- Gap notebook creation returned 202 with a regional operation Location. The
  control script refused that host before polling; the accepted operation was
  resumed at the public operation endpoint, never republished. Completed
  notebook ID `5a3200de-8ef9-4a1b-8128-db9cacc8a779`, job
  `93f696bd-8c38-4b06-aae8-98db2150cdaa`. Its Delta receipt is described above.
- Final verification originally recorded four outer logical checks despite ten
  charged physical reservations. An appended correction adds the six omitted
  subrequests (two diagnostics/four guards), with **zero new requests** and no
  counter adjustment. Correct totals: ten physical, four diagnostic, six guard.
- The unreachable intake row has a zero settled provider-token metric despite
  its retained provider metadata reporting **15,285 input / 130 output tokens**.
  A separate annotation records the provider report; no usage counters are
  reset, settled retroactively, refunded or edited. One intake call was charged.

## Run metrics and probe evidence

E was reported before the source scenarios. It stayed TRANSFORMATION_LOGIC:
definition-compatible join multiplication, not freshness evidence. The original
E path is unchanged and literal-seeded; the isolated application fixture does
not silently redirect that ticket to a different model.

Each successful quantity/audit probe below self-reports engine, identity and
object in its value statement: consistency MATCHED, coverage PARTIAL,
connection unattested. Independent engine self-report differences grade both
new boundaries ENGINE_INDEPENDENT. All comparisons remain SNAPSHOT_UNVERIFIED,
so agreement does not establish currency and divergence does not exclude timing.
No source-membership pages executed: audit unavailability stopped that producer.

| Case | Outcome/status | Physical | Diagnostic/cap | Guards/reuse | Intake/judge/synthesis | Investigation planner |
| --- | --- | ---: | --- | --- | --- | ---: |
| E | TRANSFORMATION_LOGIC | 10 | 4/12 | 6/0 | 1/1/1 | 0 |
| SOURCE_CONSISTENCY_POST_FIX | CONSISTENT_TO_BOUNDARY | 6 | 3/12 | 3/0 | 1/0/1 | 0 |
| B3_GAP | NO_KNOWN_PATTERN | 13 | 5/12 | 8/1 | 1/0/1 | 0 |
| B3_LATENCY | NO_KNOWN_PATTERN | 13 | 5/12 | 8/1 | 1/0/1 | 0 |
| B3_CONSISTENT | NEEDS_INPUT | 0 | 0/12 | 0/0 | 1/0/0 | 0 |
| B3_UNREACHABLE | NEEDS_INPUT | 0 | 0/12 | 0/0 | 1/0/0 | 0 |

Gap/latency diagnostic count five includes one metadata endpoint descriptor;
four are value queries (one DAX, three SQL: destination, application, audit).
Each has eight guard requests and one recorded guard reuse. Per-run cap 12
was not approached. E has one DAX/two SQL quantity queries plus one metadata
operation. Completed pairs have validated synthesis; neither intake refusal
ran synthesis or a walk. Every requested attempt has its own ledger row.

## E — exact outputs and probes
Session `44dabc8c-4c9c-4639-9532-31217f2453be`; synthesis COMPLETED.

| Receipt | Tool | Surface engine/object | Identity | Attestation |
| --- | --- | --- | --- | --- |
| `b8006c45-809b-4c94-bb1a-8d0a1e6d84b1` | bounded_dax | OLAP Server / 3484a2bc-98c5-4cef-be5c-a6215484075e | investigator-reader@skynwhy.com | MATCHED; PARTIAL; connection unreported |
| `0a14f9e1-6ee3-4385-a731-adc87cb71beb` | bounded_fabric_sql | Microsoft Azure SQL Data Warehouse / warehouse_gold_e1b8e1 | investigator-reader@skynwhy.com | MATCHED; PARTIAL; connection unreported |
| `dcb8e92d-6b2e-436a-9752-925d45771250` | bounded_fabric_sql | Microsoft Azure SQL Data Warehouse / warehouse_silver_e1b8e1 | investigator-reader@skynwhy.com | MATCHED; PARTIAL; connection unreported |

business_output (verbatim):

```text
You asked: Inventory Health e1b8e1 Handled Quantity may be stale. Inspect the available refresh and processing history and explain whether freshness can be established. I have not supplied a freshness SLA.
Answer to your question: Not answered.
Regarding whether the reported information is current: No completed currency check establishes whether the reported information is current. Refresh history was unavailable to the diagnostic reader. Processing history was not assessed before the investigation stopped.
What was found instead:

The report showed 8,765 for movements, matching the total used to prepare it. The table it is built from contained 7,661 for movements; the difference appears in the step that matches movements with rates. Several matching rates can cause an entry to contribute more than once. We have not confirmed the repeated matches, whether the checks describe the same moment, whether this matching rule is intended, or how movements were first entered. For the report and the table used to prepare it, the two checks used different calculation engines. For the table used to prepare the report and the table it is built from, the checks read different data sources; different calculation engines were not established, so a shared calculation fault could affect both. Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.
```

technical_output (verbatim):

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

## SOURCE_CONSISTENCY_POST_FIX — exact outputs and probes
Session `003adb5d-e2cd-4088-bca2-c36fc65613fc`; synthesis COMPLETED.

| Receipt | Tool | Surface engine/object | Identity | Attestation |
| --- | --- | --- | --- | --- |
| `c2185d91-ebc7-4434-8582-569327b0642c` | bounded_dax | OLAP Server / 0c89889c-6fe6-49ab-91e9-4b00a51070e6 | investigator-reader@skynwhy.com | MATCHED; PARTIAL; connection unreported |
| `c69c90a3-c659-4910-aadf-15645222cfa7` | bounded_fabric_sql | Microsoft Azure SQL Data Warehouse / round_two_bronze_20261003 | investigator-reader@skynwhy.com | MATCHED; PARTIAL; connection unreported |

business_output (verbatim):

```text
You asked: In Application load fixture 20261003, Movement Units shows 7,661 units. I believe a movement is missing. Please trace the displayed figure to the application so I know whether the pipeline lost anything.
Answer to your question: Not answered.
Regarding the original question: No recorded completion check establishes an answer to this request.
What was found instead:

The checked report value was 7,661. A separate check of the total used to prepare the report agreed. This rules out a report-to-input difference within these checks, but does not prove the original records are correct. The original entries, unchecked selections, update timing and intended business rules remain outside what these comparisons establish. For the report and the table used to prepare it, the two checks used different calculation engines. Recommended action: Ask the owner of the unchecked part of the process to investigate the remaining gap.
```

technical_output (verbatim):

```text
You asked: In Application load fixture 20261003, Movement Units shows 7,661 units. I believe a movement is missing. Please trace the displayed figure to the application so I know whether the pipeline lost anything.
Answer to your question: Not answered.
Regarding the original question: No recorded completion check establishes an answer to this request.
What was found instead:

Measure: Movement Units.
B1 agrees: L1 (dbo.stock movements round two 20261003 in round two bronze 20261003, upstream input) 7,661 -> L0 (Movements in Application load fixture 20261003, downstream output) 7,661.
ENGINE_INDEPENDENT: comparable quantity-bound engine self-reports differ; this is an engine-independent cross-surface comparison. (receipt boundary-1-comparison).
Declared-context reproduction unavailable: Declared-context reproduction is undeclared for question kind SOURCE_CORRECTNESS.

Across the recorded comparison, the Movement Units quantity is carried unchanged from the stock movements round two table to the Movements table. The displayed figure therefore matches the quantity present at that checked boundary.

Layers:
L0 - Movements in Application load fixture 20261003: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements
L1 - dbo.stock movements round two 20261003 in round two bronze 20261003: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003
L2 - app.stock movements round two 20261003 in ordersops: sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945

Limits:
- Unattested connection on L0 (receipt c2185d91-ebc7-4434-8582-569327b0642c).
- Unattested connection on L1 (receipt c69c90a3-c659-4910-aadf-15645222cfa7).
- SNAPSHOT_UNVERIFIED for B1: the reads cannot be tied to matching data versions; agreement does not prove currency, and different update timing was not excluded as a cause of divergence.
- Checked through L1; stopped because not comparable.
- Unchecked L1 -> L2: Application quantity was not established; the original receipt records the failure..
- Quantities trace unchanged integral columns; joins may multiply rows and whole-row deduplication may remove them. Key uniqueness and intended grain are not established.

Recommended action: Ask the owner of the unchecked part of the process to investigate the remaining gap.
```

## B3_GAP — exact outputs and probes
Session `ca4891ac-3c94-473d-9fe0-74098778db9b`; synthesis COMPLETED.

| Receipt | Tool | Surface engine/object | Identity | Attestation |
| --- | --- | --- | --- | --- |
| `a733d59a-5521-4008-98e3-30e53b93458d` | bounded_dax | OLAP Server / 0c89889c-6fe6-49ab-91e9-4b00a51070e6 | investigator-reader@skynwhy.com | MATCHED; PARTIAL; connection unreported |
| `98560a6e-defd-4bcb-824e-854cae70311e` | bounded_fabric_sql | Microsoft Azure SQL Data Warehouse / round_two_bronze_20261003 | investigator-reader@skynwhy.com | MATCHED; PARTIAL; connection unreported |
| `760c3f72-4fba-4797-9657-bb8dabf3f1dd` | bounded_sql | Microsoft SQL Azure / ordersops | orderops_investigator | MATCHED; PARTIAL; connection unreported |
| `730aaed0-ba84-4855-b4a1-2b9f48129c45` | bounded_fabric_sql | Microsoft Azure SQL Data Warehouse / round_two_bronze_20261003 | investigator-reader@skynwhy.com | MATCHED; PARTIAL; connection unreported |

Audit original rows, not substituted counters: `2a3801ae-ef67-4106-ba39-2c77fe68a158` **360 read / 360 written**, started `2026-10-04T02:25:15.2840632Z`, ended `2026-10-04T02:26:24.1249979Z`, plus `7d797def-9587-45bb-803d-5a58090cf658` with null start/end/read/write, `UNAVAILABLE_COPY_OUTPUT`. Producer result: **UNAVAILABLE**, "Audit response has malformed accounting or run timestamps." The 360/360 row was read but **not adopted as current load accounting**. No membership pages or load/gap claim followed.

business_output (verbatim):

```text
You asked: In Application load fixture 20261003, Movement Units shows 7,661 units. Recent movements are missing. Please trace this figure to the application and establish whether a completed load left anything out.
Answer to your question: Not answered.
Regarding the original question: No recorded completion check establishes an answer to this request.
What was found instead:

The report showed 7,661, matching the total used to prepare it. The table it is built from contained 7,672; the difference appears during preparation of the report. The checks locate the difference but do not establish a specific explanation for it. The retrieved definition supplies no usable business names for the compared entries; their origin, update timing and intended treatment remain unconfirmed. For the report and the table used to prepare it, the two checks used different calculation engines. For the table used to prepare the report and the table it is built from, the two checks used different calculation engines. Recommended action: Ask the responsible owner to review the recorded missing evidence and next step.
```

technical_output (verbatim):

```text
You asked: In Application load fixture 20261003, Movement Units shows 7,661 units. Recent movements are missing. Please trace this figure to the application and establish whether a completed load left anything out.
Answer to your question: Not answered.
Regarding the original question: No recorded completion check establishes an answer to this request.
What was found instead:

Measure: Movement Units.
B2 diverges: L2 (app.stock movements round two 20261003 in ordersops, upstream input) 7,672 -> L1 (dbo.stock movements round two 20261003 in round two bronze 20261003, downstream output) 7,661.
B1 agrees: L1 (dbo.stock movements round two 20261003 in round two bronze 20261003, upstream input) 7,661 -> L0 (Movements in Application load fixture 20261003, downstream output) 7,661.
ENGINE_INDEPENDENT: comparable quantity-bound engine self-reports differ; this is an engine-independent cross-surface comparison. (receipt boundary-1-comparison).
ENGINE_INDEPENDENT: comparable quantity-bound engine self-reports differ; this is an engine-independent cross-surface comparison. (receipt boundary-2-comparison).
Declared-context reproduction unavailable: Declared-context reproduction is undeclared for question kind SOURCE_CORRECTNESS.

The displayed measure aligns with the movement staging table, while an earlier relation carries a larger total, so the reduction occurs at the handoff from that relation into the staging table. The displayed measure then carries the staged total without further change in the shown comparisons.

Load accounting was unavailable: Audit response has malformed accounting or run timestamps.

Layers:
L0 - Movements in Application load fixture 20261003: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements
L1 - dbo.stock movements round two 20261003 in round two bronze 20261003: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003
L2 - app.stock movements round two 20261003 in ordersops: sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945

Limits:
- Unattested connection on L0 (receipt a733d59a-5521-4008-98e3-30e53b93458d).
- Unattested connection on L1 (receipt 98560a6e-defd-4bcb-824e-854cae70311e).
- Unattested connection on L2 (receipt 760c3f72-4fba-4797-9657-bb8dabf3f1dd).
- SNAPSHOT_UNVERIFIED for B1, B2: the reads cannot be tied to matching data versions; agreement does not prove currency, and different update timing was not excluded as a cause of divergence.
- Checked through L2; stopped because capability not implemented.
- Quantities trace unchanged integral columns; joins may multiply rows and whole-row deduplication may remove them. Key uniqueness and intended grain are not established.

Recommended action: Ask the responsible owner to review the recorded missing evidence and next step.
```

## B3_LATENCY — exact outputs and probes
Session `61284fb4-283d-429d-9b3e-b4835314ac56`; synthesis COMPLETED.

| Receipt | Tool | Surface engine/object | Identity | Attestation |
| --- | --- | --- | --- | --- |
| `0f0d6eea-b329-48b6-a50b-3e51146b0ee0` | bounded_dax | OLAP Server / 0c89889c-6fe6-49ab-91e9-4b00a51070e6 | investigator-reader@skynwhy.com | MATCHED; PARTIAL; connection unreported |
| `a7f614ff-e23b-4435-9ecb-375e9ebf398d` | bounded_fabric_sql | Microsoft Azure SQL Data Warehouse / round_two_bronze_20261003 | investigator-reader@skynwhy.com | MATCHED; PARTIAL; connection unreported |
| `15b007aa-feca-41c3-97f5-961b4252fd6e` | bounded_sql | Microsoft SQL Azure / ordersops | orderops_investigator | MATCHED; PARTIAL; connection unreported |
| `d1ce393c-ce57-480a-bfd8-25f13cc6bd5d` | bounded_fabric_sql | Microsoft Azure SQL Data Warehouse / round_two_bronze_20261003 | investigator-reader@skynwhy.com | MATCHED; PARTIAL; connection unreported |

Audit original rows, not substituted counters: `2a3801ae-ef67-4106-ba39-2c77fe68a158` **360 read / 360 written**, started `2026-10-04T02:25:15.2840632Z`, ended `2026-10-04T02:26:24.1249979Z`, plus `7d797def-9587-45bb-803d-5a58090cf658` with null start/end/read/write, `UNAVAILABLE_COPY_OUTPUT`. Producer result: **UNAVAILABLE**, "Audit response has malformed accounting or run timestamps." The 360/360 row was read but **not adopted as current load accounting**. No membership pages or load/gap claim followed.

business_output (verbatim):

```text
You asked: In Application load fixture 20261003, Movement Units shows 7,661 units and looks stale. Please check whether the application changed after the last successful load.
Answer to your question: Not answered.
Regarding whether the reported information is current: No completed currency check establishes whether the reported information is current. Refresh history was unavailable to the diagnostic reader. Processing history was not assessed before the investigation stopped.
What was found instead:

The report showed 7,661, matching the total used to prepare it. The table it is built from contained 7,678; the difference appears during preparation of the report. The checks locate the difference but do not establish a specific explanation for it. The retrieved definition supplies no usable business names for the compared entries; their origin, update timing and intended treatment remain unconfirmed. For the report and the table used to prepare it, the two checks used different calculation engines. For the table used to prepare the report and the table it is built from, the two checks used different calculation engines. Recommended action: Ask the responsible owner to review the recorded missing evidence and next step.
```

technical_output (verbatim):

```text
You asked: In Application load fixture 20261003, Movement Units shows 7,661 units and looks stale. Please check whether the application changed after the last successful load.
Answer to your question: Not answered.
Regarding whether the reported information is current: No completed currency check establishes whether the reported information is current. Refresh history was unavailable to the diagnostic reader. Processing history was not assessed before the investigation stopped.
What was found instead:

Measure: Movement Units.
B2 diverges: L2 (app.stock movements round two 20261003 in ordersops, upstream input) 7,678 -> L1 (dbo.stock movements round two 20261003 in round two bronze 20261003, downstream output) 7,661.
B1 agrees: L1 (dbo.stock movements round two 20261003 in round two bronze 20261003, upstream input) 7,661 -> L0 (Movements in Application load fixture 20261003, downstream output) 7,661.
ENGINE_INDEPENDENT: comparable quantity-bound engine self-reports differ; this is an engine-independent cross-surface comparison. (receipt boundary-1-comparison).
ENGINE_INDEPENDENT: comparable quantity-bound engine self-reports differ; this is an engine-independent cross-surface comparison. (receipt boundary-2-comparison).
Declared-context reproduction unavailable: Declared-context reproduction is undeclared for question kind FRESHNESS.

The recorded checks keep the measure value aligned between the application movements table and the fabric movements table, while the database object carries a different value than that fabric table, so the recorded divergence appears before the application layer and after the database object in the traced movement path.

Load accounting was unavailable: Audit response has malformed accounting or run timestamps.

Layers:
L0 - Movements in Application load fixture 20261003: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements
L1 - dbo.stock movements round two 20261003 in round two bronze 20261003: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003
L2 - app.stock movements round two 20261003 in ordersops: sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945

Limits:
- Unattested connection on L0 (receipt 0f0d6eea-b329-48b6-a50b-3e51146b0ee0).
- Unattested connection on L1 (receipt a7f614ff-e23b-4435-9ecb-375e9ebf398d).
- Unattested connection on L2 (receipt 15b007aa-feca-41c3-97f5-961b4252fd6e).
- SNAPSHOT_UNVERIFIED for B1, B2: the reads cannot be tied to matching data versions; agreement does not prove currency, and different update timing was not excluded as a cause of divergence.
- Checked through L2; stopped because capability not implemented.
- Quantities trace unchanged integral columns; joins may multiply rows and whole-row deduplication may remove them. Key uniqueness and intended grain are not established.

Recommended action: Ask the responsible owner to review the recorded missing evidence and next step.
```

## B3_CONSISTENT — exact outputs and probes
Intake `5fcabf1f-8924-4fe9-be7c-9fa66d1f79ac`; NEEDS_INPUT. No probes or comparisons; all intended boundaries untested.

business_output (verbatim):

```text
You asked: In Application load fixture 20261003, Movement Units shows 7,661 units. I expected a movement numbered 900099 that is absent from the authored application fixture. Please trace the displayed total to the application so I know whether this is a pipeline question or an application question.
Answer to your question: Not answered.

The investigation stopped during intake.
Reason: More than one ticket span could be the reported figure. Which figure should be compared?
No explanation of the reported difference was established.
Recommended action: Resolve the stated blocker before a new investigation.
```

technical_output (verbatim):

```text
You asked: In Application load fixture 20261003, Movement Units shows 7,661 units. I expected a movement numbered 900099 that is absent from the authored application fixture. Please trace the displayed total to the application so I know whether this is a pipeline question or an application question.
Answer to your question: Not answered.

The investigation stopped during intake.
Reason: More than one ticket span could be the reported figure. Which figure should be compared?
No explanation of the reported difference was established.
Recommended action: Resolve the stated blocker before a new investigation.
```

## B3_UNREACHABLE — exact outputs and probes
Intake `adbed9da-35ba-4407-8704-9530314b8555`; NEEDS_INPUT. No probes or comparisons; all intended boundaries untested.

business_output (verbatim):

```text
You asked: In Application load fixture 20261003, Movement Units shows 7,661 units. I expected a movement that is missing. Please establish what the pipeline faithfully received, with the application declared unavailable to this investigation.
Answer to your question: Not answered.

The investigation stopped during intake.
Reason: The required check could not be established. Its detailed blocker is retained in the technical explanation.
No explanation of the reported difference was established.
Recommended action: Resolve the stated blocker before a new investigation.
```

technical_output (verbatim):

```text
You asked: In Application load fixture 20261003, Movement Units shows 7,661 units. I expected a movement that is missing. Please establish what the pipeline faithfully received, with the application declared unavailable to this investigation.
Answer to your question: Not answered.

The investigation stopped during intake.
Reason: Report unavailable: NO_EXACT_MATCH; candidates: 
No explanation of the reported difference was established.
Recommended action: Resolve the stated blocker before a new investigation.
```

## Outcomes, limitations and honesty check

- E: B1 8,765/8,765 ENGINE_INDEPENDENT; B2 input 7,661/output 8,765
  OBJECT_DISTINCT. Stopped at the compatible transformation. Silver-to-Bronze
  and unresolved original source remain unchecked; no latency outcome.
- Gap: B1 7,661/7,661; B2 application 7,672/Bronze 7,661. Both cross-surface,
  qualified by missing connection/snapshot reports. NO_KNOWN_PATTERN because
  audit evidence is unavailable; source-version membership proof never ran.
- Latency: B1 7,661/7,661; B2 application 7,678/Bronze 7,661. Same qualification
  and audit barrier. NO_KNOWN_PATTERN, not LOAD_LATENCY.
- Consistency: the model/provider treats movement ID 900099 as an alternative
  figure to 7,661 units. NEEDS_INPUT, zero reads; no source-consistency evidence.
- Unreachable: model/provider emits a refused report binding for the semantic
  model's own name. NEEDS_INPUT, zero reads; configured termination not exercised.

The arithmetic did not call the engine/compiler or transcribe a served answer.
Mappings, stale serving, copy failures, attestation, intake, audit history and
validation could all defeat the intended outcomes—and several did. There was
no guaranteed match or outcome. No failed run was replaced or relabelled.

This round moves the observed reach from Bronze to the application, but earns
**none of INGESTION_GAP, LOAD_LATENCY, CONSISTENT_TO_SOURCE or the requested
live unreachable-source termination**. Offline tests establish contracts, not
those live outcomes. Intent, true expected-record completeness and snapshots
remain unknown. An agreeing total cannot prove an expected record exists.

Open findings, preserved rather than fixed during the batch:

1. An unorderable historical audit row blocks successful-completion history.
   New activity outputs contain 361/361 and 360/360, but the runtime SQL audit
   reads contain neither corresponding row. Direct Delta presence was not
   established; writer failure versus SQL serving lag is unresolved. Absence
   at the gap audit read (05:33:47.963836 UTC) was about six minutes after
   writer activity completion; this is an observed absence interval, not a
   measured synchronization lag.
2. Reportless intake remains vulnerable to a model-generated report binding.
   A labelled record identifier also becomes a reported-figure candidate.
   Neither ticket was changed or rerun to hide these failures.
3. Latency technical mechanism prose contradicts/obscures its deterministic
   spine ("aligned between the application movements table and the fabric
   movements table"). Schema/citation validation completed, but did not certify
   semantic truth. The business freshness header says history was not assessed
   despite a retained unavailable audit read; "capability not implemented" also
   misnames an implemented producer blocked by unavailable evidence. These
   output-accounting defects are visible in the quoted originals.
4. Token settlement and helper-level physical accounting can diverge from
   provider/reservation evidence. Corrections are appended, no counters edited.

## Load cost and both budgets

Two new pipeline runs: gap `293c0cd7-8f1f-4e74-8278-2dfafee4a04f`,
Completed 05:25:23.5280438–05:27:44.1166667 UTC, own copy **361/361**;
restoration `13ab6783-eeb2-4521-85f8-2ab6d74ab10e`, Completed
05:36:11.4265781–05:38:21.8933333 UTC, own copy **360/360**. Each child copy
reports **240,000 cpuCoreMs**. Both CopyApplication and RecordOwnAccounting
report an AzureIR billable duration of **0.016666666666666666 hours** each—two
external-activity billable minutes per pipeline, in addition to Spark compute
and retained Delta storage. This is reported metering, not a measured dollar or
capacity-CU charge. FTL4 trial unchanged; no priced estimate substitutes for
unobserved compute/storage usage. One additional fixture notebook run completed.

Part B **348/500** physical requests (including the appended six-request
accounting adjustment, which represents already charged subrequests, not new
calls). Final rolling ordinary usage **488/600**. Diagnostic cap **12 unchanged**;
no credits, resets, refunds, policy refills or deadline extensions. Baseline
reader verification used ten physical/four diagnostic/six guard requests.

## Part C — design only

See [inferred transformation bindings](inferred-transformation-binding-design.md).
It covers retained code collection, a closed proposal, exact scoped compilation,
attestation/refusal, visible INFERRED_FROM_CODE provenance and per-binding costs.
One disagreement is explicit: matching an unfiltered aggregate is a falsification
test, not proof of equivalence. No inference producer, new execution route or
SQL-view eligibility was implemented.
