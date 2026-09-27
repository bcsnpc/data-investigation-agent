# Receipt-first read accounting

Process reads are now recorded immediately after transport returns, before observation interpretation or support validation. Each record links its query receipt and result hash; metadata responses without query tables are retained in the session journal. Exceptions remain unsuccessful/uncertain attempts, never fabricated successes. The scorer and ledger use these records instead of requiring a validated conclusion. Already collected observations also survive final support-validation failure; no unvalidated assessment is published.

A regression executes a real injected-transport read, forces subsequent support validation to fail, reloads the session, and verifies the receipt and read count remain. Metadata and failed-read accounting have separate tests. Correction folding verifies the original row hash and preserves the number of investigations.

The original 223 ledger rows are byte-preserved. A correction for `0154df11-48b6-48ab-a193-f401041bd25a` records two Fabric SQL reads, one native DAX read and one Fabric endpoint metadata read, using the three sealed query receipts and the existing endpoint audit. Its HELD status, failed support validation, absent synthesis and historical extracted observations are unchanged. This is reconciliation, not a new run or retroactive successful assessment. See `docs/runs/declared-chain-depth-audit.json`. Readers aggregating the ledger should use `effective_rows()` so corrections do not count as investigations.

Three focused regression tests pass. No live rerun yet.
