# Baseline SQL proposal audit

2026-09-23. Companion to [baseline completion and stopping review](stopping-criteria-review.md).
All nine SQL proposals below are copied from the recorded provider function-call
arguments, not reconstructed from a remembered plan. Baseline A/B/C/D/H proposed
no SQL. Tape integrity hashes were checked by `planner_recording.load_session`.
No queries were executed for this audit and no engine fix was applied.

## Findings by failure class

| Proposal | Recorded result | Specific cause | Item 4 repair? |
| --- | --- | --- | --- |
| E call 2 | Admitted; SQL 229 | Permission denied on `app.dataset_runs`; relevance to this domain was not established | No. Schema backfill cannot grant access or establish relevance |
| F call 10 | `Relational complexity budget exceeded` | 9 SELECT nodes exceeds 8; 3 joins is below the 4-join cap. Four CTE SELECTs, four scalar subqueries, one final SELECT | No. Reducing query structure changes executable text |
| F call 11 | `SQL object unavailable or view dependencies not validated` | `dbo.stock_movements_e1b8e1` and `dbo.product_rates_e1b8e1` are absent from the approved Azure SQL catalog; its corresponding discovered tables are in `app` | No. Guessing/rebinding schema is not prerequisite backfill |
| G call 6 | `Relational complexity budget exceeded` | 9 SELECT nodes exceeds 8; 3 joins is below 4 | No. Needs a smaller model-proposed test |
| G call 7 | Completed | Two missing approved schemas were fetched locally, then normal validation and reader execution succeeded | Yes; two schema-prefetch repairs actually occurred |
| G calls 8 and 9 | Completed | Admitted source diagnostics with successful reader receipts | Not needed |
| G call 10 | Admitted; SQL 8120 | Compiler parameterization changed identical SELECT/GROUP BY CASE expressions into different parameter expressions | No. Compiler correction is separate from proposal repair |
| I call 6 | `SQL object unavailable or view dependencies not validated` | Joins approved `app.inventory_adjustments_e1b8e1` to `dbo.movement_values`, a Fabric Gold lakehouse table, through the Azure SQL connection | No. Cross-connection routing cannot be invented by schema backfill |

These are not unsupported parser grammar failures. Every SQL proposal parsed;
none hit the AST node allowlist. Two hit the separate resource-complexity policy,
two selected objects outside the approved connection catalog, one hit remote
permission, and one exposed a compiler binding defect after admission. Three
completed. The local rejection rate is 4/9; the two remote failures are not local
rejections or LLM provider errors.

F call 10 also contains the wrong `dbo` references, but the complexity check
rejects it before catalog binding is reached. F's `dbo` references are wrong for this connection, not evidence that the correctly
named `app` tables need another grant. Both app tables are discovered USER_TABLEs
with the proposed source columns. F had retrieved notebook text and a Silver
lakehouse, not the exact Azure SQL schemas; its all-terms search for both table
names found no combined asset. Metadata from a lakehouse does not authorize the
same name in the Azure SQL endpoint. I likewise mixed two physical systems in one
query. No approved warehouse/lakehouse SQL endpoint adapter exists on this path.

Generic follow-ups for review, not implemented: report measured SELECT/join counts
with their caps; return scoped catalog search/retrieval targets for an unavailable
object without silently changing its name; retain connector provenance when
proposing joins. None is permission to add a cross-system mapping or increase a cap.
Item 4 can only backfill exact approved schemas and repair descriptive fields; it
must continue to leave executable text unchanged.

## G compiler evidence

Saved source execution `ae91520c-1751-4fa8-b1aa-d868d6999156` records
`SourceReadError`, `SqlException`, error **8120**, at query stage on its first
connection attempt. No retry or permission failure is recorded. The safe receipt
does not retain the server's full message; 8120 is the exact retained error number.

Offline recompilation matches the original candidate's compiled hash. In the
provider proposal the SELECT CASE and GROUP BY CASE are structurally identical.
The compiler gives each repeated literal a fresh parameter: SELECT uses positive
label `@p2`, negative `@p3`, zero `@p0`, and thresholds `@p6/@p7`; GROUP BY uses
`@p4`, `@p5`, `@p1`, and `@p8/@p9`. The paired values are identical, but the bound
expressions are different. This is consistent with SQL Server rejecting the
ungrouped `adjustment_units` expression. It should not be blamed on a poor model
query or fixed with a grant.

A generic compiler correction should preserve binding identity for repeated typed
literals/expressions, with a regression for the proposed versus parameterized
GROUP BY expression. That is a separate review item, not an item 4 text repair.
No live rerun or compiler fix was made for this review.

