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
