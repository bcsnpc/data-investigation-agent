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

## 2026-09-23 clarification and compiled-candidate revision

The user withdrew the F-paced gate. It remains FAILED for test selection/budget
allocation, not a duplicate-detection tuning target. The replacement gate compares
compiler output, resolved assets, parameters, immutable scope/context, policy and
row limits. SQL source/CTE/output aliases are alpha-renamed using bound scopes;
outer DAX ROW labels and projection order normalize while resolved expressions
remain intact. Operators, filters, literals, joins and multiplicity remain part
of identity. No containment, algebraic equivalence or result comparison participates
in admission. Explicit time-dependent query functions are not reused.

Ten focused tests passed, including actual runtime admission of eight distinct
read cases with equal mock results, nested SQL aliases and self-join distinctions.
Thirteen recording tests and 36 flexible-query tests passed. Seven repair tests
passed after updating the synthetic three-read fixture: its former queries differed
only in labels, so the revised fixture uses distinct expressions. The first repair
suite correctly exposed those two obsolete assertions; those failed runs remain
recorded. The initial focused run exposed a nullable-query metric bug, corrected
before the passing runs. Full regression is pending for this revision.

Post-hoc telemetry adds result_equality_overlap_reads, schema_prefetch_repairs,
sql_query_proposals, sql_query_rejections and sql_rejection_rate to scoring and new
ledger entries. Equality means exactly equal canonical typed result rows (including
column names/order), across different compiled fingerprints; each later read is
counted once. Incomplete results and old generated observations without fingerprints are not
counted. Typed reads use their compiled candidate IDs. SQL rejection rate covers validated SQL proposals rejected during local
compilation/admission; malformed decisions without a validated tool are excluded.
These are trend metrics only. Historical ledger lines are not rewritten.

Carry-over fixes share descriptive bounds across repairs, schema and validators.
Recording withholds secret-like context/request/response bodies, marks
SECRET_DETECTED and permits the provider call. Environment substring matching
requires at least 12 characters. Guarded timing/manifest writes cannot mask provider
errors with a recording secret or filesystem failure. An excluded body is not a
complete replay tape. No live tape will be captured before item 6 merges, and no
live investigation, freeze or variant will run before items 5?8 are merged.

A subsequent code review found an output-alias ORDER BY collision in the new SQL
normalization. A local compiler probe reproduced it; this is a release blocker,
not a pass. A regression distinguishes sorting by the first versus second output
and requires equivalent renamed sort aliases to retain the same identity.

The ORDER BY regression initially failed (one test, 0.028 seconds), then passed
with the correction in the final 11-test focused suite (14.363 seconds). The
pre-correction full suite passed 993 tests in 222.397 seconds but did not contain
that regression; it is not the final release check. Final full-suite rerun pending.

Final verification: **994 regression tests passed in 219.467 seconds** on the
corrected engine. The final run includes the sort-alias regression and all eleven
redundancy tests. Staged secret scanning found no leaks; 180 local documentation
links resolved. No live call was made. The ledger remains append-only. Final CI
and merge are tracked on PR #213; item 6 follows after merge.
