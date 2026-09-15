# Capability decisions and diagnostic evidence

This grouped Phase D/E continuation follows merged PR #152 and is tracked by [#153](https://github.com/bcsnpc/data-investigation-agent/issues/153).

## Implemented behavior

`investigator/capabilities.py` publishes a versioned, hashed decision for every retained measure. It separates definition availability, query admission, observed execution, dependency discovery, effective dependency context, visual replay, upstream reconciliation, source provenance and cause verification. The evaluator reads catalog IDs and operations; it does not dispatch on metric names or evaluate DAX.

An enabled catalog can admit a validated native plan while dependency analysis remains partial. A clean dependency graph still does not certify inherited filters, date roles or relationship semantics. Metadata alone leaves native execution UNKNOWN. Upstream reconciliation and causal verification are UNSUPPORTED in this v2 registry until adapters/verifiers exist; provenance and visual replay remain UNKNOWN.

Dry-run assessment compiles the same bounded plan used by native execution. It pins context, revision, scope, request and evaluator version, and returns the discovered dependency gaps. A native run saves this decision atomically with its RUNNING receipt before calling the transport. Successful execution does not change its verification eligibility.

`investigator/diagnostic_evidence.py` lists up to the latest 100 receipts and reads a receipt only through its owning model/environment. The saved admission hash and request binding are checked. Old receipts without admission records remain readable with admission explicitly absent. This is local database integrity checking, not a cryptographic signature against a database administrator.

Evidence assessment recompiles the historical request against the current model. Disablement or context changes preserve the historical values but make current-context evidence UNKNOWN. A complete successful response is SUPPORTED **only as a historical native execution observation for that exact request**; truncated results remain PARTIAL. Timeouts are TEMPORARILY_UNAVAILABLE; other errors remain UNKNOWN rather than proving that a measure is unsupported. No response guarantees a future execution or verifies a cause.

## Admin API

These routes use the existing admin token and model/environment boundary:

| Method/path suffix under `/api/v2/admin/models/{id}` | Result |
| --- | --- |
| `GET /capabilities` | Versioned per-measure capability projection |
| `POST /assess` | Dry-run admission for the native plan JSON; no query |
| `GET /diagnostics` | Latest 100 receipt summaries |
| `GET /diagnostics/{receipt_id}` | Historical result, saved admission and current assessment |

Reader credentials cannot access these admin routes. These additions do not expose query execution over HTTP or claim that the v2 ticket workflow is enabled. No new browser controls are included in this slice.

## Verification and remaining work

The full regression suite passed: **407 tests**. Ten focused tests cover capability boundaries, context/hash changes, rejected plans, pre-dispatch persistence, environment/model ownership, stale evidence, partial results, timeout state, old receipts, integrity checks and API role separation. The native diagnostic regression suite covers the execution path. Existing retained live evidence was read successfully for all 25 catalog measures and both historical diagnostic receipts, without new cloud or LLM requests.

Full effective-context certification, authoritative upstream equivalents, source-generation proof, durable reservations/recovery, adaptive planning and the eight frozen-engine acceptance families remain open. B/C/D/E are implementation slices, not completed phases. The current evaluator is conservative and does not provide the full Phase E semantic equivalence engine.
