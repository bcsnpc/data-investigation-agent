# Declared-context reproduction: engine contract

Date: 2026-10-01. Tracking: #193 and #199. This is the first of three
separate PRs: engine, adapter, then recorded runs. Stop after this PR.

#293 merged at `1862ccb4f6e98bed843d4dc4ac31a9ad9f8bb9c0` after all six
checks succeeded. Its `inspect.py` shadowing failure, failed scan and replay
receipts remain unchanged.

## Implemented boundary

`declared_reproduction.run()` is a separately callable neutral engine check.
Adapters opt in with `declared_context_reproduction`. The vertical procedure
invokes an opted-in check after establishing its presentation baseline and
before attempting any lower read. It continues the vertical walk afterwards.
Reproduction is a separate finding, not a replacement classification: a run
may retain `NO_COMPARABLE_PATH` for its lower boundary while reporting that
the declared selections reproduce the reported figure.

The native adapter does **not** advertise or implement the capability in this
PR. No adapter, intake wire schema, estate, permission, policy, recorded run or
discovery approval changed. The caller-facing engine scope accepts an explicit
`reported_figure`; interpreting and carrying a numeric figure from a real ticket
is not established by these synthetic tests. Native predicate extraction,
compilation and that production integration remain for the adapter work.

## Neutral interface and evidence contract

The adapter supplies `declared_context(layer, measure_id, scope)` with retained
definition evidence, `DECLARED_BY_DEFINITION` provenance and bounded restrictions:
`field_id`, `operator: IN`, and typed scalar `values`. At least one restriction
must address a resolved ticket filter or dimension field. Absent or unrelated
predicates make the check undeclared and issue no value reads. Unsupported
operators refuse before execution; range/complex predicate support is not implied.

The engine intersects **every** same-field restriction and sends the composed
neutral scope to `evaluate_declared_context()`; an empty intersection stays empty.
It performs two distinct governed reads: no declared restrictions, then the
composed restrictions. The adapter must retain the applied scope and measure in
each receipt. Both quantities must be complete finite scalar values from the
same engine/connection/object, same layer and same self-reported identity.
Value sizes use the existing compiler consumer bounds. Surface attestation
applies to both. Missing or contradictory self-reports and
different surfaces/identities return unavailability, never a verdict.

The separate process receipt carries `WITHIN_LAYER_CHECK`, the original
definition and read references, all original attestations, composed restrictions,
the **undeclared-context value**, produced value and independently supplied
reported figure. Its finding label is `REPRODUCED` or `NOT_REPRODUCED`. With no
reported figure, it retains the produced value, a null label and explicit
`No reported figure supplied.` unavailability. It never invents a figure.

The engine revalidates the originals, not a lossy projection. Synthesis preserves
the complete finding and verifies the two scalar values against sealed query
receipts before rendering it. Both narratives label it within-layer. The engine-rendered question account
recognises numeric reproduction as partial evidence, never a full answer; without
a figure it explicitly names the missing figure. Repeated unattested fields on
the same surface are rendered once with both receipt references. Unattested
surface fields and active-context, correctness, native-restriction and shared-
snapshot limitations accompany the finding.

## Claims and gates

Reproduction establishes that a declaration can account for a reported figure;
it does not establish what was on screen or that the figure is business-correct.
The undeclared-context value remains subject to row-level security and other
native restrictions. It is never called an unrestricted value or true total.
Non-reproduction leaves undeclared selection/security/cross-filtering, update
timing and deeper divergence open. The reported figure is not used to execute
either query; a different reported figure, faithfully composed scope or actual
data can yield a mismatch. Equality is not guaranteed by the implementation.

No reproduction receipt is tagged `comparison`, `flow_consistency` or
`presentation_definition`. It cannot satisfy `PRESENTATION_LOGIC`,
`CONSISTENT_TO_BOUNDARY` or the pre-`DEFECT` gate. The existing
`presentation_context()` implementation remains inconclusive about actual active
selections. `_lower_quantity()` and its filtered-scope refusal remain unchanged:
`Declared source comparison does not yet translate filtered scope faithfully.`

## Validation and context cost

Twenty-five targeted tests cover intersection (including empty/type-distinct
sets), applicability, match/mismatch, missing/invalid figures, attestation,
receipt/compiled-scope preservation, sealed quantities, production narrative
assembly, placement before unavailable lower reads and all existing outcome gates.
The first full suite passed 1,350 tests; the final 25 targeted tests pass.
A second full suite and final CI are running after the question-account and
shared consumer-bound corrections; their final results will be recorded here.
No live or recorded investigation was performed, so no run ledger row is added.

Planner payload shaping is unchanged. Existing exact projected/wire goldens
remain identical; the coverage fixture remains 28 directory entries, 11 SQL
objects and 5,543 payload characters before/after. Other golden projected
payloads remain 1,460 (dense profile), 7,212 (definition children; 50 directory
entries), 4,722 (paged content) and 31,851 (per-call ceiling) characters.
Optional reproduction evidence adds synthesis context only when the capability
is later supplied; it consumes no directory allocation. Native context cost and
live read cost are not measured or claimed in this engine-only PR.

Engine bytes changed: all prior freezes are invalidated. No fresh freeze, domain
or acceptance claim is made. The next PR is the adapter implementation, followed
by a separately authored numeric fixture ticket and unchanged family D. No live
run is authorised or attempted as part of this PR.
