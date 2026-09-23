# Baseline completion and stopping-criteria review

2026-09-23. Issue #199. Follow-up to accepted PR #217.
Known-domain regressions and next-action proposal evaluation only. No engine
change, freeze, variant or unfamiliar-domain acceptance claim.

## Completed A-I baseline

A/G/H/I completed under the same profile, deployment, engine fingerprint
`049c33cb55b8`, generation settings and serial 65-second pacing as the earlier
F/B/C/D/E runs. Every run has planner recordings and one append-only ledger row.
Original failures are unchanged, including F-paced and current F. No settings,
permissions, usage policy or deadlines changed. Usage counters were never reset
and reservations were never refunded.
The model is GPT-5.4 version 2026-03-05, medium reasoning, 8,000 output tokens,
48,000 payload characters, 120-second timeout. Intake retains its separate
existing 1,500-token allowance. Capacity was read back again at
2026-09-23T17:28:00.532103+00:00: GlobalStandard 100 units, 100,000 TPM / 1,000 RPM.
No control-plane change was made; the original before/after change is in
[the prior baseline evidence](known-domain-baseline.md#authorized-azure-capacity-change).

**G attempted source reads: five SQL proposals, three successful SQL reads,
one local complexity rejection and one execution failure. It made no DAX read.**
A universal DAX-only stopping diagnosis is therefore too broad. The full baseline
exposes several independent issues: premature stopping in A; query-size and
connection-name selection in F; wrong freshness target in E; a compiler defect in
G; and expensive retrieval plus a cross-system query in I. C/D/H contain useful
native scope/definition contrasts and should not be forced to query SQL.

| Family / session prefix | Planner | SQL / native reads | Retrieval / tests | Retrieval:test | Stop / outcome | Wall seconds |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| A / 18958b85 | 2 | 0 / 1 | 0 / 1 | 0.000 | ENOUGH_DIAGNOSTICS / BUSINESS_CONTEXT_REQUIRED | 156.624 |
| B / fa3b3f3c | 6 | 0 / 1 | 3 / 1 | 3.000 | ENOUGH_DIAGNOSTICS / EXPECTED_BEHAVIOR | 431.671 |
| C / 80bcbb4a | 3 | 0 / 2 | 0 / 2 | 0.000 | ENOUGH_DIAGNOSTICS / BUSINESS_CONTEXT_REQUIRED | 217.418 |
| D / ef15c75e | 3 | 0 / 2 | 0 / 2 | 0.000 | ENOUGH_DIAGNOSTICS / EXPECTED_BEHAVIOR | 228.172 |
| E / 3accd519 | 2 | 0 / 0 | 1 / 1 | 1.000 | TOOL_UNAVAILABLE / UNRESOLVED | 202.896 |
| F / 2fd74595 | 11 | 0 / 2 | 5 / 6 | 0.833 | NO_PROGRESS / UNRESOLVED | 760.278 |
| G / 39503ca8 | 10 | 3 / 0 | 5 / 5 | 1.000 | TOOL_UNAVAILABLE / UNRESOLVED | 714.742 |
| H / 1269eb9d | 3 | 0 / 1 | 0 / 1 | 0.000 | ENOUGH_DIAGNOSTICS / BUSINESS_CONTEXT_REQUIRED | 218.875 |
| I / 975c71b9 | 11 | 0 / 2 | 8 / 3 | 2.667 | BUDGET_LIMIT / UNRESOLVED | 748.203 |

Aggregate: **51 planner calls, 14 successful reads (3 SQL, 11 native), 22 retrieval
proposals and 22 test proposals, retrieval:test 1.0**. Mean successful reads per
attempt: 14/9 = 1.556. Sixteen data calls were reserved, including E/G execution
failures. Nine SQL proposals, four local rejections: **44.4% SQL rejection rate**.
Two schema-prefetch repairs, no other repairs. Zero provider errors, redundancy
refusals or exact-result-equality overlap events. Zero exact overlap does not mean
zero semantic redundancy. Total within-run wall time 3,678.879 seconds includes
intake and excludes inter-run waiting. Cumulative planner input 1,261,082 characters;
planner output reservations 408,000 tokens. Usage records rose from 353 after the
first five baseline cases to 391 after A/G/H/I; none were removed or refunded.

| Family | Rejections | Repairs | Provider errors | Redundancy / equal-result overlap | Schema prefetch | SQL rejection rate |
| --- | --- | --- | --- | ---: | ---: | --- |
| A | None | None | 0 rate-limit / 0 timeout / 0 other | 0 / 0 | 0 | No proposals |
| B | 1 schema | None | 0 rate-limit / 0 timeout / 0 other | 0 / 0 | 0 | No proposals |
| C | None | None | 0 rate-limit / 0 timeout / 0 other | 0 / 0 | 0 | No proposals |
| D | None | None | 0 rate-limit / 0 timeout / 0 other | 0 / 0 | 0 | No proposals |
| E | None | None | 0 rate-limit / 0 timeout / 0 other | 0 / 0 | 0 | 0/1 |
| F | 1 complexity, 3 other | None | 0 rate-limit / 0 timeout / 0 other | 0 / 0 | 0 | 2/2 |
| G | 1 complexity | 2 schema_prefetch | 0 rate-limit / 0 timeout / 0 other | 0 / 0 | 2 | 1/5 |
| H | 1 schema | None | 0 rate-limit / 0 timeout / 0 other | 0 / 0 | 0 | No proposals |
| I | 1 other | None | 0 rate-limit / 0 timeout / 0 other | 0 / 0 | 0 | 1/1 |

Eight local rejections total: two schema, two complexity, four other. E's 229
and G's 8120 are separate execution failures. The seven context observations in G
include two local schema-prefetch observations; only five were planner retrieval
proposals. See [all exact SQL and failure classes](baseline-sql-proposals.md).

Interpretations remain manually reviewed, not automatic business grades:

- A stopped after one native read with a conditional gross-versus-net explanation,
  explicitly admitting it had not retrieved the source total or query. That is
  honest uncertainty but incomplete technical investigation of the discrepancy.
- B calculated the ratio and its components. C tested the derived calculation and
  a movement-type breakdown, preserving the unknown meaning of "too low."
- D tested explicit North scope against global scope; hidden visual/RLS context
  remains unknown. Its scoped contrast is more than scalar reproduction.
- E selected application `dataset_runs` and failed permission. It did not inspect
  relevant processing history already available in context.
- F found notebook join logic but both SQL proposals were rejected. It remains
  FAILED / UNRESOLVED, not rescued by metadata or repeated native values.
- G reached source stock movements and adjustments, then SQL error 8120 held the
  run. Source-read capability worked; the final failure is not DAX-only stopping.
- H explained the implemented RECEIPT/ISSUE filters with a native breakdown and
  preserved missing business intent; an unnecessary assessment-reference rejection
  cost one turn.
- I made eight lookups, proposed an inadmissible cross-system join, then completed
  two native reads. It ended BUDGET_LIMIT / UNRESOLVED after eleven planner calls;
  it had accumulated 341,649 planner input characters. It did not
  invent the code's intended meaning, but did not deliver a final answer.

The earlier five-run report and historical control trajectories remain in
[known-domain baseline](known-domain-baseline.md). New runs are retained at
`.local/unknown-domain-v4/runs/*-baseline-completion-20260923.json`, with summaries
and tape audit in `.local/known-baseline-completion-20260923/`.

## E: freshness evidence and access decision

**Case (a), within the existing metadata-context capability. No grant applied.**
The discovered notebook `Warehouse valuation e1b8e1`
(`7ccafe59-0460-4c8a-a691-bfdfa75a2b25`) has an AVAILABLE `run_history` observation.
It records RunNotebook job `1d24514c-9115-43a4-9953-fe7920a05fd1`, started
2026-09-18T18:12:02.4546073, completed 2026-09-18T18:13:23.9191421, status Completed,
with no recorded failure reason. The definition and derived lineage connect this
notebook to Gold `movement_values` and its Silver input tables. These are ordinary
collected metadata and lineage, not publisher/evaluator truth.

The unchanged runtime LOOKUP(asset) returned that history in completed context
receipt `b607eca6-18a5-498c-9779-fb0d36d4b4fa`; it is saved locally as
`freshness-context-receipt.json`. E's original first payload already exposed the
correct notebook as a context entry point, alongside the unrelated application
registry. E chose only the registry lookup before its failed SQL query.

The access claim is precise: the investigation can read the approved, locally
retained metadata through its existing context tool. This is not a claim that the
SQL principal or Power BI query reader can call Fabric job APIs directly; collection
uses its separately isolated metadata identity. No credentials were substituted.
The scan was created on September 19 at 06:02:00.695868 UTC, so this is historical
processing evidence, not a fresh September 23 API observation or proof of current
end-to-end freshness. It permits a limited answer with explicit scan age.

No domain-specific publication registry, watermark/run-marker table or marker write
was found in the discovered domain assets and notebook text. Source `event_day`
is an event date stored as text, not an ingestion watermark or SLA. The discovered
`app.dataset_runs` schema includes `order_count`, `seed`, `manifest_sha256`, `as_of`
and `completed_at`; no discovered domain lineage links it to this notebook/model.
Its relevance cannot be assumed from the word "runs." No SLA was supplied in E.
The model refresh-history observation is AVAILABLE with an empty list; the Gold
lakehouse lists five business tables and records UNKNOWN column-schema coverage.
Neither supplies an observed model-refresh timestamp. Further current-refresh
coverage may still be unavailable; that limit does not
justify granting access to the application registry. The original E failure is
preserved. No E rerun was needed under (a); the authorized grant/rerun branch (b)
was not triggered.

## Evaluated and not adopted: completion contract

Extend #207's existing support object by two bounded fields, retaining mechanism,
mechanism receipts, intent dependency/basis/receipts and remaining_test:

- `completion_basis`: `SUFFICIENT_EVIDENCE`, `BUSINESS_CONTEXT`, `BUDGET`,
  `CAPABILITY`, `SCOPE`, `PERMISSION` or `ELIGIBILITY`.
- `completion_reason`: at most 1,000 characters: what requested question is
  resolved, what material part remains unanswered, and why the best remaining
  test is unnecessary or unavailable.

For cause, defect, source/application, freshness or expected-behavior assertions,
require an explicit evidence contrast that distinguishes the mechanism from a
plausible alternative, or a claim-scoped explanation of why further evidence is
not needed/available. Merely reproducing the symptom is not mechanism evidence.
If evidence is unavailable, preserve the corresponding uncertainty; the reason
is not permission to assert a cause. Existing intent consistency and receipt
checks remain. A missing business rule does not automatically make a useful
technical test unavailable.

A native-only answer can use SUFFICIENT_EVIDENCE when a scoped definition/filter
contrast resolves the actual request. Honest uncertainty can use BUSINESS_CONTEXT
or a demonstrated limit. No required SQL, layer order, read count, family-specific
route or domain mapping. The validator can check field shape, references and
explicit consistency; it cannot certify a free-text causal explanation. The
proposal improves auditability and guidance, not deterministic semantic proof.

## Controlled next-action comparison

Eight metered provider calls compared one control and one revised-contract sample
at each saved point. Same deployment/profile/generation settings, serial 65-second
minimum spacing, recording enabled; no data tools or original runs resumed.
**All four control requests matched the corresponding original request bytes.**
Within each pair the requests are equal except for instructions and tool schema.
The saved observations, candidates, budgets and capabilities are unchanged.

| Saved point | Fresh control next action | Revised-contract next action | Offline check / interpretation |
| --- | --- | --- | --- |
| C call 3, after derived/component and movement-type reads | STOP / BUSINESS_CONTEXT_REQUIRED | STOP / EXPECTED_BEHAVIOR, intent UNKNOWN, completion SUFFICIENT_EVIDENCE | Revised proposal rejected by unchanged #207 intent check; no demonstrated improvement |
| D call 3, after North/global contrast | STOP / EXPECTED_BEHAVIOR | STOP / EXPECTED_BEHAVIOR, completion SUFFICIENT_EVIDENCE | Both valid; revised reason explicitly limits the answer to supplied scope and names missing visual/RLS context |
| F before original call 10 | QUERY bounded_dax, fanout by product | QUERY bounded_dax, fanout by movement and product | Both fail offline compiler: `Unknown or ambiguous DAX member`; neither would execute |
| F before original call 11 | QUERY bounded_sql, 7 SELECTs / 1 join | QUERY bounded_sql, 4 SELECTs / 3 joins | Both within complexity caps but still use `dbo` source names; both fail offline compiler: `SQL object unavailable or view dependencies not validated` |

The revised C rejection is exactly: `Conclusion depends on unknown business intent:
qualify as BUSINESS_CONTEXT_REQUIRED or investigate the missing premise`. The
provider returned a complete function call; this was a local conclusion-validation
failure, not a transport/provider error. The replay harness's generic failure row
initially put ValueError in `provider_errors.other`; an append-only
METRIC_CORRECTION record links that row and supplies the correct category (one
schema rejection, zero provider errors). The original row, tape and reservation
remain untouched. The harness retained its conservative charged reservation when
validation failed; no reservation was refunded.

The four QUERY responses passed proposal-shape validation, which is all the live
next-action harness performs. Their subsequent offline compiler checks all failed.
No source/native query was dispatched, no compiler workaround was applied, and
no result or successful investigation is implied by `VALID_PROPOSAL`.

This is one sample per condition, with control before revision in each pair and
no repetitions. F's new control differs from its original recorded next action
although its request is byte-exact; model variability is material. D demonstrates
that the proposed wording permits a justified native-only stop. C shows the new
fields do not eliminate unsupported confidence and can accompany a worse label.
F provides no evidence of improved admissible test selection. **This comparison
does not demonstrate a reliability gain and does not justify implementing the
proposal unchanged as a proven fix.** It remains a review draft. Keep the existing
intent guard; review task coverage and claim-scoped sufficiency separately from
query binding and compiler correctness. No mandatory SQL route follows.

Calls used 95,842 input tokens and 14,713 output tokens in provider responses;
64,000 output tokens were reserved. Provider-call elapsed time totals 197.611
seconds, excluding inter-call waits. Zero data calls and zero actual provider
errors. Usage records increased 391 to 399, with the same daily policy and no
resets/refunds. A preliminary harness invocation failed before reservation or a
provider call because saved generation_options must be supplied separately; it
has its own zero-call preflight row. The local wrapper removes that operator field
and re-supplies the identical recorded settings, including the 48,000-character
cap the harness CLI otherwise omits.

Each provider attempt has one ledger row, with source session/call, condition and
payload hash. Session suffixes (all prefixed `planner-replay:`):

| Saved point | Control | Proposed contract |
| --- | --- | --- |
| C-stop | `e9dd2719-0371-4711-b31e-cf2482a6b03c` | `0f068d06-1778-4502-81e8-f6f884da498d` |
| D-stop | `b93219b8-1397-4277-8747-1e20c934d556` | `4ea84ade-691b-45e5-94be-e07b47411163` |
| F-before-10 | `d5afe450-de9c-4fef-ac4c-b13cfaf94573` | `9a72f6c5-0909-46c7-bafb-94ba533e085a` |
| F-before-11 | `68d155e0-a61f-4c79-a1be-f78343530f73` | `c76e728d-f1dd-45b6-8a5f-d6eb68213d86` |

Local reproducibility artifacts:
`.local/compare-stopping-contract-20260923.py` uses `replay_planner.py` for each
metered next action, overriding only in-memory experimental instructions/schema
and evaluator validation of the two added fields. Existing reference/intent
validation runs unchanged after removing those experimental fields from a copy.
`.local/stopping-contract-comparison-20260923-v2/` retains the exact manifest,
payloads, eight outcomes, raw-proposal audit and generation settings. Tapes retain
request/response bytes. The initial preflight failure remains in the unsuffixed
directory. Production engine fingerprint remains
`049c33cb55b85ecd6324d623fdf6e3acc6c83815dbc19fca1a60738c50768531`.

## Review decision: rejected

The user rejected this stopping-criteria hypothesis after reviewing PR #218.
G escalated to source reads without this contract; the eight comparisons showed
no reliability gain, revised C regressed on intent consistency, and F still
proposed inadmissible queries. B/C/D stopping was plausibly appropriate for their
scoped requests. The proposed fields and instruction addition below are retained
only as a negative experimental result. They are not adopted and must not be
carried into other work. The implementation now targets compiler correctness
and physical binding context/feedback instead.

## Historical review boundary

No stopping-contract runtime change, compiler fix, freeze or publication is made.
The proposed contract and failed/partial evaluation are ready for review. Separate
follow-ups to consider are the repeated-literal compiler defect and actionable
connection-qualified object/complexity feedback; they must not silently rewrite
queries, change scope or bypass permission. F-paced and baseline F remain failed.
The two required generator tests passed; documentation/ledger checks are recorded
in the current delivery status. No full regression or browser suite was rerun for
this documentation-only milestone.

### Exact experimental instruction addition

This was appended to the existing instructions only inside the comparison process.
The only schema additions were the two support fields described above.

```text
Experimental completion contract for this next-action evaluation:
Before STOP, evaluate the actual ticket request, not only whether a number was reproduced.
Extend support with completion_basis and completion_reason. Keep all existing support fields.
completion_basis is SUFFICIENT_EVIDENCE, BUSINESS_CONTEXT, BUDGET, CAPABILITY, SCOPE,
PERMISSION or ELIGIBILITY. completion_reason is at most 1000 characters and must explain
what requested question the evidence resolves, what material part remains unanswered,
and why the best remaining discriminating test in remaining_test is unnecessary or unavailable.
Reproducing a presentation-layer value establishes WHAT, not a causal WHY. A cause,
defect, source/application issue, freshness issue or expected-behavior assertion needs
evidence that distinguishes its mechanism from a plausible alternative, or an explicit
claim-scoped explanation of why further evidence is not needed or cannot be obtained.
Do not claim that matching numbers alone distinguish a cause. Preserve limits on any claim
when evidence is unavailable. Missing business intent does not by itself make a useful,
admitted technical test unavailable; separate the unknown rule from testable implementation.
SUFFICIENT_EVIDENCE can be entirely native/DAX evidence when it resolves the scoped request;
state the observed contrast and why further tests would not affect that limited answer.
BUSINESS_CONTEXT permits honest uncertainty when the essential missing fact is intent;
do not invent it. Other bases must name the actual remaining budget or capability/scope/
permission/eligibility restriction from this context, not a hypothetical blocker.
Do not force a query, a layer order, SQL, a fixed read count or a broad investigation beyond
the ticket. Choose another admitted action only when it can materially distinguish the
remaining explanation. This is a concise evidence and task-coverage summary, not private reasoning.
```
