# Named SQL connections (PR #436)

Estate configs now declare named database connections with independent server,
database, identity and Key Vault secret-name references. Connectors select a name;
layer mappings may select any of their connectors' names. The native bundle accepts
`sql_connections` and per-layer/resource `reach.connection`. Exact asset addresses,
principals and credential references are checked together. Ambiguous, unknown or
cross-database source requests are refused. Native query routes carry only the
selected connection; legacy single-connection manifests remain supported.

The practice fixture still has exactly one connection, `application`. Its inner
native manifest is unchanged. No identities, permissions, funding or deployments
changed. Metadata collection uses separate reader ports per connection.

`config/estates/healthnet.json` uses only the already-recorded metadata in
`docs/healthnet-status.md`: `hn_clinical` and `hn_billing` on the recorded source
server, plus the known analytics container/model/report IDs. It is disabled, with
no executable installation and unknown reachability. Reader scopes, exact table
bindings, secret names, provider/model selection and budget allocation remain
unestablished. Placeholder secret names are references, not fetched credentials.
Positive limits of 1 are inert schema minima, not an approved allocation. Logical
Silver and Gold point at the existing warehouse container without inventing table
lineage. `dia estate validate` reports `DRAFT_DISABLED`, zero network calls and no
secret resolution.

Qualification receipts accompany this report. They compare all 123 saved replay
classifications with the current R27 baseline, retain its negative cases, and hash
check all 248 original frozen confirmation members. This is an offline compatibility
check, not a new quality score or HealthNet investigation. The first image gate
exposed a test dependency on excluded deployment files; the corrected tests construct
their native bundle entirely in memory. No runtime behavior changed for that repair.

No HealthNet tickets or expected answers were created or opened. No new estate
reads, model calls, permission changes, merge or tag were performed. PR #436 remains
a draft; PR #435 and the original frozen confirmation remain untouched.

## Results

- Qualified source: `4d4fd7ed583975757069e1cf0fe21d3d5ed27926` (runtime implementation `8283f192`).
- Full suite: **6,228 passed, 53 skipped, zero failures/errors**.
- Image shards: **8/8 green**.
- Saved replay classifications: **123/123 unchanged** (86 completed, 28 recorded
  failures, nine no-investigation cases); no negative case was relabelled.
- Frozen original confirmation: **248/248 hashes unchanged**; practice native
  manifest unchanged; PR #435 unchanged.
- HealthNet offline validation: **DRAFT_DISABLED**, no network/secret resolution.
- [Qualification workflow](https://github.com/bcsnpc/data-investigation-agent/actions/runs/45879677194): success.

Receipts: [suite/image](round-twenty-eight-connections-qualification.json),
[replay](round-twenty-eight-connections-replay.json),
[immutability](round-twenty-eight-connections-immutability.json),
[HealthNet validation](round-twenty-eight-healthnet-validation.json).
The published code-only image was not deployed.
