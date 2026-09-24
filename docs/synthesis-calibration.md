# Synthesis calibration and Microsoft capability review

This is known-domain regression work following #222, not frozen acceptance.
Six additional trials are complete; nine corrected trials are graded separately from run evidence. No parallel synthesis or dependency-map implementation is adopted.

## Support preservation

The raw provider responses for corrected S1 and S3 already contain exactly 500
characters ending mid-word/reference. The saved assessment matches those bytes;
this was not persistence truncation. Remove provider maxLength on support strings,
retain a concise complete-text description and the existing local 500-character
limit, and reject excess length explicitly. Remove support truncation from proposal
repair. This prevents application-side silent loss; it cannot certify that a model
has expressed every relevant premise. Historical clipped responses remain unchanged.

## Offline calibration of the original three

Evaluator-only sources: the retained publisher input and evaluator-private artifact
for e1b8e1, plus publisher construction code. These are never planner inputs.
The fixture has versioned rates and a product-only downstream join. It does not
supply an authoritative adjustment exclusion/netting rule or independent application
intent record. Randomly generated adjustments are not evidence of erroneous entries.
Hidden construction truth is not credited as an observation.

All three are **CORRECTLY_UNCERTAIN about a source/application defect**, with
important explanation and evidence-transfer limits below. None establishes that
an adjustment is a correction requiring removal of its linked stock movement.
No support-contract condition demonstrably blocked an otherwise supported cause:
the returned uncertainty assessments were accepted, not downgraded by a validator.
UNKNOWN forbids intent-dependent defect labels, but naming an observed mechanism
without calling it erroneous remains possible. Do not loosen that gate from this sample.

| Run | Established from recorded observations | Missing evidence and trajectory |
| --- | --- | --- |
| S1 c7c72f67 | `199ada7d-ab6d-4271-b8df-8df93a3205fe`: 28 unit-mismatch cases, stock units 615 versus adjustment units 22, plus one two-adjustment case with stock units 21 and adjustment units -3. `5f4d5cfc-e542-466f-b102-93dc6bf51008` profiles joined grain. Unequal quantities are observed; a requirement that they equal is not. | Trace the actual measure/transform contribution of linked movements, and seek an authoritative adjustment rule or independent application intent. The decisions concentrated on mismatch drilldowns; the next payload exceeded both available cumulative input and the per-call cap. More rows alone would not settle intended behavior. |
| S2 01935d32 | `377e8380-ff42-4620-8b63-50bf14191b96`: one multi-reason case, two adjustment rows, two reasons and units -3. `29270acc-4d68-4bf4-bc0c-aa01deac56eb` returned no stock-grain anomalies in its tested scope. | Establish the downstream inclusion path and intended treatment. The run spent six reads profiling and drilling into adjustments and stopped at the read limit; it did not demonstrate a source-to-native contribution or an independent intent discrepancy. Raw joined rows existed in `29be0010-6292-4ce5-93b3-55b71c0ed3b1` but were deliberately omitted from synthesis. |
| S3 860dc8f6 | `3a41d2ac-7724-42c3-8870-23cd8ec62f8c`: 29 adjusted movement IDs, 30 linked adjustment rows, no duplicate stock keys or conflicting tested attributes, net adjustment units 19. `244e4f49-7d05-405f-8e92-a3597d787a7f`: adjustment-linked populations of 7 and 22 movements. | The run voluntarily stopped ENOUGH_DIAGNOSTICS after ruling out duplicate/conflicting source entries, already with BUSINESS_CONTEXT_REQUIRED. A targeted measure/transform contribution test remained, followed by an authoritative intent check. The recorded hypotheses favored retained adjusted movements; they did not establish that retention was wrong. |

No native read in these three reproduced the ticket measure. No executed rate-grain
or downstream join-multiplicity comparison demonstrated the hidden fixture mechanism.
The notebook excerpts located adjustment ingestion, not an authoritative correction
rule. The synthesis digest further omitted executable transformation excerpts, raw
rows and group keys; those omissions limit explanation and must not be mistaken
for evidence the investigator never retrieved. Some query text was truncated too.

The specific next structural question is **test selection and faithful evidence
transfer**, not a relaxed support contract. A dependency view may help choose a
measure-to-transform-to-source comparison, but its effectiveness is not established
here. There is no honest SQL-only test that can manufacture an absent business rule.

