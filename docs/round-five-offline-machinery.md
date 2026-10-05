# Round Five D: offline machinery audit

2026-10-05 UTC. No live investigation runs. Prior freezes remain invalid.

## Section 1: previous acceptance failures

Most failures are fixture-state mismatches, not wording changes. Sentence equality caused answer/timestamp oracle defects, while outcome changes and failed composition remain real. A/G/I references originally failed synthesis: their mechanism outcomes are earned, successful dual outputs are not.

| Ticket | Failed invariant | Expected | Observed | Location |
| --- | --- | --- | --- | --- |
| family-A | CONTEXT_HASH_NOT_ESTABLISHED | {"context_id": "35461b1d-b5a4-48ef-a61d-aa539403a188", "hash": "8ac06cfb33b4a3a3b82e725f331c9af2885c436fdfc0dde7677b02c3e1379f0b"} | {"context_id": "e920dda4-d5c8-4a95-b9e9-a600386ae3d5", "hash": "baf3044545048d410b602ed8bec138e878d7d61da32490b364e42891db2beb2a"} | RUNNER: run used a different retained fixture state; not prose |
| family-A | CONTEXT_ID_CHANGED | {"context_id": "35461b1d-b5a4-48ef-a61d-aa539403a188", "hash": "8ac06cfb33b4a3a3b82e725f331c9af2885c436fdfc0dde7677b02c3e1379f0b"} | {"context_id": "e920dda4-d5c8-4a95-b9e9-a600386ae3d5", "hash": "baf3044545048d410b602ed8bec138e878d7d61da32490b364e42891db2beb2a"} | RUNNER: run used a different retained fixture state; not prose |
| family-A | technical_output:UNDECLARED_LAYER_ROLE | "Every compared layer has estate-declared role in receipt-backed payload" | "Checker reads assessment labels rather than full synthesis payload; must recheck actual role declarations" | CHECKER lookup; missing declarations remain estate/output limitation |
| family-B | CONTEXT_HASH_NOT_ESTABLISHED | {"context_id": "35461b1d-b5a4-48ef-a61d-aa539403a188", "hash": "8ac06cfb33b4a3a3b82e725f331c9af2885c436fdfc0dde7677b02c3e1379f0b"} | {"context_id": "e920dda4-d5c8-4a95-b9e9-a600386ae3d5", "hash": "baf3044545048d410b602ed8bec138e878d7d61da32490b364e42891db2beb2a"} | RUNNER: run used a different retained fixture state; not prose |
| family-B | CONTEXT_ID_CHANGED | {"context_id": "35461b1d-b5a4-48ef-a61d-aa539403a188", "hash": "8ac06cfb33b4a3a3b82e725f331c9af2885c436fdfc0dde7677b02c3e1379f0b"} | {"context_id": "e920dda4-d5c8-4a95-b9e9-a600386ae3d5", "hash": "baf3044545048d410b602ed8bec138e878d7d61da32490b364e42891db2beb2a"} | RUNNER: run used a different retained fixture state; not prose |
| family-C | CONTEXT_HASH_NOT_ESTABLISHED | {"context_id": "35461b1d-b5a4-48ef-a61d-aa539403a188", "hash": "8ac06cfb33b4a3a3b82e725f331c9af2885c436fdfc0dde7677b02c3e1379f0b"} | {"context_id": "e920dda4-d5c8-4a95-b9e9-a600386ae3d5", "hash": "baf3044545048d410b602ed8bec138e878d7d61da32490b364e42891db2beb2a"} | RUNNER: run used a different retained fixture state; not prose |
| family-C | CONTEXT_ID_CHANGED | {"context_id": "35461b1d-b5a4-48ef-a61d-aa539403a188", "hash": "8ac06cfb33b4a3a3b82e725f331c9af2885c436fdfc0dde7677b02c3e1379f0b"} | {"context_id": "e920dda4-d5c8-4a95-b9e9-a600386ae3d5", "hash": "baf3044545048d410b602ed8bec138e878d7d61da32490b364e42891db2beb2a"} | RUNNER: run used a different retained fixture state; not prose |
| family-D | BYTE_EXACT_REPLAY | "MATCHED" | "TAPE_UNRECORDED_IDENTITY:10543e9a-8a9e-4ac2-9596-e9cc127c209e" | TAPE: missing producer/input or unstable pre-canonical request |
| family-E | CONTEXT_HASH_NOT_ESTABLISHED | {"context_id": "35461b1d-b5a4-48ef-a61d-aa539403a188", "hash": "8ac06cfb33b4a3a3b82e725f331c9af2885c436fdfc0dde7677b02c3e1379f0b"} | {"context_id": "e920dda4-d5c8-4a95-b9e9-a600386ae3d5", "hash": "baf3044545048d410b602ed8bec138e878d7d61da32490b364e42891db2beb2a"} | RUNNER: run used a different retained fixture state; not prose |
| family-E | CONTEXT_ID_CHANGED | {"context_id": "35461b1d-b5a4-48ef-a61d-aa539403a188", "hash": "8ac06cfb33b4a3a3b82e725f331c9af2885c436fdfc0dde7677b02c3e1379f0b"} | {"context_id": "e920dda4-d5c8-4a95-b9e9-a600386ae3d5", "hash": "baf3044545048d410b602ed8bec138e878d7d61da32490b364e42891db2beb2a"} | RUNNER: run used a different retained fixture state; not prose |
| family-E | business_output:ANSWER_CHANGED | "Answer to your question: Not answered." | "Answer to your question: Partly answered." | CHECKER uses whole sentence; category change remains an OUTPUT defect if enums differ |
| family-E | technical_output:ANSWER_CHANGED | "Answer to your question: Not answered." | "Answer to your question: Partly answered." | CHECKER uses whole sentence; category change remains an OUTPUT defect if enums differ |
| family-E | technical_output:UNDECLARED_LAYER_ROLE | "Every compared layer has estate-declared role in receipt-backed payload" | "Checker reads assessment labels rather than full synthesis payload; must recheck actual role declarations" | CHECKER lookup; missing declarations remain estate/output limitation |
| family-F | CONTEXT_HASH_NOT_ESTABLISHED | {"context_id": "35461b1d-b5a4-48ef-a61d-aa539403a188", "hash": "8ac06cfb33b4a3a3b82e725f331c9af2885c436fdfc0dde7677b02c3e1379f0b"} | {"context_id": "e920dda4-d5c8-4a95-b9e9-a600386ae3d5", "hash": "baf3044545048d410b602ed8bec138e878d7d61da32490b364e42891db2beb2a"} | RUNNER: run used a different retained fixture state; not prose |
| family-F | CONTEXT_ID_CHANGED | {"context_id": "35461b1d-b5a4-48ef-a61d-aa539403a188", "hash": "8ac06cfb33b4a3a3b82e725f331c9af2885c436fdfc0dde7677b02c3e1379f0b"} | {"context_id": "e920dda4-d5c8-4a95-b9e9-a600386ae3d5", "hash": "baf3044545048d410b602ed8bec138e878d7d61da32490b364e42891db2beb2a"} | RUNNER: run used a different retained fixture state; not prose |
| family-F | business_output:MISSING_OUTPUT | "Both validated outputs" | "FAILED" | OUTPUT: failed composition |
| family-F | technical_output:MISSING_OUTPUT | "Both validated outputs" | "FAILED" | OUTPUT: failed composition |
| family-G | BYTE_EXACT_REPLAY | "MATCHED" | "TAPE_UNRECORDED_BUDGET_INPUT" | TAPE: missing producer/input or unstable pre-canonical request |
| family-H | BYTE_EXACT_REPLAY | "MATCHED" | "TAPE_UNRECORDED_BUDGET_INPUT" | TAPE: missing producer/input or unstable pre-canonical request |
| family-I | CONTEXT_HASH_NOT_ESTABLISHED | {"context_id": "35461b1d-b5a4-48ef-a61d-aa539403a188", "hash": "8ac06cfb33b4a3a3b82e725f331c9af2885c436fdfc0dde7677b02c3e1379f0b"} | {"context_id": "e920dda4-d5c8-4a95-b9e9-a600386ae3d5", "hash": "baf3044545048d410b602ed8bec138e878d7d61da32490b364e42891db2beb2a"} | RUNNER: run used a different retained fixture state; not prose |
| family-I | CONTEXT_ID_CHANGED | {"context_id": "35461b1d-b5a4-48ef-a61d-aa539403a188", "hash": "8ac06cfb33b4a3a3b82e725f331c9af2885c436fdfc0dde7677b02c3e1379f0b"} | {"context_id": "e920dda4-d5c8-4a95-b9e9-a600386ae3d5", "hash": "baf3044545048d410b602ed8bec138e878d7d61da32490b364e42891db2beb2a"} | RUNNER: run used a different retained fixture state; not prose |
| family-I | OUTCOME_CHANGED | "TRANSFORMATION_LOGIC" | "NO_KNOWN_PATTERN" | OUTPUT: changed structured outcome |
| reproduction-empty | BYTE_EXACT_REPLAY | "MATCHED" | "TAPE_EVENT_DIFFERS:BUDGET:PROVIDER_RESPONSE" | TAPE: missing producer/input or unstable pre-canonical request |
| source-consistent | OUTCOME_CHANGED | "CONSISTENT_TO_SOURCE" | "CONSISTENT_TO_BOUNDARY" | OUTPUT: changed structured outcome |
| source-consistent | business_output:ANSWER_CHANGED | "Answer to your question: Answered within the checked scope." | "Answer to your question: Partly answered." | CHECKER uses whole sentence; category change remains an OUTPUT defect if enums differ |
| source-consistent | technical_output:ANSWER_CHANGED | "Answer to your question: Answered within the checked scope." | "Answer to your question: Partly answered." | CHECKER uses whole sentence; category change remains an OUTPUT defect if enums differ |
| source-gap | CONTEXT_HASH_NOT_ESTABLISHED | {"context_id": "3693ce4e-ffcb-4cdb-b1e8-7662ebeea8ba", "hash": "54193af7ee9a2e905b154397dee7157e81767d40e6ec857248aab4f02421c394"} | {"context_id": "07662592-aecc-459e-be89-0c8bc9127ff4", "hash": "269c9abee2bec513eefb12a4dd63294c7eb36fde26dbd1cbfe29abf859e05b95"} | RUNNER: run used a different retained fixture state; not prose |
| source-gap | CONTEXT_ID_CHANGED | {"context_id": "3693ce4e-ffcb-4cdb-b1e8-7662ebeea8ba", "hash": "54193af7ee9a2e905b154397dee7157e81767d40e6ec857248aab4f02421c394"} | {"context_id": "07662592-aecc-459e-be89-0c8bc9127ff4", "hash": "269c9abee2bec513eefb12a4dd63294c7eb36fde26dbd1cbfe29abf859e05b95"} | RUNNER: run used a different retained fixture state; not prose |
| source-latency | CONTEXT_HASH_NOT_ESTABLISHED | {"context_id": "3693ce4e-ffcb-4cdb-b1e8-7662ebeea8ba", "hash": "54193af7ee9a2e905b154397dee7157e81767d40e6ec857248aab4f02421c394"} | {"context_id": "07662592-aecc-459e-be89-0c8bc9127ff4", "hash": "269c9abee2bec513eefb12a4dd63294c7eb36fde26dbd1cbfe29abf859e05b95"} | RUNNER: run used a different retained fixture state; not prose |
| source-latency | CONTEXT_ID_CHANGED | {"context_id": "3693ce4e-ffcb-4cdb-b1e8-7662ebeea8ba", "hash": "54193af7ee9a2e905b154397dee7157e81767d40e6ec857248aab4f02421c394"} | {"context_id": "07662592-aecc-459e-be89-0c8bc9127ff4", "hash": "269c9abee2bec513eefb12a4dd63294c7eb36fde26dbd1cbfe29abf859e05b95"} | RUNNER: run used a different retained fixture state; not prose |
| source-unreachable | CONTEXT_HASH_NOT_ESTABLISHED | {"context_id": "bfe54f5d-f23d-4084-8604-c58b580117ad", "hash": "b1cada4c48af05d0fdba00e83af10fdf70e8076993d8160ce175ee3df5d42431"} | {"context_id": "7f880fce-cc5b-4c60-826d-acf0a70ad796", "hash": "95aef64d1bce2cd9d93cd4c4aa51b9d5846eb93eafb687a4f9719a562dd37ed7"} | RUNNER: run used a different retained fixture state; not prose |
| source-unreachable | CONTEXT_ID_CHANGED | {"context_id": "bfe54f5d-f23d-4084-8604-c58b580117ad", "hash": "b1cada4c48af05d0fdba00e83af10fdf70e8076993d8160ce175ee3df5d42431"} | {"context_id": "7f880fce-cc5b-4c60-826d-acf0a70ad796", "hash": "95aef64d1bce2cd9d93cd4c4aa51b9d5846eb93eafb687a4f9719a562dd37ed7"} | RUNNER: run used a different retained fixture state; not prose |
| source-unreachable | business_output:MISSING_REQUIRED_TERM:2026-10-04T16:48:22.2386045Z | "2026-10-04T16:48:22.2386045Z" | "Different run has its own load timestamp; no obligation to repeat old timestamp" | ACCEPTANCE FILE: volatile timestamp embedded as prose oracle |
| source-unreachable | technical_output:MISSING_REQUIRED_TERM:2026-10-04T16:48:22.2386045Z | "2026-10-04T16:48:22.2386045Z" | "Different run has its own load timestamp; no obligation to repeat old timestamp" | ACCEPTANCE FILE: volatile timestamp embedded as prose oracle |

