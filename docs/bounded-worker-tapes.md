# Round Five Part A: bounded-worker replay

2026-10-04. Human decision: Option 1, byte-exact bounded worker responses and
provider bodies; unchanged retention. No estate run or cloud request in this PR.
Prior engine freezes are invalidated by these recording changes.

Replay reproduces engine decisions and both outputs from recorded worker responses;
it does not re-exercise upstream decoding. This is not full upstream replay.
Upstream decoding is covered separately by synthetic raw-input tests, never by
retained estate HTTP responses, Delta logs, credentials or service error prose.

## Tape contract

`bounded-worker-tape-v1` is a private, sealed, ordered journal. Each event carries
an ordinal, kind, timestamp, exact body bytes in base64 and a SHA-256 integrity
check. The outer seal binds the event order. Bootstrap pins the engine hash,
retained context identity, environment, configuration, planner profile, usage
policy, workspace owner and both SQLite backups by content hash. An estate without
a discovered context pins its actual catalog backup hash, not a placeholder ID.

Public intake, preview, creation, investigation and synthesis operations share one
tape. It retains worker requests/responses, physical REQUEST/DONE and ALLOW/REUSE
exchanges, provider request/response bodies and failures, clocks and generated
identities, configuration snapshots, budget admission/settlement, and final results.
Recorded authentication state has no credentials; request tokens are excluded and
credential-sensitive guard-cache keys use opaque per-tape labels. Existing planner
recordings remain available. The older adaptive path retains its existing harness.

Validation rejects missing bootstrap fields/artifact seals, unknown event kinds,
changed bytes/order, unmatched operation/worker/provider boundaries, secret-excluded
bodies, unfinished attempts, and completed results missing either narrative.
Interrupted attempts remain private artifacts and cannot pass as complete tapes.
The replay copies bootstrap databases into a disposable directory, re-executes the
real procedure and validation, intercepts bounded worker/provider boundaries and
blocks sockets. It never uses stored outputs as a substitute for execution: the
recomputed final result, including both outputs, must byte-match the sealed final.

## Decoder coverage outside replay

| Decoder / projection | Committed synthetic raw-input tests |
| --- | --- |
| OneLake listing and latest Delta commit JSON-lines projection | `test_read_onelake_commit.py`: two synthetic HTTP responses; allowlisted commit fields, missing/malformed/oversized logs |
| Physical SQL guard acknowledgement | `test_tape_decoders.py`: positive/negative/missing guard result, wrong request kind, safe unavailable response; `test_read_budget.py`: real synthetic worker pipe, guard reuse, failed guards, mandatory admission |
| Metadata HTTP JSON and bounded API responses | `test_tape_decoders.py`: synthetic response bytes including null, empty and invalid JSON; `test_metadata_connectors.py` |
| Native value/identity response projection and safe DAX rejection | `test_reader_execution.py`: synthetic response bytes, exact decimals and BLANK, bound principal and malformed responses; `test_tape_decoders.py` / `test_native_rejection.py`: synthetic error bodies |
| Application and Fabric SQL row/surface projection | `test_application_quantity.py`, `test_surface_self_report.py`: synthetic worker rows and self-reports, missing guards/report, wrong engine |
| XMLA failure detail code projection | `test_tape_decoders.py`, `test_specific_failure.py`: synthetic message/code bodies; no service message retention |
| Optional refresh history and snapshot metadata projection | `test_refresh_comparison.py` and `test_snapshot_attestation.py`: synthetic HTTP/worker responses and token claims, distinct identity, no query-bound snapshot invention |
| Retained job history / load accounting projection | `test_retained_job_history.py`, `test_load_accounting_rows.py`, `test_source_delivery.py`: synthetic statuses, timestamps, nested activity-output counters and invalid rows |

The XMLA failure-detail request previously escaped the physical meter. It now
consumes an overhead request slot, leaving the diagnostic cap unchanged. This can
increase honest request totals for a failing probe; it does not grant extra work.

## Verification and context cost

The synthetic test traverses actual intake, preview, procedure execution and
synthesis through the provider SDK, then replays with sockets blocked and requires
both rendered outputs to match. A separate real subprocess protocol test records
every synthetic request and guard reuse, removes the worker, and replays without
launching it. Hostile tests cover changed requests/outputs, unknown bootstrap fields,
unfinished workers and secret exclusion.

Recording is outside the planner payload. The golden-view comparison is unchanged:
2 directory entries, 1 SQL-object entry, 7,540 payload characters before and after.
The test asserts the entire payload is identical, so no directory coverage is lost.
This is synthetic verification, not evidence that the fifteen estate tapes pass.
Part B must re-record and replay those attempts before the acceptance gate can merge.
The three already documented baseline test defects remain assigned to Part D.
