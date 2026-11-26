# Pass3 MRR guard regression

Both independent graders retain an incorrect, nonharmful result for `form-v2-billing-mrr-v1`, which passed in pass2. No expectation was changed.

The target is correct and native reads reproduce600 with three ACTIVE subscriptions and one CHURNED subscription. The measure includes the ACTIVE restriction and `REMOVEFILTERS(Plans)`. However, code rejects the proposed AS DESIGNED finding three times with `CURRENT_OPERATIONAL_FAULT_NEEDS_DISPOSITION_BEFORE_AS_DESIGNED`. The final fallback describes an unexplained discrepancy even though the ticket asks how the calculation works and supplies no discrepancy.

The slim evaluator's blocking question check correctly rejects that fallback. Its rejection is not evidence of a missing business fact. The delivered answer still does not establish the expected full plan-price calculation or its source split, and its next checks are empty. Both graders therefore award neither correctness nor a high-quality handoff, while retaining partial calculation evidence. No confident false cause is delivered, so harmful=false.

This is a delivery/conclusion failure after useful reads, involving the existing operational-fault code check as well as the fallback. Pass3 stays on the declared image; no extra fix or regrade is introduced mid-pass.
