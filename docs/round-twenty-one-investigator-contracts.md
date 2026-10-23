# Round Twenty-One single investigator: offline contracts and integration

The consumer owns nine verdicts; these are not aliases for legacy outcomes.
`ledger_investigator.Tools` uses the real GraphAPI and FactLedger protocols,
requests only the admitted target's path and exposes closed identifier schemas.
The model cannot supply SQL, a new visual, arbitrary filters, refresh/job commands
or an impersonated identity. Duplicate calls reuse retained evidence IDs.

The loop recreates the visual and applicable comparison, reads independent
path-local ledger facts in parallel without model calls, then uses the existing
`GovernedDecision` provider adapter where more work is required. It sends a
compact evidence index and one-step explicit evidence fetches. Model rankings
and public action notes are taped but never treated as proof or delivered prose.
Clock observations use process_tape.clock for exact replay.

Every freshness explanation requires two divergent completed quantities under
exactly equal declared context, a quantity-preserving boundary's explicit graph
producer contract, and current observed timing tied to that producer. A failed
run without these does not explain a ticket. Latency also needs the declared
next due time and an observed median duration. BLANK remains distinct from zero,
an unavailable query and a missing reported figure. Missing/stale/future facts
cannot become a cause.

`as designed`, `access difference` and `source changed history` require checked
producer witnesses in addition to registered comparison evidence. A retained
SQL definition or model interpretation alone cannot provide one. In particular,
access checks cannot impersonate RLS and design checks cannot judge business
correctness. If the installed estate ports cannot produce these witnesses,
the capability is explicitly unavailable and the final result is `not found`.

Root integration supplies `cloud_investigator.run` with the real GraphAPI,
FactLedger, a compiler-backed gateway quantity reader, the governed model
provider, admission/persistence callbacks, and optionally the path collector and
already validated design/access/history producer. No dynamic module or handler
can come from ticket/model JSON. The standalone adapter is not yet registered
as a live handler, and no live execution or nine-verdict platform coverage is
claimed by this offline implementation.

Quantity ports must return subject, key, exact context, VALUE/BLANK state, exact
value, original receipt ID, original query/surface details, read-only verification
and route admission. They must preserve the existing tenant-principal warning
and verification warning strings. The new code renders these as labels in both
outputs, along with the snapshot caveat; it does not reinterpret them as holds.
The JSON case bundle contains the ticket, hypotheses and checked support per
hypothesis, tools/timings, original evidence, one verdict and stop reason.
Technical output includes the actual query/value/definition evidence pack.

Known integration gaps: the collector's load timestamp may be unavailable at
some nodes; graph edges may lack a checked quantity-preserving producer contract;
source row-history and side-by-side authorized security witnesses may not be
available. These remain named evidence gaps, not inferred green findings. Existing
sealed tapes, oracle records and acceptance expectations are untouched.

## Typed operational facts and live adapter fields

A request has kind `COMPARE`, `FACT` or `DEFINITION`. The latter is preserved as
an explain-route request, not silently turned into a discrepancy. A `FACT`
request additionally names its admitted subject, `RUN_STATUS` or `REFRESH_STATUS`,
and a verbatim ticket source span. Code verifies that span explicitly asks an
operational status question. A current failed run may then answer `failed job`
without a numeric query, labelled `OPERATIONAL_FACT_ONLY`: it says expressly
that no numerical cause was established. The same observation cannot support a
`COMPARE` cause. Newer empty run-history listings suppress older run records;
missing API retention is not proof that a job never ran.

Compiler-backed read-port return shape:

```text
subject: the exact requested graph node ID
key: the admitted ticket key (including explicit null when unkeyed)
context: the exact admitted declared-context object
state: VALUE or BLANK
value: exact returned scalar, or null for BLANK
receipt_id: original retained native read receipt ID
read_only_verified: true only from the existing worker's verification
route_admitted: true only after existing surface/connection/scope checks
query, execution_surface, expression_hash, warnings: original retained details
```

For `DESIGN_CHECK`, reuse the original transformation producer after real reads:
its `terminal_support`/`assessment_support.validate` and `process_outcomes.validate`
must succeed. Match its native comparison receipt IDs and declared contexts to
the new comparison's read receipts; retain the original definition observation,
checked judgment and provenance in the witness. Return `checked=true`, the
validated mechanism, `business_correctness_claim=false` and the registry support
IDs. This flag is a trusted adapter result, never a field the model may submit.
Do not implement it by accepting a free-standing model `explains=true` response
or mapping a legacy outcome label without rechecking its native evidence.

The investigator now tops up stale/missing supported runtime fact kinds only
for nodes on the admitted path when a collector is installed. Refresh results
become separate current immutable fact records. No collector means a named gap.
Reported-figure spans and digit precision reuse the existing reported_figure
contract, including EMPTY and reduced-precision qualifications; those engine
facts always remain in both outputs even if the model omits their IDs.

The new standalone outer-persistence route currently supports EXACT estates.
It refuses a projected installation before reading the graph or persisting raw
material rather than bypassing the existing privacy projection boundary. This
is a declared integration gap; no mixed exact/projected capture is accepted.
The engine freeze is invalidated by these new code bytes.

Dated tightening, 2026-10-22: a checked flag alone is insufficient for any of the
three optional witnesses. `native_verdict_support.design_witness()` retains and
validates the original process assessment/observations; terminal validation
repeats the existing assessment/process gates and matches original read IDs,
queries, execution surfaces and exact declared contexts to the new comparison.
Missing native proof or altered mechanism refuses. The access contract requires
original different authenticated identities, same query/expression/context/data
surface, and different returned values without impersonation. The history
contract requires an original guarded read at a graph-declared system of record,
back-dated before/after row data for the ticket key, and checked before/after
quantities matching the observed split. A model's boolean assertion supplies
none of these records.

Owner steer, 2026-10-22: a COMPARE request marked `comparison_pending=true`
first recreates its admitted target, then checks current facts on its declared
producer path. It may return a qualified failed/waiting/stale/scheduled-latency
status without a second quantity. Both outputs explicitly say that the
comparison was not checked and no numerical cause was established. Stale or
unrelated failures cannot take this route. Only when no operational status is
established does it ask what the user is comparing against. Normal numerical
explanations retain their equivalent-context divergent-read gate unchanged.
Admission-owned `assumptions` strings are rendered as assumption lines in both
outputs; they never silently become observed facts.

Explicit operational status questions also have a bounded negative answer:
the latest unique current `SUCCEEDED`/`COMPLETED` run is rendered as an answered
operational fact with its run identifier and observation time. The unchanged
nine-verdict vocabulary uses `not found` to mean no failed/waiting/stale
incident was established, while `claim_scope=OPERATIONAL_FACT_ONLY` records
that the requested status itself was answered. This does not claim technical
or business correctness or explain any quantity. Newer unknown observations,
stale status, an empty later history, or conflicting latest records leave it
unanswered. Direct status questions use no model or value query.
