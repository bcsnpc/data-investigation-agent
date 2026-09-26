# Self-Discovering Enterprise Data Investigator

An enterprise process debugger for Azure SQL, Microsoft Fabric and Power BI.
It has automatically discovered a newly published model and reports and made them
available for investigation without manual registration. Known-domain trials have
reached source mechanism evidence while preserving unknown business intent.
**Reliable investigation of unfamiliar domains has not passed acceptance.** The
target is to discover an approved environment and debug discrepancies by checking
whether each reachable process stage preserved a scoped quantity, using bounded
read-only queries and saved evidence. It reports implemented behavior and never
decides whether a business rule is correct.
This is an FDE integration with one enterprise environment.

Current result: review of the [correct-context three-run check](docs/correct-context-process-three.md)
found that both apparent semantic-to-Gold comparisons executed inside the same
Power BI model. They are requalified as within-model definition checks; the two
boundary claims and partial-pass statement are withdrawn without rewriting their
historical receipts. Probes now identify their engine, connection and object, and
consistency requires an equal comparison across distinct execution surfaces.
The existing reader cannot currently acquire a SQL-audience token for the Gold
analytics endpoint (`AADSTS65002`), so the active limit is
`NO_INDEPENDENT_LOWER_READ`. No permission was changed, and no freeze or unfamiliar-
domain acceptance pass is claimed.

An [execution-surface inventory](docs/execution-surface-inventory.md) then probed
which surfaces answer today, without changing the engine or any permission. Four
distinct surfaces responded: the Power BI semantic model via DAX, Azure SQL `app`
via the existing SQL reader, OneLake Delta commit metadata, and the first four
bytes of a OneLake data file. The Fabric SQL endpoint was not re-probed. No
lower-layer quantity was compiled or compared. The adapter's SQL reader
(`execute_source`) is still never called, and it can reach only Azure SQL
`app`, not the lakehouse table the process path resolves. The semantic model
is Direct Lake over that lakehouse. Whether a OneLake-file read would count as
independent, and whether the metadata identity may read rows, are open human
decisions.

The required three-run follow-up was launched after PR #235 merged, but all three
attempts failed before intake because the harness command omitted its required
`--environment` argument. They opened no sessions, made no provider or data calls,
and left usage unchanged. The failures are preserved in the
[checkpoint report](docs/independent-boundary-three.md); no fourth run was launched.

Current follow-up: the [process-debugging redesign](docs/process-debugging-redesign.md)
replaces open-ended search as the primary path. Intake distinguishes mismatch
complaints from business questions. A deterministic vertical procedure establishes
the presentation baseline, walks a discovered path of any length, compares only
faithfully translatable quantities, stops at the first evidence-bound explanation,
and always reports its visibility boundary. Thirteen closed outcomes bind claims to
required receipts and recommended actions. The adaptive loop remains the
`NO_KNOWN_PATTERN` fallback. The first three-run smoke established its baseline
and synthesis gates, then exposed an overclaim: zero comparisons cannot support
`CONSISTENT_TO_BOUNDARY`. The [corrected contract](docs/no-comparable-path-correction.md)
adds `NO_COMPARABLE_PATH`, requires real comparison evidence for verification
claims and distinguishes asset lineage from comparable-quantity bindings. Three
corrected runs stopped without a false consistency claim, but #232 later showed
they read the wrong discovery environment. Their missing-binding and structural-
limit conclusions are withdrawn. No freeze or unfamiliar-domain claim follows.

## What works today

- Related 100,000-order application data, Azure SQL source, deployed order portal,
  Fabric Bronze/Silver/Gold processing and native Power BI model/reports.
- Environment-owned metadata scans, per-surface coverage, versioned changes and
  evidence-backed context graphs. Supported discovered models/reports enter the
  ticket catalog automatically; manual registration remains a compatibility override.
- A deterministic vertical process debugger over adapter-provided discovered paths.
  It establishes a scoped presentation baseline, compares adjacent quantities,
  retains every query verbatim, exits early on an evidence contract and reports
  the deepest reachable layer. The adaptive LLM loop remains a bounded fallback.
- A local workspace with business questions, reviewed screenshot transcription,
  scope review, history, cancellation and shared business/technical evidence.
  Read-only identities, budgets and replay controls remain in place.
- The older bounded-v1 investigator and reviewed routing workflows remain available.

PR #192 is merged. Its count/sum diagnostic captures a native total and supporting
record groups together. Complete, empty and truncated live cases were checked;
this is arithmetic consistency, not general root-cause proof.

## How it works and what changes next

An operator approves a workspace/database profile once. Scans discover supported
models independently of reports and publish technical context without mandatory
business review. Explicit deny and the separate reader policy still govern access.
The complete target flow is:

```text
Approved connections -> recurring discovery -> versioned enterprise context graph
Business question / screenshot -> context resolution -> LLM hypotheses and tests
Policy + read-only tools -> real observations -> revised tests -> qualified outcome
Shared business/technical view -> human-reviewed handoff
```

Power BI remains the DAX engine. The LLM interprets context and chooses tests;
deterministic tools supply facts. New supported assets should require discovery,
not investigator-specific code changes.

## Current milestone and limitations

The redesign implementation passed **1,046 local regression tests**. Focused tests
cover all thirteen evidence contracts, arbitrary path length, early exit, explicit
`NOT_COMPARABLE`, intake triage, an end-to-end known-domain adapter run and all four
#226 synthesis failures. Planner golden payload content and directory coverage are
unchanged; only response schemas changed. The required three corrected recorded
G trials completed after PR #229 merged. All three reproduced 8,765, then stopped
at step 3 as `NO_COMPARABLE_PATH` with zero resolved boundaries, zero comparisons,
one DAX read, no SQL reads and no investigation-planner calls. #232 later proved
they opened `development` rather than the intended warehouse discovery context;
their missing-binding and structural-limit conclusions are withdrawn. All
syntheses validated and all six tapes passed integrity checks. The runs still
validate the false-consistency fix and refusal to name-match, but do not exercise
divergence localization or model judgment over a transformation definition. No
unfamiliar-domain acceptance pass is claimed. The corrected engine passes **1,052
local regression tests**; investigation planner payload content and coverage remain
unchanged.

The capability checkpoint merged with **1,073 tests and six green CI
checks**; the harness correction passed **1,074 local tests**. Its three recorded
runs each reproduced 8,765, but all used the wrong
catalog environment because of a hard-coded evaluator default. They consequently
made zero comparisons and ended at step 3. All failures remain recorded; one of
three syntheses completed, two failed validation, and all six tapes verify. The
harness now requires the exact discovery environment and has an isolation
regression. The later correct-context checkpoint above reached real equal
comparisons in two sessions; definition judgment remains unexercised because no
comparison diverged.

