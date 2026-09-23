# Ownership-label revert and controlled re-evaluation

2026-09-23. Follows reviewed #219; issue #199. Known-domain work only.

## Accepted and rejected changes

The user rejected the per-entry ownership representation in #219. It is removed
from directory entries, semantic context, profiles, discovery lookups and excerpts.
Repeated typed SQL literal binding, its regression test, measured SELECT/join caps,
connection-qualified unavailable-object hints and cross-connection rejection
statements remain. One-time SQL capability connection/schema information remains.
No compact replacement, token increase or stopping-contract field is implemented.

## Offline F call-1 coverage

| Engine | Directory entries | SQL objects | Pre-wire characters | Request bytes |
| --- | ---: | ---: | ---: | ---: |
| #218 | 28 | 11 | 14,441 | 27,902 |
| #219 labels | 11 | 3 | 17,364 | 31,236 |
| Reverted labels; accepted fixes retained | 28 | 11 | 14,538 | 28,217 |

Reconstruction uses the recorded #218 state and pinned catalog, with current
capabilities/projection and an injected SDK transport. No model or data query is
needed to verify coverage. A first request-size harness used the wrong mock branch
and failed DNS against a dummy endpoint; no real provider call or usage reservation
occurred. The corrected injected-transport check supplies the request size above.
A synthetic directory fixture preserves the original lengths/order and asserts
28 entries / 11 SQL objects survive projection. The existing query-binding and
rejection tests remain unchanged. CONTRIBUTING now requires before/after directory,
SQL-object and payload-size measurements plus coverage tests for context additions.

Ten projection and six compiler/feedback tests pass. All 1,009 local regression
tests passed before live work (366 seconds). Local receipts: `.local/ownership-revert-20260923/`.

## Evaluation boundary

Planned sequence: E/F/G/I, then two additional G trials (three G trials total).
Same tickets, catalog, deployment, generation settings, daily policy, 65-second
serial pacing and recordings as #219. Each trial gets one new ledger row, labelled
KNOWN_DOMAIN_REGRESSION. Before readback retains GlobalStandard 100 and GPT-5.4
2026-03-05. No configuration, permission, policy or deadline change is planned.
All older failed/partial/blocked results remain intact. The stopping contract stays
evaluated and not adopted. After reporting results, propose constant-cost ownership
and reasonable token allowances without implementing either, then stop.
