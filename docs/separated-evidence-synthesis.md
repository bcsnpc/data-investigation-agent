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
The trials below followed this implementation. Input controls use 128,000 per call / 1,536,000 cumulative
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
none reach synthesis. Ten focused synthesis tests passed. The separately labelled corrected batch below used one engine throughout; old results stay intact.

## Corrected six-run comparison

Commit `175b165`, engine `efa736496b2d`, same scope hash
`97be9ee7ed567d6d1dacbeb9243a759d25311c53268094a7b014757ddb8f5638`
as #221. All runs are KNOWN_DOMAIN_REGRESSION. S uses arm A's medium/8,000,
six reads, 48,000 per-call and 384,000 cumulative investigation characters;
I uses arm B's medium/8,000 and 15 reads, changing only experimental input
allowances to 128,000 / 1,536,000. I has no synthesis. Twelve investigation
planning calls, 120-second provider timeout, 1,800-second investigation deadline,
65-second pacing and serial cloud execution remain. Synthesis has its own single
120-second call; investigation deadlines are not extended. Default invocation
and default profiles remain unchanged; synthesis is opt-in (`--synthesis`).

| Trial | Investigation calls | SQL / native reads | Context lookups | Query rejections | Investigation input chars | Investigation stop | Synthesis / assessment |
| --- | ---: | --- | ---: | ---: | ---: | --- | --- |
| S1 | 10 | 5 / 0 | 6 | 1 | 335,307 | cumulative_input + per_call_input | BUSINESS_CONTEXT_REQUIRED |
| S2 | 10 | 6 / 0 | 6 | 0 | 329,699 | reads | UNRESOLVED |
| S3 | 10 | 5 / 0 | 6 | 0 | 332,458 | ENOUGH_DIAGNOSTICS | BUSINESS_CONTEXT_REQUIRED |
| I1 | 12 | 8 / 0 | 5 | 1 | 513,495 | planner_calls | Disabled; no assessment |
| I2 | 12 | 7 / 0 | 6 | 1 | 460,383 | planner_calls | Disabled; no assessment |
| I3 | 8 | 4 / 0 | 3 | 1 | 220,046 | NO_PROGRESS | Disabled; no assessment |

S1 stopped with 48,693 cumulative characters remaining; its next protected payload
was 48,940, exceeding both the 48,000 per-call cap and remaining cumulative room.
S2 hit six reads. S3 voluntarily concluded before synthesis; it must not be counted
as a conclusion created by the extra phase.

The controls were **not input-censored**: I1/I2 had 1,022,505 / 1,075,617 cumulative
characters left, and next payloads of 68,167 / 78,378 were below 128,000. They hit
twelve calls. I3 stopped NO_PROGRESS with 1,315,954 characters left and a projected
38,463-character payload. None ran out of deadline. More input alone produced
**0/3 final assessments** here, but the two call-limited trials do not prove that
conclusion failure is independent of every resource bound. No larger input default
is adopted.

### Direct arm comparisons

| Metric (three runs each) | #221 A | Corrected S | #221 B | Input control I |
| --- | ---: | ---: | ---: | ---: |
| Investigation planning calls | 31 | 30 | 33 | 32 |
| SQL reads | 15 | 16 | 19 | 19 |
| Native reads | 2 | 0 | 0 | 0 |
| Context lookups (all distinct) | 16 | 18 | 15 | 14 |
| Retrieval decisions | 12 | 12 | 12 | 10 |
| Test decisions | 19 | 17 | 21 | 22 |
| SQL proposals | 17 | 17 | 21 | 22 |
| SQL rejections | 2 | 1 | 2 | 3 |
| Schema-prefetch repairs | 4 | 6 | 3 | 4 |
| Result-equality overlap reads | 0 | 2 | 0 | 3 |
| Investigation input characters | 983,901 | 997,464 | 1,085,846 | 1,193,924 |
| Reserved investigation output tokens | 248,000 | 240,000 | 264,000 | 256,000 |
| Extra synthesis calls | 0 | 3 | 0 | 0 |
| Provider errors | 0 | 0 | 0 | 0 |
| Qualified uncertainty assessments after all phases | 0 | 3 | 0 | 0 |
| Already assessed before synthesis | 0 | 1 | 0 | 0 |
| Verified causes | 0 | 0 | 0 | 0 |
| Summed run wall seconds | 2,170.416 | 2,249.625 | 2,250.340 | 2,182.221 |
| Reference token cost, USD | 1.876329 | 2.023243 | 1.898990 | 2.053847 |

