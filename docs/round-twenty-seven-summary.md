# Round 27: redesign and prove

Status: IN PROGRESS. Owner instruction dated 2026-11-16, started 2026-11-17.

Baseline: main `6fa39d32`, v0.26 `149d290d`. Work uses the clean existing C:/temp/dia-r26-build checkout. The unrelated dirty D:/data_investigation_agent worktree is preserved as a standing-hygiene exception.

## Prompt audit and harmful root causes

Baseline verbatim literals plus dynamic prompt/tool builders are exported in docs/prompts.md. A reproducible AST exporter does not import adapters or read credentials. Four saved harmful outcomes are recorded in docs/harmful-root-cause-r27.md: two wrong target choices and two wrong conclusions from valid but non-answering evidence. No grades or expectations changed.

## Intake and conclusion redesign

IN PROGRESS. Default intake shares the configured investigator; cheap/cascade routes require explicit installation configuration. Installed guided investigations now require question-first-v1 delivery fields and preserve the explicit target in case context. New contract checks structure and declared references, not semantic truth; independent grading remains required. Ambiguous free-text intake now queues a bounded candidate inventory and routes its combined native paths to one investigator, within the same ticket cap. The AI writes each scalar check; code requires exhaustive successful checks and a unique match before a target can be selected. Terminal limits retain a structured UNRESOLVED conclusion with native partial findings and named gaps; hard-stop statuses are not upgraded. Live qualification and scoring remain pending. Focused checks: 180 Round23 tests, five new conclusion tests, two routing tests and one exporter test pass; full qualification not yet run.

## Tools and native facts

IN PROGRESS. Contribution analysis and row-level layer diff are installed over bounded AI-authored native queries, with exact-decimal arithmetic, source query IDs, duplicate-key checks and explicit truncation limits. Saved metadata failures were traced to missing SQL result-column transport fields and unsupported projected INFO rowsets. SQL metadata projection/cursor schema and documented INFO.PARTITIONS projections now have focused transport/gateway tests; writes and business-table escapes remain refused. No new estate read has been admitted.

## Dev passes and fixed regression guard
_pending_

## Freeze, fresh calibration and sealed v5
_pending_

## Grading and context gaps
_pending_

## Provider spend and platform diagnosis
_pending_

## Cleanup and release
_pending_

No Round27 ticket/model/estate run has been admitted at initialization. v5 remains sealed. No expectations changed.
