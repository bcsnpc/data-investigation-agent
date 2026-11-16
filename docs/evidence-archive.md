# Evidence archive index

Owner-approved full disk cleanup (instruction dated 2026-11-13, received 2026-11-15). **In progress.** Existing account `diaplatformd5dd7d65`, private container `evidence-archive`.

Uploads use server-validated block MD5, a client SHA-256, and stored Content-MD5/size checks before Archive tier. No archive body was downloaded. Per-file SHA-256 manifests are stored alongside each archive. Only hash-verified, eligible local files are removed. Source, locks, Git metadata, RESUME files, ledgers, sealed/held-out material and current references are retained.

| Source / contents | Archive blob | Stored bytes | SHA-256 | Member manifest blob |
|---|---|---:|---|---|
| `D:\data_investigation_agent\.local\round-ten-20261007` historical evidence | `evidence-archive/full-cleanup-20261115/round-ten-20261007/21827cded1ce3171ad17da8d6753f5b3904c64ea1dbb5b748b95f85ac4575841.tar.gz` | 1100165116 | `d868129f48904335b204e20d00b6d3f8c36c4f6c4a98728ca9bb832a63bcf51a` | `evidence-archive/full-cleanup-20261115/round-ten-20261007/21827cded1ce3171ad17da8d6753f5b3904c64ea1dbb5b748b95f85ac4575841.manifest.json` |

Completed verified batches: 1. Eligible local files removed: 635. Remaining queues and retentions are recorded locally under `.local/round-twenty-six/full-disk-cleanup-20261115/`.
