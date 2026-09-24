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

Completed sequence: E/F/G/I, then two additional G trials (three G trials total).
Same tickets, catalog, deployment, generation settings, daily policy, 65-second
serial pacing and recordings as #219. Each trial gets one new ledger row, labelled
KNOWN_DOMAIN_REGRESSION. Before readback retains GlobalStandard 100 and GPT-5.4
2026-03-05. No configuration, permission, policy or deadline change was made.
All older failed/partial/blocked results remain intact. The stopping contract stays
evaluated and not adopted. After reporting results, propose constant-cost ownership
and reasonable token allowances without implementing either, then stop.


## Matched E/F/G/I results

All four completed on commit `2f04751`, engine fingerprint beginning `50f85a0ac326`,
with the unchanged quality profile. No provider errors occurred. All three G trials are reported below; these four matched rows remain unchanged.

| Family | #218 calls; SQL/native | #219 calls; SQL/native | Revert calls; SQL/native | Revert local rejections | Revert stop |
| --- | --- | --- | --- | ---: | --- |
| E | 2; 0/0 | 6; 0/0 | 3; 0/0 | 1 | TOOL_UNAVAILABLE |
| F | 11; 0/2 | 9; 0/2 | 11; 2/2 | 1 | ENOUGH_DIAGNOSTICS |
| G | 10; 3/0 | 12; 0/1 | 10; 5/0 | 0 | ENOUGH_DIAGNOSTICS |
| I | 11; 0/2 | 11; 0/2 | 7; 0/2 | 0 | CLARIFICATION_REQUIRED |

| Matched aggregate | #218 | #219 | Revert |
| --- | ---: | ---: | ---: |
| Planner calls | 34 | 38 | 31 |
| Successful SQL / native reads | 3 / 4 | 0 / 5 | 7 / 4 |
| Retrieval / test planning calls | 19 / 15 | 23 / 13 | 14 / 14 |
| Context observations (including schema prefetch) | 21 | 23 | 16 |
| SQL proposals / local SQL rejections | 9 / 4 | 1 / 0 | 10 / 2 |
| Local SQL rejection rate | 44.4% | 0% | 20% |
| All local rejections | 6 | 7 | 2 |
| Schema-prefetch repairs | 2 | 0 | 2 |
| Cumulative input characters | 961,138 | 1,203,732 | 863,189 |
| Reserved planner output tokens | 272,000 | 304,000 | 248,000 |
| Summed run wall seconds | 2,426.119 | 3,405.390 | 2,190.282 |

The #219 wall total includes its recorded host/wait anomaly; it is not a clean
latency comparator. Successful reads exclude failed dispatches. Retrieval/test
counts exclude final ASK/STOP decisions and include rejected query proposals.
All matched batches had zero duplicate refusals and zero result-equality overlap
counts. Revert rejections were one SQL column-binding failure in E and a five-join
proposal against the four-join cap in F. F recovered by proposing a smaller query.

E remained blocked by SQL permission error 229 after cold-start connection error
40613. No access change was made. F's two SQL reads measured non-unique rate keys
and 360 base movements expanding to 406 joined rows; the recomputed 57,043 matched
Power BI. The planner emitted SOURCE_OR_APPLICATION_ISSUE, but its use of
"overstated" and its proposed corrected-total test still depend on an unknown
intended valuation rule. Grade this as supported fanout/mechanism evidence with
qualification limits, not a verified defect or corrected total.

G completed BUSINESS_CONTEXT_REQUIRED after five successful source reads. It
found adjustment-side multiplicity, tested stock-side duplicate IDs and preserved
unknown adjustment intent and unconfirmed downstream lineage. Its first successful
query repeats a CASE in SELECT/GROUP BY: offline compilation of that exact proposal
with #218 yields different bound parameters, while the retained fix yields identical
CASE nodes (13 parameters versus 2). The live receipt confirms the fixed query
executed successfully. This directly exercises the compiler repair; it does not
isolate the compiler's effect on the planner's entire trajectory.

I used two native reads and targeted notebook/schema lookup, then asked for a
business glossary/owner defining Q49 and its intended metric treatment. Runtime
label is INSUFFICIENT_EVIDENCE with CLARIFICATION_REQUIRED; no final assessment was
emitted. It did not invent the code meaning or equate observed filter behavior
with intended semantics.

Recorded sessions: E `87ead2e9-bb4c-42cc-9e23-34a64316c6d1`,
F `8168db88-d901-402e-b148-f8b87a579751`,
G1 `c3e4959a-35ed-4785-9b6f-c5d9643a3e61`,
I `e7e58bee-c103-4467-a736-8a4d35fe44ac`.
Local receipts: `.local/ownership-revert-live-20260923/`, including comparison,
recorded context/token audit and `G-live-binding-check.json`.


## All six runs and unconfounded G variance

