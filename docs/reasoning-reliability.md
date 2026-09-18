# Reasoning reliability after frozen challenge v2

Tracking: [#199](https://github.com/bcsnpc/data-investigation-agent/issues/199).
PR #200 merged after six successful CI checks. Frozen v2 acceptance remains
failed/incomplete; changes here require a fresh freeze before unknown-domain grading.

The corrections are domain-generic: distinguish new hypotheses from evidenced
updates in the provider schema; expose a bounded, kind-balanced directory of
current discovered assets; reject syntactically repeated completed scalar reads
when only labels change; clarify only material missing business intent or scope.
The scalar comparison is deliberately narrow: plain EVALUATE ROW expressions,
complete prior receipts and the same policy/context. It is not a DAX equivalence
engine and never promotes old observations to newly executed reads.

Known-domain regression is explicitly marked by the evaluator and has no valid
freeze commit. This mode is for debugging only. It must never be reported as a
frozen challenge pass. Call pacing counts against existing deadlines and does not
increase deployment quota or retry failed calls automatically.

Validation and live results are being collected. The first live regression still
proposed nonexistent SQL targets despite the discovered directory; those proposals
were blocked. The next correction makes retrieved source schema an explicit
prerequisite for generated SQL proposals, without fixing the investigation's
layer order. Existing typed diagnostics keep their own admission checks.

## Validation sequence

The first correction set passed 897 regression tests and 10 dynamic browser checks
(injected cloud transport, not live acceptance). Known-domain session
`84349b1b-4fdf-4d09-abe4-5831745a99c4` still ended unresolved after six planner
calls and one native query: source targets were invented and rejected. This is
preserved as a regression failure.

Generated SQL now additionally requires retrieved SqlObject metadata for every
referenced source object. The wire schema offers metadata/native actions before
source schemas are available; the backend independently checks the actual bound
object identities. This does not grant authority from metadata or require native
queries before source work. Twenty focused parser/runtime tests pass. A final
full regression and a second known-domain live trial are running.

The second known-domain trial (`c77dfc29-3603-48f8-9b3c-52a5cf64ad3c`)
retrieved context first, but invented one lookup identity and stopped at the
input budget after four planner calls. It made no data query and did not pass.
That intermediate code passed 898 regression tests.

The current revision adds short, schema-enumerated lookup handles with exact
server-side identity decoding, and compacts earlier metadata only in the planner
projection. Full stored receipts remain unchanged. Dynamic workspace runs allow
12 planning steps / 200,000 input characters; cloud reads remain capped at six,
wall time at 900 seconds, and daily usage policy remains in force. Legacy runs
retain their original admission limits. A fresh known-domain trial and final
regression are running; these are not frozen unknown-domain evidence.

## Reader access and final checks

The final full suite passed 900 tests; all 10 dynamic browser checks passed with
injected transport. A subsequent receipt-integrity correction passed 23 focused
tests: duplicate-read detection verifies the original sealed receipt and refuses
tampered data rather than trusting a stored request alone.

Session `bc46313f-dbc8-4859-b910-f3699d323478` retrieved a real source schema and
proposed a valid source-first query. Azure SQL rejected execution with error 229.
After explicit user approval, SELECT was granted to `orderops_investigator` on
only the six isolated `app` tables ending `_e1b8e1`: warehouse_locations,
inventory_products, product_rates, stock_movements, purchase_orders and
inventory_adjustments. The identical reader probe returned 100 rows with
`read_only_verified: true`. No write permissions or quota settings changed.
The denied session is preserved; a new session tests the corrected access.

The post-grant trial `1f1ac21b-df73-4be6-b63f-b384f7cf03e1` completed a
20-row source query but repeatedly requested a derived field absent from the
retrieved SQL schema. The operator cancelled the repetitive run; its persisted
state and decisions remain in the catalog. The outstanding planner response was
fenced after cancellation. This is a failed regression, not a diagnosis.

That run exposed two generic recovery issues: catalog-binding errors were too
vague, and rejected proposed queries/lookups did not advance the no-progress
counter. The corrections provide bounded column-binding guidance without echoing
SQL or values, and apply the existing no-progress limit before more provider or
cloud work. All 25 focused tests passed, including zero-cloud-call termination
for repeated invalid columns and lookups. The final full regression passed all
903 tests in 266 seconds. The patch secret scan found no leaks.
