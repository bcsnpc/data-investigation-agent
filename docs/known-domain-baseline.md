# Known-domain baseline after items 1-8

2026-09-23. Issue #199. Known-domain regression only; no fresh freeze or variant.

## Readiness review

Removed unused read_redundancy.normalized and its obsolete lexical-only test.
compiled_read comes directly from the SQL/DAX compilers; their identity and
nonblocking-distinct-read tests remain. Ten focused redundancy tests passed in
14.361 seconds. Test reserves deliberately count proposed turns, including rejected
queries: counting only admitted queries lets invalid proposals retain protection.
Successful reads and rejections remain separate metrics; zero reads is not success.
See [budget decision](retrieval-test-budgets.md#baseline-review-decision-2026-09-23).

## Authorized Azure capacity change

Immediately before the change, regional GlobalStandard GPT-5.4 allocation was
10 of 1,000 units. Applied only investigator-quality-54 SKU capacity 10 to 100
using the deployment PATCH API. Before/after control-plane reads show 10,000 to
100,000 TPM and 100 to 1,000 RPM; provisioning succeeded. Model gpt-5.4 version
2026-03-05 and GlobalStandard SKU were preserved. No other Azure changes were made.
SQL tier, AutoPause, firewall and connections are unchanged. The API supports a
SKU-only patch: [Microsoft deployment update](https://learn.microsoft.com/en-us/rest/api/aiservices/accountmanagement/deployments/update?view=rest-aiservices-accountmanagement-2024-10-01).

Receipt: .local/provider-capacity-applied-20260923.json, with before/after bodies,
immediate quota check and verification time. Both GPT-5.4 configuration files now
reflect capacity 100; generation settings remain medium reasoning, 8,000 output
tokens, 48,000 input characters, 120-second timeout and one metered connection
recovery. No inference calls were used to apply capacity.

## Evaluation gate

Use one worker with at least 65-second start spacing and original deadlines and
usage records. Validate provider pacing first, then record a known-domain A-I
baseline with this same configuration. Preserve every failure/partial/hold.
Any Azure environment failure stops evaluation without changing settings.
Compare with F-paced, 125414e5, e8b3d11a and the v2 post-repair matrix. Then stop
and report; no freeze follows automatically. F-paced remains FAILED and unfamiliar
acceptance remains unproven. The recorded partial outcome follows below.

## Validation before the baseline

The initial full suite ran 1,002 tests and failed one stale import of the removed
helper (266.594 seconds). That test now exercises compiler identity directly: alias
changes match, while expressions, filters and query structures remain distinct.
All 36 flexible-investigation tests passed (5.818 seconds); the full rerun passed
all 1,002 tests (243.356 seconds). The count decreased by one because the obsolete
lexical-helper test was removed. The initial failure remains recorded.

Two metered known-state provider probes used the intended full generation settings
and completed with no provider errors. Starts were 65.001 seconds apart; each
request used 15,019 input tokens, with 2,910 and 1,095 output tokens. These calls
executed no data tools and are not business investigations or acceptance. Receipt:
.local/baseline-capacity-probe-20260923.json. They charged the existing latest
catalog and usage policy without resetting prior reservations or increasing limits.
The baseline uses that same profile and catalog, targeting the known v2 tickets.

## Historical controls (unchanged)

| Saved session | Planner calls | SQL / native reads | Retrieval / test proposals | Retrieval:test | Stop |
| --- | ---: | ---: | ---: | ---: | --- |
| F-paced: 5b0e19c4-8027-4499-8695-53c89adc3876 | 6 | 0 / 5 | 0 / 6 | 0 | BUDGET_LIMIT |
| 125414e5-43ea-491d-afb0-9f0f0850551a | 11 | 0 / 1 | 8 / 1 | 8 | ENOUGH_DIAGNOSTICS |
| e8b3d11a-08af-47f7-82a5-816405cf3b4b | 11 | 3 / 1 | 6 / 4 | 1.5 | ENOUGH_DIAGNOSTICS |

The v2 matrix had 7 successful reads across 9 submitted tickets (0.778 per ticket),
no planner LOOKUP decisions and 8 test proposals. A/B/C/D/F/G read counts were
1/1/2/1/1/1; E/H/I had zero. D/E/F/G recorded RateLimitError. A stopped NO_PROGRESS;
B asked an unnecessary clarification; C reproduced arithmetic but did not establish
why the balance was low; D/E/F/G were incomplete; H asked for available metadata;
I was HELD at intake. These are the original failed/partial/blocked assessments.
The prior description of A's five native values refers to values from one query,
not five successful read receipts. The comparison counts receipt-bearing reads.

These are trajectory comparisons, not a controlled model/engine A/B experiment:
F-paced used six planner calls, 80,000 cumulative input characters and 900 seconds;
the current engine allows twelve, 384,000 and 1,800 respectively. 125414e5 used a
4,000-token output allowance; e8b3d11a used 8,000 and the current generation options
but investigated the v3 variant. The new baseline uses the v2 ticket text unchanged
and the approved current profile. No historical model/settings fields are inferred
where absent. Detailed post-hoc counters are retained in
.local/known-baseline-20260923/prior-comparison.json; no historical result was edited.

## Recorded-session replay

Session 2fd74595-df28-48c0-b5e7-f50742f0d704 retained eleven complete planner tapes.
Every request used investigator-quality-54, medium reasoning and 8,000 maximum
output tokens. Full offline replay 54c66e00-7791-4796-a680-9e88695837fd MATCHED
all eleven requests byte-for-byte, with zero network calls, zero unrecorded tool
attempts, no engine drift and no projected state differences (5.898 seconds).
Receipt: .local/known-baseline-20260923/replay-F/result.json. A matched replay
reproduces the failed trajectory; it does not upgrade its business outcome.

The baseline uses the latest retained catalog, including subsequently discovered
variants, without changing their runtime registrations. This is another comparison
limit alongside the historical budget/profile differences noted above.

## Partial baseline: stopped on Azure permission failure

All five runs are KNOWN_DOMAIN_REGRESSION, engine fingerprint
049c33cb55b8 (full hashes in their session receipts), settings hash
54add2f373fdf936bd4f86060cf771cb13ab87e66c95936574c3fbccd40c78c4.
They used the same deployment, model version, generation settings and serial
65-second pacing as the successful provider probes. Intake keeps its existing
separate 1,500-token resolver allowance; the reported profile is the planner's.
The original latest-catalog policy remains 240 planner calls, 60 cloud calls,
8,000,000 input characters and 1,500,000 output reservations per UTC day.
Catalog usage grew from 315 records immediately before the baseline to 353 after
it (313 original records plus two probes and 38 baseline reservations). No counters
were reset, reservations refunded, daily policy increased or deadlines extended.

The freshness case selected app.dataset_runs. The saved child failure receipt
15893e97-13ad-4452-b16f-e3791381860b records connection attempt 1 failing with
40613, a ten-second bounded wait, and attempt 2 reaching query execution but
failing with SqlException 229. The first error was the expected AutoPause cold
start; the terminal blocker was SELECT permission on the proposed table.
The failure receipt is retained at
.local/known-baseline-20260923/environment-failure.json. No SQL tier, AutoPause,
firewall, connection or grants were changed, and the held run was not resumed.
The evaluator stopped the batch immediately after this run, as instructed.
A/G/H/I were not started; they have no fabricated run/ledger rows.

| Family / session prefix | Planner calls | Successful SQL / native reads | Retrieval / test proposals | Retrieval:test | Stop | Wall seconds |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| F / 2fd74595 | 11 | 0 / 2 | 5 / 6 | 0.833 | NO_PROGRESS | 760.278 |
| B / fa3b3f3c | 6 | 0 / 1 | 3 / 1 | 3.000 | ENOUGH_DIAGNOSTICS | 431.671 |
| C / 80bcbb4a | 3 | 0 / 2 | 0 / 2 | 0.000 | ENOUGH_DIAGNOSTICS | 217.418 |
| D / ef15c75e | 3 | 0 / 2 | 0 / 2 | 0.000 | ENOUGH_DIAGNOSTICS | 228.172 |
| E / 3accd519 | 2 | 0 / 0 | 1 / 1 | 1.000 | TOOL_UNAVAILABLE | 202.896 |
| A/G/H/I | Not run | Not measured | Not measured | Not measured | Stopped after E's permission failure | Not measured |

Wall seconds include intake and the investigation, exclude the inter-run 65-second
wait, and are not directly equivalent to historical session-event-only durations.
One ledger row exists per attempted investigation, plus separate provider-probe,
operator-change, offline test and replay records. Raw runs remain in
.local/unknown-domain-v4/runs/*-baseline-20260923.json and all planner tapes remain
under .local/planner-recordings. No historical run was replaced.

| Family | Rejections by kind | Repairs by kind | Redundancy refusals | Equal-result overlap | Schema prefetch | SQL rejection rate | Provider errors by kind |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| F | 1 complexity; 3 other (2 DAX members, 1 unavailable SQL object) | None | 0 | 0 | 0 | 2 / 2 = 100% | 0 rate-limit / 0 timeout / 0 other |
| B | 1 schema (unknown assessment evidence) | None | 0 | 0 | 0 | No SQL proposals | 0 / 0 / 0 |
| C | None | None | 0 | 0 | 0 | No SQL proposals | 0 / 0 / 0 |
| D | None | None | 0 | 0 | 0 | No SQL proposals | 0 / 0 / 0 |
| E | None locally; 1 SQL execution failure | None | 0 | 0 | 0 | 0 / 1 = 0% | 0 / 0 / 0 |

The SQL permission error is a data-tool failure, not an LLM provider error or a
local SQL rejection. Repairs by hypothesis_id, text_bound, schema_prefetch and
other are all zero. Result equality remains a reporting-only exact-result metric;
zero does not mean these reads had no semantic overlap.

Aggregate for the five attempted families: 25 planner calls, 7 successful reads
(all native; 0 SQL), 9 retrieval decisions and 12 test proposals, ratio 0.75.
Successful reads per attempted run are 1.4. There were 8 reserved data calls,
including E's failed read. Rejections total 1 schema, 0 prerequisite, 0 redundancy,
1 complexity and 3 other. Repairs, redundancy refusals, result-equality overlaps,
schema-prefetch repairs and LLM provider errors are all zero. SQL rejection rate
is 2/3 (66.7%); the third proposal was admitted but failed at execution. Within-run
wall time totals 1,840.435 seconds. Full counters and capacity provenance are in
the append-only ledger and .local/known-baseline-20260923/aggregate.json.

## Outcome comparison and freeze decision

- F remains a failed investigation: two native reads and relevant transformation
  retrieval did not lead to an executable source test. Four rejected proposals
  ended in NO_PROGRESS. It measured current value/structure but did not establish
  the mechanism. Compared with F-paced, it uses fewer reads (2 versus 5), more
  retrieval (5 versus 0), and still no SQL. Compared with 125414e5, reads improve
  from 1 to 2 and retrieval:test drops from 8 to 0.833, but compared with e8b3d11a
  it falls short of four reads including three SQL mechanism tests. F-paced stays
  FAILED; no attempt was relabelled as acceptance.
- B now explains 6,425 / 8,765 = 0.733029092983457 using the actual component
  definitions, preserving the missing business benchmark. This completes the
  scoped calculation request more usefully than the old unnecessary clarification,
  but costs six planner calls and one citation rejection for one native read.
  EXPECTED_BEHAVIOR is limited to the implemented calculation, not business intent.
- C explains 6,425 - 2,340 = 4,085 and tests movement-type behavior in two reads.
  BUSINESS_CONTEXT_REQUIRED preserves the unknown expectation behind 'too low',
  improving on the old shallow expected-behavior label. Three planner calls, no
  rejected proposal or provider error.
- D reproduces North 3,359 versus global 8,765, and explicitly excludes hidden
  page/visual filters, interactions and RLS. Three calls/two reads complete the
  scoped request; the old attempt stopped after a read and RateLimitError.
- E consulted metadata and proposed a real catalog table instead of inventing
  INFORMATION_SCHEMA.REFRESH_HISTORY. Its admitted query was permission-denied,
  so no freshness conclusion or SLA violation is established. This is BLOCKED,
  not a correctness pass. No permission expansion was used to rescue it.

The same five historical matrix families had five reads (1.0 per attempted ticket)
and three RateLimitError blocks; the new subset has seven reads (1.4) and no LLM
provider errors, but one SQL permission blocker. Historical retrieval:test was
0/6 versus the new 9/12: a larger ratio here reflects using context that the old
runs did not inspect, so it cannot simply be called an improvement. The original
nine-family total remains seven reads across nine tickets; do not compare its
mean directly to the incomplete five-family mean without the different denominator.

**Do not freeze on this evidence.** The full baseline is incomplete and the core
transformation test-selection failure persists despite improved scoped answers
and provider reliability. The next decision is how to address source eligibility
and test selection, including whether app.dataset_runs is actually relevant to
this domain before proposing any additional reader grant. No Azure setting change
is proposed merely to rescue the held run. A/G/H/I and the full aggregate gate
remain pending. Stop here for review: no engine tuning, new freeze, new variant
or unfamiliar-domain acceptance claim follows this partial baseline.

Final local audit: 195 Markdown file targets resolved, 96 unique ledger IDs, every
notes document present, and all historical ledger lines preserved. Staged secret
scan and git diff --check passed. PR CI tracks the final commit. No live run was
started after E; the batch process exited normally after recording the hold.
