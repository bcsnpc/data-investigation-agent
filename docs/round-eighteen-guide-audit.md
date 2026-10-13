# Round Eighteen offline setup audit

Audit date: 2026-10-12 owner session. No estate reads, model calls, control-plane
calls, deployment, identity change or ledger mutation occurred in this audit.

The guide's default preflight command was executed on byte-identical temporary
copies of each current estate manifest. A temporary secret-free platform file
declared synthetic MI IDs and a PostgreSQL address, with an empty gateway and
`live_enabled=false`. No probe callbacks or `--check-shared-state` were enabled.

| Estate | Exit | Outcome | PASS | FAIL | MISSING | Estate/model/control requests |
|---|---:|---|---:|---:|---:|---|
| fixture | 2 | NOT_READY | 5 | 1 | 27 | 0 / 0 / 0 |
| billing | 2 | NOT_READY | 5 | 1 | 15 | 0 / 0 / 0 |

Manifest byte hashes:

- fixture: `6f062417950b3c6e8b0c580d54a60847211fe96d31f562b71baf6fa9e1325645`
- billing: `dbb641650d04087405f676f9750c3c85f3a1ec8e9ea43f705699308d76c999df`

The single FAIL is the intentionally disabled gateway. The five PASS checks are
configuration checks, not earned permissions. Required missing evidence covers
worker authentication, migrated PostgreSQL state, Blob, Key Vault, model endpoint,
network, each declared layer's read and definition access, three scanner tenant
settings and semantic Execute Queries. Three optional missing checks cover XMLA,
monitoring history and RLS impersonation. Missing does not mean the platform
refused permission; these checks were not run.

The audit corrected the example path (`estates/`, not `infra/estates/`), stated
that the retained examples still use workstation authentication, and documented
separate PostgreSQL/compute region parameters and staged deployment. It did not
claim that an offline schema check on billing makes billing cloud-ready.

The semantic preflight previously expected the platform worker's identity even
for an explicitly delegated Key Vault reader. The adapter now requires matching
account/tenant/principal declarations and attributes the probe to that reader.
Synthetic tests accept its receipt, refuse the vault-fetching MI as substitute,
keep an absent receipt MISSING, and refuse a mismatched declaration before any
probe callback. No live access is established by these tests.

## Storage inspection coverage

Read-only schema/count inspection of retained inventory files found only the
collector's `scans`, `assets` and `observations` tables:

| Snapshot | Bytes | Scans | Assets | Observations | SHA-256 |
|---|---:|---:|---:|---:|---|
| process-tapes/091cf70d-cfb6-4be5-b5bb-11f5c4529cac/inventory.sqlite | 36,864 | 1 | 19 | 12 | `eef1acf8c33f7d8201a23a65b21d50a9abfbbba6f3bbad16262e159d850532f0` |
| enterprise-discovery/inventory.sqlite | 2,097,152 | 2 | 966 | 78 | `a731b1b564795bc8a1526d24fbd1dda0d55c94d603c2ff1ea035c12391443242` |

The first is a small retained snapshot, not evidence that a live estate query ran.
The paired catalogs lacked diagnostic tables, so they were not used to claim
bounded diagnostic rows. The enterprise catalog was 4,407,296 bytes with five
tables (SHA-256 `e3c1bb93f6661ce039846d53cff80abf51d3edd7e04d9f94903eae3293917be5`).

A separate retained Round Seventeen capture,
`r17-c-application-20261012T185247/capture/catalog.sqlite`, has 40 tables and
349,523,968 bytes, SHA-256
`309b94f5c554e6928056820e688fe0b685f34e6fd3c7da2f13c02e73d7e0a6d7`.
Its 1,420 flexible diagnostic rows contain 1,419 parseable result documents
and one SQL NULL result. The largest result `rows` array has 249 entries.
All three native diagnostic documents parse; their largest array has one row.
Only schema, counts, shapes and hashes were printed; no row values were dumped.

This is a bounded evidence sample, not an audit of every tape, every JSON field,
or credentials inside definitions. The earlier `00041249...` sample in
`what-we-store.md` is retained as its dated prior audit; its loose database files
were not available for a second inspection. No new claim about their archival
state follows from that absence. Publication still needs its content/credential
audit and immutable bundle manifest.

## Dated control-receipt recheck (2026-10-13 UTC)

The earlier synthetic, disabled-gateway audit above remains unchanged. A later
run consumed real retained platform/authentication receipts, without requesting
new tokens, queries or control-plane operations:

| Configuration | PASS | FAIL | MISSING | Result |
|---|---:|---:|---:|---|
| fixture, retained-controls-01 | 8 | 0 | 24 | NOT_READY |
| billing, retained-controls-01 | 0 | 1 | 0 | Manifest validation refused |
| billing, retained-controls-02 | 8 | 0 | 13 | NOT_READY |
| billing, independent guide recheck-03 | 8 | 0 | 13 | NOT_READY |

The initial billing candidate changed the SQL adapter to a versioned vault cache
but retained the identity's old local credential reference. The corrected
candidate changed that reference to the same versioned vault reference. It did
not add a role or perform a query. This missing guide instruction is now explicit.
The billing example declares one semantic-model layer: its smaller prerequisite
count is not evidence that the complete billing source-to-report chain is ready.

The guide recheck executed the documented CLI with both receipt switches. It
retained these original hashes:

- Platform health: `f0dda1cf92a6406060139761225ecaeeab1f0c5047cd854a26043f6eb4ca03f1`.
- Authentication: `f94048619d30c1254691da0fcff4adb5d5e9b962c9e517b43b8b2073ccab9b2a`.
- Fixture result: `2bc15be354fe0d644880b1d9b09e9e7cc669565952640df967c35ef25fcb8f41`.
- Billing corrected result: `e3c51a5607bd172b580b7dc8ba4f430587996de4f679b20960ba2b33e57e10a8`.

The independent result is retained locally as
`round-eighteen/preflight-billing-guide-audit-03.json`. Authentication facts remain
separate from permissions. Shared-schema proof, vault/model/network access,
layer reads/definitions, tenant settings and semantic Execute Queries remain
MISSING in these particular prerequisite reports, plus the optional XMLA,
monitoring and impersonation checks. Platform health and migrated schema have
separate evidence elsewhere; no absent callback was represented as a denial.

Guide corrections now cover explicit credential-reference consistency, importing
hash-bound controls, partial preflight meaning, image-local context approval and
the gated cloud migration/demo command sequence. Deployment and teardown were
reviewed against the implementation; this helper did not create or remove an
installation while testing the guide. The full clean-client deployment,
onboarding and deletion path is therefore not claimed tested end to end.
