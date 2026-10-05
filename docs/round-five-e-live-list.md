# Round Five E: controls, stopped live list and current-engine gate

Recorded 2026-10-05 UTC. Known-domain regressions only. No acceptance pass.

## Implementation and prior evidence

[PR #393](https://github.com/bcsnpc/data-investigation-agent/pull/393) merged as
`7abaabf37812b58cc74b684de9cafc172212c1ad` after all six checks passed.
It retains safe OS error type/message/errno/location, sealed worker failures and
actual deadline expiry; declared-serverless connect-stage 40613 has bounded
resume backoff, with each attempt admitted and receipted. Pre-warm connections
and resume waits are controls, not diagnostic reads. Layer deadlines are manifest
values; the fixture application uses 240 seconds instead of the old 90 seconds.
See [implementation, tests and documented limits](serverless-source-controls.md).
No arbitrary-error retry, permission change, billing conversion or cap increase.
Prior freezes remain invalidated by the engine changes.

The historical application OSError followed successful guards. Its missing message
and errno remain unknown; old worker elapsed time does not prove a timer expiry.
The authorised disable-auto-pause request failed ProvisioningDisabled; free-limit
AutoPause remains unchanged. New handling does not rewrite that failure.

The first broad local run executed 1,849 tests but failed (two failures, eight
errors). Old transport test doubles were corrected and focused suites passed;
one combined-suite intake retry failure passed in isolation. Six CI checks passed
on the corrected implementation. Do not interpret this as a passing broad local
1,849-test run. Golden coverage stayed two entries, one SQL object, 7,540 characters.

The earlier fixture-state work in #392 replaces context-ID grading because a
recollection mints a new ID without changing the independently declared data state.
Original estate roles are explicitly declared. E and source-gap answer-category
expectations were updated with dated #372 attribution; their outcomes were not
changed. Independent arithmetic remains evaluator-only, never runtime truth.
Historical associations and sealed recordings are unchanged.

## Retained-metadata policy approval, not a fresh rescan

The manifest change required current whole-file policy approval. An explicitly
labelled EXACT_RETAINED_METADATA_POLICY_REAPPROVAL reused the prior complete scan
`9e732b6c-74dd-47fb-9b6c-b3c5fac840e8`; it made zero metadata cloud reads and
establishes no fresh remote inventory. New scan
`785a8fea-f49c-4e7e-b48f-1cae765410dc` is complete; the original estate remains the
unchanged seeded inventory-baseline state, as separately declared and approved.

- Previous policy hash: `ee6066720fe687e5c46daa03e951b73efb035fbbcf9b74b68ef9833163d182c7`.
- Current whole-config hash: `56dfa9aeab17f133b68ddfcc3761cf50d529eefdd10d4c3bfa22657fa73cf821`.
- Manifest hash: `8a4aeb47b1831bacb707a2034fb3e3e3394cc8978233a8976795e95e11d7e32b`.
- Context: `71a3817e-5513-4d21-a9fb-df6ee906998a`.
- Context hash: `eca22ae885549d766a8dd6ff7b2dcb476cb235a5640386feb18a8c3409d6f88d`.

No context ID was used to infer fixture state. Approval evidence and the complete
configuration remain private under `.local/round-five-e-live-20261005/`.

## Pre-warm control and budgets

As existing `orderops_investigator`, connection-only pre-warm began
2026-10-05T03:19:08.621929Z. Attempt one returned connect-stage 40613 at
03:19:54.565531Z. A five-second resume wait was recorded with STARTED and
COMPLETED control events. Attempt two began at 03:19:59.570786Z and returned
CONNECTED at 03:20:00.979901Z. This is observed successful resume, not a promise
that any 40613 always resumes. Two physical control requests; zero diagnostic
reads and zero model calls. Round Five pot 218 -> 220 of 400. Rolling charge after
pre-warm: 549/1,500 (rolling expiry can reduce the observed total).

## Live list: stop at the first unmet expectation

| Ticket | Fixture state | Result | Pot before -> after |
| --- | --- | --- | --- |
| D | inventory-baseline | Attempted once; NO_KNOWN_PATTERN, expectation failed | 220 -> 221/400 |
| G | inventory-baseline | Not run: D stopped the list | 221 -> 221/400 |
| H | inventory-baseline | Not run: D stopped the list | 221 -> 221/400 |
| EMPTY | report-15sep | Not run: D stopped the list | 221 -> 221/400 |
| Source consistency | source-baseline | Not run: D stopped the list | 221 -> 221/400 |

D run `33e5be52-fd0e-4201-9de7-4fea3a611376` made one intake model call,
zero investigation planner calls, zero judge calls and zero synthesis model calls.
The procedure completed ENOUGH_DIAGNOSTICS with NO_KNOWN_PATTERN / Not answered.
Deterministic refusal rendering completed; it is not successful evidence-based
synthesis of a comparison. Intake consumed 18,435 input and 178 output tokens,
with 1,500 output tokens reserved.

The selection value-existence lookup for Locations/warehouse_name failed.
Receipt `83a7814d-14b1-4355-8431-2b2c33cd0cca` is FAILED / RuntimeError.
Configured route: OLAP Server, workspace
`149f8d99-1c66-4a0a-9624-759be002bb60`, model
`3484a2bc-98c5-4cef-be5c-a6215484075e`, identity
`investigator-reader@skynwhy.com`. No value or surface self-report returned;
therefore no probe attestation succeeded, no layer quantity was established and
no boundary was compared. Model-to-serving, serving-to-refined and
refined-to-landing remain unchecked because selection resolution stopped first.
There was neither verified cross-surface nor within-layer comparison evidence.

Accounting retained one charged diagnostic/physical reservation (1/12), zero
guards, zero SQL reads and one unsuccessful bounded DAX attempt. The reservation
is not proof that an upstream query occurred: the native worker exited locally.
Pot 220 -> 221/400; rolling last observed 550/1,500. No refunds or counter resets.
No fixture mutation occurred and no restoration was required.

### Concrete worker-contract finding; no repair in this record

The native worker calls load_config before its exception handler. The exact
recorded bootstrap configuration contains `_estate`, but metadata_config's closed
allowed-key contract excludes it. Offline validation of those sealed inputs raises
`ValueError: Unexpected or missing configuration fields`. This independently
reproduces a local contract mismatch; it is not a source/database diagnosis.

Sealed worker events: ordinal 2616 WORKER_START (BOUNDED, timeout120), ordinal
2618 empty WORKER_READ, ordinal 2619 WORKER_END returncode1/error null. Historical
stderr was not sealed, so this report does not claim to have recovered it.
No engine fix or replacement attempt was made after the stop.

D's tape validates and zero-network byte-exact replay matches both refusal outputs.
Grading still fails six checks: answer_category, layers_reached, outcome,
resolutions, and ANSWER_CATEGORY_CHANGED in each output. Expected no-reported-
figure unavailability was never reached because the value check stopped earlier.

### D business output, verbatim

```
You asked: In Inventory Health e1b8e1 I selected warehouse North. Handled Quantity differs from the global total. Check the North selection and explain what report context you can and cannot reproduce.
Answer to your question: Not answered.

The investigation stopped during selection resolution.
Reason: The target check was unavailable, so the requested selection could not be established.
No explanation of the reported difference was established.
Recommended action: Resolve the stated blocker before a new investigation.
You described the selected value as "warehouse"; that description was a hint, not a reason to choose a column.```

### D technical output, verbatim

```
You asked: In Inventory Health e1b8e1 I selected warehouse North. Handled Quantity differs from the global total. Check the North selection and explain what report context you can and cannot reproduce.
Answer to your question: Not answered.

The investigation stopped during selection resolution.
Reason: Target unavailable: value-existence observation unavailable for fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name.
No explanation of the reported difference was established.
Recommended action: Resolve the stated blocker before a new investigation.
You described the selected value as "warehouse"; that description was a hint, not a reason to choose a column.```

## Current strict gate: 2/15, not the earlier recorded-era 10/15

All fifteen current-engine offline attempts used sockets blocked and made zero
estate requests/model calls. Two passed, one replayed but failed grading, and
twelve blocked. Old sealed payloads, tapes, outputs and receipts were not amended
to match new engine behaviour. Prior 10/15 was structured grading of recorded-era
results; it is preserved and is not this current-engine strict replay result.

| Ticket | Current strict status | Reason |
| --- | --- | --- |
| family-A | BLOCKED | TAPE_EVENT_DIFFERS:BUDGET:PROVIDER_RESPONSE |
| family-B | BLOCKED | TAPE_EVENT_DIFFERS:BUDGET:PROVIDER_RESPONSE |
| family-C | BLOCKED | TAPE_EVENT_DIFFERS:BUDGET:PROVIDER_RESPONSE |
| family-D | FAILED | OUTPUT_INVARIANT_FAILED |
| family-E | BLOCKED | TAPE_EVENT_DIFFERS:BUDGET:PROVIDER_RESPONSE |
| family-F | PASSED | Replay, structured match and invariants passed |
| family-G | BLOCKED | TAPE_UNRECORDED_BUDGET_INPUT |
| family-H | BLOCKED | TAPE_UNRECORDED_BUDGET_INPUT |
| family-I | PASSED | Replay, structured match and invariants passed |
| reproduction-16 | BLOCKED | TAPE_EVENT_DIFFERS:BUDGET:PROVIDER_RESPONSE |
| reproduction-empty | BLOCKED | TAPE_EVENT_DIFFERS:BUDGET:PROVIDER_RESPONSE |
| source-consistent | BLOCKED | TAPE_EVENT_DIFFERS:BUDGET:PROVIDER_RESPONSE |
| source-gap | BLOCKED | TAPE_EVENT_DIFFERS:BUDGET:PROVIDER_RESPONSE |
| source-latency | BLOCKED | TAPE_EVENT_DIFFERS:BUDGET:PROVIDER_RESPONSE |
| source-unreachable | BLOCKED | TAPE_EVENT_DIFFERS:BUDGET:PROVIDER_RESPONSE |

[PR #376](https://github.com/bcsnpc/data-investigation-agent/pull/376) remains
draft: 15/15 is not met. Its six ordinary checks passed, while strict CI also
refuses the absent private replay bundle. That CI input refusal is distinct from
the locally measured 2/15. Nothing was merged under a false acceptance claim.

The existing harness emitted these fifteen rows with its historical
ROUND_FOUR_OFFLINE_ACCEPTANCE prefix and old notes_doc. A separate dated ledger
correction attributes the fifteen reference session IDs to this Round Five E
current-engine batch. Original rows remain intact; no duplicate run or request.

Private artifacts retain pre-warm admissions/waits, whole policy approval, before/
after usage, D's live result and failed receipt, tape replay, six grading failures,
exact config validation, and the full fifteen summary. The record adds no new
estate calls, grants, policy increases or fixture changes. Later work requires a
separate decision; the live list remains stopped.
