# Provider capacity report

Historical report below. The user subsequently authorized this exact capacity
change, now applied and read back. Follow [baseline evidence](known-domain-baseline.md)
for current capacity and the required known-domain gate before any freeze.

2026-09-23. Ordered reliability item 8, issue #199. **Report only: no capacity,
permission, SQL/free-tier setting, deployment model or live-run change applied.**

## Verified current allocation

Read-only Azure control-plane inspection of `aoai-investigator-9696025` in
`rg-investigator-dev`, East US 2, returned:

| Setting | Observed | Proposed after operator approval |
| --- | --- | --- |
| Deployment | investigator-quality-54 | Same deployment |
| Model/version | gpt-5.4 / 2026-03-05 | Unchanged |
| SKU | GlobalStandard | Unchanged |
| Capacity units | 10 | 100 |
| Token limit | 10,000 per 60 seconds | 100,000 TPM |
| Request limit | 100 per 60 seconds | Expected 1,000 RPM; verify after change |
| Evaluation concurrency | No trial run in this milestone | One request in flight |
| Start-to-start pacing | Not exercised | At least 65 seconds across intake and planner calls |

The regional `OpenAI.GlobalStandard.gpt-5.4` quota reports 10 units allocated out
of 1,000. The proposed additional 90 units fit that reported allocation; no other
model needs capacity removed. This does not guarantee deployment-update success
or availability at a later time. Re-read allocation before applying the change.
The default mini deployment and the separate GPT-4.1 deployment stay unchanged.

The retained whitelisted receipt is `.local/provider-capacity-20260923.json`;
the reviewable proposal is `.local/provider-capacity-proposal.json`. Neither
contains credentials. Current reasoning-profile hash:
`54add2f373fdf936bd4f86060cf771cb13ab87e66c95936574c3fbccd40c78c4`.

## Why this allocation

An earlier source-ready replay recorded 14,560 input tokens; the quality profile
allows 8,000 output tokens. Their sum, 22,560, is a sizing reference already above
the current 10,000 TPM allocation. It is not the exact Azure admission estimate.
The 48,000-character payload limit also excludes some wire instructions/schema
overhead. Longer output allowance fixed one observed output-limit failure; cutting
it simply to fit quota would trade capacity failure for a previously observed
response-completion failure. See [provider evidence](provider-response-reliability.md).

Microsoft explains that rate limiting estimates input plus maximum output allowance,
with character-based estimation that can differ from billed tokens. RPM is coupled
to model-specific capacity, and short-window bursts can throttle below a nominal
minute total. [Microsoft quota guidance](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/quota).

The proposed 100,000 TPM and 65-second serial pacing are a conservative starting
allocation, **not a measured throughput guarantee**. Pacing alone cannot make an
oversized individual request fit 10,000 TPM. Conversely, a larger allocation does
not fix context loss, bad test selection, unsupported queries or weak conclusions.
Keep the current medium reasoning, 48,000 input-character cap, 8,000 output-token
cap and 120-second timeout for a controlled comparison. Preserve bounded calls,
existing daily reservations and the 1,800-second investigation ceiling. Pacing
consumes wall time; it must not become an unmetered retry or deadline extension.

## Concrete operator change and evidence contract

After approval, change only `investigator-quality-54` GlobalStandard capacity from
10 to 100. Preserve its model/version and re-read actual `rateLimits`. Update the
capacity metadata in `infra/llm/quality-gpt54.json` and
`infra/llm/quality-gpt54-reasoning.json` to match the approved allocation; do not
change the mini default. No update was executed for this report.

The existing evaluator accepts `--minimum-llm-interval 65`; use one evaluation
worker and no overlapping trials on this deployment. Do not enable hidden SDK
retries. For **each later trial**, append the following numeric provenance beside
its existing `settings_hash` in the ledger and retain it with the run artifact:

- `provider_capacity_units`, `provider_tpm`, `provider_rpm`
- `provider_capacity_verified_utc`, `minimum_llm_interval_seconds`
- `max_inflight_requests`, and the observed deployment/model version

Use re-read values, not this proposal's expected limits. Include the capacity and
pacing manifest with the frozen operator settings, preserving prior usage. The
current report row distinguishes observed 10,000/100 limits from proposed limits.
Historical ledger rows are untouched; missing historical capacity is not guessed.

## Delivery state and remaining gate

Items 5, 6 and 7 merged as PRs #213, #214 and #215, each with six green checks.
Item 7 passed 1,003 local regression tests. This item adds only the capacity report
and status records. No new investigator engine bytes, live inference, SQL/DAX
read, recorded live tape, freeze or unfamiliar variant was introduced.

**The operator report is ready; the capacity change and item-8 empirical gate are
pending.** After approval/application and all ordered PRs are merged, preserve the
usage ledger, prepare the single fresh freeze/variant and obtain the required
variant-specific reader grants. The nine-family matrix must then record zero
RateLimitError at the chosen pacing to pass the capacity gate. Investigation
correctness and frozen unfamiliar-domain acceptance are separate gates and remain
unproven. F-paced stays FAILED; it was neither rerun nor relabelled.

Report validation: the two required generator tests passed in 0.878 seconds.
The control-plane ledger row contains no inferred execution duration (its zero
wall value is unmeasured), no model-call reservation and no applied change.
Documentation link/secret checks and CI are required before merge. Minor separator
encoding errors introduced in recent milestone prose are corrected without
changing historical results.

Final document audit resolved 190 local links and verified 84 unique ledger IDs,
all note paths, and byte-for-line preservation of the pre-existing ledger lines.
The full README was reviewed. Final secret scanning and PR CI track delivery of
this report; the operator change and live empirical gates remain pending.
