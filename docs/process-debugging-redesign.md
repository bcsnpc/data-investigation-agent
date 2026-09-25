# Process-debugging redesign

Updated 2026-09-25. Tracking: [#193](https://github.com/bcsnpc/data-investigation-agent/issues/193).
This document records the implementation boundary and validation for the redesign
from open-ended data investigation to deterministic process debugging. It does
not claim unfamiliar-domain acceptance.

## Delivered contract

The primary vertical strategy now treats a discrepancy as a process path. Intake
classifies a reviewed question as `MISMATCH_COMPLAINT` or `BUSINESS_QUESTION` and
selects vertical, horizontal or no comparison. Ambiguity still produces one
specific clarification. Horizontal comparison remains proposal-only.

The platform-neutral engine consumes an adapter-provided path of arbitrary length.
It checks presentation freshness, establishes a presentation baseline under the
declared scope, compares adjacent comparable quantities, retrieves the definition
and job state at the first divergent boundary, and checks ingestion when every
reachable boundary agrees. `NOT_COMPARABLE` records the translation gap and the
walk continues. The first evidence-bound outcome stops the procedure. Every query
is retained verbatim and every answer names the deepest checked layer and why the
walk stopped.

The closed outcomes are `REFRESH_LATENCY`, `LOAD_LATENCY`, `PRESENTATION_LOGIC`,
`TRANSFORMATION_LOGIC`, `INGESTION_GAP`, `DEFECT`, `CONSISTENT_TO_BOUNDARY`,
`DEFINITION_DIFFERENCE`, `SCOPE_DIFFERENCE`, `DIFFERENT_SUBJECT`,
`BUSINESS_QUESTION` and `NO_KNOWN_PATTERN`. Each label has a fixed recommended
action and required deterministic evidence roles. A test removes one required
role from every outcome and confirms rejection. Boundary attribution requires a
baseline immediately above the boundary or a specific establishment barrier.
Presentation/transformation logic remains neutral implemented behavior; the user
confirms intent.

Historical assessment labels and `REPRODUCE_MEASURE` observations remain readable.
They are mapped only in projections and are never rewritten. Current capability
advertising and provider schemas use `ESTABLISH_BASELINE`, whose description states
its comparative purpose. The open adaptive loop is retained as the fallback and
can terminate only as `NO_KNOWN_PATTERN` with a named missing capability.

The provider adapter is isolated under `investigator/adapters`. It uses discovered
identity-backed measure context and the existing governed compiler, reader,
receipts and typed scope compiler. With current lineage gaps it does not bind a
similarly named source object: it establishes the presentation baseline and reports
the actual visibility boundary. Adapters advertise capabilities, the strategy
declares its required capabilities, and eligibility is computed before discovery
or execution.

## Synthesis reliability

Synthesis now mechanically assembles mechanism, intent, measure-connection,
baseline, boundary and per-role citations into the outer citation list before
semantic validation. Published text bounds use an explicit
`[TRUNCATED_TO_PUBLISHED_LIMIT]` marker rather than returning an otherwise good
answer as invalid. Missing, incomplete or unauthorized support still fails.

Sanitized regressions derived from the four failed #226 responses (M2, M3, M4 and
M9) all validate after these mechanical repairs. The deterministic process finding
is included in the frozen synthesis digest, and synthesis cannot replace its
outcome label. Model work is limited to interpreting retrieved definitions and
writing the explanation; it does not choose the next layer or exploratory probe.

## Layer-count behavior

- Three layers: establish the top baseline, compare top/middle and middle/bottom,
  then stop at the first explained divergence.
- Direct-to-lowest: one baseline read is sufficient to state
  `CONSISTENT_TO_BOUNDARY` at that one reachable layer; no fictitious lower layer
  or comparison is created.
- Unreachable source: compare every reachable layer, report the deepest one, and
  state `NO_ACCESS` or `NO_LINEAGE` as the visibility stop.
- Different layer count: the same loop consumes the adapter path. A four-layer
  test confirms that `NOT_COMPARABLE` at one boundary does not guess or stop the
  remaining walk.

The known-domain injected runtime executes the real adapter/receipt path end to
end with one native baseline read, zero planner calls and a
`CONSISTENT_TO_BOUNDARY` result. **1,046 local regression tests passed.** Live
three-run smoke results are recorded below only after implementation and CI merge.

## Planner-context cost

This change does not add investigation planner payload content. Golden views retain
the same directory entries, SQL-object entries and payload characters:

| Golden | Entries before/after | SQL objects before/after | Payload characters before/after |
| --- | ---: | ---: | ---: |
| Dense profile | 0 / 0 | 0 / 0 | 1,460 / 1,460 |
| Definition children | 50 / 50 | 0 / 0 | 7,212 / 7,212 |
| Paged content | 0 / 0 | 0 / 0 | 4,722 / 4,722 |
| Per-call ceiling | 0 / 0 | 0 / 0 | 31,851 / 31,851 |

The existing directory-coverage golden remains 28 entries and 11 SQL objects.
Only the response schema hash changes. A synthesis-only deterministic finding is
added after the investigation terminates; its measured live digest cost will be
reported with the three trials.

## Proposal only: horizontal procedure

Resolve both measures, definitions, scopes and identity-backed paths. Different
definitions terminate as `DEFINITION_DIFFERENCE`; equivalent definitions with a
different declared scope terminate as `SCOPE_DIFFERENCE`; structurally separated
subjects terminate as `DIFFERENT_SUBJECT`. Only when definition, scope and subject
path agree does the engine run the vertical procedure on both sides and compare
their first divergence. Unknown equivalence is `NOT_COMPARABLE`, never approximate.
The same baseline and visibility contracts apply independently to both paths.

## Proposal only: recurrence and learning store

Store an outcome-contract version, asset/context fingerprint, scope fingerprint,
outcome, evidence receipt IDs, visibility boundary, reporter pseudonym hash and
time. Store no ticket text, business values or raw rows. An exact current-context
fingerprint can answer a repeat ticket from the prior immutable result. Aggregates
over distinct reporter hashes and time windows expose repeated implemented-logic
complaints and support an enhancement case. Context or definition changes make a
prior result historical rather than reusable.

## Proposal only: declared business context

An operator selects discovered assets and receives a generated questionnaire about
their expected relationship, definitions and service expectations. Answers carry
`DECLARED_CONTEXT`, owner, effective date, reviewed asset-version hashes and a
reconfirmation date. Asset-definition changes or expiry mark answers stale; stale
answers remain historical and cannot upgrade a claim. Current declarations can
support `TEAM_CONFIRMED`; inference remains `LLM_INFERRED`. This surface is optional
and never blocks ordinary process debugging.

## Proposal only: known-issues register

Store issue ID, affected stable asset IDs, start/end window, status, owner and a
reviewed user-facing notice. Intake performs deterministic asset-overlap and time-
window matching. One active unambiguous match returns the reviewed notice without
an investigation; multiple matches are listed without model ranking. Expired,
resolved or version-mismatched issues remain audit history.

No freeze, new variant, unfamiliar-domain claim, permission expansion or execution-
reader elevation is part of this milestone.
