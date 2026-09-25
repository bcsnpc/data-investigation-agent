# Capability-gated process steps and declared-scope resolution

Updated 2026-09-25. Related to #193 and the process-debugging review. This is an
implementation checkpoint before the prescribed three-run known-domain evaluation.
It makes no freeze, variant or unfamiliar-domain claim.

## Corrected interpretation of the prior smoke

The previous Microsoft adapter advertised only path resolution and scoped quantity
evaluation, but its five other methods were constant stubs. The procedure still
called those methods and treated their returns as evidence that presentation or
transformation logic did not explain a divergence. A future unequal comparison
could therefore have reached `DEFECT` without checking competing explanations.
The three saved runs remain valid receipts for their baseline reads, but their
zero-planner-call behavior measured unfinished adapter wiring rather than a Fabric
estate limitation.

## Step capability contract

The neutral procedure retains the two-capability floor:
`resolve_measure_path` and `evaluate_scoped_quantity`. Each optional step has its
own capability: `presentation_freshness`, `presentation_context`,
`transformation_definition`, `job_history` and `ingestion`.

Before invoking a step, the procedure checks the adapter's declaration. An
undeclared step is not called and records `CAPABILITY_NOT_IMPLEMENTED`, its step,
capability and reason. A declared check that cannot complete is also retained as an
inconclusive capability boundary. Both the business and technical output list the
skipped checks. Outcome validation requires the corresponding capability for every
specialized result. `DEFECT` additionally requires both transformation-definition
and job-history checks to have run without a step 3/5 capability gap. A minimal
adapter that declares only path resolution and evaluation is tested against every
forbidden conclusion.

## Wired Microsoft capabilities

| Capability | Current behavior | Boundary |
| --- | --- | --- |
| `presentation_freshness` | Undeclared | Power BI refresh history returned HTTP 403 to the execution reader. The reader is not elevated. |
| `presentation_context` | Declared | Reads retained report/page/visual definitions, filter presence and slicer visual types; active bookmarks, selections and RLS remain unavailable and are reported as inconclusive. |
| `transformation_definition` | Declared only when a governed judgment provider is configured | Retrieves the exact retained definition with paging through the existing context store, passes the observed upper/lower values plus a bounded excerpt to one metered structured judgment, and retains its limitation. |
| `job_history` | Declared | Reads retained `run_history` observations collected from Fabric item job instances; absence and not-applicable boundaries stay explicit. |
| `ingestion` | Declared when the isolated metadata worker is configured | Lists only the target table's `_delta_log`, reads at most the latest 1 MB JSON commit, and returns an allowlisted commit-info subset. It never reads table rows. |

Provider failures, planner allowance and cloud reads use the existing reservations.
Each actual DAX or OneLake metadata read consumes one cloud-read reservation. A
definition judgment consumes one planner/input/output reservation. No SQL, DAX or
metadata action is retried automatically.

## Declared source primitive

The platform-neutral resolver takes exact target labels, allowed target kinds and
stable scope identities derived from the same definition. It traverses descendants
of those roots only. It never searches the wider catalog or another connection.
Its terminal statuses are `RESOLVED`, `NO_DECLARATION` at the adapter boundary,
`SCOPE_NOT_DISCOVERED`, `NO_MATCH_IN_SCOPE`, `AMBIGUOUS` and `ACCESS_DENIED`.
Ambiguity returns every candidate and selects none.

Every resolved or failed pointer carries `DECLARED_BY_DEFINITION`; resolved semantic
partition pointers also cite the definition asset, character offset, declared
connection asset and resolved asset. The Microsoft adapter parses the model's
`Sql.Database` connection declaration, follows the exact native model-to-endpoint
and endpoint-to-lakehouse topology in the approved workspace, and resolves the
partition's `schemaName.entityName` only inside that lakehouse. The beta relation
type is retained literally as `NATIVE_ASSOCIATION` or `NATIVE_CASCADEDELETE`; it is
scope/topology evidence, not rewritten as data flow.

For the known model this mechanism is intended to resolve the declared
`dbo.movement_values` partition. Definition-derived Gold-to-Silver pointers are
reported with the same provenance but do not create a comparable quantity without
a column/grain contract. No retained definition currently declares the
Silver-to-Azure-SQL application boundary, so it remains `NO_DECLARATION`; the
adapter does not guess by name.

## Planner-context cost and validation

No investigation planner context content was added. Exact golden projected and wire
payloads remain unchanged. The response schema hash changes because process support
now includes declared capabilities and skipped steps.

| Golden | Entries before/after | SQL objects before/after | Payload characters before/after |
| --- | ---: | ---: | ---: |
| Dense profile | 0 / 0 | 0 / 0 | 1,460 / 1,460 |
| Definition children | 50 / 50 | 0 / 0 | 7,212 / 7,212 |
| Paged content | 0 / 0 | 0 / 0 | 4,722 / 4,722 |
| Per-call ceiling | 0 / 0 | 0 / 0 | 31,851 / 31,851 |
| Initial investigation directory | 28 / 28 | 11 / 11 | 15,971 / 15,971 |

**1,073 local regression tests pass**, including process, resolver, discovery,
lineage, runtime, judgment, slicer and Delta-worker coverage. The two required
generator tests pass, `git diff --check` passes, and 489 local documentation targets
resolve. No cloud query was made for this implementation checkpoint.

## Next bounded evaluation

After merge, run exactly three identical recorded known-domain trials. For each,
report declared capabilities, skipped steps, resolved boundaries and provenance,
comparisons, reads by type, investigation planner calls, outcome, terminating step
and visibility boundary. Equal values satisfy the comparison gate. If values
diverge, the run must ask the governed model whether the retrieved definition
explains the observation. Stop after three; do not start a nine-run batch, freeze,
new variant or unfamiliar-domain acceptance attempt.
