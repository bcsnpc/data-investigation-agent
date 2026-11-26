# Round 27: resume after source free-allowance renewal

Owner decision, 2026-11-26: **wait; no paid SQL continuation**. No new live confirmation ticket or model call is admitted during this wait. The source free allowance renews **2026-12-01 00:00 UTC**, which is **November 30 at 6:00 p.m. Chicago time**. Renewal is a time to check availability, not proof that the source or budgets are ready. No automatic restart is configured.

1. Read CLAUDE.md, the latest RESUME, and the owner decision receipt. Keep ordersops `AutoPause` and the free offer unchanged. Do not retry the source before renewal.
2. On resumption, read the actual December ledger policy/accounts and confirm approved provider credit. Do not carry November's higher request ceilings into December or infer cash from a monthly reset. The $3 cash reserve remains protected. OpenAI grading credit expires November 29: valid approved funding is required before any resumed Sol/Astra/Terra grading. Do not switch graders or spend the reserve to work around expiry.
3. Restore the fixture before scoring anything. The original source business/schema hashes matched after removing the owned synthetic row, before SQL paused; the downstream original360 load failed and model7661 is not yet reverified. Keep the original failed capture and already-correct history ticket. Never rerun that ticket.
4. The prepared restoration-only helper uses a **new** recovery folder, verifies the old load is terminal, checks the original pipeline definition and source hashes, then starts one owned original-definition copy and verifies source hashes/model7661. It does not submit a scored ticket. After source renewal, use:

```powershell
$env:DIA_R27_HISTORY_LOAD_RECOVERY = 'history-restoration-copy-recovery2'
& '.local/llm-env/Scripts/python.exe' '.local/round-twenty-seven/recover-confirmation-history-load.py'
```

Run from `C:/temp/dia-r26-build`. Do not rerun an uncertain POST; reconcile its recorded endpoint. Existing recovery folders cannot be overwritten. A failed or unverified restore leaves the scoring pause in place.

5. Only after restoration passes, valid grading funding is established and the whole remaining confirmation fits the current budgets: preserve `.local/round-twenty-seven/opus-confirmation/OWNER_ADMISSION_PAUSE.json` as a resolved record and remove that active marker; append `history` to `sequence.json`'s completed controls, retaining its original error records. Do not release the marker while either prerequisite is missing.
6. Restart the existing confirmation controller on the **same original** root and frozen source6731ead4/imagea0e47731. It must skip all21 saved outcomes and run only latency, waiting and the two access tickets, serially with their fresh controls and restores. The separately qualified repair image is not a replacement for those four original-image cases.
7. Restart the saved-output grader watcher only with valid approved funding; it skips all21 completed independent grades. Do not mark a final gate until all25 have their required independent grades/reviews. Preserve the original14correct/2handoff/0harm checkpoint as a checkpoint, not the final score.
8. Then apply Step4's failed-gate procedure if needed: saved-trace backtrack, generic repairs, free proof first and one whole budgeted failed-only Opus replacement. Do not pool its scores with the original pass. Calibration still requires a passed confirmation and a confirmed December1balance; v5 stays sealed. Merge/tag/close remain pending that sequence.

Offline preparation: source5d8381fc, full6185PASS/53skip, all8image shardsPASS; image `sha256:af6c79da06bb8a232fd7d1d87a2ce4988448589b401de6172353d7544699f18b`. No repaired live proof is claimed. All25 source-file hashes and21 case journal chains were checked; no duplicate native run IDs. Completed results/grades have a checksum-verified Blob checkpoint copy; no original was deleted.
