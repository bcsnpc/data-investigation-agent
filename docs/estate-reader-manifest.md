# Estate reader manifest seed

Updated 2026-10-03 America/Chicago. Recorded identities, privileges and reached
surfaces are separated from intended access. This is a manifest seed from the
linked receipts, not an exhaustive live enumeration of all historical grants.
No identity was renamed, replaced, elevated or given a workspace role in this PR.

| Reader | Authentication / identity | Recorded scope | Reaches | Evidence and limits |
| --- | --- | --- | --- | --- |
| orderops_investigator | Existing contained Azure SQL SQL_USER, DATABASE authentication | Existing approved SQL reads; #343 added SELECT on app.stock_movements_round_two_20261003 only. Before/after INSERT, UPDATE, DELETE, ALTER, CONTROL remained zero on that object | Authorized Azure SQL application source; managed Copy Job uses this same read-only source credential | [Exact grant](round-two-reader-scope-grant.md); [principal kind](round-two-workspace-monitoring.md). Other prior grants retained, not claimed absent. Not an Entra/KQL identity |
| investigator-reader@skynwhy.com | Existing dedicated Entra user; isolated credential/session | Previously approved fixture workspace Viewer and model Read + Build / ReadExplore. No new role or consent here | Semantic-model quantity reads, Fabric SQL declared layers, Copy Job REST run history | [Ingestion/history receipts](round-two-ingestion-estate.md); [surface ceiling](synthesis-rendered-spine.md). History HTTP200; REST dataset-refresh and XMLA admin metadata refused. This entry records prior scope, not a fresh tenant-wide permission audit |
| dia-reader | New dedicated Entra service principal, explicitly authorized in #346; client ddd4d3cf-9cfd-440e-ac5b-be127caa46ea, SP object 59dd402b-1510-4289-96fb-f1d34d4494c5 | No requested delegated API permissions or workspace role. Intended viewer on monitoring database 7e353019-064f-4aac-9a62-a9770d1399a9; both attempts refused, so no successful data-plane grant | Kusto token authentication established; monitoring queries remain HTTP403, no successful table read | [Creation](round-two-dia-reader-monitoring.md), [renewed grant/probes](round-two-viewer-grant-repeat.md). DPAPI credential, no plaintext in git. Not a rename of either other reader |

Metadata/publisher `admin@skynwhy.com` is separate from these three execution
readers. Its latest served Kusto roles are cluster AllDatabasesViewer / Monitor
and this database Viewer / Monitor, not database Admin. These are observed
pre-existing roles, not roles granted in this work. Publisher observations may
not replace a reader's data/attestation evidence. Database viewer is the only
approved dia-reader data-plane role; no cluster or workspace role is authorized.

Dated positive route finding, 2026-10-03: investigator-reader at the unchanged recorded scope also reaches monitoring ItemJobEventLogs (including its schema) and SemanticModelLogs, HTTP200 with empty requested histories. No new permissions. dia-reader remains present without a successful monitoring role. See [reader probes](round-two-investigator-reader-probes.md).


Dated capability evidence, 2026-10-03 America/Chicago: unchanged
investigator-reader reads pipeline activity output at existing scope (HTTP200).
InvokeCopyJob exposed its own nested rowsRead/rowsCopied, 360/360, for one
successful isolated copy; three delayed monitoring histories stayed empty. Audit
writer execution failed and its SQL-row probe obtained no row. This adds observed
routes, not permission. dia-reader remains without a successful role/grant,
orderops_investigator stays at the approved SQL scope, publisher invocation uses
an existing CopyJob managed connection. See round-two-pipeline-audit.md.
