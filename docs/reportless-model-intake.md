# Reportless model intake

2026-10-04. Source attempt intake `bda61715-ec03-4156-92ba-6954a8720345`
selected the named model and measure, but stopped with
`Report unavailable: UNNAMED; candidates:`. No read or synthesis occurred.
The intake adapter resolved a report for every proposal, although the procedure
declares reproduction by question kind. This made reportless model questions
impossible even when they required only a model-anchored walk.

Report resolution now runs when a report is explicitly named, a visual/cell
selection is requested, or the consumer-owned reproduction applicability says
it is needed. A model-only source/flow question retains its measure, scope and
reported-figure provenance without inventing report context. The walk still
starts at the model. Reproduction is undeclared by kind. Explicit ambiguous
reports and missing reports for visual questions remain refusals.

Four regression tests exercise reportless numeric source intake, missing visual
report, explicit selection requiring a report and an ambiguous named report.
Historical synthetic figure-question tests now require admission to review
without manufactured report provenance; their immutable fixtures are unchanged.
82 focused intake/inventory/report-scope/discovery tests passed.

The wire schema, prompt and planner payload are unchanged; all recorded request
goldens remain byte-identical. Directory and SQL-object coverage is unchanged
(28 entries, 11 SQL objects, 5,543 characters in the golden directory view).
Only the post-response report-binding projection changes. This does not remove
filtered lower-scope refusals, supply unavailable reproduction or establish that
the source walk completes live. Prior freezes are invalidated. Existing failed
runs, original receipts and ledger rows remain unchanged. No live run in this PR.
