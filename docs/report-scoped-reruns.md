# Report-scoped reruns: intake progressed, reproduction did not

2026-10-02, America/Chicago. Three unchanged saved tickets, one attempt each,
KNOWN_DOMAIN_REGRESSION. This is failure evidence, not a reproduction or
unfamiliar-domain acceptance pass. No engine or adapter changed during the batch.

## Merged implementation and validation

| Work | PR | Merge | Checks |
| --- | --- | --- | --- |
| Report-scoped consumer contract and appended #304 correction | [#308](https://github.com/bcsnpc/data-investigation-agent/pull/308) | c109b30 | Six green |
| Report-scoped scalar cells and observed value lookup | [#309](https://github.com/bcsnpc/data-investigation-agent/pull/309) | 05a63bf | Six green |
| Field-aware quotes and one metered figure-quote repair | [#310](https://github.com/bcsnpc/data-investigation-agent/pull/310) | 73cfe44 | Six green |

PR B passed 1,550 local tests. PR C's first full-suite process was interrupted
before a result; its partial log is preserved. The resumed suite passed all
1,558 tests in 451.705 seconds. The exact-head six CI checks passed before each
merge. No live run occurred before PR C merged. The batch changed documentation
and appended ledger rows only; prior freezes remain invalidated by the preceding
implementation work. No new freeze or variant was introduced. The earlier [runs round](declared-context-runs-round.md), [quote-provenance reruns](quote-provenance-reruns.md) and superseded draft #297 retain their evidence unchanged.

## Unchanged conditions

Pinned model context: `3ae7607b-5a5e-46c6-8e1b-195dbabc9cae`.
The sessions separately record enterprise discovery projection
`a786eef2-d4fc-43a9-b5e3-2a6a1ee0774a`; these are distinct recorded identifiers,
not a new scan. Whole-config approval hash:
`19e2ef0b0b5cb6bfd8df38c5fded6c1eaac40718b3926248ac62c61abf0cf8b6`.
No recollection, reapproval, fixture change, permissions, schedules, cap or policy
change, credit grant, refund or counter reset.

The original ticket bytes were copied unchanged into a new artifact folder and
assigned new request keys. SHA-256:

- R1: `af4602acdd2a6c8bdb74892a86c4346ac957ba2ed158aeb108412f1952959e84`.
- R2: `c85cf7e9c521e40738855c70558f4b5d397e88df3a808bc932ef4f57a62275be`.
- R3: `a49412fa60ec95d487b225cb28bf710a288ab6448fd1a094390e2fddadfd8bc4`.

The existing quality deployment and intake settings were unchanged: 1,500 output
tokens per intake call, no explicit intake reasoning request. Investigation
profile, depth ceiling three, diagnostic cap four and cumulative input allowance
384,000 characters were unchanged. No investigation planner call was needed or
made. No provider retry or quote-repair call occurred.

## Per-run results

All three intakes were PROPOSED, with exact STATED report binding. The procedure
sessions are terminal COMPLETED with NO_KNOWN_PATTERN, but **none is a completed
end-to-end answer**: selection resolution refused, reproduction did not run, and
synthesis is BLOCKED. A terminal procedure status is not a correctness pass.

| Run | Investigation session | Reported state | Actual selection-resolution stop | Diagnostic / physical / guard requests | Intake / investigation planner / synthesis provider calls |
| --- | --- | --- | --- | --- | --- |
| R1 | f90928fb-732a-4bf7-a5f2-f72419c87ace | UNSPECIFIED | VALUE_EXISTENCE_RESULT | 1 / 1 / 0 | 1 / 0 / 0 |
| R2 | 480a603a-aea6-426d-9135-6eeb96ea2f83 | EMPTY | No scoped grouping column can test the extracted literal | 0 / 0 / 0 | 1 / 0 / 0 |
| R3 | cb751286-0cb1-4926-bacd-c686ced5ddbb | NUMBER, exact 9 | No scoped grouping column can test the extracted literal | 0 / 0 / 0 | 1 / 0 / 0 |

### R1: Family D, not the no-reported-figure result

Intake `c8858c69-cdb8-4ab5-9384-d847e03c7afa` named Inventory Health e1b8e1
exactly, span 3:26. It extracted **`warehouse North`**, span 38:53, as the
selection value. This is a valid quote, but it is not the literal `North`.
The bare-value resolution therefore tested that full phrase in the report's
grouping column. No foreign report's North predicate was substituted.

One compiled native existence read completed, receipt
`f892f38c-7779-4dbf-b46c-4c62683f9d82`, at 22:49:06 UTC. It returned one typed
BLANK quantity, not string `0` or `1`. The adapter accepts only those two strings
for existence and raised the exact refusal:

> Unsupported declared restriction form VALUE_EXISTENCE_RESULT; faithful translation required.

`COUNTROWS` over an empty table legitimately returns BLANK. This exposes an
unhandled native empty-result case in code intended to perform existence checks;
it is not evidence that the report contains an unsupported declaration. The
recorded refusal wording is preserved. No claim that North was absent follows:
the queried literal was `warehouse North`, not North.

Requested execution surface: OLAP Server, workspace
`149f8d99-1c66-4a0a-9624-759be002bb60`, model
`3484a2bc-98c5-4cef-be5c-a6215484075e`, reader
`investigator-reader@skynwhy.com`. The sealed transport identity records that
isolated account, principal `8a582d2a-ecb4-4320-bf72-75a529a0d382`, workspace and
model. This is transport provenance, **not** the surface's self-report.
The sealed normalized result has `surface_report: null`. It supplies no usable
quantity-bound self-report to quote for engine, identity or object. The adapter
raised before constructing an existence Probe; no attestation grade, successful
OBSERVED resolution or surface-difference grade was established. Missing
self-description is not reclassified as permission denial.

The physical receipt remains stored and counted even though no corresponding
accepted process observation was produced. No candidate quantity, totals-row
value or undeclared-context quantity was computed. R1 consequently did **not**
reach the requested no-reported-figure unavailability; UNSPECIFIED passed intake,
then an earlier lookup refusal stopped it.

### R2: EMPTY passed intake, not reproduced

Intake `22ac82a4-35dc-43a1-92ac-a885cc30ed6e` named Declared predicate fixture
20261001 exactly, span 3:38. The EMPTY source is verbatim span 71:157:

> the card Handled Quantity - extra visual predicate shows nothing (the visual is empty)

Both occurrences of `Handled Quantity` were recorded as measure provenance.
The former repeated-measure hold is gone for this attempt. However, selection
extraction again produced `warehouse North`, span 191:206. No ACTIVE literal
equals that phrase. The report's projecting cards have no grouping columns for
an OBSERVED fallback search, so resolution refused without a read:

> Target ambiguity: no scoped grouping column can test the stated value.

There is no EVIDENCE or OBSERVED binding, no compiled cell evaluation, no
undeclared-context or reproduced value and no REPRODUCED label. The fixture's
ACTIVE North restriction remains present; it was not erased, but the extracted
phrase did not match it. No transformation, presentation logic, business-correct
number or active user selection was established.

### R3: exact 9 passed intake, not compared

Intake `77c043db-851e-4c81-bc65-1d3b8e7da9ce` retained the same STATED report
binding. The NUMBER source, span 122:150, is:

> shows 9 for Handled Quantity

The consumer derived value `9` and EXACT precision. Both occurrences of the
measure quote were recorded. No tolerance or quote retry was involved.
Selection extraction was again `warehouse North`, span 163:178. Resolution
refused for the same no-grouping-column reason as R2, with zero estate reads.
No NOT_REPRODUCED result or explanatory verdict was produced. Passing figure
provenance does not establish that a figure was compared.

## Inventory and conservation evidence

The procedure's `_prepare` calls `validate_inventory` for every candidate before
attempting selection resolution. R1's lookup and R2/R3's later named resolution
refusals establish that those gates returned rather than throwing. However,
the inventories are **not durably attached to these refused runs**: the
resolution evidence marker is constructed only after successful resolution.
That is an evidence-retention limit, not a license to invent a live manifest.

A separately labelled, read-only inspection rebuilt the inventories from the
same pinned local definitions with the unchanged merged adapter, and called the
engine validator. This made no provider or estate call and is not a replacement
investigation. Its counts below are reconstructed retained-context evidence;
they must not be described as newly sealed live-run inventory receipts.

| Report / candidate context | Discovered | ACTIVE | CONDITIONAL | UNSUPPORTED | Engine conservation in local audit |
| --- | --- | --- | --- | --- | --- |
| Inventory Health, visual 25189fcc5fe05539b3b6 | 1 | 1 | 0 | 0 | Passed |
| Inventory Health, visual d21708a8bc35561c81f5 | 1 | 1 | 0 | 0 | Passed |
| Predicate fixture, unfiltered control c35f95e493de5d258b64 | 9 | 0 | 9 | 0 | Passed |
| Predicate fixture, saved selections 7b8db703ca845710aca9 | 9 | 3 | 6 | 0 | Passed |
| Predicate fixture, extra visual predicate a32b6a48db655ac8a4f2 | 9 | 4 | 5 | 0 | Passed |

These are dispositions per candidate context, not a union or 27 distinct
declarations. Inventory Health's one declaration is ACTIVE FULL_DOMAIN, empty
restrictions, VIEWER_CHANGEABLE and SAVED_DEFAULT. It does not declare North.
No predicate from the fixture report enters Inventory Health's inventory.

For the fixture's saved-selection candidate, ACTIVE restrictions are product
Component 1 (volatile slicer default), movement type RECEIPT (fixed page filter)
and warehouse North (volatile slicer default). The extra-visual candidate adds
event day 2026-09-14 as a fixed visual filter. The control candidate has no ACTIVE
restrictions. Stored bookmark alternatives and declarations applicable to other
candidate contexts are CONDITIONAL and excluded. UNKNOWN forms were not taught
to the adapter during this batch; none appeared in this reconstruction.

## Comparisons, synthesis and verbatim outputs

For every run: zero boundary comparisons, zero within-layer reproduction
comparisons, zero verified cross-surface comparisons, no snapshot grade and no
definition judge call. The same four path boundaries remain unchecked: semantic
presentation to its declared source, source to the upstream movement entity,
that entity to its earlier input, and the unresolved application-source boundary.
The first three were not reached because selection resolution terminated first;
the last has no declared upstream quantity binding in the fixture. The
lower-layer filtered-scope refusal was unchanged and not exercised after these
earlier stops.

Synthesis was invoked as a procedure step in all three sessions, but its frozen
digest failed before admission or dispatch. Stored status: BLOCKED; calls: 0;
safe error category: Conflict. A read-only build of each saved digest reproduced:

> Unsupported process receipt shape

`synthesis_digest._process_evidence` admits reproduction markers and specific
comparison statuses; it does not admit the newly emitted
`REPORT_SELECTION_REFUSED` observation. This is another interface coverage
defect, not a provider response failure. No model was asked to synthesize these
refused observations. The saved sessions and errors were not edited.

| Run | Business output, in full | Technical output, in full |
| --- | --- | --- |
| R1 | Not generated: synthesis BLOCKED before provider dispatch. | Not generated: synthesis BLOCKED before provider dispatch. |
| R2 | Not generated: synthesis BLOCKED before provider dispatch. | Not generated: synthesis BLOCKED before provider dispatch. |
| R3 | Not generated: synthesis BLOCKED before provider dispatch. | Not generated: synthesis BLOCKED before provider dispatch. |

Those are absence reports, not invented narrative text. There are no verbatim
business or technical narratives to paste. The assumed-slicer-default weaker
claim and moved-slicer open-set renderers therefore remain unverified live.
NO_KNOWN_PATTERN is the procedure's fallback label; it does not make the stopped
question answered or certify the target resolution.

## Independent derivation and honesty

R2's EMPTY and R3's 9 are fixture-authored, not observed user figures and not
transcriptions of the engine query. The previous independent notebook-seed proof
is unchanged, hash
`3a980c4bd1920343202174c26b357be6233c6db267409d226d6a95fca4694273`.
Every intended active restriction is included: page RECEIPT, visual 2026-09-14,
saved warehouse slicer North, saved product slicer Component 1. Lookup maps
warehouse/product to IDs 1/1. The only movement matching date and both defaults
is movement 300, 9 units, ISSUE. RECEIPT excludes it; no selected row remains.
SUM with no zero coercion is BLANK, not 0. The 9 figure was chosen from that
excluded movement, with this rationale kept outside runtime ticket context.

No expected reproduction/no-figure/non-reproduction result occurred, so there is
no successful result to declare inevitable. The arithmetic never guaranteed
execution, correct literal extraction, faithful compilation, a served value,
surface self-report or comparison validation. This batch stopped before testing
that arithmetic. Changing data, measure semantics or retained predicates could
also change the expected quantity; none was changed here.

## Budget, recording and remaining findings

Rolling physical allowance: 21/60 before, 22/60 after, 38 available. Each run's
diagnostic usage was 1/4, 0/4 and 0/4 respectively. One physical DAX request total;
zero SQL, other diagnostic or guard requests. Nothing stopped at a read cap.
Three intake calls: 42,659 input tokens and 321 output tokens, with 4,500 output
tokens reserved and no refunds. All three reservations settled; the sole read
also settled. Investigation planner calls zero; synthesis provider calls zero.

Three exact request/response tapes were captured with no recording exclusion or
provider error. Original HTTP bodies, terminal intakes, sessions, query receipt,
console logs, before/after usage snapshots, ticket hashes and read-only audits
remain under `.local/report-scoped-reruns-20261002/` and the existing recording
store. Exactly three new ledger rows were appended; all previous evidence stays
unchanged.

The newly exposed limits are literal extraction using a surrounding phrase,
unhandled BLANK in the existence result, missing usable self-report on that
read, inventory retention on a refused resolution, and synthesis's unsupported
refusal receipt. No replacement run, mid-batch correction, new native form,
permission or fixture mutation was used to turn these stops into successes.
The batch stops here, before the deferred date-predicate fixture change.
