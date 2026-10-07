# Round Ten: filter forms checkpoint, 2026-10-07

Starting main is `7fb887e` (#421); #420/#421 hosted archived15/15 and inferred15/15 passed. The preserved Round Nine B Top-N failed with NativeRejected HTTP400 DatasetExecuteQueriesError: a table-valued candidate reached a Boolean-predicate wrapper. Relative-date and measure remained unattempted. Original tapes, failures and counters are unchanged.

## Budget decision

Human approval is Round Ten section0. A new local operator manifest declares ROUND_TEN with800physical requests,100reserved for restoration/final replay, and rolling3,000 (previous1,500). Investigation diagnostic12 and verification-class limits unchanged. Before/after manifest and whole-config hashes plus governor control reads are in `.local/round-ten-20261007/budget-change.json`; budget-change ledger note appended. New config hash `7e2ee8fb65208825762667d9c92c5f914cdaa1c295360084f3590d45582e2f20`. Opening rolling charge130 is retained, round charge0; no reset or new batch credits, credentials or scope.

The changed whole manifest/config is not an approval for old lineage or a narrowed discovery hash. Existing approvals remain pinned to their original manifests. Operator translator verification can explicitly examine retained metadata; an end-to-end investigation will still require current discovery/lineage approval before the fifty-ticket list.

## Closed forms

Fresh translation production requires form: FILTER has PREDICATE or TABLE_FILTER, MEASURE has null. The installed producer narrows kind and form together from the request, so null-filter and form-bearing measure combinations are unrepresentable on that wire. Local validation retains the historical schema only for already-recorded pre-form proposals; fresh propose rejects a missing form. Old receipt fields/hashes are not rewritten.

The adapter parses expression form against discovered metadata before dispatch. Boolean PREDICATE becomes a key rowset via FILTER; TABLE_FILTER enters CALCULATETABLE filter context, then projects discovered keys. Quantity compilation renders CALCULATE with the corresponding predicate or table argument. A table labelled PREDICATE, a scalar labelled TABLE_FILTER, unsupported form or statement-shaped expression refuses before any budget/read. SQL predicates append WHERE to the already-scoped base; table filters join a distinct projected key rowset on declared direct base keys, including null equality, without multiplying base rows. Neither names nor result equality create key correspondence.

New synthetic cases cover both compiled forms, the original KEEPFILTERS mismatch, rejected unclassified/scalar forms, scoped SQL execution and table multiplicity, historical versus fresh contracts, and directory preservation. Six focused form tests,32proposer tests,4native tests and11previous gap tests pass. Complete regression and hosted15x2 pending; no Round Ten live request yet.

## Context cost

The retained Top-N request has3directory objects before/after,0SQL objects before/after, and5,580payload characters before/after. Consumer schema878->960characters (+82); schema growth does not evict directory members. The golden test asserts byte-identical provider input and complete object inventory after form-schema narrowing. These counts concern this native request, not a large-estate coverage claim.

## DECIDED WITHOUT REVIEW

- Kept a historical schema path for pre-form sealed proposals instead of altering tapes; fresh production is always closed-form.
- Native table modifiers enter CALCULATETABLE so KEEPFILTERS is in its supported context, rather than embedding it in FILTER or silently stripping it.
- SQL table-filter joins use DISTINCT key projection and null-safe equality; a non-direct or ambiguous base key refuses rather than guessing a join.
- The operator manifest is a new immutable local file; Round Nine policy/artifacts remain unchanged. This does not silently reapprove lineage after a whole-manifest change.

Live section1b has its40physical-request ceiling, once-only Top-N/relative-date/measure order, and first-non-VERIFIED stop. Later fifty-ticket findings do not stop their list. No ticket expectations authored/sealed, list tag, new workspace, billing estate or Data Agent attempt yet. Prior engine freezes invalidated.
