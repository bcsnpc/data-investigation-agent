# Round Nineteen archive and storage hardening

Recorded 2026-10-13 UTC. The bounded legacy-export archive is verified; local cleanup is blocked by tool policy. The full historical archive has **not** been uploaded. No model call or estate data read was made by this work.

## Inventory and cost before admission

`round-nineteen-archive-input-inventory.json` inventories file names, logical sizes and NTFS allocation. It is not a privacy approval or universal recording-content audit. It found 32,352 files across rounds five–seventeen and process-tapes: **459,000,730,051 logical bytes**, **201,197,826,530 allocated bytes** from `GetCompressedFileSizeW`. Deduplicating Windows file IDs did not reduce that allocated total. Thirteen Round Fourteen replay reparse points were skipped; their targets were not traversed. Protected ledger/catalog names and opaque containers are counted but do not become eligible merely by appearing here. This retains the narrower Round Eighteen audit limitations, including its two catalog read errors and unexamined opaque contents.

Using the retained East US retail rates in `cloud-retail-rates.json`, an intentionally uncompressed 459 GB upper scenario costs about **$0.46/month in Archive**, or **$9.55/month if left Hot for a full month**, before operations and transfer. These are incremental storage scenarios, not a new total platform estimate. Compressed storage, deduplication, eligibility and actual time in Hot tier remain unmeasured for the whole collection. A full local download for SHA verification could cause hundreds of GB of outbound transfer. The previous 250 GB assumption cannot authorize that transfer under the $20 platform ceiling. No full transfer was admitted.

