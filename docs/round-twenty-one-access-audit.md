# Round Twenty-One permission-map audit (offline)

2026-10-22. This audits declarations and packaged bindings, not effective permission. No live calls, grants, token requests or owner substitution were performed. The 71-row map retains `pg-state_migrations`: the root operator confirmed that table exists in the current PostgreSQL catalog.

The existing investigator application has distinct service-principal objects in the two tenants. Fabric rows use object `439ceb25-d200-4f02-95cf-4b1318faca62`, tenant `dff91047-ebc2-4657-8dbe-5af328d57780`; source SQL rows use object `248525da-278c-4a6c-b5c3-cc3e7728d3ce`, tenant `aeb4d0a9-e637-4a7e-8efc-63cf0c3827df`. Both use existing application `531419ef-1610-415a-b8bf-01a4b6aad751`. This corrects the declared realm; it creates no identity or scope.

## Retained SELECT-probe defect

Both Gold and Silver SQL self-reports passed in `part0-A-sealing-01-progress.json`; their object probes failed with the sanitized class `RuntimeError`. The generated payload set `max_rows=1`, while `managed_sql_worker.execute` requires `2 <= max_rows <= 251` for its bounded result envelope. It raises `ValueError("Row bound required")` before connecting; `_gold_read` replaces nonzero child exit with `RuntimeError("SMOKE_GOLD_READ_FAILED")`. The adapter now uses envelope 2, retaining `SELECT TOP (1) 1 AS access_check FROM [schema].[table]`. A regression executes the real worker against fake ODBC and verifies all identity/database/object guards run. This does not establish that the live SELECT succeeds; a new live probe must establish that.

## Full-map binding plan

The immutable input `dia-round21-part0-A-sealing-01.zip` packages 20 probe bindings and two actual authentication declarations. Presence below means packaged only, not PASS. The family-A scope executes a smaller subset. Refresh the input under a new name/hash before retesting; do not rewrite old sealed evidence.

