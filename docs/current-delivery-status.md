# Current delivery status

Updated 2026-09-14. PR #152 is merged. The next grouped work is [capability and evidence assessment](capability-evidence-assessment.md), tracked by [#153](https://github.com/bcsnpc/data-investigation-agent/issues/153).

## What is built

| Area | Delivered | Boundary |
| --- | --- | --- |
| Business data and application | Related synthetic dataset with 100,000 orders, SQL schema/loading, orders portal and deployed Azure foundation | Cloud availability is not revalidated by this status update |
| Analytics platform | Fabric Bronze/Silver/Gold processing, reconciliation, semantic model and Power BI reports | Existing platform; not a newly certified source/semantic snapshot |
| Existing investigator | Bounded two-metric diagnosis, LLM-assisted ticket planning, evidence/review workflows, defect labs, demos and reviewed routing infrastructure | Preserved as bounded-v1; not a general investigator |
| V2 onboarding | Admin UI/API, registration, environment scoping, business review, enable/disable, immutable context history | Local control plane; hosted identity/tenant product not delivered |
| V2 catalog | Metadata scan queue/worker, retained definitions, dependency/operation discovery, change diffs and invalidation | Conservative analysis; complex effective contexts remain partial |
| V2 native diagnostics | Catalog-selected Power BI measure, dependency and dimension reads; typed values, limits and saved receipts | Operator-driven, not an adaptive loop; two live reads passed |
| V2 capabilities/evidence | Per-measure decisions, dry-run admission, saved decision/request binding, scoped receipt APIs and stale/partial/error assessment | Current continuation; upstream and causal certification remain unavailable |

## Where we are

**Phase A is verified. B/C have working foundations. We are implementing D/E: native tools and semantic capability decisions. F–J remain ahead.** The roadmap is the [A–J architecture](architecture/README.md); merging a PR does not complete its phase.

The new path can discover a measure, admit a bounded diagnostic request, ask Power BI for its value and inspect saved evidence. It cannot yet autonomously choose and revise hypotheses until it proves why a business metric differs.

## Remaining grouped milestones

1. **Finish diagnostic semantics and proof prerequisites (B–E):** complete report/filter/date/effective-identity context, authoritative source mappings and upstream tools, model/source version evidence, dependency context certification, capability gates and remaining scan/onboarding lifecycle work.
2. **Durable adaptive investigation (F–G):** persisted hypotheses and scope, budget reservations, crash/timeout recovery, typed tool registry, evidence-led next-test selection, deterministic verification and impact.
3. **Prove generality (H):** freeze the engine and pass all eight acceptance families, including new additive/ratio/complex measures, visual-context, freshness, application-origin, healthy and insufficient-evidence cases. Live native version-proof prerequisites must actually pass.
4. **Complete the product workflow (I–J):** one shared run in business/technical views, enabled-report selection, clarification, reviewed routing and triage.

The platform and bounded demos are available as a foundation. The general metadata-driven investigator is still under construction; no completion percentage or delivery date is inferred from the PR count.
