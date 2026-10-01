# Freshness context precondition and isolated filter-fixture plan

Date: 2026-10-01 (client date). #290 merged after six green checks at
`e8d99c9e39736e0d530644f20d53183af2b7886d`.

## Implemented: context equivalence before comparison-based freshness

An unchanged declared source proves the quantity's expression, not the context
of the two reads. The freshness classifier previously accepted that proof without
checking explicit per-read context. The Microsoft adapter already refuses filtered
independent lower reads; this was a missing engine/outcome precondition, not a new
live demonstration of a filtered Microsoft comparison misclassified as freshness.

Completed adapter evidence now records the compiled whole-entity declared context.
The boundary observation carries both read contexts. The deterministic
REFRESH_LATENCY rule requires both to be explicit, equal, supported whole-entity
contexts, and requires the requested scope to have no filters or dimensions.
Missing context is unknown. Two identically filtered declarations are not admitted:
this narrow rule does not implement faithful filter translation.

Final outcome validation independently checks both contexts against the ORIGINAL
completed read observations. Changing only the comparison's context, removing a
read's context, or forging a fresh outcome over those records fails validation.
The source-expression proof, no-intervening-transform proof, distinct surfaces,
attestation, divergent quantities and missing-timestamp limits remain necessary.
Other procedures retain their existing gates; no report-context parsing or tests
were added. This context is the query's declared scope, not a claim that the user's
report selection or RLS membership has been captured.

The comparison-context evidence remains in original observations used by final
validation. It is not added to the model's narrative payload. Synthetic contract
audit: process-evidence projection is exactly equal before/after, 657 characters
under the same serializer; directory entries 0/0 and SQL directory objects 0/0.
This phase has no directory. No prompt, provider schema or input-budget change.

Focused checks: 15 refresh-comparison tests, 18 independent-lower tests,
43 process-debugging tests and 32 synthesis tests passed. An initial adapter test
found a duplicate context insertion referencing scope outside its method; that
implementation error was corrected before the full suite. All 1,327 full regression tests passed in 421.367 seconds (exit 0);
database resource warnings remain visible in the retained log. No live investigation or estate request.
No recorded historical observations are rewritten or upgraded to satisfy the new
precondition. Engine changes invalidate earlier freezes.

## Proposed estate change: separate report with real predicates

This is a plan, not authorization to mutate the estate. Prefer a new report item
bound explicitly to the existing semantic model in the already approved workspace.
Do not edit the original reports, model, data, partitions, refresh settings,
permissions or schedules. Creating a report uses the existing publisher identity,
never the execution reader. Microsoft's [Create Report API](https://learn.microsoft.com/en-us/rest/api/fabric/report/items/create-report)
requires a workspace Contributor and write scope; the diagnostic identity must not
be elevated for publication.

The existing [fixture report publisher](../acceptance/unknown_domain/publish_reports.py)
can publish PBIR definitions, but its main path also creates a semantic model.
Do not run that whole path to add this fixture. Use a separately journalled,
report-only publication operation with the existing model ID. This is publisher
work only, not a domain route or mapping in the engine.

Suggested contents:

- An unfiltered control page referencing the same real measure.
- A test page with native categorical slicers set to real, present values from
  existing model columns. Select values after inspecting the model and bounded
  data evidence; this plan does not invent values or assert which available fields
  will discriminate. Store the actual saved selection predicates, not just the
  slicer projections, label or dropdown formatting.
- A target card with an additional explicit visual-level predicate. Add a
  predicate-carrying page filter too, so composition across page and visual scope
  can be checked. Include a companion card without the extra visual predicate
  to distinguish a visual-only effect.
- One REPORT bookmark with Data enabled that changes a slicer to another existing
  value and targets the test page/visuals explicitly. Capture complete supported
  state, with suppressData/target-visual settings checked. A personal bookmark,
  bookmark name alone, or display-only bookmark is not a predicate fixture.