The previous separated-synthesis experiment is complete ([PR #222](https://github.com/bcsnpc/data-investigation-agent/pull/222)).
Three corrected known-domain G trials produced **3/3 receipt-supported uncertainty
assessments**, versus 0/3 in #221 arm A; one already had an assessment before
synthesis. No cause was verified. Two support fields were clipped, so explanation
quality remains incomplete. Three larger-input controls produced **0/3 assessments**:
two hit the planner-call limit and one stopped for no progress, with input available.
This small sample does not establish general reliability or rule out other bounds.

Synthesis uses one independently metered call over a deterministic frozen digest,
without the trajectory, directory or raw query-result rows. An initial metadata
excerpt defect was fixed; both initial completed attempts and the cancelled third
attempt remain recorded. Final validation: **1,026 local tests and six corrected
implementation CI checks passed**. The corrected batch's reference token cost was
**USD 4.08**, excluding intake/cloud costs; original daily policy was restored
without refunds. See [results, limitations and proposal](docs/separated-evidence-synthesis.md).

The earlier pooled G result remains **1 qualified conclusion in 15 runs** across
#220/#221, not a reliability foothold. Three independent synthesis passes were
**proposed only** and are deferred. Support preservation and the
nine-run calibration are complete; the next proposals await review.
Typed dependency traversal remains a later candidate, not implemented. Larger input
is an experimental control, not a new default. No freeze or unfamiliar-domain claim.

The following describes the completed #221 milestone:

The controlled twelve-run G experiment is complete. The
[offline trajectory audit](docs/g-trajectory-audit.md) showed genuine hypothesis
revision, with read admission preventing a final synthesis turn in prior G2/G3.
A once-per-connection registry preserves all 53 historical directory views:
F stays at **28 entries / 11 SQL objects**, with **477 added pre-wire characters**.
Saturated prompts omit the optional registry without evicting evidence. Dynamic
runs default to 15 reads; the experiment compared 6/15 reads and medium 8,000/high
16,000 output profiles while keeping other run limits fixed.

All twelve known-domain runs ended UNRESOLVED: **124 planner calls, 62 SQL + four
native reads, eight query rejections, zero provider errors and no qualified final
assessment**. Input admission stopped every higher-read run; two also exceeded the
per-call protected-context limit. No arm establishes improved conclusion
reliability. Reference-priced planner tokens cost **USD 8.86**, excluding intake
and cloud costs; this is not Azure billing. Original daily policy was restored
without resetting usage. SQL free-tier settings and provider capacity are unchanged.

Validation: **1,016 local regression tests and six implementation CI checks passed**.
See [results, context limits and concurrency proposal](docs/g-read-reasoning-experiment.md)
and [PR #221](https://github.com/bcsnpc/data-investigation-agent/pull/221) for final CI.
That milestone's input-sizing proposal has since been tested as a temporary control;
two-process investigation concurrency remains proposed only. The stopping
contract remains evaluated and not adopted. No freeze, new variant or unfamiliar-domain claim.
[Original #219 results](docs/physical-binding-reliability.md),
[negative stopping result](docs/stopping-criteria-review.md) and
[original nine-family SQL audit](docs/baseline-sql-proposals.md) remain historical evidence.

Item 1 of the ordered offline reliability plan merged in PR #209: opt-in exact
planner request/response recordings and loadable local fixtures. Recordings include
runtime context, budget and reservation metadata; credentials and headers are
excluded. Transport tests use no live LLM calls. See the
[recording runbook](docs/planner-call-recordings.md).
Item 2 merged in PR #210: planner-view goldens, counted omissions, preserved
links and deterministic fitting; 968 regression tests passed.
Item 3 merged in [PR #211](https://github.com/bcsnpc/data-investigation-agent/pull/211): a recorded-provider session simulator runs the actual
runtime over isolated database copies with network access blocked. Five focused
tests cover complete replay, malformed proposals at each step, prerequisite
rejections, recorded timeouts and input/configuration safeguards. Saved completed
query receipts are reused; no fresh SQL/DAX execution or business correctness is
claimed. All 973 local regression tests passed. See [replay evidence](docs/offline-session-replay.md).
Item 4 merged in [PR #212](https://github.com/bcsnpc/data-investigation-agent/pull/212): identical duplicate updates and descriptive text bounds
are repaired locally; missing approved SQL schemas are fetched before dispatch.
Repairs have separate events and do not change executable query text or authority.
Six repair and five replay tests passed; all 979 regression tests passed. See
[local repair evidence](docs/local-proposal-repairs.md).
Item 5 merged ([PR #213](https://github.com/bcsnpc/data-investigation-agent/pull/213)):
compiled SQL/DAX duplicates reuse sealed receipts without another data read.
Eleven focused checks cover alias normalization and admission of distinct reads;
result equality is a reporting-only metric. Recording exclusions no longer abort
provider calls. All 994 regression tests and six CI checks passed.
F-paced remains failed for test selection and is no longer the duplicate gate.
See [redundancy evidence](docs/conservative-read-redundancy.md).
Item 6 merged ([PR #214](https://github.com/bcsnpc/data-investigation-agent/pull/214)) separates retrieval allowance from two protected test-planning turns
within the existing total. Five focused checks include four lookups and two mock
reads in six calls with exact offline replay. Session metrics report reads and the
retrieval/test ratio. All 999 regression tests and six CI checks passed. See
[budget evidence](docs/retrieval-test-budgets.md).
Item 7 merged in [PR #215](https://github.com/bcsnpc/data-investigation-agent/pull/215), adding twelve synthetic intake captures covering nine ticket families
and three specific missing user facts. All nine reach reviewed investigation and
a mock read; negative probes reject unnecessary metadata clarification. Four tests
passed; all 1,003 regression tests and six CI checks passed. This checks admission and replay of
controlled responses, not live LLM judgment. See [intake evidence](docs/intake-family-regressions.md).
Item 8's [capacity report](docs/provider-capacity-readiness.md) recorded the original
10,000 TPM / 100 RPM allocation. The approved increase now reads back as 100,000 TPM
and 1,000 RPM. The known-domain baseline gate precedes any freeze or publication.
V4 remains invalidated. See [current status](docs/current-delivery-status.md).

Current reliability work makes conclusion support explicit: a proposed mechanism,
its evidence, dependency on business intent, and remaining useful tests. The
validator rejects a defect/expected-behavior label that explicitly depends on an
unknown intended rule. This catches structural contradictions, not semantic truth;
interpretations remain LLM_INFERRED. Targeted search and discriminating-test guidance
are under known-domain evaluation. See [conclusion quality](docs/conclusion-quality.md).
The previous [provider response milestone](docs/provider-response-reliability.md)
added safe failure categories, retained numeric usage and aggregate-query admission
checks; its 943 regression tests passed. Default model settings remain unchanged.

Structural-discovery work added automatic structural hypotheses to discovered
model context, SQL/DAX capability descriptions from the validators, and autonomous
structural experiments during relevant tickets. Keys, grain, join behavior,
functional dependencies and freshness can be tested through the existing bounded
read-only tools. Metadata guesses remain distinct from measured evidence and
business intent. Scans do not launch background data profiling. See
[structural discovery](docs/structural-discovery.md). The frozen unfamiliar-domain
challenge remains the main acceptance gate; these additions do not replace it.
Earlier known-domain transformation runs timed out or stopped at business-context
questions without measuring source join behavior. A discovered compaction bug
removed retrieved transformation text from later planner prompts; bounded evidence
retention now preserves recent excerpts and their provenance. That milestone passed
939 local regression tests. Its final known-domain trial reached both source schemas
without proposal rejections or repeated lookups, but a provider-response error
stopped it before SQL execution. A separate quality-profile ratio trial completed
the requested value/component explanation in two planner calls and one native read,
while the default model asked an unnecessary clarification. General reliability
and unfamiliar-domain acceptance remain unproven.


**Discovery-to-ticket (Stages 2–3)** merged in PR #196. **Dynamic reasoning and
governed tools (Stages 4–5)** merged in PR #198. The v4 attempt remains historical discovery evidence. The preceding v3 attempt discovered its new model
and reports automatically, then exposed excessive planner-profile truncation.
The generic correction required a fresh freeze and variant. The first nine-family trial recorded partial reads,
reasoning failures and provider rate-limit blocks; it has **not passed**.
[Challenge acceptance](docs/unknown-domain-challenge.md) remains in progress.
[Current delivery status](docs/current-delivery-status.md) owns
implementation and verification claims; [stages 1–9](docs/architecture/phases-and-acceptance.md)
define remaining work.

Discovery currently uses one approved workspace and SQL database/schema per profile.
Finite repeat scans support an external scheduler; no persistent scheduler is installed.
Denied/unsupported metadata is explicit. Warehouse catalogs require an approved
endpoint adapter. Search exposes context but does not grant query authority.

Generated queries support explicit grammar subsets; SQL views are not yet admitted.
Practical assessments are evidence-qualified LLM interpretations, not verified causes.
Frozen unknown-domain acceptance remains pending. The legacy manual
catalog retains its review gates. Runtime report filters/RLS and cross-system
comparability remain explicit limits. V2 is local and single-operator; enterprise
hosting/authentication is pending. The earlier context/query recovery revision passed
920 local regression tests and 10 dynamic browser checks. The structural-discovery
revision passed 929 regression tests; its ten browser checks preceded the final
profile projection correction. Structured definitions, parent-qualified asset search, missing-schema
recovery, actionable query feedback and remaining-time context are implemented.

A GPT-5.4 known-domain trial completed a qualified join-multiplication diagnosis:
one Power BI read and two SQL reads reproduced 57,043 and linked it to the inspected
notebook logic. It preserved uncertainty about the intended rate-selection rule
and corrected total. Earlier trials remained unresolved; one successful case does
not establish model superiority or unfamiliar-domain generality. The default model
is unchanged. SQL firewall error 40615 was resolved by a user-approved single-IP
rule; free-limit AutoPause remains.
See [context/query recovery](docs/context-query-recovery.md) and
[quality engineering research](docs/investigation-quality-engineering.md).
These checks do not establish unfamiliar-domain acceptance or retest every
deployed application.

## Run and demo

- [Local v2 workspace setup](docs/investigation-workspace-milestone.md#local-runbook)
  and [reviewed screenshot intake](docs/screenshot-intake-milestone.md).
  Install `scripts/requirements-workspace.txt` in your development environment.
  Keep provider credentials and workspace token outside Git. Execution requires an eligible discovered or enabled legacy catalog and
  configured provider access. Discovered execution requires a separate reader.
- [Environment discovery runbook](docs/enterprise-discovery-milestone.md).
- [Dynamic investigation behavior and limits](docs/dynamic-investigation-milestone.md).
- [Model admin fallback](docs/model-onboarding.md) and
  [metadata scan worker](docs/catalog-scans-and-semantics.md).
- [Bounded-v1 presenter runbook](docs/demo-runbook.md): historical demonstrations,
  not proof of unfamiliar-domain self-discovery.
- [Order portal setup](docs/order-portal.md), [synthetic data/loading](docs/synthetic-data.md)
  and [runtime identities](docs/runtime-identities.md).

Development order portal: https://orderops-portal-9696025.azurewebsites.net

## Engineering and plan

[Controlling mission](SELF_DISCOVERING_ENTERPRISE_INVESTIGATOR_PLAN.md) |
[Architecture and audit](docs/architecture/README.md) |
[Current status](docs/current-delivery-status.md) |
[Progress history](docs/progress.md) |
[Handoff](PROJECT_STATE_AND_NEXT_STEPS.md) | [Contributing](CONTRIBUTING.md)

Keep SQL free-overage settings unchanged. Query/result limits do not guarantee zero
resource cost. Automatic production repairs, deployments and data mutations are
outside the investigation product boundary.