The previous phrase '3/3 supported' described qualified uncertainty, not three
correctly identified causes. S1 and S3 also retain clipped support and therefore
are not clean complete-support successes. The new six are reported separately
and combined transparently, without rewriting historical results.

Wire-cost check on recorded S1 synthesis: compact request 19,570 -> 19,837 characters. Input payload is unchanged, as are all investigation directory and SQL-object entries; only the response schema changes. No directory is present in the synthesis payload.

## Additional trials (completed)

S4 (`21070f54-28bc-4a18-a008-0b698bdd3e45`) is **MIXED**. Eight planning
calls, four SQL reads, six context lookups, zero rejections; NO_PROGRESS after
closely related empty exception reads. Synthesis completed INSUFFICIENT_EVIDENCE
with intact support. Receipts `2efc26e4-bfda-47c9-b9fb-bfbec86ac531`,
`a3e283a0-ce77-48ff-9566-563273257e1f` and
`3f713755-39a6-457a-8db2-e0cf212be110` have explicit predicates testing missing,
non-single or conflicting stock matches for adjustment-linked IDs, with no returned
exceptions. Those scoped negative findings are useful, but the digest omits the
predicates after its 400-character query prefix. Synthesis explicitly says it
cannot tell what was tested. Uncertainty about a defect is justified; loss of this
negative evidence is not a support-contract rejection. No hidden truth was needed
to identify this loss. A source-to-measure contribution and authoritative intended
treatment remain unestablished. The digest was not changed during this batch.

Coverage check: all nine recorded call-1 payloads retain **28 directory entries,
11 SQL objects and 15,067 payload characters**, with identical investigation envelopes. All four golden projected/wire
payloads and handles remain identical; only response-schema hashes changed.

### Evaluation limits

G's wording is a suspected-source-entry question, not an authoritative statement
that adjustments cancel their linked movements. The evaluator fixture does not
supply such a rule. This nine-run series can measure repeatability, evidence use
and refusal to invent intent; it cannot alone demonstrate calibrated identification
of likely causes across tickets with known authoritative contracts. Preserve that
limit even if all nine produce supported uncertainty. Original S1/S3 remain
clipped historical responses; pooling them does not retroactively fix support.

Run conditions remain medium reasoning, 8,000 output tokens, 48,000 per-call /
384,000 cumulative input characters, six data reads, twelve investigation planner
calls, 120-second call timeout and 65-second pacing. Only the support-preservation
response contract differs from the original three. Temporary daily reservations
are 315 planner calls, 160 cloud calls, 10,000,000 input characters and 2,824,500
output tokens, including retained prior usage. No counter reset or refund occurs.
Full offline tests ran concurrently with S4/S5; wall times are not a controlled
throughput comparison. Original daily policy was restored after all runs and probes completed; final counts follow.

S5 (`e9d4876b-cdab-4925-88ac-9473f331dcc9`) is **MIXED**. Nine planning
calls, six SQL reads, three lookups and zero rejections; read-limit stop. The
BUSINESS_CONTEXT_REQUIRED assessment preserves unknown intent and observes
unadjusted duplicate non-key signatures (`c8ab57e3-7f05-440a-b453-24320a2e2779`).
These are not duplicate movement IDs and do not establish erroneous events.
However, its mechanism says zero cases where net **or absolute** adjustments
"meet or exceed" movement units. Receipt `7c1ce53c-03a4-40c0-9338-3195ecbbad8a`
tests ABS(net) >= ABS(movement), but SUM(ABS(adjustments)) **>**, not >=.
The latter equality case is not ruled out by that receipt. Do not count the whole
assessment as fully supported. Support is intact; the error is interpretation,
not truncation or a validator-forced hedge. Six reads were spent on adjustment
profiles and duplicate non-key signatures without testing downstream contribution.

S6 (`cf858f67-a33c-4b0a-bbd5-37093db8db55`) is **CORRECTLY_UNCERTAIN**
about the ticket cause. Eleven calls, five SQL reads, five lookups and one complexity
rejection; budget stop. Receipt `69c5fa91-afe5-4bc5-be7a-a4a3b3164bbd` establishes
360 unique movement IDs, 29 adjustment-linked groups and 361 rows in the tested
naive adjustment join. Synthesis names this fanout as a risk, without claiming
that the actual measure uses the join. `4e9d109e-8429-42d6-b1af-5380b3b4f037`
returned no duplicate signatures in the tested linked population. The missing
steps are actual measure-path validation and authoritative intended treatment.
Its suggestion that one rule alone would settle the matter is incomplete: the
production inclusion path still needs establishing. No contract rejection blocked
a supported production-cause claim, and support text is intact.

