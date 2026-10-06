# Identifier-only run history

Updated 2026-10-06 America/Chicago. Round Seven post-gate item; offline only.

New adaptive records link to earlier records for the same model and byte-identical
ticket text, and separately to earlier records carrying the same validated native
cell address. Links contain identifiers only. They never carry previous findings
into a planner payload or treat them as evidence. Paraphrases are not inferred to
be the same ticket, and historical receipts without a native read address are not
backfilled. Existing records and outputs stay unchanged.

Creation records ticket links; terminal persistence refreshes cell links after the
observations exist. Synthesis appends one technical “Previous runs” line, leaving
business prose unchanged. Corrupt prior records make history explicitly unavailable
with the offending identifier; they cannot silently produce incomplete links.
The lookup currently scans earlier records of the same model in the local database.
An indexed history store remains future scale work, not a bounded omission of links.

Five regression tests cover independent ticket/cell identity, ordering and model
isolation, immutable prior records, invalid history, actual runtime persistence,
unchanged provider input, and byte-identical business composition. The eleven
planner projection goldens remain unchanged. Hosted seven-check and two-column
replay results are recorded on this PR before merge. No investigation, fixture
change or estate request occurred, so no investigation ledger row is added.

DECIDED WITHOUT REVIEW: “same ticket” means identical retained ticket text within
the same model; semantic similarity would require a new judgment mechanism. Only
consumer-validated native cell addresses earn cell links. This is ordinary new-run
history, not the earlier one-time retrospective receipt migration. Engine bytes
changed, so prior freezes are invalidated; historical tapes keep their producer pins.
