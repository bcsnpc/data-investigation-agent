# Approved local categorical replay

approved_categorical_replay.py adds a separate operator-reviewed local execution flow. It does
not alter the production ticket worker or its native slicer execution holds.

Prepare validates complete supported native selections and stores the exact definition bundle,
page, selections, resolved lab path and fingerprints of the lab source/Gold tables in a review
record. show returns the complete scope and its SHA-256. approve requires that hash and an
explicit reviewer label; it does not run anything. run requires the approved hash.

```powershell
python scripts/approved_categorical_replay.py --database .local/replay-review.sqlite prepare --lab .local/defect-lab/lab.duckdb --definitions .local/report-bundle.json --page definition/pages/PAGE_ID/page.json --selections .local/selections.json
python scripts/approved_categorical_replay.py --database .local/replay-review.sqlite show --id REVIEW_UUID
python scripts/approved_categorical_replay.py --database .local/replay-review.sqlite approve --id REVIEW_UUID --hash REVIEWED_HASH --reviewer OPERATOR
python scripts/approved_categorical_replay.py --database .local/replay-review.sqlite run --id REVIEW_UUID --hash REVIEWED_HASH
```

Execution atomically claims the review as UNCERTAIN before attempting the replay. It verifies
lab fingerprints inside the same read transaction used to capture rows. Changed lab data is
rejected. A successful result is retained and status becomes COMPLETED; repeated run requests
return that result without another capture. Errors or crashes leave UNCERTAIN and are not
retried. There is no automated uncertain-state recovery; inspect evidence and prepare a new
review when appropriate. Review scope hashes protect local consistency, not external signatures.

The definition bundle is the frozen reviewed snapshot, not a fresh live API definition. The
reviewer label is a local operator assertion, not enterprise authentication. This CLI does not
execute Power BI reports, verify live parity, dispatch delivery or change production data.

Six tests cover unapproved runs, one execution/persisted replay, wrong hashes, changed lab
snapshots, stored scope changes and failure retry prevention. Retained native Order Operations
selectors were exercised against an injected isolated double-refund fixture: approved replay
found a mismatch, repeated execution returned the same result and reset completed READY.
Artifact: .local/approved-categorical/4159e0c6-ce11-466a-8711-9f12455054b6/report.json.
No cloud, SQL business queries, LLM or delivery calls.

Next: expose this explicit local review scope in the UI and establish live filter/snapshot
parity before enabling production execution.
