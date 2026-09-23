# Planner call recordings — offline reliability item 1

Date: 2026-09-22. Tracking: #199. No unfamiliar-domain acceptance claim.

The previous runtime saved projected-payload hashes and numeric usage, which could
not reconstruct the actual request after wire-handle conversion. An operator can
now enable local capture with `INVESTIGATOR_RECORD_PLANNER=1` before starting the
existing investigator command. Unset it to restore default content-free operation.
Install the existing pinned `scripts/requirements-llm.txt` dependency first.

Each call gets a new directory under `.local/planner-recordings/` containing:

- `context.json`: session/call identifiers, context version, projected payload,
  state excluding the runtime fencing token, budget snapshot and reservation.
- `request.body`: exact SDK-serialized HTTP entity bytes, including instructions,
  wire input, schema and generation settings. Headers and credentials are excluded.
- `response.body`: raw decoded HTTP entity bytes before SDK/provider validation,
  including malformed responses and HTTP error bodies.
- `response-status.json`: numeric HTTP status only.
- `manifest.json`: byte lengths, SHA-256 hashes, safe error category and explicit
  capture/exclusion indicators. Exclusive file creation preserves previous calls.

This captures submitted request bodies, not proof that the remote model received
a request after a connection failure. Compression framing, HTTP headers and TLS
bytes are not model input and are not recorded. Missing responses remain explicitly
missing. Known credential values from process environment and common credential
patterns cause capture to fail closed, rather than silently redact an allegedly
exact fixture. A detected response credential is withheld and marked as excluded.
Pattern detection is not a guarantee against arbitrary secrets in business text;
use approved secret-free context. The opt-in files contain investigation data and
must remain local. Default receipts still contain only safe error/usage information.

Runtime sessions supply the full budget and context metadata. The existing single
proposal replay evaluator supplies its reservation. Standalone `azure_plan` calls
without a runtime context explicitly record unknown budget/context as null; these
are not sufficient full-session replay fixtures.

Load a recorded session without network calls:

```python
from investigator.planner_recording import load_session
calls = load_session(session_id)
request_bytes = calls[0]['bodies']['request.body']
response_bytes = calls[0]['bodies'].get('response.body')
state = calls[0]['context'].get('state')
```

The loader verifies lengths/hashes and rejects incomplete or modified fixtures.
It does not execute an investigation: full offline simulation is item 3. Context
golden tests, proposal repairs, redundancy and new budgets are not included here.

## Verification

Initial offline suites passed seven and then eight focused tests. They compare
captured bytes with actual mock-transport bytes, retain a 429 body with one attempt,
block credential-bearing requests before transport, withhold credential-bearing
responses, exercise default-off behavior and verify fixture integrity. A complete
runtime STOP session verifies the saved context version, charged reservation and
pre-response session state. No Azure, SQL, Power BI or paid LLM call was made.
The final full regression passed 959 tests (293.456 seconds). Focused validation passed ten
recording tests and 31 runtime-governance tests, including timeout capture,
standalone-call capture and zero metadata collection when the flag is disabled.
PowerShell syntax, six portal tests and the production build passed. Six CI checks
passed on the implementation head; PR #209 records final-head checks and merge state.

An additional retained offline investigation, session
`d883f3f6-fac2-4b8f-bcac-4e1482e46820`, completed two mocked planner calls and one
mocked native read. Both request/response pairs matched transport bytes exactly;
the loader recovered them without network calls. It reserved 3,000 output tokens
and recorded 3,598 cumulative input characters. Its INSUFFICIENT_EVIDENCE outcome
is deliberately NOT_GRADED: this checks recording, not investigation quality.
The local summary is `.local/recording-offline-proof.json`.

Ledger scope: the first two rows describe focused test-suite invocations, not live
trials. Their zero input count means fixture input telemetry was not aggregated;
it must not be interpreted as empty prompts. The retained session row has measured
input/reservation counts. Its manifest-short field identifies the unfrozen engine
fingerprint, not an acceptance freeze. These initial limitations are preserved
instead of rewriting ledger history. HTTP-failure cases in unit tests are synthetic
and are not counted as live provider outages.

The [official SDK overview](https://developers.openai.com/api/docs/libraries) was
consulted; integration is verified against the repository's pinned Python SDK with
a mock HTTP transport. It does not require a new agent framework.

## Freeze and remaining work

These engine changes invalidate v4 for further frozen grading. Frozen manifests,
stored receipts and historical run evidence were not rewritten. After items 1–8
pass, create one new freeze and one fresh variant for the nine-family matrix.
