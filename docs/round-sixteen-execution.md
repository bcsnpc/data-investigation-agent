# Round Sixteen execution record

Started 2026-10-12 05:50:24 UTC. Part A ends no later than 07:50:24 UTC; each following part receives its own maximum two-hour window and continues without an owner wait. Work remains on draft #423, which will not be merged.

## Owner approval and shared accounting

The supplied `round-sixteen-claim-first-redesign.md` authorizes a new maximum $25 of model spend, with the hard ceiling set to the actual starting shared total plus $25. The retained starting total is **$94.704272**; the policy ceiling changed from $190 to **$119.704272**. Counters and 13 historical uncertain calls remain unchanged. The existing $10 protected margin is retained, so new admission currently has $15 headroom below that margin. These are conservative rate-card estimates, not the provider invoice.

The same canonical model ledger and estate pot remain in use. Pot starts at 2,641/4,000; restoration reserve 95, rolling limit 3,000, investigation diagnostic cap 12 and disk floor 10 GiB remain unchanged. Model billing or authorization refusal stops new live admissions without retry. Each part has at most one live smoke batch, at most three tickets and 15 minutes; the only full scored run is Part D.

A1 explicitly authorizes connection User on the billing SQL connection and VIEW DEFINITION on billing tables for existing investigators, with before/after control evidence. Operator-fetched Copy definitions are onboarding evidence with that operator's provenance. No new identity or credential is authorized. Part D permits new scenarios through the existing build/seed path and its publisher, never investigator writes.

## DECIDED WITHOUT REVIEW

- The installed CLAUDE.md contains no `Standing approvals (owner)` heading. The explicit grants in the supplied A1 instructions are sufficient authorization for those grants only; no missing broader standing grant is invented.
- Connection User is granted only to the existing identity that produced the retained connection 403, after identity verification. The connection uses an existing owner credential; User is permission to use that stored connection and is not described as a SELECT-only role. Diagnostic SQL remains isolated to its existing reader credential.
- The old $10 margin is retained because the new $25 limit is a maximum and the instructions preserve other limits. Removing that margin to consume the whole $25 was rejected.
- Part A repairs may assess an explicitly named chain's readiness only if the scoring consumer is bound to that scope. A partial global estate is never relabelled complete. The former exhaustive gate must not make an unrelated, unready application branch invalidate an independently proven original chain; missing proof still blocks.
- The requested eight workers are the default live queue width. The shared budget, capture isolation and disk admission conditions still govern actual concurrency. Code work uses the available three helper slots plus the root; eight coding agents are not available.

Part reports will carry actual work, failures, tests, live usage and commit hashes. No historical ticket, tape or expectation is rewritten.
