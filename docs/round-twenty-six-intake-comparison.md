# Round 26 intake diagnostics

| First-leg model | Ready | Actual USD/call | Cached input |
|---|---:|---:|---:|
| Astra | 28/40 | 0.123874 | 18.37% |
| Terra | 21/40 | 0.010282 | 86.74% |
| Sol | 28/40 | 0.024139 | 88.04% |

Selected: Sol, by readiness then actual cost. These are observed cohorts on different engine revisions, not a controlled attribution of quality to the model. Eight operational routes per cohort made no model call. A later Terra cohort (retained separately) reached 19/40.

Sol plus one Astra fallback pass reached 29/40, cost $7.733820 total, 13 fallback tickets, zero estate reads. The original interrupted Sol attempt remains recorded and charged; its labelled replacement is included once in readiness. No expectation or original tape was rewritten.

Machine-readable receipts: [comparison](round-twenty-six-intake-model-comparison.json), [Sol per-call costs](round-twenty-six-intake-sol.json), [cascade per-ticket resolution](round-twenty-six-intake-selected-cascade.json). Investigation scores, harmful findings, time and independent grading are separate and not yet established by this intake check.
