# Shared application authority

Round Nineteen implementation, 2026-10-13. Live state uses the existing scoped
PostgreSQL `state_documents` repository. No new database, role, secret or estate
permission is required. The worker does not create PostgreSQL tables.

`ModelStore.connect()` routes the explicit application-table inventory in
`shared_application.TABLES` through this repository. This includes claim intake
and revisions, confirmed investigations and failures, handoffs and glossary,
runtime runs/steps/events, adaptive sessions and synthesis, workspace jobs,
bounded diagnostic receipts and seals, screenshot metadata, and agent progress.
Existing catalog, smart-ticket and usage authorities remain their own typed
repositories. They are not re-imported by this migration.

Every touched table is read from shared state, hash checked, and reconstructed
in a transient **in-memory** SQLite view. This retains existing application SQL
semantics without translating SQL to PostgreSQL. It is not a per-job durable
authority. A short PostgreSQL transaction checks every observed revision and
commits changed rows and corresponding case-file sections atomically. A racing
revision refuses before overwriting it. Only then is the private SQLite replay
mirror updated. Mirror failure cannot roll back the already committed authority;
it fails the operation, and the next read fetches the shared revision.

The production case writer retains source rows and hashes, not a newly inferred
finding. Claims link to runtime sessions only through recorded session IDs.
Migration also builds historical case sections from their exact source rows.

## Migration and replay

Drain writers first. Run `scripts/migrate_shared_application.py` without `--apply`
to prepare a source hash and per-table counts. The catalog is opened read-only.
Add `--apply` only with the existing migration principal and gateway-approved
PostgreSQL route. `state_migrations` is an operator-owned audit table; the worker
does not receive new migration rights. Specify a fresh `--receipt` path.

The migration compares every row and column, including original JSON string
bytes, SQLite row IDs, NULLs and REAL values. It refuses nonempty target tables,
a changed source for an existing migration ID, malformed schemas and opaque BLOB
cells. **Historical screenshot BLOBs require a separate pixel migration; this
command refuses them rather than uploading pixels in a PostgreSQL document.**
The operator should report that refusal and retain the original source; this
implementation does not silently delete or alter a historical capture.

New workspace/verifier tapes declare `shared-application-rows-v1`. They capture
the exact shared snapshots consumed and commit hashes; replay uses those inputs
without a PostgreSQL connection. Old tapes retain their old contract. Controller
construction uses sealed bootstrap schemas; it does not invent operation reads.

## Screenshot storage and retention

For a live shared installation, `DIA_SCREENSHOT_STORAGE_CONFIG` names an
operator-owned JSON file containing `account_url`, the existing managed-identity
declaration, and a private platform `channel`. That gateway identity must have
`role: platform` and `platform_screenshots: [{account_url: ..., container:
screenshots}]`. No estate/model tool can choose this channel.

Pixels are immutable objects at `screenshots/images/<estate SHA-256>/<image
UUID>/<content SHA-256>`. PostgreSQL retains metadata and an indexed pending,
active, removed or expired disposition. A failed upload stays pending, so it can
be resumed or expired without an untracked object. Raw pixels are never written
to the replay catalog. Upload retries verify bytes before accepting an existing
object. Each physical SDK attempt still passes the gateway and control journal.

`intake.screenshot_retention_days` defaults to **30**, with the existing validated
estate override. The original upload time fixes expiry; reads do not extend it.
Every pixel access checks expiry before and after download. Expired pixels are
deleted through an exact bound DELETE on that object; deletion failure refuses
the access and leaves expiry visible for retry. New uploads also run a bounded
purge. `scripts/purge_screenshots.py` is the bounded operator/scheduled control for
idle estates, with a per-invocation limit and a retained control receipt.

**Operational limitation:** the purge command is implemented but no recurring
schedule or storage lifecycle policy is applied by this code change. Access
expiry is enforced immediately; unattended physical deletion is not claimed
until the operator schedules the control or applies an equivalent scoped Blob
lifecycle policy. Historical tapes containing image pixels are immutable and
have not been silently rewritten or deleted.

Projected screenshots still refuse: hashing text cannot redact image pixels.
Cloud pixel access inside an immutable process capture also refuses explicitly,
because copying the pixels into that tape would defeat retention. Metadata and
reviewed facts remain capturable. A retention-aware vision-request reference
contract is still required for that capture path.

## Recorded implementation decision

DECIDED WITHOUT REVIEW: use typed shared row documents and a transient in-memory
transaction view. Rejected alternative: a broad SQLite-to-PostgreSQL SQL shim,
which would change JSON/order/budget-journal semantics and require untested
grants. The parent reviewed and accepted this bounded approach during Round
Nineteen. Durable authority is shared; table-level snapshots can consume memory
and cause conservative conflicts between unrelated rows. Native per-aggregate
repositories and delta snapshots remain a performance follow-up, not an earned
claim. No raw projected-state fallback is provided.
