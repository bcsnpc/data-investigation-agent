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
