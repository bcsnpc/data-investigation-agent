# Current delivery status

Updated 2026-09-18. Tracking: [#193](https://github.com/bcsnpc/data-investigation-agent/issues/193).
Direction: [Self-Discovering Enterprise Data Investigator](../SELF_DISCOVERING_ENTERPRISE_INVESTIGATOR_PLAN.md).
This is the authoritative current status; milestone pages retain historical evidence.

## Current milestone

**Dynamic reasoning and governed tools (Stages 4–5) passed validation.**
[Issue #197](https://github.com/bcsnpc/data-investigation-agent/issues/197) tracks
this grouped change. Architecture PR #194 and discovery PR #196 are merged.
Discovery merged at `af6a0523db3d2e9e6c308f98b01d1e5a3745fcf4`.

The planner can retrieve discovered definitions/lineage, propose parser-governed
SQL/DAX, use typed diagnostics and revise hypotheses from observations. The local
workspace enables this path for discovered models, including budgeted global
questions. Suggested explanations are LLM_INFERRED, not verified causes or confirmed
business intent. Reader isolation, budgets, receipts, cancellation and replay remain.

Validation: **891 regression tests and 40 browser checks passed**. Live generated
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

No SQL quota, production data, identity permissions or deployment changed in these
milestones. SQL TOP limits returned rows, not work scanned.

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
| 4 Expanded LLM reasoning | Implemented and validated on branch under #197 |
| 5 Flexible governed tools | Implemented and validated on branch under #197 |
| 6 General engine freeze | Next after grouped dynamic milestone review/merge |
| 7 Unknown Domain Challenge | Not run; publish unfamiliar domain after freeze and test all nine families |
| 8 UX consolidation | Dynamic local flow works; broader effective-context and hosted delivery remain |
| 9 Support-engine-ready core/handoff | Generic boundaries partly established; integrated v2 impact/ownership/triage remains |

Next: **freeze plus unfamiliar-domain challenge**. Freeze engine, prompts, tools,
validators and policy semantics before publishing new assets. Keep evaluator truth
outside runtime context. Record failed/partial/blocked outcomes, and invalidate and
repeat the freeze with a fresh variant if engine behavior must change.

See [stage exits](architecture/phases-and-acceptance.md),
[challenge contract](architecture/enterprise-discovery-pivot.md#h-frozen-unknown-domain-challenge)
and [historical pre-pivot status](delivery-status-before-discovery-pivot.md).
