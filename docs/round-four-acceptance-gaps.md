# Round Four acceptance roster and replay gaps

The strict implementation and declarative files are in draft [PR #376](https://github.com/bcsnpc/data-investigation-agent/pull/376),
not on main. This evidence record does not install or claim that gate passed.

2026-10-04. The requested roster is **15**, not 13: nine families, EMPTY and 16,
four source scenarios. All are retained as separate declarative files under
acceptance/known_domain/cases. Expectations state outcome, execution status,
answer line and mandatory output invariants. Initial expectations use reviewed
evidence and subject coverage; they are not transcribed from this checker.
Preserved failures do not acquire invented successful outcomes.

Fifteen offline attempts invoked the existing session replay harness with socket
connect/create_connection blocked and no provider/estate request. Each attempt has
one appended ledger row. **0 passed, 15 blocked**. Original receipts, recordings,
catalogs and prior ledger lines are unchanged. No request-byte match was reached,
so this is not a successful replay or an acceptance pass.

| Ticket | Expected outcome | Expected answer | Actual replay stop |
|---|---|---|---|
| A | TRANSFORMATION_LOGIC | Partly answered | MISSING_RESPONSE_OR_RUNTIME_TIMING |
| B | NO_KNOWN_PATTERN | Not answered | INCOMPLETE_SESSION_RECORDINGS |
| C | no classification, HELD | Not answered | INCOMPLETE_SESSION_RECORDINGS |
| D | NO_COMPARABLE_PATH | No verdict: no figure supplied | INCOMPLETE_SESSION_RECORDINGS |
| E | TRANSFORMATION_LOGIC | Not answered | MISSING_RESPONSE_OR_RUNTIME_TIMING |
| F | CONSISTENT_TO_BOUNDARY | Partly answered | INCOMPLETE_SESSION_RECORDINGS |
| G | TRANSFORMATION_LOGIC | Partly answered | MISSING_RESPONSE_OR_RUNTIME_TIMING |
| H | NO_KNOWN_PATTERN | Not answered | INCOMPLETE_SESSION_RECORDINGS |
| I | TRANSFORMATION_LOGIC | Not answered | MISSING_RESPONSE_OR_RUNTIME_TIMING |
| EMPTY | NO_COMPARABLE_PATH; reproduction Yes | Yes, qualified saved context | INCOMPLETE_SESSION_RECORDINGS |
| 16 | no classification, HELD; reproduction Yes | Yes, qualified saved context | INCOMPLETE_SESSION_RECORDINGS |
| source gap | INGESTION_GAP | Answered within checked scope | INCOMPLETE_SESSION_RECORDINGS |
| source latency | LOAD_LATENCY | Partly answered | INCOMPLETE_SESSION_RECORDINGS |
| source consistency | CONSISTENT_TO_SOURCE | Answered within checked scope | INCOMPLETE_SESSION_RECORDINGS |
| unreachable source | CONSISTENT_TO_BOUNDARY | Partly answered | INCOMPLETE_SESSION_RECORDINGS |

The nine-family sources are the corrected autonomous batch from #335, with failed
synthesis preserved. EMPTY uses retained d831c404 evidence; 16 uses 46826851 and
its subsequent deterministic composition evidence. Source gap/latency use Round
Three; source consistency/unreachable use Round Four. The original first Round
Four source-read failure remains separately recorded, not replaced by its follow-up.

The harness starts at a recorded adaptive planning call, requires request/response
and runtime timing, then a full state/profile/config bootstrap. Process debugging
uses zero investigation-planner calls. A/E/G/I have judgment recordings under their
session IDs, but those are not adaptive-runtime bootstrap tapes and fail the earlier
timing requirement. The other eleven have no qualifying runtime recordings.
Separate synthesis recordings do not fill that missing start-of-run contract.
The existing harness also refuses unrecorded tool reads; an end-to-end process
replay needs faithful receipt-backed transports for those reads and intake/judge/
synthesis request replay, not a fabricated planner response.

Changing A1/A3 changes provider request shapes. Old tapes must not be rewritten
to byte-match new requests. Neither canonical outputs nor a copied final state
is substituted for actual replay. Before a green gate is possible, capture/export
needs a process-runtime bootstrap, complete metered tool requests/results, original
provider exchanges and retained context. Private .local run artifacts must not be
committed; CI needs an approved protected replay bundle. None was uploaded here.

The new pull-request-only workflow supplies the requested additional check. It
fails if any ticket is blocked, has changed outcome/answer, lacks either output,
contains serialized output or identifier-form business prose, repeats its timing
hedge, or uses an invalid mechanism layer reference. Unknown invariant names and
unexplained acceptance edits fail closed. Four checker regression tests passed.
CI has no private replay bundle and must report MISSING_PRIVATE_REPLAY_INPUTS;
this PR remains draft and unmerged rather than installing a knowingly red main.
The current source-consistency business output would additionally fail the
once-only timing invariant; its original duplicate wording is preserved.

No engine/adapter behavior, estate, scope, budget or configuration changed in this
work item. A new test file changes the covered fingerprint; prior freezes remain
invalid. No further live measurements were performed to fill the gaps. Round Four
physical use remains 51/300, rolling last observed 641/1000, diagnostic cap 12.
