# Current delivery status

Updated 2026-09-18. Tracking: [#193](https://github.com/bcsnpc/data-investigation-agent/issues/193).
Direction: [Self-Discovering Enterprise Data Investigator](../SELF_DISCOVERING_ENTERPRISE_INVESTIGATOR_PLAN.md).
This is the authoritative current status; milestone pages retain historical evidence.

## Current milestone


**Current milestone: provider response reliability and conclusion quality.**
Provider failures now retain safe categories and numeric usage without retaining
response content. Four source-ready replays at 4,000 output tokens produced three
structured proposals and one observed OUTPUT_TOKEN_LIMIT. The experimental profile
now allows 8,000 output tokens; default settings remain unchanged. A narrow SQL
AST check rejects mixed aggregate/nonaggregate projections without GROUP BY.
**943 local regression tests passed.** See [research and evaluation](provider-response-reliability.md).

The next full known-domain transformation run completed without a provider error:
eight planner calls, two native reads, five metadata lookups and no SQL reads.
It reproduced 53,145 but proposed a sign-handling diagnosis whose business premise
was not established, while leaving join duplication untested. This is **partial
investigation evidence, not a correctness or frozen-acceptance pass**. Increased
output room alone has not resolved test selection or conclusion qualification.
The ambiguity run completed with BUSINESS_CONTEXT_REQUIRED after seven planner
calls, two native reads and four context lookups, preserving unknown code meaning
and intended rules. The original daily policy was restored without resetting
usage. The fresh freeze remains pending while transformation test selection and
claim qualification are improved. No permissions or SQL limits changed.

### Previous milestone: planner reliability and evidence continuity (merged PR #205)

**Planner reliability and evidence continuity.**
Research and live evaluations led to bounded retention of retrieved transformation
text, keyed hypothesis updates, response-schema field limits, governed reasoning/
output/timeout settings, and one optional metered planner connection recovery.
The experimental quality profile allows 48,000 input characters per call; default
settings, cumulative bounds, reader permissions and SQL free-tier policy remain.
No domain-specific route, metric branch or scenario mapping was added.

The final known-domain transformation trial made **nine planner calls, one native
read and seven metadata lookups**, reproducing 53,145 and reaching the actual
notebook join plus both source schemas. It had no rejected proposal or repeated
lookup, but **ended UNRESOLVED before SQL execution** on a provider-response
`ValueError`. The saved category does not identify whether the response was
incomplete or otherwise invalid. This is not an end-to-end reliability pass.
Earlier timeout, contract, payload-limit and interrupted experiments remain recorded.

A final quality-profile ratio trial completed its requested calculation in **two
planner calls and one native read**: 6,432 / 8,580 = 0.7496503496503496. It explained
the actual measure definitions and preserved the missing business benchmark.
The default-model trial instead asked for confirmation already supplied in the
ticket; that task-completion failure is recorded. Neither establishes generality.
The original daily LLM policy was restored after testing without resetting usage.

**939 local regression tests passed** on the final engine. Six CI checks passed
on the implementation commit; final PR checks track the documentation head.
No dedicated browser session was rerun locally. See [research, trials and limits](planner-runtime-quality.md).

The follow-up above distinguishes provider response failures and continues
transformation and ambiguity evaluations before freezing a new engine to publish
a fresh domain for the full acceptance matrix. The unknown-domain challenge
remains the priority and has not passed. Broader discovery, hosted authentication
and integrated handoff remain pending.

### Previous milestone: structural discovery (merged PR #204)

**Structural discovery within the existing reliability work.**
New model contexts now include bounded metadata-derived role/key/date/measure
hypotheses and explicit unknown semantics. SQL/DAX adapters advertise supported
operations, prerequisites and limits; runtime eligibility does not grant execution.
Relevant tickets can choose bounded uniqueness, grain, functional-dependency,
join, freshness and native measure-behavior experiments with existing query receipts.
There is no new architecture layer, mandatory tool sequence or domain mapping.
Data profiling is ticket-driven, not an automatic scan-time sweep. The fresh engine
freeze and unfamiliar-domain challenge remain next, with no acceptance pass claimed.
Validation: 929 regression tests passed after the dense-profile correction; ten injected-transport browser checks
passed before the final profile-size adjustment. A ratio trial reproduced native
components in one read; an ambiguity trial requested business meaning without
inventing it, but did not exhaust available documentation. These are known-domain
checks. Attempt v3 froze `05348d0` and published variant `0fd86f`, retaining prior
usage and applying explicitly approved reader grants. Its complete 63-operation
scan discovered the model and reports automatically, but exposed a planner profile
projection that discarded all table hints for dense scoped IDs. A generic correction
now retains selected-table member hints with explicit truncation. This engine
change ends v3 frozen acceptance; further v3 runs are known-domain regressions.
A fresh freeze and variant are required; no acceptance pass is claimed.
The post-correction known-domain transformation run ended UNRESOLVED after an
API timeout: ten planner calls, five native reads, four metadata lookups and no
SQL reads. It reproduced 53,145 but did not test the upstream join mechanism.
Overlapping tests and timeout behavior need quality evaluation before another
freeze. Original daily limits were restored without resetting usage.
See [structural discovery evidence](structural-discovery.md).


**Investigation quality before a fresh unfamiliar-domain challenge.** Discovery,
dynamic queries and earlier reliability work merged in PRs #194, #196, #198,
#200, #201 and #202. The v1/v2 frozen attempts are historical failed/partial
attempts; changed engine code cannot use them as acceptance evidence.

[PR #203](https://github.com/bcsnpc/data-investigation-agent/pull/203) implements
structured large-asset context, parent-qualified search, exact missing-schema
recovery targets, SQL alias feedback and safe connection-error receipts. Dynamic
runs allow 384,000 cumulative input characters under the user-approved increase;
12 planner calls, per-call output of 1,500 tokens and existing SQL/cloud limits
remain bounded. No domain-specific investigation route or expected answer was added.

The final GPT-5.4 known-domain trial completed with **LIKELY_TECHNICAL_DEFECT**:
nine planner calls, one Power BI read, two SQL reads and five distinct metadata
lookups. It reproduced 57,043 in Power BI and the source join, connected the result
to the notebook's product-only join against versioned rates, and explicitly left
the intended rate-selection rule and corrected total unknown. No query rejection
or repeated lookup occurred. This is a qualified mechanism explanation in one
known case, not verified business intent or unfamiliar-domain acceptance.

Earlier GPT-4.1 and GPT-5.4 runs ended unresolved; their failures remain recorded.
The final generic changes expose unsupported SQL constructs and remaining dispatch
time, with a 1,800-second dynamic-run ceiling. A prior failure exposed firewall
error 40615; the user-approved single-IP rule restored reader access. SQL
useFreeLimit=true and AutoPause remain unchanged. The original daily LLM policy
was restored after testing without resetting usage. The default mini model is unchanged.

Validation: **920 regression tests and 10 dynamic browser checks passed** after
the final backend changes. Browser checks used injected transport, with no live
cloud calls. [Context/query recovery evidence](context-query-recovery.md) records
trial IDs, failures, query observations, budget changes and limits. CI and merge
state are available on PR #203.

PR #203 follow-up is now the structural-discovery extension and frozen v3 attempt
above. Further repeated evaluations and unfamiliar-domain acceptance remain required. The nine-family challenge, broader
discovery, hosted authentication and integrated handoff remain pending. Earlier
[reasoning reliability](reasoning-reliability.md) and [quality engineering](investigation-quality-engineering.md)
retain their release-specific evidence.

Dynamic reasoning and governed tools merged in PR #198 after all six CI checks passed.
[Issue #197](https://github.com/bcsnpc/data-investigation-agent/issues/197) tracks
this grouped change. Architecture PR #194 and discovery PR #196 are merged.
Discovery merged at `af6a0523db3d2e9e6c308f98b01d1e5a3745fcf4`.

The planner can retrieve discovered definitions/lineage, propose parser-governed
SQL/DAX, use typed diagnostics and revise hypotheses from observations. The local
workspace enables this path for discovered models, including budgeted global
questions. Suggested explanations are LLM_INFERRED, not verified causes or confirmed
business intent. Reader isolation, budgets, receipts, cancellation and replay remain.

Earlier dynamic-tool milestone validation: **891 regression tests and 40 browser checks passed**. Live generated
DAX returned a ratio of 0.2 with its component values in one native query. A separate
context-first SQL investigation returned 20,000 total and distinct customer IDs.
Both completed with the isolated reader. Earlier contract/Decimal failures and
their fixes are recorded in [dynamic milestone evidence](dynamic-investigation-milestone.md).
These are existing-domain checks, not frozen unfamiliar-domain acceptance.

Discovery's business-environment repeat scan completed with **567 assets and 69
operations**, resolving the initial lakehouse-listing gap through bounded OneLake
fallback. An isolated workspace scan and two finite repeat scans completed with
nine operations each; repeat scans recorded zero changes. A discovered native
query returned 8. No permanent scheduler was installed.
See [discovery runbook/evidence](enterprise-discovery-milestone.md).

The earlier discovery/tools milestones changed no production data or SQL quota.
The challenge publishes isolated fixtures and uses separately approved Read + Build
grants on its models. SQL free-overage settings remain unchanged. SQL TOP limits
returned rows, not work scanned.

## Working foundation and limits

| Area | Delivered behavior | Current limit |
| --- | --- | --- |
| Business platform | Related 100,000-order SQL application, deployed portal, Fabric transformations and Power BI reports | Historical platform deployment; not every application retested this milestone |
| Discovery/context | Workspace enumeration, definitions, SQL catalogs, lakehouse tables, lineage, immutable versions/diffs, automatic ticket projection | One approved workspace/database/schema per profile; warehouse endpoint adapter and permanent scheduler pending |
| Catalog | Independent model context, graph search, reportless models, optional business enrichment, persistent explicit deny | Selected model anchor; bounded initial ticket catalog still limits large estates |
| Diagnostics | Typed native/source tools and parser-governed proposed SQL/DAX with actual reader execution | Explicit grammar subsets; SQL views/computed columns excluded; hidden report context and cross-system equivalence remain uncertain |
| Adaptive runtime | Context lookup, hypotheses, proposed tests, observation-led revision and qualified outcomes | Generality unproven; no VERIFIED_TECHNICAL_DEFECT classification |
| Workspace | Text/reviewed screenshot intake, scope review, history, cancellation, business/technical evidence | Local single operator; hosted enterprise authentication/deployment pending |
| Handoff | Older reviewed issue/notification workflows | Integrated v2 impact/ownership/routing pending |

## Remaining roadmap

| Stage | Status |
| --- | --- |
| 1 Architecture pivot | Merged #194 |
| 2 Enterprise discovery | Merged #196; coverage/diffs and finite repeat validation |
| 3 Automatic context graph | Merged #196; independent context, graph/search and ticket visibility |
| 4 Expanded LLM reasoning | Merged #198; dynamic context/tests and qualified assessments |
| 5 Flexible governed tools | Merged #198; parser-governed SQL/DAX and isolated execution |
| 6 General engine freeze | v3 profile finding requires a fresh freeze; previous attempts preserved |
| 7 Unknown Domain Challenge | v3 discovery complete; planner reliability/context retention under regression; fresh variant pending |
| 8 UX consolidation | Dynamic local flow works; broader effective-context and hosted delivery remain |
| 9 Support-engine-ready core/handoff | Generic boundaries partly established; integrated v2 impact/ownership/triage remains |

Current: **reasoning reliability before a fresh unfamiliar-domain challenge**. Prior
attempts froze the engine before publication; changed code cannot reuse their acceptance. See [live acceptance evidence](unknown-domain-challenge.md). Keep evaluator truth
outside runtime context. Record failed/partial/blocked outcomes, and invalidate and
repeat the freeze with a fresh variant if engine behavior must change.

See [stage exits](architecture/phases-and-acceptance.md),
[challenge contract](architecture/enterprise-discovery-pivot.md#h-frozen-unknown-domain-challenge)
and [historical pre-pivot status](delivery-status-before-discovery-pivot.md).
