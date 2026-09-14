# Local classification evaluation matrix

Run `python scripts/evaluate_lab_matrix.py`. The command creates a fresh UUID directory under
.local/lab-evaluations, saves report.json and retains each case's lab/evidence databases.
An optional --output selects a new directory; existing directories are never overwritten.
Exit status is nonzero if any observed result or reset fails.

| Case | Expected classification | USD difference |
| --- | --- | ---: |
| Matching without business context | UNRESOLVED | 0 |
| Complete capture/refund explanation | EXPECTED_BEHAVIOR | 0 |
| Output omission without cause proof | UNRESOLVED | -99 |
| Verified filter build | TECHNICAL_DEFECT | -99 |
| Verified stale refund source | REFRESH_FRESHNESS | +99 |
| Missing filter receipt | UNRESOLVED | -99 |
| Changed filter receipt | UNRESOLVED | -99 |
| Unexplained Gold value change | UNRESOLVED | +10 |
| Incomplete business context | UNRESOLVED | 0 |

The expected answers live only in the evaluator. Investigation receives the normal business
evidence projection, optional business context and the existing verifier. It does not receive
case names or expected classifications. The report checks exact classification, monetary
difference, affected-record count, verified-cause flag and disabled automatic routing.
Each case uses its own fresh database and resets before completion. Evidence run IDs remain
available for audit even though the lab output is reset.

This is a regression matrix for supported deterministic local behavior, not an independent
blind benchmark, LLM evaluation or cloud acceptance test. It adds an unexplained value-change
case and consolidates existing positive/evidence-gap cases into one report. All data comes
from the three-order fixture; the live 100,000-order baseline is untouched. Passing sets
passed=true while product_acceptance remains false.

Broader application/ingestion/Silver/model/report defects, multiple currencies and business
rules, live snapshot guarantees, richer agent tool selection and full ticket-to-delivery
acceptance remain outside this matrix.
