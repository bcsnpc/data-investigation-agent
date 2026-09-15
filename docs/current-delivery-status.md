# Current delivery status

Updated 2026-09-14. **PR #162 is merged.** The next grouped milestone, [evidence-led diagnostic investigation](adaptive-investigation-milestone.md), is open in [PR #164](https://github.com/bcsnpc/data-investigation-agent/pull/164), tracked by [#163](https://github.com/bcsnpc/data-investigation-agent/issues/163).

## What is built

| Area | Delivered | Current boundary |
| --- | --- | --- |
| Business foundation | Related 100000-order dataset, Azure SQL loading and orders application | Existing deployment; no new application deployment in this milestone |
| Analytics | Fabric Bronze/Silver/Gold processing, reconciliation, semantic model and Power BI reports | Complete native/source snapshot certification remains separate |
| Bounded-v1 investigator | Two-metric diagnosis, LLM-assisted ticket planning, review/evidence/routing workflows, defect labs and demos | Preserved as the bounded baseline |
| V2 onboarding/catalog | Admin UI/API, model registration, metadata scans, immutable contexts, business review, dependency discovery and invalidation | Hosted onboarding and broader semantic/context coverage remain |
| V2 diagnostic tools | Metadata-selected Power BI scalar/dependency/dimension reads, SQL count/sum reads, typed filters, saved receipts and comparison gaps | Scope/version/equivalence proof remains incomplete |
| Durable runtime | Typed plans, reserved budgets/receipts, idempotency, worker fencing, explicit recovery and timeout holds | Local operator runtime; uncertain completion is not automatically retried |
| Adaptive diagnostic loop | LLM selects the next admitted test from saved observations; hypotheses, clarification, scope successors and stop reasons persist | Not a complete causal verifier; source tests still need reviewed configuration |
| Shared projections | Business and technical API projections share one session, scope and outcome hash | Backend only; unified v2 ticket UI is not deployed |

**Validation:** 505 script tests passed. One live session used two Azure LLM decisions and two data reads, each returning 100000. Repeating the completed session made no new reads; both projections shared the same outcome. Earlier provider-response failures and their fix are recorded in the milestone document.

## Where we are

**Phase A is verified. B-E have working implementation slices. F/G now have durable execution and evidence-led planning foundations; their full acceptance gates remain open.** H is pending. I has a shared backend projection but still needs its user workflow; J has reusable bounded-v1 routing but no completed v2 handoff.

The new path can select a catalog measure, choose and run an approved diagnostic, observe the result and choose a different next test. It no longer requires an operator to prewrite the whole sequence. It still cannot certify a general business cause from incomplete evidence. Numeric observations and diagnostic differences come from saved receipts; hypotheses stay unverified and routing stays ineligible.

## Remaining grouped milestones

1. **Complete trustworthy investigation and proof:** effective report/identity/date context, authoritative source mappings, version/shared-generation evidence, supported causal/freshness/application-intent verifiers, impact/ownership and cross-session usage governance. Complete the remaining B-G exit gates together with meaningful end-to-end checks.
2. **Prove generality:** freeze the runtime and run all eight hidden/native acceptance families, including new additive, ratio and complex measures, healthy/defect/gap variants and repeated planner evaluations. Current injected tests and live smoke checks do not replace this gate.
3. **Complete the user product:** resolve business tickets/screenshots into reviewed scope, build the shared business/technical workspace, integrate reviewed v2 routing/triage, then deploy and verify the complete workflow.

See the [tracker](progress.md), [milestone behavior and limits](adaptive-investigation-milestone.md) and [A-J acceptance plan](architecture/phases-and-acceptance.md). PR count is not a completion measure.
