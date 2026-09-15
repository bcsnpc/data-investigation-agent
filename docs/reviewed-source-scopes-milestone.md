# Reviewed source discovery and typed scopes

Tracked by [#169](https://github.com/bcsnpc/data-investigation-agent/issues/169), implemented in [PR #170](https://github.com/bcsnpc/data-investigation-agent/pull/170), following merged PR #168. This grouped milestone covers source-scope compilation, onboarding mapping reuse, admission/provenance, admin/operator preview and verification. It advances B/D/F/G without completing their proof gates.

## What changes for investigations

Previously each adaptive envelope needed a manually written source plan, and SQL filters supported strings only. With `source_selection: "reviewed_mappings"`, the runtime discovers a unique current reviewed mapping for each reachable measure and translates the complete native scope into a source test. The LLM can choose that candidate from evidence; it cannot invent an object, rewrite the mapping or remove a filter.

The existing manual source-test mode remains available. Automatic discovery requires `source_tests: []`; the two modes cannot be mixed. The native dependency graph still controls which measures are reachable and which child contexts can be investigated.

Missing mappings, ambiguous current mappings, uncovered filters and unsupported bindings yield explicit gaps while retaining otherwise admissible native diagnostics. Discovery does not choose the newest of conflicting reviews. Retiring a review requires an explicit revocation. A changed review set invalidates an active session's candidate catalog.

## Typed SQL scope

| Catalog SQL types | JSON values | Supported predicates |
| --- | --- | --- |
| varchar/nvarchar/char/nchar | Bounded strings or null | Membership |
| tinyint/smallint/int/bigint | Exact integers within SQL range and the native literal budget, or null | Membership, half-open range |
| decimal/numeric/money/smallmoney | Fixed decimal text, at most four decimal places, within both native and SQL budgets, or null | Membership, half-open range |
| bit | JSON booleans or null | Membership |
| date/datetime2 | ISO dates or whole-second local datetimes, or null | Membership, half-open range |

Ranges include their lower endpoint and exclude their upper endpoint. Range endpoints cannot be null, equal or reversed. Membership with null emits `IS NULL`; it never substitutes zero. Duplicate typed values are rejected. Computed and unsupported columns are not admitted.

Numeric/date values remain parameters. The generated SQL explicitly casts numeric parameters and converts dates with ISO style 126, following Microsoft's [CAST and CONVERT documentation](https://learn.microsoft.com/en-us/sql/t-sql/functions/cast-and-convert-transact-sql). Decimal scale/precision checks reject rounding and overflow before dispatch. Strings retain the existing NVARCHAR parameter transport. No caller-supplied type declaration or SQL expression is accepted.

Offset timestamps, fractional-second scope inputs and time-to-date truncation are rejected. Dates are model/source-local values: this does not certify timezone conversion, business calendar, date role, identity/RLS or relationship propagation. SQL NULL and DAX BLANK are not declared equivalent. Source/native exact JSON filter matching is an intent/scope check, not semantic or version proof.

## Review, preview and execution

Use the existing admin `POST /api/v2/admin/models/{id}/comparison-mappings` to retain a confirmed diagnostic mapping. It binds a measure, source object/operation/value column, grain, unit, date basis, blank policy and the complete native-to-source filter-column mapping to a context/revision. Admission additionally checks actual retained object/column types and native filter validity.

New admin operations:

- `GET /comparison-mappings`: inspect up to 100 retained model mappings; a larger catalog fails closed instead of truncating discovery.
- `POST /comparison-mappings/{mapping-id}/revoke`: `{"reason":"..."}`; retains the original review/history.
- `POST /diagnostic-preview`: complete adaptive envelope; returns candidates/gaps without query dispatch.

These paths are relative to `/api/v2/admin/models/{id}` and require the admin credential. Preview requires the configured connection controller. A mapping review remains `TEAM_CONFIRMED_INTENT`, not verified equivalence. The existing registration endpoint retains a review; executable readiness is determined by preview/admission, not by registration success alone.

To use automatic source discovery, keep the model, measure, native filters, dimensions and limits in the envelope and set:

```json
{
  "source_selection": "reviewed_mappings",
  "source_tests": []
}
```

For example, an approved native date filter has this shape (use a real catalog ID):

```json
{
  "column_id": "<native-date-column-id>",
  "operator": "range",
  "values": ["2026-08-01", "2026-09-01"]
}
```

Preview before using the existing approved execution command:

```powershell
python scripts/run_adaptive_investigation.py --config infra/metadata/development.json --database .local/model-admin-verify/native-diagnostics.sqlite --environment development --envelope .local/reviewed-envelope.json --preview
```

Preview does not create an investigation runtime, acquire an Azure LLM key or dispatch a cloud query. Source catalog discovery also reports filter capabilities. There is no new browser UI or cloud deployment in this milestone.

Generated plans retain `comparison_mapping_id`; compiled requests, candidates and observations retain the mapping hash and authority. Source dispatch rechecks the binding before and after its read. Revocation or changed binding stops admission; completed receipts remain historical and expose whether their mapping is still current. The adaptive engine's existing budget, cancellation, recovery and replay mechanisms apply unchanged.

## Verification and live boundary

The complete script regression passed: **579 tests**. 31 focused tests cover parameterization, temporal boundaries, exact decimal storage, booleans/nulls, unsupported types, complete scope translation, ambiguity, stale/revoked/tampered mappings, cross-model rejection, adaptive selection/replay and admin/CLI preview without cloud calls.

Live Azure SQL check on 2026-09-15 UTC: run `1cb82f63-8fb9-47cd-b09d-9adb23f728b2`, receipt `4701ab20-9e40-4055-971f-d8ceee1474b4`. One count query with USD membership, order date `[2026-08-01, 2026-09-01)` and total amount `[0, 1000000000)` returned **21365** rows. It connected on the first attempt. Replay returned the saved receipt with no cloud dispatch. Evidence is retained under ignored `.local/reviewed-scopes-live-evidence.json`.

The development catalog currently contains **no reviewed source mapping**. Its automatic preview correctly retained the native candidate and returned `CURRENT_SOURCE_MAPPING_MISSING`. We did not fabricate team confirmation to make the live automatic path pass. Automatic execution is verified with controlled reviewed fixtures; the live result above verifies typed SQL scope, not a live reviewed mapping or Power BI equivalence. The preview is retained in `.local/reviewed-scopes-live-preview.json`.

No LLM call was needed for this transport check. It used the operator runtime's one-query bound, outside the adaptive daily ledger. SQL tier/free-offer/overage settings were unchanged. Neither a query bound nor this result certifies compute consumption.

## Next exit gates

Review actual development source mappings and business scope before automatic source execution there. Then complete effective report/date/identity context, publication/shared-generation readback and semantic/causal proof. A matching count is not an expected-behavior certificate. After those B-G gates, run the frozen eight-family native acceptance protocol, finish the shared ticket workspace and reviewed v2 handoff, and deploy/verify the end-to-end product.
