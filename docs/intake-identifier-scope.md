# Identifier membership is not measure scope

Round Four A1, 2026-10-04. Intake grouping now has a consumer-validated verbatim
grouping request. An IDENTIFIER mention supplies expected-record membership only;
its quoted span cannot supply a grouping or filter restriction. Missing grouping
provenance, an unrequested breakdown or overlap with the identifier refuses.
Nothing is silently deleted to force the source walk to proceed.

A separate explicitly requested grouping remains possible when a ticket also
names an expected record. That grouping has independent provenance; the identifier
is never its justification. This preserves legitimate requested scope rather than
forbidding every breakdown on tickets that contain identifiers.

Tests: figure + identifier produces no filter/grouping and one expected record;
hostile identifier-derived grouping, missing provenance and identifier-derived
filter refuse; a distinct explicit breakdown is retained. Scalar grouping handles
without provenance are no longer wire-representable. Ten numeral-role and 36
intake tests passed. The older round's proposals and receipts remain unchanged.

Context-cost check against the retained current intake catalog: before/after six
models, 95 columns, 38 measures and **32,256 payload characters**, byte-identical
catalog/payload. Response schema grows 5,085 → 5,248 characters (+163). No planner
initial directory or SQL-object entries changed; catalog coverage regression stays
in the suite. No investigation/cloud run or ledger row in this implementation PR.
Engine bytes changed; prior freezes invalid. Two scenario runs wait until A1–A4
are merged, under the separate Round Four pot.
