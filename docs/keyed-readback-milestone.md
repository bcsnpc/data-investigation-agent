# Bounded record readback and keyed evidence

Tracked by [#171](https://github.com/bcsnpc/data-investigation-agent/issues/171), following merged PR #170. This grouped milestone adds native/SQL record acquisition, typed durable tools, keyed evidence, adaptive pairing, recovery tests and live verification. It advances D/F/G and the readback prerequisite for H; it does not pass H's shared-generation or causal acceptance gate.

## What it establishes

Aggregate equality can conceal changed records whose differences cancel out. The investigator can now read selected columns and keys, preserve group multiplicity, and compare complete captured responses by key. It can report observed missing/extra keys or changed projected values without claiming which system is correct or why they differ.

Registered tools:

| Tool | Work and limit |
| --- | --- |
| `native_records` | One Power BI DAX query against a retained table, with explicit filters, 1-8 projected columns, 1-3 projected key columns and a limit of 1-250 groups |
| `source_records` | One parameterized SQL query with the same projection/key bounds, using existing scoped catalog and typed-filter admission |
| `compare_records` | Local comparison of saved readbacks using explicit complete column and filter bindings; no cloud query |

Both readers group by every selected column and retain multiplicity. They request `limit + 1` groups to detect an exceeded limit. Native ordering includes every grouped column so [TOPN boundary ties](https://learn.microsoft.com/en-us/dax/topn-function-dax) cannot expand a unique grouped projection indefinitely. A duplicate entity can appear through multiplicity greater than one or through distinct values with the same declared key; both make keyed comparison ineligible.

`COMPLETE_RESPONSE` means the bounded query returned all its projected groups. It does not mean every model column, every business entity or every source partition was captured. A response with the sentinel group is `PARTIAL`, and its retained records cannot establish missing keys or equality. Over-budget, malformed, repeated-group and provider-error responses fail.

Strings, exact integers/decimals, booleans, blanks and local datetimes have explicit representations. Decimal normalization preserves exact values; datetime normalization preserves up to seven fractional digits without timezone conversion. Unsupported/lossy types and oversized values fail. Native double columns are not admitted. SQL NULL and native BLANK remain semantically uncertified even though both have a blank representation.

## Keyed comparison

Column bindings must cover the entire projection bijectively, and declared keys must map to each other. Exact filter-intent matching, complete responses, compatible types, current context at assessment, non-null keys and unique keys are required before differences are computed.

The result distinguishes:

- `OBSERVED_EQUAL`: no difference among these captured projected records.
- `OBSERVED_DIFFERENCE`: `ONLY_NATIVE`, `ONLY_SOURCE` or `VALUES_DIFFER` evidence, with an exact difference count and at most 50 examples.
- `NOT_ASSESSED`: incomplete/unavailable reads, incompatible scope/types, duplicate/null keys or stale context.

The overall outcome remains `INSUFFICIENT_EVIDENCE`. `comparable`, `root_cause_verified` and `delivery_eligible` stay false. Shared generation, semantic equivalence and effective identity/context are separate proof gaps. Equal captured values are not a business expected-behavior certificate. Different captured values are not automatically a defect.

Row ordering does not affect keyed comparison. Evidence hashes preserve the captured ordering; they detect local receipt changes and are not provider signatures or data-version attestations.

## Durable and adaptive execution

The existing runtime reserves readback receipts and cloud-call budgets before dispatch. Receipt integrity covers the request, status, creation time and result. Recovery adopts only terminal matching evidence; uncertain remote completion cannot be silently resent. Local comparisons can be recovered separately. Cancellation keeps recovered evidence without restarting work.

Each record plan has these exact fields:

```json
{
  "model_id": "<registered-model-id>",
  "revision": 1,
  "context_id": "<current-context-id>",
  "object_id": "<native-table-or-SQL-object-id>",
  "column_ids": ["<key-column-id>", "<value-column-id>"],
  "key_column_ids": ["<key-column-id>"],
  "filters": [{"column_id": "<scope-column-id>", "operator": "in", "values": ["<approved-value>"]}],
  "limit": 50
}
```

Use the existing `run_investigation_v2.py` command with `native_records`/`source_records` actions. A later `compare_records` action takes `native_step`, `source_step`, `column_bindings` and `filter_bindings`. Each binding is `{"native_column_id":"...","source_column_id":"..."}`. Invalid projection mappings are rejected before either query runs.

Adaptive envelopes optionally admit up to four `record_tests`, each containing `tool`, `measure_id` and `plan`. A record test unlocks after its associated native scalar succeeds. Native record filters must preserve the envelope's complete native scope. Source record plans remain explicitly operator-approved; automatic record-projection discovery from onboarding is not implemented.

Up to two optional `record_pairs` declare `native_test` and `source_test` indexes into that `record_tests` list, plus the complete column/filter bindings. Once both observations arrive, deterministic keyed evidence is stored in the session and supplied to the next planner decision. Pair evaluation consumes no cloud call. Planner row samples are bounded and explicitly marked when shortened; stored evidence remains intact. Business and technical projections share the stored comparisons and outcome.

Admin endpoints under `/api/v2/admin/models/{model-id}`:

- `GET /record-readbacks/{receipt-id}` reads saved evidence.
- `POST /record-comparisons` accepts saved native/source receipt IDs and complete bindings.
- `GET /record-comparisons/{assessment-id}` reads the retained local assessment.

These use the existing admin credential. No browser UI or cloud deployment is included.

## Verification

35 focused tests cover bounded native/SQL compilation, exact values and dates, complete/empty/partial responses, offsetting changes hidden by equal totals, missing keys, duplicates, null keys, scope mismatch, receipt integrity, API authorization, replay, interrupted-read and local-comparison recovery, cancellation, and an adaptive paired-read sequence feeding the next planner decision.

Live run `28d0f9aa-ec3e-4314-8d3b-231c4174cdef` on 2026-09-15 UTC selected five existing orders, USD scope, and four projected fields: order ID, currency, status and order date. SQL and native Power BI each returned five groups with multiplicity one. Keyed comparison returned `OBSERVED_EQUAL`, zero differences, and all three proof gaps. Their row ordering differed; keyed matching correctly ignored that ordering difference.

Receipts: SQL `4bd4be0d-94de-4ec6-9ef3-a2b2424a0543`, native `89e82289-423e-4009-9623-a342c6d5dde0`, comparison `6feabd51-8113-4f29-b914-69dbc5b1f0ab`. Full evidence and the approved request are retained in ignored `.local/keyed-readback-live-evidence.json` and `.local/keyed-readback-live-request.json`.

SQL first returned 40613 during connection and succeeded on the second connection attempt through the existing bounded retry policy. Only one SQL data query and one native query were dispatched; the comparison is local. No LLM call was needed for this transport check. It used the operator runtime's two-call allowance outside the adaptive daily ledger. SQL free-offer/tier/overage settings were unchanged. Query bounds do not certify compute billing.

## Remaining proof and product work

This closes the missing bounded native/source record-acquisition capability. The complete-native-readback proof requirement is now **PARTIAL**, since published-generation contents, exclusive publication/write boundaries, exact report/identity/date context and equivalent source semantics remain unverified.

Next: establish the controlled generation/publication and business-scope contracts, use readback to validate that boundary, and add supported causal confirmation. Actual development source mappings still need team review. Then run the frozen eight-family native acceptance protocol, finish the shared business/technical ticket workspace and reviewed routing, and deploy/verify the end-to-end v2 product. The five-order live check is not a substitute for those acceptance families.

Full regression: **614 tests passed**. Completed live-run replay returned the saved result with transports configured to fail if called: **zero cloud calls**.
