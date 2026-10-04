# Round Five Part A: tape boundary decision

2026-10-04. Design/audit only. No recorder, replay, adapter, fixture or
investigation changes. Part A is not implemented. No model or estate request.

## One decision before implementation

The requested combination is not satisfied by saving the current physical-read
protocol. It also is not satisfied by recording every raw upstream response
under the current receipt retention rule. The two instructions are:

> every physical request and its response bytes

> Tapes never contain business data beyond what receipts already hold

There is a concrete transport projection below receipts:

```python
# scripts/read_onelake_commit.py:45-53
return response.read(1_000_001)
actions=[json.loads(line) for line in raw.decode().splitlines() if line.strip()]
info=next((x['commitInfo'] for x in actions if isinstance(x,dict)
           and isinstance(x.get('commitInfo'),dict)),None)
return {'status':'AVAILABLE','latest_commit':commits[-1],
        'commit_info':{k:info[k] for k in
            ('timestamp','operation','operationParameters','operationMetrics') if k in info}}
```

The log response includes actions other than `commitInfo`; the receipt does
not retain them. Capturing the raw log would widen retention to those actions,
which can include file paths and data statistics. This finding is from the code,
not a new probe of the fixture. The listing response is likewise projected to
the selected commit before the parent receives it.

SQL has a separate representation problem. `Read-FabricSqlAggregate.ps1` calls
`ExecuteScalar()` for each permission guard, checks the returned count, then
emits only a `DONE` message with `guard_passed`. `physical_reads.run()` consumes
that protocol. The tape cannot recover a SQL request/result from that message.
`sql_quantity` emits `DONE` before the rows are consumed; the final worker
response carries the bounded rows. A `DONE` event is not the response body.
Record physical requests individually, and associate the quantity's final
bounded body with its physical request; never count a reused guard as a request.

**Recommended decision:** define byte-exact replay at the trusted, bounded
worker/adapter boundary, excluding authentication, with every physical request
represented in order and linked to its bounded returned evidence. Retain exact
provider request/response bodies under the existing safe-recording policy.
This keeps receipt-level retention. It does not replay the upstream HTTP/SQL
response decoder below that boundary, and must not be described as doing so.

**Alternative decision:** require raw upstream-response replay and explicitly
change retention to permit the bounded raw metadata bodies it needs. This would
need a revised retention contract and worker capture protocol before recording.
Credentials and authentication bytes would still never be captured.

No choice is silently implemented. The Round Five instruction explicitly says
to stop after Part A when the tape schema needs a decision.

## Proposed closed tape schema after the decision

All objects reject unknown keys. Each version has one owned schema, shared by
writer and replay validator. This is a proposed contract, not running code.

| Object | Required content and validation |
|---|---|
| Bootstrap | Tape version, run identity, engine fingerprint, entry point, original ticket bytes, environment, configuration snapshot/hash, planner profile/hash, usage-policy snapshot/hash, approved discovery context identity/hash, retained-context/catalog bootstrap, prior budget state. References resolve inside the sealed bundle. No expected answer or fixture truth. |
| Ordered event | Contiguous ordinal, closed event kind, phase, start/end clock, request/response body references and hashes, status/error, parent operation and physical ordinal where applicable. A started attempt without a terminal disposition is incomplete. |
| Configuration read | Named source, content hash, returned non-secret configuration, sequence. Replay supplies this read and rejects an extra or changed read. Secret references remain references, not credential material. |
| Budget decision | Reservation key, request category, admitted/refused decision, before/after limits and charged counts, settlement/uncertainty, restoration purpose. Replay reruns admission in a disposable state; never resets live counters. Refusal is a terminal decision, not an omitted event. |
| Physical request | Declared execution identity/surface, exact admitted statement or HTTP request descriptor at the agreed boundary, parameters, response association, timing, completion or typed failure. Guard establishment/reuse is explicit; reuse references the prior establishment. |
| Model call | Phase (intake, judge, synthesis or planner), attempt/retry identity, generation settings, exact safe request/response bytes, HTTP status, start/end and runtime-return clock, usage/uncertainty and reservation link. No response cannot be replaced by a reconstructed answer. |
| Finalisation | Original terminal state/outcome, both output byte hashes when generated, ordered event count, bootstrap and body seals, completeness result/reasons. A legitimate held or failed run is replayable only if its failure path is complete. It is never given synthetic outputs. |

The body store is local/private, append-only and exclusively created. Secret
detection withholds the body, records `SECRET_DETECTED`, and makes the tape
non-replayable. It must not mask the investigation's original error. A run's
evidence/outcome remains preserved; tape validity is a separate required result,
and a missing/invalid tape fails the recording invariant. It is not silently
labelled a successful recorded run.

## Wiring the code actually requires

- Intake already records provider bodies in `question_intake.py`, but its tape
  has `context_version: None` and no runtime-return timing or full bootstrap.
- Process judgment records payload/profile/policy in `adaptive_runtime.py`,
  but lacks runtime-return timing and a shared run bootstrap.
- Synthesis records bodies and runtime-return timing in `evidence_synthesis.py`,
  under a separate `:synthesis` session; it must link to the same run tape.
- `physical_reads.py` and its workers meter physical reads; they do not record
  all request/response bodies. Native reads, metadata endpoint workers and
  failure-detail workers also need explicit capture/replay seams.
- Clock values, generated identities, guard receipts, prior catalog/usage state
  and configuration reads must be reproducible. Saving final observations is
  not executing the procedure again.
- `session_replay.py` bootstraps from an adaptive planner call. Add a declared
  process-run bootstrap, not a fabricated planner call; retain socket blocking,
  byte-exact request checks and refusal of unrecorded requests.

Acceptance tests must exercise the actual procedure and synthesis: a synthetic
complete run replays both outputs byte-for-byte with sockets blocked; removal
of any required event/body/bootstrap field fails completeness; changed request
bytes or additional reads fail replay; guard reuse stays reuse; failures and
secret exclusions cannot be mistaken for clean tapes. No live run is authorised
by this design note beyond the already approved Round Five task.

Parts B-D remain unstarted. Draft #376 remains unmerged. No freeze is created;
prior freezes remain invalid. Round Five use is 0/400, rolling last observed
641/1500, diagnostic cap 12. The budget decision is separately recorded.