SQL rejection rates: A 2/17, S 1/17, B 2/21, I 3/22. S's one rejection was
column binding; I had two column-binding rejections and one complexity rejection.
No compiled-duplicate refusal occurred. Result-equality overlaps remain a metric,
not an admission signal. Ledger rows retain individual repairs, ratios and costs.
Wall time includes intake/pacing; the final offline test suite overlapped I1 and
early I2, so wall-time differences are not a clean throughput comparison.

### Receipt-support review, not business-truth certification

**3/3 corrected synthesis calls produced supported qualified uncertainty**, versus
0/3 assessments in arm A. This means concrete observed facts plus a specific
unestablished premise, not a verified cause or complete ticket resolution.
The review was performed against frozen digest values and saved receipts;
it is not an independent blinded evaluator. Machine ledger grades remain
NOT_GRADED; the separate [review record](runs/separated-synthesis-review.json)
records this narrower assessment without rewriting historical rows.

- S1 cites `199ada7d-ab6d-4271-b8df-8df93a3205fe`: displayed categories contain
  28 linked cases with stock/adjustment totals 615/22 and one case with 21/-3.
  It preserves unknown intended reconciliation and inclusion rules. These are
  query-defined categories, not proof that mismatches are business defects.
- S2 cites `377e8380-ff42-4620-8b63-50bf14191b96`: one returned case has two
  adjustment records, two reason codes and total -3. It explicitly cannot
  establish bad stock entries or the measure's intended handling. Its label
  remains UNRESOLVED; the explanation is more useful than an empty budget stop.
- S3 cites `3a41d2ac-7724-42c3-8870-23cd8ec62f8c`: 29 linked movement IDs,
  30 adjustment rows, and zero measured duplicate/conflicting-stock counts in
  that tested population. It weakens that specific source-duplication hypothesis,
  preserving unknown downstream inclusion rules. It already had a qualified
  investigation assessment; synthesis cannot receive credit for creating it.

S1 and S3's mechanism strings end mid-sentence at the existing 500-character
repair bound (S3 even cuts an inline citation). Their complete structured citation
arrays and main claims remain supported, but this is a presentation defect, not
production-ready explanation quality. S2's support is complete. Thus **only 1/3
has no observed support-text clipping**, despite 3/3 supported main uncertainty
claims. No claim of general reliability follows from three samples. The prior
pooled 1/15 remains historical; do not combine different protocols into a new
headline success rate.

### Digest size, cost and controls

Final corrected historical digests measure **10,868-18,601 characters** across
all twelve #221 sessions. Live S1/S2/S3 digests are **14,590 / 15,166 / 15,488**
characters (30.4-32.3% of 48,000), plus schema/instructions/provider framing.
No unstructured metadata excerpt, query-result record rows, trajectory, rejected
proposal or directory is sent in these corrected synthesis payloads. Aggregate
outputs are selections from receipts, not newly computed values. Omitting metadata
text and grouping keys can make some questions unanswerable; the digest is lossy.

All three S initial recorded investigation payloads retain **28 directory entries,
11 SQL objects and 15,067 characters**, matching A1's recorded view. I starts with
28/11 and 15,071 characters; the four-character difference is the experimental
input profile. Admission character accounting precedes transport-added generation
options and provider instructions; it is not a total wire-token cap.

