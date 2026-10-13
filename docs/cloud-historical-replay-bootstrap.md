# Historical cloud replay bootstrap

`python scripts/cloud_replay_bootstrap.py --config /config/replay.json` is a fixed
entrypoint. It downloads one private, SHA-256 pinned transit package; there is no
command, shell, credential, estate configuration or arbitrary endpoint argument.

Configuration is non-secret and closed:

```json
{
  "version": 1,
  "input_url": "https://YOURACCOUNT.blob.core.windows.net/tapes/pilot.tar.gz",
  "input_sha256": "64 lowercase hex characters",
  "result_url": "https://YOURACCOUNT.blob.core.windows.net/captures/replay-shard-0.json",
  "identity": {"mode": "managed_identity", "client_id": "UUID", "tenant_id": "UUID", "principal_id": "UUID"},
  "channel": "worker-platform-artifacts",
  "max_download_bytes": 1073741824,
  "max_expanded_bytes": 4294967296,
  "shard": 0,
  "shards": 8
}
```

Use a real lowercase account name and canonical UUIDs. The deployment separately
mounts `DIA_GATEWAY_POLICY` granting this channel GET on the exact input URL and
PUT on the exact result URL, purpose `platform_blob`; never wildcard access.
Each shard has its own immutable result URL (`If-None-Match: *`). The platform
identity needs only the previously approved artifact container scope. MSI token
acquisition is authentication-plane traffic, separate from replay evidence reads.

The gzip tar must contain only `engine.bundle`, `replay-manifest.json`, and
`evidence/...`. The Git bundle must contain every immutable engine revision named
in the manifest. The manifest uses `cloud_offline_worker.py` version 1, with paths
relative to `evidence/`. Include each native tape directory and all its snapshot
files unchanged. The package is a transit copy, not a replacement for CAS or the
original tape. Packaging/publication requires the existing evidence privacy
review; the bootstrap does not certify that a package contains no secrets.

Archive extraction refuses absolute/traversing paths, links, device nodes,
packaged `.git` directories and undeclared roots. Hash and compressed/expanded
size checks precede engine execution. Git receives only local bundle fetches of
40-hex revisions; ambient Git configuration is disabled. Trusted compatibility
helpers come from the image, and the historical engine comes from its pinned Git
revision. No packaged hooks/config are executed.

The fixed worker subprocess has a minimal environment with
`DIA_LIVE_ACCESS_DISABLED=1`, no inherited Azure credentials or estate paths, and
the existing socket-denial replay driver. Artifact transport remains in the parent
before/after replay. This is an application-level network refusal, not a claim of
Container Apps network-namespace isolation. Only counts, hashes, sizes and exit
status are uploaded or printed; output prose and provider bodies stay private in
temporary scratch. A replay mismatch returns nonzero, and does not become a pass.

One tape with eight shards yields seven empty shards, not eight historical replays.
For an eight-worker comparison, provide eight uniquely identified entries (the
same preserved tape may be repeated explicitly as a throughput benchmark), and
report that repetition separately from coverage of distinct investigations.
