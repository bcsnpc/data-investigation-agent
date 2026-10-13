ï»¿# Round Eighteen â€” Part D checkpoint

Recorded 2026-10-13 UTC. This is the setup/documentation result, not a successful
estate onboarding or completed cloud demonstration.

The client guide covers prerequisites with consequences, configuration, a single
deployment command, preflight, onboarding and removal boundaries. The separate
cloud verification guide provides the bounded migration path. Reviewing and
following the configuration/preflight steps exposed and corrected an example
path error, missing separate database/compute region parameters, workstation
credential assumptions, and inconsistent identity/adapter credential references.
Hash-bound control imports are now documented explicitly.

The retained-control fixture preflight is **8 PASS / 0 FAIL / 24 MISSING**.
Billing candidate 01 failed manifest validation; its result remains preserved.
Candidate 02 and an independent guide recheck both give **8 PASS / 0 FAIL /
13 MISSING**. Every new guide check was offline: zero estate/model/control calls.
Neither report is READY. Billing's example currently declares only its semantic
model, so its shorter checklist does not cover the entire billing chain.
Detailed receipt hashes, commands and missing evidence are in
[the guide audit](round-eighteen-guide-audit.md).

`what-we-store.md` describes metadata, bounded query evidence, tickets, exact and
projected captures, shared PostgreSQL, private replay SQLite, Blob storage,
retention and deletion. Schema/shape inspection confirmed that the sampled
`inventory.sqlite` files contain collector metadata/observations rather than
business tables. Sampled diagnostic results include actual values, up to 249
rows; they are not metadata-only. The cloud demo input package also passed the
credential scanner across both selected SQLite snapshots and JSON inputs.

**The requested universal claim that no historical recording contains bulk
estate rows is not established.** The inspected snapshots and selected converted
tapes do not cover the entire archive. No bulk table was found in the inspected
inventory samples, and no sealed tape was rewritten. The remaining archive needs
its own content audit before any archive-wide claim or publication. Privacy-
projected PostgreSQL persistence is also still an explicit unsupported boundary.

The guide has not yet been executed from a clean client subscription through
successful onboarding and teardown. The infrastructure operator has separate
platform evidence; guide-driven billing prerequisite checks remain incomplete.
No deletion was performed to test the teardown instructions. The current guide
is executable and candid about these limits, not certified as full onboarding.

`owner-actions.md` now distinguishes resolved approvals from remaining operator
work. Same-tenant client managed identity is the default. The approved test user's
vault cache remains that existing reader; the code-reader Contributor is never a
quantity identity. Cross-tenant MI federation is documented as a future proposal
only. No new permission or secret was created by this documentation work.

A later offline [recording-content audit](round-eighteen-recording-content-audit.md)
expands the earlier samples to the available loose tape JSON and inventory/catalog
schemas. Its exact coverage and exceptions are recorded there; it does not turn
schema-only or archive-member inspection into a universal no-bulk claim. Storage
documentation also now names unenforced screenshot expiry and the remaining
projected cloud-capture boundaries.


## Part D close, 2026-10-13

The final structural audit and its explicit gaps are committed. The separate legacy export is not deleted or published; normal recording publication excludes it. A final code review corrected a shared-state overclaim: smart-ticket state is wired to PostgreSQL, but claim-first/runtime/image state remains per-job SQLite and the generic case-file repository has no production writer. These gaps are documented rather than represented as a completed migration. Existing workstation secret mechanisms remain; approved cloud copies use Key Vault.

Guide-driven billing configuration and retained-control preflight were completed offline, with the failed initial candidate preserved. Whole-estate readiness, a fresh client subscription onboarding, and deletion/teardown are not established. No new estate/model request or permission change was made during Part D. The cloud demo remained blocked by exact replay in Part C. Final integrated regression and closing disk measurement are reported in the round summary.


## Final close, 2026-10-13 05:48 UTC

Integrated db3bed8 suite:4,073 PASS,46 skipped,1,416 subtests in449.65seconds. All eight cloud CI shards passed and GHCR publication succeeded (workflow38352575331). No live execution uses that corrected image in this round. All22 listed Container Apps executions are stopped. Closing SELECT-only repeatable-read report at05:48:18 preserves pot3,017/4,000, rolling376/3,000, restoration95, new178 physical reservations SETTLED, and zero new monetary reservations/model spend. D: free12,648,144,896 bytes, above10GB. Opening Part D free13,558,284,288; net change -910,139,392 bytes after retaining new evidence/working material, not a net cleanup saving. Reports and fixes are pushed to draft424; neither PR merges. The demo, full state migration, whole-estate onboarding and universal archive-content claim remain unearned as listed in the summary. No more admissions.