Local audit artifacts: `.local/known-baseline-completion-20260923/sql-tape-audit.json`
and `G-failed-compiled.json`. Full raw tapes stay local and unmodified. The SQL
below is the exact proposed text; compilation parameterizes values and adds the
bounded output limit before execution.

## Exact proposals

### E planner call 2

Session `3accd519-57e8-4121-aed5-e466d415281b`. Result: **FAILED: SourceReadError / SqlException / 229**.

```sql
SELECT TOP 50
  dr.dataset_id AS dataset_id,
  COUNT(*) AS run_count,
  MIN(dr.as_of) AS min_as_of,
  MAX(dr.as_of) AS max_as_of,
  MIN(dr.completed_at) AS min_completed_at,
  MAX(dr.completed_at) AS max_completed_at,
  SUM(CASE WHEN dr.status = 'SUCCESS' THEN 1 ELSE 0 END) AS success_runs,
  SUM(CASE WHEN dr.status <> 'SUCCESS' THEN 1 ELSE 0 END) AS non_success_runs
FROM app.dataset_runs AS dr
GROUP BY dr.dataset_id
ORDER BY MAX(dr.completed_at) DESC
```

### F planner call 10

Session `2fd74595-df28-48c0-b5e7-f50742f0d704`. Result: **Relational complexity budget exceeded**.

```sql
WITH movement_base AS (
    SELECT
        COUNT(*) AS movement_rows,
        COUNT(DISTINCT sm.movement_id) AS distinct_movement_ids
    FROM dbo.stock_movements_e1b8e1 AS sm
),
join_profile AS (
    SELECT
        COUNT(*) AS joined_rows,
        COUNT(DISTINCT sm.movement_id) AS joined_distinct_movement_ids,
        SUM(CASE WHEN pr.product_id IS NULL THEN 1 ELSE 0 END) AS unmatched_movement_rows
    FROM dbo.stock_movements_e1b8e1 AS sm
    LEFT JOIN dbo.product_rates_e1b8e1 AS pr
        ON sm.product_id = pr.product_id
),
fanout_movements AS (
    SELECT
        sm.movement_id AS movement_id,
        COUNT(*) AS joined_rows_for_movement
    FROM dbo.stock_movements_e1b8e1 AS sm
    LEFT JOIN dbo.product_rates_e1b8e1 AS pr
        ON sm.product_id = pr.product_id
    GROUP BY sm.movement_id
    HAVING COUNT(*) > 1
),
rate_multiples AS (
    SELECT
        pr.product_id AS product_id,
        COUNT(*) AS rate_rows_for_product
    FROM dbo.product_rates_e1b8e1 AS pr
    GROUP BY pr.product_id
    HAVING COUNT(*) > 1
)
SELECT
    mb.movement_rows AS movement_rows,
    mb.distinct_movement_ids AS distinct_movement_ids,
    jp.joined_rows AS joined_rows_after_product_join,
    jp.joined_rows - mb.movement_rows AS join_row_excess,
    jp.joined_distinct_movement_ids AS joined_distinct_movement_ids,
    jp.unmatched_movement_rows AS unmatched_movement_rows,
    COALESCE((SELECT COUNT(*) FROM fanout_movements AS fm), 0) AS movements_with_fanout,
    COALESCE((SELECT MAX(fm.joined_rows_for_movement) FROM fanout_movements AS fm), 0) AS max_join_rows_per_movement,
    COALESCE((SELECT COUNT(*) FROM rate_multiples AS rm), 0) AS products_with_multiple_rates,
    COALESCE((SELECT MAX(rm.rate_rows_for_product) FROM rate_multiples AS rm), 0) AS max_rate_rows_per_product
FROM movement_base AS mb
CROSS JOIN join_profile AS jp;
```

### F planner call 11

Session `2fd74595-df28-48c0-b5e7-f50742f0d704`. Result: **SQL object unavailable or view dependencies not validated**.

