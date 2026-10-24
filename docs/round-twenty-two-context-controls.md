# Same-source context controls: independent arithmetic

These are application stock-movement export comparisons, not claims about a report total or a pipeline defect. No estate mutation is needed. Both groups use the same additive units column on the same source; only the explicitly selected context differs.

Before querying, the committed seed was read as literals with `fixture.seed.load()`. Its six business fields were compared against all360rows of the sealed source preimage. Each expected figure is computed independently as follows (never by running an engine-compiled query):

```python
seed = load()
table = next(t for t in seed['tables'] if t['name'] == 'stock_movements_e1b8e1')
columns = [c[0] for c in table['columns']]
rows = [dict(zip(columns, row)) for row in table['rows']]
for column, values in [('warehouse_id', [1, 2]), ('product_id', [7, 8]),
                       ('event_day', ['2026-09-14', '2026-09-15'])]:
    for value in values:
        selected = [r for r in rows if r[column] == value]
        print(column, value, len(selected), sum(r['units'] for r in selected))
```

| Context | Rows | Sum of units |
| --- | ---: | ---: |
| {'warehouse_id': 1} | 139 | 2948 |
| {'warehouse_id': 2} | 102 | 2084 |
| {'product_id': 7} | 46 | 1104 |
| {'product_id': 8} | 56 | 1258 |
| {'event_day': '2026-09-14'} | 44 | 923 |
| {'event_day': '2026-09-15'} | 38 | 772 |

Seed SHA-256: `313e90c9e25e1e1e844aac5383bfb3c01c4bd11684faeaabf48c207c623cf0c1`. Full per-row contributions are retained privately in `.local/round-twenty-two/source-scope-controls/prepared.json`; the literals are committed in the fixture notebook. Native values are not yet observed. These are prepared cases, not scored findings. Expected class: different question, with the differing warehouse/product/day context named. A grouped native read will verify both groups; its keyed output is preserved as control evidence, not backfilled into an investigation receipt.
