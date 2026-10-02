# Project handoff: self-discovering enterprise investigator

Updated 2026-09-18. [Current delivery status](docs/current-delivery-status.md) is
authoritative. [The new mission](SELF_DISCOVERING_ENTERPRISE_INVESTIGATOR_PLAN.md)
supersedes manually onboarded models as the primary product path.

The SQL/application/Fabric/Power BI foundation, metadata/lineage, manually onboarded
catalog, adaptive runtime, receipts/budgets, dedicated reader and local text/screenshot
workspace are working foundations. PR #192 merged at `d0c7bee`; its aggregate/record
checks remain reusable.

Discovery-to-ticket merged in PR #196: environment
scans, independent model context, versioned graph/search and automatic catalog
projection. See current status for acceptance results and remaining limits.
Dynamic reasoning and parser-governed SQL/DAX merged in PR #198, with 891 regression
tests, 40 browser checks and live native/source reads. The engine is now tagged
unknown-domain-engine-v1; unfamiliar warehouse assets were published after freeze.
The [challenge](docs/unknown-domain-challenge.md) is in progress, not passed.
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


## Dated correction: surface verification (2026-10-02, America/Chicago)

The historical claims above about verified cross-surface comparisons must not be
read as satisfying the full-coverage standard merged in #299 (`955b3fe`). The
[receipt audit](docs/retrospective-surface-attestation.md) found identity-only DAX self-reports and
identity/database-only SQL self-reports, with engine/connection (and the DAX
model object) unattested. Earlier MATCHED/CROSS_SURFACE_VERIFIED labels admitted
partial coverage; #299 now calls that PARTIAL and refuses verified boundary
eligibility. Snapshot alignment remains unestablished separately.

Run c2658c88 remains the first completed end-to-end **execution**, with two
observed values of 8,765 on independently declared routes; it did not establish
a fully attested verified boundary. Run 3d2c5bf0 observed 8,765, 8,765 and 7,661,
and invoked a judge that identified a compatible join mechanism; neither its
DAX/SQL boundary nor its SQL/SQL boundary satisfies #299. These observations
and the qualified mechanism remain useful, but do not prove actual duplicate
matches, current snapshots, intended semantics or verified transformation
attribution. Other historical comparisons using the same partial self-report
contract are subject to the same qualification. Original prose, outputs,
receipt bodies, counts and outcome labels are preserved, not retrospectively
regraded. Ledger corrections are annotations, not replacement runs.
