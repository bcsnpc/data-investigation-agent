# Explicit isolated administrator-profile grant: refused, stopped

2026-10-03 America/Chicago / 2026-10-04 UTC.

## Human identity-scope decision

The user explicitly directed the existing `.local/azure-fabric-sql` profile to
perform only the permission listings and the already-prepared viewer grant.
No workspace role, Eventhouse administration, other item or reader elevation
was authorized. If this profile was refused, the instruction was to stop,
not escalate or try a different scope. This is a recorded identity-scope-change
attempt, not a successful scope change.

## Profile and identity actually used

Azure CLI token acquisition set `AZURE_CONFIG_DIR` to the absolute
`.local/azure-fabric-sql` directory and requested the Kusto audience.
Validated token identity: `admin@skynwhy.com`, object `23de217f-6e14-49cf-9acd-47dcd83cb82f`,
tenant `dff91047-ebc2-4657-8dbe-5af328d57780`, audience `https://api.kusto.windows.net`.
No profile fallback, new identity or credential change.
The earlier #349 permission requests also used this same isolated profile;
this is a newly authorized recorded attempt, not a switch from a different
publisher account. A profile's administrator label does not establish
Database Admin permission on this particular monitoring database.

Target database: `7e353019-064f-4aac-9a62-a9770d1399a9`.
Endpoint: `https://trd-0795s2y5q96wchvu48.z8.kusto.fabric.microsoft.com`.
Both physical requests POST `/v1/rest/mgmt`; database and command sent unchanged.

## Before

```kusto
.show database ['investigator-fixture-83139e71cbdf6a50_Monitoring_item_investigator-fixture-83139e71cbdf6a50_Database'] principals
```

HTTP 200. Filtering the served principal rows for dia-reader's exact app/object
IDs yields this permission listing:

```json
[]
```

Zero dia-reader entries. Full served rows remain in the sealed local receipt.

## Prepared grant, unchanged

```kusto
.add database ['investigator-fixture-83139e71cbdf6a50_Monitoring_item_investigator-fixture-83139e71cbdf6a50_Database'] viewers ('aadapp=ddd4d3cf-9cfd-440e-ac5b-be127caa46ea;dff91047-ebc2-4657-8dbe-5af328d57780') 'Explicit user approval: fixture monitoring viewer only 2026-10-03'
```

HTTP 403. Exact response:

```text
Forbidden: Caller is not authorized to perform this action
Error details:
ClientRequestId='unspecified;5436c608-2ceb-4fd6-875c-71c4c8b2a5a7', ActivityId='baf4c9c2-cb0c-4e9c-8872-eb7af6793b3b', Timestamp='2026-10-04T01:12:59.1919416Z'.
```

## After and subsequent work

**Not requested.** The user's step 2 requires stopping immediately on a refusal.
There is no new after listing and no claim that an after check was performed.
No successful permission change occurred; the command returned refusal.
No different actor, API, scope or role was tried after that refusal.
No reader probe, schema inspection, additional Copy Job load, binding integration
or authored scenario was performed. Earlier refused/empty evidence stays unchanged.
No refresh-history capability or accounting availability is established by this
attempt. B1 and the four scenarios remain pending.

## Ledger and usage

Two physical requests: one before listing and one refused mutation. No diagnostic
or model calls. Part B **62 -> 64 / 120**; rolling observed **217 -> 219 / 300**.
No cap, credit, refund or reset. The ledger appends the blocked attempt with
human approval in the sealed receipt and this delivery record. Original ledger
rows remain byte-for-byte unchanged. No engine/config change; prior freezes
remain invalid.

Local receipt `.local/round-two-20261003/monitoring-admin-profile-grant.json`:
SHA-256 `7f5a3cb704e7d17ddca9174d29522694b3f4d1c4217feddf5176fa869b64d672`.

The [reader manifest](estate-reader-manifest.md) remains unchanged: dia-reader
has no successful monitoring grant. The prior [effective-role finding](round-two-viewer-grant-repeat.md)
records Viewer/Monitor for the same publisher on this database, not Database Admin.