Archive retention has a 180-day minimum billing period; early deletion/rehydration has charges. See [Microsoft access tiers](https://learn.microsoft.com/en-us/azure/storage/blobs/access-tiers-overview/) and [archive billing guidance](https://learn.microsoft.com/en-us/azure/storage/blobs/archive-blob). Prices are estimates, not an invoice. A future large batch should measure its compressed size first and verify in the same Azure region where appropriate, with compute and controls included in its approved estimate.

## Bounded duplicate export: actual result

The owner approved archiving the duplicate legacy bulk source export and then deleting both verified local copies. These are **bulk source rows**, not merely investigation metadata. The original two directories contained 25 files totaling **304,087,195 bytes**. The ten data files were identical, but the two manifest/receipt sets and one Bronze plan were distinct. All unique material was retained: **15 unique members / 152,090,749 bytes**, plus the exact mapping of all 25 original paths.

The lossless tar is 152,115,200 bytes. Its streaming gzip stored **17,369,676 bytes** in the private `archive` container of `diaplatformd5dd7d65`. The pre-admission cost bound was **$0.10** and **49 Blob controls** across restarts. At the retained rates, the stored bytes alone cost under $0.00002/month in Archive; even conservatively charging this small verification transfer and all 49 controls remains under the admitted bound.

| Proof | SHA-256 |
|---|---|
| Original 25-path manifest | `835af4c7b4311bcc2e58f0a0fa18aa3844cd776021eecf98a3b329716e7dd788` |
| Uncompressed bundle | `857ad2bd15ef7a14c651b7c3b6216a13e5509bfb07b5777a79d3050c2097b418` |
| Bundle publication plan | `ce2e963c4fd9c70ba906c31ae273eb74ec5e2f003c44dcb9f8fbd785d4536085` |
| Completed archive receipt | `ba43043769c87368ab4c4649a1e9c32da62acc0ff661b14067b8cebbde7546e6` |

Every member's hash and size were verified locally. The uploaded gzip was then downloaded in full, decompressed with a bounded decoder and checked against the exact uncompressed bundle SHA. The unchanged Hot object's ETag was checked, tiering was conditional on that ETag, and Archive tier was confirmed. This proves the remote container has the same verified members without treating a metadata-only HEAD as a content check. The receipt records original and compressed hashes separately.

The existing owner CLI identity used token authentication after the parent applied the separately approved, platform-storage-only Blob Data Contributor grant. No account key, new identity, new role grant, or credential file was created by this helper. The first network attempt retained two successful blocks before a connection reset; the resumed attempt reused them. Total **16 platform controls: 5 HEAD, 3 GET, 8 PUT**, including the failed PUT. Controls are separate from estate investigation reads. Two pre-network setup failures are retained as well: an unnecessary `azure.identity` import, then Azure CLI rejecting simultaneous `--tenant` and `--subscription`. The corrected explicit CLI path pins the subscription and checks both returned subscription and tenant; it never changes authority.

Local receipt directory: `.local/round-nineteen/source-export-archive/`. It contains `before.json`, `after.json`, all failed/successful publication logs, the hash-chained progress journal, control receipts, privacy review, bundle plan and final receipt. `round-nineteen-source-export-archive-result.json` is the secret-free summary.

**Cleanup was rejected before launch**: `CreateProcess rejected: blocked by policy`. No alternative deletion was attempted. All 25 originals remain; the prepared owner script is `.local/round-nineteen/source-export-archive/cleanup-verified.ps1`. It rechecks resolved containment, reparse points, size and SHA for each file and records each removal. It deletes individual verified files only, never recursively. After successful owner execution the two empty source directories may be removed separately. The historical source-snapshot registry has not been rewritten to pretend those files are locally available. This document and the archive receipt are the cold-storage pointer.

At the post-attempt measurement D: free space was **11,915,845,632 bytes**. Concurrent work means this difference from the earlier measurement is not attributable solely to archiving. No space saving is claimed while cleanup remains blocked.

## Implementation and repeatable operator path

- `inventory_archive_inputs.py` performs a read-only size/allocation inventory, skipping reparses.
- `archive_finished_rounds.py plan` accepts explicit file paths for finished rounds five–seventeen/process-tapes, protects live state and quarantines credentials/opaque containers. Source exports require a separately explicit root list and a versioned manifest.
- `archive_finished_rounds.py upload-resumable` uses deterministic 4 MiB blocks, immutable commit, a manifest/remote-bound fsynced hash-chain journal, full download verification and conditional tiering. The explicit control cap persists across restart. HTTP 429/temporary server errors and transport resets get at most three attempts; authentication refusals do not retry. No local delete happens in publication.
- `archive_source_exports.py build` produces one deduplicated bundle containing the full original path manifest and every unique byte stream. `publish` applies the same remote proof and derives member cleanup receipts only after bundle verification. Extra, missing, changed or trailing members fail validation.
- `platform_blob_transfer.py get|put` replaces fixed owner bootstrap transfers: existing CLI identity only, exact gateway URL, SHA-pinned local input/output, immutable upload, bounded single transfer, retained partial downloads. Managed-identity CAS/recording paths remain unchanged.

The source batch's concrete build invocation is retained in the local bundle plan. Its manifest is committed as `round-nineteen-source-export-archive-plan.json`. Publication requires explicit `--tenant`, `--subscription`, `--azure-cli-python`, `--gateway-channel`, `--max-control-requests`, SHA-pinned manifest/bundle plan, privacy review, output and journal. No token or password is an argument. The gateway operator policy uses:

```json
{"version":1,"live_enabled":true,"identities":{"owner-source-archive":{"role":"platform","platform_archive":[{"account_url":"https://diaplatformd5dd7d65.blob.core.windows.net","container":"archive"}]}}}
```

That declaration alone cannot dispatch arbitrary URLs. Trusted archive code binds one exact operation, content-derived key, request-body SHA and required conditional headers for each send. There is no wildcard route or container-wide client tool.

## Shared-key hardening status

Tracked storage runtime callers already use explicit identity credentials. Fourteen private Round Eighteen operator scripts used `listKeys`; their names and original hashes are preserved in `round-nineteen-retired-storage-callers.json`. They are historical evidence and must not be used for new work. The identity-only transfer/archive commands replace their get/put/archive roles; CAS callers must inject the explicit owner token credential or existing managed identity, never a key. No historical script was silently rewritten.

The Bicep desired state now sets `allowSharedKeyAccess: false`. **This helper did not deploy or disable it live.** The parent must first confirm no active operator process relies on a retired script, move remaining orchestration to identity, then apply and read back the setting. A desired-state file is not evidence that live shared-key access is disabled.

## Validation

Forty focused tests pass with `pytest -n auto`: interruption/resume, block reuse, immutable publication, remote corruption, cold-resume proof, journal tampering, source mutation, duplicate conservation, missing/changed/trailing members, source-scope approval, token-only credentials, CLI subscription/tenant pinning, transient retry, authentication refusal, control-cap conservation, exact gateway bodies and conditional tiering, gzip raw/stored hashes, partial-download retention and cleanup containment. These tests use synthetic local/fake transport data; the bounded source archive is the separately recorded live check. No universal archive/privacy audit or full-batch completion is claimed.
