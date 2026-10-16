# Round Nineteen B metadata-reader audit

The retained Round Nineteen scan contains **36 owner failures across eight kinds**, not 36 different kinds. These are historical observations; this offline audit makes no new estate reads. All original failures remain unchanged.

| Kind | Owners | Reader / remaining gap |
| --- | ---: | --- |
| Lakehouse | 14 | Lakehouse metadata/table listing plus separately attested column catalog |
| Warehouse | 3 | existing bounded SQL object/schema reader requires explicit object and reader route configuration |
| SQLEndpoint | 14 | existing bounded SQL object/schema reader requires explicit object and reader route configuration |
| Monitoring | 1 | unsupported; retain UNKNOWN until an explicit structural reference requires this kind |
| Eventhouse | 1 | unsupported; retain UNKNOWN until an explicit structural reference requires this kind |
| KQLDatabase | 1 | unsupported; retain UNKNOWN until an explicit structural reference requires this kind |
| Reflex | 1 | unsupported; retain UNKNOWN until an explicit structural reference requires this kind |
| OperationsAgent | 1 | unsupported; retain UNKNOWN until an explicit structural reference requires this kind |

The 31 data-container owners are lower-data candidates, not 31 demonstrated complete visual paths. The retained graph stops at unresolved DAX before those paths can be established. Five monitoring/automation owners have no established structural visual-to-data reference. An item GET is not a table/column/definition reader. Replacing an owner with just its item metadata would erase retained children and overstate collection success; this implementation does not do that.

The exact owner IDs, names, kinds and errors are in [the audit JSON](round-nineteen-b-unsupported-kinds.json).

## Dated REST correction ? 2026-10-13

The older ExecuteQueries endpoint excludes INFO. Microsoft now documents a different [ExecuteDaxQueries API](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/execute-dax-queries) that supports DAX and INFO and returns Apache Arrow IPC streams. The new adapter uses only that explicit route, fixed INFO queries, bounded timeout/rows/body, and the existing gateway and request meter. It retains the exact raw response privately before parsing. HTTP 200 error streams, unsupported modern infrastructure, and permission failures remain failures. No live compatibility is claimed by these tests.

[INFO.CALCDEPENDENCY](https://learn.microsoft.com/en-us/dax/info-calcdependency-function-dax) still requires model Write permission. The dedicated approved scanner is the intended principal; the investigation reader does not gain scope. CALCDEPENDENCY edges are DECLARED engine evidence, never VERIFIED solely because the engine reported a dependency. Exact model definition, table and member identities must resolve; incomplete rows and empty results retain UNKNOWN.

[Lakehouse table listing](https://learn.microsoft.com/en-us/rest/api/fabric/lakehouse/tables/list-tables) is a table inventory, not a column-schema or transformation-definition guarantee. SQL object/schema collection remains separately attested and bounded to declared objects.
