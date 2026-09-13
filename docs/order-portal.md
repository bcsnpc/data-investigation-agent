# Order Operations Portal

Tracking: APP-001 (#4). Browsing is deployed (PR #8). Ship/deliver/return actions
and transactional audit writing are implemented and verified on the feature branch;
the action release is not deployed yet.

Live development URL: https://orderops-portal-9696025.azurewebsites.net

Verified on 2026-09-12: Central US, F1 Free plan, HTTPS-only. Public API tests
passed against the real SQL baseline. The operator password is available through
the local clipboard helper below; it is not the SQL admin password.

## Architecture

Browser -> React + TypeScript (Vite build) -> Express API -> Azure SQL `ordersops`.
Express serves the static frontend and API from one origin and one Node process.
The API uses the designated `orderops_app` contained SQL user, never the setup
administrator. SQL credentials stay in server environment variables.

The source plan allows React + Vite. Node/Express was chosen for a single compact
App Service deployment; a Python investigation engine can be added separately.
Northline is fictional demo branding, not a real retailer.

## Implemented

- Password-protected development workspace with an eight-hour signed session.
- Overview counts and paginated orders, 25 per page.
- Literal order/customer search, status filter and inclusive date filters.
- Order detail: customer, lines, promotions/coupons, tax, payments, shipments,
  refund lines and related order/payment/shipment/refund audit events.
- UTC date display and USD formatting; order total is not labeled revenue.
- Loading/error/empty states, preserved filters when returning from details,
  and responsive desktop/mobile layouts.
- Bound SQL parameters, validated input, pooled connections and query timeouts.
- Protected API endpoints, HttpOnly/SameSite cookies, secure cookies in deployed
  production mode, login rate limiting and security headers.

This is single-operator demo authentication, not enterprise SSO. Session signing
is stateless: logout clears the browser cookie; rotating SESSION_SECRET revokes
all issued sessions. Writes use a server-assigned shared `portal-operator` identity;
this does not identify individual people. JSON plus a required custom header,
Fetch Metadata checks and no CORS support reject cross-site browser writes.

## Local operation

Requirements: Node 24, npm, Windows PowerShell for encrypted local credentials.

```powershell
cd apps/order-portal
npm ci
npm run build
npm test
cd ../..
powershell -ExecutionPolicy Bypass -File infra/scripts/Start-OrderPortal.ps1
```

Open http://localhost:3000. In another PowerShell terminal, run:

```powershell
powershell -ExecutionPolicy Bypass -File infra/scripts/Copy-PortalPassword.ps1
```

Paste the copied password in the portal. Do not paste it into chat or source code.
The portal password is distinct from every SQL password. Local portal/session
credentials are encrypted under `.local/` and excluded from Git.

## Tests

`npm test` runs API authentication, invalid filters, missing-order, forged-cookie,
secure-cookie and logout tests against a stub database. `npm run build` checks
TypeScript and builds the frontend. These do not require Azure credentials.

Live development smoke test (reads only):

```powershell
powershell -ExecutionPolicy Bypass -File infra/scripts/Test-OrderPortal.ps1
```

The live test checks anonymous rejection, session login, the 100k count,
pagination, search, status/date filtering, and ORD-000002's independently verified
$1,682.64 total and $153 refund. Agent-browser verifies desktop/mobile rendering,
search-to-detail navigation and browser errors. Cloud verification uses the same
test with `-BaseUrl https://<app-host>`.

## Azure deployment

Target: personal trial subscription, resource group `rg-investigator-dev`, Linux
App Service F1 Free plan, Node 24 LTS. The script refuses to reuse a paid plan.
If regional quota/capacity prevents F1 provisioning, do not silently upgrade.
Free hosting has resource limits and is appropriate for development, not an SLA.

```powershell
powershell -ExecutionPolicy Bypass -File infra/scripts/Deploy-OrderPortal.ps1
```

Azure CLI must be installed at `.local/azure-cli-env/` and signed into the personal
subscription. The script provisions the plan/app, enables HTTPS-only and TLS 1.2,
disables FTP, securely sends settings through the ARM API, and deploys an explicit
ZIP allowlist. The ZIP contains frontend build output, server runtime files and
package manifests. It excludes credentials, datasets and source-only tests.

Oryx installs dependencies on Azure; the frontend is prebuilt locally. The ZIP's
package manifest keeps only the start script so Azure does not try to rebuild
absent frontend source. Runtime settings: SQL_SERVER, SQL_DATABASE, SQL_USER,
SQL_PASSWORD, PORTAL_PASSWORD, SESSION_SECRET and NODE_ENV=production.
Settings are stored in App Service configuration; Key Vault integration is later
work. The existing SQL server permits Azure service network access; SQL
authentication still controls database access. A future network-hardening task
can scope outbound IP rules or private connectivity.

`/healthz` is a liveness check, not proof of SQL connectivity. Verify real API
reads after deployment. Re-deploy a previously verified ZIP to roll back code;
no database schema/data changes are part of this portal deployment.

References: [Node App Service quickstart](https://learn.microsoft.com/en-us/azure/app-service/quickstart-nodejs),
[ZIP deployment](https://learn.microsoft.com/en-us/azure/app-service/deploy-zip),
[application settings API](https://learn.microsoft.com/en-us/rest/api/appservice/web-apps/update-application-settings?view=rest-appservice-2024-11-01).

## Controlled order actions (awaiting release)

- Ship a PAID order: requires one captured payment matching its total, reconciled
  lines, and no existing shipments/refunds. Creates one shipment with every order
  line and changes status to SHIPPED. Carrier and unique tracking number required.
- Deliver a SHIPPED order: verifies shipment coverage and chronology, records UTC
  delivery and changes status to DELIVERED.
- Return selected lines on a DELIVERED/PARTIALLY_RETURNED order: returns all units
  of each selected line. Uses stored `line_total` (after both discounts) plus
  original `tax_amount`, calculated as SQL decimal, never client amounts. Creates
  refund/header lines tied to the captured payment; status becomes PARTIALLY_RETURNED
  or RETURNED. Previously returned or unrelated lines and over-refunds are rejected.
- These are synthetic business records: no carrier or payment gateway is contacted.
  Split shipments, partial line quantities, cancellations and payment capture are
  outside this release. Existing baseline lifecycle conventions are preserved.

`POST /api/orders/:id/actions` accepts action, UUID-v4 requestId, expectedUpdatedAt,
reason, and carrier/trackingNumber (ship) or lineIds (return). Authentication and
input validation precede SQL. Client actor, amounts and timestamps cannot override
server-owned values. Reasons are required for every action.

A SQL transaction holds an update lock on the order through business writes and
three audit inserts (status before/after, related record before/after including
new line records, and action reason/request payload). A failure rolls back all
changes. Each request ID is an audit primary key: an identical retry returns
success without repeating writes, while changed payloads conflict. `updated_at`
provides an optimistic version; locks serialize concurrent portal actions. A
five-second lock wait returns a conflict for refresh/retry. This protocol governs
portal actions; direct admin SQL writers must follow equivalent invariants.
Detail reads hold the order lock while fetching related tables so portal writes
cannot commit halfway through a detail response.

The browser refreshes detail, list and counts after success. Retrying unchanged
form values keeps the request ID if a response is lost. Refreshing the browser
loses that ID, but lifecycle/version checks still reject an already-applied ship
or delivery and previously returned lines.

### Write verification

```powershell
powershell -ExecutionPolicy Bypass -File infra/scripts/Test-OrderActions.ps1
```

Uses the restricted app credential and rolls back every transaction. Verified:
authenticated API -> Azure SQL -> shipment/delivery/partial/full refunds; exact
refund sums including discounted merchandise and tax; 12 audit entries across
four actions; identical retries; stale version; invalid transition; changed
request payload; competing connection lock; duplicate/unrelated returned lines;
captured-payment mismatch; unchanged baseline after rollback.

`-Browser` starts an isolated localhost-only harness on port 3001 with a bounded
15-minute rollback transaction and a test-only password `rollback-browser-test`.
It is excluded from deployment. Stop with Ctrl+C; disconnect also rolls back.
Browser verification exercised ship -> deliver -> partial return, refreshed
status/refund/audit display, and 390px layout without horizontal page overflow or
browser errors. The harness serializes requests because one transaction uses one
SQL connection; the normal server uses its connection pool.

The 100k seed is an initial snapshot. After actual portal actions are committed,
status/refund/audit counts and timestamps will legitimately change. Do not treat
the original cutoff-specific baseline report as a live-data acceptance test or
reload the baseline over live changes. Code rollback does not undo business writes.
