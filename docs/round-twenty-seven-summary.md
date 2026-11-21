# Round 27: redesign and prove

Status: IN PROGRESS. Started2026-11-17; resumed2026-11-20 under the amended prompt, including its separate Opus evaluator. Existing branch/PR435 retained.

Baseline: main `6fa39d32`, v0.26 `149d290d`. Work uses the clean existing C:/temp/dia-r26-build checkout. The unrelated dirty D:/data_investigation_agent worktree is preserved as a standing-hygiene exception.

## Prompt audit and harmful root causes

Baseline verbatim literals plus dynamic prompt/tool builders are exported in docs/prompts.md. A reproducible AST exporter does not import adapters or read credentials. Four saved harmful outcomes are recorded in docs/harmful-root-cause-r27.md: two wrong target choices and two wrong conclusions from valid but non-answering evidence. No grades or expectations changed.

## Intake and conclusion redesign

IN PROGRESS. Default intake shares the configured investigator; cheap/cascade routes require explicit installation configuration. Installed guided investigations now require question-first-v1 delivery fields and preserve the explicit target in case context. New contract checks structure and declared references, not semantic truth; independent grading remains required. Ambiguous free-text intake now queues a bounded candidate inventory and routes its combined native paths to one investigator, within the same ticket cap. The AI writes each scalar check; code requires exhaustive successful checks and a unique match before a target can be selected. Terminal limits retain a structured UNRESOLVED conclusion with native partial findings and named gaps; hard-stop statuses are not upgraded. Qualified image source0b12e9e5 passed5902tests with53skips and all8image shards. The separate Opus evaluator receives only the ticket, draft and cited native evidence, checks four dimensions, returns specific reasons, and downgrades after an initial rejection plus two retries. Its cost has a separate EVALUATOR ledger purpose within the same case/monthly cap. Independent grading remains separate. See round-twenty-seven-evaluator.md and round-twenty-seven-qualification.json.

## Tools and native facts

IN PROGRESS. Contribution analysis and row-level layer diff are installed over bounded AI-authored native queries, with exact-decimal arithmetic, source query IDs, duplicate-key checks and explicit truncation limits. Saved metadata failures were traced to missing SQL result-column transport fields and unsupported projected INFO rowsets. SQL metadata projection/cursor schema and documented INFO.PARTITIONS projections now have focused transport/gateway tests; writes and business-table escapes remain refused. Read-only baseline admission later verified360source rows, original row/schema hashes, temporalON and model7661; no fixture injection changed during the static queue.

## Dev passes and fixed regression guard
IN PROGRESS. Fixed55cohort slots comprise50unique byte-identical inputs (32static,18fault-dependent); duplicate inputs share only when expectation identity, estate and fixture also agree. All20regression guard IDs and10fresh post-freeze calibration IDs were fixed before new outcomes. See round-twenty-seven-dev-selection.json.

Static cases run three at a time on imagef19ed639. Three initial local capture-declaration preflight failures are preserved, proven to have dispatched no native request, and unscored; replacement case logs are distinct. An Azure polling connection reset resumes the same submitted execution, never a new one. Two early saved outcomes have both independent grades; one cause disagreement awaits independent review. No partial-cohort quality headline is claimed.

## Freeze, fresh calibration and sealed v5
_pending_

## Grading and context gaps
_pending_

## Provider spend and platform diagnosis
IN PROGRESS. Owner confirmed OpenAI31.06USD expiresNov29; protect2USD, purpose grading/review/smoke only. Anthropic cash remains ledger-derived71.855458USD, protect3USD; owner approved dev and fresh calibration now, conditional v5 waits for its later full-budget gate and any confirmed December grant. Initial calibration allowance6.853973USD rose to8.999140USD from completed observed costs. No cap or usage reset. Optional third pass is cut first to protect calibration. Bedrock cap20USD, Amazon models only; Anthropic never grades.

Historical PostgreSQL root cause remains NOT ESTABLISHED from retained metrics/logs; no tier change. Current laptop read timeout was resolved by replacing only the existing PostgreSQL /32 rule; the existing SQL laptop /32 was similarly updated under standing approval, both with readback. No other access change. See round-twenty-seven-postgres.md and decisions.md.

## Cleanup and release
_pending_

Initialization admitted no runs. The dev queue is now active; v5 remains sealed and unopened. No expectation changed.


## Owner-approved pass 1 image split (in progress)

Owner stopped new original-image admissions and allowed the two already-tested plumbing repairs mid-pass. All 29 old-image outcomes are saved unchanged. Repair image `1df39718ad4a1296cba45a57ef82f89faf98a2cb8d7042447d75a74d061e4178`, source `be73c5ff`, passed 5,910 tests with 53 skips, zero failures/errors, and all eight image shards. The remaining 21 tickets use this image; five trace-established one-time plumbing reruns are isolated from their originals. See [image split](round-twenty-seven-image-split.md) and [qualification](round-twenty-seven-plumbing-qualification.json). Final pass score, calibration and v5 gate are pending. No freeze or release is claimed.


Owner budget order, 2026-11-21: finish pass 1 including faults within current dev allowance. Make generic fixes from its backtrack; qualify offline with full suite and all image shards. Pass 2 = pass-1 failures plus the 20-ticket regression guard. Calibration only after pass 2. Protect $14.34 calibration and existing $3 reserve. If pass 2 cannot fit, pause Opus only pending owner-confirmed Dec 1 balance; continue grading, backtracks, docs, tests and fixture restores. After pass 2: calibration, then full v5 budget gate; never partial v5. No limits, counters, expectations or held-out changes.

## Admission checkpoint: protected Opus floor

At 2026-11-21T18:07:55.106873+00:00, 42/50 planned unique tickets had measured attempts: 41 sealed native outcomes and one native intake error with a preserved partial unsealed capture. Eight are NOT RUN: two remaining text-latency tickets, two access forms and all four stale tickets. They are not scored as engine failures and have not been submitted. Of the 42 attempts, 29 used the original image and 13 the qualified repair image; the five owner-approved plumbing reruns remain separate.

Anthropic charged/committed $103.284651 against the existing $120.575301 ceiling; headroom $17.290650. Calibration $14.34 stays protected, and the $3 cash reserve is already excluded from that ceiling. The existing single-run buffer stopped admission before the next ticket. Opus admissions are paused only; saved-output grading, backtracks and offline fixes/qualification continue. No calibration, pass 2 or v5 was admitted. The remaining pass-1 inputs and image assignments stay unchanged for later completion when sufficient credit is confirmed.

All owned latency schedules were removed and source row/schema hashes restored. No access injection or stale toggle was started. Automatic updates were not changed during these cohorts. The Nova primary authorization blocker and reviewed harmful flag remain open; this is not a final score or release qualification.
