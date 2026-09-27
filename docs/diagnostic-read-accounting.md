# Diagnostic caps and receipted guard reuse

2026-09-27. #280 merged after six green checks, preserving both previous HELD
runs. This change invalidates earlier engine freezes. No cap, estate, permission,
configuration or ordinary allowance is raised.

## What the numbers bound

The unchanged per-run `cloud_calls` compatibility field now counts admitted
**diagnostic operations**: an evaluated quantity or a requested metadata diagnostic.
A diagnostic can need multiple physical requests. For example, OneLake commit
inspection needs a listing and a commit GET, both charged physically but belonging
to one diagnostic. Failed/uncertain admitted operations still consume their slot.
The cap bounds how many investigations of the estate a run can initiate; the SQL
transport's own guard work does not consume another diagnostic slot.

`physical_requests` counts actual transport attempts/uncertain reservations,
including every guard, quantity command and metadata GET. All remain charged to
the rolling 24-hour ordinary allowance or the run's expiring batch credits. This
bounds remote request load, not scanned rows, compute or monetary spend. Exhaustion
refuses the next request before send, including when a diagnostic is partially
finished. There are no refunds. Existing cancellation, deadline, replay, identity
and scope checks remain in place.

The receipt-first ledger and score report include `diagnostic_reads`,
`diagnostic_read_cap`, `physical_requests`, `guard_requests` and `guard_reuses`.
Historical records are not relabelled; their diagnostic count is unknown unless
written with the new accounting version. Both earlier failed ledger rows remain.

## Guard lifetime and evidence

Successful database and object read-only permission checks are cached in memory
for one run invocation. The cache key binds the transport, server, database,
credential fingerprint, check kind and exact object for object checks. Changed
credentials/connections/objects require new evidence; a restart rechecks rather
than reusing an old cache. Credential fingerprints never enter receipts.

Each new SQL connection still obtains its own identity self-report. Permission
queries and allowed-permission sets are unchanged. A nonzero, failed, uncertain
or malformed guard result is never cached. A transport without a matching cache
entry must execute the guard before the quantity query. Outside a metered run the
transport executes every guard. Permission stability is assumed only during the
bounded run; this is not a persistent permission certification. Database permission
enforcement remains active on every actual SQL query.

`SQL_GUARD_ESTABLISHED` records a unique guard receipt and scope. `SQL_GUARD_REUSED`
references that receipt explicitly; reuse is neither a physical request nor an
unrecorded skip. The corresponding physical request receipt retains the guard
receipt ID. Admission still rechecks engine/config/context/policy invariants.

## Verification

Focused offline checks cover cap separation, per-request admission, receipt-first
failure accounting, same-run reuse, different objects/databases/credentials,
cross-run isolation and refusing unsuccessful guard evidence. PowerShell syntax
passes. The full local suite passed 1,303 tests; the final focused suite passed
18 tests, including the reporting assertion added while the full suite ran.
The full run emitted SQLite ResourceWarnings but no failures. The two requested
live repeats remain pending.
The prior batch credits were scoped to the old sessions; a separate bounded grant
for the new pair has been requested. No new live run has started.

## Follow-up: live pair after merge

#281 merged after six green checks. The approved pair completed both investigations
at four diagnostic operations and ten physical requests each, with zero guard
reuse. Both synthesis calls failed ValidationError. [Full results and rejected
drafts](diagnostic-budget-live-pair.md) supersede the pending-live status above.
