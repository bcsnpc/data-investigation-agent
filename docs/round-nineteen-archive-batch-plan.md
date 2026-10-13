# Bounded continuation of the historical archive

Recorded 2026-10-13 UTC; supplements the source-export pilot. No local cleanup is admitted: the earlier tool-policy refusal remains in force.

The parent authorized incremental archive storage up to **$2/month**, transfer/control spend up to **$0.50**, with the existing **$13.74/month** platform estimate and overall **$20/month** ceiling preserved. These are limits, not amounts already spent. Each admitted publication also has a **128 MiB measured compressed-byte limit** and a **49-request cap** that persists across restarts. Whole-bundle compression is measured before the first network request. The source scan, member validation, remote download hash and conditional tier proof are unchanged.

## Compression evidence

`archive-compression-sample.json` is retained locally. SHA-256: `92ab23e9e0512c2dc98e9c9402a295d51340849a232ef6617c8ecb2d7d84f1cd`.

The read-only sampler read **268,435,051 bytes**, below its 256 MiB bound, at the beginning, middle and end of small/median/large files in folder-by-file-class strata. It stores only offsets, byte counts and hashes, never sampled raw contents. **90 of 96 strata** received samples. Those samples compressed to **33,713,436 bytes**. Applying each observed ratio to its own stratum projects **47,838,719,717 bytes** from **434,777,780,588 logical bytes**; the other **24,222,949,463 logical bytes** were not sampled. This projection is not a guaranteed compression ratio, a privacy verdict, a full-data scan or permission to upload the entire collection. The actual byte cap, not the projection, governs admission.

The cutoff is the Round Nineteen opening receipt, `2026-10-13T06:08:36.151168+00:00`. The planner skips reparses and captures containing newer files. It balances complete capture directories between rounds, takes every file in a selected directory, and removes the entire directory from admission if one member is quarantined. Explicit prior plans are hash checked; their selected or held paths are not silently selected again. Live/shared-state protections continue to apply. Excluded and interrupted evidence remains local and unchanged.

## First finished-capture batch

Batch 02 contains **166 files / 42 complete directories**, from process-tapes and rounds fifteenâ€“seventeen. Original paths total **245,364,053 bytes**. The lossless bundle has **147 unique members / 217,781,589 bytes**, with every original path mapped to its member. Another **34 files** are held: 12 snapshots without valid sealed tapes, 6 protected-state files and 16 peers excluded to avoid splitting their captures.

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

The `partition` planner divides this same pinned selection by whole capture directory. Tests require exact entry conservation, unchanged hashes and sizes, no duplicates, and refusal if one capture exceeds the bound. Parent exclusions remain recorded against the parent manifest. The three child selections are 20, 18 and 253 files respectively, totaling the same 291 files; original bytes are 711,023,623, 603,494,411 and 483,853,103. Their publication status is recorded separately; selection alone is not an archive result.

