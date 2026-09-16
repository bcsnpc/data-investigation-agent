# Shared investigation workspace and isolated reader verification

Updated 2026-09-15. PR #180 is merged. This combined milestone is tracked by [#181](https://github.com/bcsnpc/data-investigation-agent/issues/181). It delivers a local interactive v2 workspace and verifies the dedicated fixture reader. It does not close the general causal-investigation or hosted-product gates.

## Delivered behavior

- Select an enabled catalog model and metric, describe the concern, and enter typed, bounded filters and an optional breakdown. A query-free preview pins the catalog context, scope, candidates and engine. Start is a separate explicit action; previews expire after 15 minutes.
- A background worker runs the existing governed adaptive runtime. Duplicate starts return the same saved session. One active job is admitted per workspace database. Fixed per-session limits are six cloud calls, six planner calls, 900 seconds, 80,000 input characters and dependency depth three, alongside the existing shared usage policy.
- Business overview and technical evidence come from the same saved projection and outcome hash. Captured values, progress, uncertainty and missing evidence are visible; technical evidence can be downloaded. A finished check is not labelled a verified cause.
- History reads do not re-query providers. Clarification creates a newly reviewed successor scope and does not reuse old facts. Cancellation fences later work; it cannot abort a request already executing remotely.
- Restart does not silently take over another worker's queued or uncertain work. Interrupted submissions and detached workers remain visible for operator review through the existing recovery procedures.
- The loopback API requires a separate local key, validates host/origin, bounds JSON bodies and serves a restrictive CSP. The browser retains the key only in memory. This is single-operator access, not enterprise user authorization.

Implementation: `scripts/investigator/workspace.py`, `workspace_api.py`, `scripts/serve_investigator_workspace.py`, and `apps/investigator-workspace/`. The existing v1 portal and admin UI remain separate.

## Local runbook

Use the existing development Python environment and authenticated provider configuration. Generate a separate key and retain it privately for the browser login:

```powershell
$env:INVESTIGATOR_WORKSPACE_TOKEN = python -c "import secrets; print(secrets.token_urlsafe(40))"
python scripts/serve_investigator_workspace.py --config infra/metadata/development.json --database .local/model-admin-verify/native-diagnostics.sqlite --environment development --live --usage-policy infra/runtime/development-usage-policy.json --azure-settings infra/llm/development.json
```

Open `http://127.0.0.1:8776`. Omitting `--live` disables execution; saved history remains available. The database must contain an onboarded, enabled model and its retained metadata. The key is supplied through `INVESTIGATOR_WORKSPACE_TOKEN`, never committed or placed in a URL. Live execution uses the configured development provider connections; it does **not** automatically switch to the isolated fixture reader.

API routes under `/api/workspace`: `GET models`, `POST previews`, `GET/POST sessions`, `GET sessions/{id}`, and `POST sessions/{id}/cancel`. There is no arbitrary SQL/DAX input endpoint.

## Verification

**746 regression tests passed**, including 24 workspace and four reader tests. JavaScript syntax checks passed. The browser harness passed 12 checks: login, explicit scope, preview/start, numeric values, shared outcome, technical view, history without re-query, clarification successor, cancellation, mobile layout, signout and console errors. Its two native calls are injected test responses, not cloud acceptance evidence.

A separate live browser-to-API-to-runtime check used the existing development connection:

| Observation | Result |
| --- | --- |
| Metric and bounded scope | Units Ordered; order IDs ORD-000001 through ORD-000005 |
| Saved native result | **49**, complete response |
| Provider usage | One Azure LLM planning call and one Power BI query; 1,771 planner input characters |
| Session | `0a5446bd-db07-48ac-bd6d-00bc8e4d7a56` |
| Native receipt | `8136211a-60a9-442d-805f-685cc388313e` |
| Stop | `NO_ADMITTED_TEST` after the captured native read |
| Cause and delivery verified | Both false |

Approved source and detailed-record mappings for this metric/scope were missing. Effective context/version/causal proof was also missing. The overview reports those gaps in plain language. The value 49 is an observation, not proof that a report is correct or defective. No Azure SQL query, SQL quota change, business-model write or Azure application deployment occurred in this live UI check.

Local evidence is retained under `.local/workspace-live-session.json`, `.local/workspace-live-browser.json`, `.local/workspace-browser-verification.json` and corresponding screenshots; it is intentionally not committed. Run `python scripts/verify_investigator_workspace.py --agent-browser <installed-agent-browser-executable> --output .local/workspace-browser-verification.json` to repeat the injected browser integration checks.

## Dedicated fixture reader

The user created `investigator-reader@skynwhy.com` and completed its own interactive sign-in. It received Viewer on the isolated workspace `ae4637b9-7d8b-4d7f-9f3e-28f3b3859080` and model Read/Build (`ReadExplore`) on `6304045c-f80f-4e24-b905-b65522dff7ad`. No business-workspace access was added.

`scripts/connect_fixture_reader.py` keeps its MSAL cache under `.local/fixture-reader-auth/`, encrypted with Windows DPAPI and separate from the publisher cache. It validates the expected tenant, audience and account, with no fallback to the publisher. Its own token returned a matching `USERPRINCIPALNAME()` and all ten exact typed fixture rows. A refresh-history request returned **403**; that endpoint requires [dataset Write permission](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/get-refresh-history-in-group). This is one observed denied capability, not proof of every possible permission boundary.

```powershell
.local/fabric-cli-env/Scripts/python.exe scripts/connect_fixture_reader.py --tenant dff91047-ebc2-4657-8dbe-5af328d57780 --account investigator-reader@skynwhy.com --workspace ae4637b9-7d8b-4d7f-9f3e-28f3b3859080 --model 6304045c-f80f-4e24-b905-b65522dff7ad --bundle .local/import-fixture-bundle.json --output .local/fixture-reader-verification.json
```

Add `--sign-in` only when interactive authentication is needed. Existing Fabric CLI environment dependencies include MSAL and MSAL extensions. The result records `fixture_reader_checks_passed=true`, while **`generation_proven=false` and `live_acceptance_ready=false`** remain intentional. Publisher access still exists; an isolated reader and exact rows do not establish exclusive remote publication or shared-generation proof.

## Remaining grouped work

1. Complete effective report/filter/date/identity context, authoritative model mappings, enforceable publication/version evidence and supported causal verifiers. Carry the isolated reader into the actual frozen acceptance workflow. Close the remaining B-G exit gates using these proofs.
2. Freeze the runtime and pass all eight Phase H acceptance families, including unseen additive, ratio and complex measures and healthy/defect/gap variants. Current smoke checks do not establish generality.
3. Complete business screenshot/report intake and scope reproduction, hosted multiuser onboarding/workspace authorization, reviewed v2 routing and Azure deployment. This workspace is the local Phase I execution/review slice; users still choose the catalog metric and bounded filters manually.

The cumulative source of truth is [current delivery status](current-delivery-status.md), with [A-J acceptance gates](architecture/phases-and-acceptance.md).
