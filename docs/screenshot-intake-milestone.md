> Release-specific implementation/runbook. Its old roadmap and next-step statements
> are historical. [Current status](current-delivery-status.md) and the
> [discovery-first plan](architecture/README.md) govern new work.

# Reviewed report screenshot intake

Review: [PR #190](https://github.com/bcsnpc/data-investigation-agent/pull/190).

PR #188 is merged. This milestone is tracked by [#189](https://github.com/bcsnpc/data-investigation-agent/issues/189).

A business user can attach a PNG or JPEG, explicitly request an AI transcription,
correct the visible metric/value/filter text, and confirm it. The existing catalog
resolver then suggests a scope. A separate scope review and Start action are still
required before the adaptive investigator can query data. Saved results show the
user-provided screenshot and reviewed text separately from native observations.

## Implementation

- Authenticated loopback upload/content/history/removal APIs, with no remote image URL fetching.
- Exact original bytes are decoded and checked using pinned Pillow 12.3.0: at most
  1 MiB, one PNG/JPEG frame, 5,000 pixels per dimension and 8 million pixels total.
  Stored active image content is capped at 25 MiB per local workspace database.
- Explicit Azure vision transcription uses the existing configured deployment,
  structured output, a 45-second provider timeout, no SDK retries and `store=false`.
  Vision shares the durable planner allowance; encoded input characters and output
  reservations are recorded. These allowances do not certify provider-wide spend.
- Uploads, reads and reviews have immutable hashed records and request keys.
  Interrupted or uncertain reads remain held/reserved; checking status never resends
  the image. An explicit hold fences a late result. Reattaching permits a new request.
- Only a saved, confirmed transcription enters question resolution. Clarifications
  inherit its provenance. Changing extracted text invalidates confirmation.
- Image content is available only through authenticated requests. Browser object URLs
  are cleared on reset/sign-out; image data is not embedded in JSON exports.
- Removing stored image content preserves earlier transcriptions, questions and
  investigations. This is logical removal, not certified secure erasure of SQLite,
  filesystem backups, browser internals or provider retention.

Install the workspace dependency before running the local host:

```powershell
python -m pip install -r scripts/requirements-workspace.txt
```

The existing `serve_investigator_workspace.py --live` configuration enables vision
alongside question intake. It uses the same Azure deployment and explicit usage
policy. No additional endpoint, credentials, SQL changes or cloud deployment are
introduced. Responses image transport follows the [official vision input
documentation](https://developers.openai.com/api/docs/guides/images-vision).

## Verification and limits

All **844 regression tests** passed, including **22 screenshot tests**. Coverage
includes corrupt/oversized/animated input, MIME mismatch, storage and integrity,
request replay, interrupted/late responses, authenticated binary access, reviewed
scope provenance and the inline-image SDK request.

All **26 browser checks** passed, including the full screenshot-to-reviewed-scope
flow, separate input/queried values, no-call image history, removal preserving the
question, mobile layout and sign-out. The harness uses injected responses; its
results are saved in `.local/screenshot-workspace-browser.json` with review/result
captures. Browser checks do not replace the independent live verification below.

A real Azure run used a browser-rendered **controlled report-style card**, explicitly
not an actual Power BI screenshot. Its visible input was `Base cb5bda`,
`Refunded: false`, no date restriction and displayed value **9**. The operator
confirmed that text; the real catalog resolver proposed the matching fixture measure
and Boolean filter. The adaptive runtime returned native value **8** using the
dedicated investigator reader. Calls: one vision, one resolver, one adaptive planner
and one Power BI query; zero Azure SQL calls. Saved replay added zero provider calls.
Local artifacts: `.local/screenshot-intake-live.json`, its separate SQLite database,
and `.local/screenshot-live-input.png`; generated artifacts are not committed.

The controlled card checks the integration, not report rendering accuracy or OCR
generality. Visible values remain claims, and human review does not prove hidden
filters, effective report/RLS identity, semantic equivalence, shared generation or
root cause. The runtime still reports `cause_verified=false`. This advances Phase I;
it does not close Phase H or the remaining B-G acceptance gates.

## Next grouped work

1. Establish effective report/context and shared-generation evidence, enforce the
   isolated publication boundary, and complete supported causal verifiers.
2. Run all eight frozen native acceptance families with hidden measures and healthy,
   defect and insufficient-evidence cases.
3. Deliver hosted v2 authentication, onboarding, reviewed routing/handoff and an
   actual Power BI screenshot demonstration. The older Azure deployment is unchanged;
   this workspace remains local and single-operator.
