# Partial self-report retention

2026-10-02 America/Chicago. PR A of the partial-report/composition/cap request.
#315 merged at 578c1af after six green checks. No estate reads or model calls.

## Delivered change

Original self-report columns are captured before quantity extraction, retaining
exact labels, text, explicit null, empty string and absent-column distinctions.
Only compiler-declared self-report aliases are copied; no quantity or other
business column enters this field. Capture is bounded to 64 rows and 300
characters per text scalar; oversized text refuses, never truncates. Numeric
scalars use the existing exact canonical-number encoding. Row truncation is
explicit and cannot create an attested report from a subset.

A partial report retains answered identity and null engine/object fields.
Engine attestation records PARTIAL coverage, ATTESTED/UNATTESTED field states,
and missing required fields. Missing required fields still make the probe
UNAVAILABLE for binding, reproduction and boundary grading. Identity-only
reports on a route declaring identity alone retain their prior qualified
eligibility; no required-field gate is weakened.

The receipt writer validates original raw capture independently of extraction.
An extractor omitting/changing it cannot complete the receipt. If extraction
fails after capture, the failed receipt still retains original self-report
columns. Synthesis validates the same raw evidence against the sealed receipt.
Historical receipts and attestation labels are not rewritten or upgraded;
old receipts lacking the new required raw evidence cannot satisfy this contract.

## Sweep correction and testing

The #299 absence sweep missed flexible_tools._split_surface_report, which
removed raw columns and replaced any partial mapping with None. A second
all-fields collapse existed in fabric_sql_surface.self_report; it also now
retains the actual identity/object mapping, including nulls. _transport_report
now admits explicit nulls rather than discarding a partial mapping. The search
covered scripts and PowerShell transport code. Other all(...) predicates found
were completion checks, definition coverage, whole-gold integrity, snapshot
eligibility or independent field comparisons; they do not discard a multi-field
self-report and remain unchanged. The PowerShell quantity transport already
retains its mapping. This is a retention change, not permission or attestation
promotion.

Ten new tests cover partial-null capture/refusal, hostile missing raw evidence,
wrong extraction, no business columns in raw capture, null/empty/absent
separation, bounds/truncation, boundary refusal, and SQL transport preservation.
Existing surface26, graded13, explicit-absence16, descriptor14 and flexible39
tests pass. A targeted test initially failed because its temporary SQLite
connection was not closed on Windows; the fixture now closes it explicitly.
The started full suite was stopped after this known fixture failure; its partial
log is preserved. Final full-suite and six exact-head CI results are recorded
on the PR. No investigation was run, so no ledger row.

All engine freezes are invalidated. Live partial-report retention is not yet
verified. PR B's bounded composition probe set is next; cap ordering, scoped
inventory consumer and R1 output repairs remain queued. Fixture mutation waits.
