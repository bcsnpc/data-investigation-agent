# Part A — retained graph on the platform

2026-10-13. The static graph is now in the existing PostgreSQL authority. Its raw definitions are immutable private Blob objects, referenced by SHA-256. This is a seed from retained, time-labelled context, not a fresh estate scan.

| Estate | Owners | Nodes | Edges | DECLARED | UNKNOWN | Visual/slicer paths inspected |
|---|---:|---:|---:|---:|---:|---:|
| Fixture | 40 | 851 | 980 | 855 | 125 | 76 |
| Billing | 9 | 270 | 294 | 277 | 17 | 7 |

Every inspected path returned a named stop without truncation; zero complete or VERIFIED paths are claimed. Full type counts, gaps/remedies and the 83 path results are in `round-nineteen-graph-coverage-a.json`. The API supplies bounded path, visual context, filters, columns, definition and freshness slices with per-object gateway checks and historical reads. Missing timing is unknown, not an inferred refresh time.

1,504 content-addressed objects occupy 397,001 stored bytes. Each immutable PUT was followed by byte-equivalent GET verification: 3,008 platform Blob controls, zero estate reads and zero model calls. These platform storage operations are recorded separately from the 1,500-request estate pot. Storage and transaction cost at this size is below USD0.10; it fits the existing conditional USD13.74/month platform estimate and USD20 ceiling.

Readback receipt SHA-256: `6f107f066314aa12f38826adb9fcc3eb3673102670b6183ba3257dad3c5bce98`. The first operator readback used the API's default 1,000-record bound and correctly failed conservation after committing the fixture. A separate readback used the explicit 10,000-record bound, confirmed the unchanged fixture and completed billing; no published definition or historical record was replaced to pass the check.

Observed performance defect: row-by-row graph writes held the platform transaction for minutes over the network. Batched writes now preserve the same atomic transaction/history; a regression injects a late failure and proves complete rollback. Targeted validation: 46 tests passed/14 optional tests skipped, then 33 graph/neutrality tests passed with the new regression.

Part B is correcting extraction gaps found against actual retained definitions: notebook column lineage was not using the existing static transformation reader, and pipeline Script bodies were omitted. DAX engine dependency access remains a separate permission/surface limitation; code parsing must not pretend to resolve it.
