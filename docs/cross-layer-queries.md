# Read-only cross-layer metric queries

The OrderOps adapter queries Azure SQL, Bronze, Silver, Gold and the deployed semantic model. It supports **Order Count** and **Net Cash**, a required currency and an optional exact order ID. It does not accept arbitrary SQL/DAX, product/date filters or report slicers.

## Business contracts

Source and Bronze calculate captured payments minus refunds per order, including paid cancellations. Failed payments contribute nothing. Silver reads `fact_order.net_amount`; Gold reads the allocated `order_line_summary.net_cash_amount`; Power BI evaluates `[Net Cash]`. Net Cash includes tax and is distinct from Net Sales.

Source/Bronze/Silver count order rows. Gold counts distinct orders in line data and Power BI evaluates `[Order Count]`. Differences caused by missing or duplicated rows remain observable. The verified source schema enforces unique order IDs. Both metrics define an empty filtered result as zero. Monetary results are exact decimal strings with four fractional digits; DAX formats results inside the service to avoid binary JSON floats.

Templates are specific to the versioned OrderOps contract. Connection/auth configuration is reused, but a different schema or metric requires a reviewed adapter, not an inferred query. The representative path follows orders through the layers; source net cash also queries payments and refunds, whose references are retained in the executed SQL. This is not exhaustive branch-by-branch root-cause diagnosis.

## Running

```powershell
python scripts/cross_layer_investigation.py --lineage-run b5db8886-61e4-49cc-92c5-4f682ab7268f --currency USD --order-id ORD-000002
```

Omit `--order-id` for the currency-wide total. Optional `--config` and `--estate` select the existing metadata and Fabric environment configurations. The workspace must agree across configurations. Planned assets and upstream paths must exist in the selected lineage build before querying.

Azure SQL uses the restricted investigator DPAPI credential. Fabric endpoints are discovered through authenticated lakehouse API calls and use Entra SQL tokens; Power BI uses the signed-in enterprise account. Queries never trigger refreshes or modify tables/definitions. SQL filter values are bound parameters; DAX filter values pass strict allowlists. Each SQL command has a 90-second query timeout and returns one aggregate row; this bounds output and execution time, not the number of rows scanned. The worker accepts only the fixed operations.

If the SQL audience needs interactive authentication, run this explicitly in PowerShell and sign in with the configured enterprise account:

```powershell
& 'D:\data_investigation_agent\.local\fabric-cli-env\Scripts\python.exe' 'D:\data_investigation_agent\scripts\connect_fabric_sql.py'
```

The helper uses Azure CLI browser authentication with the Windows broker disabled and verifies the current development operator `admin@skynwhy.com` and configured tenant. SQL authentication uses the isolated `.local/azure-fabric-sql` profile; the personal Azure CLI profile and Fabric REST/Power BI sessions remain unchanged. The account constant is specific to this development adapter; reusable hosted identity configuration remains follow-up work. Tokens remain in the Windows-protected Azure CLI cache or process memory; the SQL token is passed to the child process over stdin, never in command arguments, logs or an exported file. Background queries never initiate interactive sign-in. Hosted identity provisioning remains separate work.

## Boundary interpretation and persistence

Each result is stored in the existing `investigation_runs` SQLite table with query text/hash, adapter hashes, filter context, acquisition times, endpoint evidence and the selected lineage build. Failed reads retain sanitized error type/stage/code; credentials and raw service error bodies are excluded. A failed layer does not discard successful neighboring observations.

Two distinct results are exposed:

- `observed_value`: numerical MATCH/MISMATCH when business context agrees, or UNKNOWN when it does not. This alone cannot prove a common snapshot.
- `status`: the stricter existing comparison result, including NOT_COMPARABLE for missing/different source snapshots and UNAVAILABLE for failed reads.

The live adapters deliberately set `source_snapshot` to null. Sequential read times, matching values, a refresh ID and the static lineage build do not prove a common upstream data version. Propagating verified extraction/dependency versions remains necessary for snapshot-comparable diagnosis.

`first_observed_difference` identifies the earliest numerical difference only when every earlier boundary has an observed match. `first_verified_divergence` additionally requires matching comparison context and snapshots, no relevant lineage gaps, and verified matches at every earlier boundary. Missing earlier evidence prevents either claim as appropriate. Even a verified comparable difference remains classified UNRESOLVED until independent business-rule and causal evidence supports a classification. No bug or notification is created.

## Verification status

Twelve offline tests cover ordered divergence, unknown snapshots, unavailable earlier layers, incompatible filters, lineage gaps, reversed paths, injection rejection, partial DAX errors, query provenance and persistence of partial acquisition. The actual source SQL template is tested against paid cancellation, split refunds, failed payments, mixed currencies and an empty order scope using the existing DuckDB test dependency.

Live Azure SQL and Power BI reads agree on 100,000 USD orders and net cash `64892824.4900`. Sample `ORD-000002` returns one order and net cash `1529.6400`. Endpoint comparison evidence is persisted in run `1cae5e66-3293-41b4-9491-b59ccc3de7cb`; strict comparison correctly remains NOT_COMPARABLE because common snapshot evidence is absent.

Bronze/Silver/Gold endpoint queries are implemented but live verification is pending the additional Fabric SQL audience sign-in. The existing REST and Power BI sessions work; silent SQL-token acquisition returned an authentication broker error. No complete five-layer validation or first broken boundary is claimed yet.

Microsoft references: [SQL endpoint connectivity and Entra authentication](https://learn.microsoft.com/en-us/fabric/data-warehouse/how-to-connect), [Power BI Execute Queries](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/execute-queries-in-group).

Authentication troubleshooting: the initial Windows broker flow failed while showing a different account (`cbusa2025@skynwhy.com`). The SQL helper now uses browser sign-in with an explicit operator hint; REST/Power BI authentication is unchanged. Browser sign-in is still pending user completion. See [Microsoft MSAL account selection and broker documentation](https://learn.microsoft.com/en-us/entra/msal/python/advanced/wam).

Confirmed authentication cause: browser login returned AADSTS65002 because the Fabric CLI first-party application is not preauthorized for the SQL resource. The displayed account was not sufficient evidence of the cause. The SQL adapter now uses Azure CLI via its supported login/get-access-token commands and an isolated `AZURE_CONFIG_DIR`. No app registration or tenant permission change is made. See [Azure CLI configuration](https://learn.microsoft.com/en-us/cli/azure/azure-cli-configuration). Live sign-in remains pending.
