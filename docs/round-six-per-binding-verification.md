# Round Six D: per-binding verification

Dated 2026-10-05. #408 merged as `cae5463` with seven green checks.
The single-cell verifier was a specification error: thirteen unrelated columns
could not borrow a units cell address. Target-native type now selects a closed
profile; both probes carry the same explicit bounded sample. No family or
measure selects that profile. Original receipts remain unchanged.

## Preserved proposals, zero reads

The manifest declares only the separate application ? landing copy. None of
these fifteen original notebook proposals has a same-boundary declared equivalent.
The preceding source-copy 7,661/7,661 receipt cannot verify these boundaries.

?Needed by? means the quantity's full candidate walk would need this binding,
including a deeper hop not reached by the retained short walk. A/E/G/I use units;
F uses movement_value. Other target projections are useful discoveries but do not
independently feed those quantities. The units expression itself still carries
all deduplication keys and join inputs; this table never removes them. B's ratio,
C's complex expression and D's filtered lower refusal remain capability stops;
H's retained native-only route establishes no lower-quantity binding dependency.
I's business question may check the flow but does not establish business intent.
This conservative full-path gate is fixed before the reader rerun, not selected
after seeing which candidates verified.

| # | Boundary | Target column | Needed by | Declared equivalent |
| --- | --- | --- | --- | --- |
| 1 | original-landing ? original-refined | `movement_id` | ? | No; discovery |
| 2 | original-landing ? original-refined | `warehouse_id` | ? | No; discovery |
| 3 | original-landing ? original-refined | `product_id` | ? | No; discovery |
| 4 | original-landing ? original-refined | `units` | A, E, G, I | No; discovery |
| 5 | original-landing ? original-refined | `event_day` | ? | No; discovery |
| 6 | original-landing ? original-refined | `movement_type` | ? | No; discovery |
| 7 | original-refined ? original-serving | `movement_id` | ? | No; discovery |
| 8 | original-refined ? original-serving | `warehouse_id` | ? | No; discovery |
| 9 | original-refined ? original-serving | `product_id` | ? | No; discovery |
| 10 | original-refined ? original-serving | `units` | A, E, G, I | No; discovery |
| 11 | original-refined ? original-serving | `event_day` | ? | No; discovery |
| 12 | original-refined ? original-serving | `movement_type` | ? | No; discovery |
| 13 | original-refined ? original-serving | `rate_version` | ? | No; discovery |
| 14 | original-refined ? original-serving | `unit_cost` | ? | No; discovery |
| 15 | original-refined ? original-serving | `movement_value` | F | No; discovery |

## Offline implementation and limits

NUMERIC returns SUM and COUNT(*) including NULL rows; STRING requires COUNT,
COUNT DISTINCT and a stable order-independent content-hash sum; TEMPORAL returns
MIN/MAX/COUNT; BOOLEAN returns true count and COUNT. Synthetic SQLite execution
covers every type and deliberately wrong bindings, including equal SUM with a
wrong COUNT and equal string cardinality with changed content. A declared-form
proposal and a MODEL-form proposal round-trip through the same governed vector
compiler and original evidence. The old fixture copy tape is SUM-only and is
explicitly refused as incomplete; no historical count is manufactured.

Both queries compile before either runs. Missing target type or any faithful
construct produces UNVERIFIED naming it. Native target SQL catalog reads supply
actual types, including the code extractor's unknown derived field. The explicit
fixture sample is movement_id 1?360 inclusive, independently read from literal
seed metadata in notebook hash 313e90c9e25e1e1e844aac5383bfb3c01c4bd11684faeaabf48c207c623cf0c1,
line 8. It is applied to expression outputs on both sides, never guessed as a
pushdown through joins or deduplication. No expected sums/counts enter the verifier.

Previous refusal: ?Deduplication equivalence is not established across code and
execution languages; no assumed string collation or padding?. The new manifest
layer field is `comparison_normalization` (declared collation, trim, case_fold,
and evidence, or explicit UNDECLARED). Retained metadata does not establish
Spark deduplication semantics; no Spark or model default is filled in by assumption.
Those expressions refuse COLLATION_UNDECLARED naming the manifest field. Even an explicitly declared string
normalization needs a faithful adapter renderer; the current SQL adapter refuses
NORMALIZATION_RENDERING_UNSUPPORTED rather than approximate. The neutral verifier
and synthetic declared binary renderer support the full string profile.

Snapshot clarification: the human explicitly retained query-bound aligned served
versions. Standalone stable versions/refresh observations never remove
SNAPSHOT_UNVERIFIED. The earlier 8,765/8,765 proof has that limitation because
neither quantity query reported its served version; it does not establish that
the versions differed. Every provisional binding must be reverified for use.
Sample proofs cannot silently be reused as ticket-cell proofs.

## Budget decision, before live

DECIDED WITHOUT REVIEW, human-directed 2026-10-05: implement a separate
approval-time verification budget class in manifest budgets, default two probes
per binding plus metadata. It records each admission/refusal separately and grants
no physical credit. Human approval permits 33 total verification probes in this
single session. Investigation diagnostics remain 12 throughout; no global cap
change is made. The session override is removed after the pass. Endpoint and
native-type metadata count against verification, physical guards/identity requests
still count against the rolling and round allowances. Code/control requests are
separate from investigation diagnostics. Round pot 400, restoration reserve 60,
ordinary stop 340; rolling allowance 1,500 unchanged.

Upper profile cost is 30 data probes plus metadata; the approved cap is 33 and
binds even if additional metadata would be useful. Some faithfully unrenderable
bindings may refuse before reading. Physical requests are estimated separately
before live, never substituted for observed accounting. No replacement runs.

Sixteen new offline tests passed. Full regression and seven CI checks pending.
No D estate read yet; no fifteen-by-two or unfamiliar-domain acceptance earned.
Engine changes invalidate previous freezes. README/status report this checkpoint.
