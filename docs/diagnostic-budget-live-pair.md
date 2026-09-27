# Diagnostic budget: two live divergence repeats

2026-09-27. #281 merged after all six checks passed, as
`a5fb6b0c674e6e664923c7acbed9b141eecd3a48`. Both runs used this merged engine,
fingerprint `096482dcb8ad2062e2073774bd9aa2e989f2df9579cf9ff388f651f904c11fe4`.
No engine, config, permission, estate, diagnostic-cap or ordinary-allowance change
occurred during this batch. These are KNOWN_DOMAIN_REGRESSION runs only.

**Both investigations completed; neither completed end to end.** The accounting
fix removed the earlier cap hold. Both reached two boundary comparisons and the
definition judge, but both synthesis calls failed ValidationError. Failed synthesis
is preserved; no retry or behavior change was made to obtain a pass.

## Matched conditions and results

Same saved G ticket and resolved scope as the preceding pair; GPT-5.4 medium,
8,000 output tokens, 384,000 cumulative input characters, 65-second call pacing,
three-boundary ceiling, recording and synthesis enabled. Diagnostic cap remains
four; ordinary physical allowance remains 60 per rolling 24 hours.

| Run | Session | Diagnostics / cap | Physical / batch credits | Guards | Reuses | Procedure | Synthesis |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | `79735d7d-e7cb-4496-8f33-6b6b33cf1d4a` | 4 / 4 | 10 / 10 | 6 | 0 | COMPLETED | FAILED |
| R2 | `43977d8e-aad4-435b-ae5f-f0ee1ca2c071` | 4 / 4 | 10 / 10 | 6 | 0 | COMPLETED | FAILED |

All ten requests completed in each run. There was no read-cap refusal. Neither
limit had remaining capacity for another request/diagnostic, but no additional
read was attempted. Each run used one intake call, one investigation definition-
judge call and one synthesis call. The process stop was ENOUGH_DIAGNOSTICS and the
procedure assessment TRANSFORMATION_LOGIC. This is not a validated final synthesis.

The exact physical sequence in both runs was:

1. Power BI DAX quantity.
2. Gold SQL identity self-report.
3. Gold database permission check.
4. Gold object permission check.
5. Gold SQL quantity.
6. Fabric endpoint metadata lookup.
7. Silver SQL identity self-report.
8. Silver database permission check.
9. Silver object permission check.
10. Silver SQL quantity.

The four diagnostic operations were DAX quantity, Gold quantity, endpoint lookup
and Silver quantity. SQL physical count is eight, of which six are guards; one
DAX and one metadata request bring the total to ten.

**Guard reuse saved zero requests against the ten-request estimate.** The SQL
reads use different database/object scopes (`warehouse_gold_e1b8e1` and
`warehouse_silver_e1b8e1`). Each needed its own database and object checks; each
new connection still self-reported identity. Each run contains four ESTABLISHED
guard events and no REUSED event. The cache's same-scope reuse remains established
by offline tests, not exercised by this pair. The cap accounting change, rather
than a physical-request saving, allowed the procedure to proceed.

## Comparisons and claim limits

Each run compared presentation to Gold (8,765 = 8,765), then Gold to Silver
(8,765 versus 7,661). Both comparison receipts say CROSS_SURFACE_VERIFIED,
meaning independently attested execution surfaces, not aligned snapshots.
Both also say SNAPSHOT_UNVERIFIED. Agreement does not establish currency;
different update timing was not excluded as a cause of the divergence.

Both judges found the declared matching of movements to rates compatible with
row multiplication. This does not establish actual duplicate matches, intended
grain, source correctness or business intent. Silver-to-Bronze was not checked
because the procedure terminated; Bronze-to-application remains unresolved.
Refresh timestamps were unavailable to the reader. Seven surface fields remain
unattested across the three quantity probes: DAX connection/engine/object, and
SQL connection/engine for each of the two SQL surfaces. These limits remain in
the retained assessment; the failed synthesis did not produce final outputs.

## Credits, usage and expiry

The user approved ten expiring physical-request credits per run, twenty total,
for this batch only. Both immutable grants were recorded before investigation,
with before/granted/after control-plane readbacks. No restoration was needed.

| Batch | Granted | Charged | Unused | Expires UTC |
| --- | --- | --- | --- | --- |
| `G-diagnostic-budget-R1-20260927-credits` | 10 | 10 | 0 | 2026-09-27T23:08:19.180873+00:00 |
| `G-diagnostic-budget-R2-20260927-credits` | 10 | 10 | 0 | 2026-09-27T23:10:48.476794+00:00 |

Total: **20 granted, 20 charged, zero unused**. Exhausted grants expire at the
recorded times; nothing was refunded or transferred. The ordinary allowance stayed
60, with 92 still-recent historical reservations and zero ordinary availability
before and after both runs. All twenty new requests consumed batch credits.
UTC-day historical totals moved 89 -> 99 -> 109; these are counters, not a raised
ceiling. Policy/config/profile/ticket hashes match before and after. The earlier
pair's remaining credits stayed tied to those earlier sessions and were not used.

## Synthesis failure and verbatim drafts

Both sealed synthesis records say FAILED / ValidationError. Read-only validation
of each recorded provider response against its own recorded request schema finds
five enum violations at `limitations[1..5].text`. The provider reports completed,
not output truncation. No engine or validation rule was changed. This inspection
is of saved JSON, not a new live call or a replayed investigation.

No validated business or technical output was published. The following are the
exact proposed `text` fields from each recorded synthesis response, **rejected
drafts**, not a successful rendered explanation. Consequently they do not include
the deterministic additions that successful assembly would append.

### R1: rejected proposal

Recording: `c8c04c61-a17a-477e-96e1-dd4c8c933835`.

Business draft, verbatim:

> The report showed 8,765 for movements, matching the total used to prepare it. An earlier check of movements returned 7,661; the difference appears in the step that matches movements with rates. Several matching rates can cause an entry to contribute more than once. We have not confirmed the repeated matches, whether the checks describe the same moment, whether this matching rule is intended, or how movements were first entered. Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.

Technical draft, verbatim:

> The procedure recorded 2 independently compared boundaries. The fixed boundary account states input-to-output ordering and observed quantities. Several matching rates can cause an entry to contribute more than once. A compatible definition does not prove actual repeated matches, source correctness or business intent.

### R2: rejected proposal

Recording: `3bb20bae-67ea-4814-86dc-1e11d167b184`.

Business draft, verbatim:

> The report showed 8,765 for movements, matching the total used to prepare it. An earlier check of movements returned 7,661; the difference appears in the step that matches movements with rates. Several matching rates can cause an entry to contribute more than once. We have not confirmed the repeated matches, whether the checks describe the same moment, whether this matching rule is intended, or how movements were first entered. Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.

Technical draft, verbatim:

> The procedure recorded 2 independently compared boundaries. The fixed boundary account states input-to-output ordering and observed quantities. Several matching rates can cause an entry to contribute more than once. A compatible definition does not prove actual repeated matches, source correctness or business intent.

Both draft text pairs are byte-identical; citations and proposed limitation text
vary. Full provider responses and original run artifacts remain unchanged under
`.local/diagnostic-budget-live-20260927/` and their referenced planner recordings.
One ledger row was appended per run, including the failed synthesis status.
[Public accounting receipt](runs/diagnostic-budget-live-pair.json) records counts,
guard references, approvals and expiries without provider prose or query values.

Validation for this evidence-only change: required generator tests passed (two).
No engine tests or browser/cloud probes were added beyond the two requested runs.