S7 (`be7cce38-4a69-440f-98d1-63c440ce8175`) delivered **no assessment**.
Its rejected proposal is **CORRECTLY_UNCERTAIN**, but is excluded from the
supported-assessment numerator. Nine calls, three SQL reads, six lookups, two
query rejections and NO_PROGRESS. Receipt `7aeca75e-5f56-4834-8eed-919f0264da79`
shows 23 linked adjustment rows across 22 movements in one group. The proposal
correctly makes adjustment-join fanout conditional on the measure using that join.
It fails the citation-subset contract: support IDs must also occur in the outer
assessment evidence list. Offline validation of the recorded response reproduces
`Support must cite completed assessment evidence`. This is a structural citation
failure, not a cause claim suppressed by the unknown-intent guard. Text was not
clipped, no retry occurred and all usage remains charged. The proposed next test
was actual measure grain against a multi-adjustment case; it was not executed.

S8 (`f0be3674-5d48-4ff4-872c-38ed3e01a8fb`) also delivered **no assessment**.
The rejected proposal is **CORRECTLY_UNCERTAIN**, not a delivered success. Nine
calls, six SQL reads, three lookups, no query rejections; read-limit stop. Receipt
`d2f9fc34-7a92-40d4-bdd5-0d809969ecdc` establishes 30 distinct adjustments on 29
movement IDs, net units 19; `8cc588ee-de1b-415b-8831-9cc551aee811` shows displayed
linked groups with unequal units and a multi-reason case. The support list cites
`896da39f-39d5-4b59-ba56-87ecfcfc6257`, which is a completed receipt but absent
from the outer assessment evidence list. Offline validation reproduces the same
citation-subset failure as S7. Six reads went to mismatch drilldowns/summaries,
without the production measure-path test. No clipping or retry occurred.

S9 (`99ec6c13-3e95-4012-a0e8-157d6539ea32`) is **CORRECTLY_UNCERTAIN**
on its preserved investigation assessment. Ten calls, four SQL reads, five lookups,
no query rejection; voluntary ENOUGH_DIAGNOSTICS. Receipts
`8c52ff69-3d21-42b2-b763-5745d7468c9b` and
`73b82092-d27b-43b8-b506-1304aa679ad6` establish 22 RECEIPT and seven ISSUE
adjustment-linked movements, unequal linked units, and no tested stock-key or
attribute inconsistency in that linked population. They do not establish which
side is erroneous. The proposed next test was the actual Activity load/measure
path and intended adjustment rule. Synthesis failed the same citation-subset check:
`546fdc36-4413-4056-83d7-1d68bd1d686c` was cited in support but absent from the
outer evidence list. Its existing BUSINESS_CONTEXT_REQUIRED assessment survived.
Do not attribute that assessment to the failed synthesis. No clipping or retry occurred.

## Nine-run result and spread

| Trial | Investigation calls | SQL / native reads | Context lookups | Query rejections | Investigation stop | Synthesis | Calibration |
| --- | ---: | --- | ---: | ---: | --- | --- | --- |
| S1 | 10 | 5 / 0 | 6 | 1 | Input limit | Accepted BCR, clipped | Correctly uncertain |
| S2 | 10 | 6 / 0 | 6 | 0 | Read limit | Accepted UNRESOLVED | Correctly uncertain |
| S3 | 10 | 5 / 0 | 6 | 0 | Voluntary | Accepted BCR, clipped; prior assessment | Correctly uncertain |
| S4 | 8 | 4 / 0 | 6 | 0 | No progress | Accepted INSUFFICIENT_EVIDENCE | Mixed: negative findings lost |
| S5 | 9 | 6 / 0 | 3 | 0 | Read limit | Accepted BCR | Mixed: comparison overstated |
| S6 | 11 | 5 / 0 | 5 | 1 | Input limit | Accepted UNRESOLVED | Correctly uncertain |
| S7 | 9 | 3 / 0 | 6 | 2 | No progress | Citation failure; no assessment | Correctly uncertain rejected proposal |
| S8 | 9 | 6 / 0 | 3 | 0 | Read limit | Citation failure; no assessment | Correctly uncertain rejected proposal |
| S9 | 10 | 4 / 0 | 5 | 0 | Voluntary | Citation failure; prior BCR retained | Correctly uncertain prior assessment/proposal |

