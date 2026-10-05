# Exact-span recovery, budget replay and source consistency

2026-10-05 UTC. Implementation PRs #399 and #400 merged with six green checks each. Prior freezes invalidated. No fresh variant or unfamiliar-domain acceptance claimed.

## Final column

All fifteen preserved tapes were graded with zero estate reads and zero model calls: **13 passed, one blocked, one failed**. The newly authorized source run then passed its separate byte-exact replay. Selected evidence is **14/15**, not a new full fifteen-case sweep or a single-engine acceptance claim. Historical producers remain pinned to their separately recorded revisions.

| Case | Preserved-tape grade | Final selected grade |
| --- | --- | --- |
| family-A | PASSED | PASSED |
| family-B | PASSED | PASSED |
| family-C | PASSED | PASSED |
| family-D | PASSED | PASSED |
| family-E | PASSED | PASSED |
| family-F | PASSED | PASSED |
| family-G | PASSED | PASSED |
| family-H | PASSED | PASSED |
| family-I | PASSED | PASSED |
| reproduction-16 | BLOCKED | BLOCKED |
| reproduction-empty | PASSED | PASSED |
| source-consistent | FAILED | PASSED |
| source-gap | PASSED | PASSED |
| source-latency | PASSED | PASSED |
| source-unreachable | PASSED | PASSED |

Numeric reproduction remains blocked. An isolated zero-network diagnostic retained the first mismatch: PROVIDER_REQUEST ordinal 2557. The provider input has identical structured content but different cell_display_names map order. The historical producer creates its target set without sorting and iterates that set. The later finally settlement originally masked this with BUDGET versus PROVIDER_RESPONSE. Budget decision matching does not authorize relaxing provider-body byte equality. Original tapes, source files and earlier passing/blocked grades remain unchanged. #376 remains draft; its 15/15 merge condition is unmet.

Accounting v2 is dated retrospectively to #393 (`7abaabf37812b58cc74b684de9cafc172212c1ad`), with physical guard/control accounting and bounded resume as the reason. Recorder v3 seals accounting_version 2; legacy tapes are untouched. BUDGET comparisons preserve every decision/count/field while decoding reserved/actual count-map serialization. Provider bodies and physical requests remain byte-exact. Archived producers use this versioned budget consumer. First transport mismatches are retained instead of masked by later settlement.

## Live source run

**a96e0ca5-0266-439d-a72f-c83a99b505b1 ? CONSISTENT_TO_SOURCE.** Fixture-authored unchanged ticket; approved source-baseline, context d48aa1d0-f692-44ed-969c-083c6d3df49f, SHA-256 e284a33adec25f6aeb592adca76b88ed30f48e4596ef7dacd7f70cb99d0c05a0. Config SHA-256 56dfa9aeab17f133b68ddfcc3761cf50d529eefdd10d4c3bfa22657fa73cf821. Recorded engine revision 75493590ad72c64dde179b922181ce2528631350; tape v3.

Intake accepted SOURCE_CORRECTNESS on its first call, with expected record 900099, no filter/grouping and no selection target. The new retry was therefore not exercised live; its success/refusal/metering paths were tested offline. No causal claim that the retry made this first response valid.

| Probe | Surface / reader | Value or membership | Attestation | Receipt |
| --- | --- | --- | --- | --- |
| Membership | OLAP Server / 0c89889c-6fe6-49ab-91e9-4b00a51070e6 / investigator-reader@skynwhy.com | 900099 absent | PARTIAL: engine, object, identity match; connection unattested | b9c343ae-162d-4129-8fb3-be6a2789246d |
| Quantity | OLAP Server / 0c89889c-6fe6-49ab-91e9-4b00a51070e6 / investigator-reader@skynwhy.com | 7,661 | PARTIAL: engine, object, identity match; connection unattested | 7f04bc07-0bef-4ecf-94ed-d691421dd82a |
| Membership | Microsoft Azure SQL Data Warehouse / round_two_bronze_20261003 / investigator-reader@skynwhy.com | 900099 absent | PARTIAL: engine, object, identity match; connection unattested | 4a447bb7-bc94-41a3-aa8a-21229bac25de |
| Quantity | Microsoft Azure SQL Data Warehouse / round_two_bronze_20261003 / investigator-reader@skynwhy.com | 7,661 | PARTIAL: engine, object, identity match; connection unattested | 75707f75-cdbb-4584-8854-be91bdac6342 |
| Membership | Microsoft SQL Azure / ordersops / orderops_investigator | 900099 absent | PARTIAL: engine, object, identity match; connection unattested | 3b0d562e-58ed-4f12-bc6e-3461e51726c9 |
| Quantity | Microsoft SQL Azure / ordersops / orderops_investigator | 7,661 | PARTIAL: engine, object, identity match; connection unattested | ab18cb6d-0b97-41cc-96a8-5bc77fc42e41 |

Both boundaries were compared: semantic model ? landing, and landing ? application. Both are ENGINE_INDEPENDENT cross-surface comparisons with equal 7,661 quantities. None is fully surface-verified or snapshot-verified: connection remains unattested on each surface; both comparisons are SNAPSHOT_UNVERIFIED. No within-layer reproduction was attempted. The declared source was reached, so no lower boundary was skipped. Optional refresh timing remains unavailable to the reader; report reproduction is undeclared for model-only context.

Six diagnostic reads / cap twelve: two semantic DAX, two landing SQL, two application SQL. Fourteen physical requests: two DAX, four SQL value/membership queries, four SQL identity checks, two database-permission checks, two object-permission checks. Eight overhead guards; four permission-check reuses; zero connection-retry requests inside the investigation. Intake one, investigation planner zero, definition judge zero, synthesis one. Synthesis COMPLETED and validated; v3 byte-exact replay PASSED with zero network requests.

