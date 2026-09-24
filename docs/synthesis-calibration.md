# Synthesis calibration and Microsoft capability review

This is known-domain regression work following #222, not frozen acceptance.
Six additional trials are pending. No parallel synthesis or dependency-map implementation is adopted.

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
are not clean complete-support successes. The new six will be reported separately
and combined transparently, without rewriting historical results.

Wire-cost check on recorded S1 synthesis: compact request 19,570 -> 19,837 characters. Input payload is unchanged, as are all investigation directory and SQL-object entries; only the response schema changes. No directory is present in the synthesis payload.

## Additional trials (in progress)

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
treatment remain unestablished. Do not fix the digest during this batch.

Coverage check: old S1 and new S4 call 1 both retain **28 directory entries,
11 SQL objects and 15,067 payload characters**. All four golden projected/wire
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
throughput comparison. Policy restoration and final counts remain pending.

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
