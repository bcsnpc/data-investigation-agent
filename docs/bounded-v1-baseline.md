# Phase A: bounded-v1 baseline

Verified 2026-09-14 for [tracking issue #147](https://github.com/bcsnpc/data-investigation-agent/issues/147).

PRs #144 and #146 are merged. Tag `bounded-v1-20260914` points to `60a8594a24aa93700e45409ba066262a7fee4c58`. Its source tree is identical to the tested demo head `c92d56b73294a9957742cf33f515b82d253eefab`.

The [machine-readable manifest](bounded-v1-baseline.json) records the source tree, 286 source/dependency file hashes, installed Python dependency versions, verification artifacts and 16 retained investigation IDs. Those saved baseline runs are pinned to `bounded-v1` by request/result hashes in the manifest. Their database schemas and historical outcomes were not rewritten. Future v2 runs must persist their own engine/context versions as specified in Phase F.

| Check | Result |
| --- | --- |
| Full Python script suite | 366 passed, 121.369 seconds |
| Portal API tests | 6 passed |
| Portal TypeScript/Vite build | Passed |
| PowerShell script parsing | Passed |
| Isolated defect matrix | 10/10 passed |
| Multilayer matrix | 5/5 passed |
| Ticket → review → worker → verified defect draft → reset | Passed; fixture reset READY |
| Demo PR CI | All generator, PowerShell and portal checks passed |

PowerShell surfaced unittest's stderr progress as `NativeCommandError`, producing a shell-level nonzero result; unittest itself finished with `Ran 366 tests` and `OK`. Both the raw log hash and this caveat are retained. This is not a hidden failing assertion.

The full suite includes business-demo attachments, changed-source holds, idempotency, interrupted-work handling and API authentication. This run used local automated demo flows, not a new browser recording. Prior browser/video artifacts remain historical evidence.

Reproduce in a fresh ignored folder:

```powershell
python -m unittest discover -s scripts -p "test_*.py"
python scripts/evaluate_lab_matrix.py --output .local/baseline-check-lab
python scripts/evaluate_multilayer_matrix.py --output .local/baseline-check-layers
python scripts/demo.py rehearse --folder .local/baseline-check-demo
```

Use a new output folder for each rehearsal; existing folders are deliberately preserved. Portal verification uses `npm test` and `npm run build` in `apps/order-portal`.

## Retained boundaries

No source/Fabric data, deployed models, cloud tier, quota configuration, LLM calls or external notifications were changed by baseline verification. Existing live-system evidence was not refreshed. This remains a bounded two-metric investigator with separate isolated demos, not catalog-v2. Exact semantic snapshot comparability and the wider product gaps remain open.

For rollback/reference, inspect the baseline tag in a separate worktree; do not reset over active work. The revised product plan and A–J roadmap are delivered alongside this baseline. **Next implementation: Phase B model onboarding foundation.**
