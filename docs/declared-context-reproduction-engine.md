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
each receipt. Both quantities must be complete scalar values (finite when numeric; native blanks stay blank) from the
same engine/connection/object, same layer and same self-reported identity.
Value sizes use the existing compiler consumer bounds. Surface attestation
applies to both. Missing or contradictory self-reports and
different surfaces/identities return unavailability, never a verdict.

The separate process receipt carries `WITHIN_LAYER_CHECK`, the original
definition and read references, all original attestations, composed restrictions,
the **undeclared-context value**, produced value and independently supplied
reported figure. Its finding label is `REPRODUCED` or `NOT_REPRODUCED`. With no
reported figure, it retains the produced value, a null label and explicit
`No reported figure supplied.` unavailability. It never invents a figure. A native
blank remains blank, including after an empty intersection; it is not coerced
to zero or treated as an invalid value.

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

Twenty-nine targeted tests cover intersection (including empty/type-distinct
sets), applicability, match/mismatch, missing/invalid figures, attestation,
receipt/compiled-scope preservation, native blank preservation, sealed quantities, production narrative
assembly, placement before unavailable lower reads and all existing outcome gates.
The second local full suite passed 1,352 tests before the final native-blank
and deep-copy guards. The final 128 focused tests (including all 29 reproduction
tests and original outcome/synthesis/question/golden checks) and two required
generator tests pass. Final full-suite CI is tracked on
[PR #294](https://github.com/bcsnpc/data-investigation-agent/pull/294); no final
local full-suite rerun is claimed after those last narrow guards.
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


## Dated amendment: pre-intersection checks (2026-10-01)

The user's audit question 2 is withdrawn and the existing intersection design is
accepted: execution receives one intersected restriction per column, while the
original declarations remain in definition evidence. Passing originals separately
would reintroduce same-column replacement. The original audit comment is unchanged;
a dated correction was appended on PR #294.

An empty intersection is represented as a restriction with `values: []`, unlike
an undeclared scope's empty restriction list. A scope-evaluating synthetic adapter
test returns zero only when that empty restriction actually reaches evaluation;
the separate blank-result test preserves native blank without converting it to zero.

The engine type represents only bounded `IN` sets of typed scalar values, including
empty sets. Range, negation, relative date, measure condition and Top N are not
representable or intersectable by this type. Any such operator refuses the entire
declaration as UNDECLARED before reproduction reads, naming the form; valid IN
members before or after it are never executed alone. Extra semantic fields and
structured IN values also refuse rather than being coerced. Bounds still fail
closed. The vertical procedure and synthesis retain the named refusal. Native
extraction/rendering refusals remain the adapter's responsibility in PR2.

The intersection key is the exact opaque `field_id` of a fully resolved catalog
column, never its display name or a shortened path. Resolution belongs to the
adapter, not native-syntax validation in the engine. A same-named-column test uses
distinct resolved table/column identities and verifies both restrictions reach
execution separately, even when their sets are disjoint.

The amended 34 reproduction tests pass. A first test attempt exposed mutation of
a frozen synthetic Probe; the fixture now uses dataclass replacement. No production
read occurred. Full regression validation follows below. Planner shaping, native
adapter, discovery approval, lower filtered-scope refusal and recorded runs are
unchanged. Engine changes invalidate prior freezes; no end-to-end claim is made.


Final amended-engine validation: all 1,361 local regression tests passed in
404.778 seconds, including the 34 reproduction tests. Two required generator
tests passed separately; 732 local documentation link targets resolved and
`git diff --check` passed. The full suite emitted SQLite resource warnings but
no test failures. Final amended-head CI and merge state are tracked on PR #294.
