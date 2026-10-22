# DAX authorization diagnosis — 2026-10-21

Retry 05 failed the native semantic-to-Gold comparison because the DAX read
returned HTTP 401 `PowerBINotAuthorizedException`; Gold returned 8,765. This
is not a numeric mismatch. The subsequent demo uses the same workspace
`149f8d99-1c66-4a0a-9624-759be002bb60`, model
`3484a2bc-98c5-4cef-be5c-a6215484075e`, investigator and Execute Queries endpoint.

Two fresh bounded cloud probes used image
`sha256:0da44613f04a2f87d8bd4a094c1796beb495f203ff20a2267e4c980239d39edf`.
`round20-dax-auth-original-01` repeated the retained request, SHA-256
`4779b78bf53b5dd575fb9edcacb9495abc64c1c604948093745d3ffe2a072cbc`.
`round20-dax-auth-data-only-01` removed only the two `INFO.PROPERTIES()`
self-report projections, request SHA-256
`c3d4670c6edffa9c38bfa81688e86bffbcba1c4531067662d841cba12c0aba9e`.
Both returned HTTP 401 `PowerBINotAuthorizedException`. Removing those
unsupported functions did not fix authorization. Each used one physical
request, zero model calls, settled its reservation, and retained all twelve
record hashes plus a valid outer seal. Originals were not edited.

Both actual data-plane tokens reported only these retained claims:

| Claim | Value |
|---|---|
| aud | `https://analysis.windows.net/powerbi/api` |
| tid | `dff91047-ebc2-4657-8dbe-5af328d57780` |
| oid | `439ceb25-d200-4f02-95cf-4b1318faca62` |
| appid | `531419ef-1610-415a-b8bf-01a4b6aad751` |

No bearer token or credential was recorded. Audience and tenant match the
configured Power BI resource and model tenant; this is not the former user
cache or SQL login.

The current saved administrator control snapshot contains seven
read-only control-plane responses, all HTTP 200; the administrator did not
query estate data. Dataset users list the investigator directly with `Read`
and security group `79c75be9-d8c3-4824-91c2-fc945041a8c3`
(`dia-investigator-round19-api-readers`) with `ReadExplore` (Read + Build).
The service principal's Graph `memberOf` response contains that exact group.
The group's v1.0 `members` response was empty, but this is not evidence of
non-membership: Microsoft documents that API's service-principal omission.

The returned tenant settings `ServicePrincipalAccessPermissionAPIs` and
`DatasetExecuteQueries` are enabled, with no allow/exclude-group restriction
returned. Therefore the response shows neither setting excluding the
investigator group. Dataset metadata reports effective-identity requirements
false; the SQL item connection is `Automatic`. These fields do **not** prove
that every underlying SSO or model-security restriction is absent.

The documented Execute Queries limitations include unsupported INFO functions
and no service-principal support for datasets with RLS or SSO. The fresh
data-only failure means unsupported INFO is a separate query-compatibility
issue, not an established explanation of this 401. The precise remaining
service-side authorization cause is unestablished. No permission, tenant
setting, identity, cache or schedule was changed. Owner inspection steps are
in `owner-actions.md`; a broader grant is not justified by these receipts.

DirectLake defaults to Entra SSO, but this model's actual connection SSO
setting has not been read. Owner inspection: model Settings → Gateway and
cloud connections → mapped connection → Authentication method and “Use SSO
via Microsoft Entra ID for DirectQuery and Direct Lake queries.” Record the
connection ID and checkbox value without changing them. An `Automatic`
connection is consistent with the documented implicit SSO connection, but is
not a readback of `credentialDetails.singleSignOnType`. See
[DirectLake connection security](https://learn.microsoft.com/en-us/fabric/fundamentals/direct-lake-security-integration)
and [connection metadata schema](https://learn.microsoft.com/en-us/rest/api/fabric/core/connections/get-connection).

Private exact receipts remain under `.local/round-twenty/`: current control
responses in `current-dax-authorization-controls.json`, and both run names'
`-progress/` and `-audit.json` files. Monthly physical usage after the pair is
248/6,000 (investigation 243/4,905; scan 5/1,000; restoration 0/95). Active
request/model reservations are zero; historical counters remain untouched.

Sources: [Execute Queries and limitations](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/execute-queries-in-group),
[Graph members limitation](https://learn.microsoft.com/en-us/graph/api/group-list-members?view=graph-rest-1.0),
[tenant settings API](https://learn.microsoft.com/rest/api/fabric/admin/tenants/list-tenant-settings),
[dataset metadata](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/get-dataset-in-group),
[item connections](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/list-item-connections).


## Dated update: SSO confirmed, 2026-10-22 00:10 UTC (owner date October21)

The earlier absence of an SSO readback above is superseded by a live, read-only browser inspection as admin@skynwhy.com. On the exact demo model's Gateway and cloud connections page, Maps to is selected as **Default: Single Sign-On (Entra ID)**; Apply remains disabled. The SQL endpoint database is77c49180-2ef9-4558-837c-f50fdb1df8de, matching the retained Gold binding. No setting was changed. Exact selected-state fragment and URL: docs/runs/round-twenty-dax-sso-setting.json.

This establishes a documented blocking configuration: Execute Queries does not support service principals on SSO-enabled datasets, regardless of the tenant API setting. Correct audience, tenant and Read/Build cannot remove that restriction. The generic401 does not establish that there are no additional restrictions, but a broader grant is not a justified repair. Owner-controlled alternatives are in owner-actions.md; no new demo or DAX retry is admitted merely to repeat this known incompatibility.
