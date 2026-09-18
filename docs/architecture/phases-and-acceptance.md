# Discovery-first stages and acceptance

This replaces the old A-J delivery order. [Current status](../current-delivery-status.md)
records implementation. Stage descriptions are commitments, not completion claims.
The [architectural review](enterprise-discovery-pivot.md) defines migration.

| Stage | Deliverable | Exit evidence |
| --- | --- | --- |
| 1 Architectural pivot | Audit, PR reconciliation, manual-dependency map, target/migration and README | Complete A-J review; working code distinguished from target; prior roadmap historical |
| 2 Enterprise discovery | Approved roots, durable enumeration/scans, coverage/diffs, periodic dispatcher | New models/reports/SQL/Fabric/semantic assets found without registration; partial/denied scan cannot imply deletion; repeat scheduling demonstrated |
| 3 Automatic context graph | Independent model/report/source graph, lineage, capability and ticket projection | New supported assets become ticket targets under policy without business-review gate; ambiguity retained; changed context invalidates affected work |
| 4 Expanded reasoning | Context retrieval, semantic/transform interpretation, hypothesis-led tests | Unfamiliar questions resolved; evidence changes next tests; failed hypothesis revised; inferred meaning labelled |
| 5 Flexible tools | Parser-enforced SQL/DAX, profile/key/dimension/freshness/transform diagnostics | Real reads/receipts; new diagnostic needs no Python template; write/escape/timeout/truncation negatives pass |
| 6 Engine freeze | Tagged code/prompt/tool/policy manifest; separate evaluator/publisher | Frozen logic/config audited for scenario/answer leakage; truth unavailable to runtime |
| 7 Unknown Domain Challenge | Post-freeze Inventory/Warehouse SQL/Fabric/model/reports and nine ticket families | Real discovery/investigations without ID registration/code edits; honest pass/gap/failure matrix; all-gap answers fail |
| 8 UX consolidation | Question plus optional report/screenshot/value; shared timeline | Actual Power BI-to-investigator business/technical flow; real progress/shared evidence; hosting/auth verified before hosted claim |
| 9 Support-engine-ready core and reviewed handoff | Generic asset/context/tool/evidence boundaries; qualified impact, ownership, reviewed drafts and triage | No automatic send/repair; stale/duplicate approval handling; missing owners explicit |

Group implementation: architecture; discovery-to-ticket (2-3); reasoning/tools
(4-5); freeze/challenge (6-7); UX/handoff (8-9). No helper-only PR chains.

[The exact experiment](enterprise-discovery-pivot.md#h-frozen-unknown-domain-challenge)
covers discrepancy, ratio, nested derived measure, visual context, freshness,
transformation, source/application, expected behavior and missing business context.
Also test new SQL/Fabric/semantic tables, models/reports, changed DAX/relationships,
rename/removal and permission failures. Repeat selected LLM cases; report reliability
and resource usage. A failed hypothesis must be revised from actual evidence.

Freeze before domain publication. Credentials/access/business documentation may
change but cannot hide executable scenario logic or answers. Runtime/prompt changes
invalidate the attempt: refreeze and run a fresh variant. No domain-name branches.

Preserve generator, portal, bounded-v1, catalog, runtime, intake and delivery
regressions. Primary success is unfamiliar-environment behavior, not test/PR count.
Formal exclusivity is no longer a universal prerequisite; evidence fits each claim.
The [historical A-J plan](archive/2026-09-16-phases-and-acceptance.md) remains readable.