| Check | Declared identity | Existing A input | Next bounded proof |
|---|---|---|---|
| fixture-workspace | investigator | Packaged | Run actual identity-bound http probe; no inferred PASS |
| fixture-definitions | scanner | Absent | Bind existing scanner token and GET workspace/items definition metadata; never investigator fallback |
| fixture-bronze-sql | investigator | Packaged | Run actual identity-bound sql probe; no inferred PASS |
| fixture-bronze-select | investigator | Packaged | Run actual identity-bound sql_object probe; no inferred PASS |
| fixture-silver-sql | investigator | Packaged | Run actual identity-bound sql probe; no inferred PASS |
| fixture-silver-select | investigator | Packaged | Run actual identity-bound sql_object probe; no inferred PASS |
| fixture-gold-sql | investigator | Packaged | Run actual identity-bound sql probe; no inferred PASS |
| fixture-gold-select | investigator | Packaged | Run actual identity-bound sql_object probe; no inferred PASS |
| billing-workspace | investigator | Absent | Exact GET /v1/workspaces/{declared-workspace} as investigator |
| billing-definitions | scanner | Absent | Bind existing scanner token and GET workspace/items definition metadata; never investigator fallback |
| billing-bronze-sql | investigator | Absent | Use matching estate manifest server/database/object and actual investigator authentication; never copy fixture endpoints |
| billing-bronze-select | investigator | Absent | Use matching estate manifest server/database/object and actual investigator authentication; never copy fixture endpoints |
| billing-silver-sql | investigator | Absent | Use matching estate manifest server/database/object and actual investigator authentication; never copy fixture endpoints |
| billing-silver-select | investigator | Absent | Use matching estate manifest server/database/object and actual investigator authentication; never copy fixture endpoints |
| billing-gold-sql | investigator | Absent | Use matching estate manifest server/database/object and actual investigator authentication; never copy fixture endpoints |
| billing-gold-select | investigator | Absent | Use matching estate manifest server/database/object and actual investigator authentication; never copy fixture endpoints |
| rebuilt-workspace | investigator | Absent | Exact GET /v1/workspaces/{declared-workspace} as investigator |
| rebuilt-definitions | scanner | Absent | Bind existing scanner token and GET workspace/items definition metadata; never investigator fallback |
| rebuilt-bronze-sql | investigator | Absent | Use matching estate manifest server/database/object and actual investigator authentication; never copy fixture endpoints |
| rebuilt-bronze-select | investigator | Absent | Use matching estate manifest server/database/object and actual investigator authentication; never copy fixture endpoints |
| rebuilt-silver-sql | investigator | Absent | Use matching estate manifest server/database/object and actual investigator authentication; never copy fixture endpoints |
| rebuilt-silver-select | investigator | Absent | Use matching estate manifest server/database/object and actual investigator authentication; never copy fixture endpoints |
| rebuilt-gold-sql | investigator | Absent | Use matching estate manifest server/database/object and actual investigator authentication; never copy fixture endpoints |
| rebuilt-gold-select | investigator | Absent | Use matching estate manifest server/database/object and actual investigator authentication; never copy fixture endpoints |
| fixture-dax | investigator | Packaged | Run actual identity-bound http probe; no inferred PASS |
| fixture-fixed-connection | fabric-owner | Absent | Separate owner/control receipt only; never bind owner into investigation. Without it NOT_TESTABLE |
| fixture-connection-use | investigator | Absent | Keep NOT_TESTABLE: No separate connection grant inferred; successful model DAX probes actual model route |
| billing-dax | investigator | Absent | Constant EVALUATE ROW access_check on declared billing model; require returned value 1 |
| billing-fixed-connection | fabric-owner | Absent | Separate owner/control receipt only; never bind owner into investigation. Without it NOT_TESTABLE |
| billing-connection-use | investigator | Absent | Keep NOT_TESTABLE: No separate connection grant inferred; successful model DAX probes actual model route |
| ordersops-app-connect | investigator-source | Absent | Bind existing home-tenant federation; explicit ordersops/billingapp database and declared table, never Fabric-tenant token |
| ordersops-app-select | investigator-source | Absent | Bind existing home-tenant federation; explicit ordersops/billingapp database and declared table, never Fabric-tenant token |
| billingapp-app-connect | investigator-source | Absent | Bind existing home-tenant federation; explicit ordersops/billingapp database and declared table, never Fabric-tenant token |
| billingapp-app-select | investigator-source | Absent | Bind existing home-tenant federation; explicit ordersops/billingapp database and declared table, never Fabric-tenant token |
| tenant-service-principals-use-fabric-apis | fabric-owner | Absent | Separate owner/control receipt only; never bind owner into investigation. Without it NOT_TESTABLE |
| tenant-dataset-execute-queries-api | fabric-owner | Absent | Separate owner/control receipt only; never bind owner into investigation. Without it NOT_TESTABLE |
| tenant-enhance-admin-api-detailed-metadata | fabric-owner | Absent | Separate owner/control receipt only; never bind owner into investigation. Without it NOT_TESTABLE |
| tenant-enhance-admin-api-dax-mashup | fabric-owner | Absent | Separate owner/control receipt only; never bind owner into investigation. Without it NOT_TESTABLE |
| pg-state_schema_versions | worker | Packaged | Run actual identity-bound postgres probe; no inferred PASS |
| pg-state_migrations | worker | Absent | Bind existing table privilege query as worker; retain row |
| pg-state_accounts | worker | Packaged | Run actual identity-bound postgres probe; no inferred PASS |
| pg-state_documents | worker | Packaged | Run actual identity-bound postgres probe; no inferred PASS |
| pg-state_reservations | worker | Packaged | Run actual identity-bound postgres probe; no inferred PASS |
| pg-state_usage | worker | Packaged | Run actual identity-bound postgres probe; no inferred PASS |
| pg-state_read_batches | worker | Packaged | Run actual identity-bound postgres probe; no inferred PASS |
| pg-state_read_batch_runs | worker | Packaged | Run actual identity-bound postgres probe; no inferred PASS |
| pg-state_read_allocations | worker | Packaged | Run actual identity-bound postgres probe; no inferred PASS |
| pg-state_usage_acknowledgments | worker | Packaged | Run actual identity-bound postgres probe; no inferred PASS |
| pg-budget-update | worker | Absent | Keep NOT_TESTABLE: NO_HARMLESS_SAME_IDENTITY_READ_PROVES_THIS_CONTROL_ACTION |
| pg-monthly-accounts | owner | Absent | Keep NOT_TESTABLE: NO_HARMLESS_SAME_IDENTITY_READ_PROVES_THIS_CONTROL_ACTION |
| worker-blob-captures | worker | Absent | Bind actual worker identity, exact container List Blobs GET with maxresults=1 and x-ms-version; proves read/list only, not write |
| worker-blob-archives | worker | Absent | Bind actual worker identity, exact container List Blobs GET with maxresults=1 and x-ms-version; proves read/list only, not write |
| worker-vault | worker | Absent | Keep NOT_TESTABLE: Secret values must not enter access receipts; exercise only approved consumer and retain sanitized outcome |
| graph-scan-blob-captures | graph-scan | Absent | Bind actual worker identity, exact container List Blobs GET with maxresults=1 and x-ms-version; proves read/list only, not write |
| graph-scan-blob-archives | graph-scan | Absent | Bind actual worker identity, exact container List Blobs GET with maxresults=1 and x-ms-version; proves read/list only, not write |
| graph-scan-vault | graph-scan | Absent | Keep NOT_TESTABLE: Secret values must not enter access receipts; exercise only approved consumer and retain sanitized outcome |
| smoke-blob-captures | smoke | Absent | Bind actual worker identity, exact container List Blobs GET with maxresults=1 and x-ms-version; proves read/list only, not write |
| smoke-blob-archives | smoke | Absent | Bind actual worker identity, exact container List Blobs GET with maxresults=1 and x-ms-version; proves read/list only, not write |
| smoke-vault | smoke | Absent | Keep NOT_TESTABLE: Secret values must not enter access receipts; exercise only approved consumer and retain sanitized outcome |
| owner-secret-investigator-fixed-connection-20261021 | owner | Absent | Separate owner/control receipt only; never bind owner into investigation. Without it NOT_TESTABLE |
| owner-secret-anthropic-api-key | owner | Absent | Separate owner/control receipt only; never bind owner into investigation. Without it NOT_TESTABLE |
| owner-app-rotation | owner | Absent | Keep NOT_TESTABLE: NO_HARMLESS_SAME_IDENTITY_READ_PROVES_THIS_CONTROL_ACTION |
| owner-container-jobs | owner | Absent | Keep NOT_TESTABLE: NO_HARMLESS_SAME_IDENTITY_READ_PROVES_THIS_CONTROL_ACTION |
| legacy-sql-reader-historical | legacy-sql-reader | Absent | Keep NOT_TESTABLE: Not a live cloud route; never substitute this identity for configured investigator |
| legacy-user-reader-historical | legacy-user-reader | Absent | Keep NOT_TESTABLE: Not a live cloud route; never substitute this identity for configured investigator |
| legacy-code-reader-historical | legacy-code-reader | Absent | Keep NOT_TESTABLE: Not a live cloud route; never substitute this identity for configured investigator |
| legacy-kql-reader-historical | legacy-kql-reader | Absent | Keep NOT_TESTABLE: Not a live cloud route; never substitute this identity for configured investigator |
| billing-tester-historical | billing-tester | Absent | Keep NOT_TESTABLE: Not a live cloud route; never substitute this identity for configured investigator |
| pg-estate_node_facts | worker | Packaged | Run actual identity-bound postgres probe; no inferred PASS |
| pg-estate_fact_cursors | worker | Packaged | Run actual identity-bound postgres probe; no inferred PASS |
| pg-current-model-account | worker | Packaged | Run actual identity-bound postgres probe; no inferred PASS |

