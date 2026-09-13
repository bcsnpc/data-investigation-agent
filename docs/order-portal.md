# Order Operations Portal: first release

Tracking: APP-001 (#4). The first release supports authenticated, read-only
order browsing. Updates and transactional live audit writing remain pending.

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
  refund lines and related order/payment/refund audit events.
- UTC date display and USD formatting; order total is not labeled revenue.
- Loading/error/empty states, preserved filters when returning from details,
  and responsive desktop/mobile layouts.
- Bound SQL parameters, validated input, pooled connections and query timeouts.
- Protected API endpoints, HttpOnly/SameSite cookies, secure cookies in deployed
  production mode, login rate limiting and security headers.

This is single-operator demo authentication, not enterprise SSO. Session signing
is stateless: logout clears the browser cookie; rotating SESSION_SECRET revokes
all issued sessions. The next application write phase must add business-rule
validation, actor attribution, CSRF protection and atomic audit insertion.

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
