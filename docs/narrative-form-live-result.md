# Narrative form: single live result

2026-09-28 UTC. #284 merged after all six checks passed at
`e60b54acede9100497282d72be3599f48029a30c`.

Session `778bcd6f-582f-4b5a-bef3-ed4f2cea15d6` completed as
TRANSFORMATION_LOGIC with validated synthesis. This was the single authorized
KNOWN_DOMAIN_REGRESSION run. No retry or second investigation was performed.
Engine/config/profile/policy/ticket hashes stayed unchanged during the run.

**Runtime completion is not full presentation acceptance.** The seven surface
fields are grouped once with receipts, the full layer identifiers appear once
in the legend, the divergent totals lead the output, and neither narrative
contains serialized structures. The business timing caveat is integrated into
its body. However, free model commentary and the retained judge limitation both
repeat snapshot uncertainty and unproved duplicate matches in addition to the
canonical limits. The tests covered duplicated generated blocks, not semantic
paraphrases across free prose. This remaining presentation defect is preserved
verbatim; no claim of complete non-repetition is made.

## Execution and limits

Two independent cross-surface comparisons completed: presentation/Gold agrees
at 8,765; Gold/Silver diverges at 8,765 versus 7,661. Both remain
SNAPSHOT_UNVERIFIED. The definition judge was called and interpreted a possible
join-multiplication mechanism. Actual repeated matches, aligned snapshots and
intended business rules are unproved. Silver/Bronze was not checked after the
procedure terminated; the application-source binding remains unresolved.

One intake call, one investigation definition-judge call and one synthesis call
completed. Four diagnostic operations reached the unchanged cap of four:
one Power BI quantity, two Fabric SQL quantities and an endpoint metadata lookup.
Ten physical requests completed: one Power BI request, eight SQL requests (two
quantities and six guards), and one metadata request. Guard reuse was zero;
the SQL reads addressed different database/object scopes. No request failed.

## Approved credits and usage

The user approved ten physical-request credits for one run only, with two-hour
expiry. Batch `G-narrative-form-R1-20260927-credits` was scoped to this session.
Before/granted/after control-plane readbacks and the exact approval are retained
under `.local/narrative-form-20260927/`.

- Granted: 10; charged: 10; remaining: 0.
- Expiry: 2026-09-28T05:15:42.406944+00:00.
- Diagnostic use/cap: 4/4. Ordinary rolling allowance stayed 60.
- Rolling ordinary charged: 77 before and after; ordinary available: zero.
  All new requests used the approved batch. Historical counters were preserved.

Exactly one live ledger row was appended. The recorded tapes are
`0e2f88b3-4bf5-483d-b38f-9e4b6f955101`,
`55917e86-763c-46af-9ebc-52337ec2389a`, and
`c7f99d6f-4727-42b2-bb4c-8ecf08a1e958`.
The engine fingerprint is `d33b2685ea14fc44b2153b80e070d000731055f17fcb8ab295c4ddaae1a930af`.
No engine or policy change followed the result. The merged implementation had
1,311 passing local regression tests and six green CI checks. This documentation
change made no further cloud calls and did not rerun that suite.

## Business output ? verbatim

```text
The report showed 8,765 for movements, matching the total used to prepare it. An earlier check of movements returned 7,661; the difference appears in the step that matches movements with rates. Several matching rates can cause an entry to contribute more than once. We have not confirmed the repeated matches, whether the checks describe the same moment, whether this matching rule is intended, or how movements were first entered. Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.
```

## Technical output ? verbatim

```text
Measure: Handled Quantity.
B2 diverges: L2 (stock movements e1b8e1, upstream input) 7,661 -> L1 (movement values, downstream output) 8,765.
B1 agrees: L1 (movement values, upstream input) 8,765 -> L0 (Activity, downstream output) 8,765.

The implemented logic joins movements with rates by product_id before deriving movement_value from units and unit_cost. Because uniqueness on that key is not assumed, one movement can match several rates and its units can be repeated in the joined result, which can raise the summed quantity. This explains the aggregate gap between the compared layers, but it does not show that repeated matches occurred in the checked data, that both reads reflect the same snapshot, or that this rule matches business intent.

Layers:
L0 - Activity: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity
L1 - movement values: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values
L2 - stock movements e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1
L3 - stock movements e1b8e1: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1

Limits:
- Unattested connection, engine, object on L0 (receipt 69ee4e50-d281-4df6-b752-d1cd0d1b8741).
- Unattested connection, engine on L1 (receipt 81755b52-3393-4e38-afb5-70e431bb6ea6).
- Unattested connection, engine on L2 (receipt b89ea49f-fa67-4e4f-9d2b-9a194abe2f43).
- SNAPSHOT_UNVERIFIED for B1, B2: the reads cannot be tied to matching data versions; agreement does not prove currency, and different update timing was not excluded as a cause of divergence.
- Checked through L2; stopped because reached.
- Unchecked L2 -> L3: Investigation terminated before this boundary.
- Unchecked L3 -> unresolved upstream: No declared upstream read for this quantity (literal initialization or derived/unsupported column).
- Quantities trace unchanged integral columns; joins may multiply rows and whole-row deduplication may remove them. Key uniqueness and intended grain are not established.
- This explanation depends on duplicate matches on the join key in the joined input. The definition shows multiplication is possible, but it does not establish whether such duplicate matches actually occurred in the compared data or whether both sides use the same snapshot.

Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.
```