## Section 2: structured grading

Version 3 cases grade status, outcome (walk tickets), closed answer category,
resolution kinds, ordered boundary identities/equality/independence grades,
quantity-read execution surfaces reached, and the addressed reproduction verdict.
Reproduction tickets retain the walk label separately, as previously ruled.
The expected reference session is provenance, not the ID a future attempt must
reuse: ticket/model hashes and the immutable context pin identify the test.

No whole sentence or old load timestamp is an oracle. Prose checks retain
serialized-structure and identifier bans, one timing hedge, declared roles,
explicit provider-mechanism provenance and valid layer tokens. The answer header
must express the structured category (Yes/No/no verdict or answer coverage),
without requiring one exact sentence. Full receipt-backed synthesis labels are
used rather than a lossy assessment-only label lookup. Missing estate roles still
fail; they are not inferred from layer position or object names.

Nine checker tests pass: wording variation passes; changed outcome, answer
category, boundary grade or reached surface fails. Raw identifiers/serialization,
missing answer headers and unknown/incomplete contracts fail. A/G/I references
retain their original failed composition; no successful dual output is invented.

All fifteen were regraded from preserved zero-network recorded-era executions,
with explicit sealed provider fields, original receipts and full local payloads.
This is new grading of existing replay evidence, not fifteen replacement live
runs or newly claimed successful byte replays. The following column remains:

| Ticket | Replay | Structured acceptance / invariants |
| --- | --- | --- |
| family-A | MATCHED | CONTEXT_HASH_NOT_ESTABLISHED; CONTEXT_ID_CHANGED; STRUCTURE:resolutions; technical_output:UNDECLARED_LAYER_ROLE |
| family-B | MATCHED | CONTEXT_HASH_NOT_ESTABLISHED; CONTEXT_ID_CHANGED; STRUCTURE:resolutions |
| family-C | MATCHED | CONTEXT_HASH_NOT_ESTABLISHED; CONTEXT_ID_CHANGED; STRUCTURE:resolutions |
| family-D | FAILED | TAPE_UNRECORDED_IDENTITY:10543e9a-8a9e-4ac2-9596-e9cc127c209e |
| family-E | MATCHED | CONTEXT_HASH_NOT_ESTABLISHED; CONTEXT_ID_CHANGED; STRUCTURE:answer_category; STRUCTURE:resolutions; business_output:ANSWER_CATEGORY_CHANGED; technical_output:ANSWER_CATEGORY_CHANGED; technical_output:UNDECLARED_LAYER_ROLE |
| family-F | MATCHED | CONTEXT_HASH_NOT_ESTABLISHED; CONTEXT_ID_CHANGED; STRUCTURE:resolutions; business_output:MISSING_OUTPUT; technical_output:MISSING_OUTPUT |
| family-G | FAILED | TAPE_UNRECORDED_BUDGET_INPUT |
| family-H | FAILED | TAPE_UNRECORDED_BUDGET_INPUT |
| family-I | MATCHED | CONTEXT_HASH_NOT_ESTABLISHED; CONTEXT_ID_CHANGED; STRUCTURE:boundaries; STRUCTURE:layers_reached; STRUCTURE:outcome; STRUCTURE:resolutions |
| reproduction-16 | MATCHED | PASSED |
| reproduction-empty | FAILED | TAPE_EVENT_DIFFERS:BUDGET:PROVIDER_RESPONSE |
| source-consistent | MATCHED | STRUCTURE:answer_category; STRUCTURE:boundaries; STRUCTURE:outcome; business_output:ANSWER_CATEGORY_CHANGED; technical_output:ANSWER_CATEGORY_CHANGED |
| source-gap | MATCHED | CONTEXT_HASH_NOT_ESTABLISHED; CONTEXT_ID_CHANGED; STRUCTURE:answer_category; business_output:ANSWER_CATEGORY_CHANGED; technical_output:ANSWER_CATEGORY_CHANGED |
| source-latency | MATCHED | CONTEXT_HASH_NOT_ESTABLISHED; CONTEXT_ID_CHANGED |
| source-unreachable | MATCHED | CONTEXT_HASH_NOT_ESTABLISHED; CONTEXT_ID_CHANGED |

