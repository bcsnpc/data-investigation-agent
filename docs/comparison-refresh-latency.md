# Comparison-based refresh latency

2026-09-27. PR #273 merged after all six checks passed (`4f27678`).
Engine changes invalidate earlier freezes; this is known-domain development only.
No new live investigation or timestamp probe has been performed for this change.

## Implemented rule

The vertical procedure no longer terminates on a timestamp-derived freshness status.
After the first real independent comparison diverges, an adapter may supply a
positive `UNCHANGED_DECLARED_SOURCE` proof. Only a presentation-to-its-own-declared-
source proof, matching the measured quantity and exact boundary, permits
REFRESH_LATENCY. Other boundaries retain the existing transformation/refusal path.

The Microsoft proof currently accepts one entity partition in Direct Lake/import
mode, a complete pass-through Sql.Database expression, no model roles or calculation
groups, and a plain SUM of one physical integral column in that same semantic table.
The connection must match the approved SQL reader server. Filtered/grouped scopes,
computed columns, conversions, multiple partitions, extra M operations, ambiguous
references and missing definitions cannot establish this proof. Existing lower-read
and surface-attestation gates still run first. This deliberately narrow subset is
not a universal semantic-equivalence solver.

Original observations carry the declaration asset/hash, exact source and measured
column, scope, comparison reference, missing-timestamp reason and optional timing.
The validator checks these original observations; the digest explicitly preserves
the new evidence for rendering. Historical timestamp-contract records remain
readable, but current execution cannot produce a timing-selected outcome.

Both outputs give the two observed quantities and explain the serving-state
freshness discrepancy, missing refresh-time permission, and recommended recheck.
The reads do not establish a shared snapshot, duration, which state is newer,
correctness of source entries, or business intent. Existing unattested surface
fields and unchecked deeper boundaries remain mandatory limits.

## Optional timing

Absent by default. An operator may add a secret-free `fabric.refresh_timing_reader`
section with `account` and a separate `.local/` Azure CLI `profile`. This changes the
whole configuration approval hash and requires normal discovery re-approval.
The profile must already have authorized access; the code does not grant access,
start interactive consent, use the publisher session, or fall back to the reader.

The optional REST call validates token account, tenant and audience, is metered,
and retains a separate metadata-identity provenance and bounded latest history.
Returned status, refresh type and timestamps enrich the technical record; they do
not establish the cause of the discrepancy or decide any outcome. Unavailable,
refused, malformed or budget-denied timing leaves the comparison outcome unchanged.
The new transport is included in the engine fingerprint.

## Validation and pending live work

Focused tests cover direct divergence, transformed/unknown boundaries, attestation
refusal, mandatory timestamp limits, digest preservation, timing independence,
identity provenance, full-expression parsing and physical-column restrictions.
The real retained model definition satisfies the positive proof without cloud calls.
The initial full suite passed 1,268 tests (392 seconds). After the final exact-table
guard and identity-provenance tightening, all 61 targeted tests passed (13 new-rule,
41 procedure, seven synthesis tests). CI runs the complete final tree. No browser
flow changed and no live transport was used by these tests.

Intake and open-planner payload builders are unchanged; this change adds no directory
entries or per-entry labels and cannot reduce their coverage. New proof/timing
content is supplied only to post-execution synthesis, which has no asset directory.
The proof/digest field preservation test checks every newly consumed evidence field.

The latest real presentation/source pair is equal (8,765/8,765); its later
transformation divergence is not evidence for this new outcome. A controlled
stale-framing setup and one live investigation remain pending. The local plan is
`.local/comparison-refresh-20260927/live-test-plan.md`; no fixture has been mutated.
Daily investigation usage is70 against the restored ceiling60, so no live call was
started. No verbatim live outputs exist for this change.

Microsoft documents automatic framing as enabled by default and the portal's
"Keep your Direct Lake data up to date" switch as the control for a stale-framing
experiment. This setup must retain the old frame while changing only source data,
then restore it; a modified measure would violate the new rule's preconditions.
[Direct Lake framing and automatic updates](https://learn.microsoft.com/en-us/fabric/fundamentals/direct-lake-how-it-works).
