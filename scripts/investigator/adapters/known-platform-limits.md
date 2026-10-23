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


## Refresh history: identity-specific capability, owner2026-10-22 / observedUTC2026-10-23

Power BI `GET groups/{workspace}/datasets/{model}/refreshes?$top=20` returned403 for the federated investigator Viewer. Microsoft documents dataset **Write** permission for this history GET; its delegated Read.All scope does not mean workspace Viewer is sufficient. Existing `dia-scanner`, through the two exact history/schedule GET routes only, returned200 on all three estates. Investigator rights did not change. This establishes a scanner metadata capability, not refresh-history access for the Viewer investigator, and not permission to trigger a refresh.

Fixture:2successful retained refreshes (latest end2026-10-07T21:15:37.357Z). Billing and Microsoft sample: complete empty API histories, not proof no refresh ever occurred. All3native schedules disabled. Historic403 facts remain intact beside fresh successful-history observations. No rows-read/written accounting was fabricated. [Microsoft requirement](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/get-refresh-history-in-group); [schedule GET](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/get-refresh-schedule-in-group); [exact retry facts and receipts](../../../docs/runs/round-twenty-one-refresh-audit-retries.json).

Fixture Warehouse audit: the prior workerEOF RuntimeError did not retain an SQL error or child exit code. Two later reads, including the unchanged0.25vCPU/0.5Gi collector allocation, succeeded with the same principal/query and query-bound attestation;11audit rows, latest360read/360written. Original cause remains unestablished. It is not labelled a permission issue, SQL endpoint sync lag or memory failure. Future EOF diagnostics retain the safe child exit code. [Diagnosis](../../../docs/round-twenty-one-refresh-collector-diagnosis.md).
