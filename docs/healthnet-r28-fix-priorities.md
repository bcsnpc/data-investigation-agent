# R28 priorities from the frozen HealthNet test

Owner decision, 2026-11-26: defer fixes until after the complete HealthNet test. Frozen image and original outcomes stay unchanged.

1. Model-facing catalog scope: the HN-002 request contains all three models, an unrelated A/R candidate and full multi-table pipeline definitions. Use exact native ownership/bindings and transitive candidate paths; retain full immutable definitions for evidence lookup. Do not drop tied candidates, required dependencies or guard scopes. Validate generically on practice/saved evidence before changing the engine.
2. No-tool delivery retry loop: HN-002 performed twelve late model calls with no tools or new reads after source-consistency rejection and delivery-repair exhaustion, spending $1.239632. Diagnose the source-declaration boundary separately; stop no-progress retries with checked findings and an honest limitation. Never weaken read-only, evidence-ID or harmful protections.

Evidence: [cost audit](healthnet-opus-cost-audit.md), [call-level measurements](healthnet-opus-cost-audit.json). These are measured plumbing/control-flow defects, not permission to alter sealed expectations or the test image. No fixes applied during HealthNet.
