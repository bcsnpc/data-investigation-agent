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

## Single reader pass, preserved result

Session `round-six-d-binding-reader-20261005T233448`, engine `b122207`.
Completed 2026-10-05T23:39 UTC; KNOWN_DOMAIN_REGRESSION, not acceptance.
The controller processed all fifteen preserved proposals once. No fixture,
manifest bytes, approval, configuration hash, identity or permission changed.
Seven VERIFIED, eight UNVERIFIED, zero FALSIFIED. Each VERIFIED result was
independently recomputed from both original profile observations offline afterward.
No extra read or provider call occurred during that validation.

| # | Boundary | Column | Native profile | Status | Target / source quantities | Needed by | Declared equivalent |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | original-landing ? original-refined | `movement_id` | NUMERIC | UNVERIFIED | No data probes; compile refusal | ? | No |
| 2 | original-landing ? original-refined | `warehouse_id` | NUMERIC | UNVERIFIED | No data probes; compile refusal | ? | No |
| 3 | original-landing ? original-refined | `product_id` | NUMERIC | UNVERIFIED | No data probes; compile refusal | ? | No |
| 4 | original-landing ? original-refined | `units` | NUMERIC | UNVERIFIED | No data probes; compile refusal | A,E,G,I | No |
| 5 | original-landing ? original-refined | `event_day` | STRING | UNVERIFIED | No data probes; compile refusal | ? | No |
| 6 | original-landing ? original-refined | `movement_type` | STRING | UNVERIFIED | No data probes; compile refusal | ? | No |
| 7 | original-refined ? original-serving | `movement_id` | NUMERIC | VERIFIED | sum=73672, count=406 / sum=73672, count=406 | ? | No |
| 8 | original-refined ? original-serving | `warehouse_id` | NUMERIC | VERIFIED | sum=789, count=406 / sum=789, count=406 | ? | No |
| 9 | original-refined ? original-serving | `product_id` | NUMERIC | VERIFIED | sum=2028, count=406 / sum=2028, count=406 | ? | No |
| 10 | original-refined ? original-serving | `units` | NUMERIC | VERIFIED | sum=8765, count=406 / sum=8765, count=406 | A,E,G,I | No |
| 11 | original-refined ? original-serving | `event_day` | STRING | UNVERIFIED | No data probes; compile refusal | ? | No |
| 12 | original-refined ? original-serving | `movement_type` | STRING | UNVERIFIED | No data probes; compile refusal | ? | No |
| 13 | original-refined ? original-serving | `rate_version` | NUMERIC | VERIFIED | sum=452, count=406 / sum=452, count=406 | ? | No |
| 14 | original-refined ? original-serving | `unit_cost` | NUMERIC | VERIFIED | sum=2597, count=406 / sum=2597, count=406 | ? | No |
| 15 | original-refined ? original-serving | `movement_value` | NUMERIC | VERIFIED | sum=57043, count=406 / sum=57043, count=406 | F | No |

Every successful pair was OBJECT_DISTINCT: Microsoft Azure SQL Data Warehouse,
same isolated SQL connection, distinct warehouse_gold_e1b8e1 and
warehouse_silver_e1b8e1 database objects. Both self-reported the configured
investigator-reader@skynwhy.com identity, engine product and database. Coverage
PARTIAL, consistency MATCHED; connection remains UNATTESTED. No semantic-model
value or served-version claim is borrowed from those SQL reads.

Each of seven pairs carries SNAPSHOT_UNVERIFIED and requires re-verification:
neither query supplied a bound served-version report. SUM/COUNT agreement is
bounded aggregate evidence, not rowwise equivalence, currency or business intent.
The sample includes join multiplicity: 406 output rows inside the declared key
range does not mean 406 distinct movement IDs.

### Findings for all fifteen discoveries

