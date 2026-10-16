# Finished-round archive and snapshot conversion

`scripts/archive_finished_rounds.py` is an operator migration tool, never an
investigation tool. No command removes files. `cleanup-script` generates an
owner-reviewable PowerShell file; running it is a separate action under the
owner's existing archive-deletion approval and tool policy. This implementation
was tested with synthetic files and an in-memory remote only. No upload,
conversion of historical evidence, tier change or deletion is claimed here.

The candidate scope is explicit individual paths beneath `.local/round-five`
through `.local/round-fifteen` (including suffixed round work folders), and
`.local/process-tapes`. The operator must assert these are finished and supply
the current shared-state protection list. No recursive candidate scan or glob
is admitted. Paths outside the workspace, links and junctions are refused.
Known ledger/budget/usage/pot filenames are protected even inside old rounds;
this includes `.local/round-thirteen/model-spend.sqlite`. Shared catalog and
inventory roots are protected. Only snapshots in tape/capture/replay directories
are eligible; the explicit protection list overrides even that allowance.

## Privacy quarantine precedes upload

A plan is SHA-256 pinned and starts `QUARANTINED_PENDING_REVIEW`. Sensitive paths,
private-key/JWT/Bearer/password patterns and opaque compressed/encrypted containers
are excluded, with reasons. This is a conservative screen, not proof that an
arbitrary database contains no secret. A reviewer must inspect the remaining
files, including SQLite pages and model bodies, and supply a separate review:

```json
{"status":"APPROVED","manifest_sha256":"<exact plan SHA>","reviewer":"<name>","basis":"<what was inspected and why upload is permitted>"}
```

The review cannot de-quarantine excluded files. Correcting a plan creates a new
manifest/hash/review. Raw legacy tapes are never relabelled privacy-projected or
redacted during migration: that would change sealed evidence. An installation
whose evidence requires projection must use the capture-time privacy format;
this legacy EXACT conversion refuses projected tapes. Quarantined originals
remain on disk and cannot enter a cleanup script. The archive is private Blob
storage; this command does not publish a release or broaden evidence access.

## Invocation sequence

```powershell
python scripts/archive_finished_rounds.py plan --workspace D:\dia-round-eleven-links --files .local/archive-files.json --protected-paths .local/archive-protected.json --finished-statement "Finished rounds 5–15 and old sealed tapes; active shared files excluded" --output .local/archive-manifest.json
python scripts/archive_finished_rounds.py upload --manifest .local/archive-manifest.json --manifest-sha256 <printed-sha> --privacy-review .local/archive-review.json --account-url https://<platform-account>.blob.core.windows.net --managed-client-id <explicit-client-id> --gateway-channel <platform-archive-channel> --output .local/archive-receipt.json
python scripts/archive_finished_rounds.py cleanup-script --manifest .local/archive-manifest.json --manifest-sha256 <printed-sha> --receipt .local/archive-receipt.json --receipt-sha256 <printed-receipt-sha> --output .local/cleanup-archived.ps1
```

Both JSON path lists contain workspace-relative file paths. Output files use
exclusive creation; there is no overwrite flag. Gateway policy must explicitly
allow the platform archive channel. Only explicit managed identity is used;
there is no operator CLI credential fallback in this CLI.

Every object uploads once in **Hot**, downloads as a stream and verifies full
SHA-256 and size, then changes to **Archive** with an ETag precondition. The
receipt requires confirmed Archive tier, ETag and downloaded SHA. A corrupt
download never advances tier or permits deletion. An interrupted batch can
leave unreceipted remote objects; those do **not** authorize local cleanup.
Existing objects refuse overwrite. Recovery requires checking the actual blob
and issuing a fresh verified receipt; no guessed success or blind overwrite.

Cleanup embeds only individually verified files. It rechecks absolute workspace
bounds, every ancestor for reparse points, size and SHA immediately before each
`Remove-Item -LiteralPath`. It never uses recursive deletion, logs each removed
file and its actual byte count, and prints the total. Archive retention cost and
rehydration delay remain; Archive is not an instant replay source.

### Optional lossless gzip storage

Add `--storage-encoding gzip` to **plan** to pin compression in the reviewed
manifest. Existing manifests without this field remain raw `identity` storage;
their original receipts and cleanup authorization remain valid. Choosing gzip
changes the manifest hash and requires its own privacy review. Compression does
not change any source file, tape event or original SHA-256 expectation.

The upload iterator reads one MiB at a time, compresses with a gzip wrapper and
streams directly into Blob's block upload. There is no whole-file buffer or
temporary compressed disk copy. Blob upload concurrency is one. The SDK's
[documented iterable upload interface](https://learn.microsoft.com/en-us/python/api/azure-storage-blob/azure.storage.blob.blobclient)
provides bounded block transfer. The `.gz` object key distinguishes it from a
previous raw copy without overwriting either.

Verification streams the downloaded gzip through a bounded decompressor and
checks the **original** byte count and SHA-256 from the manifest. It separately
checks stored byte count and SHA against the uploaded encoded stream. Corrupt
CRC/trailer, truncation, extra concatenated members/trailing bytes, excess
decompressed bytes, original-hash mismatch or ETag change prevent Archive tier
and prevent cleanup authorization. Originals remain local until verification
and tier confirmation have succeeded.

Every new receipt reports `original_bytes`, `stored_bytes`, `stored_sha256` and
`storage_encoding` per object, plus both byte totals for the batch. These are
observed streamed counts, not a compression estimate. Cleanup always rechecks the
original local file's hash and original length. Compression can reduce transfer
and storage; it is optional and does not itself establish a cost-budget block.

## Conversion and honest replay status

```powershell
python scripts/archive_finished_rounds.py convert --manifest .local/archive-manifest.json --manifest-sha256 <sha> --privacy-review .local/archive-review.json --tape-directory .local/process-tapes/<sealed-run> --local-cas .local/snapshot-cas --output .local/<run>-bundle.json
```

All original tape and snapshot files must appear in the reviewed manifest.
`tape_bundle.pack` stores unchanged original tape/event bytes and content-addressed
snapshot chunks using the existing `Files` API. Materialization reconstructs
every byte and validates the original seal. The report states
`byte_restoration: PASSED` and **`engine_replay: NOT_RUN`**. That is intentionally
distinct from replaying the full engine: the existing entry-point-specific
offline replay harness must subsequently run both the original and materialized
tape and compare its outcome. This tool does not fabricate that result or claim
space freed while originals remain. CAS deduplication and disk savings can be
measured only after actual conversion and approved verified cleanup.
