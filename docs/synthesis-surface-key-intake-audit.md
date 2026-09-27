# Synthesis surface key and intake nondeterminism audit

2026-09-27 UTC. Tracking: #193. Known-domain regression; no acceptance claim.

## Publication and scope

Documentation commit `7fea46fd2614428bdbad423d775f27b0d3f17b39` is preserved
unchanged on remote branch `records/discovery-reapproval-three` and in
[PR #254](https://github.com/bcsnpc/data-investigation-agent/pull/254).
[PR #253](https://github.com/bcsnpc/data-investigation-agent/pull/253) merged as
`76a5b2f822ccf2816f89a6ebc21809eae2f52e76` after six successful checks.
Original runs, ledger rows and evidence remain unchanged.

The only engine change uses the process debugger's existing `_surface_key` in
synthesis: engine, connection and object determine equality. Identity remains
in the returned evidence. A regression checks identical triples with matching,
differing and absent identities are all refused as cross-surface comparisons;
changing each triple member permits distinct surfaces and retains identity.
Missing or malformed required triple fields still fail validation.

## Requested R2 scenario rerun

One new attempt, `G-surface-key-R2-repeat-20260927`, used the same ticket, catalog,
config, profile and limits, with recording and synthesis enabled. Engine commit
`f23d169`, fingerprint `6c845e2eb1590e4c5f098a472886c8571b979e67686f92cbac3c276eb12629d1`.
It was **HELD at intake** for `MISMATCH_COMPLAINT` + `NONE`. No investigation
session was created; no probes, comparisons, investigation planner calls or
synthesis calls occurred. Synthesis did not complete. No automatic retry or
forced scope followed. One new ledger row preserves the failed attempt.

The recorded intake request was byte-identical to all three original requests.
The attempt took 8.584 seconds. Daily reservations increased by one intake call,
42,479 input characters and 1,500 output tokens; cloud reservations stayed at 7.
All reservations are settled. No settings, permissions, deadlines or budgets changed.
The configured 8,000-output/medium-reasoning investigation profile does not apply
to intake: its actual request still used 1,500 output tokens and the provider
reported reasoning effort `none`.

Separately, an **offline** replay of saved R2 through the changed digest cleared
`Process execution surface differs` and exposed the next rejection:
`Process comparison differs from referenced observations`. The process adapter
compares normalized scalar quantities; synthesis instead hashes raw rows.
The native receipt column is `[baseline]`; the SQL receipt column is `quantity`.
Normalized quantities agree, while the raw rows differ. This is a further
representation mismatch, not evidence of a numerical discrepancy. It is recorded
without altering the original session, receipts or comparison, and without
changing that second validator. A successful live synthesis remains unproven.

## Original R1/R2/R3 intake recordings

All three tape manifests and file hashes verified. Their provider request bodies
are **byte-for-byte identical**, 38,020 bytes, SHA-256
`715a29b4cdcf2223e42ccbf4a96792407b03743a248b6510fa4a7957872d58d4`.
Instructions, ticket, catalog/context versions, model/measure handles, function
schema and generation settings therefore did not change. The input JSON string
has 28,658 characters. Local recording IDs/timestamps differ outside that body.

| Field | R1 | R2 | R3 |
| --- | --- | --- | --- |
| Action | PROPOSE | PROPOSE | PROPOSE |
| Model / measure handles | m2 / m2v3 | m2 / m2v3 | m2 / m2v3 |
| Ticket shape | MISMATCH_COMPLAINT | MISMATCH_COMPLAINT | MISMATCH_COMPLAINT |
| Comparison mode | NONE | VERTICAL | NONE |
| Metric quote | Handled Quantity may include incorrect source entries | Handled Quantity | Handled Quantity |
| Filters / dimensions | empty / empty | empty / empty | empty / empty |
| Strict wire schema | valid | valid | valid |
| Application validation | incompatible pairing | valid | incompatible pairing |
| Input tokens | 13,621 | 13,621 | 13,621 |
| Cached input tokens | 2,176 | 13,440 | 13,440 |
| Output tokens | 71 | 67 | 66 |

All responses completed, with no provider error, truncation or content-filter
block. Other response differences are generated IDs/timestamps, usage and
completion filter offsets corresponding to different output lengths. The provider
reported the same deployment, temperature 1.0, top_p 0.98 and reasoning `none`
(zero reasoning tokens). The request did not explicitly select those sampling or
reasoning settings. Cache differences are recorded; these data do not establish
that caching caused the decision difference.

The request's strict schema declares `ticket_shape` and `comparison_mode` as
independent enums. It contains no constraint linking them. Offline JSON Schema
validation accepts **all three** responses. Application validation independently
reproduces R1/R3's `Comparison mode conflicts with ticket shape` and accepts R2.
Both metric quotes are verbatim and valid; they do not cause the refusals.

The prompt says VERTICAL is for one presentation measure versus its path,
HORIZONTAL for explicitly compared reports/measures, and NONE for a business
question. It permits source-discrepancy investigation from the named metric and
says missing business rules are not automatically an intake ambiguity.

**Finding:** inconsistent adherence to a cross-field instruction that the wire
schema does not enforce. The model satisfied the same schema on every call;
it did not satisfy the application contract consistently. All three agreed this
was a mismatch complaint, so the observed disagreement is routing mode, not
model/metric selection or reported uncertainty about ticket shape. The validator
matches the stated routing contract; this evidence does not justify weakening it.
Prompt wording may influence reliability, but these three responses cannot
identify the model's internal reason or prove a specific prompt revision would
solve it. This is not a changing-input, discovery-policy or provider-failure issue.
No intake implementation, schema, prompt or setting was changed. Audit stops here.

## Validation and artifacts

18 synthesis tests and two generator tests passed. Full regression result is
recorded in the PR and current status after completion. No investigation planner
payload is shaped by this change: directory and SQL-object coverage are unchanged.
The live intake request hash also verifies unchanged intake context. Synthesis
retains its existing surface evidence; this change only admits identity-bearing
surfaces and keys equality by the shared triple.

- [Rerun ledger summary](runs/synthesis-surface-key-retest.json).
- [Machine-readable audit, settings and offline diagnosis](runs/synthesis-surface-key-intake-audit.json).
- [Original three-run report](discovery-reapproval-three.md).
- Original local tapes and new tape remain under `.local/planner-recordings/`;
  IDs appear in the machine-readable reports. Raw provider bodies remain local.
- New local manifest, log and diagnostics: `.local/synthesis-surface-key-20260927/`.
