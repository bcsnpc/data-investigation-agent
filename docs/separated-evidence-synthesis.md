# Separated evidence synthesis

2026-09-24. Related #199; follows accepted #221. KNOWN_DOMAIN_REGRESSION only.

## Proposal, measured before implementation

The pooled historical G outcome is **1 qualified conclusion in 15 runs** across
#220 and #221. Conditions differ, so this is a descriptive pooled rate, not an
identical-condition estimate. The single #220 success is not a reliability foothold.
At 15 reads, high/16,000 produced 2/6/4 SQL reads versus medium/8,000's 6/8/5.
This interaction is recorded; separate output and input accounts do not establish
that reasoning tokens directly displaced reads. Every higher-read run hit input
admission. Treat evidence accumulation and missing conclusion formation as the
structural finding; no further standing-setting increase is proposed here.

Freeze successful observations when investigation ends. Build one deterministic
entry per successful observation: original ID, requested query/lookup (bounded and
marked if truncated), stored result selection, completeness and receipt provenance.
Copy parser-identified SQL aggregate outputs through alias/CTE lineage; never
calculate new aggregates. DAX ROW scalar outputs may be copied. Keep at most four
returned aggregate values per output, with truncation and missing-group-key flags.
Omit raw record rows and grouping keys, not disguise them as prose. Unrecognized
result shapes retain row count/hash and explicit omissions. Bounded metadata
excerpts are source evidence, not tool instructions. Hypotheses remain explicitly
unverified and cannot establish omitted numeric facts. The question and declared
scope remain. No trajectory, planner payloads, rejected proposals or directory.

The prototype sizes below include that digest and hypotheses, before provider
schema/instructions. Final request bytes and input reservations will also be
reported. These are 23-37% of the 48,000-character cap, not a claim of lossless
compression. Omitted grouping detail limits conclusions and must stay explicit.

| Session | Characters | Successful observations | Reads retaining aggregate outputs |
| --- | ---: | ---: | ---: |
| A1 | 14317 | 12 | 4 |
| A2 | 15996 | 12 | 4 |
| A3 | 15165 | 9 | 5 |
| B1 | 15834 | 12 | 4 |
| B2 | 17939 | 11 | 7 |
| B3 | 13859 | 11 | 4 |
| C1 | 15223 | 12 | 6 |
| C2 | 12646 | 9 | 5 |
| C3 | 16068 | 12 | 4 |
| D1 | 10976 | 9 | 2 |
| D2 | 14945 | 11 | 6 |
| D3 | 15730 | 11 | 4 |

One clean synthesis call returns the existing #207 assessment/support object.
Existing citation and intent checks apply; sealed data receipts and stored session
integrity are checked before dispatch. Citation existence is not semantic proof.
Do not force a cause: BUSINESS_CONTEXT_REQUIRED, INSUFFICIENT_EVIDENCE and
UNRESOLVED remain valid. Preserve investigation outcome separately. Freeze the
payload/hash durably, reserve one full provider allowance independently of the
exhausted investigation budget, and never retry uncertain provider completion.
Cancellation, changed policy/context or invalid receipts prevent dispatch.

Three synthesis-enabled runs use arm A conditions (medium/8,000; six reads;
48,000 per call and 384,000 cumulative investigation characters). Three separate
input controls use arm B (15 reads), synthesis disabled, and explicitly experimental
input allowances. All six remain sequential. Do not change settings mid-run.
Every failure stays recorded, with one ledger row per investigation and separate
synthesis-call accounting. No freeze, new variant or unfamiliar-domain claim.

Parallel synthesis and graph traversal remain proposals/candidates, not implemented.

## Implementation verification

The sealed implementation measured 11,304-18,595 characters across all twelve
prior sessions, plus 2,467 characters of schema/instructions before provider framing.
The investigation payload method is unchanged. The recorded A1 initial payload
retains 28 directory entries, 11 SQL objects and 15067 characters before/after;
all twelve recorded initial payloads are unchanged. A fixed-clock regression
asserts byte-exact investigation payload and directory equality across synthesis.

The full local suite passed 1,024 tests. A subsequent usage-overrun guard and CLI
argument validation were followed by nine synthesis tests, all passing.
Live trials are pending. Input controls use 128,000 per call / 1,536,000 cumulative
characters with synthesis disabled; defaults remain unchanged.

## Initial batch interrupted: metadata projection defect

At commit 383e708, S1 and S2 produced BUSINESS_CONTEXT_REQUIRED after six SQL
reads each (eight/ten planner calls). S2 exposed embedded source rows inside a
notebook excerpt. This violated the raw-row exclusion contract; it is not a valid
clean-context result. S1's main uncertainty claim matched displayed aggregates,
but its mechanism field was cut off at the existing text bound. Neither result
is adopted as the corrected comparison.

S3 was cancelled during its first planner call after discovery of this defect.
Its recording is interrupted, completion uncertain, and the full reservation is
retained. Exactly three initial ledger rows preserve these attempts. No control
trial was started. The original daily policy was restored before correction.

The correction excludes all unstructured metadata excerpts, including notebook
content, find matches and free-text expressions. Asset identity/kind, lookup count
and provenance remain; omission is explicit. This trades metadata detail for a
fail-closed no-raw-rows boundary and may limit conclusions about transformations.
A regression inserts embedded rows through all three metadata paths and confirms
none reach synthesis. Ten focused synthesis tests passed. A new, separately
labelled batch will use the corrected engine throughout; old results stay intact.
