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
`NO_COMPARABLE_PATH`, `DEFINITION_DIFFERENCE`, `SCOPE_DIFFERENCE`, `DIFFERENT_SUBJECT`,
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
three-run smoke results follow.

## Three-run known-domain smoke

PR #227 merged as `c52673a` after all six CI checks passed. Exactly three G trials
then ran under identical known-domain conditions with recording enabled. Each
ended at procedure step 6 as `CONSISTENT_TO_BOUNDARY`, established the presentation
baseline with the verbatim query `EVALUATE ROW("baseline", [Handled Quantity])`,
made one DAX read, no SQL reads and no investigation-planner calls, and reported
the Activity semantic table as the deepest visible layer with `NO_LINEAGE` below it.
All three syntheses validated.

| Trial | Outcome / step | Reads SQL / DAX | Baseline | Visibility stop | Synthesis |
| --- | --- | ---: | --- | --- | --- |
| P1 | `CONSISTENT_TO_BOUNDARY` / 6 | 0 / 1 | Established | Activity / `NO_LINEAGE` | Valid |
| P2 | `CONSISTENT_TO_BOUNDARY` / 6 | 0 / 1 | Established | Activity / `NO_LINEAGE` | Valid |
| P3 | `CONSISTENT_TO_BOUNDARY` / 6 | 0 / 1 | Established | Activity / `NO_LINEAGE` | Valid |

All six intake/synthesis tapes passed hash and length verification with complete
request and response bodies and no exclusion. Synthesis digests were 3,308
characters each. The original daily policy remained unchanged and all 156 usage
records are settled. [Machine-readable results](runs/process-debugging-smoke.json)
retain the sessions, queries, boundaries and tape IDs.

Compared with #226's nine runs, investigation-planner calls fell from 97 to zero,
SQL reads from 25 to zero and DAX reads from seven to three. Explicit baseline
establishment rose from 0/9 to 3/3 and valid syntheses from 5/9 to 3/3. This is a
smoke test of one branch. It shows reliable baseline and boundary reporting; it
does not show multi-layer divergence localization or source-mechanism analysis.
The subsequent review found that the three `CONSISTENT_TO_BOUNDARY` labels were
invalid because no comparison executed. Their receipts remain historical evidence;
the corrected contract and binding analysis are in
[no-comparable-path correction](no-comparable-path-correction.md).

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
3,308 characters in each of the three trials.

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

## Corrected zero-comparison follow-up

The first smoke's three `CONSISTENT_TO_BOUNDARY` outcomes were invalid because no
boundary comparison executed. PR #229 adds `NO_COMPARABLE_PATH` and the stricter
comparison contracts described in the
[correction](no-comparable-path-correction.md). Exactly three corrected recorded G
runs each stopped at step 3 with zero resolved boundaries and comparisons, one DAX
baseline of 8,765, no SQL read and no investigation-planner call. The specific
barrier is `CAPABILITY_UNAVAILABLE`: Activity's `dbo.movement_values` partition
label has no stable discovered asset binding under the declared scope. There was
no `NOT_COMPARABLE` event because the first adjacent boundary itself was unresolved.
All three syntheses and all six tapes validated. These results replace no historical
receipt and make no freeze or unfamiliar-domain claim. See the
[machine-readable review](runs/no-comparable-path-corrected-smoke.json).
