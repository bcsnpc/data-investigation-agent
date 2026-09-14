# Multi-layer evaluation matrix

Run `python scripts/evaluate_multilayer_matrix.py`. Each run uses a new directory under
.local/multilayer-matrices, or a new --output path. Reports retain expected/observed boundaries,
evidence run IDs, affected order IDs, exact impact and reset status. Failures return a nonzero
exit code. Existing output directories are never overwritten.

| Scenario | Bronze/Silver difference | Silver/Gold difference | First local mismatch |
| --- | ---: | ---: | --- |
| Matching | USD 0, no affected records | USD 0 | None |
| Propagated Silver change | USD +10, one order | USD 0 | Bronze/Silver |
| Gold omission | USD 0 | USD -99, one order | Silver/Gold |
| Offsetting Silver changes | USD 0, two orders | USD 0 | Bronze/Silver |
| Both boundaries affected | USD +10, one order | USD -99, one order | Bronze/Silver |

The offsetting case increases ORD-000002 by USD 10 and decreases ORD-000001 by USD 10, with
corresponding Silver order/line changes propagated through shared Gold SQL. Aggregate net cash
remains USD 154. Record-level reconciliation must still report MISMATCH and both affected IDs.
The two-boundary case must retain both discrepancies while identifying the earlier observation.

Expected answers are evaluator-only. The investigator receives the same local business
projection used by reviewed execution, without case names or expected findings. All results
must remain UNRESOLVED with root cause unverified and automatic routing disabled. Each fresh
fixture resets and verifies the original baseline before the case completes.

This extends local regression coverage, not transformation-cause proof, cloud validation,
model/DAX evaluation or full product acceptance. Product acceptance remains false. Live data,
LLM and external delivery are not invoked. Broader business/currency/model scenarios and
end-to-end hosted acceptance remain pending.
