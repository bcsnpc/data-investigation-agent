# Correct-context process-debugging check

Updated 2026-09-25. This is a known-domain regression on the unfrozen engine at
`80423ea`. It is not unfamiliar-domain acceptance.

The batch stopped after exactly three launched evaluator runs. All requested runs
selected `unknown-domain-v4`; the preflight context was
`758842ba-a478-4470-a9f2-d7e7a2ec4413`. C1 failed before intake because the local
usage policy was still labeled `development`. It made no provider or data call and
created no investigation session. The failed run has its own ledger row.

Between C1 and C2, the control plane was aligned to the explicit discovery
environment. Only the policy environment label changed. All 1,181 historical usage
reservations were migrated to that label in one transaction, preserving every row,
daily count and limit. There was no reset, refund or limit increase. The exact
before/after control read is retained locally with the run artifacts.

| Run | Opened context | Result | Boundary and comparison | Reads | Investigation planner | Stop / visibility |
| --- | --- | --- | --- | --- | --- | --- |
| C1 | Preflight found `unknown-domain-v4` / `758842ba…`; no session opened | Infrastructure failure: usage-policy environment mismatch | None | 0 | 0 | Before procedure start; no outcome |
| C2 | Asserted `unknown-domain-v4` / `758842ba…` in the session | `CONSISTENT_TO_BOUNDARY` | Semantic `Activity` -> Gold `movement_values`, `DECLARED_BY_DEFINITION`; 8,765 = 8,765 | 2 DAX, 1 Delta-metadata, 0 SQL | 0 | Step 6; Gold `movement_values`, then `CAPABILITY_UNAVAILABLE` |
| C3 | Asserted `unknown-domain-v4` / `758842ba…` in the session | `CONSISTENT_TO_BOUNDARY` | Semantic `Activity` -> Gold `movement_values`, `DECLARED_BY_DEFINITION`; 8,765 = 8,765 | 2 DAX, 1 Delta-metadata, 0 SQL | 0 | Step 6; Gold `movement_values`, then `CAPABILITY_UNAVAILABLE` |

For C2 and C3, the semantic model's retained `model.bim` named the SQL endpoint and
`dbo.movement_values`. Resolution stayed below that declared connection. The native
endpoint-to-lakehouse relation agreed, leaving one in-scope table candidate. The
notebook definition also declared both Silver inputs. This is statement following,
not global name matching.

Both completed sessions declared `evaluate_scoped_quantity`, `ingestion`,
`job_history`, `presentation_context`, `resolve_measure_path` and
`transformation_definition`. Presentation freshness alone was skipped because the
isolated reader lacks that capability; it remains visible in both outputs. The
procedure did not need transformation judgment or job-history discrimination after
the first boundary agreed. Investigation planner calls were therefore zero. This is
expected for the deterministic path, not evidence that an LLM considered the
transformation.

The next Silver-to-application boundary remains explicit
`CAPABILITY_NOT_IMPLEMENTED`; no absence finding is made. Optional synthesis also
stopped explicitly with `Conflict` because its receipt-integrity adapter does not
yet accept the process receipt shape. That did not replace or alter the saved
deterministic assessment. Both captured intake tapes pass byte/hash verification.

The low acceptance bar was reached by C2 and C3: each executed a real scoped
comparison. No values diverged, so the conditional requirement to ask whether a
transformation definition explained the difference was not triggered. The batch is
partial overall because C1 exposed the policy-label integration defect. No fourth
run, nine-run batch, freeze, variant or unfamiliar-domain claim follows.

See the [machine-readable result](runs/correct-context-process-three.json), the
[fallback audit](silent-fallback-audit.md), and the preserved
[wrong-context correction](no-comparable-path-correction.md#2026-09-25-correction-after-232).
