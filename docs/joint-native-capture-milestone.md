# Native totals and record groups captured together

Review: [PR #192](https://github.com/bcsnpc/data-investigation-agent/pull/192).

PR #190 is merged. This milestone is tracked by [#191](https://github.com/bcsnpc/data-investigation-agent/issues/191).

The investigator can request a supported native measure and its bounded projected
record groups in **one DAX query and one response**. It reconstructs the count or
sum from the returned groups, including multiplicity and blanks, and saves the
comparison with the same receipt. The business view displays both values; the
planner receives the saved consistency assessment when choosing its next check.

This closes the separation between these two native observations. It does **not**
establish snapshot isolation, exclusive publication, source/native shared generation,
effective report/RLS context, semantic equivalence or a verified business cause.

## Supported scope and behavior

- Direct `COUNTROWS(table)` and `SUM(table[column])` over exact numeric columns.
- The aggregate input, projected records and explicit filters must use the same
  native table. A SUM input must be included in the reviewed projection.
- Up to 250 retained groups, one sentinel group for truncation, or one
  empty-record placeholder. Strict parsing rejects changing repeated totals, extra
  fields, nonnumeric totals and malformed empty placeholders.
- Complete groups produce `CAPTURE_RECONCILES` or `CAPTURE_INCONSISTENCY` using exact
  arithmetic. Truncated groups produce `NOT_ASSESSED`. Neither outcome is a cause.
- Reviewed record discovery selects this form when supported and enabled in the
  envelope. Unsupported shapes retain the original record read and an explicit gap.
  Review revocation and context changes retain their existing admission checks.
- Workspace scopes enable joint discovery. Direct API envelopes can select it with
  `joint_native_records: true`; explicit native record plans use
  `aggregate_measure_id`. SQL record plans cannot request this extension.
- Both values, the reconstruction and reader identity are sealed in the record
  receipt. Reopening saved sessions or receipts performs no additional query.

The compiler returns a single table, as required by the [Power BI Execute Queries
API](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/execute-queries).
It combines a scalar row and bounded record groups through [DAX
GENERATEALL](https://learn.microsoft.com/en-us/dax/generateall-function-dax), preserving
the total even when the record set is empty. This API shape is
not a documented guarantee of a shared snapshot across external data sources.

## Verification

**860 regression tests** and **30 browser checks** passed. The 16 focused tests
cover exact counts/sums, blanks, multiplicity, partial results, malformed responses,
reviewed discovery, unsupported scope, sealed receipt tampering, adaptive planning
and dedicated-reader verification/replay. Browser checks exercise scope review,
execution, the observed/rebuilt total, shared outcomes, mobile layout and history.
Injected browser values are 30 observed and 30 rebuilt; they are not live evidence.

The reader verifier now accepts `--joint-measure` alongside its existing fixture,
scope, database, model and request-key options. `--approve` enables a live call;
`--status-only` reads the saved receipt and never dispatches. The fixture evaluator
compares complete projected contents outside the runtime; expected rows or expected
metric values do not enter the query/planner.

Local regression/browser artifacts are `.local/joint-capture-regression-final.log` and
`.local/joint-capture-browser-final.json`. Live verification status is recorded below;
test fixtures and local credentials are not committed.

### Live verification, 2026-09-16

The final compiler passed these dedicated-reader checks against the existing isolated
Import fixture; no publication, permission or Azure SQL changes were needed:

| Check | Observed result |
| --- | --- |
| Complete filtered count and records | 8 observed, 8 reconstructed; eight projected fixture rows matched; one query |
| Empty filter result | Blank observed and reconstructed, zero records; one query |
| One-group retention limit | Partial capture, `NOT_ASSESSED`; one query |
| Real Azure adaptive planner | Selected scalar then combined record read; two LLM calls and two native queries; saved joint assessment reached the outcome |
| Completed-run replay and receipt reads | Zero additional provider calls |

Artifacts: `.local/joint-capture-final.json`, `.local/joint-capture-empty.json`,
`.local/joint-capture-partial.json` and `.local/joint-adaptive-live.json`.
Live SUM parity is not claimed; exact SUM/multiplicity/null behavior has injected
coverage. These cases do not replace the eight hidden/native acceptance families.

The first UNION-based implementation timed out. Four UNION query attempts/probes
timed out while constant, table-count and grouped-record control queries succeeded.
A GENERATEALL probe succeeded, followed by the final runtime checks above. Across
debugging and final verification there were **13 Power BI query attempts** and
**two Azure LLM calls**, with zero Azure SQL calls. One attempted follow-up in the
original catalog was blocked before dispatch. Earlier uncertain receipts remain
held in their original local catalogs; they were not rewritten as completed, and
the final query used a separate verification catalog. This history is not a claim
that the remote completion of a timed-out request was established.

## Remaining work

The Phase D/H requirements still include controlled publication, binding source
and native evidence to a proven generation, effective report/context evidence,
and supported causal verifiers. The eight hidden/native acceptance families have
not passed. Hosted v2 authentication, onboarding and reviewed routing/handoff also
remain; the existing Azure deployment is unchanged.
