# Business vocabulary and unfinished-judge audit

PR #270 merged after six green checks at `bbb64d6`. This follow-up changes output vocabulary only; it does not change judge instructions, schema, bounds, generation settings or retry behavior. The engine remains unfrozen and all trials are known-domain regressions.

## Judge investigation, before further changes

Both recorded judge requests carried strict JSON Schema with explanation/limitation `maxLength: 500`, a sentence-ending pattern and a description requiring complete sentences within the bound. The bound reached the provider; it was not lost in an intermediate projection. The transport decodes returned JSON without slicing those fields.

| Recorded judge | Explanation / limitation characters | Output tokens including reasoning | Provider state |
| --- | --- | --- | --- |
| 877adec9, run 529249ef | 500 / 251 | 504 of 8,000; 309 reasoning | completed; no error or incomplete detail |
| e88630e2, run f7a016d9 | 349 / 277 | 277 of 8,000; 136 reasoning | completed; no error or incomplete detail |

The first raw provider response already contains the unfinished final fragment, followed by a period and valid JSON closure. It repeats long technical identifiers and begins another conditional sentence at the character ceiling. This is not evidence of exhaustion of the overall token allowance, a network cut or local truncation. It is consistent with failed prose planning under a field constraint; the tape cannot distinguish the model's composition from the provider's constrained decoding. We do not have decoder internals or a counterfactual experiment proving that narrower causal claim.

The successful 349-character explanation demonstrates that this particular mechanism can fit the bound, not that all possible explanations can. The two samples used different instructions/patterns: the second already requests concise wording without repeated identifiers and has the stronger completion guard merged in #270. One failure in these two different revisions is not an estimate of a stable 50% failure rate. No additional judge fix, allowance increase or retry is implemented here. Raw tapes and original run states remain unchanged. The two requested repeats use the same current judge configuration.

## Vocabulary enforcement

The adapter retains simple readable labels actually used for the operands in a retrieved definition, separately from technical table/column identifiers. Each retained label has a definition identity/hash, operation index and exact source span. For the recorded definition those labels are `movements` and `rates`; we do not manufacture `product rates` by stripping a technical table suffix. Lexical provenance is not a claim that business meaning was independently confirmed.

The quantity's declared origin determines which operand is the subject, including quantities carried from the other side of a match. Physical table/column names, coded identifiers, layer names and placeholder aliases are ineligible. Multiple/unsupported operation paths or missing readable labels produce an explicit naming gap. This initial extractor supports readable single-word operand labels, not arbitrary noun extraction from natural-language descriptions. It never guesses a business name from a technical identifier.

The closed business composition uses only those source-backed domain terms, sealed quantities and fixed procedural/action language. Provider-invented nouns cannot enter the permitted text. The schema enumerates the exact composition and consumer validation rejects substitutions, technical identifiers and abstractions such as “other information” and “the information before the last check.” Labels and spans remain in separate vocabulary evidence; IDs never enter the business paragraph. The judge receives no vocabulary additions: they are attached to the retained definition receipt after its call, with an explicit regression test for that separation.

Saved-run context measurement: synthesis payload 13,797 -> 14,419 characters (+622), directory entries 0 -> 0 and SQL objects 0 -> 0. Investigation planner coverage is unchanged; the existing golden views remain part of regression validation. The extra synthesis content is bounded lexical provenance, not another directory. No context cap changed.

All 1,243 regressions passed before a final schema-component exclusion; 25 focused vocabulary/path/synthesis tests passed after that narrow correction. Two recorded repeats are reported below. The user authorized only today's cloud-read ceiling to rise from 60 to 68 for these repeats; all other limits stay unchanged and usage is retained. The policy was restored after the batch without resetting counters.

## Two recorded repeats

Both used engine `ec75232`, the same ticket, medium reasoning, 8,000 output tokens, seven-read ceiling and three-boundary ceiling. No engine or settings changed between runs.

| Run | Outcome | Synthesis | Reads (native / SQL / metadata) | Investigation judge calls |
| --- | --- | --- | --- | --- |
| R1 `4f263d32` | TRANSFORMATION_LOGIC | COMPLETED | 1 / 2 / 1 | 1 |
| R2 `74da03d4` | TRANSFORMATION_LOGIC | COMPLETED | 1 / 2 / 1 | 1 |

The [full artifact](runs/business-vocabulary-two.json) preserves the exact outputs, vocabulary spans, per-probe surfaces and attestations, comparison/skipped-boundary details, provider usage and receipt-integrity checks. This is a consistency sample on one known-domain ticket, not unfamiliar-domain acceptance or a population failure-rate estimate.

### R1 — `4f263d32-dd07-4429-a102-745a2ef68737`

**Business explanation, verbatim**

```text
The report showed 8,765, matching the total used to prepare it. An earlier check returned 7,661; the difference appears during preparation of the report. A matching step can count an entry more than once when it has several matches. The retrieved definition supplies no usable business names for the compared entries; their origin, update timing and intended treatment remain unconfirmed. Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.
```
**Technical explanation, verbatim**

