# Consumer-computed ticket provenance

2026-10-02. Parent: #305, merged `7018b2f`; original three HELD runs remain unchanged.

## Contract change

The model-facing schema changes: figure candidates and target-request sources now
contain only a verbatim quote. Additional properties are closed, so model-emitted
start/end fields are rejected, never discarded. The persisted figure/target span
shape is unchanged: the consumer locates the exact quote and stores start/end/quote
before existing precision, provenance and inventory validation. No offsets anywhere
in the model-facing schema. Metric/filter provenance already used plain quotes;
those now pass the same unique exact locator without changing their persisted shape.

The locator searches case-sensitively without trimming, normalization or fuzzy
matching. No match produces an explicit not-found refusal. Multiple occurrences,
including overlaps, produce a refusal naming the exact count. No first occurrence
is selected. A longer unique quote supplied on a later extraction locates correctly;
there is no automatic provider retry in this PR. Quote resolution is provenance,
not semantic interpretation: a longer quote still must satisfy the existing value,
precision or inventory interpretation. No semantic extraction or tolerance fallback
was added. Named quote refusals become NEEDS_INPUT and retain known provider usage.

## Other model-computation audit

The model-facing intake schema has action/triage, catalog handles, verbatim metric
and filter quotes, typed filter literals, dimensions, figure quotes and target quotes.
No other count/index/hash/checksum calculation is requested. Handle strings contain
indices, but code supplies them and the model selects an enum, not computes an
index. Typed values and scope/date intent remain interpretation of stated ticket
facts, not authorization to invent bounds or arithmetic.

The persisted envelope carries limits/counters, hashes, model revisions, context
identities, figure precision, target provenance and prepared plans. Those are
constructed or validated by preview/runtime/compiler, not exposed as model-generated
intake fields. Reported NUMBER/value/precision is derived by reported_figure from
ticket wording; the model does not compute it. Existing persisted spans are consumer
records, not surviving model-output offset fields. No additional demonstrated
model-computed field was found; no unrelated field is changed in this PR.

## Coverage and validation

Nine new tests cover correct spans, changed character/case, absent/repeated quotes,
overlapping matches, a longer unique quote on a subsequent extraction, hostile
model offsets, original downstream span shape, metric/filter uniqueness, closed
wire fields and retained catalog coverage. The sixteen inventory-resolution tests
and twelve immutable intake golden cases also pass. Synthetic expected wire schemas
are updated, but saved live tapes and fixtures are not edited.

All twelve intake context payloads are byte-identical: 1,050-1,952 characters,
Family D 1,103/1,103. Catalog model/column counts are unchanged. The single-model
schema shrinks 2,463 to 2,193 characters; the two-model schema 2,531 to 2,261.
Instruction constants grow by 315 characters. No inventory is added to the model
request, no context cap changes, and the investigation planner's 28-entry/11-SQL-object
coverage golden and byte-exact projections are unchanged. Full regression and
six exact-head CI checks are recorded on the PR before merge.

README/current status updated. Engine bytes invalidate previous freezes. No live
investigation or model/cloud call, ledger row, fixture/config/permission/budget
change in this implementation PR. The three #305 failures and their uncertain
reservations remain unchanged. Re-runs occur only after this PR merges and receive
new rows and evidence in a separate report. The date-predicate fixture change waits.
