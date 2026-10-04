# Microsoft adapter: load-audit synchronization

2026-10-04 UTC: `LAKEHOUSE_SQL_AUDIT_SYNC_LAG`. A committed audit row was absent
from the lakehouse SQL endpoint at least 6m20.259836s after its Delta commit.
Later SQL served it; exact convergence time unobserved. This is not a usual-lag
estimate. Sealed administrator Delta receipts `audit-delta-admin-rows.json`,
original B3 gap reader receipt at 05:33:47.963836 UTC and later
`audit-sql-current.json` establish it. Hashes/counts remain in the ledger.
[Full evidence](../../../docs/audit-row-validation.md).

Estate readiness: audit tables live in a Warehouse, never behind a lakehouse
SQL endpoint. The producer refuses lakehouse SQL audit sources, rather than
inferring last-run currency from a potentially stale view. Original lakehouse
audit table unchanged. Warehouse quantities still carry SNAPSHOT_UNVERIFIED;
this route does not establish query-bound snapshot identity.
