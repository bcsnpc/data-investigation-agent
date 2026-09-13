# Transaction-consistent source artifacts

The source exporter reads all ten OrderOps tables through one SQL connection and one explicit `IsolationLevel.Snapshot` transaction. It requires snapshot isolation to be enabled already and fails without changing database settings if it is unavailable. It uses the restricted investigator credential and executes only SELECT statements. A successful export provides a transaction-consistent source artifact; it does not retroactively certify the existing Bronze copy.

## Artifact and publication contract

Each capture creates a new UUID directory under ignored `.local/source-snapshots/`. Table data is UTF-8 JSON Lines: each line is an array in recorded column order. Non-null values are invariant strings, while null stays JSON null. This preserves decimal precision and distinguishes null from empty text. Schema records include SQL and CLR types, size, precision, scale and nullability. Dates retain their SQL value representation; no local-time conversion is applied.

After all reads succeed, the transaction commits and a receipt is written. Python computes table content and schema hashes, validates every row shape and count, then renames a pending manifest to `manifest.json`. Failures leave no READY manifest. Existing run files are never overwritten. The final manifest hash, source identity, directory and capture time are registered in `source_snapshots` in the metadata SQLite database.

The snapshot UUID is a collector-generated extraction identifier, **not a SQL LSN or a server transaction ID**. Timestamps describe acquisition, not an independently addressable database snapshot. The isolation guarantee comes from the actual SNAPSHOT transaction. Artifacts are content-addressed and checked against the registered manifest hash; they are not filesystem-enforced WORM storage. The collector and its local registry are trusted, not a cryptographic attestation from SQL Server.

Consumers must verify the registered or independently trusted manifest hash before consuming files. Rehashing a modified manifest and trusting its new value is insufficient. Raw folder verification without an expected hash checks internal consistency only.

## Commands

```powershell
python scripts/source_snapshot.py
python scripts/source_snapshot.py --snapshot-id 3b9354f3-af21-4296-a936-91b4a299777a
```

The first command captures a new snapshot; the second verifies the registered reference. `--config` selects the existing metadata configuration. Portable artifact verification supports `--verify <folder> --manifest-sha256 <trusted-hash>`.

`ingestion_contract.plan(folder, manifest_sha256, workspace, lakehouse)` verifies the exact extraction and creates a PLANNED mapping into an isolated `snapshot_<uuid>` Bronze schema. It does not execute a copy. The existing `app` Bronze tables are not targeted.

The publication receipt contract requires every source table exactly once, unchanged source content/schema references and destination paths, matching row counts, distinct Delta table UUIDs, nonnegative pinned versions, and successful content reconciliation. `validate_receipt` checks these structural requirements only; it explicitly returns `snapshot_proof: false`. A trusted publisher and independent reads of those Delta versions are still required to establish remote content evidence.

## Live verification

Final source snapshot: `3b9354f3-af21-4296-a936-91b4a299777a`.

Manifest SHA-256: `809b998a4a731072f504e5435e0b3cdd08a61abf18947e926c9cac2ea358601a`.

All ten tables and 1,410,699 rows were exported and verified. Reverification against the SQLite hash passed. An independent calculation from exported orders, captured payments and refunds returned 100,000 orders and USD 64,892,824.49 net cash; payment/refund order references were checked. The ten-table Bronze plan is stored locally with status PLANNED. No cloud data, pipeline, notebook or model was changed.

Eight tests cover escaped strings/nulls, content tampering, rewritten manifest references, missing/duplicate/escaping artifacts, failed transaction receipts, wrong row counts, pending readiness, complete version maps and registered-hash verification. Generator tests also passed.

## Next integration

Publish this verified artifact into its isolated Bronze destination, reconcile all contents and record the actual Delta table UUID/version map. Then wire Silver/Gold and semantic reads to that manifest/version chain. Existing cross-layer observations must keep their snapshot gaps until the full chain is verified; the new SQL extraction alone does not close them. No fabricated publication receipt has been registered as live evidence.

Reference: [Microsoft SQL snapshot isolation with ADO.NET](https://learn.microsoft.com/en-us/dotnet/framework/data/adonet/sql/snapshot-isolation-in-sql-server).
