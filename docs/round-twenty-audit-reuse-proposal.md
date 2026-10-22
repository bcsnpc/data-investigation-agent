# Per-run reuse of successful SQLite credential audits (proposal)

Implementation now uses an explicit per-run in-memory scope; the requirements below remain its trust boundary. The first capture's repeated full-catalog audits can dominate the worker lifetime even after batching: retaining the prepared catalog, snapshotting it, retaining both the capture baseline and working copy, then retaining baseline/working/after copies after execution. Byte-identical copies do not gain security from repeating the same successful detector against the same secret environment.

## Required trust boundary

Reuse is safe only inside an explicit, newly constructed run scope, held in memory. Its identity is the full file SHA-256 plus detector/normalization profile and the current secret-environment fingerprint. A different run starts empty. Nothing in a tape, file, CAS reference or old receipt may populate it. A different file location is eligible only after hashing every byte and satisfying the same sealed-file conditions; a matching basename, inode, size or mtime is insufficient. No audit result contains a secret or environment values. A changed environment invalidates prior results because `_safe` tests the actual environment's credential values in addition to fixed patterns. Hashing the whole sorted environment is conservative and avoids maintaining a second credential-variable classifier.

Check for SQLite `-wal`, `-shm` and `-journal` sidecars before and after hashing/audit; any such file disables reuse and refuses direct retention of the database as a sealed artifact. Snapshot may still use SQLite backup to make a consistent, fully audited in-memory copy. Reject links/reparse points as current retention already does. Hash before and after a full direct audit; only identical hashes after successful completion may populate trust. If auditing raises, register nothing. Source files remain untouched.

`Files.capture` already requires a consistent sealed file rather than a live database. This optimization does not relax that prerequisite or solve concurrent mutation. Files being used as live working databases must be closed/quiescent before retention or replaced by the existing consistent snapshot path. Validate the returned CAS reference against the audited SHA, and treat mismatch as a defect; it cannot retroactively make publishing a mutating file safe.

## Two current audit profiles are not interchangeable

`cloud_stage_worker.audit_database` audits string cells after attempting JSON parsing and normalizing them; binary cells go raw to `_safe`. `cloud_verification_capture.snapshot` also audits schema metadata and normalizes strings, but UTF-8 binary cells are wrapped as JSON strings before `_safe`. The latter can hide an additional nested JSON-escape layer compared with the raw-binary path. Therefore a successful snapshot audit must not simply be called equivalent to a stage audit.

The smallest safe first implementation keeps distinct profile keys and deduplicates only repeated stage-retention audits of byte-identical copies. Snapshot's full in-memory audit remains mandatory before any destination SQLite write. The stronger follow-up is to run both raw and existing normalized binary checks during that in-memory audit, retain its schema checks, then register the output SHA for both profiles after writing/closing the destination. This adds checks rather than removing an existing one and lets retention reuse snapshot attestations. Snapshotting a source may bypass its full memory audit only if the exact retained backup result, not merely the source main-file hash, is already certified for the full snapshot profile.

## Regression tests required before enabling reuse

- One run: two byte-identical sealed databases at different paths perform one full audit; both references have the same full SHA. The second phase still hashes all bytes.
- A second run repeats the full audit; no persisted trust file exists.
- Same path and size but one changed cell causes a new audit; a newly introduced raw, JSON-escaped, nested-escaped or binary credential refuses before any CAS publication.
- A new environment credential causes a fresh audit and refusal even when file bytes match an earlier success.
- Raw binary and UTF-8/escaped JSON binary exercise both profiles. Snapshot-only trust must not bypass raw retention checks until both checks ran.
- Schema metadata containing a credential still refuses snapshot; stage-only trust cannot skip schema checks.
- WAL, SHM or journal appearance before or during hashing/audit prevents registration/reuse and publication.
- A detector exception does not register success; a later attempt runs it again.
- A snapshot with unsafe input creates no destination. Source hash remains unchanged on success and failure.
- Instrument the production audit and retention paths with a synthetic SQLite fixture, not only a cache unit double. Prove unchanged CAS bytes/manifest identity and fewer full detector passes.

Expected benefit is fewer repeated detector passes, not fewer physical/model requests or a larger time allowance. Every newly changed catalog (including the post-execution accounting mutation) still needs one complete audit. Keep the 1,800-second hard job limit and all native-read request limits unchanged.


## Implemented boundary and validation

`investigator.run_database_audits.scope` is entered by `unified_runner.run` and reset on every exit; transient retry failures invalidate all previous successes. The stage audit's key is `(full SHA-256, explicit stage profile, detector callable, hashed current credential environment)`. The environment classifier is shared directly with `_safe`, rather than independently inferred. Every lookup rehashes all bytes; links and SQLite sidecars refuse, and successful full audits require identical before/after file and environment identities. No receipt, tape or persisted file can populate this set.

Snapshot still always audits a frozen readonly SQLite transaction before writing a destination. The same source connection supplies the final backup; the database is no longer duplicated in RAM. Its schema and string checks plus raw/normalized BLOB checks form a superset of the stage profile; after successful destination backup and exact destination hashing it can register that written file for stage reuse. No trust is registered from the unexamined source main file. A changed catalog still receives a full snapshot audit. This reuses successful detector work only, not SQLite state, accounting, CAS bytes or evidence claims.

The production retention regression writes real synthetic SQLite databases and real local CAS objects. Before/after retention of identical baseline and working files runs the full stage detector once instead of four times; both manifests and restored bytes remain exact. Other tests cover same-size mutation, new credential environment, changed environment during audit, new run/profile/detector, sidecars before/during audit, failed audit, schema-only credentials, raw/escaped/binary secrets before destination write, unchanged source hashes, retry invalidation and run-scope exit.