## Section 3: runner-owned context

PR #390 merged as 8675a6e after six green checks. select_store loads the acceptance
file directly and selects its retained context; an explicitly invoked successor
refuses before store/transport work, naming both IDs and hashes. Two runner tests
pass. Existing ModelStore tests prove hash checking and old-context selection
without altering the current catalog. Replays also check the sealed bootstrap's
actual context against the file: old tapes cannot be silently retargeted.
The former parallel manual pin map is not the input to this selector.

## Section 4: recording gaps

| Tape | Current validator / replay | Why omitted | Existing repair and exercised test |
| --- | --- | --- | --- |
| D | `TAPE_UNRECORDED_IDENTITY:10543e9a-8a9e-4ac2-9596-e9cc127c209e` | Report-selection UUID bypassed the recordable source; old validator did not conserve final identities | #381 common UUID producer and identity conservation; `test_report_selection_identity_replays_from_inventory_without_a_probe`, `test_final_cannot_introduce_unrecorded_identity` |
| G/H | `TAPE_UNRECORDED_BUDGET_INPUT` | Concurrent operator charges changed admission inputs without a recorded producer | #383 sealed external inputs; `test_external_budget_inputs_replay_without_repeating_other_work_or_replacing_own_decisions`, hostile-input rejection |
| EMPTY | Validator still validates its sealed event structure; first replay mismatch `TAPE_REQUEST_BYTES_DIFFER` at PROVIDER_REQUEST ordinal 2550 (later settlement masks it as `TAPE_EVENT_DIFFERS:BUDGET:PROVIDER_RESPONSE`) | Pre-#386 provider input used nested insertion order; equal decoded values do not mean equal request bytes | #386 canonical future serializer; new `test_canonical_nested_payload_records_validates_and_replays_byte_exactly` validates/replays reordered inputs and fails if canonicalisation is removed |

