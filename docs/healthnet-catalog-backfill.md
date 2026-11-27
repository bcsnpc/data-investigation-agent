# HealthNet native catalog backfill

Owner-approved 2026-11-26. Frozen image 8018ca9a and its engine, prompts and guards are unchanged. Only native discovery records, explicit native bindings and deployment input pins change. No expected-answer fields were consulted.

All 28 model tables bind to their exact recorded SQL objects through the named warehouse connection. The native server is explicit; the model database GUID is matched to the native Warehouse ID, whose recorded SQL database is hn_dw. Operations currently declares Direct Lake entity partitions; Revenue and Productivity declare Import M partitions. M parameter values come from the models' native expressions. No table is mapped by a similar name outside its exact database/schema.

Native column inventory: hn_clinical 23 tables / 265 columns; hn_billing 14 / 161; hn_raw 33 / 344; hn_dw 25 / 306. Three models contain 28 tables / 343 declared business columns plus 28 native engine row-number columns. All 333 dependency/relationship column-reference occurrences and 65 visual member-reference occurrences resolve. Missing columns: zero. Missing model-table SQL bindings: zero.

Fresh native SQL module bodies add 19 INSERT producer bindings, and native pipeline definitions plus verified connection IDs and native lakehouse endpoint metadata add 32 copy bindings to the two application databases. Every mapped object must already exist at its exact native address; unresolved objects are reported, never guessed. This backfill found no unresolved producer/copy input addresses. These are declared definition links, not proof that a job ran or that values agree.

The frozen path builder and validator were checked offline on the original HN-003/HN-007 requests. All eight former catalog rejections are admitted on their actual scoped paths (20 nodes each, no truncation); the source/raw/warehouse query routes are present. No live query or model was used in that preflight. The validator was not widened to every object in the estate.

HN-008 had the same initial catalog defect on three requests. It is also unscored environmental, preserving its original answer. Two of its queries independently contain unsupported RIGHT syntax; that secondary limitation remains in the frozen grammar. No claim is made that catalog repair alone makes every HN-008 query valid.

HN-003/HN-007 originals and original independent grades are preserved as unscored environmental, with one owner-approved replacement each. HN-008's original is preserved likewise. The previously approved HN-001/HN-002 replacements remain pending. All original calls stay charged.

The legacy installation has a single optional global system_of_record field. It remains unset rather than arbitrarily declaring one application table as the source for this two-application estate. Native per-table source routes now come from the graph. This limitation is separate from binding/column completeness and remains visible in the case context.

HN-009 remains UNESTABLISHED: its start timed out without returning an Azure execution name. Execution-list APIs return BadGateway; native activity/capture checks have not established a matching execution. It is excluded from new submissions, never counted as a result, and will not be duplicated while uncertain. Reconciliation continues alongside other work.
