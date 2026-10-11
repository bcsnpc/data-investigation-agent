# Repeated tool results

Owner steering, 2026-10-11: identical tool calls return a short already-obtained note and the original evidence IDs, without executing again.

The loop records `TOOL_REUSED`, its arguments, the original receipt and evidence IDs. It does not call the handler or reserve another tool/read operation. Model steps still count. Results remain complete in the original transcript and delivery validator; reuse cannot replace, rebind or upgrade evidence. Argument key order is immaterial; any changed argument is a different call. Repeated `get_evidence` also returns the note after the first full fetch.

DECIDED WITHOUT REVIEW: a `NOT_ADMITTED` response is not cached. It describes the absence of admitted authority, not the tool's result; treating it as the admitted result would prevent legitimate execution after intake settles. All established results, including unavailable evidence, are reused within this run. Failed calls and unknown evidence IDs remain refusals rather than cached success. Cache lifetime is one loop, never another ticket or run.

The implementation was prepared in a separate worktree while attempt A7 continued on its unchanged source pin. No investigation or estate read was made for this change. Existing tapes and acceptance expectations are untouched. The current freeze is invalidated; draft #423 remains draft, and pipeline remains the default.

Verification covers one handler invocation/read admission on a repeat, original evidence identity, canonical argument ordering, changed arguments, pre-admission retry and repeated full-detail fetch. Omitting empty identifier descriptions also restores the existing 32,000-character initial-request regression without changing its ceiling; populated identifiers remain supplied exactly.

The earlier full regression's three local-factory test errors came from a fake local adapter without an exported bundle. Those factory tests now double only the separately tested bundle-approval boundary; production approval, candidate and budget checks are unchanged.