```sql
WITH source_movements AS (
    SELECT
        sm.movement_id AS movement_id,
        MIN(sm.product_id) AS any_product_id,
        COUNT(*) AS source_rows,
        COUNT(DISTINCT sm.product_id) AS distinct_products
    FROM dbo.stock_movements_e1b8e1 AS sm
    GROUP BY sm.movement_id
),
rate_counts AS (
    SELECT
        pr.product_id AS product_id,
        COUNT(*) AS rate_rows,
        COUNT(DISTINCT pr.unit_cost) AS distinct_unit_costs
    FROM dbo.product_rates_e1b8e1 AS pr
    GROUP BY pr.product_id
),
joined_counts AS (
    SELECT
        sm.movement_id AS movement_id,
        COUNT(*) AS joined_rows
    FROM dbo.stock_movements_e1b8e1 AS sm
    LEFT JOIN dbo.product_rates_e1b8e1 AS pr
        ON sm.product_id = pr.product_id
    GROUP BY sm.movement_id
)
SELECT
    COUNT(*) AS movement_ids_profiled,
    SUM(sm.source_rows) AS source_rows,
    SUM(CASE WHEN sm.source_rows > 1 THEN sm.source_rows - 1 ELSE 0 END) AS duplicate_source_row_excess,
    SUM(CASE WHEN sm.distinct_products > 1 THEN 1 ELSE 0 END) AS movement_ids_with_multiple_products,
    SUM(jc.joined_rows) AS joined_rows_after_product_join,
    SUM(jc.joined_rows) - SUM(sm.source_rows) AS join_row_excess,
    SUM(CASE WHEN jc.joined_rows > sm.source_rows THEN 1 ELSE 0 END) AS movement_ids_with_join_fanout,
    SUM(CASE WHEN COALESCE(rc.rate_rows, 0) > 1 THEN 1 ELSE 0 END) AS movements_on_multi_rate_products,
    SUM(CASE WHEN COALESCE(rc.distinct_unit_costs, 0) > 1 THEN 1 ELSE 0 END) AS movements_on_conflicting_cost_products
FROM source_movements AS sm
INNER JOIN joined_counts AS jc
    ON sm.movement_id = jc.movement_id
LEFT JOIN rate_counts AS rc
    ON sm.any_product_id = rc.product_id
```

### G planner call 6

Session `39503ca8-e318-493f-a6d1-201563c0b444`. Result: **Relational complexity budget exceeded**.

```sql
WITH movements AS (
    SELECT sm.movement_id AS movement_id,
           sm.units AS movement_units
    FROM app.stock_movements_e1b8e1 AS sm
),
adjustments AS (
    SELECT ia.adjustment_id AS adjustment_id,
           ia.movement_id AS movement_id,
           ia.units AS adjustment_units
    FROM app.inventory_adjustments_e1b8e1 AS ia
),
adj_per_movement AS (
    SELECT a.movement_id AS movement_id,
           COUNT(*) AS adjustment_row_count,
           SUM(a.adjustment_units) AS adjustment_units_sum
    FROM adjustments AS a
    WHERE a.movement_id IS NOT NULL
    GROUP BY a.movement_id
),
direct_join AS (
    SELECT m.movement_id AS movement_id,
           a.adjustment_id AS adjustment_id
    FROM movements AS m
    LEFT JOIN adjustments AS a
        ON m.movement_id = a.movement_id
)
SELECT COUNT(*) AS stock_movement_rows,
       COUNT(DISTINCT m.movement_id) AS distinct_stock_movement_ids,
       (SELECT COUNT(*) FROM adjustments AS a) AS adjustment_rows,
       (SELECT COUNT(DISTINCT a.movement_id) FROM adjustments AS a WHERE a.movement_id IS NOT NULL) AS distinct_adjustment_movement_ids,
       (SELECT COUNT(*) FROM direct_join AS dj) AS rows_after_left_join_on_movement_id,
       SUM(CASE WHEN apm.movement_id IS NOT NULL THEN 1 ELSE 0 END) AS stock_movements_with_adjustments,
       SUM(CASE WHEN COALESCE(apm.adjustment_row_count, 0) > 1 THEN 1 ELSE 0 END) AS stock_movements_with_multiple_adjustments,
       SUM(CASE WHEN apm.movement_id IS NOT NULL AND m.movement_units <> apm.adjustment_units_sum THEN 1 ELSE 0 END) AS matched_movements_units_not_equal_adjustment_units_sum,
       (SELECT COUNT(*)
        FROM adjustments AS a
        LEFT JOIN movements AS m2
            ON a.movement_id = m2.movement_id
        WHERE a.movement_id IS NOT NULL
          AND m2.movement_id IS NULL) AS adjustment_rows_without_matching_stock_movement
FROM movements AS m
LEFT JOIN adj_per_movement AS apm
    ON m.movement_id = apm.movement_id;
```

### G planner call 7

Session `39503ca8-e318-493f-a6d1-201563c0b444`. Result: **COMPLETED**.

