# Project handoff: self-discovering enterprise investigator

Updated 2026-09-18. [Current delivery status](docs/current-delivery-status.md) is
authoritative. [The new mission](SELF_DISCOVERING_ENTERPRISE_INVESTIGATOR_PLAN.md)
supersedes manually onboarded models as the primary product path.

The SQL/application/Fabric/Power BI foundation, metadata/lineage, manually onboarded
catalog, adaptive runtime, receipts/budgets, dedicated reader and local text/screenshot
workspace are working foundations. PR #192 merged at `d0c7bee`; its aggregate/record
checks remain reusable.

Discovery-to-ticket is implemented on the current feature branch: environment
scans, independent model context, versioned graph/search and automatic catalog
projection. See current status for acceptance results and remaining limits.
The next grouped milestone is dynamic reasoning and governed tools. Generated
SQL/DAX and post-freeze unknown-domain acceptance are not yet delivered.
The [audit/proposal](docs/architecture/enterprise-discovery-pivot.md) and
[stages 1?9](docs/architecture/phases-and-acceptance.md) define the work.

The user authorizes autonomous implementation, PR review/merge and continuation
through the roadmap. Stop only for a genuine external blocker or material change
in product direction. Data investigation is the first domain of an enterprise
support engine; retain generic asset/context/tool/evidence concepts without
building hypothetical vendor integrations or generic SaaS features.

Do not resume the old proof-preflight-first sequence. Keep useful safety/evidence
controls and make claims proportionate to observations. Existing Azure application
and SQL/Fabric/Power BI have historical live verification. V2 remains local;
enterprise hosting/auth and deployment are pending. See [run/demo](README.md#run-and-demo).

[The earlier handoff](docs/project-state-before-discovery-pivot.md) is historical,
including its old limitations and next-step paragraphs. [Progress](docs/progress.md)
retains milestone evidence and chronology.