The tape contract existed when these ran, but its completeness validation and
producer coverage were insufficient. D predates the identity fix; G/H predate
external-input recording; EMPTY predates canonical request serialization.
None can be repaired by appending guessed missing historical evidence. D/G/H
need new authorised recordings; EMPTY already appears in the next live list.
Original tapes and their earlier VALIDATED labels remain untouched. Current
validator findings are separate annotations. Forty-three existing recorder,
planner, context and onboarding checks passed, plus the new canonical tape test.
Directory coverage stayed 2 entries / 1 SQL entry / 7,540 characters.

## Section 5: source tier and failed configuration attempt

No live investigation ran. Five metered control-plane requests occurred after
sections 1-4: one failed Fabric-tenant GET, then the existing Azure subscription
profile served GET, PATCH, async-status GET and after GET. No identity/scope change.
The first HTTP401 was InvalidAuthenticationTokenTenant (Fabric tenant versus Azure
subscription tenant); it is preserved rather than replaced by the later success.

Azure reports ordersops on sql-orderops-9696025 as GeneralPurpose Gen5 serverless,
2 maximum vCores, minCapacity 0.5, status Paused, autoPauseDelay 60,
useFreeLimit true, freeLimitExhaustionBehavior AutoPause.

The authorised exact PATCH was:

