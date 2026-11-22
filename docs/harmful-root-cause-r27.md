# Round 27 harmful root causes

Saved dev evidence only, reviewed before redesign code. All four original outcomes, grades and expectations remain unchanged. The inspected outcome files include case context, ordered decisions/queries and the delivered business answer; this is not a claim that every raw provider/network tape byte was replayed. No estate read or model call.

| Cohort / ticket | First wrong step | Classification |
|---|---|---|
| dev02 / R17-01-v1 | conclusion | wrong conclusion from correct evidence |
| dev02 / R17-05-v1 | target | wrong target picked |
| opus-calibration01 / R17-01-v1 | conclusion | wrong conclusion from correct evidence |
| opus-calibration01 / R17-02-v1 | target | wrong target picked |

## dev02 / R17-01-v1

Wrong conclusion from correct evidence: the measure/count question was answered with a categorical upstream join explanation. SUM(units) is not COUNT(records); an observed join expansion does not by itself answer why the named measure is called a count.

Saved outcome SHA-256: `c0000b139ce5d1d0e45a4684985e2634d95934735e59c5a9d49df87e956a4430`. Capture seal: `00513d461dc769d0767966e6282a935d6486121deda90ecd521ed23d657f75cd`.

Delivered answer excerpt:

> transformation logic. The unfiltered Handled Quantity measure reproduces 8765 and matches movement_values in warehouse_gold_e1b8e1. It sums units, rather than counting records. Stock movements in both warehouse_bronze_e1b8e1 and warehouse_silver_e1b8e1 total 7661 units. The retained Warehouse valuation e1b8e1 notebook joins movements to product rates on product_id only. Actual silver inputs contain two rate rows for product 7; its 46 movements total 1104 units, while gold contains 92 rows for those same 46 movements, totaling 2208 units. Recreating that join on silver returns 8765, explaining the extra 1104 units. This identifies the calculation mechanism, not whether it meets business policy. The last recorded model refresh succeeded on 2026-10-07 at 21:15:37.357 UTC and the refresh schedule is disabled; the separate Direct Lake automatic-update switch is unreadable. Current model/gold value agreement does not establish snapshot alignment or historical freshness. Definitions are retained, not freshly verified deployment definitions.

## dev02 / R17-05-v1

Wrong target picked: a similar card/model or inferred page displaced the user-named scope. Matching 8765 on another visual did not establish that it was the requested visual, and its filters changed the question.

Saved outcome SHA-256: `4325c849cd341b867469db46836dc77f20b7235ac5d852f3cbb1f3151f4064c4`. Capture seal: `6b5859b99c9cb3dab3975308a665a3fcf14dfcceae471342be489deacdea23ff`.

Delivered answer excerpt:

> different question. The reported 8765 matches Handled Quantity with no filters, in both Warehouse Operations e1b8e1 and the gold movement_values table. It does not match the selected card's retained page and visual predicates: Saved predicate selections restricts movement_type to RECEIPT, and Handled Quantity - extra visual predicate restricts event_day to 2026-09-15. Recreating those two predicates returns 665 in both the model and gold table. This establishes a filter-scope mismatch, not why the live screen showed the unfiltered total: current report-definition collection was unavailable, and live slicer/bookmark state was not established. Checks cover model and gold only, not the whole source chain or aligned snapshots. Refresh history records a successful refresh ending 2026-10-07T21:15:37.357Z and a disabled scheduled refresh; the Direct Lake automatic-update switch is unreadable. Those facts alone do not establish stale data.

## opus-calibration01 / R17-01-v1

Wrong conclusion from correct evidence: the measure/count question was answered with a categorical upstream join explanation. SUM(units) is not COUNT(records); an observed join expansion does not by itself answer why the named measure is called a count.