```sql
WITH adj_per_movement AS (
    SELECT ia.movement_id AS movement_id,
           COUNT(*) AS adjustment_row_count,
           SUM(ia.units) AS adjustment_units_sum
    FROM app.inventory_adjustments_e1b8e1 AS ia
    WHERE ia.movement_id IS NOT NULL
    GROUP BY ia.movement_id
)
SELECT COUNT(*) AS stock_row_count,
       COUNT(DISTINCT sm.movement_id) AS stock_distinct_movement_id_count,
       SUM(CASE WHEN sm.movement_id IS NULL THEN 1 ELSE 0 END) AS stock_null_movement_id_count,
       COUNT(apm.movement_id) AS stock_movements_with_adjustment_count,
       SUM(CASE WHEN apm.adjustment_row_count > 1 THEN 1 ELSE 0 END) AS stock_movements_with_multiple_adjustment_rows,
       SUM(CASE WHEN apm.movement_id IS NULL THEN 1 ELSE 0 END) AS stock_movements_without_adjustment_count,
       COALESCE(SUM(apm.adjustment_row_count), 0) AS joined_adjustment_row_total,
       COALESCE(SUM(CASE WHEN apm.adjustment_units_sum <> sm.units THEN 1 ELSE 0 END), 0) AS movement_to_adjustment_unit_mismatch_count,
       COALESCE(SUM(CASE WHEN apm.adjustment_units_sum = sm.units THEN 1 ELSE 0 END), 0) AS movement_to_adjustment_unit_match_count,
       (SELECT COUNT(*) FROM app.inventory_adjustments_e1b8e1 AS ia2 WHERE ia2.movement_id IS NULL) AS adjustment_null_movement_id_count,
       (SELECT COUNT(*) FROM app.inventory_adjustments_e1b8e1 AS ia3 LEFT JOIN app.stock_movements_e1b8e1 AS sm2 ON sm2.movement_id = ia3.movement_id WHERE ia3.movement_id IS NOT NULL AND sm2.movement_id IS NULL) AS adjustments_without_matching_stock_movement_count
FROM app.stock_movements_e1b8e1 AS sm
LEFT JOIN adj_per_movement AS apm
    ON apm.movement_id = sm.movement_id;
```

### G planner call 8

Session `39503ca8-e318-493f-a6d1-201563c0b444`. Result: **COMPLETED**.

```sql
WITH adj_per_movement AS (
    SELECT ia.movement_id AS movement_id,
           COUNT(*) AS adjustment_row_count,
           SUM(ia.units) AS adjustment_units_sum
    FROM app.inventory_adjustments_e1b8e1 AS ia
    WHERE ia.movement_id IS NOT NULL
    GROUP BY ia.movement_id
)
SELECT TOP 50
       sm.movement_id AS movement_id,
       sm.warehouse_id AS warehouse_id,
       sm.product_id AS product_id,
       sm.event_day AS event_day,
       sm.movement_type AS movement_type,
       sm.units AS stock_units,
       apm.adjustment_row_count AS adjustment_row_count,
       apm.adjustment_units_sum AS adjustment_units_sum,
       ia.adjustment_id AS adjustment_id,
       ia.units AS adjustment_units,
       ia.reason_code AS reason_code
FROM app.stock_movements_e1b8e1 AS sm
INNER JOIN adj_per_movement AS apm
    ON sm.movement_id = apm.movement_id
INNER JOIN app.inventory_adjustments_e1b8e1 AS ia
    ON sm.movement_id = ia.movement_id
WHERE apm.adjustment_units_sum <> sm.units
ORDER BY sm.movement_id ASC,
         ia.adjustment_id ASC;
```

### G planner call 9

Session `39503ca8-e318-493f-a6d1-201563c0b444`. Result: **COMPLETED**.

```sql
WITH adj_per_movement AS (
    SELECT ia.movement_id AS movement_id,
           COUNT(*) AS adjustment_row_count,
           SUM(ia.units) AS adjustment_units_sum
    FROM app.inventory_adjustments_e1b8e1 AS ia
    WHERE ia.movement_id IS NOT NULL
    GROUP BY ia.movement_id
)
SELECT TOP 50
       sm.movement_id AS movement_id,
       sm.warehouse_id AS warehouse_id,
       sm.product_id AS product_id,
       sm.event_day AS event_day,
       sm.movement_type AS movement_type,
       sm.units AS stock_units,
       apm.adjustment_row_count AS adjustment_row_count,
       apm.adjustment_units_sum AS adjustment_units_sum,
       ia.adjustment_id AS adjustment_id,
       ia.units AS adjustment_units,
       ia.reason_code AS reason_code
FROM app.stock_movements_e1b8e1 AS sm
INNER JOIN adj_per_movement AS apm
    ON sm.movement_id = apm.movement_id
INNER JOIN app.inventory_adjustments_e1b8e1 AS ia
    ON sm.movement_id = ia.movement_id
WHERE apm.adjustment_row_count > 1
ORDER BY sm.movement_id ASC,
         ia.adjustment_id ASC;
```

