# Current delivery status

Review: [PR #180](https://github.com/bcsnpc/data-investigation-agent/pull/180).

Merged: [PR #178](https://github.com/bcsnpc/data-investigation-agent/pull/178).

Merged: [PR #176](https://github.com/bcsnpc/data-investigation-agent/pull/176).

Merged: [PR #174](https://github.com/bcsnpc/data-investigation-agent/pull/174).

Updated 2026-09-15. **PR #178 is merged.** The current milestone is [isolated Import fixture publication and verification](isolated-import-fixture-milestone.md), tracked by [#179](https://github.com/bcsnpc/data-investigation-agent/issues/179). Live contents are verified; the broader Phase H gate remains blocked by publication control and effective context/identity.

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
| Aggregate record consistency | Sealed aggregate receipts, exact count/sum reconstruction, SQL count checks, durable/local assessments and adaptive consumption | Arithmetic consistency across separate captures; remote generation/context/causal proof remains |
| Proof feasibility | Bounded live metadata preflight, two definition hashes, access/refresh summaries, persisted history and CLI gate | Actual acceptance blocked: exclusive publication, shared generation, fixture contents and effective identity/context remain unproven |
| Shared projections | Business and technical API projections share one session, scope and outcome hash | Backend only; unified v2 ticket UI is not deployed |

**Previous preflight validation:** 694 regression tests passed, including 26 focused proof-preflight tests. Live collection completed six observations using 10 metadata HTTP calls. It found Direct Lake, one workspace Admin assignment, five completed refreshes and equal definition hashes. This is not stability or exclusivity proof. Historical read used zero HTTP calls; the CLI acceptance gate returned exit 2. No SQL/DAX queries, permission changes, remote writes or deployment occurred in this milestone.

**Current validation:** 718 regression tests passed, including 24 fixture/publication tests; live create, refresh, exact content verification and replay passed.

## Latest isolated lab milestone

PR #178 is merged. The [isolated Import fixture](isolated-import-fixture-milestone.md) now publishes hashed inline data into a separate workspace/model, correlates refresh completion and verifies complete typed row multisets. Live verification matched 10 rows; native measures returned 10 eligible, 2 refunded, 20% and 65 units. Interrupted publication is held; received mutations replay without creating or refreshing again. This removes the need for mutable external fixture inputs, but does not establish remote exclusivity or shared-generation proof. The dedicated reader account is user-approved and awaiting enterprise account creation/sign-in. No business model or Azure SQL quota settings changed.

## Where we are

**Phase A is verified. B-E have working implementation slices. F/G now have durable execution, evidence-led planning and governed session controls; their full acceptance gates remain open.** H acceptance is blocked by the now-measured version/identity/publication prerequisites; its eight acceptance families have not passed. I has a shared backend projection but still needs its user workflow; J has reusable bounded-v1 routing but no completed v2 handoff.

The new path can select a catalog measure, choose and run an approved diagnostic, observe the result and choose a different next test. It can now derive approved record projections from reusable model reviews and ticket filters, then use saved keyed comparisons in later decisions. It no longer requires an operator to prewrite the whole sequence. With reviewed model mappings, source tests are derived from the ticket filters rather than manually authored per ticket. It can also establish whether supported captured count/sum totals agree with their bounded record evidence, including whether those records explain a numeric delta. It still cannot certify a general business cause from incomplete evidence. Numeric observations and diagnostic differences come from saved receipts. A reviewed watermark policy can now establish a narrow age condition; the reported business cause, hypotheses and routing remain unverified.

## Remaining grouped milestones

1. **Resolve the measured proof blocker:** isolate and enforce the fixture publication boundary, separate collector/publisher and readonly investigator identities, then bind input/model hashes to publication and complete readbacks. The [live preflight](native-proof-preflight-milestone.md) documents exact observations. **Complete trustworthy investigation and proof:** effective report/identity/date context, authoritative source mappings, version/shared-generation evidence, supported causal/freshness/application-intent verifiers, impact/ownership and provider-wide monetary governance. Shared adaptive request allowances are now implemented. Complete the remaining B-G exit gates together with meaningful end-to-end checks.
2. **Prove generality:** freeze the runtime and run all eight hidden/native acceptance families, including new additive, ratio and complex measures, healthy/defect/gap variants and repeated planner evaluations. Current injected tests and live smoke checks do not replace this gate.
3. **Complete the user product:** resolve business tickets/screenshots into reviewed scope, build the shared business/technical workspace, integrate reviewed v2 routing/triage, then deploy and verify the complete workflow.

See the [tracker](progress.md), [milestone behavior and limits](adaptive-investigation-milestone.md) and [A-J acceptance plan](architecture/phases-and-acceptance.md). PR count is not a completion measure.
