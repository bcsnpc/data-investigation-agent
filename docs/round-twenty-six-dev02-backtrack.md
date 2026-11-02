# Dev pass2 backtrack

Dev02 only; saved outcomes and ordered logical case checkpoints, not raw provider/network tapes. No new estate or model calls. Backtrack analysis is separate from independent grading.

Primary5/30; secondary5/30; strict4/30; reviewed evidence-projection5/30. The independent reviewed harmful count is2. All original grades remain. R17-01 is included despite its original primary pass.

First-step labels below come from saved input/result data and ordered persisted logical messages. They are not copied blindly from the primary grader: for example R17-09 did contain the refresh facts, and waiting did identify the right job. A recoverable first rejection is distinguished from the later delivery failure. UNKNOWN_REPORT is retained as a malformed-input/catalog mismatch, not silently repaired.

| Case | First observed step | What went wrong | Correct action |
|---|---|---|---|
| form-v2-warehouse-scope-v2 | intake | The supplied opaque report address was not found in the retained catalog (UNKNOWN_REPORT). No investigation started. | Keep this malformed-input result separate; do not silently repair the sealed form or substitute another report. |
| form-v2-billing-invoices-v1 | query | First native measure read timed out. Later source/join reads did not produce a validated final answer; the submission cited a failed query. | Retain the transport failure, use successful evidence separately, and return the partial per-layer findings and remaining check. |
| form-v2-before-temporal-retention-v1 | query | Turn2 metadata was refused before dispatch (National/ObjectId); turn3 sys catalogs were outside the old table binder. | Allow read-only metadata, establish the earliest retained time with native evidence, and explain why the requested earlier state cannot be reconstructed. |
| form-v2-other-collected-definition-v1 | query | Turn2 valid native-style EVALUATE with ORDER BY was refused by the limited grammar. The corrected query succeeded; the last submission then used an uncited3. | Use a supported native read or extend its read-only grammar; distinguish returned-row counts from native scalar cells and retain the actual calculation in the handoff. |
| form-v2-source-history-v1 | tool choice | Turn3 requested lineage without a valid node and attempted a sys catalog query the old binder refused. History later succeeded, but the last finding included uncited6. | Use the exact source node, permit native metadata, cite the retained history and return established values even if the causal submission is rejected. |
| text-R17-01-v1 | conclusion | Turn4 submitted transformation logic as the answer to the measure-interpretation question. Native join arithmetic did not make that the requested semantic verdict. | Lead with SUM(units) versus a record count and its limits. Keep any independently observed upstream divergence separate from the explanation of the asked calculation. |
| text-R17-04-v1 | intake | The run stopped before technical investigation, asking for report. | Check the native named-container/metric candidates within the cap and retain every measured result; ask only if the target remains unresolved. |
| text-R17-05-v1 | target | A loose measure/card reference was treated as a specific visual on a model-inferred page with extra retained predicates. | Resolve across the named report unless the user actually names a page; check actual candidate scopes or ask grounded visual choices without inventing a page selection. |
| text-R17-08-v1 | intake | The run stopped before technical investigation, asking for report. Its bounded measure checks did not uniquely resolve the target; this is not evidence of a harmful invented finding. | Check the native named-container/metric candidates within the cap and retain every measured result; ask only if the target remains unresolved. |
| text-R17-09-v1 | conclusion | The saved answer did include the native refresh end and disabled schedule, contrary to the primary reason; its observed-value verdict still did not establish the expected verdict. | Separate what is established by native refresh facts from what remains unverified and state the supported verdict with a concrete handoff. |
| text-R17-10-v1 | intake | The run stopped before technical investigation, asking for report. | Check the native named-container/metric candidates within the cap and retain every measured result; ask only if the target remains unresolved. |
| text-R17-11-v1 | conclusion | The answer explained SUM and a join, but did not make unknown physical/business meaning its main conclusion. | State that intended meaning is not established by SUM, retain the technical definition separately, and route the meaning decision to the business owner. |
| text-baseline-S02-v1 | write-up | Turn5 attempted the finding with250 not present as a literal scalar in its cited successful results. | Cite the actual boundary/join values; measure or explicitly support a derived difference before placing it among native scalar numbers. |
| text-different-warehouse-v2 | intake | The run stopped before technical investigation, asking for report. | Check the native named-container/metric candidates within the cap and retain every measured result; ask only if the target remains unresolved. |
| text-older-export-movement-1-v1 | intake | The run stopped before technical investigation, asking for report. | Check the native named-container/metric candidates within the cap and retain every measured result; ask only if the target remains unresolved. |
| text-older-export-movement-1-v2 | intake | The run stopped before technical investigation, asking for report. | Check the native named-container/metric candidates within the cap and retain every measured result; ask only if the target remains unresolved. |
| text-history-source-900201-v1 | tool choice | Turn4 attempted temporal history on a warehouse Bronze object, not the declared application temporal table. | Activate the exact already-authorized application source and read its retained history; current absence in warehouse snapshots does not answer an older-export question. |
| text-history-source-900201-v2 | tool choice | Turn4 attempted history on the warehouse object, then replaced the requested historical explanation with current key absence. | Read the declared source history at the relevant times before concluding; preserve current absence as a separate observation. |
| text-latency-900501-v1 | intake | The run stopped before technical investigation, asking for report. | Check the native named-container/metric candidates within the cap and retain every measured result; ask only if the target remains unresolved. |
| text-latency-900501-v2 | intake | The run stopped before technical investigation, asking for table. | Check the native named-container/metric candidates within the cap and retain every measured result; ask only if the target remains unresolved. |
| text-latency-900502-v1 | intake | The run stopped before technical investigation, asking for table. | Check the native named-container/metric candidates within the cap and retain every measured result; ask only if the target remains unresolved. |
| text-latency-900502-v2 | target | Intake chose an unrelated report for a ticket naming application rows and a specific Bronze container. It later established present/absent but not the load cause. | Bind the literal native container/table before choosing a report; use the correct path run/schedule and temporal evidence to decide latency. |
| text-access-export-1-v1 | intake | The run stopped before technical investigation, asking for table. | Check the native named-container/metric candidates within the cap and retain every measured result; ask only if the target remains unresolved. |
| text-access-export-1-v2 | intake | The run stopped before technical investigation, asking for table. | Check the native named-container/metric candidates within the cap and retain every measured result; ask only if the target remains unresolved. |
| text-waiting-fixture-load-v1 | triage | The native-status fast path correctly found the running job, but did not establish the specific Wait-control cause required by the unchanged expectation. | Keep the running verdict and literal run details; explicitly hand off the unchecked reason instead of claiming the Wait activity was observed. |

