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

Appended second-pair checkpoint, 2026-10-11:

| Ticket | Mode / repeat | Result | Physical / diagnostic | Model calls | Rate-card USD | Questions | Answer contract | Harmful claims |
|---|---|---|---|---|---|---|---|---|
| 03 | AGENT / 1 | HELD, waiting for user | 0 / 0 | 14 | 0.660804 | 1 | Not delivered | 0 |
| 04 | AGENT / 1 | HELD, loop exhausted | 0 / 0 | 25 | 1.040023 | 0 | Not delivered | 0 |

Ticket 03 asked: “To resolve the ticket exactly, which number should I treat as the figure reported by the MRR All Plans card itself?” Its preceding attempts included manual-sum and disputed-difference figures alongside the displayed figure, nested/span errors, and a route failure. The displayed sentence “It says 600.” parses after the repair, but the additional 700 and 100 candidates remain ambiguous. This is not an estate finding.

Ticket 04 repeatedly failed nested provenance, reached a business-rule refusal, then continued trying until its loop cap. It delivered nothing. The extra calls did not establish the requested monthly event or business policy. Both captures have zero pending artifacts or exclusions.

Both first-pair tapes replayed exactly, with zero network or model calls and no engine identity substitution. The initial isolated replay failed the engine hash before executing: checkout line endings differed from the recorded native bytes. Restoring only normalized-content-identical source files in that isolated consumer yielded the sealed engine hash `c76de81a237a2b42f3075fc2346ac9cef82ef2c90ab2bcc34a262d81f6a9acff`. Original tapes and the initial failure receipt are unchanged. This does not clear unrelated original-fixture or rebuilt-verifier replay failures.

The saved 21 pipeline billing holds remain eligible baselines. Reinspection of the precision refusal for ticket 14 repeat 2 found spelled-out “zero” and “four” figure candidates, not sentence punctuation; that refusal is unchanged. Other retained holds occur on verbatim-span, unresolved-subject, or business-intent paths before the repaired numeric punctuation check. Six pre-intake operator failures still lack pipeline baselines and need fresh ordinary attempts; free-text has no historical baseline.

Second-pair closing window: pot 2,377/4,000, reserve 95; rolling 1,227/3,000; 835/2,000 model calls and 30,788,580/40,000,000 input characters. Four billing attempts are root-reviewed: zero delivered answer contracts, zero harmful claims, three questions.


Dated hybrid transition, 2026-10-11: the admitted ticket-13 attempt held for a freshness-anchor question (5 model calls, 0 physical requests); ticket-14 exhausted its 25-decision cap while revisiting retained definitions (25 model calls, 1 physical candidate read). Neither delivered a finding; both sealed originals remain unchanged. Remaining pure-agent slots are not run after the owner changed the plan to pipeline-first HYBRID. The trailing-period repair passed all 3,284 regression tests on 5b77962 (1,140.366 seconds).
