# Independent lower-layer read (item 2b)

Updated 2026-09-27. `evaluate()` can now read a `declared_source` layer on an
independent surface, the Fabric SQL analytics endpoint, as the least-privilege
reader. The within-layer DAX check is kept alongside it. **No comparison run
(item 3) has been performed.**

## How the quantity is obtained: compiled, never templated

When the resolved path reaches a `declared_source` layer and the adapter
declares `independent_lower_surface`, `_lower_quantity()` builds the lower
quantity **only from declarations**:
- **The binding:** a `RESOLVED` binding and its declared SQL endpoint asset. The
  endpoint's discovered name is the database.
- **The partition:** the definition's single, whole-entity partition source
  (schema and entity).
- **The column:** the measured column's declared `sourceColumn` and `dataType`,
  from the referenced `SemanticColumn` asset.
- **The query:** `SELECT SUM(<source column>) AS quantity FROM
  <schema>.<entity>`. It is compiled by the existing SQL compiler against a
  catalog derived from those declarations (`DECLARED_BY_DEFINITION`), through the
  admission path (`flexible_tools`, new tool `bounded_fabric_sql`), with a sealed
  receipt. The tool requires that declared catalog, and it is never offered to a
  planner.
- **Nothing hard-coded:** no table, measure or column names, and no join shapes
  or per-family behaviour, appear in code. A test checks the adapter, engine and
  admission code for estate names.

**On a measure and an estate never seen before:** the same steps apply
unchanged. The quantity is compiled only if the measure is a plain `SUM` over one
column, and the definition declares all of the following:
- a single whole-entity partition with its source schema and entity;
- a physical `sourceColumn` for that column;
- no security roles;
- a SQL endpoint for the binding.

If any is missing, the independent read is refused with the reason recorded, and
the existing within-layer DAX check runs instead. Nothing is approximated or
matched by name.

## Faithful equivalence or `NOT_COMPARABLE`

- **Filtered scope:** the refusal is **unchanged, and it comes first**:
  "Declared source comparison does not yet translate filtered scope
  faithfully." Nothing is read.
- **Unfaithful mappings:** each is refused, the within-layer check runs, and the
  reason is kept as `independent_read_refused`. Covered by tests:
  - security roles present;
  - more than one partition;
  - a non-entity partition;
  - a calculated column, or no source column;
  - no declared endpoint;
  - an unresolved binding.
- **Security roles:** a model with row-level security could filter the DAX side
  and not the SQL side, so it is refused outright.

## The surfaces

| | Presentation | Declared source |
| --- | --- | --- |
| Engine | `POWER_BI_DAX` | `FABRIC_SQL` |
| Connection | workspace | `sql://<endpoint host>` |
| Object | model ID (not self-reported) | database (self-reported by `DB_NAME()`) |
| Identity | the reader (`USERPRINCIPALNAME()`) | the reader (`SUSER_SNAME()`) |

- **Engine and connection differ,** so the #235 cross-surface invariant holds by
  construction.
- **Identity is deliberately the same** least-privilege reader on both sides.
  Item-2.md expected the identity to differ as well. It does not, and that is by
  design: the reader is the one identity that should hold this access.
- **Read-only first:** the lakehouse transport (`Read-FabricSqlAggregate.ps1`)
  runs the same read-only permission guard as the Azure SQL reader before any
  query. It always names the database.
- **Self-report:** in the same connection, the endpoint reports who connected
  and to which database.

## Provenance, `WITHIN_LAYER_CHECK`, `DEFECT`

- **Provenance:** every cross-surface comparison records its lower binding's
  provenance in both outputs (`compared_bindings`). A comparison resting on an
  `INFERRED_FROM_CODE` binding also names that in its limits, and validation
  refuses a claim that omits it. No code produces `INFERRED_FROM_CODE` today;
  every binding is `DECLARED_BY_DEFINITION`.
- **`WITHIN_LAYER_CHECK`:** still reachable. It is reached with no independent
  surface, with a refused mapping, and with a filtered scope (as
  `NOT_COMPARABLE`).
- **`DEFECT`:** a divergence found this way **cannot become `DEFECT`**,
  confirmed by test, not assumed. It covers three profiles: no competing checks,
  checks declared but unavailable, and checks declared with nothing explaining.
  In each, the existing gate returns `NO_KNOWN_PATTERN`, naming the competing
  explanations that were not checked. For this adapter, `presentation_context`
  is always `INCONCLUSIVE` (static definitions cannot establish runtime
  selection), so `DEFECT` is currently unreachable.
- **Definition checked on divergence:** a divergence still asks for the
  transformation definition when that capability is declared.

## Transport checks (not an investigation)

Two metered reads of the declared-source layer only, through
`adapter.evaluate()`. Recorded as they happened:
1. **`lower-read-check-20260927T004920Z`: refused.** The reason was "The
   measured column does not declare a physical source column", and it fell back
   to the within-layer DAX read. **This was an adapter bug:** the column
   declarations are on the referenced `SemanticColumn` assets, not on the table
   asset. Fixed, with a regression test.
2. **`lower-read-check-20260927T005032Z`: `OBSERVED`.**
   - **Compiled:** `SELECT SUM([units]) AS [quantity] FROM [dbo].[movement_values]`,
     on `warehouse_gold_e1b8e1`.
   - **Guard and self-report:** the read-only guard passed on the lakehouse
     endpoint. The self-report was the reader on `warehouse_gold_e1b8e1`, with
     attestation `MATCHED` on identity and object.
   - **Receipt:** sealed, `COMPLETE_RESPONSE`.
   - **Not compared:** the value was not compared with the DAX baseline. That
     comparison is item 3.

## Not established

- **No investigation has run with the independent path,** and no cross-surface
  comparison of real values has been made.
- **The engine fingerprint does not cover the adapters.** `fingerprint()` hashes
  only `scripts/investigator/*.py`, not `scripts/investigator/adapters/`. So the
  engine tag `unfrozen-a909b4d9785e` does not change when only the adapter
  changes, and a freeze would not detect adapter changes. Recorded here; not
  fixed in this PR.
