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

All 1,243 regressions passed before a final schema-component exclusion; 25 focused vocabulary/path/synthesis tests passed after that narrow correction. Two recorded repeats are pending. The user authorized only today's cloud-read ceiling to rise from 60 to 68 for these repeats; all other limits stay unchanged and usage is retained. The policy will be restored after the batch without resetting counters.
