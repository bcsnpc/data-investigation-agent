# Expected net cash after refunds

Run `python scripts/lab_investigator.py --explain-returns` against the reset local lab.
The explicit question is `why_net_cash_below_captures`, using the fixed
`captured-minus-refunds-v1` contract. It is not a general revenue-trend explanation.

Business drivers and Silver/Gold comparison rows are captured in one DuckDB statement.
The verifier requires matching records, complete one-to-one business-key/currency
coverage, valid capture/refund amounts, refunds no greater than captures, and exact
capture-minus-refund arithmetic for every order. At least one positive refund must
support the explanation. It never reads evaluation answers or scenario labels.

The reset fixture verifies USD 253 captured minus USD 99 refunded equals USD 154 net
cash. Both compared layers match, so the narrowly scoped result is EXPECTED_BEHAVIOR.
Evidence records and the business contract are retained alongside the investigation,
with an evidence hash covering both comparison and business context. No bug is routed.

Missing business evidence, unsupported questions, scope differences, incorrect
arithmetic or record mismatches remain UNRESOLVED. Duplicate/invalid drivers reject the
attempt. Plain reconciliation without business context still remains UNRESOLVED.

This demonstrates one mandatory no-defect lab case. It does not verify real-world refund
authorization, full-estate correctness, snapshot comparability outside the local query,
or month-over-month business drivers. It is not yet wired to ticket interpretation or
the investigation UI. Verified technical-defect causes remain a separate next step.

Validation: local saved investigation 606c4909-9a79-40bc-9602-f43fe191ef73 returned
EXPECTED_BEHAVIOR with the exact arithmetic above. Tests cover omission, missing/scope
and arithmetic evidence, invalid drivers and matching-without-context behavior. No
cloud queries, LLM calls or baseline changes occurred.
