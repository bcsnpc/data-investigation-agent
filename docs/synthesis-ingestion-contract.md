# Synthesis ingestion-context contract correction

2026-09-27 UTC. Tracking #193. Saved-R2 offline check; no live run.

## Which side was wrong

**Synthesis was wrong to assume every `tool=context` observation contains a
`metadata` object. The ingestion producer was not missing a required field.**

`MicrosoftProcessAdapter.ingestion` returns `asset_id` and `delta_commit` in its
process evidence. The latter is the bounded report from `read_onelake_commit`.
`process_debugging._observation` preserves adapter evidence and adds status,
completeness and roles; its contract does not wrap all evidence in `metadata`.
Other process-adapter context records also use role-specific root fields.
`metadata` belongs to the context-search/path response shape. Synthesis incorrectly
used the broad tool name as proof that every record had that narrower shape.

The synthesis consumer now explicitly dispatches ingestion-role evidence to a
Microsoft adapter projection. It validates the asset, report status and exact
required fields for AVAILABLE, EMPTY_RESPONSE and UNAVAILABLE. AVAILABLE needs
commit identity and a commit-information object. Empty/unavailable results retain
their status and failure information; they never acquire an invented commit.
The complete bounded commit report and original-observation hash are retained.
The producer and saved artifacts are unchanged. No synthetic `metadata` wrapper,
empty fallback, swallowed exception or silent omission was introduced.

Normal lookup/path observations still require an actual metadata object.
Malformed ingestion, mixed receipt shapes and unsupported context shapes fail
with explicit contract errors. Platform-specific commit fields are interpreted
inside the adapter projection, not the neutral process algorithm.

## Saved R2 offline result

Source session: `54509912-5e30-4850-afd7-ed26b5bc56aa`. The catalog was opened
read-only, the original source-file hash was checked before/after, and the
existing digest builder reverified sealed query receipts.

- Digest construction **passes**: five evidence entries, 6,298 characters.
- Ingestion projection: 947 characters, retaining the exact commit report and
  matching original-observation provenance hash.
- Zero network/provider calls. No original record or usage counter changed.
- **Synthesis does not complete.** Next failure during response validation:
  `CONSISTENT_TO_BOUNDARY requires at least one successful equal boundary comparison`.

There is no saved synthesis model response for R2: the original attempt failed
before calling its provider. This offline check projects the original deterministic
assessment to the synthesis response schema; it does not fabricate an LLM output
or claim a provider replay. The assessment passes the same underlying validator
against original observations, but fails through `evidence_synthesis.validate`.
That function rebuilds observations with only ID, tool, status, completeness,
roles and test purpose, dropping the digest's comparison status, equal-value flag
and execution surfaces. The validator can therefore no longer see the real equal
cross-surface comparison. This is the next blocker; it is recorded, not fixed in
this change. No live run was launched because the offline-completion condition
was not met.

## Validation and delivery

37 focused tests passed: 22 synthesis, two commit-reader, eleven planner golden
projection and two generator tests. New regressions preserve the entire ingestion
report without mutating its source; require missing fields to fail loudly; and
retain empty/unavailable reports without upgrading them. Full regression is in
progress; the final result will be recorded before handoff.

No investigation planner payload changes: its directory entries, SQL-object
entries and payload characters are identical before/after (the eleven golden
projection checks pass). The synthesis payload was previously unbuildable for
this receipt; it now contains the explicit 947-character ingestion entry within
the existing input cap. The neutral investigation procedure and provider settings
are unchanged.

PR #257 merged as `7ef4a062f87729e9433ab6bbaab7e311c9af129d` after six successful
checks. PR #258 had a documentation-only merge conflict with #257; both progress
entries were preserved, checks reran successfully, and #258 merged as
`b692b029098a222eb83230bb9f95e4fc2a67f5a3`. Neither engine fix was changed during
conflict resolution.

[Machine-readable offline result](runs/synthesis-ingestion-offline.json).
Local full digest and test logs: `.local/synthesis-ingestion-context-20260927/`.
This is a read-only validation diagnostic, not an additional investigation run;
no investigation ledger row or synthesis-provider tape was invented.
