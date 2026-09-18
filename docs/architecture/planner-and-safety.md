# Evidence-led reasoning and governed execution

Target behavior follows [review sections E-G](enterprise-discovery-pivot.md).
The candidate-selection runtime remains during migration; [status](../current-delivery-status.md)
records actual capabilities.

The LLM resolves unfamiliar questions, retrieves discovered context, proposes
hypotheses/tests and revises interpretations from observations. DAX, SQL, notebooks,
pipelines, filters and descriptions are untrusted data, never tool authority.
There is no mandatory layer sequence or parent-scalar-first rule for every test.
Missing business meaning produces a specific context question. Power BI executes DAX.

Deterministic orchestration validates query syntax, identity, scope, versions,
budgets and completeness. Keep durable reservations, cancellation, idempotency,
receipt integrity and uncertain-completion recovery. Saved replay makes no queries.
Persist Hypothesis, Test, Observation, Interpretation and Next action, not private
chain-of-thought. Facts/numbers reference receipts; inferred context stays inferred.

Claims use OBSERVED, STRONGLY_SUPPORTED, VERIFIED or INSUFFICIENT_EVIDENCE.
New outcomes: EXPECTED_BEHAVIOR, LIKELY_TECHNICAL_DEFECT,
VERIFIED_TECHNICAL_DEFECT, SOURCE_OR_APPLICATION_ISSUE, REFRESH_OR_FRESHNESS_ISSUE,
BUSINESS_CONTEXT_REQUIRED, INSUFFICIENT_EVIDENCE, UNSUPPORTED, UNRESOLVED.
Version them without upgrading historical outcomes. Completion is not resolution.

A likely mechanism needs relevant observations and stated alternatives/limits;
a verified cause needs its mechanism and intended contract established. Equality
alone does not prove expected behavior. Shared-generation/exclusivity requirements
limit applicable claims, not all useful reads. Existing formal proof tools remain
optional advanced checks, not the primary delivery sequence.

Preserve free SQL overage settings and bounded recovery. Resource limits do not
certify zero cost. No automatic repairs, data writes, deployments or runtime PRs.
External issue/notification delivery remains human-reviewed.

Negative tests cover unauthorized assets, malicious ticket/metadata/code comments,
query write/escape attempts, ambiguous names, stale context, timeout/cancellation,
empty/truncated results, duplicates, unknown rules and contradictory evidence.
