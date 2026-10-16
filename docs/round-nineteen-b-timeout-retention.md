# Round Nineteen B timeout and partial retention

2026-10-13. No third Part C attempt is authorized or performed. The second
verification execution stopped at the platform job timeout. The operator's
plan supplied a 1,200-second worker deadline while the existing scheduled job
had a 600-second `replicaTimeout`. A per-execution container template does not
establish a different job timeout. No platform setting was changed by this fix.

## Durable verification evidence

The read-only PostgreSQL snapshot at 17:58:13 UTC is retained locally in
`.local/round-nineteen-b/verify-02-durable-audit/readback.json`, SHA-256
`5378b9f676980306719095e69c00bda4b0a5e48a50f6329988d616fea5500000`.

- Session `round-nineteen-b-verify-02`: 33 physical slots, all SETTLED;
  zero outstanding reservations in that session. The charged quantity comes
  from `reserved.cloud_calls`; `actual={}` is not a zero charge.
- The reservation keys identify 14 admitted operations: two `target-schema`
  metadata operations and twelve `bounded_fabric_sql` value operations.
  These are admission/accounting observations, **not completed witness results**.
- Exact guard count, successful witness count and their result values are
  unavailable from this accounting surface. Investigation diagnostics and
  model calls were not part of this verification control.
- The model publication survives in PostgreSQL at revision 6, body hash
  `f89de65b94812047b8d99fd73e2ffaeb538f688cd73e25d6657f4572e6effdae`.
  Its receipt says `NOT_EARNED_BY_PUBLICATION`. It establishes neither
  readiness nor successful verification or replay.

The code in `cloud_verification_capture.Capture` writes the tape, event journal,
working snapshots and progress under the container's local work directory.
This path does not publish incremental slim-recording objects to remote CAS.
`cloud_stage_worker.run` packages and uploads them in its Python `finally`
block. A hard container termination can bypass that block. The operator
reported the output ZIP absent; no remotely recoverable partial tape is
established by this capture path. The absence of a final ZIP does not erase
the durable publication or ledger charges. No partial result is counted as a
pass, and exact replay has not been earned for this attempt.

## Fixture4 interrupted scan

Read-only owner-health snapshot at 17:58:13 UTC:

| Owner suffix | Durable disposition |
| --- | --- |
| `8e434350-7100-47b7-a0de-2c5732385dbb` | CURRENT at 17:41:35 |
| `95b6d455-9150-4738-983d-ca6e7e0f3719` | CURRENT at 17:44:28 |
| `974791f8-3e8f-4f38-a129-b15b9030ab14` | CURRENT at 17:49:44 |
| `b4871498-bd35-45be-916c-9a642568012c` | CURRENT at 17:50:04 |
| `8195c990-f9ed-4190-a935-ec3fa2ef443c` | Fresh unsupported-kind refusal |
| `a23c2d34-8d82-4772-ab32-bf26face4d83` | Fresh unsupported-kind refusal |
| `a3aca96f-d2f1-4495-8a0c-bf761774dfe4` | Fresh unsupported-kind refusal |
| `a5797c7c-d548-4f40-8b74-56a42d0c895e` | Fresh unsupported-kind refusal |
| `ad49e54f-50b2-4562-9c43-9e6ba0fcd5cb` | Fresh unsupported-kind refusal |
| `b0ab76f7-20c7-410e-90e4-2c4eb104059a` | Fresh unsupported-kind refusal |
| `b71c906a-0ada-4565-adb5-81c8745f7f30` | REFRESHING from 17:50:18; interrupted, not completed |
| `ba24d52c-fcf9-4f1f-a377-f4d38547d887` | Only prior 08:10 observation; not reached in this attempt |

The scan session `graph-scan:4bd73a28-772d-4216-b5dd-12f1f6dc9381`
has 20 charged reservation slots: 19 SETTLED and one RESERVED at the
18:01:24 UTC accounting readback. The helper did not settle or release it.
No CPU-loop, privacy-audit stall or query failure is inferred from owner health.
A narrow retry configuration includes only the last two owners, omits INFO
model collection and explicitly disables admin metadata. Existing scope and
caps remain unchanged. The original failed execution remains recorded.

Fixture5's 17:59:49 UTC snapshot shows all ten owners reached: five CURRENT,
five fresh unsupported-kind refusals. Its session
`graph-scan:10a7e5e8-e37a-40c4-aa14-0080023191eb` has 21 SETTLED physical
slots and no pending reservations at 18:01:24 UTC. This is not a claim about
the execution's final status or publication of its scan summary.

## Next-launch prevention

`cloud_stage_environment.build` now requires a retained control-plane job GET
with its observation time for every verification launch. Admission refuses
missing, invalid or stale timeout observations and any remaining worker
deadline longer than the observed `replicaTimeout`. The resulting environment
carries a hash of that observation. This checks the observed setting; it never
raises it. The CLI requires `--job-observation` for verification. The check
does not guarantee that work and output packaging will fit inside the limit;
operators must allow time for packaging within the existing job duration.

Validation: 13 tests and 9 subtests pass across job admission, environment
construction and stage execution, including a 1,200-second deadline rejected
against a 600-second observed job and no launch environment returned.
All changes are future-facing; no attempt or sealed capture was rewritten.
