# HealthNet Opus cost audit

Owner date: 2026-11-26. Observation: 2026-11-27T00:07:57.024547+00:00. New admissions are paused. HN-011/HN-012 were already in flight when the controller was stopped; both finished and their sealed results were recovered without another submission. No engine, prompt, catalog, expectations or budget settings were changed for this audit.

## Per-ticket actual Opus cost

| Ticket | Current attempt | Billed calls, all AI steps | Earlier environmental cost | Status |
|---|---:|---:|---:|---|
| HN-001 | $1.527289 | 6 | $0.000000 | ANSWERED |
| HN-002 | $3.091234 | 19 | $0.000000 | BLOCKED |
| HN-003 | $0.674285 | 3 | $1.359384 | ANSWERED |
| HN-007 | $1.405502 | 7 | $0.666453 | ANSWERED |
| HN-008 | $1.142894 | 9 | $2.028076 | ANSWERED |
| HN-010 | $2.251753 | 12 | $0.000000 | ANSWERED |
| HN-011 | $0.914345 | 5 | $0.000000 | ANSWERED |
| HN-012 | $1.318072 | 7 | $0.000000 | ANSWERED |

Current eight attempts: **$12.325374**. Earlier catalog-environmental attempts: **$4.053913**. Combined HealthNet Opus spend: **$16.379287**. Startup/usage-policy failures consumed no Opus. Originals remain unscored and charged. HN-009 has an uncertain startup, no established result or saved AI usage; it is not counted as zero cost or resubmitted. Authoritative ledger commitments below cover any posted exposure.

## HN-002: where the money went

Two intake calls cost $0.366690; sixteen investigation calls cost $2.155076; one delivery-repair call, accounted under EVALUATOR, cost $0.569468. Total **$3.091234**. The per-ticket actual-use stop is $3; the already-in-flight final call may cross it. No cap was increased. The top-level `model_calls=17` excludes the two intake calls; the billed usage records establish 19 calls in total.

Six queries succeeded: two semantic-model Completed Orders reads, source order-line counts, raw order-line counts, mart order counts, and a raw order/header/encounter join explaining dropped rows. Physical request count was 37, including metadata/control/native work; it is not the SQL/DAX query count.

| Call | Step | Request characters | Input tokens (includes cached/write) | Cache-read tokens | Output tokens | Actual cost |
|---|---|---:|---:|---:|---:|---:|
| 1 | INTAKE | 125,740 | 62,061 | 0 | 1,236 | $0.332919 |
| 2 | INTAKE | 130,734 | 63,360 | 59,955 | 408 | $0.033771 |
| 3 | INVESTIGATOR | 292,083 | 126,351 | 0 | 1,100 | $0.652000 |
| 4 | INVESTIGATOR | 305,561 | 131,891 | 124,596 | 515 | $0.064400 |
| 5 | INVESTIGATOR | 311,101 | 134,110 | 124,596 | 1,695 | $0.096876 |
| 6 | EVALUATOR | 326,500 | 130,679 | 0 | 2,264 | $0.569468 |
| 7 | INVESTIGATOR | 317,436 | 136,173 | 124,596 | 1,547 | $0.102168 |
| 8 | INVESTIGATOR | 323,418 | 138,076 | 124,596 | 755 | $0.093940 |
| 9 | INVESTIGATOR | 324,338 | 138,394 | 124,596 | 842 | $0.096952 |
| 10 | INVESTIGATOR | 325,270 | 138,716 | 124,596 | 912 | $0.099640 |
| 11 | INVESTIGATOR | 326,214 | 139,042 | 124,596 | 944 | $0.101584 |
| 12 | INVESTIGATOR | 327,170 | 139,372 | 124,596 | 838 | $0.100784 |
| 13 | INVESTIGATOR | 328,138 | 139,706 | 124,596 | 939 | $0.104140 |
| 14 | INVESTIGATOR | 329,118 | 140,044 | 124,596 | 889 | $0.104492 |
| 15 | INVESTIGATOR | 330,110 | 140,386 | 124,596 | 932 | $0.106720 |
| 16 | INVESTIGATOR | 331,114 | 140,732 | 124,596 | 844 | $0.106344 |
| 17 | INVESTIGATOR | 332,130 | 141,082 | 124,596 | 783 | $0.106524 |
| 18 | INVESTIGATOR | 333,158 | 141,436 | 124,596 | 816 | $0.108600 |
| 19 | INVESTIGATOR | 334,198 | 141,794 | 124,596 | 810 | $0.109912 |

Request size is the exact canonical JSON API body in characters, including tools, system, messages and envelope; UTF-8 byte counts and capture hashes are in the companion JSON. Token counts are provider-normalized billed usage, not character-based estimates. All calls used claude-opus-5-5.