An owner/legacy row without a supported authentication binding remains NOT_TESTABLE. A known wrong principal is FAIL. Do not use the owner CLI as a hidden backend for investigator or scanner checks. Tenant-setting reads must retain returned setting values/group inclusions, not treat HTTP 200 alone as proof that the setting includes the required group. The fixed-connection check likewise must check returned singleSignOnType and binding coordinates; successful DAX proves its route, not a separately inferred connection permission.

Vault metadata is `/secrets/<name>/versions`, never the secret-value endpoint. Do not put owner credentials into worker binding inputs. Historical SQL/user/code/KQL/tester identities remain declared but unused. Current-month account proof reads the actual period row under the worker; table SELECT privilege alone is insufficient. Blob write proof uses the existing run-bound immutable recorder/readback, not a grant inferred from listing.

## Interrupted form planning is resumable, not a completed demo

The retained cloud attempt saved its form input at revision 1, then intake capture publication raised `URLError`. The retry treated every nonzero revision as complete and returned the still-NEW ticket; the cloud form worker accepted it as a finished attempt. Submission now resumes planning only for an identical retained NEW form without an adopted intake, under its unchanged catalog hash. Already adopted, HELD, CLARIFYING, INVESTIGATING and completed tickets are not replanned. Different input or catalog refuses instead of selecting against new definitions. The cloud worker gives NEW one bounded controller resume and then raises `CLOUD_FORM_PLANNING_INCOMPLETE_NEW`; it cannot call an unfinished ticket a delivered answer. Tests preserve a simulated publication failure before resuming the same ticket, stale-catalog refusal, held-state idempotency and bounded worker retry. Focused form/controller and cloud suite: 61 passed, zero new live or model calls.