| Trial | Planner calls | SQL reads | Native reads | Lookups (distinct) | Local rejections | Stop | Wall seconds |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| E | 3 | 0 | 0 | 1 (1) | 1 | TOOL_UNAVAILABLE | 271.249 |
| F | 11 | 2 | 2 | 7 (7) | 1 | ENOUGH_DIAGNOSTICS | 742.573 |
| G1 | 10 | 5 | 0 | 4 (4) | 0 | ENOUGH_DIAGNOSTICS | 694.354 |
| I | 7 | 0 | 2 | 4 (4) | 0 | CLARIFICATION_REQUIRED | 482.106 |
| G2 | 11 | 6 | 0 | 6 (6) | 1 | BUDGET_LIMIT | 769.782 |
| G3 | 11 | 5 | 1 | 7 (7) | 0 | BUDGET_LIMIT | 792.372 |
| Total | 53 | 18 | 5 | 29 (29) | 3 | Three unresolved; F qualified mechanism; G1 business context; I clarification | 3,752.436 |

G source-read counts were **5, 6, 5**, compared with **0, 0, 0** under #219
and three in the original #218 G. Native counts were **0, 0, 1**; planner calls
were **10, 11, 11**; rejections **0, 1, 0**. G2's 16-SELECT/8-cap rejection
recovered to a smaller successful query. G1 stopped ENOUGH_DIAGNOSTICS with
BUSINESS_CONTEXT_REQUIRED. G2 and G3 exhausted six cloud reads and stopped
BUDGET_LIMIT/UNRESOLVED without a final assessment. Their source observations are
useful, but neither is a completed-answer pass. More output tokens alone would
not remove this cloud-read ceiling. No stopping-contract change was adopted.

G2 session: `d789ea5d-0249-4829-b146-d2a7ba7d403b`.
G3 session: `ccd13ccb-ca0f-4e0f-819b-54f0813ce7c3`.

| All-six aggregate | #219 | Revert |
| --- | ---: | ---: |
| Planner calls | 53 | 53 |
| SQL / native successful reads | 0 / 7 | 18 / 5 |
| Retrieval / test proposals | 33 / 18 | 23 / 27 |
| Context observations (distinct) | 33 (32) | 29 (29) |
| SQL proposals / local SQL rejections | 1 / 0 | 22 / 3 |
| Local SQL rejection rate | 0% | 13.6% |
| All local rejections | 10 DAX member | 2 SQL complexity, 1 SQL column binding |
| Schema-prefetch repairs | 0 | 6 |
| Other repairs | 0 | 0 |
| Redundancy refusals / result-equality overlaps | 0 / 0 | 0 / 0 |
| Provider errors | 1 connection error | 0 |
| Cumulative input characters | 1,693,697 | 1,591,030 |
| Reserved planner output tokens | 424,000 | 424,000 |
| Summed wall seconds | 4,469.055 | 3,752.436 |

The original nine-family #218 baseline had 51 calls, 3 SQL and 11 native reads;
its extra families make it unsuitable as the matched denominator. The E/F/G/I
comparison above is the direct comparison. Ledger rows preserve all per-run counters,
rejection details and tape IDs. Low SQL rejection rate under #219 reflected its
single SQL proposal, not better SQL investigation.

The ownership representation caused a deterministic coverage regression. Removing
it materially restored source investigation in this matched sample, and all three
G repeats exceeded the original G's three-source-read count. The original source
path was not a one-off lucky sample. This is stronger evidence than the prior
correlation, but three G samples do not establish a population success rate or
eliminate planner variance. They specifically show remaining variance in completed
conclusions despite reliable source access. F-paced, original baseline F, #219
failures and all prior challenge attempts retain their original outcomes.

## Postflight controls and verification

All 53 recorded calls load with verified body hashes and the same engine fingerprint
`50f85a0ac326f2eb5c9f6dc8f094aedbcade769b7d46e1dc5ca2dcae7ebf835c`,
context `ffbc0be4-225a-47d9-a280-4c0a456646d6` and planner-profile hash
`54add2f373fdf936bd4f86060cf771cb13ab87e66c95936574c3fbccd40c78c4`.
Deployment before/after readbacks are equal: GlobalStandard 100, GPT-5.4 2026-03-05,
100,000 TPM / 1,000 RPM. Policy and settings are unchanged; 12 planner calls,
6 cloud reads, 384,000 cumulative input characters, 48,000 per-call characters,
8,000 output tokens, medium effort, 120-second provider timeout and 1,800-second
run deadline remain. Pacing stays 65 seconds; execution is serial.

Usage records grew 466 -> 549. The 83 new reservations are 53 planner attempts,
six intake calls and 24 cloud dispatches (23 successful reads plus E's failure).
UTC-day totals after the batch are 188 planner/intake calls, 48 cloud dispatches,
5,702,369 input characters and 1,367,500 reserved output tokens, below unchanged
240 / 60 / 8,000,000 / 1,500,000 limits. No active reservations or usage violations
remain. The 117 prior ledger rows are byte-preserved; exactly six rows were appended.
No counters, refunds, grants, freezes, variants or deadline extensions were used.

The 1,009-test engine and required two generator tests passed before live work;
six CI checks passed on the implementation commit. No UI change or dedicated local
browser rerun was required. The initial shell postflight command could not locate
`az`; the existing isolated Azure CLI environment supplied the successful readback.
No control-plane mutation occurred.

Work stops at the [compact ownership and reasoning-budget proposal](ownership-and-reasoning-proposal.md).
Neither proposal is implemented. This is known-domain evidence, not unfamiliar-domain acceptance.
