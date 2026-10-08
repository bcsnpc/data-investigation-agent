# Estate reader manifest seed

Dated code-only identity addition, 2026-10-05: the human authorized
`investigator-code-reader` (app2dd2f5c3-f7af-4804-b79e-6019e63efa60,
SPdc89155f-9a9a-4daa-9c20-7eff55818ccd). Before assignment absent; after
Contributor on workspace149f8d99-1c66-4a0a-9624-759be002bb60 only. Both fixture
installations declare that workspace. It reads item definitions only through the
explicit API code-source path, never diagnostic quantities or investigations.
DPAPI credential local only. Existing execution readers unchanged. This is a
separate identity, not a rename. See [exact decision and grant](round-six-code-sources.md).

Dated single-object addition, 2026-10-04 UTC: explicit human decision granted
investigator-reader@skynwhy.com SELECT on dbo.load_run_audit in isolated Warehouse
round_three_ops_audit_20261004 (bea673e0-a206-461e-9b2f-1b3b827e80de). Before
principal/explicit permissions empty; after EXTERNAL_USER, SELECT/GRANT. Applied
by existing admin profile; query execution stayed on reader. No OneLake,
workspace, write, admin or other object grant. Warehouse row matches own copy
360/360 counters/times. Other readers unchanged. See [record](audit-row-validation.md).

Updated 2026-10-03 America/Chicago. Recorded identities, privileges and reached
surfaces are separated from intended access. This is a manifest seed from the
linked receipts, not an exhaustive live enumeration of all historical grants.
No identity was renamed, replaced, elevated or given a workspace role in this PR.

| Reader | Authentication / identity | Recorded scope | Reaches | Evidence and limits |
| --- | --- | --- | --- | --- |
| investigator-code-reader | Separate Entra service principal, human-authorized Round Six B; app2dd2f5c3-f7af-4804-b79e-6019e63efa60 | Contributor on fixture workspace149f8d99-1c66-4a0a-9624-759be002bb60 only; no Graph application permissions | Recorded definition fetch for notebook7ccafe59-0460-4c8a-a691-bfdfa75a2b25, then local/Git exports | [Before/after and hashes](round-six-code-sources.md). Write-scoped platform API limitation; not an investigation execution identity |
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


Dated identity scope change, 2026-10-04 UTC, explicit human decision: existing
`investigator-reader@skynwhy.com` gained **Read + Build / ReadExplore on semantic
model `0c89889c-6fe6-49ab-91e9-4b00a51070e6` only** (`Application load fixture
20261003`). The existing publisher applied the exact prepared request. Before
Read; after ReadExplore; no write, workspace role or other item. This permits
reader quantity execution on this isolated presentation layer; execution itself
is still untested here. SQL `orderops_investigator` and roleless `dia-reader`
are unchanged. [Decision, exact request and listings](round-two-application-presentation.md#dated-human-approved-identity-scope-change).


Dated installation supersession, 2026-10-04 UTC: the identity table remains historical evidence. Active installation declarations now live in the single [estate manifest](estate-installation-manifest.md); they do not grant access or retrospectively change scope. The fixture installation still requires current discovery re-approval before live use.

Dated Round Ten explicit scope decision, 2026-10-07 America/Chicago: new rehearsal workspace `d028fa2b-0d1b-4dd8-b423-37dd161cd5d0` only. Existing investigator-reader (`8a582d2a-ecb4-4320-bf72-75a529a0d382`) now holds Viewer there; existing investigator-code-reader (`dc89155f-9a9a-4daa-9c20-7eff55818ccd`) holds Contributor there for code-definition access. Neither had a role before, both roles match the source fixture and were verified afterward. No new identity or audience, no existing-workspace change, no new model Build or SQL-table grant yet. See [exact grants](round-ten-rebuild-rehearsal.md).