Authoring choices: Power BI Desktop/PBIP provides a native way to save slicer
selections and report bookmarks; export the resulting PBIR and inspect it. A
fixture-only extension to the existing definition generator is also possible,
but it must emit and validate real semantic-query predicate ASTs and bookmark
explorationState against their declared schema versions. Prefer native authoring
for the first fixture, then retain the exported definition as the publisher
artifact. Neither route requires a new model or data mutation. The report shares the
existing model's serving state and normal platform caching/framing behavior; it
is not a separate data snapshot. No refresh/reframe is requested. Before/after
value checks preserve the observed baseline but cannot attest a served version.
[PBIR files](https://learn.microsoft.com/power-bi/developer/projects/projects-report),
[report bookmarks](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-bookmarks),
[bookmark schema](https://raw.githubusercontent.com/microsoft/json-schemas/main/fabric/item/report/definition/bookmark/1.0.0/schema.json).

## Verify the estate fixture before building the capability

Future authorized publication should record original model/report IDs, definition
hashes and the original reader baseline before and after. Retain the exact
published report parts and retrieve the SERVED report definition to verify:

1. The dataset binding resolves to the existing model, with no new model created.
2. Page/visual filters carry actual filter predicates and typed values.
3. Slicer default selections survive publication and apply to the target visual;
   interaction/sync settings are explicit.
4. The returned report bookmark includes its saved predicates and data-applicability
   options. If it is absent, unsupported or display-only, the fixture is not ready.
5. The control, selected and bookmarked displays discriminate as intended, with
   formatting/rounding noted. Capture those native observations under explicit
   publisher/evaluator identity provenance; do not put expected totals in runtime
   configuration or claim they were investigator-reader receipts.

The published artifact must be discoverable through ordinary definitions. Opening
or merely naming a bookmark is not proof of its retained predicate. Baseline
verification and any future native display/read checks need their own bounded
read allowance; none is spent or proposed as already authorized here.

## What changes or is invalidated

| Item | Effect of adding the isolated report |
| --- | --- |
| Existing baseline | Original report/model definitions and data are intended to remain byte-identical. Verify the original quantity before/after; do not assume a value or imply currency. The new report is a separate artifact. |
| Discovery | Rescan the approved workspace and fetch the new definition. A new immutable discovery/context version includes the report, pages, visuals and bookmark DefinitionParts. Previous versions remain historical and cannot show the new fixture. |
| Projected model context | enterprise_discovery.project includes all explicitly bound discovered reports and definition hashes. The existing model can therefore receive a new context ID/revision even though its calculation definition is unchanged. |
| Whole-config policy approval | adaptive_candidates validates discovery.policy_hash against the entire config digest. A new report in the already approved workspace need not change config or invalidate this hash. If scope/config is changed for any reason, matching re-approval is required; do not narrow the hash. Record policy/config hashes around discovery. |
| Intake/preview/scope approval | Old previews pin catalog/context/engine hashes; old envelopes pin model revision/context ID. Recreate intake and review against the new context. Matching config approval does not make an old preview current. |
| Reader access | Existing workspace Viewer and model Read + Build may suffice for the additional report/model reads; confirm actual coverage. No new reader grant is assumed or authorized by this plan. Metadata collection stays on its distinct approved identity. |
| Recorded runs/tapes | Keep all prior runs exactly as recorded. They remain evidence for the prior engine/context and cannot validate the added predicates. Payload-changing new contexts do not byte-match old tapes. New runs are known-domain regressions, not fresh-domain acceptance. |
| Freeze | This engine precondition change already invalidates previous engine freezes. Adding the report is also an estate change and cannot be inserted into a completed frozen attempt as though it were the original variant. |

Creating the separate report is additive. If removal is later authorized, delete
only the recorded new item and rescan; retain its historical publisher, context and
run receipts. No restoration of data is required because the plan performs no data
mutation. The filter reproduction capability remains unimplemented pending the
user's decision about the fixture.
