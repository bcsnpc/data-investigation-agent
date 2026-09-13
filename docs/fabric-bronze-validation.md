# Initial Fabric Bronze validation

Recorded: 2026-09-12. Tracking: [FAB-001 #5](https://github.com/bcsnpc/data-investigation-agent/issues/5).

## Environment

- Workspace: `ws-investigator-dev`, ID `09cea7db-63ec-41f0-9cf0-872a6dc5c61d`.
- Capacity: Fabric Trial, Central US, confirmed by the user's workspace screenshot.
- Source: Azure SQL `ordersops` on `sql-orderops-9696025.database.windows.net`.
- SQL connection: `conn_ordersops_sql`, designated read-only `orderops_fabric` user.
- Destination: `lh_investigator_bronze`, preserving `app` schema and table names.
- Pipeline: `pl_ordersops_to_bronze`, invoking `CopyJob_1` through a Copy job activity.
- Full copy of 10 business tables. Dataset manifest is not part of this copy.

## Evidence

The user reported the run Succeeded. A screenshot of the Lakehouse SQL analytics
endpoint confirms the following counts match the original Azure SQL baseline:

| Table | Rows |
|---|---:|
| customers | 20,000 |
| products | 150 |
| orders | 100,000 |
| order_lines | 286,652 |
| payments | 105,047 |
| shipments | 95,545 |
| shipment_lines | 273,805 |
| refunds | 7,270 |
| refund_lines | 12,680 |
| audit_log | 509,550 |

The user executed the eight-check SQL query supplied in chat and confirmed every
failure count was zero:

1. Orders missing customers.
2. Order lines missing orders or products.
3. Order totals differing from line merchandise plus tax.
4. Captured payments differing from payable order totals or exceeding totals.
5. Shipment lines missing parents or linked to a different order.
6. Refunds missing a captured payment belonging to the same order.
7. Refund lines missing parents or linked to a different order.
8. Refund headers differing from summed refund-line merchandise plus tax.

The initial evidence above was user-provided; subsequent direct notebook and API verification is recorded below. Matching counts and these checks do not establish complete
row-by-row equality, key uniqueness, every chronology rule, or an atomic multi-table
snapshot. The user was instructed to pause order updates for the initial load.

## Direct verification completed

- Enterprise CLI access verified as the workspace user. API confirmed all ten tables use Overwrite.
- Pipeline run `7d169d18-02c5-468a-ad16-ad8d79156215` completed successfully,
  from `2026-09-13T04:23:55.0816538Z` to `2026-09-13T04:25:28.0966667Z`.
- Item IDs and run association are recorded in `infra/fabric/environment.json`.
- The notebook independently validated all ten counts, unique/non-null keys and
  eleven relationship/financial/status checks against pinned Bronze Delta versions.
- ORD-000002 matched SQL in every compared column across orders (1), lines (2),
  payments (1), shipments (1), shipment lines (2), refunds (1), refund lines (1)
  and audit events (7). Total 1682.64; refund 153.00.
- Source run ID and Delta version map are preserved in Silver rows and the
  validation report. The source run association is explicit for this baseline.

FAB-001 is complete for the initial ingestion milestone. Recurring snapshot
coordination and incremental loading remain future work. See [Silver evidence](fabric-silver.md).
