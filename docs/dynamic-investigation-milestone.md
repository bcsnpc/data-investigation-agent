# Dynamic reasoning and governed diagnostics

2026-09-18. Grouped Stages 4–5, [issue #197](https://github.com/bcsnpc/data-investigation-agent/issues/197),
under [mission #193](https://github.com/bcsnpc/data-investigation-agent/issues/193).
See [current status](current-delivery-status.md) for the active milestone.

## Delivered behavior

Discovered models use `dynamic-investigation-v1`. The planner can retrieve graph
assets and definitions, propose SQL or DAX, use existing typed diagnostics, ask a
material question or stop with a qualified assessment. Observations can change
the next tool and hypothesis; there is no mandatory report-to-source order.
Legacy manually registered investigations retain their existing behavior.

SQL is parsed and bound with SQLGlot against approved catalog objects. One
SELECT/CTE, explicit syntax/function allowlists, approved schema/table references,
parameterized values, four joins, sixteen output columns and bounded results are
enforced. Views and computed columns are currently excluded. The SQL worker checks
effective database/object permissions before executing proposed queries; elevated
identities fail closed. TOP is a result bound, not a scan-cost guarantee.

DAX uses a recursive parser over the shared lexer, approved model references and
an explicit function/grammar subset. It permits one EVALUATE expression, not write
commands or arbitrary DEFINE blocks. Power BI executes it using the isolated
reader. Unsupported grammar is reported rather than approximated locally.

Both tools use existing durable dispatch, context/policy checks, reservations,
receipts, cancellation and replay controls. Result bytes, rows and time remain
bounded. Exact numeric values are retained. Query rejection is feedback for a
revised proposal, never permission to bypass validation.

The workspace permits a budgeted global question for discovered models. Business
cards distinguish diagnostic results from the originally selected metric; the
technical view retains decisions and receipts. Suggested explanations are labelled
LLM_INFERRED and are not verified causes or confirmed business intent. Non-gap
assessments require complete query evidence and explicit alternatives/limitations.

## Verification

- All **891** regression tests passed, including the required generator tests and
  15 new parser, permission, dynamic-path, cancellation, context-change and receipt tests.
- Live generated DAX returned Base=10, Replaced=2, Kept=2, Outer=2 and Ratio=0.2
  in one native read. Session `ecb91c60-a609-44a7-8d1f-90d713b78aa5` completed
  after three planner turns; receipt `4646fbf8-46f1-434f-af7a-de360fa6d486`.
  The explanation cited the observed ratio and preserved business-intent uncertainty.
- Live source investigation first retrieved context, then proposed SQL comparing
  total and distinct customer IDs: both **20,000**. Session
  `46061abd-15c7-469c-8eaf-5f3bd4b5f1a4` completed in three planner turns and
  one SQL call with the worker's read-only permission checks passing.
- Earlier live attempts failed on conflicting action fields and Decimal result
  serialization. These failures prompted disjoint structured-output action shapes,
  recoverable contract feedback and exact-number result serialization. They are
  retained locally; the successful reruns do not imply broad LLM reliability.

Browser checks and final PR verification are recorded in current status/progress.
Local artifacts live under `.local/enterprise-discovery/`; they are not credentials
or fixtures to copy into runtime configuration.

## Boundaries and next acceptance

This is dynamic investigation on supported grammar, not generality acceptance.
The live examples used an existing isolated fixture and the existing source.
No unknown domain has yet been published after an engine freeze.

Remaining limits include one connection profile, a selected semantic-model anchor,
bounded initial ticket context, unsupported SQL views/DAX grammar, no independent
verification of causal mechanism/business intent, and local single-operator hosting.
Warehouse endpoint catalog support and permanent scan scheduling remain pending.
Hidden report selections/RLS and cross-system equivalence are never inferred from
matching names or values. The engine cannot issue VERIFIED_TECHNICAL_DEFECT yet.

Next: freeze the engine and policies, then publish and discover an unfamiliar domain
and run the nine-family challenge, including failed-hypothesis revision and change/
permission experiments. If engine behavior needs fixing, invalidate the attempt,
refreeze and use a fresh variant. Keep publisher/evaluator truth outside runtime context.
