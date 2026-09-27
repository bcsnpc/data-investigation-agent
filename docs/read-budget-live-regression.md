# Physical-read budget: two live divergence regressions

2026-09-27. PR #279 merged as `5bffe397d36707abbd81ca0a49411e5d42b62a9e`
after all six checks passed. Both runs used that merged engine, fingerprint
`988034c43bbf77e76d3afea404f84285871f1b31459b840fc799fb83da98a319`.
No engine, policy, config, cap, permission or estate change during the batch.

**Neither run completed.** The budget controls bound correctly, but the previously
successful divergence procedure no longer completes under its unchanged four-read
cap. This is a live regression result, not a passing investigation.

## Matched conditions

Same saved G ticket as the successful [vocabulary-form pair](vocabulary-form-live-and-latency-audit.md),
GPT-5.4 medium reasoning, 8,000 output tokens, 384,000 cumulative input characters,
65-second model pacing, three-boundary ceiling, recording and synthesis enabled.
The saved successful pair's **four-read cap** was kept exactly; the CLI's larger
default was not used. Both intakes proposed the same model, measure, filters and
dimensions. Each intake used one model call. These are KNOWN_DOMAIN_REGRESSION
runs, not a freeze or unfamiliar-domain acceptance attempt.

## Results

| Run | Session | Completed? | Physical reads / cap | Investigation planner calls | Synthesis |
| --- | --- | --- | --- | --- | --- |
| R1 | `a7d36799-fb4f-4b8c-a66e-b13012a9e7d9` | No: HELD | 4 / 4 | 0 | Not run |
| R2 | `1cfd52f2-b825-4e13-9737-9a78cfca3a68` | No: HELD | 4 / 4 | 0 | Not run |

Both runs executed the same four requests:

1. Power BI DAX quantity read: completed.
2. Fabric SQL identity/database self-report: available.
3. Fabric SQL database read-only permission check: available.
4. Fabric SQL object read-only permission check: available.

The next request, the Fabric SQL quantity query, was refused **before send**.
There were no endpoint-metadata reads and no SQL quantity values returned.
Both sealed logical SQL receipts are HELD with `error_type: UsageHold`:
`23bfba16-1cc0-4bc4-ba65-166a6e6ea4e0` and
`e391d202-1c9c-4077-af1a-c0bcc0a0dc12` respectively.
Each run's physical receipts retain all four successful requests and the nested
logical receipt for the held SQL probe. No charged request was erased or refunded.

The runtime stop reason is `TOOL_UNAVAILABLE`, with fallback classification
`UNRESOLVED`; the sealed receipt identifies the budget refusal more specifically.
There is no validated assessment, boundary comparison or definition judgment.
The runner's process exit code was zero for each recorded result; it must not be
interpreted as investigation success. The ledger labels them HELD/NOT_GRADED.

## Needed versus available

Each run had **four** per-run slots and needed **at least five** just to obtain
the first SQL quantity and attempt the presentation/source comparison. That fifth
slot is demonstrated by the actual refused request, not an estimate.

The previously completed path had one DAX read, two single-object Fabric SQL
probes and one endpoint lookup. Under current accounting that same request path
would require **ten physical reads** (1 + 4 + 4 + 1). Ten is a structural estimate
for those previously observed steps, **not a live demonstration that ten would
complete this engine's run**. Later steps and synthesis were not reached. The cap
was not changed, and neither run was retried to get a pass.

## Explicit expiring credits and usage

The user authorized Codex to grant this batch's needed credits. Two immutable
approvals were recorded before their respective sessions started investigation:

| Batch ID | Granted | Charged | Unused | Expiry (UTC) |
| --- | --- | --- | --- | --- |
| `G-physical-budget-R1-20260927-credits` | 10 | 4 | 6 | 2026-09-27 22:46:40 |
| `G-physical-budget-R2-20260927-credits` | 10 | 4 | 6 | 2026-09-27 22:48:46 |

Total: **20 granted, 8 charged, 12 unused**, expiring automatically. The ten credits
per run deliberately exceed its four-slot envelope so batch credits cannot mask
which limit binds. No credit increase or cap change occurred mid-run. There was
no mutation and no restoration operation; no restoration credits were needed.

Control-plane before/granted/after readbacks and approval files are retained in
`.local/read-budget-live-regression-20260927/`. UTC-day historical counters moved
81 -> 85 -> 89. The rolling ordinary balance remained **98 charged against 60**
throughout; it includes still-recent prior-day historical reservations. These runs
spent only their batch credits. No ordinary ceiling change, counter reset or
refund occurred. Policy/config/profile/ticket hashes match before and after.

## Outputs, verbatim availability

### R1

Business output: **not generated**. Technical output: **not generated**.
There is no synthesis output to quote; no substitute explanation was created.

Runner status, verbatim (this is not a business or technical explanation):

```json
{"intake": "PROPOSED", "question": null, "status": "HELD", "classification": "UNRESOLVED", "planner_calls": 0, "cloud_calls": 4}
```

### R2

Business output: **not generated**. Technical output: **not generated**.
There is no synthesis output to quote; no substitute explanation was created.

Runner status, verbatim:

```json
{"intake": "PROPOSED", "question": null, "status": "HELD", "classification": "UNRESOLVED", "planner_calls": 0, "cloud_calls": 4}
```

Both complete run artifacts, intake recordings, logs, approvals and control-plane
readbacks are retained locally. One ledger row was appended per run. Public
[accounting receipt](runs/read-budget-live-regression.json) contains counts and
identifiers, not business values or provider prose. No engine fix is included in
this documentation milestone; the next capacity/procedure decision belongs to
the user.
