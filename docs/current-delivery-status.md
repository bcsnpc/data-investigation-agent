# Current delivery status

Review: [PR #174](https://github.com/bcsnpc/data-investigation-agent/pull/174).

Updated 2026-09-14. **PR #172 is merged.** The next grouped milestone adds [reviewed record discovery](reviewed-record-discovery-milestone.md), tracked by [#173](https://github.com/bcsnpc/data-investigation-agent/issues/173).

## What is built

| Area | Delivered | Current boundary |
| --- | --- | --- |
| Business foundation | Related 100000-order dataset, Azure SQL loading and orders application | Existing deployment; no new application deployment in this milestone |
| Analytics | Fabric Bronze/Silver/Gold processing, reconciliation, semantic model and Power BI reports | Complete native/source snapshot certification remains separate |
| Bounded-v1 investigator | Two-metric diagnosis, LLM-assisted ticket planning, review/evidence/routing workflows, defect labs and demos | Preserved as the bounded baseline |
| V2 onboarding/catalog | Admin UI/API, model registration, metadata scans, immutable contexts, business review, dependency discovery and invalidation | Hosted onboarding and broader semantic/context coverage remain |
| V2 diagnostic tools | Metadata-selected Power BI scalar/dependency/dimension reads, SQL count/sum/watermark reads, typed date/numeric/boolean/null filters, saved receipts and comparison gaps | Scope/version/equivalence proof remains incomplete |
| Durable runtime | Typed plans, reserved budgets/receipts, idempotency, worker fencing, explicit recovery and timeout holds | Local operator runtime; uncertain completion is not automatically retried |
| Adaptive diagnostic loop | LLM selects the next admitted test from saved observations; hypotheses, clarification, scope successors and stop reasons persist | Not a complete causal verifier; automatic source tests require unique current onboarding mappings |
| Governed adaptive controls | Shared daily reservations, policy pinning, cancellation/reconciliation and no-progress stopping | Same catalog/environment; provider-wide spend is not certified |
| Scoped freshness evidence | Metadata-selected watermark reads, immutable reviewed policies, revocation and deterministic age conditions | Narrow historical watermark rule only; no production SLA or report-cause proof |
| Reviewed source discovery | Derives complete source scopes from onboarding mappings; ambiguity/revocation gates and query-free preview | Development mappings still need actual team review; no equivalence certification |
| Record evidence | Bounded Power BI/SQL projected groups, multiplicity, keyed differences, saved adaptive pairs and recovery | Complete response is not shared-generation or semantic proof; model mappings now derive reviewed projections per ticket |
| Shared projections | Business and technical API projections share one session, scope and outcome hash | Backend only; unified v2 ticket UI is not deployed |

**Validation:** 641 script tests passed, including 27 focused reviewed-record discovery tests. A query-free draft preview compiled both four-field order projections against the saved development catalog, with matching supported types and no saved confirmation. The previous PR's live five-order reads and zero-call replay remain historical evidence. This milestone made no SQL/LLM calls or quota changes and did not deploy the UI. Actual development mappings still need business review.

## Where we are

**Phase A is verified. B-E have working implementation slices. F/G now have durable execution, evidence-led planning and governed session controls; their full acceptance gates remain open.** H is pending. I has a shared backend projection but still needs its user workflow; J has reusable bounded-v1 routing but no completed v2 handoff.

The new path can select a catalog measure, choose and run an approved diagnostic, observe the result and choose a different next test. It can now derive approved record projections from reusable model reviews and ticket filters, then use saved keyed comparisons in later decisions. It no longer requires an operator to prewrite the whole sequence. With reviewed model mappings, source tests are derived from the ticket filters rather than manually authored per ticket. It still cannot certify a general business cause from incomplete evidence. Numeric observations and diagnostic differences come from saved receipts. A reviewed watermark policy can now establish a narrow age condition; the reported business cause, hypotheses and routing remain unverified.

## Remaining grouped milestones

1. **Complete trustworthy investigation and proof:** effective report/identity/date context, authoritative source mappings, version/shared-generation evidence, supported causal/freshness/application-intent verifiers, impact/ownership and provider-wide monetary governance. Shared adaptive request allowances are now implemented. Complete the remaining B-G exit gates together with meaningful end-to-end checks.
2. **Prove generality:** freeze the runtime and run all eight hidden/native acceptance families, including new additive, ratio and complex measures, healthy/defect/gap variants and repeated planner evaluations. Current injected tests and live smoke checks do not replace this gate.
3. **Complete the user product:** resolve business tickets/screenshots into reviewed scope, build the shared business/technical workspace, integrate reviewed v2 routing/triage, then deploy and verify the complete workflow.

See the [tracker](progress.md), [milestone behavior and limits](adaptive-investigation-milestone.md) and [A-J acceptance plan](architecture/phases-and-acceptance.md). PR count is not a completion measure.
