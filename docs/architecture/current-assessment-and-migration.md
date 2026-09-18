# Current assessment and migration

The code audit and migration proposal are in
[architectural review sections A, B and I](enterprise-discovery-pivot.md).
[Current delivery status](../current-delivery-status.md) tracks implementation.

PR #192 merged at `d0c7bee` after six CI checks passed. No other PR was open at
audit time. No cloud deployment changed. The collector already enumerates workspace
items and visible SQL objects. Publication into a manually registered, reviewed
and enabled model/report catalog is the main discovery bottleneck. The adaptive
LLM selects precompiled tests; it cannot yet generate diagnostic SQL/DAX or retrieve
arbitrary estate context during a run.

Use additive inventory/graph schemas and a catalog projection. Separate discovered
facts, query policy and business authority. Replace report-owned model-assets
assumptions together. Preserve old run readers, review/revocation history and
bounded-v1. Workspace policy must not silently broaden the reader's permissions.
Rollback chooses legacy mode for new work; existing runs keep their original context.

The [older assessment](archive/2026-09-16-current-assessment-and-migration.md) is
historical; its PR stack and proposed module list are not current status.
