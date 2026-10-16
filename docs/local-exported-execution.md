# Local exported execution

`execution` and `investigation` are independent manifest choices. Omitting them keeps live execution and the pipeline baseline. Agent mode remains opt-in until its adoption gate is earned.

A local installation declares `execution.mode: LOCAL_EXPORTED`, an explicit bundle directory, its raw `manifest_sha256`, and `source_manifest_hash`. The last field identifies the approved LIVE manifest under which the export was collected. The local installation has its own manifest hash, which changes when execution settings are added. These hashes are distinct authorities; neither is normalized or relabelled. Retained model context IDs, hashes and revisions, plus the enterprise context ID/hash, must match the export pins exactly.

The bundle reader rehashes the manifest, database and retained definition files before and after reads. Nonempty SQLite WAL or journal overlays refuse. Connections use read-only immutable SQLite with query-only enabled. Tables, columns, storage types and row counts must match the sealed export. Missing assets or columns never fall back to another layer or seeded rows.

Quantities come from exported rows, not recorded outcomes. Direct additive SUM over INTEGER or DECIMAL columns uses exact Decimal arithmetic; no non-NULL rows produces BLANK, separately from zero or an unavailable query. The surface attests `SQLITE_LOCAL_COPY`, its local export identity and its exact asset. It never reports a Microsoft native engine or an aligned native snapshot. Outputs retain `LOCAL_EXPORTED` provenance and `SNAPSHOT_UNVERIFIED`.

Currently unsupported operations refuse explicitly: ratio or other non-SUM DAX, inferred relationship joins, grouped quantity scope, lower-layer filtered scope, native string/collation comparisons, REAL summation and projected quantity computation. Privacy-projected export execution requires a separately tested projection-aware contract; it does not read an exact fallback. Native transports and authentication workers are forbidden in local execution.

Design decision: local reads consume diagnostic admission while recording zero estate physical requests. Export collection costs remain in the original guarded control receipts. Picked form facts remain immutable; a local candidate search returns receipted candidates and never assigns an unnamed visual.
