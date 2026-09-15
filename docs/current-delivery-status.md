# Current delivery status

Updated 2026-09-14. PR #160 is merged, including comparison intent and evidence gates. The next substantial backend milestone is implemented on `feature/v2-investigation-milestone`, tracked by [#161](https://github.com/bcsnpc/data-investigation-agent/issues/161). See [implementation and verification](v2-diagnostic-milestone.md).

## What is built

| Area | Delivered | Boundary |
| --- | --- | --- |
| Business data and application | Related synthetic dataset with 100,000 orders, SQL schema/loading, orders portal and deployed Azure foundation | Cloud availability is not revalidated by this status update |
| Analytics platform | Fabric Bronze/Silver/Gold processing, reconciliation, semantic model and Power BI reports | Existing platform; not a newly certified source/semantic snapshot |
| Existing investigator | Bounded two-metric diagnosis, LLM-assisted ticket planning, evidence/review workflows, defect labs, demos and reviewed routing infrastructure | Preserved as bounded-v1; not a general investigator |
| V2 onboarding | Admin UI/API, registration, environment scoping, business review, enable/disable, immutable context history | Local control plane; hosted identity/tenant product not delivered |
| V2 catalog | Metadata scan queue/worker, retained definitions, dependency/operation discovery, change diffs and invalidation | Conservative analysis; complex effective contexts remain partial |
| V2 native diagnostics | Catalog-selected Power BI measure, dependency and dimension reads; typed values, limits and saved receipts | Operator-driven, not an adaptive loop; two live reads passed |
| V2 capabilities/evidence | Per-measure decisions, dry-run admission, saved decision/request binding, scoped receipt APIs and stale/partial/error assessment | Merged in #154; upstream and causal certification remain unavailable |

Typed diagnostic scope adds date, integer, fixed-decimal and boolean filters, explicit BLANK values, scope discovery and validation. Two new live Power BI reads passed; this continuation is not full visual-context certification.

Source diagnostics now add pinned-catalog SQL count/sum reads and saved evidence. Live USD order count and total-amount sum succeeded after one separately recorded failed attempt. This adds source observations; source-to-measure equivalence is still unverified.

Comparison assessment now pairs saved observations, checks reviewed mappings and scope, and persists exact missing-proof reasons. It does not yet certify comparability or a cause. No business mapping was invented during validation.

## Larger backend milestone now implemented

- Metadata-derived direct SUM/COUNTROWS semantics and recursive dependency shape inspection; unsupported expressions remain explicit.
- A typed tool registry and durable action plans supporting source-first, multiple native observations and explicit evidence references.
- Idempotent run creation, reserved receipts/call budgets, worker fencing, admission fingerprints and conservative crash recovery.
- SQL connection-only 40613 recovery using the existing bounded retry policy; query failures are not retried.
- Admin run history and proof-readiness endpoints, a CLI, and regression coverage.

**Validation:** 472 script tests passed. A live run read 100000 from both Power BI and SQL using two cloud actions; repeating the completed run created no new reads. The comparison correctly remained insufficient evidence because mapping, version and context proof are missing. No new v2 UI or Azure deployment is claimed.

## Where we are

**Phase A is verified. B/C have working foundations. We are implementing D/E: native tools and semantic capability decisions. F now has a durable runtime foundation; G-J remain ahead.** The roadmap is the [A–J architecture](architecture/README.md); merging a PR does not complete its phase.

The new path can discover a measure, admit a bounded diagnostic request, ask Power BI for its value and inspect saved evidence. It cannot yet autonomously choose and revise hypotheses until it proves why a business metric differs.

## Remaining grouped milestones

1. **Finish diagnostic semantics and proof prerequisites (B–E):** complete report/filter/date/effective-identity context, authoritative source mappings and upstream tools, model/source version evidence, dependency context certification, capability gates and remaining scan/onboarding lifecycle work.
2. **Complete durable adaptive investigation (F-G):** typed tools, persisted diagnostic actions, budget reservations and conservative recovery are implemented. Persisted hypotheses, evidence-led next-test selection, deterministic verification and impact remain. Uncertain cloud completion intentionally holds for reconciliation.
3. **Prove generality (H):** freeze the engine and pass all eight acceptance families, including new additive/ratio/complex measures, visual-context, freshness, application-origin, healthy and insufficient-evidence cases. Live native version-proof prerequisites must actually pass.
4. **Complete the product workflow (I–J):** one shared run in business/technical views, enabled-report selection, clarification, reviewed routing and triage.

The platform and bounded demos are available as a foundation. The general metadata-driven investigator is still under construction; no completion percentage or delivery date is inferred from the PR count.