1. Refinement movement_id: UNVERIFIED. The whole-row string deduplication in the
source expression cannot be rendered faithfully under undeclared normalization.
2. Refinement warehouse_id: the same independent proposal has the same genuine
string-deduplication precondition; no narrowed key is substituted.
3. Refinement product_id: UNVERIFIED for the same complete-expression reason;
its numeric target type does not make string deduplication safe.
4. Refinement units: UNVERIFIED/COLLATION_UNDECLARED. This needed A/E/G/I binding
blocks resume; the earlier serving-units proof cannot establish this deeper hop.
5. Refinement event_day: STRING, not a date guessed from its name. Its distinct/
content profile lacks declared comparison_normalization and refuses before reads.
6. Refinement movement_type: STRING, the same missing declared semantics; cardinality
alone is not accepted as content verification.
7. Serving movement_id: SUM73,672 and COUNT406 agree across independent objects.
This verifies only the bounded profile of this code-derived projection.
8. Serving warehouse_id: its own native numeric SUM/COUNT agree (table above),
not borrowed from units or from the movement_id profile.
9. Serving product_id: its own native numeric profile agrees; this does not prove
key uniqueness or remove join multiplicity.
10. Serving units: SUM8,765/COUNT406 agree. This reproduces the first code-derived
binding proof (2026-10-05) with the additional cardinality witness, independently
of a Revenue/ticket cell.
11. Serving event_day: STRING profile refused on COLLATION_UNDECLARED, no date cast,
no count-only shortcut and no invented native hash semantics.
12. Serving movement_type: STRING profile refused for the same missing declaration.
13. Serving rate_version: SUM452/COUNT406 agree. Neither value establishes a
business rule for selecting rates.
14. Serving unit_cost: SUM2,597/COUNT406 agree; its actual target type came from
the reader-owned native catalog, not from a chosen measure.
15. Serving movement_value: SUM57,043/COUNT406 agree after compiling the proposed
expression. Native target metadata resolves the code extractor's derived-type
placeholder. This is a sampled mechanism witness, not a corrected business total.

Native target catalog returned text collation Latin1_General_100_BIN2_UTF8 on
both queried SQL endpoints. It did not report Spark deduplication collation or the
model's native collation. Therefore the fixture field cannot truthfully be filled
with the requested Spark/model defaults; those values remain undeclared. No name
or platform default is substituted. The manifest schema can record an explicit
UNDECLARED reason, or declared values with their metadata evidence; declaring the
SQL endpoint collation alone would not satisfy the cross-language requirement.

### Costs and stop

Before: round69/400, reserve60 (ordinary stop340); rolling150/1,500. After:
round111/400, rolling192/1,500. All42 charges SETTLED. They comprise2 local code
operations,3 reader HTTP endpoint lookups and37 SQL requests (16 quantity/catalog
statements,16 identity checks and5 permission guards). Thirty-four guard reuses
were recorded against their establishment receipts. No counter reset or refund.

Verification19/33 =14 profile probes +5 metadata probes (3 endpoint,2 native catalog).
Investigation diagnostics0/12; controls0; model/planner/synthesis calls0. No
synthesis or business/technical investigation output was manufactured for this
verification session. The one-off verification override was removed at session
end; before/after investigation cap is12. Separate budget class is implemented;
its physical admissions remain in the existing rolling/round governor.

Resume condition fails on refinement units, needed by A/E/G/I. No nine-family,
EMPTY/16 or source control run followed. Current runtime activation remains
closed; a vector sample is not silently treated as a ticket-cell proof. No15?2
or unfamiliar-domain acceptance claim. Previous freezes remain invalid.

Full local regression:1,987 tests passed in359.070s, including16 new binding tests.
Seven hosted checks pending on the documentation head; archived fifteen-tape
replay is a separate historical gate, never this engine's unfamiliar acceptance.

Tape SHA-256: `0e9d68b4638b37454761f4ed4950395a0e1c4ee5c86b796a066d323dbaa28cc5`.
933 events, FINAL present, zero exclusions. Original C tape, prior failures and
scalar-only declared-copy fixture remain unchanged. Missing historical COUNT
was refused, never backfilled.
