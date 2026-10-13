# Round Eighteen recording-content audit

Dated 2026-10-12 America/Chicago; execution continued on 2026-10-13 UTC.
This is a read-only structural audit. It is not a replay, a credential scan,
or a proof that every retained client value is necessary or anonymised.
No estate/model requests, extraction of archives, deletion or tape rewrite
was performed. Original captures and ledgers were not changed.

## Coverage and findings

The scan enumerated `D:/data_investigation_agent/.local`; installed-library,
Git, node_modules and named Azure CLI profile directories were excluded.
Counts refer to files observed by that enumeration, not unique investigations.
Duplicates, replay working copies and sealed originals can all occur.
The detailed path/hash/shape records remain local in
`.local/round-eighteen/recording-content-audit-01/`.

Enumeration began at 04:41:38 UTC; all planned local passes completed before
05:11 UTC. The [machine-readable manifest](round-eighteen-recording-content-audit.json)
contains version counts, exceptions and SHA-256 hashes of every local receipt.
Its SHA-256 is `35a5ea970dca8cfd6c7851b40e8be3c939587f10162bc9af7c310b1f02e3ca28`.

| Material | Coverage | Result |
|---|---|---|
| Loose tapes | 1,146 files; 9,754,414,222 bytes; versions 1 through 14; 1,101,704 events | 1,005 JSON-shape scans complete within the stated bounds; 141 partial due to 1,813 non-JSON events |
| Decoded `rows` arrays | 20,121 occurrences | 9,652 exceed 249; all are the two known accounting tables. Zero larger non-accounting arrays identified in the decoded portions |
| Terminal marker | 1,141 tapes end in FINAL; five do not | Marker presence only; seals/replay were not revalidated and unfinished captures were preserved |
| Inventory schemas/counts | 1,596 files | 1,595 contain exactly `assets`, `observations`, `scans`; one legacy shared inventory has additional operational/registry tables, investigated below |
| Catalog schemas | 1,961 files, 321,854,537,728 logical bytes | 1,959 inspected; 51 distinct operational table names. Two readonly errors; no catalog-wide payload inspection |
| Archive metadata | Six ZIPs and eight gzip files | ZIP member names/sizes only; no Parquet/DuckDB/CSV member names found there. Gzip contents not inspected; no archives extracted |

The 1,813 non-JSON events are 1,809 `WORKER_SEND` and four `WORKER_READ`
events; they were recorded as inspection gaps rather than inferred empty.
The exploratory summary's `max_result_rows` label was overly broad: its
9,408 maximum belongs to accounting state. The structured manifest calls it
`max_rows_array_including_accounting`; it is not a 9,408-row diagnostic result.
Later files created by the concurrent cloud work are outside this enumeration.
Disk free after the audit: **13,021,548,544 bytes**, above the 10 GB floor.

A `rows` array longer than 249 is a review candidate, not proof of an
unbounded export: metadata and budget state also use that member name, and a
small complete table can fit within a legitimate evidence bound. The audit
separates known `BUDGET_INPUT` accounting tables from potential query evidence.
No values from these arrays are reproduced in this report.

The two catalog schema reads that failed were preserved as failures:
`process-tapes/1f75553d-c365-45f5-8a30-8420757e00e7/catalog.sqlite` and
`process-tapes/914cb4a3-8d29-41f3-8245-c55f867f0c62/catalog.sqlite` both returned
`OperationalError: attempt to write a readonly database`. No journal recovery,
immutable-mode bypass or writable reopen was attempted. This establishes an
uninspected boundary, not corruption or absence of data.

## A real full-source export exists outside the recordings

The legacy `.local/metadata/inventory.sqlite` is not a three-table-only
collector image. It also holds lineage, investigation/publication receipts and
a `source_snapshots` registry. That registry points to
`.local/source-snapshots/3b9354f3-af21-4296-a936-91b4a299777a/`.

This is an intentional full ten-table SQL source export from 2026-09-13,
recorded in the original [source-snapshot documentation](source-snapshot.md)
and [delivery history](progress.md). It contains **1,410,699 rows in
151,996,446 bytes** of JSONL: customers 20,000; products 150; orders 100,000;
order_lines 286,652; payments 105,047; shipments 95,545; shipment_lines 273,805;
refunds 7,270; refund_lines 12,680; audit_log 509,550.

The existing offline verifier rechecked every data-file hash, schema hash and
row count against manifest SHA-256
`809b998a4a731072f504e5435e0b3cdd08a61abf18947e926c9cac2ea358601a`.
No values were displayed. The files remain untouched. This export is an
older ingestion/publication development artifact, not a bounded investigation
result. Its presence means **the whole `.local` tree must never be described
or bundled as metadata-only**. It must stay outside normal client recording
publication; discovering its path in a registry does not authorise uploading
the referenced data. This audit did not find it embedded in the inspected
decoded tape row arrays, but archive contents have not all been inspected.

A second directory, `aa95b1d3-7626-4adc-860f-fd8cb2e3041c`, contains the
same ten JSONL data files byte-for-byte (all ten SHA-256 comparisons passed),
but is not the registered source snapshot in the inspected inventory. Its
manifest hash is
`b694c6f54e6c93ec67cd3ad0694eeddc6120c7158ff90f262210f4600ce2dc52`.
It remains unmodified and was not promoted to a trusted registry entry. The
two copies total 303,992,892 data bytes and 2,821,398 stored row occurrences;
those are duplicate storage counts, not independent data. A third source-
snapshot directory is empty.

Separate local development files comprise 52 lab DuckDB files (196,198,400
bytes) with business tables of one to three rows each, plus one fixture Parquet
of one row/nine columns. Their table/schema counts were inspected read-only;
they were not mixed into the recording audit or treated as client evidence.

## Storage and retention corrections

Code review confirmed that screenshot bytes are stored in
`workspace_images.content`, alongside separate image read/review tables.
`screenshot_retention_days` has a schema/default but no deletion consumer;
claiming automatic screenshot expiry would be wrong. The storage guide now
states that clearly.

The local retention planner defaults tapes and ledger rows to indefinite,
keeps unknown/unfinished material, verifies hashes before deletion and records
a durable audit. It is not a cloud lifecycle scheduler. No comprehensive
client-wide PostgreSQL/Blob/backup/version purge is implemented.

The cloud shared-state adapter rejects privacy-projected persistence, the
slim recorder rejects projected captures, and screenshot upload rejects
projected estates because column projection cannot redact image pixels.
These are explicit unsupported boundaries, not permission to record exact
bytes for an installation that declared projection.

## What this does not establish

The catalog scan inspected table names, not all JSON/BLOB values across the
321.85 GB logical catalog population. Earlier sampled diagnostic documents
were bounded to 249 rows, but those samples do not cover every catalog cell.
Tape decoding also has opaque protocol/text events outside the JSON-shape
check. Only arrays named `rows` are counted; other result member names are
not a complete row census. Nested-string parsing has a 64 MiB/depth-80 bound
and recognises strings starting directly with a JSON object/array delimiter.
Excluded regions are not counted as proof of absence. Archive member metadata does not inspect archived database contents.
An archive-wide assertion of no bulk business rows therefore remains unearned.
No publication is authorised by this audit alone: credential/content review,
existing evidence-location approvals and sealed hashes still apply.

The audit helper has five offline regression tests covering nested response
JSON, bounded versus metadata arrays, conservative accounting classification,
unchanged input bytes and explicit unsupported/opaque coverage. All five pass.
The existing seven local retention tests also pass. No source restriction or
capture schema was weakened to obtain these results.
