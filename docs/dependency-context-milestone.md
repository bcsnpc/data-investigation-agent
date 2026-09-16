# Native dependency calculation contexts

Review: [PR #186](https://github.com/bcsnpc/data-investigation-agent/pull/186).

PR #184 is merged. This grouped milestone is tracked by [#185](https://github.com/bcsnpc/data-investigation-agent/issues/185).

A measure can change filters before evaluating its components. Reading every child under the original ticket filters could therefore show an unrelated component value. The investigator now derives supported filter paths from retained model definitions and asks Power BI to evaluate the child in that calculation context. No metric names, expected values or local DAX evaluator are added to the agent.

## Delivered together

- Metadata parser for neutral arithmetic/DIVIDE dependencies and top-level CALCULATE of a direct measure with up to eight typed equality predicates, including KEEPFILTERS.
- Nested paths across measure definitions, with native wrapper order preserved. Paths are bounded, acyclic and definition-bound.
- Separate candidate identities for the same child reached under different filters. A contextual child unlocks only after its exact parent candidate; its breakdown unlocks after its contextual scalar.
- Context retained in sealed native receipts, adaptive observations and planner input. The local workspace reviews supported filter changes before start and labels the calculation path beside values.
- Explicit holds on contextual source comparison and record reconstruction. An ordinary source count cannot silently be treated as equivalent to a transformed child.
- Operator-only durable verification CLI, context regression tests and the expanded browser workflow.

CALCULATE replaces existing filters on the same columns by default; KEEPFILTERS intersects them. These transformations remain native Power BI operations. See Microsoft's [CALCULATE](https://learn.microsoft.com/en-us/dax/calculate-function-dax) and [KEEPFILTERS](https://learn.microsoft.com/en-us/dax/keepfilters-function-dax) documentation.

## Verification

All 795 regression tests passed. Twenty focused tests cover typed constants, replacement/intersection, nested paths, repeated children, ambiguity, unsupported syntax, stale definitions, candidate gates, receipt persistence and zero-query replay. The browser harness passed 14 checks including context review and result labels, with five injected native calls and zero live calls. Browser values are test injections, not semantic parity evidence.

An isolated ten-row Import fixture was published and refreshed, with its contents checked. Workspace `149f8d99-1c66-4a0a-9624-759be002bb60`, model `5f2afb96-157e-46ab-9fcb-b56a2bb37fba`. The dedicated reader was granted Viewer and Read/Build only in this additional fixture workspace/model. The business model and Azure deployment were unchanged.

Eight native reads completed under the dedicated reader, run `51a54f86-429a-4947-b0c4-e1452c6b5029`. With the ticket filter Refunded=false:

| Read | Native value |
| --- | --- |
| Replacing parent / contextual child | 2 / 2 |
| Intersecting parent / contextual child | BLANK / BLANK |
| Nested parent / contextual child | 2 / 2 |
| Ordinary base count | 8 |
| Ratio | 0.25 |

All eight matched separately held evaluator expectations. Completed replay and history made zero cloud calls. Definitions use a fresh name suffix; the engine receives definitions and scope, not the evaluator answers. This is operator-manifest fixture verification, not production report onboarding or hidden Phase H acceptance. Local artifacts are under `.local/dependency-context-*`; credentials, databases and generated fixtures remain untracked.

The actual Azure LLM planner also completed session `684e00fa-b124-4494-9f8b-f0475b846fc2`: parent -> contextual child -> contextual base, using three planner calls and three reader-bound Power BI queries. It retained two contextual observations and stopped with `NO_ADMITTED_TEST`; the outcome correctly remained insufficient evidence for a verified cause. No expected answers were provided to the planner. Across this milestone, diagnostic runs used eleven native queries, plus the publisher's separate fixture-content verification. No SQL queries or Azure deployment changes were made.

## Boundaries and next work

Supported equality contexts are a bounded expansion of D/E/G, not completion of complex DAX coverage. Inline nested CALCULATE within one definition, table filters, date/relationship switches, iterators, conditionals, arbitrary expressions and report/page/visual/RLS capture remain unsupported for contextual decomposition. The selected root can still be evaluated natively where admitted; unsupported decomposition remains a gap.

Effective identity/context, exclusive publication and shared source/model generation remain unproven. Contextual values do not establish source equivalence or a verified cause. `cause_verified`, `generation_proven` and `live_acceptance_ready` remain false.

Next grouped work remains: effective-context and publication/generation prerequisites; broader dependency semantics with evidence-backed causal verifiers; all eight Phase H acceptance families; business screenshot/report intake and hosted authorization; reviewed handoff and Azure v2 deployment. The existing Azure bounded-v1 application remains the deployed baseline; the v2 workspace is local.
