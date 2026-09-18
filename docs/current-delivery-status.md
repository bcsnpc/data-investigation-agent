# Current delivery status

Review: [PR #194](https://github.com/bcsnpc/data-investigation-agent/pull/194).

Updated 2026-09-18. Tracking: [#193](https://github.com/bcsnpc/data-investigation-agent/issues/193).
Direction: [Self-Discovering Enterprise Data Investigator](../SELF_DISCOVERING_ENTERPRISE_INVESTIGATOR_PLAN.md).
This page is the authoritative current status; milestone documents retain historical evidence.

## Current milestone

**Discovery-to-ticket, grouped Stages 2?3, is implemented and being validated.**
[Issue #195](https://github.com/bcsnpc/data-investigation-agent/issues/195) tracks
this substantial change. PR #194 merged at `a27369df5834932ba23032ce16598b97ff0ec0f5`.

Environment scans now retain coverage, immutable context and changes, derive graph
edges and automatically project supported models/reports into ticket intake.
Reportless models have independent model assets. Business review is optional for
this path; explicit deny survives scans. The configured reader can authorize an
approved workspace without a model-ID list. It never falls back to the publisher.

Live validation collected 399 assets from the business environment, including the
existing model, three reports, semantic definitions and approved SQL catalog.
One lakehouse-table surface failed in the first scan and is retained as a gap.
A separate reader-workspace scan populated the catalog automatically and one native
query completed with value 8 under `investigator-reader@skynwhy.com`.
All 876 regression tests pass, including generator and discovery change/denial/
ambiguity coverage; 30 existing browser checks pass. The isolated workspace's
initial scan and two finite scheduled repeat scans completed, each with nine
transport/catalog operations. Both repeat scans recorded zero changes. This
demonstrates finite repetition, not an installed perpetual discovery service.

Scope: one approved workspace and SQL database/schema per profile; warehouse catalog
adapter, permanent scheduling, broader context retrieval and dynamic queries remain.
No source data, permissions, SQL quota or cloud deployment was changed.
See [implementation/runbook](enterprise-discovery-milestone.md).

## Working foundation

| Area | Delivered behavior | Current limit |
| --- | --- | --- |
| Business/data platform | Related 100,000-order SQL application, deployed portal, Fabric Bronze/Silver/Gold and Power BI reports | Historical deployment evidence; current cloud availability not retested |
| Metadata/lineage | Workspace item enumeration, SQL catalogs, TMSL/PBIR definitions, lakehouse table listing, semantic dependencies and evidence-backed lineage | Configured roots; metadata/permission gaps; warehouse endpoint catalogs pending |
| Catalog | Automatic discovery projection, independent model assets, immutable contexts and explicit deny; legacy registration remains | One workspace/profile; oversized ticket catalogs still require bounded retrieval work |
| Diagnostics | Native scalar/dependency/dimension/record reads; typed SQL count/sum/watermark/record tools; keyed comparisons and joint total/record checks | Bounded grammar, mappings and scopes; no general generated SQL/DAX tool |
| Adaptive runtime | LLM selects admitted tests, sees observations, revises hypotheses; saved receipts, budget, cancellation, replay and identity controls | Precompiled candidates; practical causal classification remains narrow; not a general investigator |
| User workspace | Local business text and reviewed screenshot intake, scope review/start, timeline/history and shared business/technical evidence | Single operator; no hosted v2 auth/deployment; hidden report context is not inferred |
| Handoff | Bounded-v1 reviewed issue/notification workflows | Full v2 impact/ownership/routing integration pending |

The latest implementation evidence is [joint native capture](joint-native-capture-milestone.md):
860 prior regression tests, 30 browser checks, live complete (8 observed/8 rebuilt),
empty and partial checks, plus a real LLM-selected combined read and no-call replay.
These are prior milestone results, not fresh architecture-audit test results.
Timeout history and limitations remain in that document.

## Where we are and what remains

| Stage | Status |
| --- | --- |
| 1 Architecture pivot | Merged #194 |
| 2 Enterprise discovery | Implemented on branch; live scans, coverage/diffs and finite repeat validation |
| 3 Automatic context graph | Implemented on branch; independent context, graph/search and automatic ticket visibility |
| 4 Expanded LLM reasoning | Planned; context retrieval, unfamiliar semantics and dynamic hypothesis/test proposals |
| 5 Flexible governed tools | Planned; parser-enforced SQL/DAX and broader generic diagnostics |
| 6 General engine freeze | Pending working discovery/reasoning/tools |
| 7 Unknown Domain Challenge | Not run; publish unfamiliar assets after freeze and exercise nine families |
| 8 UX consolidation | Working local foundation; discovery-first flow, effective context, hosted authorization/deployment remain |
| 9 Support-engine-ready core and reviewed handoff | Generic asset/context/tool/evidence boundaries; integrated v2 impact/ownership/triage remains |

The next cohesive implementation after discovery acceptance is **dynamic reasoning
plus governed tools (Stages 4?5)**: retrieved definitions/lineage, hypothesis-led
proposed tests, parser-enforced SQL/DAX and evidence-qualified outcomes. Freeze only
when those work, then publish the unknown domain. Do not describe this catalog
milestone as general investigation acceptance.

See [stage exits](architecture/phases-and-acceptance.md),
[exact unknown-domain experiment](architecture/enterprise-discovery-pivot.md#h-frozen-unknown-domain-challenge)
and [historical pre-pivot status](delivery-status-before-discovery-pivot.md).
