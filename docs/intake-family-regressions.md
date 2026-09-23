# Nine-family intake regressions

2026-09-23. Ordered reliability item 7, issue #199.

The fixed fixture contains twelve synthetic offline captures through the actual
intake SDK adapter: nine business-ticket families and three material-clarification
cases. Requests, catalog payloads, structured provider responses and decoded
scopes are asserted together. These are mock-provider captures, not historical
live model decisions. No investigator prompt, production mapping or runtime
behavior changed for this item. Fixture expectations and family labels remain
outside the investigator.

All A?I fixtures proceed to proposed scope without asking for a definition, refresh
pipeline or business-rule confirmation as an intake prerequisite. Separate tests
use the actual discovered catalog, scope review, workspace start, governed runtime
and mock native reader. Each family reaches a read of its selected measure. The
synthetic planner subsequently requests business intent; this is not nine solved
business investigations. The original user question remains intact for subsequent
investigation, including unknown code meaning and missing runtime visual context.

| Clarification case | Specific fact | Why metadata cannot provide it |
| --- | --- | --- |
| Selected reporting period | User's exact start/end dates | Data date ranges do not identify the user's unprovided selection. |
| Highlighted visual | Active filters/selections | Static model/report metadata does not capture this user's current runtime selections. |
| Unidentified report | Which of two reports the user meant | Catalog enumeration shows both; it does not identify the user's choice. |

The fixture grader rejects injected metadata-confirmation ASK responses for all
nine proceed cases. It also rejects a vague question in a material case and an
ASK when the required user fact is already supplied. This is a fixed-case rubric,
not a general natural-language semantic judge. Runtime security/provider/staleness
holds remain distinct operational failures, not fabricated missing business facts.
A future live model can still choose an unnecessary ASK; these fixtures do not
prove it will not. The full live acceptance matrix remains required.

## Verification and retained failures

Four tests passed in 13.977 seconds, covering twelve request/response roundtrips,
nine reviewed starts/reads and negative grading probes. The committed JSON is a
synthetic test fixture containing no live business data or credentials. Historical
recordings, failed runs and frozen artifacts were not modified.

The first fixture-capture script had recording disabled, so its MockTransport
injection was not used by the SDK. DNS resolution of the dummy offline hostname
failed before any provider request succeeded. It used a placeholder credential,
not a live endpoint or key. This failed setup is retained in the ledger. The
corrected capture and all tests explicitly block both DNS and socket connection
and use MockTransport. Twelve corrected captures completed with zero network calls.

A retained nine-case flow proof passed in 12.640 seconds and is stored at
`.local/intake-family-proof-c232b36b-0bc3-45c6-9c7a-a6a9cc04204c/`.
Its nine ledger rows record actual investigation counters: two injected planner
calls and one mock native read per case. Intake resolver capture is separate from
these investigation counters. Per-session wall time is the fixed test clock (zero),
not a measured production latency. Validation-suite rows do not aggregate fixture
sessions. The full regression suite and CI remain pending.

PR #214 merged at 97d7572cd7f8d1faae9ec766fde5466971bb200d after six green checks.
This item adds offline acceptance coverage, with no new investigator engine bytes.
V4 remains invalidated by earlier changes; no live investigation/tape, freeze or
variant is permitted yet. Item 8 is a separate operator capacity report. Raising
provider capacity requires approval; SQL/free-tier settings remain unchanged.

Final local verification: **1,003 regression tests passed in 231.426 seconds**.
Final CI/merge remain pending. This adds a repeatable intake admission gate; it
neither changes live model behavior nor passes the unknown-domain challenge.