## Cause: broad catalog plumbing plus a delivery loop

**Yes: the model-facing catalog extends beyond this ticket's scoped clinical order path.** The first intake system has 94,990 characters; its retained catalog includes 241 native objects (123 tables, 64 copy activities, 36 measures, eight sources, six pipelines, three models and one notebook), plus the report/page/visual inventory. Intake sends this inventory even though the user says the ops report and clinical app.

The investigation system repeats **251,283 characters** on every investigation call. The saved native context has 104 definition records: 13 semantic tables, 51 relationships, 15 definition parts, all three semantic models, three measure records, and other SQL/column/module records. Its retained definitions serialize to 327,216 characters before model-facing compression; layer schemas add 109,290 and graph path 78,153. These are separate representations with overlap, not an additive estimate of the transmitted prompt. Two complete pipeline-content definitions alone serialize to 210,455 characters and include activities outside the order path. Revenue/A/R Balance and the billing connection were carried alongside the two Completed Orders models. This is not required merely to explain the clinical orders total.

Code causes: `Factory.target_path().associated()` adds MODEL nodes by shared `owner`; all three HealthNet models have generic owner `retained-catalog`. `NativeCatalog.context()` includes sibling definition parts and relationships under opened containers; whole pipeline definitions are sent instead of only the native activities on the path. The text resolver also embeds the entire native intake inventory. Backfilling made the metadata complete, but these existing broad selectors turn completeness into larger prompts. This audit does not attribute every byte of the increase to the backfill without a controlled pre/post request comparison.

There is also a separate investigation/control-flow failure: after the sixth successful query, submit_finding was refused with `SOURCE_CONSISTENCY_UNESTABLISHED: no reachable declared system of record`. The diagnostic result did include an actual source read, but the legacy scalar source declaration was absent in this multi-database estate. Repair then exhausted its delivery-contract repair. The next **12** investigation responses ended in prose (`end_turn`) without tool calls or new reads. The loop kept giving a format warning and calling again; those twelve calls cost **$1.239632**. These were not twelve necessary investigative steps. No sealed answer was consulted for this diagnosis.

## Narrow scoping proposal — not applied

Keep the complete, immutable backfilled catalog and read-only guard scopes. Change only the model-facing projection: (1) use explicit report/page/visual and exact native model ownership/bindings to scope intake; for free text, send ranked label candidates and fetch details through existing lookup tools; (2) include only selected/candidate paths and their transitive native dependencies, keeping truly tied candidates; (3) replace generic owner-based model attachment with exact model/table binding membership; (4) send only path-relevant pipeline/copy activities and referenced SQL statements, retaining original full definitions and evidence IDs for get_evidence. Do not truncate evidence or infer lineage by names. Add offline tests that required dependencies remain and unrelated models/activities are absent. Qualify on saved/practice evidence before any new HealthNet image is admitted. This needs owner approval because the test image is frozen.

Scoping alone will not fix the separate source-declaration/format-retry loop. Preserve it as a reported defect; do not silently weaken evidence or read-only checks. Any proposed connector declaration correction or loop change should be approved separately from the projection change.

## Remaining budget

Authoritative monthly Anthropic charged and committed: $227.506725. Raw account ceiling $258.108251, protected $8 ($3 reserve + $5 R27), effective ceiling $250.108251. **Available after protection: $22.601526**. No pending model reservations remain after the current pair. The credit-policy display still names the original $3 reserve, but the actual account has $8 protected and its normalized ceiling already excludes the additional $5; do not subtract it twice.

Eight outcomes are saved. Eighteen tickets have not been admitted: eleven Part-1 tickets and seven faults. HN-009 is a separate uncertain submission, not permission to rerun it. At the current eight-ticket mean $1.540672, the eighteen would cost **$27.732091**, a **$5.130566 shortfall**. If HN-009 later needs an owner-approved replacement, nineteen tickets project $29.272763, short $6.671237. These are extrapolations, not guarantees; screenshots and serial fault cohorts are not yet measured.

The eleven unadmitted Part-1 tickets alone project $16.947389, leaving $5.654137 for seven faults. Planning each of eighteen at the $3 actual-use threshold requires $54, short $31.398474, and final in-flight overshoot means $54 is not a strict upper bound. No cash top-up or budget raise is assumed. OpenAI grading has $9.006635 separate ledger headroom and its existing Nov29 UTC expiry; it is not extra Anthropic investigation funding.

New admissions remain paused pending the owner's scoping decision. No injections are active; the current pair completed and its captures are saved. No merge or tag.
