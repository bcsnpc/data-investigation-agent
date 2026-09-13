# Silver snapshot input contract

The Silver input builder binds one explicit registered Bronze verification to its registered SQL source manifest. It rechecks source artifact hashes, the stored Bronze proof hash, completed verifier evidence and exact ten-table mapping. It produces `.local/silver-snapshot-input.json` with the source snapshot, proof reference, paths, Delta IDs, versions, schemas and counts.

```powershell
python scripts/silver_snapshot_input.py --snapshot-id 3b9354f3-af21-4296-a936-91b4a299777a --verification-id a28d6885-78a8-4f5a-b97b-59cdd90a265b
```

`infra/fabric/read_pinned_bronze.py` provides the notebook reader for this trusted builder output. It checks each current table identity before reading, uses `versionAsOf` for every read, checks schema and row count, then checks identity again. Missing or vacuumed versions fail without a fallback to latest. A newer version of the same table does not invalidate a retained pinned version. The binding file is a local deployment artifact, not an authenticated user-supplied request; deployment must rebuild it from the registry.

The builder itself prepares inputs only. The Silver deployment helper now rebuilds the binding from the registry, embeds the pinned reader and updates the configured existing Silver notebook. No new Silver table set is created. Gold and reports continue using their earlier publications until a separate propagation step. End-to-end snapshot comparability remains incomplete.

The publisher reuses the existing ten Silver tables, records each output Delta identity/version/schema with the source and Bronze proof references, and marks the run ready only after all outputs reconcile in both directions. Source snapshot, manifest hash and Bronze proof hash are also retained on output rows. The legacy pipeline run marker is null because this input did not come from that pipeline. Column names/types and exact row contents are checked; Delta's persisted nullability metadata can differ from Spark expression nullability. Gold and semantic refresh must then consume that publication chain. Per-table writes are not a ten-table atomic transaction, so incomplete runs must never be accepted as a common snapshot. The final check rejects changed output identities or versions during publication; it is not a distributed writer lock.

`record_silver_publication.py --job-id <id>` checks the named READY receipt against the rebuilt input binding and completed job time window, then stores the receipt/job evidence and hash in SQLite `silver_snapshot_publications`. This is publisher reconciliation evidence, not a separate independent Spark verifier. Future consumers must recheck identities and read the recorded versions.

Six input-reader tests and four publication-receipt tests cover proof tampering, failed verification, pinned reads, replaced identities, unavailable versions, incomplete mappings, schema/count differences, invalid versions and wrong destinations.
