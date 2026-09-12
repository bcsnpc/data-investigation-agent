# Cross-System Data Investigator

The project specification is in [cross_system_data_investigator_poc.md](cross_system_data_investigator_poc.md).

## Current implementation

- Azure SQL application schema and lifecycle extensions.
- Deterministic retail generator for 100,000 connected orders.
- Local relationship validation and tests that introduce invalid records.
- Transactional SQL bulk loader, reconciliation queries and a dataset manifest.
- Restricted app, Fabric and investigator SQL users with live permission tests.

See [synthetic data rules and loading instructions](docs/synthetic-data.md).
See [runtime identities](docs/runtime-identities.md) for credentials and permission boundaries.

Track completed work and remaining phases in [project progress](docs/progress.md)
and [GitHub issues](https://github.com/bcsnpc/data-investigation-agent/issues).
See [baseline verification](docs/baseline-validation.md) for live SQL evidence.
CI runs generator tests and PowerShell syntax checks without cloud credentials.

## Connection

Development server: `sql-orderops-9696025.database.windows.net`.
Database: `ordersops`. Credentials are never stored in source files.

On Windows, save the SQL credential for your current Windows user:

```powershell
powershell -ExecutionPolicy Bypass -File infra/scripts/Initialize-AzureSql.ps1 -SaveCredentialOnly
```

Create the base schema if using a fresh database:

```powershell
powershell -ExecutionPolicy Bypass -File infra/scripts/Initialize-AzureSql.ps1
```

The loader applies the lifecycle schema extension automatically. Scripts target
this development database explicitly. Configure another target in the connection
code before using another environment.

## Verify the loaded baseline

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File infra/scripts/Get-BaselineReport.ps1
```

Generator tests need Python 3.10+ and only its standard library. Loader scripts
use Windows PowerShell 5.1 and .NET System.Data.SqlClient. No Fabric ingestion,
business web application, or AI investigation engine is implemented yet.
