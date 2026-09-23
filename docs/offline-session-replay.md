# Recorded-provider session replay

2026-09-23 UTC. Ordered reliability item 3; issue #199. This is an offline
engineering check, not a new frozen-domain acceptance attempt.

The simulator runs `AdaptiveRuntime` and the provider SDK over copies of the
catalog and inventory. Every assembled HTTP request must exactly match the saved
request before its raw response is returned by mock transport. Context lookup,
schema validation, rejected proposals, hypothesis updates, compaction, prerequisite
checks, existing redundancy handling, reservation and stop paths use the runtime.
A completed saved child run supplies its original query receipt after normal
admission; an uncached query is blocked. Socket connections are blocked. Source
databases and recordings are not modified. There is no new provider or data read.

```powershell
python acceptance/unknown_domain/replay_planner.py --offline-session SESSION_ID --folder .local/RUN --recordings .local/planner-recordings --output .local/NEW_REPLAY
```

The output directory must be new. It contains disposable database copies and a
result with exact-request comparisons and final-state differences. The command
appends content-free telemetry to `docs/runs/ledger.jsonl`. MATCHED requires all
requests and selected final-state fields to agree. It never grades business truth.
`--inject-at N --injection .local/proposal.json` replaces one function argument
object in memory and stops after that step. A probe is not a full replay pass.
`--allow-engine-drift` permits explicit regression comparison; exact request bytes
must still match, and it does not restore frozen acceptance.

Full replay requires original context versions and completed receipts, exact config,
contiguous call recordings, planner profile, usage policy and return timing. This
item adds the last three fields to opt-in recording. Older recordings remain
unchanged; missing bootstrap/timing is an explicit unsupported gap. Concurrent
usage that cannot be reconstructed fails closed. Transport failures without response
bytes replay their safe timeout/connection category rather than inventing a response.
Arbitrary historical exception causes are not reconstructed. The existing live
single-call comparison remains separate; `--offline-session` selects offline mode.

## Verification and failures

Five focused tests passed in 25.700 seconds, including original synthetic SDK
recording creation with mocked readers. The retained six-call replay alone took
**1.666 seconds**: six byte-identical requests, one reused SQL receipt, one reused
DAX receipt, two context lookups, a rejected unsafe query, duplicate-lookup notice,
revised hypothesis and explicit business-context stop. No state differences occurred.
Inputs, recordings and results remain under
`.local/session-replay-proof-18f26acc-b382-4a86-a2c1-7138c7828325/`.

Malformed proposals at each of six steps followed the actual rejection path.
Additional probes verified missing-schema recovery targets, timeout accounting,
configuration drift and refusal to reuse an output directory. Source database byte
hashes stayed unchanged. Ledger assertions cover read counts, timeout counts and
append-only writes. Retrieval/test ratio counts validated LOOKUP versus RUN/QUERY
proposals, including rejected tests; successful reads are separate. Local repairs
and the new conservative redundancy policy remain later ordered work items.

The first three-test run failed because the synthetic provider expected a schema
field that existing compaction omitted; the visible qualified asset name remained.
The fixture was corrected to use that name. The next three-test run passed, and
the expanded five-test set passed twice. A module-style unittest invocation failed
because these tests require `discover -s scripts` for sibling imports; the supported
invocation passed. These are fixture/runner failures, not live provider evidence.
Ledger rows marked `family=validation` describe suite invocations; their zero
trajectory counters do not aggregate the internal mocked sessions. The retained
original/replay pair has separate engineering rows with measured trajectory counts.
Full regression passed 973 tests in 245.492 seconds. Secret scanning and changed-document local links passed.

Engine recording bytes change, so v4 remains invalidated for further frozen
grading. A fresh freeze and variant must wait for all offline reliability gates.
Frozen artifacts, stored receipts and failed historical attempts remain unchanged.
