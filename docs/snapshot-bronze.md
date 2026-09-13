# Isolated versioned Bronze publication

This publisher consumes the exact registered SQL snapshot manifest. It stages source files under `Files/source_snapshots/<snapshot-id>` and writes ten typed Delta tables under `Tables/snapshot_<snapshot-id-without-hyphens>/`. The existing `Tables/app` ingestion path is not targeted.

## Guarantees and boundaries

- Uploads use create-if-absent. An existing staged file is accepted only if its content hash matches the verified local file; conflicting files are never overwritten.
- Fabric verifies the manifest and every uploaded file hash. Spark consumes those exact verified bytes from the driver, avoiding a second unverified remote read.
- Types are derived from captured SQL metadata. Nullability is checked, and non-null values must round-trip through their target types without loss. Unsupported SQL types fail before publication. Timestamp precision beyond Spark's supported microseconds is rejected rather than silently rounded.
- All input frames are validated before output publication. New destinations must be absent. Delta writes use `errorifexists`; a receipt appears only after all ten tables pass.
- Every table is reconciled in both directions with `exceptAll`, retaining duplicate multiplicity and null semantics. Schema types and row counts are checked as well.
- Receipts retain actual Delta table UUIDs, versions, schemas, source content/schema hashes and row counts. The independent verifier reads exactly those versions and rejects replaced identities, changed versions or schemas, and content differences.

The current implementation materializes verified files on the Spark driver and is sized for the 152 MB POC export. Larger sources need a scalable immutable staging reader. The tables are protected by the publisher's no-overwrite contract, not WORM storage. Future consumers must verify table IDs and read the pinned versions; missing or vacuumed versions must fail instead of falling back to latest.

## Components and operation

`upload_source_snapshot.py` runs in the Fabric CLI environment and uses the existing enterprise storage token. `deploy_snapshot_publication.py` creates/updates dedicated publisher and verifier notebooks and waits for asynchronous deployment. Deployment does not start a Spark job.

```powershell
& '.local/fabric-cli-env/Scripts/python.exe' scripts/upload_source_snapshot.py --snapshot-id 3b9354f3-af21-4296-a936-91b4a299777a
python scripts/deploy_snapshot_publication.py --snapshot-id 3b9354f3-af21-4296-a936-91b4a299777a
python scripts/deploy_snapshot_publication.py --snapshot-id 3b9354f3-af21-4296-a936-91b4a299777a --verify-only
```

Run the publisher notebook, wait for completion, then run the verifier notebook. The verifier writes only a new verification receipt; it does not alter Delta tables. A partial publication without a complete receipt is not adopted or overwritten automatically.

`record_bronze_publication.py --snapshot-id <id> --notebook-id <verification-notebook-id> --job-id <completed-job-id>` acquires remote receipts and correlates the verification timestamp with a completed job. It validates source references and pinned identities, then records the evidence and its hash in SQLite `bronze_snapshot_verifications`. Verification IDs cannot be replaced with different evidence.

This is evidence for the **isolated source-to-Bronze mapping only**. Existing Silver, Gold, reports and their metadata lineage still describe the earlier `app` path. They must be wired to this exact version chain before claiming end-to-end snapshot comparability.

## Testing

Tests cover exact pinned verification, replacement table IDs, changed versions/schemas, incomplete content verification, repeated execution IDs, failed jobs, unsupported SQL types, create/append/flush uploads, safe retries and conflicting staged files. Source-artifact and generator checks remain part of validation.

References: [OneLake ADLS-compatible access](https://learn.microsoft.com/en-us/fabric/onelake/onelake-access-api), [Lakehouse schemas](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-schemas).

## Live evidence

Source snapshot `3b9354f3-af21-4296-a936-91b4a299777a` was published into schema `snapshot_3b9354f3af214296a93691b4a299777a` in the existing Bronze lakehouse.

- Publisher notebook: `f7465b47-a127-49fa-91f4-24624a28aebf`; successful job `8091da39-ff69-4a8e-ac86-7cb583270380`.
- Independent verifier notebook: `26cedef4-8133-4446-a694-cbe8878bd3d8`; successful job `ee41fc12-0e81-4d44-a68f-a4ce47cbdcde`.
- Ten distinct Delta table IDs, all version 0; 1,410,699 rows reconciled in both directions.
- Registry status: SOURCE_TO_BRONZE_VERIFIED. Actual receipts and completed-job evidence are stored in SQLite and `.local/snapshot-bronze-verified.json`; nonsecret environment references are committed in `infra/fabric/environment.json`.

A post-publication read of the existing app Bronze tables still returned 100,000 orders and USD 64,892,824.49 net cash. The existing app/Silver/Gold/model path has not been repointed. Next is a Silver publication that consumes these precise Delta IDs and versions and records its own output version map.
