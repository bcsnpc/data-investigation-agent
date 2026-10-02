# First declared-context estate attempt: fixture and integration blockers

Date: 2026-10-02 UTC. Engine main: `e2c7235` (#295 and #296 merged).
This is a partial PR3 record, not reproduction acceptance. One of three requested
runs was attempted; the two authored-figure tickets were not executed. No engine,
adapter, estate, policy, allowance, credit, or discovery change was made.

## Independent figure derivation

The evaluator inspected the seeded Bronze rows retained in the notebook definition,
not a compiled investigator query. The retained notebook contains the same relevant
movement rows as the original publisher input. The publisher input differs in its
rate rows from the retained notebook; the authoritative derivation uses the retained
notebook seed, not that older rate payload. This difference cannot create a matching
row under the active filters. The notebook content SHA-256 is
`3a980c4bd1920343202174c26b357be6233c6db267409d226d6a95fca4694273`.

The independently applied rules are: whole-row deduplication into Silver; a Gold
left join to all product-rate matches on product_id, repeating units for each match;
and the measure `SUM('Activity'[units])`. No investigator query/compiler was run to
author a figure.

The full active set is:

- page: movement_type = RECEIPT;
- visual: event_day = 2026-09-14;
- saved location slicer: warehouse_name = North (warehouse_id 1);
- saved product slicer: product_name = Component 1 (product_id 1).

Before the RECEIPT predicate, the only matching seeded row is movement 300:
`[300, 1, 1, 9, "2026-09-14", "ISSUE"]`. The page predicate excludes it.
There are therefore no qualifying Bronze rows, no qualifying joined Gold rows,
and no nonblank units for the measure to sum. The independently expected measure
result is BLANK, not a numeric zero. This is an expectation from seed/definition,
not an observed live quantity. Microsoft documents explicit blank-to-zero conversion
with [COALESCE(SUM(...), 0)](https://learn.microsoft.com/en-us/dax/coalesce-function-dax);
the actual measure has no conversion, and reproduction preserves blank separately
from numeric zero.

The first preparation script's Python sum of an empty list returned zero and
created candidate texts with 0 and 1. That preparation error is preserved locally,
with a dated correction: neither candidate was used in an investigation. Zero
cannot honestly be presented as a numeric reproduction figure for this fixture.
The numeric-reproduction requirement therefore needs a fixture or acceptance
change before Ticket 1 can be authored correctly. Ticket 2 was also left unrun,
rather than presenting an incomplete pair as the requested batch.

A possible bounded fixture change, NOT made or authorised here, is to change the
target visual's day predicate to 2026-09-15. Under the same page and both saved
slicers, movements 10 (4 units) and 238 (12 units) qualify; Component 1 has one
rate row, so the independent quantity is 4 + 12 = 16. Publication, collection and
current discovery approval would need to be established again. Neither model nor
data needs changing. This is a proposal, not a published fixture or live result.

## Actual unchanged family D run

Run `6582f4a1-e8a0-4bb1-b8a3-c41286fa4e12` used family D's original ticket byte-for-byte.
It completed with NO_COMPARABLE_PATH and validated synthesis, but it DID NOT reach
the required no-reported-figure unavailability. Its reproduction check instead
reported `DECLARATION_INVENTORY_CONTRACT`: "Required declaration inventory missing
or malformed". No declared-context verdict or PRESENTATION_LOGIC finding exists.

A local extraction audit, without data reads, exposes the underlying prerequisite:
AMBIGUOUS_OR_MISSING_DECLARATION_TARGET, with five matching visual parts across the
retained reports. The runtime does not carry a definition target into vertical(),
and also does not carry the reported figure. The inventory validator runs before
checking this prerequisite refusal, masking its more useful reason. These are
integration/feedback findings, not evidence of an unsupported native predicate
inside a constructed inventory. No code was changed to obtain a pass.

Inventory totals/dispositions and conservation confirmation are N/A for this run:
extraction refused before constructing the inventory. The earlier extraction-only
4 ACTIVE / 5 CONDITIONAL fixture audit must not be reported as this live run's
engine-confirmed inventory. No active set entered reproduction. The restricted
and undeclared-context reproduction probes did not execute; both values are N/A.
The ticket had no numeric reported figure.

The only data probe was the ordinary warehouse-North presentation baseline:
3359, POWER_BI_DAX, connection `149f8d99-1c66-4a0a-9624-759be002bb60`, model
`3484a2bc-98c5-4cef-be5c-a6215484075e`, reader
`investigator-reader@skynwhy.com`. Receipt `c555aad1-048a-427a-9bbe-442e3741045a`
self-reported identity MATCHED. Engine, connection and object were unattested.
It was not a cross-surface comparison. Every lower filtered boundary remained
NOT_COMPARABLE; the existing refusal was preserved.

Accounting: one DAX physical request, one diagnostic operation against cap 4,
zero SQL/metadata requests, zero guards/reuse, zero investigation planner calls,
one intake call and one synthesis call. Synthesis COMPLETED/validated. The rolling
ordinary allowance was 60 with 53 available before the run; one was charged.
No credits were granted and no cap was raised. One ledger row was appended from
receipts. Original payloads, responses, run state and outputs remain unchanged.

The reproduction assumed-slicer qualification and non-reproduction moved-slicer
open set were NOT exercised. The honesty check cannot claim a first-attempt match:
no reproduction attempt has occurred. A genuine future test could fail on stale
or changed data, incorrect relationship/selection propagation, join multiplicity,
compiler translation, mismatched target, or an arithmetic error; no served value
was transcribed into the authored candidates.

## Verbatim business output

```text
You asked: In Inventory Health e1b8e1 I selected warehouse North. Handled Quantity differs from the global total. Check the North selection and explain what report context you can and cannot reproduce.
Answer to your question: Not answered.
Regarding the requested comparison: No independent comparison established an answer to the requested difference.
What was found instead:

The declared selections could not be tested with the available evidence. The checked report value was 3,359. The available evidence did not establish an independent comparison with the total used to prepare the report. A difference between the report and its input therefore remains possible. The original entries, unchecked selections, update timing and intended business rules remain outside what these comparisons establish. Recommended action: Ask the system owner to provide the missing connection information or read access identified in the limits.
```

## Verbatim technical output

```text
You asked: In Inventory Health e1b8e1 I selected warehouse North. Handled Quantity differs from the global total. Check the North selection and explain what report context you can and cannot reproduce.
Answer to your question: Not answered.
Regarding the requested comparison: No independent comparison established an answer to the requested difference.
What was found instead:

Measure: Handled Quantity.
No independently compared boundary was established.
Declared-context reproduction unavailable: Required declaration inventory missing or malformed

A direct query applied the selected warehouse value through a filter on the warehouse name column, evaluated the measure, and returned one row containing the measure result. The query also appended the current principal name as surface identity for that observation.

Layers:
L0 - Activity in Warehouse Operations e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity
L1 - movement values in warehouse gold e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values
L2 - stock movements e1b8e1 in warehouse silver e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1
L3 - stock movements e1b8e1 in warehouse bronze e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1

Limits:
- Checked through L0; stopped because capability unavailable.
- Unchecked L0 -> L1: Declared source comparison does not yet translate filtered scope faithfully..
- Unchecked L1 -> L2: Declared quantity trace supports only whole-entity scope without filters or grouping..
- Unchecked L2 -> L3: Declared quantity trace supports only whole-entity scope without filters or grouping..
- Unchecked L3 -> unresolved upstream: No declared upstream read for this quantity (literal initialization or derived/unsupported column).
- Quantities trace unchanged integral columns; joins may multiply rows and whole-row deduplication may remove them. Key uniqueness and intended grain are not established.

Recommended action: Ask the system owner to provide the missing connection information or read access identified in the limits.
```
