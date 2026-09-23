# Compiler binding and physical-context reliability

2026-09-23. Issue #199; follows accepted #218. Known-domain work only.

## Decision and scope

The stopping-contract hypothesis was evaluated and rejected. Its proposed fields,
method and negative results remain in [the review record](stopping-criteria-review.md).
No completion-basis/reason field or experimental stopping instruction is adopted.
This change addresses compiler correctness, rejection feedback and physical
membership only. There is no required SQL step, connection preference, query
rewrite, scope expansion, permission change or cross-system adapter.

## Compiler correction

The SQL compiler now reuses a binding for an identical typed literal, keeping text,
integer and decimal values separate. It preserves original expressions, so repeated
SELECT/GROUP BY CASE expressions retain identical bound forms. The old 60 literal
occurrence limit remains, as do all other admission limits. Validator version is
bounded-tsql-v3. Saved receipts and historical runs are not rewritten.

The exact G call-10 proposal is retained as a regression fixture. Tests compare
its qualified CASE expression to the parameterized expression with literals
restored only in test code, assert identical SELECT/GROUP BY bound forms, and
check type/value separation. Offline recompilation against the actual saved
candidate and pinned catalog succeeds with four parameters instead of ten.
No live read was used to confirm this deterministic fix. Receipt:
`.local/physical-binding-20260923/G-recompiled.json`.

## Rejection feedback and physical membership

Complexity errors retain the measured SELECT/join counts and caps. Unavailable
object errors identify the searched approved SQL connection/schema, requested
object, a bounded list of same-name catalog retrieval targets, and a scoped search.
Hints never choose a replacement name or establish identity by name equality.
Cross-connection candidates explicitly cannot be joined through this SQL path;
separately authorized reads may be compared with equivalence limitations.

Search results, asset/child lookups, definition excerpts, semantic context, domain
profile tables and directory entries identify physical ownership and known schema.
An unobserved schema remains UNKNOWN; lakehouse names do not imply dbo or an
established SQL endpoint. Compaction preserves binding labels and actionable
rejection fields. Advertised SQL capability identifies its actual configured
connection and approved schema. Existing execution admission remains authoritative.

Offline replay of F calls 10/11, G call 6 and I call 6 confirms that original
queries stay rejected and unchanged while feedback becomes actionable. F/G
complexity reads SELECTs 9/8 and joins 3/4. F receives exact catalog hints; I sees
Fabric ownership instead of an implicit Azure SQL binding. E's accessible notebook
history remains present after projection. These checks execute no data tools.
Receipt: `.local/physical-binding-20260923/rejection-replays.json`.

## SELECT-count review

The cap stays at eight SELECT nodes and four joins. CASE expressions themselves
do not add SELECT nodes. The recorded F/G proposals exceeded the cap because of
nested SELECTs (CTEs/scalar subqueries), not CASE branches alone. These are
structural-complexity guardrails, not reliable estimates of resource cost: row
counts, indexes, selectivity and execution plans are not represented by this count.
One SELECT can scan a large table; several small subqueries need not be expensive.
There is no measured execution-cost basis here for raising the cap, and it was
not tuned to admit F/G. No new live cost experiment was performed.

## Validation and re-baseline

Six focused binding/feedback tests, 36 flexible-query tests and nine projection
tests passed. The first full-suite run caught a missing-SQL-configuration error
in capability display (1 error in 1,008 tests); the display now leaves absent
connection/schema unknown, and all nine domain-profile tests pass. The final
full-suite rerun passed all **1,008 tests** in 362.588 seconds. Two generator tests
pass; 63 local documentation targets resolve and the staged secret scan is clean.

The planned re-baseline is E/F/G/I plus two extra G trials, under the same model,
profile, generation settings, catalog, policy and serial 65-second pacing as #218.
Every attempt is recorded and labelled KNOWN_DOMAIN_REGRESSION, with its own
ledger row. Deployment readback confirms GPT-5.4 2026-03-05, GlobalStandard 100
units, 100,000 TPM / 1,000 RPM. No configuration changes are needed or made.
Counters, reservations and deadlines remain intact. No freeze, fresh variant or
unfamiliar-domain claim follows. Original F-paced and baseline F remain failed.