Counts by first step: {"intake": 12, "query": 3, "tool choice": 3, "conclusion": 3, "target": 2, "write-up": 1, "triage": 1}.

## R17-01 harmful conclusion, retained verbatim

Primary: correct, harmful false. Secondary and the separate independent review: incorrect, harmful true. The operator does not replace that adjudication. The native observations remain valid observations; the issue is promoting a different causal explanation to the answer to the asked semantic question.

DIA business answer:

> transformation logic. The unfiltered Handled Quantity measure reproduces 8765 and matches movement_values in warehouse_gold_e1b8e1. It sums units, rather than counting records. Stock movements in both warehouse_bronze_e1b8e1 and warehouse_silver_e1b8e1 total 7661 units. The retained Warehouse valuation e1b8e1 notebook joins movements to product rates on product_id only. Actual silver inputs contain two rate rows for product 7; its 46 movements total 1104 units, while gold contains 92 rows for those same 46 movements, totaling 2208 units. Recreating that join on silver returns 8765, explaining the extra 1104 units. This identifies the calculation mechanism, not whether it meets business policy. The last recorded model refresh succeeded on 2026-10-07 at 21:15:37.357 UTC and the refresh schedule is disabled; the separate Direct Lake automatic-update switch is unreadable. Current model/gold value agreement does not establish snapshot alignment or historical freshness. Definitions are retained, not freshly verified deployment definitions.
> Numbers: 8765, 7661, 1104, 7, 2, 46, 92, 2208.
> Checked: warehouse_bronze_e1b8e1, warehouse_silver_e1b8e1, warehouse_gold_e1b8e1, Warehouse Operations e1b8e1.
> Native comparisons are observational snapshots; aligned query-bound versions are not established.
> Catalog bookkeeping unavailable: collector containment (recovered from literal native address), current inventory availability, inventory content hashes (metadata digests are derived and labelled), inventory provenance, per-asset collector timestamps. This does not block investigation; successful queries establish present readability only.
> attestation limited: the engine can’t self-report the calling principal; the token and connection were verified separately

## Five additional trace points

### text-latency-900501-v1

The run stopped before technical investigation, asking for report. Check the native named-container/metric candidates within the cap and retain every measured result; ask only if the target remains unresolved.

Outcome SHA-256: `bdab991cbaefb38398d02a242e228c08685a90ad8b1c1a66e3631309f41a606a`. No investigator checkpoint exists because intake did not admit a case.

### text-R17-05-v1

A loose measure/card reference was treated as a specific visual on a model-inferred page with extra retained predicates. Resolve across the named report unless the user actually names a page; check actual candidate scopes or ask grounded visual choices without inventing a page selection.

Outcome SHA-256: `4325c849cd341b867469db46836dc77f20b7235ac5d852f3cbb1f3151f4064c4`. No investigator checkpoint exists because intake did not admit a case.

### form-v2-before-temporal-retention-v1

Turn2 metadata was refused before dispatch (National/ObjectId); turn3 sys catalogs were outside the old table binder. Allow read-only metadata, establish the earliest retained time with native evidence, and explain why the requested earlier state cannot be reconstructed.

Outcome SHA-256: `b2d1a367b8f884e6fbd3d315348960540f171cf5c07136eb28548d757fd16c90`. No investigator checkpoint exists because intake did not admit a case.

### form-v2-other-collected-definition-v1

Turn2 valid native-style EVALUATE with ORDER BY was refused by the limited grammar. The corrected query succeeded; the last submission then used an uncited3. Use a supported native read or extend its read-only grammar; distinguish returned-row counts from native scalar cells and retain the actual calculation in the handoff.

Outcome SHA-256: `afd38f3b4055ec05bf6655c93f2a41ca40efb7050649987a186a656b05821983`. No investigator checkpoint exists because intake did not admit a case.

### text-history-source-900201-v1

Turn4 attempted temporal history on a warehouse Bronze object, not the declared application temporal table. Activate the exact already-authorized application source and read its retained history; current absence in warehouse snapshots does not answer an older-export question.

Outcome SHA-256: `1546ea099eea8dd7d66f02440e27bff78a591895e18354968bfc0bf4c4631dbc`. No investigator checkpoint exists because intake did not admit a case.