BCR means BUSINESS_CONTEXT_REQUIRED. The distinction between accepted, supported,
and complete is material:

- **6/9 (66.7%) accepted synthesis outputs**; the new six contributed 3/6.
- **5/9 (55.6%) receipt-grounded qualified synthesis outputs** under the earlier
  support criterion, excluding S5's unsupported threshold wording but including
  historical clipping. This is the comparable supported-assessment rate, not a cause rate.
- **3/9 (33.3%) intact, receipt-grounded synthesis outputs** after also excluding
  clipped S1/S3. S4 still omits useful negative findings and S6's next-test wording
  is incomplete; grounded statements do not imply a fully useful investigation.
- **7/9 final assessments** includes S9's preserved prior assessment. S3 also had
  an assessment before synthesis. Only five runs gained an assessment; one is S5.
- Seven uncertainty grades and two MIXED grades describe the reviewed evidence or
  proposals, including rejected proposals; they are not seven delivered synthesis successes.

Totals: **86 investigation calls, nine synthesis calls, 44 SQL reads, zero native
reads, 46 completed context lookups and four query rejections**. New-six totals
are 56/6 calls, 28 SQL reads, 28 lookups and three query rejections. There were no
provider transport failures; three synthesis validation failures remain failures.
Calls span 8-11, SQL reads 3-6, lookups 3-6 and query rejections 0-2. The new-six
wall times span 658.767-802.925 seconds, with concurrent offline tests/probes as
noted above. Repeated adjustment profiling, rather than actual measure-path
validation, dominates the trajectories. Neither more synthesis nor a relaxed
intent guard supplies the missing production-path and business-rule evidence.

All nine reference token costs total **USD 5.334540**, including **USD 0.432381**
for synthesis; the new six cost USD 3.311297, including USD 0.283442 for synthesis.
These are measured token counts at reference prices, excluding intake/cloud costs,
not Azure billing. The original three and new six differ only in the support
response contract; the new six used one unchanged engine. Pooling is not a claim
of nine runs on one frozen engine. No new control arm was run. Initial invalid
#222 attempts remain excluded from this corrected denominator and preserved.

## Controls, validation and next proposal

All 62 new investigation/synthesis tapes verified, including failed synthesis
responses. Six ledger rows were appended once; offline grades are in
[the calibration artifact](runs/synthesis-calibration.json), separate from the
[run ledger](runs/ledger.jsonl). Ledger NOT_GRADED is the automatic scorer field,
not a replacement for this independent review. Usage history grew **893 -> 1,007**,
with no reset/refund and zero active reservations at restoration. Retained September
24 reservations are 299 planner/intake calls, 159 cloud calls, 9,835,114 input
characters and 2,696,500 output tokens, including earlier work and 18 metadata probes.
Original daily limits (240 / 60 / 8,000,000 / 1,500,000) were restored, not usage.
Capacity/model and SQL free-limit/AutoPause controls read back unchanged.

**1,027 local regression tests passed**, including the no-silent-support-loss test
and golden views; implementation CI passed six checks. Golden projected/wire
payloads and handles were unchanged; only response-schema hashes changed.
No browser session was needed for this backend-only change.

Propose next, **not implemented**: preserve complete bounded validated query text
or lossless compiled predicates in the synthesis digest, and construct/check the
outer citation list deterministically from valid referenced receipts. Do not weaken
receipt validity or intent requirements. Offline copies of all nine digests with
full query text measure 12,144-22,718 characters versus 10,618-15,488 currently,
all below 48,000. S4 is 12,216 -> 19,496. No directory exists in either synthesis
form (0 -> 0 entries/SQL objects); investigation coverage remains 28/11. This is
measured on these receipts only, not an arbitrary-query size guarantee. Any later
implementation needs explicit overflow behavior and a coverage regression test.

Input-only expansion is closed as the remedy tested in #222, not proof that every
resource bound is irrelevant: S6 here stopped with 34,412 characters remaining
against a 47,909-character next payload. No limit increase or parallel synthesis
is proposed from this result. Test selection and faithful evidence transfer remain
the structural priorities. [Microsoft findings](microsoft-native-capability-review.md)
identify optional metadata sources, not a complete replacement dependency graph.
Stop here for review: no Microsoft adapter, dependency map, parallel synthesis,
new freeze, new domain or unfamiliar-domain acceptance claim.
