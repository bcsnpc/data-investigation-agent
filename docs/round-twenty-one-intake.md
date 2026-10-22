# Round Twenty-One: essentials intake

The additive `investigator-essentials-v1` entry point accepts incomplete essentials.
A missing comparison does not block recreation or freshness checks. A uniquely
matched retained number can establish its report with an explicit assumption;
otherwise one combined named-choice question resolves missing report/number.
Page, value, filters, date and screenshot remain optional.
The existing form, claim and model-only contracts are unchanged. The new form is
served at `/essentials`; authenticated API endpoints are
`/api/workspace/essentials/schema`, `/api/workspace/essentials`, and
`/api/workspace/essentials/<intake-id>/reply`. The form never stores its workspace
key and renders catalog choice names, never their internal identities.

Names and enrichment synonyms are ranked deterministically. Confidence is a
lexical ranking score, not a probability: exact selected identity/name 1.0,
human-confirmed synonym 0.95, inferred synonym 0.90, partial name at most 0.80.
Report and optional page constrain eligible numbers before ranking. An unknown
enrichment subject cannot create a node. An exact unique match proceeds; only
equal top candidates produce a question. That question is rendered from actual
retained names and comes with the catalog hash. Unresolved labels, unavailable
names and unresolved second ties become explicit holds. A submitted question
and its one reply are retained; a second reply cannot reset the question budget.

A named measure remains a measure anchor. Intake does not select a different
visual, make a TOTAL address, assume saved filters, infer a tolerance, or promote
an inferred synonym to causal evidence. Explicit filters are checked against
typed retained columns and preserved; they do not attest faithful lower-layer
scope translation. An admission means the new investigator can start checking
this subject, not that its visual query, lower comparisons or explanation have
already been validated. Business-rule correctness remains an owner question.

Internal catalog, resolver and value errors return HELD with their recorded
type and cause. Both input and result are persisted in `workspace_essentials`.
This is a logical application table backed by the existing shared
`state_documents` authority, with the worker's existing scoped privileges, not
a new PostgreSQL table or a local-only cloud cache. The table is registered in
the shared application contract. Projected installations explicitly refuse this
new persistence path rather than writing a raw fallback.

## Original decision (superseded by the dated owner steer below)

Part C's blanket comparison requirement conflicts with Parts A/E's native
freshness and calculation questions. Following the round owner's request and
the parent's interpretation, goal type is explicit: COMPARE requires a stated
comparison; FRESHNESS and DEFINITION retain comparison `null`. Rejected:
inventing `LATEST_REFRESH` or `DEFINITION` as if the user had supplied a numerical
comparator. Report remains required. A historical ticket without one is not
silently assigned a report from the scorer's knowledge.

## Original twelve-ticket offline check (preserved)

Source text is unchanged from `docs/round-seventeen-scored-results.json`.
Definitions are the original saved `current-fixture-catalog.json`, raw SHA-256
`4edaf69ecd5d00b4dbac203f17f74632c16810bca356cc64d4b65fdeee6b7afa`, canonical
catalog hash `834f789f87df145325248a4a12e234e435b5bb747116c45d303bf6a037fe292b`.
That canonical hash matches the retained Round Seventeen claim states. No
oracle, golden record, expectation or ticket text changed. The offline adapter
extracts exact known name spans only; it does not invent missing essentials.

| Ticket | Class | New intake | Reason |
|---|---|---|---|
| R17-01 | quantity | HELD | No comparison supplied |
| R17-02 | quantity | HELD | No comparison supplied |
| R17-03 | quantity | HELD | No comparison supplied |
| R17-04 | quantity | HELD | No comparison supplied |
| R17-05 | quantity | HELD | No comparison supplied |
| R17-06 | quantity | HELD | No comparison supplied |
| R17-07 | freshness | HELD | No report named |
| R17-08 | freshness | HELD | No report named |
| R17-09 | freshness | READY | Named report, page and measure bound |
| R17-10 | definition | HELD | No report named |
| R17-11 | definition | HELD | No report named |
| R17-12 | definition | HELD | No report named |

**One admission to the investigator, zero questions, eleven holds.** No
investigation was executed by this offline intake check, so this is not a
claim that a live answer was delivered or that any held ticket was solved.
Original Round Seventeen result: six errors, six clarifying, zero investigations.
The new contract removes those crashes from this check but holds legitimate
incomplete inputs; it does not meet an unstated target by filling them in.

`docs/round-twenty-one-old-ticket-intake.json` contains all inputs, reasons and
source hashes. `score_retained_essentials.py` refuses a different catalog pin.
Estate requests zero, model calls zero. Harmful findings zero because no
technical findings were produced, not evidence of an independently scored answer.

Offline regressions cover required fields, goal separation, page-scoped synonym
matching, one grounded question, wrong visual prevention, precision, preserved
filters, shared persistence, internal holds, API authorization and visible form
choices. Original wrong-cell and comparison-span tests remain applicable.

## Owner steer, 2026-10-22: investigate before demanding comparison

The owner superseded the strict missing-field refusal. Missing comparison now
admits `comparison: null`, `comparison_pending: true` and available steps
`RECREATE`, `FRESHNESS`. The deferred comparison question explicitly says to ask
only if no quick verdict is established. Intake itself does not fabricate a
freshness fact, reproduce a value or issue a technical finding.

Missing report is inferred only when the number's exact name/selected identity
or accepted current synonym gives a unique report at lexical confidence >=0.9.
The result retains the catalog hash, inferred report, confidence and a rendered
assumption sentence; the form displays it. Multiple matching reports remain a
question. Missing report/number gets one combined choice from real named
report/number pairs; replies apply only the offered, catalog-pinned bindings.
Unavailable candidate names or unresolved choices after one question remain held.
No arbitrary default visual or scope is selected.

The same immutable twelve texts and same catalog hash were re-scored offline:
**4 admitted, 7 one-question, 1 held, 0 quick verdicts**. R17-01, R17-02,
R17-05 and R17-09 are admitted. R17-03, R17-06, R17-07, R17-08, R17-10,
R17-11 and R17-12 ask one grounded question because the retained number names
occur in more than one report. R17-04 remains `BUSINESS_INTENT_REQUIRES_OWNER`:
its explicit question is whether this is the intended value. Estate requests 0,
model calls 0, technical investigations 0. The earlier 1/0/11 result above is
preserved as history, not re-labelled. No expectation or ticket changed.

The schema and UI accept missing details instead of browser-blocking submission.
Regression coverage includes deferred comparison, unique report assumptions,
multi-report ambiguity, one combined question and its durable reply, unchanged
catalog hashes, precision and scope preservation, authentication and names-only
choices. Focused essentials suite: 24 passed.