The three synthesis calls took 17.168 / 17.555 / 46.254 seconds after reservation.
They used 17,833 input tokens and 6,957 output tokens (3,977 reasoning), costing
**USD 0.148939** at the same reference rates used in #221. They reserved 24,000
output tokens in full. No refunds or repeated synthesis calls occurred.
The six corrected trials used **938,118 input tokens, 115,453 output tokens
(74,540 reasoning), no cached tokens**, for **USD 4.077090** reference cost.
The initial two completed attempts add USD 1.063370; the cancelled attempt has
unknown provider usage. Intake and SQL/cloud charges are excluded, and these are
reference prices, not Azure billing.

All 65 corrected tapes (62 investigation, three synthesis) load with verified
body hashes. Exactly nine rows were appended to the 135-row ledger: three initial
attempts, six corrected trials. The original prefix is preserved. Usage history
is **751 -> 787 -> 893**, with zero active reservations or usage violations.
The cancelled attempt remains UNCERTAIN, with its interrupted tape preserved.

Before each batch, control-plane reads and policy snapshots were saved. The first
batch temporarily used 240 calls / 126 reads / 10,000,000 input / 2,100,000 output;
following interruption the original policy was restored. The corrected batch used
241 calls / 132 reads / 10,000,000 input / 2,271,500 output to retain prior charges
and admit the requested fresh comparison. No setting changed inside a run.
Final UTC-day reservations are 231 calls, 113 cloud dispatches, 7,735,208 input
characters and 2,191,500 output tokens. Original limits **240 / 60 / 8,000,000 /
1,500,000** were restored without resetting usage; additional live work can be
held by today's exhausted original limits. Concurrency remains one. Azure
GlobalStandard 100 deployment settings and SQL free limit/AutoPause are unchanged;
only SQL's rolling earliest-restore timestamp advanced.

Validation: **1,026 final local regression tests passed**, including ten synthesis
checks, plus six green CI checks on corrected implementation commit 175b165.
No dedicated local browser run was needed for this backend/evaluator change.

## Three independent synthesis passes: proposal only

Use three fresh, independent calls over one identical frozen digest hash and one
pinned schema/instruction/profile version. No pass sees another pass's answer;
none retrieves new data. Keep each response, failure, receipt references and full
reservation separately. Three calls require three allowances, including failed
or uncertain completions. Do not implement or run them in this milestone.

For comparison, require a small explicit mechanism descriptor alongside the same
support contract: referenced asset/relationship identifiers from the digest,
operation or condition asserted, affected scope, intent dependency, and sorted
observation-ID sets. Compare those fields and cited IDs, not prose similarity.
Report exact agreement, differing IDs with the same stated mechanism, incompatible
mechanisms, and unresolved naming differences separately. Unknown normalization
must remain incomparable; do not invent semantic equivalence or use majority vote.
Each pass still needs independent receipt/support validation. Agreement on an
unsupported claim is not validation.

If passes disagree, preserve all answers and state that the investigation does
not settle that mechanism. Present the competing mechanisms and differing receipts;
do not resolve by voting. If they agree, report agreement plus the existing evidence
limits, not a higher verification label. Honest shared uncertainty is permitted.

Measured single-pass costs suggest roughly USD 0.10-0.24 for three similar calls;
full 8,000-output reservations imply about USD 0.41 at these measured input sizes
and reference rates. This is sizing, not an invoice or guaranteed cost. Resolve
support-text clipping and test comparison behavior offline before proposing a live
trial. Do not silently increase text bounds: measure digest/directory/payload cost.

Actual parallel dispatch also needs shared token/rate admission and three distinct
reservation/recording keys. Keep SQLite transactions short and serialize ledger
writes through one collector; calls happen outside transactions. Three calls at
roughly 6,100 measured input tokens plus 8,000 output allowance total about 42,300
tokens, below the current 100,000 TPM nominal capacity, but pacing must account for
other traffic and provider estimation. This does not authorize changing concurrency.

Typed dependency traversal with per-node verdicts remains the **next structural
candidate only**. It is not implemented here. The stopping contract remains
unadopted. No freeze, fresh variant or unfamiliar-domain claim is made.
