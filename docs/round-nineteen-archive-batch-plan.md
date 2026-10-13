# Bounded continuation of the historical archive

Recorded 2026-10-13 UTC; supplements the source-export pilot. No local cleanup is admitted: the earlier tool-policy refusal remains in force.

The parent authorized incremental archive storage up to **$2/month**, transfer/control spend up to **$0.50**, with the existing **$13.74/month** platform estimate and overall **$20/month** ceiling preserved. These are limits, not amounts already spent. Each admitted publication also has a **128 MiB measured compressed-byte limit** and a **49-request cap** that persists across restarts. Whole-bundle compression is measured before the first network request. The source scan, member validation, remote download hash and conditional tier proof are unchanged.

## Compression evidence

`archive-compression-sample.json` is retained locally. SHA-256: `92ab23e9e0512c2dc98e9c9402a295d51340849a232ef6617c8ecb2d7d84f1cd`.

The read-only sampler read **268,435,051 bytes**, below its 256 MiB bound, at the beginning, middle and end of small/median/large files in folder-by-file-class strata. It stores only offsets, byte counts and hashes, never sampled raw contents. **90 of 96 strata** received samples. Those samples compressed to **33,713,436 bytes**. Applying each observed ratio to its own stratum projects **47,838,719,717 bytes** from **434,777,780,588 logical bytes**; the other **24,222,949,463 logical bytes** were not sampled. This projection is not a guaranteed compression ratio, a privacy verdict, a full-data scan or permission to upload the entire collection. The actual byte cap, not the projection, governs admission.

The cutoff is the Round Nineteen opening receipt, `2026-10-13T06:08:36.151168+00:00`. The planner skips reparses and captures containing newer files. It balances complete capture directories between rounds, takes every file in a selected directory, and removes the entire directory from admission if one member is quarantined. Explicit prior plans are hash checked; their selected or held paths are not silently selected again. Live/shared-state protections continue to apply. Excluded and interrupted evidence remains local and unchanged.

## First finished-capture batch

Batch 02 contains **166 files / 42 complete directories**, from process-tapes and rounds fifteen–seventeen. Original paths total **245,364,053 bytes**. The lossless bundle has **147 unique members / 217,781,589 bytes**, with every original path mapped to its member. Another **34 files** are held: 12 snapshots without valid sealed tapes, 6 protected-state files and 16 peers excluded to avoid splitting their captures.

| Artifact | SHA-256 |
|---|---|
| Selected original manifest | `e50adb78781bacd758153301511b211c50a6d6c5ae1c410ff9fef1a0cf5686d5` |
| Exact uncompressed bundle | `a84f1d22fec852222473c0cd9da1aeec76c8b9886ec2ce96679fd2fcb615d6a0` |
| Publication plan | `71e92ddbda6bfa9728f32af22d1cc24dd4f501a0c9e3e5e9a3fc1b475c4cbfce` |
| Verified Archive receipt | `9153c71ab4f9f29a63a5339cd1df1c4c284b5650554d175794a63ad4631924d5` |

Publication completed using the existing owner token identity after account-key access was disabled by the parent. **24,463,899 stored bytes; 14 Blob controls**. Whole-download SHA and Archive tier confirmed. No deletion attempted. Combined with the source export, this is **30 controls and 41,833,575 stored bytes**. These are platform controls, with zero model calls and zero estate investigation reads.

## Repeatable bounded steps

1. Run `plan_archive_batches.py sample` once against the root and opening cutoff; no cloud call occurs.
2. Run `plan_archive_batches.py batch --max-original-bytes ... --max-files ... --protected-paths ... --previous-plans ...`. Keep its quarantined directories and prior plan hashes.
3. Build the bundle using `archive_source_exports.py build`. For larger raw captures use `--bundle-compression gzip --max-staging-bytes 134217728`. This streams directly into bounded compressed staging, never creates a bulk uncompressed temporary, and reserves a 10 GiB disk floor before writing. An exceeded bound leaves a partial artifact and refuses publication.
4. Check the specific manifest and write a privacy review against its exact hash. A sample size estimate is not that review. Quoted JSON credential keys and decoded tape-event bytes are scanned; opaque/undecodable material is refused rather than presumed harmless.
5. Use `archive_source_exports.py publish` with `--max-stored-bytes 134217728 --max-control-requests 49`, the approved token identity, pinned manifest/plan and a new durable journal. Sum receipts and dispatched controls across batches against the overall approved caps. Do not admit a batch if its conservative incremental cost would exceed the remaining ceiling.
6. Retain all original files, failures and receipts. The owner cleanup script is a separate action; this session must not bypass the policy refusal.

Compressed staging may be gzip wrapped by the existing archive gzip transport. Both layers are lossless: the remote proof covers the exact staged container, and its member proof covers every original byte stream. This avoids changing old archive contracts or requiring uncompressed disk space for a large snapshot. It does not rewrite sealed tape bytes or interpretations.

The remaining collection is not complete merely because a batch succeeds. Report admitted, archived, quarantined, interrupted and not-attempted sets separately. The retained Round Eighteen schema audit limitations remain; no universal no-bulk or no-sensitive-data claim is earned here.

## Larger-batch refusal and subdivision

Batch03 selected 291 files in 74 complete captures, 1,798,371,137 original bytes. Its manifest is `f998af3770cd0b5e1cbc7cecd48baf87b25e310b73e1eaffea384b3f901b9b79`; six snapshots without valid sealed tapes and three peers remain excluded. Gzip staging stopped at `investigator.artifact_store.ArtifactError: ARCHIVE_STAGING_BOUND`, before any network request. The partial gzip and failure record remain under `.local/round-nineteen/archive-batch-03/`. No original changed and no cap increased.

The `partition` planner divides this same pinned selection by whole capture directory. Tests require exact entry conservation, unchanged hashes and sizes, no duplicates, and refusal if one capture exceeds the bound. Parent exclusions remain recorded against the parent manifest. The three child selections are 20, 18 and 253 files respectively, totaling the same291 files; original bytes are711,023,623,603,494,411 and483,853,103. Their publication status is recorded separately; selection alone is not an archive result.

The first100 GB/month internet egress allowance and the subsequent North American premium rate of$0.087/GB are documented by [Microsoft Bandwidth pricing](https://azure.microsoft.com/en-us/pricing/details/bandwidth/). Remaining account-wide free allowance has not been established here, so admission conservatively credits none. Downloading the sampled47.84 GB compressed projection alone would then be about$4.16, beyond the helper's current$0.50 allocation. This is a conservative estimate, not an invoice or a claim that free allowance is exhausted. Same-region streaming verification in the existing worker could avoid that laptop transfer, but the current archive workflow has not implemented or exercised that split. It would need exact streamed-byte proof and an unchanged object ETag before tiering, not metadata-based verification.
