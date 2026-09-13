# Fabric Bronze to Silver

The Fabric CLI uses the enterprise interactive identity. Credentials and tokens
stay in its local cache; the repository contains only non-secret environment IDs.
The Azure CLI's personal subscription remains separate.

## Reproducible implementation

- `infra/fabric/environment.json`: workspace, Lakehouse and initial ingestion run IDs.
- `infra/fabric/bronze_to_silver.py`: deployed PySpark notebook source.
- `scripts/deploy_silver_notebook.py`: creates or updates the notebook using its
  supported ipynb definition; does not execute it.
- `scripts/compare_bronze_order.py`: compares a local SQL trace with the notebook's
  pinned Bronze trace for ORD-000002, including all columns in eight related tables.

Deploy with `python scripts/deploy_silver_notebook.py`, then explicitly run:

```powershell
& ".local/fabric-cli-env/Scripts/fab.exe" job start "ws-investigator-dev.Workspace/nb_ordersops_bronze_to_silver.Notebook"
```

## Business rules

Silver lives in `lh_investigator_silver`. This Lakehouse uses the default table
namespace (schemas disabled); the Lakehouse itself identifies the Silver layer.
The six core entities from the plan are extended with four lifecycle/audit entities:

| Table | Grain | Rule |
|---|---|---|
| dim_customer | Customer | Preserve profile and key; add trimmed uppercase location codes |
| dim_product | Product | Preserve source attributes and prices |
| fact_order | Order | Aggregate captured payments/refunds separately before joining |
| fact_order_line | Order line | Preserve both discounts; add combined discount, payable amount and product category |
| fact_payment | Payment attempt | Captured amount is zero for failed attempts |
| fact_refund | Refund | Preserve linked payment and original amount |
| fact_shipment | Shipment | Preserve UTC shipment/delivery timestamps |
| fact_shipment_line | Shipment/order-line pair | Preserve quantity and both keys |
| fact_refund_line | Refund/order-line pair | Preserve original refunded merchandise and tax |
| fact_audit_event | Audit event | Preserve evidence, actor and event ID |

`fact_order.net_amount` means captured funds minus refunds, including tax. It is
not accounting revenue. `net_merchandise_amount` is the original discounted order
merchandise excluding tax, before returns. No discount is subtracted twice. Failed
attempts and cancelled orders do not contribute captured cash. Gold metric names
and recognition rules must explicitly distinguish cash, merchandise and tax.

Invalid keys or relationships stop publication; no records are silently dropped
or deduplicated. Source keys are retained, not replaced by arbitrary surrogate IDs.
UTC is configured for Spark. Monetary expressions use stored decimal values.

## Validation and publication

This initial-baseline notebook asserts the ten known counts and unique/non-null
keys, plus eleven relationship/financial/status checks. It pins each input table
to a Delta version, validates expected sample amounts, checks output grain and
order-line payable totals before publishing, and checks persisted counts/keys.
The initial counts deliberately fail if the source baseline changes; adapt the
ingestion contract before using this as a recurring operational refresh.

Each row carries `_silver_run_id`, `_bronze_pipeline_run_id`, `_processed_at_utc`
and the source table version map. The pipeline run association is supplied from
the recorded successful initial run; it is not automatically discovered on reruns.
Reports are stored in Silver `Files/validation/<run_id>.json` and `latest.json`.

Publication uses Delta overwrite per table. There is no atomic transaction across
all ten tables. `latest.json` becomes RUNNING before publication and READY only
after all output checks pass. Downstream work must require READY and matching row
run IDs. Do not run overlapping notebook jobs or refresh Bronze while establishing
a new cross-table snapshot. Failed publication requires investigation/rerun; it
must not be treated as a complete dataset.

This step does not build Gold, Power BI or recurring ingestion orchestration.

References: [Fabric CLI](https://learn.microsoft.com/en-us/rest/api/fabric/articles/fabric-command-line-interface),
[Notebook definitions](https://learn.microsoft.com/en-us/rest/api/fabric/articles/item-management/definitions/notebook-definition),
[Create Lakehouse](https://learn.microsoft.com/en-us/rest/api/fabric/lakehouse/items/create-lakehouse).

## Executed verification

Notebook job `ab0efd65-d6ed-45f5-bba1-ddea9eeb31cb` completed successfully on
2026-09-13 UTC, 04:42:24 to 04:45:48. Validation run
`55cdeeb3-0772-494a-8e7f-f0df4da03353` is READY. All eleven integrity failure
counts were zero, and all source and persisted destination counts/keys passed.

Silver row counts: dim_customer 20,000; dim_product 150; fact_order 100,000;
fact_order_line 286,652; fact_payment 105,047; fact_refund 7,270;
fact_shipment 95,545; fact_shipment_line 273,805; fact_refund_line 12,680;
fact_audit_event 509,550.

The independent SQL-to-Bronze ORD-000002 comparison passed across eight related
tables. Its Silver net cash is 1,529.64 = 1,682.64 captured - 153.00 refunded.
The report is in the Silver Lakehouse at
`Files/validation/55cdeeb3-0772-494a-8e7f-f0df4da03353.json`.
Local source/report captures remain under `.local/` and are not committed.

Python source compilation and existing generator regression tests passed. No
Azure SQL or Bronze business records were changed by this notebook.
