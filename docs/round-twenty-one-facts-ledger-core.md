# Round Twenty-One facts-ledger core

This component extends the existing SharedState PostgreSQL authority and existing
GraphRepository/GraphAPI. It is not a second catalog or a local live database.
SQLite remains an offline test backend only.

Migration 4 creates `estate_node_facts` (append-only observations, validated graph-node
subject membership (history survives current-projection replacement)) and `estate_fact_cursors` (incremental collector markers). The same
migration grants existing application role `id-dia-worker`:

```sql
GRANT SELECT, INSERT ON TABLE estate_node_facts TO "id-dia-worker";
GRANT SELECT, INSERT, UPDATE ON TABLE estate_fact_cursors TO "id-dia-worker";
```

Apply SharedState.migrate as the existing application schema owner, with
`search_path=dia_state,pg_catalog`. The worker does not gain schema ownership,
DDL, delete/truncate, budget-policy creation or any estate write privilege.
`facts_worker_verification.verify_worker_role` performs real reads and
transactional probe inserts/cursor updates after `SET LOCAL ROLE`, checks exact
privileges, and rolls everything back. The PostgreSQL test is explicitly opt-in
via `DIA_TEST_POSTGRES_FACTS_DSN`; a skipped test is not evidence of deployment.

Each immutable fact has subject, kind/value, observed and collected timestamps,
source, retained evidence IDs, collector/locator, explicit state and reason.
Only runtime observation, declared configuration and deterministic derivation
from observations enter this ledger. Inferred enrichment does not. Unavailable,
stale, missing and observed-negative remain different. Unreadable counts remain
null; profiles require an actual count, checksum and checksum method, never a
substitute from a different source. Historical reads exclude facts collected
later even when their observation timestamp is earlier.

GraphAPI.node_facts reads only explicit admitted subjects. freshness loads only
the admitted upstream path using SQL-filtered historical adjacency, then reads
facts for that path. GraphAPI.as_of applies the same historical cut to facts.
GraphAPI.refresh_facts rejects historical views, checks the gateway's admitted
IDs, and tops up only missing/stale/unavailable facts for those IDs.

## Collector adapter contract

`IncrementalFactCollector(ledger, adapter, budget=..., key_tables=...)` runs no
models. Platform API interpretation stays in the adapter. The adapter must make
all physical reads through the existing read-only gateway and shared SCAN
account. The injected `budget.claim(operation, subjects)` admits bounded LIST,
FETCH and PROFILE operations before the adapter is called; the adapter/gateway
must still reserve and charge each real physical request, including pagination.
Exhaustion prevents calls and explicitly reports stale coverage, never a fresh
negative. The list interval is configurable: a 30-minute wake schedule does not
promise every item receives a cloud read on every wake.

- `identity`: stable collector name.
- `list_changes(subjects)`: `{items, complete, evidence_ids}` where each item is
  `{subject, marker, load_marker}`. No objects outside the explicit path.
- `fetch(subject, now=...)`: normalized fact objects, including unavailable
  observations with evidence/reason for unsupported routes. Run facts use
  `run_id`, status, start/end, error and optional rows_read/rows_written. An empty
  list is refused rather than read as proof of no runs.
- `profile(subject, load_marker=..., now=...)`: TABLE_PROFILE with `load_marker`,
  actual `row_count`, `checksum`, and `checksum_method`. Only configured key
  tables are profiled, once per detected load. A failed profile is retryable.

List calls with unchanged markers avoid per-item fan-out. A subject missing from
an incomplete (or complete) list is a coverage gap, not proof of a successful
empty runtime history. Subject markers advance only after retained observations
are written and none is unavailable. Listing errors and guardrail exceptions
propagate; adapters must retain the actual failed receipt rather than fabricate
one. Median recent successful durations and overdue status derive only from
observed runs and a declared next-due schedule, with evidence IDs retained.

`FactLedger.coverage(estate, nodes_by_id, expected_kinds_by_node_type, now=...)`
reports each requested node/kind's state, freshness and reason; it never treats a
capability implemented offline as live coverage. Live adapters, their grants,
actual worker-role test results, schedule/cost admission and per-estate collected
coverage must be recorded separately by the operator.