```text
Handled Quantity returns 8765 in the model, and the same aggregate is present in dbo.movement_values. The lower checked source dbo.stock_movements_e1b8e1 sums units to 7661, so the increase appears between stock_movements_e1b8e1 and movement_values rather than in the report measure itself. The retrieved transformation definition shows a left join from stock movements to product rates on product_id before deriving movement_value, while units remains an additive carried column. Because key uniqueness is not assumed, multiple rate matches can replicate movement rows and increase the summed units without recalculating units. This is observed aggregate agreement across checked layers, not proof that the source rows, snapshot alignment, or business treatment are correct.

Surface attestation limits:
- Unattested connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity (receipt 3dfa3247-0878-4f9e-b9a9-cf1e2a78f676).
- Unattested engine on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity (receipt 3dfa3247-0878-4f9e-b9a9-cf1e2a78f676).
- Unattested object on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity (receipt 3dfa3247-0878-4f9e-b9a9-cf1e2a78f676).
- Unattested connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values (receipt 64ea25ac-0668-4d43-abd1-0f5498a94753).
- Unattested engine on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values (receipt 64ea25ac-0668-4d43-abd1-0f5498a94753).
- Unattested connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1 (receipt 4b34f724-2de6-49cf-a22e-2835954607d8).
- Unattested engine on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1 (receipt 4b34f724-2de6-49cf-a22e-2835954607d8).

Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.
```

**Judge, verbatim**

The definition includes a left join on product_id where matching rows may multiply because uniqueness is not assumed. That can duplicate stock movement rows in the upper table, causing the additive units total to increase from 7661 to 8765 even though units itself is not recalculated.

Limitation: This explains the difference only through join-driven row multiplication visible in the definition. The payload does not establish whether duplicate matches actually occurred for the observed data or whether both sides use the same snapshot.

### R2 — `74da03d4-ff3b-419c-8d40-80e0df2395f7`

**Business explanation, verbatim**

```text
The report showed 8,765, matching the total used to prepare it. An earlier check returned 7,661; the difference appears during preparation of the report. A matching step can count an entry more than once when it has several matches. The retrieved definition supplies no usable business names for the compared entries; their origin, update timing and intended treatment remain unconfirmed. Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.
```
**Technical explanation, verbatim**

```text
The measure returns 8,765, and the compared movement_values total is also 8,765, but stock_movements_e1b8e1 totals 7,661. The retrieved definition shows units carried forward through a left join on product_id before the upper table is produced, and it explicitly notes that matching rows may multiply because uniqueness is not assumed. That observed logic is sufficient to explain the increase between stock_movements_e1b8e1 and movement_values, but it does not identify the duplicated rows, prove source correctness, or establish that this implemented handling matches business intent.

Surface attestation limits:
- Unattested connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity (receipt 5db6677d-270f-4017-98bf-46596be19e6e).
- Unattested engine on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity (receipt 5db6677d-270f-4017-98bf-46596be19e6e).
- Unattested object on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity (receipt 5db6677d-270f-4017-98bf-46596be19e6e).
- Unattested connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values (receipt 144bce36-5c96-4cc3-a59b-6afce7f79944).
- Unattested engine on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values (receipt 144bce36-5c96-4cc3-a59b-6afce7f79944).
- Unattested connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1 (receipt 8dbce7b8-8066-49ea-86cb-9eed2519fc58).
- Unattested engine on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1 (receipt 8dbce7b8-8066-49ea-86cb-9eed2519fc58).

Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.
```

**Judge, verbatim**

The definition includes a left join on product_id and explicitly states that matching rows may multiply because uniqueness is not assumed. If product_rates has multiple matches for some product_id values, stock movement rows and their units are duplicated in the upper table, which can raise the total from 7661 to 8765.

Limitation: This explains the difference only through join-driven row multiplication visible in the definition; it does not identify which rows matched multiple times or establish snapshot alignment beyond the declared transformation scope.

## Vocabulary failure and scoped correction

Both runs above completed the investigation and synthesis but **failed this milestone's business-vocabulary requirement**. The original exclusion consulted all asset names in the estate. An unrelated semantic model has a table called `Movements`; that homonym suppressed the current definition's operand label and caused the fallback claiming no usable names. That naming-gap statement is incorrect and is withdrawn for both runs. Their exact stored outputs remain unchanged, with append-only quality corrections in the ledger.

The first offline preview tested the parser's spans but bypassed the full catalog exclusion. That verification gap is also recorded, not presented as successful end-to-end vocabulary validation. The corrected filter considers only physical identifiers in the compared definition's quantity scope. Regression tests assert that unrelated table/schema homonyms cannot remove labels, while actual in-scope table, column and schema identifiers remain excluded.

Twenty-six focused tests passed after this correction. A second offline check used the full real catalog and the same `extend()` path used by the adapter: it retains `movements` and `rates`. Its synthesis payload is 13,661 -> 14,283 characters (+622), with directory/SQL-object counts unchanged at 0/0. This is a local check, not a further investigation or a live pass. The corrected engine passed all 1,245 regression tests in 400.359 seconds and six CI checks on f08c2d0. Two additional live repeats require the separately requested read-budget approval. The original policy is restored at 60, with 62 reads retained and no reset.

The two new judge requests match after removing only the generated definition receipt ID: instructions, strict schema, model/reasoning/output settings and input evidence are identical. Both returned completed prose (285/241 and 320/228 explanation/limitation characters). No provider truncation or guard rejection occurred in this pair. This is two observations, not a reliability-rate estimate.
