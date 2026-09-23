# Conservative read redundancy

2026-09-23 UTC. Ordered reliability item 5, issue #199.

Generated SQL/DAX reads compare tokenized query text, declared plan scope, immutable
run scope, discovery context version, model context hash and connection policy.
Whitespace (and SQL lexer comments) may normalize away; identifier/literal text,
output labels, projection order and row limits remain significant. No expression
subset, projection reordering, result containment or semantic equivalence is used.
The earlier scalar-expression subset detector has been removed because it rejected
differently labelled queries more broadly than this contract permits.

Only complete, sealed receipts from the current session can be reused. Missing
version metadata and incomplete receipts do not become matches. A match records
`READ_REDUNDANT`, attaches the prior receipt ID and reused values to a rejected
proposal, and does not dispatch or reserve another data read. The values are
explicitly labelled reused, not a new observation. Already-spent planner calls and
token reservations remain charged; this is not a refund of provider work.
Typed candidate-ID guards remain in place; this new text comparison covers the
generated SQL/DAX tools. `score_run.py` reports `redundant_reads_blocked` separately.

## Offline checks and the F-paced limit

The final six focused tests passed in 8.202 seconds. An exact DAX repeat with
different spacing reuses its receipt, leaving a two-read allowance for a subsequent
mock source query in three planner calls. That session stops at its read budget;
it does not establish a business conclusion. A SQL repeat also dispatches once.
A recorded-provider injection reproduces the duplicate at step five with zero
network calls and no unrecorded tool execution. Scope/version/policy/limit changes,
different labels, reordered projections and distinct literals remain separate.
The earlier four-test set passed in 2.949 seconds; the expanded six-test set passed
in 7.091 seconds before the explicit run-scope check. Five replay tests passed in
16.588 seconds and six local-repair tests in 8.146 seconds. The 36 flexible-query
tests passed in 7.105 seconds. All 985 regression tests passed in 236.691 seconds. Secret scanning and local links passed.

Read-only inspection of the original `.local/unknown-domain-v2/runs/F-paced.json`
found **no identical native queries**. They overlap or reorder projected measures;
the source proposal uses an unqualified object. Under the user's strict matching
rule, these cannot be blocked as identical reads or converted into an authorized
source query. The original six-call BUDGET_LIMIT result remains a failure. It was
not rerun, modified or relabelled. There is no pre-item-1 HTTP recording from which
to claim exact full-provider replay of that historical run.

Clarification was requested on using the exact-duplicate fixture as the item-5
blocking-check gate while retaining F-paced as a test-selection failure. Until that
is resolved, the original F-paced acceptance wording is **not met**. The safe text
comparison is implemented without expanding into semantic matching. No fresh
freeze or unfamiliar-domain acceptance pass is claimed.

The run ledger retains individual validation invocations. Validation-suite rows
do not aggregate internal mock trajectories. No live LLM/cloud calls, permission
changes or SQL-limit changes were made. Engine bytes change, so v4 remains
invalidated; frozen artifacts and stored historical evidence stay untouched.
