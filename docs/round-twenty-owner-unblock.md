# Owner-approved demo prerequisites — 2026-10-21

Owner approval was recorded before changes in CLAUDE.md section 8. Execution
crossed UTC midnight on October 22. This is a control-plane record, not an
investigation or a new successful demo.

## PostgreSQL: applied and verified

Only `OwnerCurrentIp` on `pg-dia-d5dd7d65` was replaced: start=end
`209.240.14.44` before, start=end `184.105.12.85` after. The latter was the
laptop's outward IPv4 at execution. Existing `AllowAzureServices` and all other
settings were unchanged. Exact approved command:

```powershell
az postgres flexible-server firewall-rule update --resource-group rg-dia-platform --server-name pg-dia-d5dd7d65 --name OwnerCurrentIp --start-ip-address 184.105.12.85 --end-ip-address 184.105.12.85 --output none --only-show-errors
```

As the existing owner, using an Entra token in memory over verified TLS,
provisioned `model-microdollars:2026-10` and `model-microdollars:2026-11`.
Before: neither existed. After: each has unit MICRODOLLARS, ceiling 40,000,000
($40), protected 0, opening 0 and violated=false. Historical account and balances
were unchanged. Worker permissions before and after were identical: SELECT and
column-level UPDATE(violated); no INSERT, DELETE or TRUNCATE. No role was widened.

Before/after receipts are retained locally as
`.local/round-twenty/pg-firewall-approved-unblock-receipt.json` and
`.local/round-twenty/approved-oct-nov-budget-provision.json`. Neither contains a
credential. Fresh readback at 2026-10-22T00:26:37Z: physical 286/6000
(INVESTIGATION245, SCAN41, RESTORATION0), restoration95 remaining; October and
November model accounts each charged $0/$40. These are platform controls, not
estate diagnostic reads or model calls.

## Power BI: approved, not applied

The fixture model still maps to **Default: Single Sign-On (Entra ID)**. The
admin browser's Create a connection route and Manage connections route load an
empty `gatewayAdminPortalFrame`. A standalone connection portal displays:

> Unable to authenticate for GRAPH service. Please contact Microsoft support if this issue persists.

Reloading the embedded route did not resolve it. This does not establish a
missing Graph permission. No new role, credential, connection or model binding
was created. The investigator service principal is federated-only, with no
existing client secret. The documented Fabric create API requires a secret for
ServicePrincipal authentication; its public credential union does not provide
the existing user's OAuth sign-in flow. The legacy Create Datasource API
explicitly excludes cloud gateways and OAuth2. No undocumented credential body
or broader identity was substituted.

Sources: [Fabric Create Connection](https://learn.microsoft.com/en-us/rest/api/fabric/core/connections/create-connection),
[Power BI Create Datasource limitations](https://learn.microsoft.com/en-us/rest/api/power-bi/gateways/create-datasource),
[Execute Queries service-principal restrictions](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/execute-queries-in-group).

### Exact owner click steps

1. In the admin's Power BI browser open [the fixture model settings](https://app.powerbi.com/groups/149f8d99-1c66-4a0a-9624-759be002bb60/settings/datasets/3484a2bc-98c5-4cef-be5c-a6215484075e?experience=power-bi).
2. Expand **Gateway and cloud connections**, then under **Cloud connections**,
   open **Maps to** and choose **Create a connection**. If the embedded portal
   is blank in this browser too, the portal authentication problem must be
   resolved; it is not permission to grant Graph or workspace access.
3. Retain SQL server
   `i4iptx6c5nlundn6llzsrvlxqa-tggz6fdgdqfevfreown6aav3ma.datawarehouse.fabric.microsoft.com`
   only if it matches the existing source shown in settings. **Use the existing
   server field verbatim rather than retyping this note.** Database must remain
   `77c49180-2ef9-4558-837c-f50fdb1df8de`.
4. Name the connection `dia-fixture-readonly-fixed`. Choose Organizational
   account/OAuth2 and sign in as existing read-only
   `investigator-reader@skynwhy.com` for the **data-source credential**, not the
   admin. Leave encryption on. Turn off **Use SSO via Microsoft Entra ID for
   DirectQuery and Direct Lake queries** if offered. Do not enable sharing to
   additional users, add permissions, or create a service-principal secret.
5. Create the connection, return to the model's **Maps to**, select that named
   connection and **Apply**. Record the connection ID and visible authentication
   identity, without credentials. Leave RLS unchanged.
6. If billing MRR also uses default SSO, repeat for [billing model settings](https://app.powerbi.com/groups/7d67bb36-04f6-4182-95aa-da5d515248fa/settings/datasets/c6c1091c-3bde-46ca-94fc-58f62d1e4188?experience=power-bi),
   using its own existing server/database fields unchanged and connection name
   `dia-billing-readonly-fixed`.

The fixture server is to be copied from the UI; the retained authoritative
before-setting is `docs/runs/round-twenty-dax-sso-setting.json`.

## Reruns and merge status

No new demo, value check or replay was admitted after this approval: the
fixed-identity prerequisite remains unresolved. Original failed runs and tapes
are unchanged. Next order is family A demo, filtered-fixture value check,
billing MRR value check, then same-image replay, each reported separately.
Full engine regression remains 4,747 passed /47 skipped /1,622 subtests on
2c3b8e2. Draft #427 remains unmerged and `v0.20` is not created.
