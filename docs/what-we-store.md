# What the investigator stores

This describes the implemented foundation, not the future graph/agent design.
An installation keeps client evidence in its configured tenant/storage. Operators
must treat definitions, ticket text, screenshots and bounded query results as
client data even when they contain no credentials.

| Material | Contents | Location and current boundary |
|---|---|---|
| Discovery inventory | Scan times/status; asset IDs, parent IDs, kind, name, source, collection time, definition hash and JSON metadata; capability observations | Retained `inventory.sqlite` images; content-addressed snapshot storage when converted |
| Published catalog | Model registration/enablement, immutable report/model context definitions, scope/source hashes, event history and readiness certificates | Shared PostgreSQL documents; private historical SQLite images remain for replay |
| Tickets/shared case state | Submitted text, selected context, question/reply history, claims and evidence references, revisions and hashes | Shared PostgreSQL for configured cloud workers; offline SQLite for historical tests/replay |
| Investigation evidence | Exact guarded SQL/DAX requests, bounded responses or aggregate values, surfaced identity/permission attestation, limitations and receipts | Per-job evidence/capture state and recordings; private Blob containers when published |
| Model recordings | Provider request/response bytes, structured decisions, usage and failures, tool events and timing | Sealed tapes plus referenced immutable starting snapshots and changes |
| Budgets | Original reservation counts, actual usage, status, overrun acknowledgments, expiring credits, pot/reserve policy, conservative dollar accounting | Shared PostgreSQL authority; local originals and per-job replay mirrors retained |
| Screenshots | User-uploaded report images and associated intake provenance | `workspace_images.content` stores image bytes in the case catalog; read/review records are separate tables. The declared retention period has no implemented screenshot purge job. |
| Secrets | Only approved connector credentials when unavoidable | Key Vault; managed-identity access tokens stay in memory, never in tapes or database snapshots |

`metadata_inventory.Inventory` creates exactly three collector tables: `scans`,
`assets`, and `observations`. `assets.metadata` holds definitions and schema
metadata, including PBIR page/visual parts, model tables/measures/relationships,
SQL columns/keys and transformation source text. It is not a collector of client
business-table rows. Older shared inventory files can contain additional
lineage, investigation and snapshot-registry tables. The retained legacy
source registry references a separate full ten-table SQL export: 1,410,699 rows
in 151,996,446 bytes, plus a separate byte-identical data copy not registered
in that inventory. That intentional ingestion-development artifact is not
normal client capture and must never be swept into a recording bundle merely
because it is under `.local`; see the [dated audit](round-eighteen-recording-content-audit.md).
Definitions can themselves contain literal values, query
text, resource identifiers and credential-free connection routes; they remain
sensitive evidence.

Investigations retain only the bounded results used to support a finding, not an
unbounded backup of client tables. A bounded record-list probe can contain actual
client row values. A small table fitting within a row cap is not automatically
anonymous or safe to publish. Synthetic fixture seeds and the stopped local-data
export experiment are separate test/development artifacts; they are not part of
normal client capture and must not be swept into a client recording bundle.

This source/schema inspection does **not** establish that every historical tape
contains no accidentally copied bulk data. A complete archive claim requires the
dated archive/snapshot content audit and its manifest. If an audit finds an
unbounded export in a recording, stop publication, retain the finding and remove
that material through an explicitly recorded correction; do not quietly rewrite
a sealed tape and describe it as the original.

## Dated retained-snapshot sample (2026-10-12)

A read-only inspection of process tape
`00041249-84f3-4ddf-aae0-b1e3f62eb94e` inspected its pinned `inventory.sqlite`
(58,171,392 bytes) and `catalog.sqlite` (183,496,704 bytes). The inventory has
45 scans, 32,210 metadata assets and 3,698 observations in its three collector
tables. Asset kinds include definitions, columns, tables, report visuals and
transformation items; no separate copied business-data table was present.

The catalog has 37 operational tables, including 962 flexible diagnostics,
3 native diagnostics, 304 adaptive sessions, 232 model contexts, 773 smart
tickets and 6,213 usage rows. Parsing all diagnostic result documents found a
maximum of 249 rows per flexible result and one row per native result; the
largest session observation value array also has 249 entries. These are actual
bounded evidence values, not only schema metadata. This was a structural/count
audit: it did not print raw business values or establish that no definition
contains a credential. It covers these two snapshots only, not every tape or
all JSON fields in the archive. Publication still requires its separate
credential/content audit and hash-pinned manifest.

A later offline recheck inspected two other inventory snapshots and the retained
Round Seventeen application capture. The latter contains 1,419 non-null flexible
result documents (maximum 249 rows), one NULL result, and three native result
documents (maximum one row). Exact hashes and the deliberately limited coverage
are in [the setup audit](round-eighteen-guide-audit.md). These observations do not
make a publication credential audit unnecessary. A broader later
[structural audit](round-eighteen-recording-content-audit.md) records the exact
loose-tape and database-schema coverage, including unreadable/opaque cases.

## Exact and privacy-projected recordings

An estate explicitly selects EXACT or PRIVACY_PROJECTED. Exact tapes retain exact
request/response evidence. Projected tapes apply an estate-keyed projection at
capture; raw values do not first pass through a disk file. Their label says
comparison is exact **after projection**. The projection key stays in the secret
store, not the recording. Existing exact gate tapes remain exact.

Projected tapes cannot be re-projected under a different column list or key to
create equivalent evidence; they require re-recording. The current shared-state
PostgreSQL adapter refuses projected live persistence until that entire boundary
is implemented. Slim cloud recording also rejects projected captures
(`SLIM_PROJECTED_CAPTURE_NOT_IMPLEMENTED`). Screenshot upload refuses projected
estates because column projection cannot redact image pixels. No silent switch
to exact recording is allowed.

## Retention and deletion

The manifest owns tape and ledger retention. Existing defaults are **indefinite**;
there is no promise of automatic expiry unless a finite policy and its scheduled
execution are configured and verified. Screenshot retention is separately
declared in intake configuration, but `screenshot_retention_days` currently has
no deletion consumer. It is a policy declaration, not enforced expiry. Shared
PostgreSQL and Blob lifecycle policies
must be operated consistently with those declarations; storing a number in the
manifest does not by itself schedule a cloud deletion job.

The local retention planner conservatively keeps unfinished tapes, unknown
sidecars and undated ledger rows. Deletion requires a reviewed plan, root/path
checks, fresh hashes and a durable audit. It does not operate on published release
bundles. Shared snapshots must remain while any retained tape references them.
Archived copies are removed locally only after hash-verified upload, per the
owner-approved archive manifest; an upload success alone is insufficient.

To remove a client's material, stop admissions, settle usage, decide what must be
retained, then delete the client's ticket/evidence namespaces, unreferenced Blob
objects and any separately exported copies using an audited operator procedure.
Account for database backups, Blob versions/soft-delete, archive retention,
release artifacts and Key Vault soft-delete. The current CLI does not implement
a comprehensive client-wide cloud purge; do not claim deletion is complete from
removing one local directory.
