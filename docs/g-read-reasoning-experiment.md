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

Validation before live execution: **1,016 local regression tests passed** in
354 seconds, plus the focused dynamic-admission checks and two generator tests.
Secret scan and diff whitespace checks passed. Implementation commit: 29ea9a1.

Reference cost calculation uses measured input/cached/output tokens at USD 2.50 /
USD 0.25 / USD 15 per million respectively, verified in the
[official GPT-5.4 reference](https://developers.openai.com/api/docs/models/gpt-5.4).
These figures are estimates, not Azure billing receipts; SQL/Fabric costs are excluded.

## Live results

All twelve sequential trials completed: **124 planner calls, 62 SQL reads,
four native reads, eight local query rejections, zero provider errors and zero
qualified final assessments**. Every run ended UNRESOLVED / BUDGET_LIMIT. This is
an unsuccessful conclusion-conversion experiment with useful read receipts, not
a correctness pass or unfamiliar-domain acceptance.

Values below are in trial order 1/2/3. Costs use measured tokens and reference rates.

| Arm | Calls | SQL reads | Native reads | Rejections | Qualified conclusions | Median cost (range), USD |
| --- | --- | --- | --- | --- | --- | --- |
| A: medium, 6 reads | 12/11/8 | 4/5/6 | 2/0/0 | 0/1/1 | 0/3 | 0.704 (0.418–0.754) |
| B: medium, 15 reads | 11/11/11 | 6/8/5 | 0/0/0 | 1/0/1 | 0/3 | 0.617 (0.609–0.672) |
| C: high, 6 reads | 10/7/12 | 6/6/4 | 0/0/0 | 0/0/2 | 0/3 | 0.809 (0.577–1.100) |
| D: high, 15 reads | 11/11/9 | 2/6/4 | 2/0/0 | 2/0/0 | 0/3 | 0.822 (0.750–1.030) |

Neither change, nor their combination, produced a qualified conclusion under
these controls. B2 used eight successful reads: the raised ceiling actually
allowed additional investigation. All B runs then hit cumulative input admission.
D1 hit cumulative input, D2 both cumulative and per-call input, and D3 per-call
input alone. Input limits censored all higher-read trajectories. These results
cannot establish that high effort helps or harms final synthesis, or that more
reads are intrinsically ineffective. Spreads overlap; n=3 per arm and the bundled
high/16,000 change do not support selecting a superior reasoning setting.

The prior #220 G1 conclusion remains recorded; the pooled rate is 1/15 across
differing conditions. It is not a reliability foothold; this batch did not reproduce it.
All four arms contain the registry, so this experiment does not isolate its
behavioral effect. The 53-view audit proves preserved directory coverage, not
unchanged LLM decisions. No stopping-contract change was adopted.

Eight stops involve cumulative input, four the six-read ceiling, two the 12-call
ceiling, and two per-call input (counts overlap). D2's next projected view was
54,122 characters; D3's was 50,210, above 48,000 even after the existing fitter
omitted directory/action tails and optional ownership. Protected observations
alone occupied 44,496 / 40,337 characters. D3 still had 108,652 cumulative characters,
three planning turns and eleven reads remaining. This is a concrete observation-
context limit, distinct from daily cost or provider capacity. No extra synthesis
turn was dispatched and no limit was extended to rescue a run.

Rejection kinds: A2 result-column naming; A3 unsupported SQL National node;
B1 SELECT complexity (14/8); B3 unsupported Sign; C3 unsupported Union and SELECT
complexity (17/8); D1 two unknown/ambiguous DAX members. The ledger categorizes two
as complexity and six as other; none are schema, prerequisite or redundancy
refusals. SQL rejection rate is 6/68 (8.82%). Fifteen schema-prefetch repairs and
one result-equality overlap (C1, reporting only) remain recorded. No distinct read
was refused as a duplicate in this batch. The [ledger](runs/ledger.jsonl) preserves
NOT_GRADED: these are known-domain regressions, not evaluator correctness labels.

### Accounting and experimental integrity

Measured planner usage: **1,699,486 input tokens** (2,688 cached), **308,030 output
tokens**, including 242,296 reasoning tokens. Reference cost: **USD 8.863119**
total, USD 0.418–1.100 per run, below the approved USD 30 allowance. This excludes
intake and SQL/Fabric and is not an Azure invoice. Full planner output reservations
total 1,472,000; the largest actual call used 12,860 output tokens, supporting the
choice not to under-reserve against the old observed peak. Summed run wall time
was 8,778 seconds (146 minutes), excluding inter-run pacing.

All 124 exact request/response recordings load with no exclusion or missing usage.
Actual request settings match each assigned medium/8,000 or high/16,000 arm.
All twelve intakes resolved the same model, measure, dimensions, filters, symptom
and context revision. Engine hash stayed
f16ba81dc702e03e40a7077b6ce00791de1ae574138e39790e8aee9b3912c0c5.
No rescan, grant change, concurrent run or mid-run profile/policy change occurred.

Usage history grew **549 → 751** records; zero active reservations and zero
violations remain. September 24 reservations include intake: 136 planner calls,
66 cloud reads, 4,479,643 input characters and 1,490,000 output tokens. Twelve
ledger rows were appended with the original prefix unchanged. The original
60-read / 1,500,000-output daily policy was restored after the batch without
counter resets or refunds. Usage above a restored daily ceiling stays charged.

After-batch control-plane reads confirm unchanged GlobalStandard capacity 100,
100,000 TPM / 1,000 RPM, GPT-5.4 version 2026-03-05, SQL useFreeLimit=true,
freeLimitExhaustionBehavior=AutoPause and autoPauseDelay=60. Local manifests,
before/after controls, stop reconstruction and tape checks are under
.local/g-arms/. Original results use
.local/unknown-domain-v4/runs/G-registry-{arm}{trial}-20260924.json.

### Individual trials

| Trial | Calls | SQL/native | Lookups including prefetch | Rejections | Stop | Qualified assessment |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | 12 | 4/2 | 6 | 0 | BUDGET_LIMIT | no |
| A2 | 11 | 5/0 | 7 | 1 other | BUDGET_LIMIT | no |
| A3 | 8 | 6/0 | 3 | 1 other | BUDGET_LIMIT | no |
| B1 | 11 | 6/0 | 6 | 1 complexity | BUDGET_LIMIT | no |
| B2 | 11 | 8/0 | 3 | 0 | BUDGET_LIMIT | no |
| B3 | 11 | 5/0 | 6 | 1 other | BUDGET_LIMIT | no |
| C1 | 10 | 6/0 | 6 | 0 | BUDGET_LIMIT | no |
| C2 | 7 | 6/0 | 3 | 0 | BUDGET_LIMIT | no |
| C3 | 12 | 4/0 | 8 | 1 complexity, 1 other | BUDGET_LIMIT | no |
| D1 | 11 | 2/2 | 5 | 2 other | BUDGET_LIMIT | no |
| D2 | 11 | 6/0 | 5 | 0 | BUDGET_LIMIT | no |
| D3 | 9 | 4/0 | 7 | 0 | BUDGET_LIMIT | no |

### Measured planner usage

| Trial | Input tokens | Output tokens (reasoning subset) | Output reserved | Reference USD |
| --- | --- | --- | --- | --- |
| A1 | 159303 | 23746 (19050) | 96000 | 0.754448 |
| A2 | 165391 | 19369 (13303) | 88000 | 0.704013 |
| A3 | 101033 | 11019 (5979) | 64000 | 0.417868 |
| B1 | 153616 | 15562 (9491) | 88000 | 0.617470 |
| B2 | 157744 | 18525 (12356) | 88000 | 0.672235 |
| B3 | 152640 | 15179 (9775) | 88000 | 0.609285 |
| C1 | 134929 | 31420 (26818) | 160000 | 0.808623 |
| C2 | 92572 | 23013 (18524) | 112000 | 0.576625 |
| C3 | 165085 | 45845 (37748) | 192000 | 1.100388 |
| D1 | 147124 | 25906 (21533) | 176000 | 0.750352 |
| D2 | 151768 | 43374 (37764) | 176000 | 1.030030 |
| D3 | 118281 | 35072 (29955) | 144000 | 0.821782 |

### Stop admission audit

The next view was reconstructed offline at each recorded STOPPED timestamp with
unchanged catalog/policy. No provider or data call was made. Multiple limits can bind.

| Trial | Cumulative characters used | Remaining characters | Next projected characters | Binding limits |
| --- | --- | --- | --- | --- |
| A1 | 368889 | 15111 | 43072 | planner_calls, reads, cumulative_input |
| A2 | 377783 | 6217 | 47395 | cumulative_input |
| A3 | 237229 | 146771 | 47942 | reads |
| B1 | 354210 | 29790 | 47540 | cumulative_input |
| B2 | 377597 | 6403 | 47817 | cumulative_input |
| B3 | 354039 | 29961 | 46937 | cumulative_input |
| C1 | 311366 | 72634 | 47539 | reads |
| C2 | 227341 | 156659 | 47377 | reads |
| C3 | 379869 | 4131 | 47556 | planner_calls, cumulative_input |
| D1 | 348386 | 35614 | 47333 | cumulative_input |
| D2 | 357838 | 26162 | 54122 | cumulative_input, per_call_input |
| D3 | 275348 | 108652 | 50210 | per_call_input |


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

This batch measured a maximum 22,417 input tokens. Two calls at that
size plus 16,000 output allowances total 76,834 tokens; three total 115,251, above
the deployment TPM. This is sizing evidence, not a substitute for provider admission
estimation or a guarantee about larger future requests.

At two planners, require a shared rolling admission budget based on full serialized
request token estimates plus each output allowance, including intake and recovery.
Each process's current 65-second timer is insufficient to govern their combined
rate. Keep headroom below 100,000 TPM and 1,000 RPM; verify actual requests and rate
limit receipts before considering three or four workers. Also cap concurrent data
reads independently (initially one) to protect SQL free-tier compute and avoid
time-varying data/context confounds. Two is a proposed initial test ceiling, not a
measured safe throughput claim. No concurrency setting or implementation is changed.

## Historical input-sizing proposal (superseded by structural synthesis review)

Input admission needs a separate controlled evaluation before attributing missing
conclusions to model reasoning. A 576,000 cumulative-character allowance would
cover twelve 48,000-character turns, but would not fix D2/D3's per-call overflow
or provide a thirteenth synthesis turn. For comparison, 64,000 per call and
768,000 cumulative would cover twelve such turns and these measured views, at
increased token/throughput cost. These are arithmetic sizing proposals, not
approved changes or guarantees of convergence. First inspect receipt-backed
observation projection offline and preserve directory coverage; then choose a
separate input-budget experiment instead of changing projection, reasoning and
ceilings together. No input limit, planner-call limit, stopping contract or
concurrency behavior is changed by this report.

The subsequent review stops settings optimization: [separated synthesis](separated-evidence-synthesis.md) is next. Larger input is authorized only as an experimental control.