```json
{"properties":{"autoPauseDelay":-1}}
```

HTTP202 only accepted the operation. Its status GET returned HTTP200 with
status Failed and this exact error:

> ProvisioningDisabled: Only default value for auto pause delay is allowed for Free Limit database with auto pause exhaustion behavior

The fresh after GET still reports delay 60, minCapacity 0.5, free-limit true,
AutoPause and Paused. No configuration change succeeded. The initial ledger's
REQUESTED is request admission, not completion; a dated appended correction
records the asynchronous failure. No minimum increase, billing conversion or
free-limit removal was attempted. Increasing minimum serverless capacity alone
does not disable idle auto-pause. Switching to paid overage is outside this
bounded attempt and cannot be reverted to free-limit AutoPause, so it needs a
separate explicit decision, not an automatic fallback.

Cost: no incremental charge-bearing setting was applied. The current free offer
includes 100,000 vCore-seconds/month and pauses at exhaustion; paused compute is
not billed. Keeping a 0.5-vCore minimum awake would consume at least 1,800
vCore-seconds/hour (memory or load may raise that), exhausting that allowance in
at most about 55.6 hours without other usage. A paid conversion would require a
separate region-specific quote, not the example rate in documentation.
See [free-offer terms](https://learn.microsoft.com/en-us/azure/azure-sql/database/free-offer?view=azuresql)
and [serverless billing](https://learn.microsoft.com/en-us/azure/azure-sql/database/serverless-tier-billing?view=azuresql).

### OSError is not established as a connection failure

The earlier class-only receipt is `OSError`; no errno or message was retained.
It cannot honestly be expanded into a quoted socket error. The sealed worker
had already completed SQL permission and identity queries before requesting
quantity execution. Its event timeline is:

| Event | Ordinal | Seconds since worker start |
| --- | --- | --- |
| WORKER_START | 2780 | 0 |
| Database permission DONE / AVAILABLE | 2784 | 45.1 |
| Object permission DONE / AVAILABLE | 2802 | 56.7 |
| Identity DONE / AVAILABLE | 2825 | 76.5 |
| Quantity REQUEST | 2831 | 86.7 |
| Quantity ALLOW written to tape | 2844 | 99.4 |
| WORKER_END, returncode 1 | 2850 | 108.0 |

Read-CatalogAggregate sets stage query immediately after connection.Open; these
completed guards establish that connect succeeded for this worker. physical_reads
starts a 90-second Timer and its Pipe.write records WORKER_SEND before writing
to the child. ALLOW after 99.4 seconds is consistent with a closed pipe after
that timer. The timer firing and exact OS message were not separately retained,
so that causal attribution remains limited. No query result was established.
Serverless resume is a documented explanation for earlier SQL40613, not proof
that this particular OSError was a failed connect. [Microsoft documents first
resume attempts returning 40613](https://learn.microsoft.com/en-us/azure/azure-sql/database/serverless-tier-auto-pause-resume?view=azuresql).

The adapter propagates a generic OSError; it retries only stage connect with a
published numeric SQL error. A bounded transport retry would be appropriate
only for a positively classified connection-refused/connect-timeout failure,
with stage connect, safe OS/socket code, backoff and each attempt charged.
A generic OSError, worker pipe write, killed child, query timeout or uncertain
completion must not enter that rule. No retry widening or timer/deadline increase
was implemented. The current record cannot supply the missing classification.

## Stop before the live list

No EMPTY/I/source/D/G/H investigation rerun was started. The source's sleep
setting remains blocked by free-offer constraints, and its previous OSError
was after connect. Report now, before section 6, as requested. #376 stays draft;
no fresh freeze or unfamiliar-domain claim. README claims unchanged.

Round Five: 213 -> 218/400 (182 requests remain). Rolling last observed 580/1500;
its decreases reflect ordinary expiration, not refunds or resets. Diagnostic cap
12 unchanged. Offline grading used zero estate requests. Control-plane receipt
hashes and before/after state are retained privately and referenced in the ledger.


## Dated grading correction: 2026-10-05 UTC

The preceding Section 2 column is preserved as the first v3 grading. Its
`STRUCTURE:resolutions` flags were checker defects: entity binding `kind=REPORT`
was incorrectly treated as a resolution kind. Only an explicit `resolution_kind`
is now compared. An entity-type addition leaves the projection unchanged; changing
STATED to EVIDENCE still changes it. Ten checker tests pass. This correction
neither changes the expected outcomes nor retargets the tapes' context.

The corrected column below supersedes those flags. Fifteen new zero-request
grading rows were appended; the earlier rows and original run evidence remain.
The result remains 11/15 replayable and 1/15 accepted. #376 stays draft.

| Ticket | Replay | Corrected structured acceptance / invariants |
| --- | --- | --- |
| family-A | MATCHED | CONTEXT_HASH_NOT_ESTABLISHED; CONTEXT_ID_CHANGED; technical_output:UNDECLARED_LAYER_ROLE |
| family-B | MATCHED | CONTEXT_HASH_NOT_ESTABLISHED; CONTEXT_ID_CHANGED |
| family-C | MATCHED | CONTEXT_HASH_NOT_ESTABLISHED; CONTEXT_ID_CHANGED |
| family-D | FAILED | TAPE_UNRECORDED_IDENTITY:10543e9a-8a9e-4ac2-9596-e9cc127c209e |
| family-E | MATCHED | CONTEXT_HASH_NOT_ESTABLISHED; CONTEXT_ID_CHANGED; STRUCTURE:answer_category; business_output:ANSWER_CATEGORY_CHANGED; technical_output:ANSWER_CATEGORY_CHANGED; technical_output:UNDECLARED_LAYER_ROLE |
| family-F | MATCHED | CONTEXT_HASH_NOT_ESTABLISHED; CONTEXT_ID_CHANGED; business_output:MISSING_OUTPUT; technical_output:MISSING_OUTPUT |
| family-G | FAILED | TAPE_UNRECORDED_BUDGET_INPUT |
| family-H | FAILED | TAPE_UNRECORDED_BUDGET_INPUT |
| family-I | MATCHED | CONTEXT_HASH_NOT_ESTABLISHED; CONTEXT_ID_CHANGED; STRUCTURE:boundaries; STRUCTURE:layers_reached; STRUCTURE:outcome |
| reproduction-16 | MATCHED | PASSED |
| reproduction-empty | FAILED | TAPE_EVENT_DIFFERS:BUDGET:PROVIDER_RESPONSE |
| source-consistent | MATCHED | STRUCTURE:answer_category; STRUCTURE:boundaries; STRUCTURE:outcome; business_output:ANSWER_CATEGORY_CHANGED; technical_output:ANSWER_CATEGORY_CHANGED |
| source-gap | MATCHED | CONTEXT_HASH_NOT_ESTABLISHED; CONTEXT_ID_CHANGED; STRUCTURE:answer_category; business_output:ANSWER_CATEGORY_CHANGED; technical_output:ANSWER_CATEGORY_CHANGED |
| source-latency | MATCHED | CONTEXT_HASH_NOT_ESTABLISHED; CONTEXT_ID_CHANGED |
| source-unreachable | MATCHED | CONTEXT_HASH_NOT_ESTABLISHED; CONTEXT_ID_CHANGED |