The claim establishes observed unchanged quantities and independently observed absence through this declared path for one fixture-authored known-domain ticket. It does not establish business correctness, complete source contents, key uniqueness/intended grain, shared snapshots or currency. The action points to the application owner. No fixture data, identity, permission, scope, cap or policy changed.

## Controls and both budget windows

Pre-warm: first connect failed SQL40613, then a recorded five-second resume wait, then connection success. Two physical controls and zero diagnostic reads. Pot 247?249/400. Resume started 2026-10-05T05:49:19.898489Z and completed 2026-10-05T05:49:24.900214Z.

A private harness path typo caused FileNotFoundError before intake or any investigation read. That zero-read/zero-model-call setup failure is preserved separately in the ledger; only its local case path was corrected. Exactly one actual investigation was submitted.

Investigation pot 249?263/400; restoration reserve 50, usable remainder 87. Batch total sixteen physical requests including the two controls. Rolling ordinary allowance before investigation 384/1500, after 396/1500 over 86400 seconds. Fourteen new run requests were charged; two older requests aged out during the run. No reset or refund. Diagnostic cap twelve unchanged; actual six.

## Business output ? verbatim

```text
You asked: In Application load fixture 20261003, Movement Units shows 7,661 units. I expected a movement numbered 900099 that is absent from the authored application fixture. Please trace the displayed total to the application so I know whether this is a pipeline question or an application question.
Answer to your question: Answered within the checked scope.
Regarding whether the application information was delivered: The compared path agreed through the declared application source, with the requested record membership checked. The remaining expectation belongs to the application owner; currency is not established.
What the investigation established:

The checked reported calculation value was 7,661. Every checked step agreed with the application that the system owner declared authoritative. These comparisons found no delivery difference; they do not establish that the application contains every expected entry. The record you named was absent at every checked layer: reported calculation, landing table and application. The checks do not establish whether they describe the same moment or whether the original entries are correct. For the reported calculation and the landing table, the two checks used different calculation engines. For the landing table and the application, the two checks used different calculation engines. Recommended action: Ask the application owner about the expected entry; an entry absent from the application is not a delivery problem in the checked process.
```

## Technical output ? verbatim

```text
You asked: In Application load fixture 20261003, Movement Units shows 7,661 units. I expected a movement numbered 900099 that is absent from the authored application fixture. Please trace the displayed total to the application so I know whether this is a pipeline question or an application question.
Answer to your question: Answered within the checked scope.
Regarding whether the application information was delivered: The compared path agreed through the declared application source, with the requested record membership checked. The remaining expectation belongs to the application owner; currency is not established.
What the investigation established:

Measure: Movement Units.
B1 agrees: L1 (dbo.stock movements round two 20261003 in round two bronze 20261003; role LANDING, upstream input) 7,661 -> L0 (Movements in Application load fixture 20261003; role SEMANTIC, downstream output) 7,661.
B2 agrees: L2 (app.stock movements round two 20261003 in ordersops; role APPLICATION, upstream input) 7,661 -> L1 (dbo.stock movements round two 20261003 in round two bronze 20261003; role LANDING, downstream output) 7,661.
ENGINE_INDEPENDENT: comparable quantity-bound engine self-reports differ; this is an engine-independent cross-surface comparison. (receipt boundary-1-comparison).
ENGINE_INDEPENDENT: comparable quantity-bound engine self-reports differ; this is an engine-independent cross-surface comparison. (receipt boundary-2-comparison).
Declared-context reproduction unavailable: Declared-context reproduction is undeclared for model-only or layer-only named context.

The measure total at L0 (SEMANTIC) matches the total at L1 (LANDING), and the total at L1 (LANDING) matches the total at L2 (APPLICATION). The recorded checks therefore trace the displayed measure through those layers without a change in the counted quantity.

Presence checks: the record you named was absent in L0 (SEMANTIC, reported calculation); the record you named was absent in L1 (LANDING, landing table); the record you named was absent in L2 (APPLICATION, application).

Layers:
L0 - Movements in Application load fixture 20261003; role SEMANTIC: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements
L1 - dbo.stock movements round two 20261003 in round two bronze 20261003; role LANDING: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003
L2 - app.stock movements round two 20261003 in ordersops; role APPLICATION: sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945

Limits:
- Unattested connection on L0 (receipt 7f04bc07-0bef-4ecf-94ed-d691421dd82a).
- Unattested connection on L1 (receipt 75707f75-cdbb-4584-8854-be91bdac6342).
- Unattested connection on L2 (receipt ab18cb6d-0b97-41cc-96a8-5bc77fc42e41).
- SNAPSHOT_UNVERIFIED for B1, B2: the reads cannot be tied to matching data versions; agreement does not prove currency, and different update timing was not excluded as a cause of divergence.
- Checked through L2; stopped because reached.
- By configuration, these checks cannot establish which data versions they read.
- By configuration, the calculation account cannot report its connection.
- Quantities trace unchanged integral columns; joins may multiply rows and whole-row deduplication may remove them. Key uniqueness and intended grain are not established.

Recommended action: Ask the application owner about the expected entry; an entry absent from the application is not a delivery problem in the checked process.
```

Tests: seven intake retry tests, thirteen quote-provenance tests, thirty-six intake tests, five budget-contract tests and twenty-six tape tests passed. Tape golden coverage unchanged: two directory entries, one SQL object, 7,540 payload characters. All failures and original ledger rows preserved; no replacement investigation.
