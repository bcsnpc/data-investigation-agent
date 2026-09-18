# Investigation quality engineering

Tracking: #193 and #199. Current implementation status remains in
[current delivery status](current-delivery-status.md).

## Research and decisions

Reviewed 2026-09-18:

- [Anthropic: writing effective tools](https://www.anthropic.com/engineering/writing-tools-for-agents)
  recommends evaluation-driven tool design, concise context, and actionable
  errors. Apply this through definition navigation, bounded content retrieval,
  explicit tool history and recovery signals rather than business-specific tools.
- [OpenAI: evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
  distinguishes variable model behavior from ordinary software testing. Keep
  deterministic boundary tests and live behavioral evaluations separate, and
  record failures rather than equating green unit tests with agent quality.
- [Anthropic: demystifying agent evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
  supports evaluating both outcomes and trajectories. Track repeated lookups,
  rejected actions, recovery, tool evidence and limits; these are diagnostic
  indicators, not an automatic correctness grade.
- [OpenAI: GPT-4.1 guidance](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-4.1)
  discusses planning between calls. This project retains concise test objectives
  and evidence summaries only, not private chain-of-thought. Tool choice remains
  dynamic; no predetermined Power BI-to-source investigation sequence.

## Model experiment

The user authorized stronger models if useful. Azure offered GPT-4.1, GPT-5-mini
and GPT-5.4 in the account's regional catalog. A separate GlobalStandard GPT-4.1
2025-04-14 deployment, `investigator-quality`, was created at capacity 10 for a
controlled comparison with GPT-4.1-mini. The existing default deployment remains
unchanged. Both use the same 1,500-output-token contract, isolated readers,
query validation and run/daily budgets. A single trial cannot establish superiority.
No SQL quota, production data or reader permissions were changed for this work.

Evaluator configuration can select the model deployment and records that choice
with each trial. Existing v2 assets are known-domain regressions. Engine changes
still require a fresh freeze and fresh published variant for acceptance.

## Observed context problems

Notebook parent assets contain item metadata. Code resides in separate
DefinitionPart children; opaque graph links alone make those children difficult
to navigate. Large definitions are currently reduced to head/tail JSON excerpts,
which may omit relevant code and cannot be paged. Repeated lookup results add
receipts without adding information. These are general context/tool problems;
fixing them must not encode warehouse table names, metric formulas, defect labels,
expected values or a required investigation route.

## Implemented changes and trial evidence

DefinitionPart content now supports bounded character pages and literal search;
parent lookup returns labelled children. Unicode escaping is included in response
budgets, and unsupported/non-current targets fail closed. These are read-only
metadata tools, never code execution. Repeated identical lookups under one context
version are marked with the prior receipt and count toward no-progress; a new
lookup resets that counter. The planner sees bounded recent actions and remaining
budgets. Stored evidence remains unchanged. Strategy version is v3; no new freeze
yet exists.

The evaluator accepts an explicit Azure settings file and records its deployment.
`acceptance/unknown_domain/score_run.py` summarizes trajectory signals while
explicitly leaving business correctness NOT_GRADED. It reads no evaluator truth.

GPT-4.1 baseline `fdfb386a-eefb-42a5-bd63-cea755faed7a` stopped HELD /
USAGE_LIMIT after four planning calls, four metadata lookups (three distinct), and
zero data calls. This used the pre-navigation engine and cannot compare the new
tools. Today's shared output reservation limit was reached; it was not reset or
bypassed. User approval for an additional 20 bounded calls is pending.


Model configuration is secret-free in `infra/llm/quality-evaluation.json`.
Use `--azure-settings infra/llm/quality-evaluation.json` with the evaluator for
an explicitly marked known-domain regression. Frozen trials require the selected
settings path/hash to be included in the freeze; model substitution is rejected.
No keys are stored in this file. Deployment catalog availability is not proof of
quality or a guarantee that the deployed model will stay available indefinitely.

A stored-live-metadata probe navigated two notebook definition children, paged
20,528 characters, and found two literal `join` matches without SQL or LLM calls.
This proves tool reachability, not agent selection or diagnosis. Ten browser checks
passed with injected transport and no browser errors; the screenshot was inspected.


Validation: the full local suite passed 910 tests in 245 seconds. After the final
pagination-completeness and evaluator-freeze checks, six navigation tests and two
evaluation-boundary tests passed. Ten browser checks passed. No live LLM result
for the new navigation engine is claimed while daily budget approval is pending.
