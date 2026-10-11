# Round Fourteen billing comparison — first pair

2026-10-11. Independent sealed tester inputs and expectations are unchanged. These are answer contracts, not declared outcome labels; no outcome expectation has been invented for grading.

| Ticket | Mode / repeat | Result | Physical / diagnostic | Model calls | Rate-card USD | Questions | Answer contract | Harmful claims |
|---|---|---|---|---|---|---|---|---|
| 01 | AGENT / 1 | HELD, waiting for user | 0 / 0 | 4 | 0.153791 | 1 | Not delivered | 0 |
| 02 | AGENT / 1 | HELD, waiting for user | 0 / 0 | 6 | 0.244119 | 1 | Not delivered | 0 |

Ticket 01 asked: “Please confirm the exact value as displayed on the Invoiced Amount card, including any decimals, currency symbol, commas, or suffixes (for example: 950, 950.00, $950, or 0.95K).” Its model span retry supplied “The card shows 950.” The parser wrongly rejected sentence-ending punctuation. The generic repair preserves the entire quoted span and exact precision; it does not supply a value, widen a tolerance, or replace this attempt.

Ticket 02 asked: “Which page-1 figure do you want me to investigate as the main number: 550 collected, 950 invoiced, or the difference between them as the amount still to chase?” Its model-assigned PRIMARY/COMPARISON/CONTEXT roles did not settle competing reported figures. This follows the existing conservation invariant: extraction cannot discard a reported candidate merely by assigning a role. The form did not pick one native target. The refusal remains; no role-based bypass was added.

Both attempts are sealed, with zero pending captures or exclusions, and no business or technical output. Absence of a delivered finding is not an answer-contract pass. Agent questions are counted from executed `ask_user` transcript events, including cases with an empty questionnaire question list.

DECIDED WITHOUT REVIEW: correct sentence punctuation in the numeric parser, with end-to-end provenance/precision and malformed/competing-number regressions. Rejected alternative: trusting model figure roles to erase candidates, which would reintroduce the preserved competing-figure defect. The completed pair stays unchanged; only unattempted ordinary slots may use a fresh engine/context pin. Mixed revisions cannot establish same-revision repeat stability.

The prior recorder-launch revision ce0de1e passed all 3,281 tests in 1,673.593 seconds. This punctuation repair passed 68 focused tests, including the wrong-cell/competing-figure/span intake regressions. Current full regression is pending. Engine freeze invalidated; #423 remains draft, PIPELINE remains default, and the earlier two harmful agent findings still fail adoption.

Closing window: pot 2,377/4,000, protected restoration reserve 95; rolling requests 1,227/3,000; 796/2,000 model calls and 29,368,429/40,000,000 input characters today. Actual provider credit remains unverified; rate-card accounting is not a provider-credit balance.
