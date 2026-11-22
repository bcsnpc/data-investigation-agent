# Round 27 pass 2: partial checkpoint

**22/41 raw-reviewed correct, 11 useful handoffs, 5 harmful.** Official 22/41; strict 22/41. This is the saved-grade checkpoint at 2026-11-22 07:00 UTC; the required final denominator is48.

The fixed guard has 15 correct among 18 measured; 2 guard tickets remain. No measured guard answer is harmful. The required20/20 and zero-reviewed-harm gate is **not satisfied**; finishing the denominator cannot erase the retained misses and harmful answers.

Both graders same vendor (OpenAI); independent of investigator vendor (Anthropic).

The measured subset contains eight unchanged billing/sample baselines and one independently graded billing-failure ticket. The one incorrect baseline-S02-v1 answer has the correct layer and cause but calls the implemented calculation DEVIATION instead of the expected AS DESIGNED. Both graders retain that verdict failure; the operator has not changed a score or expectation.

The billing-fault ticket is correct and nonharmful. Its original pipeline definition is hash-restored; the follow-up original job retains the known billing2011 failure. Owner confirmed Direct Lake automatic updates ON; native refresh was accepted and model7661 verified. Fixture pass2 continues after the fresh baseline check. No calibration or v5 attempt has started.

Qualified image362005b0 / source35f4aa5c:5,985tests passed,53skipped, all8shards passed. Native captures are sealed in the existing Blob account; current saved traces are indexed without new estate/model calls.

The five reviewed harmful answers so far are R17-01-v1, R17-02-v1, R17-05-v1, older-export-movement-1-v2 and latency-900501-v1. The latest latency answer locates the source-to-Bronze split but substitutes a source-history explanation for scheduled-load latency. Its saved triage actually retains an enabled future schedule; `next_due` is null because recurrence normalization did not support that configuration. A successful temporal AS OF query shows the row absent at the prior load, but ordering application-modified timestamps does not establish the asserted deletion/reinsertion timeline. The validator also refused the discovered hidden temporal period columns. These are retained engine limitations, not changed expectations or an invalid latency fixture.

The current serialized latency controller must finish and restore its rows/schedule before access and stale controls proceed. Pass2 stays on its original image throughout. Fresh calibration and v5 remain unstarted and blocked by the quality gate.
