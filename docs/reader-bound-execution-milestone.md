# Reader-bound native execution

Updated 2026-09-15. PR #182 is merged. Review: [PR #184](https://github.com/bcsnpc/data-investigation-agent/pull/184). This milestone is tracked by [#183](https://github.com/bcsnpc/data-investigation-agent/issues/183).

The dedicated reader can now execute through the actual native diagnostic worker and durable runtime. Previously, its sign-in was verified separately while all runtime queries still selected the Fabric CLI publisher login. This change makes reader selection explicit and carries the observed principal into saved evidence.

## Behavior and trust boundary

- Optional `fabric.native_reader` config selects the isolated MSAL/DPAPI reader cache. The existing `fabric.auth` remains the metadata/publisher connection. Existing configurations retain their previous behavior; the business development configuration was not switched or granted new access.
- The native worker checks the configured account, tenant, object ID and model allowlist. Missing credentials, another principal or an out-of-scope model fail without selecting the publisher. Interactive login is never started by an investigation worker.
- The runtime also applies the boundary to injected native transports. Configured reader execution cannot silently accept a response without matching identity evidence. Adaptive scope admission rejects models outside the configured reader scope before calling the planner.
- Scalar, dimensional and native record receipts retain the principal, account, tenant, target model/workspace, query hash, response hash and capture time. Decimal precision and blank values survive the subprocess boundary. Receipt seals cover the identity metadata as well as the values.
- Adaptive observations and technical projections retain the saved identity. Planner payloads omit account identifiers; the LLM does not need them to select diagnostics. Historical receipts without an identity remain historical, without an invented principal.
- Changing the runtime connection config invalidates active pinned execution. The isolated verification command also rejects replay under a different connection/reader profile, preventing relabelling of old evidence.

These are **local transport observations**, not Microsoft-signed evidence. They establish which token principal the trusted local worker used for a particular query. They do not establish report-viewer equivalence, RLS/OLS equivalence, role stability, exclusive publication, shared generation or cause. An administrator could later change the reader's permissions. All effective-identity, generation and causal acceptance flags remain false.

Microsoft documents Read and Build requirements for [Execute Queries](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/execute-queries). The implementation uses the reader's delegated token directly and does not send an impersonated username.

## Configuration and operation

Add the following optional object alongside `fabric.workspace_id` and `fabric.auth` in a private local connection profile. Use the actual enterprise object ID, not an email-derived identifier:

```json
"native_reader": {
  "mode": "isolated_reader",
  "tenant_id": "<enterprise-tenant-UUID>",
  "account": "investigator-reader@skynwhy.com",
  "principal_id": "<reader-object-UUID>",
  "model_ids": ["<allowed-semantic-model-UUID>"]
}
```

The tenant must match the metadata profile's enterprise tenant. This is non-secret configuration; access tokens, passwords and caches stay under `.local/`. The worker uses the configured Fabric Python environment, which already has MSAL and MSAL extensions. Complete interactive reader login with `scripts/connect_fixture_reader.py --sign-in` when needed, then use the regular native/adaptive/workspace entrypoints with this profile. It affects native Power BI reads, not SQL authentication or metadata collection.

The new `scripts/verify_reader_runtime.py` performs an explicit three-action verification: native scalar/dependencies, native breakdown, and projected native record groups. It consumes a validated Import fixture bundle plus a bounded scope file, uses a separate immutable local fixture catalog and persists normal runtime/receipt records. This operator fixture catalog is **not** a fabricated report scan: it has no registered Power BI report and is labelled `OPERATOR_FIXTURE_MANIFEST`. It does not change production onboarding tables. Expected rows are compared after execution; they are not supplied as metric answers to the runtime. The fixed verification sequence is a test workflow, not the adaptive investigation planner or hidden evaluator.

```powershell
python scripts/verify_reader_runtime.py --config .local/reader-runtime-config.json --bundle .local/import-fixture-bundle.json --scope .local/reader-runtime-scope.json --database .local/reader-runtime-verification-final.sqlite --model 6304045c-f80f-4e24-b905-b65522dff7ad --request-key reader-bound-native-v1 --approve --output .local/reader-runtime-result-final.json
```

Scope fields: `table`, `measures`, `filter_column`, `filter_values`, `dimension`, `record_columns`, `key_columns`. These reference fixture metadata names; no raw query field is accepted. Query builders enforce their normal typed-filter and result limits. Repeating a completed request key reuses its saved result. `--status-only` reads that saved scope without dispatch. Uncertain execution is held, never automatically repeated. Changed fixture contents/definitions require a separate verification database. Keep generated outputs local.

## Live evidence

The final verification below repeated the three bounded reads after tightening the receipt-seal check: six Power BI queries total across both live runs, with zero-query replay checks. The existing isolated Import model was read under the dedicated reader, with no business-workspace permission change, remote write, SQL query or LLM call in this milestone's live verification.

| Evidence | Observed result |
| --- | --- |
| Workspace | `ae4637b9-7d8b-4d7f-9f3e-28f3b3859080` |
| Model | `6304045c-f80f-4e24-b905-b65522dff7ad` |
| Durable run | `0ad5287c-7977-4c5f-9470-779a7437b5e9` |
| Scalar values | 10 eligible, 2 refunded, 0.2 refund rate, 65 units |
| Breakdown | Two boolean groups, complete response |
| Native records | Ten projected groups/rows exactly matched fixture scope |
| Queries | Three Power BI calls, each with matching reader identity evidence |
| Replay and status | Same saved summary; zero additional cloud calls |
| Proof flags | Effective identity, generation, live acceptance and cause remain unverified |

The breakdown itself illustrates why context proof matters: the fixture's refund calculation replaces its boolean refund filter, so its native result under the non-refunded group remains two. These native results are preserved; the verifier does not assume every child shares its parent's effective filters or call that behavior a defect.

Local artifacts: `.local/reader-runtime-result-final.json`, `.local/reader-runtime-replay-final.json`, `.local/reader-runtime-verification-final.sqlite`. Scalar receipt `b91eebe4-9b11-4316-8a67-22b56f41df74`; breakdown `fa19ed61-e79e-4422-9b1d-994035dee062`; records `f1056df2-98ec-41fa-ab57-16d0db4fa0c8`.

## Validation and remaining work

All **775 regression tests passed**, including twenty focused identity/config/transport/receipt tests and nine durable fixture-workflow tests. Coverage includes missing credentials, wrong principal/tenant/target, omitted or altered identity evidence, sealed-history tampering, decimal/blank preservation, no publisher fallback, no-query replay, uncertain completion and account data exclusion from planner input. The full regression result is recorded in [current delivery status](current-delivery-status.md).

The next proof work is effective report/filter/date/identity context, authoritative source mappings, controlled publication/version evidence and supported causal verifiers. Then freeze and execute all eight hidden/native Phase H acceptance families. Business screenshot intake, hosted multiuser access, reviewed v2 routing and Azure v2 deployment remain separate product work. Reader-bound queries remove a concrete prerequisite gap; they do not close those larger gates.
