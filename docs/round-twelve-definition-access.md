# Round Twelve definition access ? 2026-10-10 UTC

The fixture report ID `692f3ead-d1d1-4f7f-984b-51e54f3e7497` is a Fabric Report item in workspace `149f8d99-1c66-4a0a-9624-759be002bb60`. The existing approved Contributor code reader listed that exact item (HTTP 200), submitted its definition request (HTTP 202), and retrieved the completed operation and result (HTTP 200 each): 13 definition parts. The same workspace/report route previously returned HTTP 404 `EntityNotFound` for the diagnostic reader. Wrong ID/type is ruled out; definition access differs by identity. No permission was changed.

Microsoft's [Get Report Definition contract](https://learn.microsoft.com/en-us/rest/api/fabric/report/items/get-report-definition) requires read and write permission on the report. Read-only report/page listing does not imply definition permission. Use existing approved code-reader or retained definitions for visual titles; diagnostic quantities stay on the diagnostic identities. The form must retain its optional visual field and refuse unresolved ambiguity.

The first local attempt dispatched zero requests because its Python environment lacked MSAL. The continuation dispatched four requests (two authentication controls, item listing, definition submission) and stopped at a regional operation URL rejected by the local URL guard. Its evidence is preserved. A separately recorded continuation authenticated again and read the operation/result, four requests. The returned regional URL was checked against its exact HTTPS host/path; access was made through the documented Fabric operation endpoint. No repeated definition submission was needed.

Private sealed receipts: `.local/round-twelve-definition-audit.json`, `.local/round-twelve-definition-audit-continuation.json`, `.local/round-twelve-definition-operation-result.json`. Ledger contains all three controls. Total eight physical requests, zero diagnostic reads, zero model calls. Pot 1,134 ? 1,142/1,500; restoration reserve 95 unchanged; rolling limit 3,000 unchanged.

## DECIDED WITHOUT REVIEW

Use the existing approved Contributor code identity for report definitions, not a broader diagnostic grant. Rejected treating the reader's concealed-resource 404 as proof that the report is absent. Definition access is metadata authority, not permission to use this principal for value probes.

## Sections 1?2 checkpoint

The sealed oracle remains unchanged: two consequential-field conflicts against it, zero if both requested figure amendments are approved. `docs/oracle-amendment-request.md` quotes both exact tickets and fields. Ten illegitimate question events across nine held-out tickets are classified in `docs/round-twelve-question-classification.md`. No universal fact was established that would justify a dev-only gate relaxation; no additional free-text held-out pass was run. Frozen free-text held-out settlement remains 17/28, 12 questions, ten illegitimate questions, and two consequential mismatches; quality gate remains FAILED.

Draft #423 continues. Copying owner-authored billing evidence does not create independent tester evidence. No expectations for the unplanned report rendering issues, no fixture change, no new credential/scope, no investigation run, prior freeze invalid.
