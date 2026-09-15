# Comparison intent and evidence gates

This grouped D/E continuation follows merged PR #158 and is tracked by [#159](https://github.com/bcsnpc/data-investigation-agent/issues/159). It pairs retained native/source observations and records why they are not yet comparable. It is not a completed equivalence verifier.

## Reviewed intent

An admin can register an immutable mapping that pins the model revision/context, native measure, SQL object/operation/value column, declared grain/unit/date basis, BLANK preservation and native-to-source filter bindings. Confirmation must be explicit. The record retains the reviewer and body hash as TEAM_CONFIRMED_INTENT.

Registration records intent; actual bindings are checked against the selected executed receipts. It does not prove a DAX expression is equivalent to a SQL operation, certify the declared grain/date role, or turn a reviewer assertion into remote version evidence. Re-review creates a new mapping; an old mapping fails current-context assessment after a revision changes.

## Assessment

The request contains only `native_receipt_id`, `source_receipt_id`, `measure_id` and nullable `mapping_id`. Values are read from scoped saved evidence, not accepted from the client. Proof flags, thresholds and numeric answers cannot be supplied in this request.

The assessor checks:

- Current enabled context and matching native/source context versions.
- Successful source read, complete scalar native response and the selected measure's presence.
- Reviewed mapping bound to the exact source object, operation and value column.
- Complete one-to-one filter coverage and exact string value agreement. Extra date filters, numeric coercion, case folding and partial filter matches cannot be silently ignored. Semantic filter propagation and SQL collation equivalence remain unverified.
- BLANK and nonnumeric observations remain explicit; they do not become zero.

When those structural gates pass, exact Decimal subtraction can produce a **diagnostic** native-minus-source difference. A zero difference is not a healthy classification, and a nonzero difference is not a defect classification. When mapping/scope gates fail, no difference is produced; both available observations can still be shown.

All current assessments return INSUFFICIENT_EVIDENCE and leave comparability, verified cause and delivery eligibility false. Four proof gates remain open: upstream semantic equivalence, effective context, remote definition version and shared data generation. There is deliberately no client-supplied flag or review override to bypass these missing adapters.

The assessment persists request, context/revision, evidence hashes, mapping hash, typed observations, diagnostic difference and explicit gaps. Historical reads validate the saved assessment hash and report whether the context and referenced evidence remain current/unchanged. Hashes protect local consistency, not against an administrator rewriting the database and hashes together.

## Interfaces

Admin-only routes under `/api/v2/admin/models/{id}`:

| Route | Behavior |
| --- | --- |
| `POST /comparison-mappings` | Register explicitly confirmed mapping intent |
| `GET /comparison-mappings/{id}` | Read scoped historical mapping |
| `POST /comparisons` | Assess saved observations and persist the result |
| `GET /comparisons/{id}` | Read assessment, context status and evidence-change status |

The API uses the existing bounded JSON and role/environment checks. It makes no SQL, Power BI or LLM requests.

A local assessment without a reviewed mapping is also available:

```json
{
  "native_receipt_id": "saved-native-receipt-id",
  "source_receipt_id": "saved-source-receipt-id",
  "measure_id": "retained-measure-id",
  "mapping_id": null
}
```

```powershell
python scripts/assess_comparison.py --database .local/catalog.sqlite --inventory .local/metadata/inventory.sqlite --environment development --model-id REGISTERED_MODEL_ID --request .local/comparison.json
```

## Verification

The full regression suite passed: **437 tests**. The focused suite also passed after historical evidence-change checks were added. Ten focused tests cover unreviewed/equal-value cases, exact decimal differences, BLANK/scalar requirements, complete scope alignment, stale reviews, mismatched bindings, rejected proof flags, failed reads, hash integrity, evidence changes and admin authorization. No case claims verified equality or cause.

Two assessments of real retained receipts ran without new cloud queries:

- `75cdfa38-109f-47f3-a020-e3b39c1498c3` retained Funded Orders 97527 and source order count 100000, reported the missing reviewed mapping and proof, and produced no difference. These are differently defined quantities; the assessor did not claim a discrepancy.
- `573e08a5-0a00-4883-8c19-7d38c2961f15` paired the native observation with the earlier failed source read and added SOURCE_READ_UNAVAILABLE with no source value.

Both are retained in the existing local diagnostic catalog. No real business mapping was fabricated or auto-confirmed during validation.

## What closes the remaining gates

Implement authoritative operation/grain/filter/date/BLANK equivalence adapters and capture effective identities. Establish remote model-definition and source/semantic generation proof, including the controlled native acceptance prerequisites in the phase plan. Then add deterministic eligibility for supported comparisons. Durable run/budget recovery, adaptive hypothesis selection and the eight acceptance families remain subsequent milestones.
