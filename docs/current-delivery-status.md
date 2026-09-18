# Current delivery status

Updated 2026-09-18. Tracking: [#193](https://github.com/bcsnpc/data-investigation-agent/issues/193).
Direction: [Self-Discovering Enterprise Data Investigator](../SELF_DISCOVERING_ENTERPRISE_INVESTIGATOR_PLAN.md).
This page is the authoritative current status; milestone documents retain historical evidence.

## Current milestone

**Stage 1 architectural pivot is documented.** The [architectural review](architecture/enterprise-discovery-pivot.md)
records the code audit, exact manual-onboarding gates, reusable foundations,
discovery/graph design, LLM/tool boundaries, simplification, migration and frozen
Unknown Domain Challenge. README and controlling architecture now follow this plan.
No new self-discovery or generated-query runtime capability is claimed by this change.

PR #192 merged at `d0c7bee353119f1f932ada59852bd6d46aa7ab0c`. It was the only open PR
at audit time and all six checks passed. The pivot preserves its reusable native
aggregate/record diagnostic. No cloud deployment, identity, data or SQL quota setting
changed during the architecture audit.

## Working foundation

| Area | Delivered behavior | Current limit |
| --- | --- | --- |
| Business/data platform | Related 100,000-order SQL application, deployed portal, Fabric Bronze/Silver/Gold and Power BI reports | Historical deployment evidence; current cloud availability not retested |
| Metadata/lineage | Workspace item enumeration, SQL catalogs, TMSL/PBIR definitions, lakehouse table listing, semantic dependencies and evidence-backed lineage | Configured roots; metadata/permission gaps; no automatic environment-to-ticket publication |
| Catalog | Manual model/report registration, retained scan import, immutable contexts, review/enablement and queued scans | New models/reports still require manual onboarding; model assets depend on report bundles |
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
| 1 Architecture pivot | Review and documentation completed on this branch |
| 2 Enterprise discovery | Next; reuse collectors, add approved-root policy, coverage/diffs and recurring jobs |
| 3 Automatic context graph | Next, grouped with Stage 2; independent model/report context and automatic ticket visibility |
| 4 Expanded LLM reasoning | Planned; context retrieval, unfamiliar semantics and dynamic hypothesis/test proposals |
| 5 Flexible governed tools | Planned; parser-enforced SQL/DAX and broader generic diagnostics |
| 6 General engine freeze | Pending working discovery/reasoning/tools |
| 7 Unknown Domain Challenge | Not run; publish unfamiliar assets after freeze and exercise nine families |
| 8 UX consolidation | Working local foundation; discovery-first flow, effective context, hosted authorization/deployment remain |
| 9 Reviewed handoff | Reusable legacy foundation; integrated v2 impact/ownership/triage remains |

The next cohesive implementation is **discovery-to-ticket**, not more defect fixtures
or exclusive-publication proof infrastructure. New supported models/reports/tables
should appear through scans, without investigator Python changes or manual ID entry.
Business definitions become optional enrichment; policy and reader permissions still
control execution. Observed, likely and verified claims retain different evidence
requirements. No runtime safety gate was silently relaxed in this documentation change.

See [stage exits](architecture/phases-and-acceptance.md),
[exact unknown-domain experiment](architecture/enterprise-discovery-pivot.md#h-frozen-unknown-domain-challenge)
and [historical pre-pivot status](delivery-status-before-discovery-pivot.md).
