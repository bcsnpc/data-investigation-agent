# Reviewed record discovery

Tracked by [#173](https://github.com/bcsnpc/data-investigation-agent/issues/173). Builds on merged PR #172.

## Problem and delivered behavior

Previously an operator had to provide both record plans and comparison bindings for every ticket. An admin can now review a reusable projection once for a model/context/measure. Subsequent tickets opt into `record_selection: reviewed_mappings`; the candidate catalog derives native and source plans from that review and the ticket's complete filters.

The mapping records a native table, source table, paired columns, native keys, paired filter columns, record limit, grain and date basis. Catalog validation checks table ownership, supported matching types, unique projected keys, bijective mappings and consistency between shared projected/filter columns. It does not infer business meaning from names. Computed SQL projections and unsupported native types are rejected.

Both reads unlock after the associated measure's scalar observation. Once captured, their deterministic keyed comparison is available to the next planner decision. No additional query is needed to compare saved evidence. Manual record plans remain supported; automatic selection cannot mix with manual tests or pairs.

## Admin workflow

All endpoints are under `/api/v2/admin/models/{model_id}` and require the existing admin credential.

1. `POST /record-mapping-preview` with `{mapping, filters}` validates an unconfirmed draft against example ticket filters. It compiles both bounded projections, returns types and hashes, and saves no review or evidence. `confirmed: false` is permitted here.
2. `POST /record-mappings` records a validated mapping with explicit `confirmed: true`. The saved actor is the authenticated local-admin role; this is not a directory-backed named approver identity.
3. `GET /record-mappings` and `GET /record-mappings/{id}` retain immutable review bodies, hashes and revocation history.
4. `POST /diagnostic-preview` accepts an adaptive envelope with `record_selection: reviewed_mappings` and no manual record tests/pairs. It returns candidates and precise gaps without querying data or invoking the planner.
5. `POST /record-mappings/{id}/revoke` accepts `{reason}`. Revocation is irreversible and idempotent; a replacement requires a new review. Historical receipts are retained.

Mapping body:

```json
{
  "revision": 1,
  "context_id": "catalog-context-id",
  "measure_id": "catalog-measure-id",
  "native_object_id": "catalog-native-table-id",
  "source_object_id": "catalog-source-table-id",
  "column_bindings": [
    {"native_column_id": "native-key-id", "source_column_id": "source-key-id"},
    {"native_column_id": "native-value-id", "source_column_id": "source-value-id"}
  ],
  "key_column_ids": ["native-key-id"],
  "filter_bindings": [
    {"native_column_id": "native-scope-column-id", "source_column_id": "source-scope-column-id"}
  ],
  "limit": 100,
  "grain": "Team-reviewed record grain",
  "date_basis": "Team-reviewed date basis",
  "confirmed": false
}
```

Use actual catalog IDs. Preview does not confirm this example. Ticket values are not stored in the reusable mapping; each ticket supplies its own full filter scope.

## Admission, evidence and limits

- Exactly one current, unrevoked mapping per reachable measure is required. Missing or ambiguous mappings become explicit gaps. Discovery never chooses a convenient match.
- Filter-column sets must match the review exactly; unsupported or extra scope is held, never dropped. Native and source filter values are carried unchanged through the column mapping.
- Up to two discovered pairs, eight projected fields, three key fields and 250 groups per read retain the existing record budgets. Exceeding the pair budget rejects admission rather than silently omitting checks.
- Mapping IDs/hashes are included in plans, receipts, candidates and paired observations. Runtime admission and pre/post-read compilation recheck review, metadata and scope. Revocation or new ambiguity holds active sessions before further dispatch. Completed historical evidence remains readable.
- Review means `TEAM_CONFIRMED_INTENT`. It never certifies effective RLS/filter propagation, source/native semantic equivalence, shared generation, cause or delivery eligibility. Grain/date prose remains reviewed descriptive context, not an executable equivalence contract.

## Verification

Full regression: **641 tests passed**, including 27 focused tests. The focused tests cover reusable scopes, missing/ambiguous mappings, explicit confirmation, catalog/type/key rejection, unchanged scope, tampering, revocation before/during reads, durable admission, child-measure gating, saved provenance, API roles, draft preview and adaptive paired evidence. In the adaptive fixture, matching and differing records lead to different subsequent planner decisions; the planner is injected, so this is not a live LLM reliability result.

The query-free development preview validated the previously captured order projection (`order_id`, `currency`, `status`, `order_date`) against the pinned native/SQL catalog. Both projections compiled with types string/string/string/dateTime. Result: `DRAFT_VALIDATED`, `UNCONFIRMED_DRAFT`, zero cloud calls, no saved review. The ignored artifact is `.local/record-mapping-draft-preview.json`.

No SQL adapter changes, data queries, LLM calls, cloud writes, quota changes or UI deployment were needed for this milestone. The live read evidence from PR #172 remains historical evidence, not a fresh read in this milestone.

## Remaining

Actual development mappings still require business review. Shared generation, effective context, semantic equivalence and supported causal verifiers remain open, followed by the frozen eight-family acceptance protocol and unified user workflow. This milestone improves reusable discovery and admission; it does not complete phases B-G or H-J.
