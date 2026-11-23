# OpenRouter SuperVL original proof ? synthetic DEV only

All15 original runs use the same pinned model/provider and source77267c82/image08474. Single independent Sol grading; free results satisfy no quality gate. The repair cohort is separate.

| Ticket | Correct | Useful nonharmful handoff | Harmful | First-wrong-step / trace classification |
|---|---:|---:|---:|---|
| billing-invoices-v2 | 1 | 0 | 0 | NONE; none |
| application-baseline-v1 | 0 | 1 | 0 | MODEL_DELIVERY_FORMAT; wrong conclusion |
| billing-mrr-v1 | 0 | 1 | 0 | MODEL_INCOMPLETE_LAYER_COVERAGE; wrong conclusion |
| fixture-quantity-v1 | 1 | 0 | 0 | NONE; none |
| record-repeated-gold-v2 | 1 | 0 | 0 | NONE; none |
| record-absent-everywhere-v1 | 0 | 1 | 0 | MODEL_CONCLUSION_LABEL; wrong conclusion |
| screenshot-record-01-v1 | 0 | 1 | 0 | DIA_COMPARISON_PROOF_FEEDBACK; query validation |
| screenshot-record-02-v1 | 0 | 1 | 0 | DIA_COMPARISON_PROOF_FEEDBACK_AND_NATIVE_ANALYSIS_PROJECTION; target |
| screenshot-record-03-v1 | 0 | 1 | 0 | DIA_COMPARISON_PROOF_FEEDBACK; wrong conclusion |
| screenshot-record-04-v1 | 0 | 1 | 0 | DIA_COMPARISON_PROOF_FEEDBACK_AND_NATIVE_ANALYSIS_PROJECTION; wrong conclusion |
| warehouse-scope-v1 | 0 | 1 | 0 | DIA_SCOPE_VERDICT_COMPATIBILITY; wrong conclusion |
| failed-application-load-v1 | 1 | 0 | 0 | NONE; none |
| failed-billing-transform-v1 | 0 | 0 | 1 | MODEL_UNSUPPORTED_CAUSAL_CONCLUSION; wrong conclusion |
| source-history-v2 | 1 | 0 | 0 | NONE; none |
| latency-record-v1 | 1 | 0 | 0 | NONE; none |

Total:6 correct /8 useful nonharmful handoffs /1 harmful. The raw grader partial flag is9 because one harmful answer also carries it; it does not earn handoff credit.

First model errors and later DIA defects remain distinct: screenshot02 first returned malformed undecided; screenshot03 first cited an unknown query. Both subsequently hit misleading DIA proof feedback. Screenshots02/04 also hit exact native SQL/DAX headers and numeric representation mismatch. The repairs do not waive scalar comparison proof or overwrite any native evidence.

The harmful billing answer inferred a correcting-refresh causal history not established by the returned current totals. Its unsupported-claim policy stays advisory as the owner instructed. No engine tuning or regrading from this reasoning error.

Correct-case caveats remain: history adds unproven export provenance, and latency has a last-load timestamp detail caveat. Scores are the grader verdict/layer/cause metric, not a claim that every detail is proven.

All fault controls restored. Native baseline11:48UTC:360 rows, model7661, temporalON; owned latency schedule removed. Source and schema hash qualifications are in baseline-admission and injections records.

Comparison against historical Opus is observational and confounded by code/evaluator/grading differences:6/15 same correct/incorrect classifications. Historical Opus13/15 is not rerun here.