The first 100 GB/month internet egress allowance and the subsequent North American premium rate of $0.087/GB are documented by [Microsoft Bandwidth pricing](https://azure.microsoft.com/en-us/pricing/details/bandwidth/). Remaining account-wide free allowance has not been established here, so admission conservatively credits none. Downloading the sampled 47.84 GB compressed projection alone would then be about $4.16, beyond the helper's current $0.50 allocation. This is a conservative estimate, not an invoice or a claim that free allowance is exhausted. Same-region streaming verification in the existing worker could avoid that laptop transfer, but the current archive workflow has not implemented or exercised that split. It would need exact streamed-byte proof and an unchanged object ETag before tiering, not metadata-based verification.

## Completed subdivisions

| Batch | Original files | Original bytes | Stored bytes | Blob controls | Verified receipt SHA-256 |
|---|---:|---:|---:|---:|---|
| 03-0 | 20 | 711,023,623 | 65,438,324 | 25 | `31e7c326bc916d13df90e81e4113c0da8b539c0a1dff1ccf1ef7930f29a13d21` |
| 03-1 | 18 | 603,494,411 | 55,658,328 | 22 | `b3632d26bd605bfbc07cabee81750c886fab415c4c316aaa6691f758ebbc2b88` |
| 03-2 | 253 | 483,853,103 | 46,232,072 | 21 | `8a3abc172c4651c99dc82f12a23aa9bb94b1a864863e6008864cd8ab37fc8660` |

Every member and whole remote bundle hash matched; Archive tier was confirmed. Batch 03-2 first failed before dispatch because the gateway environment variable received JSON text instead of its policy-file path. That failure log is retained; the policy was unchanged. Batch 03-0 finished remote proof but its final local seal check failed with `ModuleNotFoundError: No module named 'jsonschema'` in the Azure CLI Python environment. It resumed from the same durable journal using the existing full Python runtime plus the installed Azure SDK packages. The one additional HEAD and all earlier controls are counted. No object was overwritten or reuploaded to make the receipt pass.

The publication path now validates source seals and runtime dependencies before any remote mutation, and repeats the check before deriving original-file receipts. A regression test makes missing dependencies fail with zero remote calls. The direct per-file streaming command also accepts a required measured `--max-stored-bytes` bound, checked before requests, and reports unique remote storage rather than double-counting duplicated source paths. This option avoids any bundle staging copy; request, privacy and exact-byte guards still apply.

The aggregate checkpoint is in [the machine-readable archive progress](round-nineteen-archive-progress.json). At this checkpoint, 482 original paths / 2,347,822,385 bytes are preserved in 209,162,299 stored bytes with 98 Blob controls. No original was deleted; free disk is lower because staging and concurrent root work remain. Full historical coverage and local cleanup remain incomplete.

## Direct-stream checkpoint, 2026-10-13

Batch04 archived one complete four-file capture without a local body copy: 154,311,703 original bytes, 15,819,180 stored bytes, 39 controls (16 HEAD, 8 GET, 15 PUT). Manifest `4f96058fedace5fe522af2a5f7303187f01ef3d7e84bd3d885f767ceb5363100`; receipt `6c451eebbb3f0fd2f90e0986046ce8e8c8bf0865ca82ef729b380d9fd9418a17`. Each remote object matched its original SHA-256 before conditional Archive tiering. The earlier three-file selection was empty and remains recorded; no file was split out to force admission.

The [second aggregate checkpoint](round-nineteen-archive-progress-02.json) pins the first checkpoint and records 486 original paths / 2,502,134,088 original bytes, 224,981,479 stored bytes and 137 Blob controls. There were zero estate investigation reads, zero model calls and zero original deletions. The transfer estimate conservatively credits no free egress allowance; estimated archive storage is below $0.001/month and transfer plus transactions below $0.03, not an invoice. All totals remain within the helper allocation. Free disk remains only slightly above the 10 GiB floor; no additional staging bundle is admitted.

The integrated platform-literal check found transport implementation in the neutral archive module. That implementation now lives in `adapters/platform_archive_client.py`, retaining the existing public import and unchanged receipt semantics. No debt allowance was raised. The literal sweep and focused archive tests passed 17/17; new live admissions paused during the correction, and the already-running batch04 finished safely.

## Checkpoint 03: streamed bundles, 2026-10-13 08:08 UTC

Batch05 archived 200 paths / 662,379,820 original bytes as 69,505,445 stored bytes using 26 controls. Batch06 archived 198 paths / 727,933,616 original bytes as 69,815,967 stored bytes using 25 controls. Both stream deterministic TAR and gzip directly: no archive body is staged on disk. The complete remote decompression hash proves the original TAR byte stream; its hash-pinned member manifest maps every original file. Originals are rechecked before and after publication, and remain unchanged.

The new [checkpoint](round-nineteen-archive-progress-03.json) counts the source export **once**, then all seven capture batches: **884 original paths, 3,892,447,524 original bytes, 364,302,891 stored bytes and 188 platform controls** (46 HEAD, 23 GET, 119 PUT). Successful uploaded archive payload and fully verified downloaded payload are each exactly 364,302,891 bytes. Three retained failed STAGE attempts each offered 4,194,304 bytes; their partial wire transfer is unknown, bounded by 12,582,912 additional upload payload bytes. This is payload accounting, not a claim to measure HTTP/TLS framing or small metadata responses.

Conservative estimates without crediting any free egress: **$0.031694351517** download egress, **$0.00188** controls, and **$0.00036065986209/month** Archive storage. These are estimates, not an invoice. The three transient failures are included in the 188 controls. No estate request, model call or local deletion occurred. Free D: space at the checkpoint was **10,827,874,304 bytes**, only 90,456,064 bytes above the 10 GiB admission floor. No new large disk-usage scan was run; this is the operating system's volume counter.

The parent expanded its internal transfer allocation from $0.50 to **$4.50**, with the existing **$20/month platform ceiling** unchanged. It did not raise an owner budget. The continuation policy allows at most 50 GB stored, reserves every next batch's full 128 MiB / 49 controls before admission, counts Archive storage and paid download egress conservatively, and keeps a $0.50 control allowance. Source-only upload is free ingress under the referenced pricing; unknown failed-upload wire bytes are still recorded rather than erased.

The decoded-event credential scan now covers sidecars as well as the tape envelope. A retrospective local check scanned 110 already-published event sidecars with zero pattern matches; this is a bounded pattern check, not a universal sensitive-data certification. The exact same credential patterns now use a mandatory-prefix fast search before matching. One 8 MiB sample took 0.9556 seconds with the canonical whole-buffer scan and 0.0610 seconds with the prefix scan, with identical result; equivalence tests cover the original patterns, case variants and random buffers. None of these checks changes sealed tape bytes.

## Prepared controller; not launched

`archive_background.py` supports a bounded, observed continuation. It takes a SHA-pinned config and accounting checkpoint, scans only complete eligible captures before the original cutoff, remembers prior selected/held paths, and refuses changed sources, seals, unknown encodings or credential-pattern matches. Each batch emits incremental ADMITTED / VERIFIED JSON and fsyncs its journal. Cost and disk checks happen before selection and before cloud admission. An explicit UTC deadline or owner STOP marker closes admissions; an already-admitted transfer finishes or records its failure, and no successor starts. Any exception stops the whole controller. It never deletes originals or local staging.

Local plan `.local/round-nineteen/archive-controller-plan-01.json`, SHA `b9c6c87716cb77ce4adac447373e80ffd94726074f4bf0507b312373319f3ffe`, pins checkpoint SHA `ba3e1b6a0b630553a577288c6238c2a4361a37dd9397e95dcd32a7374ea2b119`. It permits at most four batches, each <=700 MiB original selection / 200 files / 128 MiB stored / 49 controls, with no admission after **08:45 UTC on 2026-10-13**. Changing the deadline or checkpoint requires a new explicitly reviewed config hash. This plan has not run. Only one controller/manual archive executor may use this checkpoint; concurrent use is forbidden because these archive counters are not a transactional shared ledger.

After root review, from the integrated worktree:

```powershell
$env:PYTHONPATH='scripts;D:/data_investigation_agent/.local/azure-cli-env/Lib/site-packages'
$env:DIA_GATEWAY_POLICY='D:/data_investigation_agent/.local/round-nineteen/source-export-archive/gateway.json'
C:/Users/chait/anaconda3/python.exe scripts/archive_background.py --config D:/data_investigation_agent/.local/round-nineteen/archive-controller-plan-01.json --config-sha256 b9c6c87716cb77ce4adac447373e80ffd94726074f4bf0507b312373319f3ffe --output D:/data_investigation_agent/.local/round-nineteen/archive-controller-run-01
```

Do not relaunch this controller using stale accounting after interruption. Resume only that batch via `archive_streaming_bundle.py publish` with its original source/bundle plans and `progress.jsonl`; dispatch counts remain charged. Reconcile all partial and successful controls into a new pinned checkpoint before admitting another controller. Preserve the failed config/output folder. Creating `.local/round-nineteen/ARCHIVE-STOP` prevents the next admission. Root must observe the process and close admission before round closure; no unattended admissions are left running by this task.

Offline regression: **19 passed** across controller, streaming TAR conservation/resume, archive cap tests and platform literal sweep. The first controller test exposed mutable previous-plan aliasing; it was fixed by snapshotting the list before hashing. No controller cloud request occurred before or after that fix. Deadline and stop-marker tests prove zero clients are constructed after closure.

This remains a **partial archive**. The opening inventory of 32,352 files / 459,000,730,051 logical bytes includes material not admitted by the whole-capture planner. Protected/live files, invalid snapshot seals, opaque containers and quarantined peers remain local. No claim that the entire historical collection is archived, universally secret-free or free of bulk client rows is made. Cleanup is still blocked by tool policy; all originals remain.

## Checkpoint 04: observed controller completed, 2026-10-13 08:31 UTC

Root ran the reviewed four-batch controller to completion (session67231, exit0). It added **424 paths, 2,925,681,702 original bytes, 294,262,540 stored bytes and 106 platform controls**. Last VERIFIED event: `2026-10-13T08:27:03.209012+00:00`. Result SHA-256: `4b3799ee6c1ae4fc5ab8a384db62767c9ff963f4cb8cfb6f68e96cb870f1f8f4`.

| Controller batch | Paths | Original bytes | Stored bytes | Controls |
|---|---:|---:|---:|---:|
| 0000 | 88 | 733,966,202 | 75,116,155 | 26 |
| 0001 | 80 | 733,744,665 | 74,901,255 | 26 |
| 0002 | 56 | 733,991,546 | 76,407,484 | 28 |
| 0003 | 200 | 723,979,289 | 67,837,646 | 26 |

Cumulative, including the source export exactly once: **1,308 paths / 6,818,129,226 original bytes / 658,565,431 stored bytes / 294 controls** (62 HEAD, 31 GET, 201 PUT). Successful upload payload and verified download payload are each 658,565,431 bytes. Five failed 4 MiB STAGE attempts across all batches are included in the controls; partial failed-upload wire bytes remain unknown, with a 20,971,520-byte payload upper bound. Two of these failures occurred in the controller; both resumed without losing conservation or exceeding their 49-control caps.

The [fourth checkpoint](round-nineteen-archive-progress-04.json) pins the prior checkpoint and individual receipts. Offline reconciliation checked each new receipt SHA, source manifest/member `(path, SHA, bytes)` conservation, complete journal hash chain, successful stage-byte sum, whole-download hash equality, final Archive proof and dispatched-control count. These are checks of retained live receipts; reconciliation made **zero cloud requests, zero model calls and zero bulk-source reads**.

Cumulative estimates, not invoices: **$0.057295192497** paid egress with no free allowance credit; **$0.00294** controls at the conservative all-write rate; **$0.00065197977669/month** Archive storage. Combined with the conditional $13.74 platform baseline, the same-month conservative projection is **$13.80088717227369**, below $20. Disk free at reconciliation: **11,491,274,752 bytes**. No deletion savings are attributed to this change; other work was concurrent and all archive originals remain.

**Ledger/delivery note — 2026-10-13:** Owner Round Nineteen authorizes private, identity-authenticated historical archives after SHA verification. Root executed the reviewed controller under the existing platform-only storage identity scope and cost allocation; this checkpoint records its four finished publications and all 106 controls, including failed attempts. Every original is retained because deletion remains policy-blocked. No identity, role, secret, model/estate limit or acceptance expectation changed. No new uploads/jobs were admitted for this reconciliation. The historical archive remains partial, not complete; protected, opaque, invalid-seal and unselected material remains local. No universal no-bulk/no-secret assertion is made.
