# G read-budget and reasoning experiment

2026-09-24. Follows accepted #220, issue #199. KNOWN_DOMAIN_REGRESSION only.

## Offline diagnosis, then implementation

The [three-trajectory audit](g-trajectory-audit.md) was completed before engine
changes. G2/G3's sixth read prevented a subsequent planner turn; both had genuine
observation-driven hypothesis revisions. The experiment changes the authorized
read ceiling, not the stopping contract or hypothesis-selection instructions.

Ownership now appears once per configured connection, keyed `s` (approved SQL),
`f` (Fabric metadata), `p` (selected Power BI model) and `a` (unknown). Existing
asset handles use these prefixes; suffixes remain unique and server-resolved.
Connection roots stay literal even when the same root has an asset handle.
Fabric metadata membership does not establish a SQL endpoint or authorize reads.
No per-entry labels, business mapping or query rewrite are added.

The registry is attached after ordinary context fitting, before usage reservation.
If it exceeds per-call or remaining cumulative character allowance, it is omitted;
existing directory/evidence is unchanged. It never invokes the fitter a second
time to evict context. All 53 original recorded calls preserve their exact
directory entries and SQL-object counts; five omit the header at 48,000 characters.
Permanent tests cover those 53 size/count shapes, a 28/11 directory golden,
identity boundaries, root/handle round trips and saturated payloads.

| Recorded F call 1 | Before | After |
| --- | ---: | ---: |
| Directory entries | 28 | 28 |
| SQL objects | 11 | 11 |
| Pre-wire core characters | 14,409 | 14,886 |
| Including unchanged generation-options field | 14,538 | 15,015 |
| Compact wire characters | 9,734 | 10,210 |
| Serialized request bytes | 28,217 | 28,780 |

The +477 core-character cost is constant in directory size, per configured
connection set. The local measurement is `.local/g-arms/registry-audit.json`.

## Fixed experimental controls

| Arm | Reasoning | Maximum output tokens/call | Reads/run |
| --- | --- | ---: | ---: |
| A | medium | 8,000 | 6 |
| B | medium | 8,000 | 15 |
| C | high | 16,000 | 6 |
| D | high | 16,000 | 15 |

Three sequential runs per arm, interleaved A/B/C/D, B/C/D/A, C/D/A/B, using the
same existing G ticket, catalog, reader and model deployment. All arms use the new
registry. C/D change effort and output allowance together, so their effect cannot
be attributed to effort alone. Earlier #220 runs are historical context, not an
identical-engine randomized control. Intake remains the ordinary resolver and its
scope variation is recorded. This small sample can show spread, not generality.

Unchanged controls: 12 planner calls, 48,000 characters/call, 384,000 characters/run,
120-second provider timeout, 1,800-second run deadline, 65-second serial pacing,
one optional metered planner recovery, one in-flight planner, read-only identities,
SQL free limit and AutoPause. With one action per planning turn, 15 reads cannot
all be used under the 12-turn ceiling; the raised ceiling primarily removes the
six-read stop and may expose planner/input limits instead. This limitation is
reported, not silently repaired by another increase.

The dynamic workspace defaults to 15 reads; the evaluator's operator-only
`--read-limit` sets A/C to 6 before creating their reviewed envelopes. Legacy
candidate-building limits remain bounded and do not own the dynamic read budget.
Default mini and medium generation settings are unchanged; high has a separate
experimental configuration.

The local experiment daily output ceiling is raised from 1,500,000 to **2,000,000**,
rather than reserving below the requested provider maximum. Full 8,000/16,000
reservations remain conservative and are never refunded. Twelve worst-case
12-call plans reserve 1,728,000 output tokens plus intake. At the preflight UTC
day boundary there are no new-day reservations; all 549 historical records remain.
The user separately approved 60 -> **126 daily cloud reads** for this experiment.
Daily planner/input limits remain 240 / 8,000,000. Local before/after policy
readbacks and Azure deployment/database control reads are saved under
`.local/g-arms/`. Original daily policy is restored only after the batch, without
altering any reservations. No mid-run setting change is permitted.

The approved planning allowance is $30. Report actual token use and an explicitly
labelled pricing estimate separately from Azure billing; a token reservation is
not a billed charge. Preserve every failed/partial/blocked attempt and append one
ledger row per run. No freeze, fresh variant or unfamiliar-domain claim.

## Live results

Pending. No result is inferred from the offline coverage checks.

## Concurrency proposal — not implemented

Start with **two independent investigator processes**, one catalog/usage database
and one deployment-wide admission coordinator. Keep current execution serial until
that coordinator and tests exist. `max_inflight_planners` currently accepts 1–4
and counts RESERVED planner rows across the environment, including intake; raising
it alone supplies neither a queue nor TPM/RPM pacing. A competing reservation can
produce USAGE_LIMIT instead of waiting. It does not cap simultaneous SQL/native
reads or whole investigations.

The shared SQLite reservations and session transitions use BEGIN IMMEDIATE,
unique reservation keys and no refunds. Writes serialize; 10-second connection
timeouts can still fail under contention. Provider work runs outside transactions.
Use the same database for all workers: copied catalogs would independently spend
the same daily allowance. Never clear stranded RESERVED rows as a concurrency fix;
preserve uncertain completion and reconcile through explicit recovery. Pin engine,
connection policy and context versions for the batch; don't rescan or change grants
during the experiment.

Use distinct run/request/session IDs and UUID recording directories. ContextVar
recording state isolates calls, but process-global environment credentials and
`local_azure_key` make separate processes safer than mixed-profile threads.
The current interactive workspace has a unique single-active-job index; it cannot
be advertised as concurrent without a separately reviewed queue change. The
evaluator bypasses that queue and must not be confused with hosted UX support.
The JSONL ledger append is not a transactional multiprocess collector: one parent
process should append completed run rows, with durable deduplication/recovery.

At two planners, require a shared rolling admission budget based on full serialized
request token estimates plus each output allowance, including intake and recovery.
Each process's current 65-second timer is insufficient to govern their combined
rate. Keep headroom below 100,000 TPM and 1,000 RPM; verify actual requests and rate
limit receipts before considering three or four workers. Also cap concurrent data
reads independently (initially one) to protect SQL free-tier compute and avoid
time-varying data/context confounds. Two is a proposed initial test ceiling, not a
measured safe throughput claim. No concurrency setting or implementation is changed.
