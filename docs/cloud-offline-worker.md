# Offline cloud worker

The public image contains tracked Python source, dependency declarations, and
PowerShell source used by synthetic contract tests. The staging command rejects
data JSON, databases, receipts, captures, installations, `.local`, `.git`, and
untracked files. It does not package private evidence or secrets. Its source
manifest records each included file's SHA-256.
The only JSON source exceptions are two named scalar code policies:
`WorkerResponseBounds.json` and `intake-resolution-policy.json`. Neither holds
estate data, identities, endpoints or evidence. Their bytes participate in the
engine fingerprint and cannot be omitted from a working image.

`Cloud worker offline foundation` builds on PR/main and runs eight synthetic
contract shards with Docker networking disabled, a read-only filesystem, no
capabilities, a non-root user, and a separate writable results directory. These
shards test transport, tape, accounting and native-reader contracts. They are
**not** the sealed historical acceptance score. The existing acceptance workflows
continue independently and are not weakened or replaced.

GHCR publication occurs only on a manual workflow dispatch with `publish=true`,
after all eight shards pass. The image uses a commit tag and records its registry
digest. Deploy by that digest. Package visibility is an owner/operator action;
this workflow does not change visibility or any estate setting. Build sources
are public-repository code; do not put private fixture values in source literals.

The image includes Microsoft ODBC Driver 18 using Microsoft's documented Debian
12 package route. Authentication comes from the separately configured managed
identity when a future live entrypoint is admitted; this entrypoint has **no live
mode**. See [Microsoft's Linux ODBC installation instructions](https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server).

## Sealed replay jobs

Mount evidence read-only at `/evidence`, a full public git checkout with all
recorded engine revisions at `/repo`, and a private writable output volume at
`/results`. Do not bake or upload those mounts into the image. Supply:

```text
--mode replay --repo /repo --manifest /evidence/replay-manifest.json
--evidence /evidence --output /results --shard 0 --shards 8
```

Dispatch one job for each shard 0 through 7. The manifest has `version: 1` and
`entries`, each with `id`, `tape_path`, `tape_sha256`, and `engine_revision`.
Optional `estate_manifest_path` and `estate_manifest_sha256` must appear together.
All artifact paths are relative to the evidence mount and hash-checked before
replay. The exact recorded engine is loaded from git, with network disabled in
the replay subprocess. No git fetch, provider or estate request is attempted.
Each shard writes counts and per-case match/error-type results without raw
failure text in public logs. Preserve the private full replay outputs on the
output volume. Join all eight shard files before claiming complete coverage.

The worker always sets the live-access kill switch. The deployment must also
deny egress for replay jobs; Docker CI supplies `--network=none`. Azure job
network isolation is deployment configuration and is not established by an
environment variable. No cloud job or image was deployed by adding these files.