### G planner call 10

Session `39503ca8-e318-493f-a6d1-201563c0b444`. Result: **FAILED: SourceReadError / SqlException / 8120**.

```sql
WITH movement_adjustment_rows AS (
    SELECT sm.movement_id AS movement_id,
           sm.warehouse_id AS warehouse_id,
           sm.product_id AS product_id,
           sm.event_day AS event_day,
           sm.movement_type AS movement_type,
           sm.units AS stock_units,
           ia.adjustment_id AS adjustment_id,
           ia.units AS adjustment_units,
           ia.reason_code AS reason_code
    FROM app.stock_movements_e1b8e1 AS sm
    INNER JOIN app.inventory_adjustments_e1b8e1 AS ia
        ON sm.movement_id = ia.movement_id
)
SELECT mar.movement_type AS movement_type,
       mar.reason_code AS reason_code,
       CASE WHEN mar.adjustment_units > 0 THEN 'POSITIVE'
            WHEN mar.adjustment_units < 0 THEN 'NEGATIVE'
            ELSE 'ZERO' END AS adjustment_sign,
       COUNT(*) AS adjustment_row_count,
       COUNT(DISTINCT mar.movement_id) AS adjusted_movement_count,
       COUNT(DISTINCT mar.product_id) AS adjusted_product_count,
       COUNT(DISTINCT mar.warehouse_id) AS adjusted_warehouse_count,
       MIN(mar.event_day) AS first_event_day,
       MAX(mar.event_day) AS last_event_day
FROM movement_adjustment_rows AS mar
GROUP BY mar.movement_type,
         mar.reason_code,
         CASE WHEN mar.adjustment_units > 0 THEN 'POSITIVE'
              WHEN mar.adjustment_units < 0 THEN 'NEGATIVE'
              ELSE 'ZERO' END
ORDER BY adjusted_movement_count DESC,
         mar.movement_type ASC,
         mar.reason_code ASC,
         adjustment_sign ASC;
```

### I planner call 6

Session `975c71b9-08e7-434b-af5c-465efa6aa6b8`. Result: **SQL object unavailable or view dependencies not validated**.

```sql
WITH adj AS (
    SELECT
        ia.reason_code AS reason_code,
        ia.movement_id AS movement_id,
        COUNT(*) AS adjustment_rows,
        SUM(ia.units) AS adjustment_units
    FROM app.inventory_adjustments_e1b8e1 AS ia
    GROUP BY
        ia.reason_code,
        ia.movement_id
),
mv AS (
    SELECT
        mv.movement_id AS movement_id,
        COUNT(*) AS activity_rows,
        SUM(mv.units) AS activity_units
    FROM dbo.movement_values AS mv
    GROUP BY
        mv.movement_id
)
SELECT TOP (20)
    adj.reason_code AS reason_code,
    SUM(adj.adjustment_rows) AS adjustment_rows,
    COUNT(*) AS adjustment_movement_groups,
    SUM(CASE WHEN adj.movement_id IS NULL THEN 1 ELSE 0 END) AS null_movement_id_groups,
    SUM(CASE WHEN mv.movement_id IS NOT NULL THEN 1 ELSE 0 END) AS groups_with_activity_match,
    SUM(CASE WHEN mv.movement_id IS NULL THEN 1 ELSE 0 END) AS groups_without_activity_match,
    SUM(adj.adjustment_units) AS adjustment_units,
    SUM(CASE WHEN mv.movement_id IS NOT NULL THEN adj.adjustment_units ELSE 0 END) AS adjustment_units_with_activity_match,
    SUM(COALESCE(mv.activity_rows, 0)) AS matched_activity_rows,
    SUM(COALESCE(mv.activity_units, 0)) AS matched_activity_units
FROM adj AS adj
LEFT JOIN mv AS mv
    ON adj.movement_id = mv.movement_id
GROUP BY
    adj.reason_code
ORDER BY
    CASE WHEN adj.reason_code = 'Q49' THEN 0 ELSE 1 END,
    adj.reason_code;
```