Saved outcome SHA-256: `42f0c2999e430fca9a73d50f3b73ee1dab3a27630d9de525da30442f08007a3a`. Capture seal: `e6bb1e1ff530e80691f7487e541a45f77ff98c68ffebde87eab51e5eb06cce3c`.

Delivered answer excerpt:

> transformation logic. The Handled Quantity card is showing the model's actual value. Running the measure (SUM('Activity'[units])) against the model gives 8765, the same as the ticket. The model table Activity reads Direct Lake from the gold table movement_values, where SUM(units) is also 8765. Upstream, the units total in stock_movements_e1b8e1 is 7661 in both silver and bronze. So the extra units first appear between silver and gold. The saved Warehouse valuation notebook builds movement_values with a LEFT join from silver stock_movements_e1b8e1 to silver product_rates_e1b8e1 on product_id only. In silver product_rates_e1b8e1, product 7 has 2 rate rows, so every product 7 movement appears twice in gold. Gold has 406 rows but only 360 distinct movement_ids. Product 7 movements total 1104 units in silver, and 7661 + 1104 = 8765. That means product 7's units are counted twice in the card. This finding is about where the extra units come from. Whether both rate versions should apply to each movement is a rule I have not judged. Not established: when the notebook last ran (job-run facts were unavailable). Also, the model's last recorded refresh succeeded at 2026-10-07T21:15:37Z, and the refresh schedule is disabled. The Direct Lake automatic-updates setting could not be read. Snapsho

## opus-calibration01 / R17-02-v1

Wrong target picked: a similar card/model or inferred page displaced the user-named scope. Matching 8765 on another visual did not establish that it was the requested visual, and its filters changed the question.

Saved outcome SHA-256: `7e9b2bccc93dfeb7d01e79f4a03c36d2def8100a4866a74bd0e7dacf08bbf51a`. Capture seal: `e508c6c08a385f71fdb330d5e5bf81ce0dcfc3496053a1040c9c61474b97f2dc`.

Delivered answer excerpt:

> transformation logic. The 8765 is reproduced exactly. In the model, Handled Quantity = SUM('Activity'[units]) returns 8765 with no filters, and the gold movement_values table also sums to 8765. The source movement tables do not match. Silver stock_movements_e1b8e1 sums to 7661, and so does bronze stock_movements_e1b8e1. The gap starts between silver and gold.

## Redesign obligations

B: Explicit report/page/visual choices constrain candidate enumeration through retained containment. Keep each candidate?s own filters. A unique value match may narrow only within that valid scope; equal numbers never authorize overriding an explicit choice. Ambiguous candidates remain side-by-side findings.

C: The conclusion carries a direct answer, the rule as implemented, the verdict class, evidence per layer and an explicit missing-fact statement. Definition/interpretation questions must distinguish the implemented aggregation from separate pipeline observations. A quantitative split is not automatically the cause of the user?s interpretation. Supported AS DESIGNED means correct under implemented logic, not approval of business intent.

Tests must exercise both classes generically with synthetic catalog identities and values, retain the wrong-cell and comparison-span regressions, and rerun the harmful public dev cases on the qualified image before freeze. Evidence-only phrasing changes do not erase a causal error.

## Pass2 partial recurrence, 2026-11-22UTC

The saved-output score at25 graded outcomes contains3 harmful answers. R17-01-v1 and R17-02-v1 reproduce the requested card at8765 and quote its additive SUM definition, then label an incidental Silver-to-Gold fan-out as a transformation DEVIATION. This substitutes an unasked numerical-cause question for verification of the named card. R17-05-v1 additionally selects the extra-visual-predicate card on Saved predicate selections instead of the named card's scope. Independent graders retain all three harmful flags; independent Terra reviews settle the R17-01 handoff disagreement and R17-05 target/handoff disagreement without curing the harm. These are not unsupported-data fabrications: the wrong conclusion or referent is attached to real query results. Freeze remains blocked until generic causes are fixed and safely rerun. No expectation, score or running pass2 image changed.

