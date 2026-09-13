# Silver snapshot input contract

The Silver input builder binds one explicit registered Bronze verification to its registered SQL source manifest. It rechecks source artifact hashes, the stored Bronze proof hash, completed verifier evidence and exact ten-table mapping. It produces `.local/silver-snapshot-input.json` with the source snapshot, proof reference, paths, Delta IDs, versions, schemas and counts.

```powershell
python scripts/silver_snapshot_input.py --snapshot-id 3b9354f3-af21-4296-a936-91b4a299777a --verification-id a28d6885-78a8-4f5a-b97b-59cdd90a265b
```

`infra/fabric/read_pinned_bronze.py` provides the notebook reader for this trusted builder output. It checks each current table identity before reading, uses `versionAsOf` for every read, checks schema and row count, then checks identity again. Missing or vacuumed versions fail without a fallback to latest. A newer version of the same table does not invalidate a retained pinned version. The binding file is a local deployment artifact, not an authenticated user-supplied request; deployment must rebuild it from the registry.

This change prepares inputs only. The helper is not yet wired into or deployed over the existing Silver notebook. No Silver tables or cloud notebooks are created by the builder. Existing Silver, Gold and reports continue using their earlier publications. End-to-end snapshot comparability remains incomplete.

The next publication step should reuse the existing ten Silver tables, record each output Delta identity/version with the source and Bronze proof references, and mark the run ready only after all outputs reconcile. Gold and semantic refresh must then consume that publication chain. Per-table writes are not a ten-table atomic transaction, so incomplete runs must never be accepted as a common snapshot.

Six offline tests cover proof tampering, failed verification, pinned reads, replaced identities, unavailable versions, incomplete mappings, and schema/count differences. The reader has not yet been exercised in a live Spark job.
