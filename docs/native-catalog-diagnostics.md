# Native catalog diagnostics

Phase D is in progress, tracked by [#151](https://github.com/bcsnpc/data-investigation-agent/issues/151). PR #150 merged the scan/dependency foundation. This continuation provides an operator CLI for native measure, dependency and dimensional reads in one delivery. It does not enable an autonomous planner or replace the bounded-v1 ticket runtime.

## What works

`scripts/investigator/native_diagnostics.py` compiles catalog IDs into native DAX. Measures are selected from the enabled, reviewed, immutable model context; there is no metric-name allowlist. Power BI evaluates the expressions. The compiler does not translate DAX into local arithmetic.

A plan pins model ID, revision and context ID. It selects 1–12 measures, 1–8 explicit string-column filters (up to 50 values each), an optional catalog dimension, and a dependency flag. Unknown IDs, extra fields, stale contexts and disabled models fail admission. Dependency traversal uses retained metadata and stops where analysis or inherited effective context is not certified. Child values are separately evaluated under the requested filters; they are not represented as certified intermediate values inside a parent expression.

The transport sends one read to the configured workspace/model using the existing Power BI credential provider. It rejects redirects, applies a 90-second HTTP timeout and a 120-second worker timeout, and bounds the response to 2 MiB. Dimension queries request at most 501 rows; 501 means PARTIAL and only 500 rows are retained. These bounds do not guarantee a bound on engine scan cost. There are no automatic retries.

The local catalog database stores a `native_diagnostics` receipt before dispatch and updates it after completion. Each receipt retains the plan, generated query, catalog/context/scope hashes, selected IDs, typed results and status. BLANK remains BLANK; decimals retain their numeric type and decimal text across the subprocess boundary. Missing/error responses never become zero. Local context changes during execution hold the result. Timeouts are INTERRUPTED because remote completion is unknown; an abandoned RUNNING receipt is not automatically resumed.

## Run

Use IDs from the current catalog context, not the illustrative placeholders below:

```json
{
  "model_id": "registered-catalog-model-id",
  "revision": 5,
  "context_id": "current-context-id",
  "measure_ids": ["retained-measure-asset-id"],
  "filters": [{"column_id": "retained-string-column-id", "values": ["USD"]}],
  "dimension_id": null,
  "include_dependencies": true
}
```

Save the plan under `.local/`, then run:

```powershell
python scripts/run_native_diagnostic.py --config infra/metadata/development.json --database .local/catalog.sqlite --environment development --plan .local/native-plan.json --approve
```

Use the database/environment belonging to your model-admin instance. Review and enable its catalog first. The separate hidden worker is an internal operator-owned transport, not an API for model-generated DAX. Credentials are not included in plans or receipts. Results and database files stay out of Git.

## Verification on 2026-09-14 (local time)

The full regression suite passed: **397 tests**. Ten focused tests cover unfamiliar measures, escaping, stale/disabled admission, dependency context gaps, exact decimals, BLANK, invalid responses, dimensional truncation, persisted receipts, midflight disablement and redacted failures. The focused suite also verifies interruption status for timeouts. CI includes this suite.

Two live Power BI reads succeeded using a separate local test catalog and explicit unknown business policy fields. Average Order Value returned **651.9948**, with discovered Funded Orders **97527** and Sales Amount **63587096.7**, under the requested FactOrderLine currency USD filter. The category diagnostic returned one Office Electronics row. These are observed responses, not a claim about expected data or exhaustive business categories. No Azure SQL query or LLM call was made by this diagnostic validation.

Local receipts: `60562384-9018-4335-b057-613d120aa3ce` (scalar) and `85c51bbb-18d8-484d-b102-296924b105bb` (dimension), in `.local/model-admin-verify/native-diagnostics.sqlite`. The test catalog does not supply production ownership, SLA or tolerance decisions.

## Still pending

- Verify remote definition/version and effective identity at execution; reproduce the actual visual's complete filter/date/RLS context.
- Add upstream tools with source/snapshot comparability and richer typed filters.
- Certify effective dependency contexts, dimensional attribution and semantic capability gates.
- Add concurrent budget admission, interruption reconciliation and durable investigation orchestration.
- Build the adaptive planner/verifier, frozen-engine unseen-metric acceptance, and shared ticket views.

Every successful receipt explicitly leaves snapshot comparability, remote-definition verification, effective identity, visual replay and root-cause verification false. COMPLETE_RESPONSE describes the response shape only; it is not a verified healthy/defect outcome. Grouped Power BI results may omit all-BLANK groups.
