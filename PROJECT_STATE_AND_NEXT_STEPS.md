# Project handoff: self-discovering enterprise investigator

Updated 2026-09-18. [Current delivery status](docs/current-delivery-status.md) is
authoritative. [The new mission](SELF_DISCOVERING_ENTERPRISE_INVESTIGATOR_PLAN.md)
supersedes manually onboarded models as the primary product path.

The SQL/application/Fabric/Power BI foundation, metadata/lineage, manually onboarded
catalog, adaptive runtime, receipts/budgets, dedicated reader and local text/screenshot
workspace are working foundations. PR #192 merged at `d0c7bee`; its aggregate/record
checks remain reusable.

Next is automatic discovery-to-ticket context under environment policy. Registration,
report lists, business review and enablement currently gate catalog use; the LLM
selects precompiled tests. Generated SQL/DAX and post-freeze unknown-domain acceptance
are not yet delivered. The [audit/proposal](docs/architecture/enterprise-discovery-pivot.md)
and [stages 1-9](docs/architecture/phases-and-acceptance.md) define the concrete work.

Do not resume the old proof-preflight-first sequence. Keep useful safety/evidence
controls and make claims proportionate to observations. Existing Azure application
and SQL/Fabric/Power BI have historical live verification. V2 remains local;
enterprise hosting/auth and deployment are pending. See [run/demo](README.md#run-and-demo).

[The earlier handoff](docs/project-state-before-discovery-pivot.md) is historical,
including its old limitations and next-step paragraphs. [Progress](docs/progress.md)
retains milestone evidence and chronology.
