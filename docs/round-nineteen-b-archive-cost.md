# Round Nineteen-B archive cost admission

2026-10-13. No new archive batch has been uploaded at this checkpoint.

The owner specified Cool uploads followed by Archive, without downloading blob bodies. Microsoft documents that this immediate transition incurs Cool early-deletion charges. The controller reserves **31 days** at the Cool storage rate (31/30 of a monthly price) before upload; it does not silently substitute Hot. [Tier rules](https://learn.microsoft.com/en-us/azure/storage/blobs/access-tiers-overview#changing-a-blobs-access-tier).

The public [Azure Retail Prices API](https://prices.azure.com/api/retail/prices) was queried for Consumption Storage in East US. The retained local response SHA-256 is `c716419de807d74313890266ec792172dba4afbfdc471a0e0aae65ed93cad356`. Matching General Block Blob v2 USD prices:

| Meter | Unit | Price |
|---|---|---|
| Archive LRS Data Stored | 1 GB/Month | 0.00099 |
| Cool LRS Write Operations | 10K | 0.1 |
| Archive LRS Write Operations | 10K | 0.1 |
| Cool LRS Data Stored | 1 GB/Month | 0.0152 |
| Cool LRS Early Delete | 1 GB | 0.0152 |

Policy version 2 separates the owner's USD20/month steady-state ceiling from the USD2 one-off archive ceiling. The latter includes prior round expenditure, all retry controls, and the full Cool minimum-retention reserve. Existing historical bytes and controls are explicit checkpoint fields; earlier expenditure is not silently counted as this round's new expenditure. Decimal GB (1,000,000,000 bytes) is conservative relative to the service's binary GB storage convention. Archive retention is at least 180 days; no archive deletion or rehydration is admitted here.

The compressed stream is measured locally before creating a network client. No raw TAR is staged. The next admission reserves the measured compressed bytes and three attempts for every block and eight metadata/commit/tier operations. A failed controller stops and preserves its journals; an operator must include partial dispatched controls and any committed blob before resuming from a fresh checkpoint. It cannot reuse stale accounting automatically.

The earlier controller's mixed one-off/monthly estimate remains available only for historical readback mode. New checksum mode requires policy version 2; either mismatched pairing refuses. Tests cover both caps independently, Cool charges, retry accounting, invalid baselines, and refusal before client creation.

The metadata inventory found 82,130 files, 458,651,625,223 logical bytes and 202,187,003,870 allocated bytes. It skipped 13 reparses and reported zero enumeration errors. This is not an eligibility or privacy verdict. Environments, authentication and secret locations, active round controls, referenced replay inputs and pinned runtime contexts remain excluded. Entire Round Eighteen and Round Nineteen directories remain conservatively held pending narrower dependency review. No universal archive-complete or no-bulk-data assertion is made.

The first admitted candidate selection has 100 files / 4,862,985,129 original bytes, source-manifest SHA-256 `555aa8c9fe2337eb2a91175d46a4421cafab00d821b401998bf46ac14e8b3f68`. Metadata measurement reports 1,993,265,077 bytes from Windows GetCompressedFileSizeW; this is potential cleanup allocation, not space already freed. New removal stays an owner action after verified archive proof and current runtime exclusion checks.

Before any network request, the first local compression premeasurement was recorded `INTERRUPTED_BY_OPTIMIZATION` and restarted once at the root's explicit direction. The previous JWT negative scan retried a long base64-like token from every embedded JSON prefix. The optimized scanner keeps the exact credential regex and skips only shorter starts that share the same failing suffix. Randomized/adversarial equivalence and archive tests passed (32 tests). No source, sealed evidence or privacy rule was changed, and the interrupted attempt used zero network requests.

Dated selection correction, 2026-10-13: the first 100-file candidate did not reach an HTTP request. A fresh scan of current acceptance references identified six capture parents (24 files) that must remain runtime inputs; the earlier 89-file hold set covered historical cleanup inputs, not every new archive candidate. The pre-upload source recheck was stopped with `INTERRUPTED_RUNTIME_REFERENCE_HOLD`, preserving its original plan, measurement and reservation. No blob was created, no control charge occurred and no file was removed by that attempt. Selection now scans current code/config references before admitting each subsequent batch and protects all copies of a referenced capture identity. This corrects a selection defect, not an owner's error.

The corrected candidate has 76 files / 3,814,310,643 original bytes, source-manifest SHA-256 `d7eb01054c3424d1e3df69c9e4a3a56df160cbb2e5d65cd59c4a2e085b62e332`. The measured compressed stream is 321,898,401 bytes (77 blocks), SHA-256 `284bef4923aaf405bfee81545313df352c152208b448faa53e4d1bc95c6efb12`. Its admission reserves 255 controls and USD0.00805595088504 one-off, including USD0.00505595088504 Cool minimum-retention reserve and the retained USD0.00045 prior-control allowance. This is an admission, not yet a completed upload or actual bill. Historical failed and interrupted attempts are not relabelled successful.

Measured performance follow-up, 2026-10-13: one retained 159,592,448-byte catalog took 17.56 seconds to revalidate; 14.94 seconds were sealed-tape validation, including 10.63 seconds of SQLite identity scanning. A separate comparison across that catalog's 125,451 text cells / 152,609,370 characters found the same 865,056 UUID occurrences with the original regex and an exact candidate-start optimization. Timed matching was 11.12 seconds versus 4.41 seconds on this sample. The optimization locates a UUID's mandatory first dash in C, then applies the unchanged regex against the original string; Unicode word boundaries, case handling and non-overlapping match order remain intact. Other patterns keep their original path. It changes no cache limit or evidence check, and it is not a claim about all recording performance. Twenty-five tests passed on committed source, including randomized boundary cases and the real-tape unrecorded-identity refusal. The already-running archive tranche keeps its loaded implementation; subsequent processes receive the optimization.
