# Next failed-ticket fix batch

Owner steer, 2026-11-02. This batch includes containment commit `3676d2ff`; it changes no ticket, golden record, expectation or saved tape.

Ambiguous report/table candidates are checked with up to three bounded native reads. A target is selected only when every candidate was checked and exactly one matches. Unsupported scope stays explicitly unchecked rather than silently becoming an unfiltered query. Loose card references cannot acquire a page the ticket did not name.

Every terminal result now includes the established verdict or `not established`, findings per reached layer, retained calculation, undecided checks and reasons, and engineer/business-owner routing. Partial findings do not upgrade a failed or clarifying run to answered. This is output completeness, not a claim that every investigation now succeeds.

Investigation query validation admits current-database SQL catalogs and DMVs, direct DAX INFO rowsets and exact admitted Delta DESCRIBE/HISTORY reads. Writes, DDL, execution, cross-database substitutions and unsafe expressions remain refused. Native permissions still apply. Retention explanations use an explicit minimum over temporal history or a complete bounded Delta history result; a full latest-N sample cannot establish the oldest available version.

The saved-trace backtrack covers all 25 independently reviewed failures, including R17-01 despite its original primary pass. Primary 5/30, strict 4/30 and reviewed 5/30 remain distinct; reviewed harmful count is 2. No score was changed by the backtrack.

Focused validation: 252 tests passed. Full hosted suite and tested-image publication are required before admitting the next failed-only OpenAI pass. The original dev1 stale cohort continues on its original image, separately from these fixes.

Metadata references: [SQL DMVs](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/system-dynamic-management-objects), [DAX INFO.PARTITIONS](https://learn.microsoft.com/en-us/dax/info-partitions-function-dax), [Fabric Delta describe](https://learn.microsoft.com/en-us/fabric/data-engineering/delta-lake-describe).
