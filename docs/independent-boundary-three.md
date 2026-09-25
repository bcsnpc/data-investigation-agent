# Independent-boundary three-run checkpoint

Updated 2026-09-25. This is a known-domain regression checkpoint on the
unfrozen engine at `c10131b`. It is not unfamiliar-domain acceptance.

PR #235 corrected the evidence invariant before this batch. Every process probe
now identifies its engine, connection and object. A boundary is verified only
when its two observations came from distinct execution surfaces. Same-model DAX
checks remain visible as definition checks and cannot produce
`CONSISTENT_TO_BOUNDARY`. Derived process observations can enter synthesis only
after their references, equality and surface identities validate.

The existing investigator reader was also probed for the discovered Gold SQL
analytics endpoint. Its configured MSAL client failed before connection with
`AADSTS65002`, because that client is not preauthorized for the
`database.windows.net` resource. No SQL connection or data query occurred, so
table permission was not established and no permission was changed. Independent
Gold execution remains unavailable through the current reader transport.

## Exactly three launched attempts

| Run | Session | Calls / reads | Surfaces / comparison | Synthesis | Result |
| --- | --- | --- | --- | --- | --- |
| R1 | None | 0 / 0 | None; boundary distinctness not evaluated | Not requested | Infrastructure failure before intake |
| R2 | None | 0 / 0 | None; boundary distinctness not evaluated | Not requested | Infrastructure failure before intake |
| R3 | None | 0 / 0 | None; boundary distinctness not evaluated | Not requested | Infrastructure failure before intake |

All three evaluator commands omitted the now-required `--environment` argument.
`run_ticket.py` rejected each command before opening a session. Usage remained
unchanged at 135 planner calls, 47 cloud reads, 4,082,965 input characters and
950,000 reserved output tokens, with all 182 records settled. The raw stderr,
manifest and summaries are preserved locally. Each failed attempt has one ledger
row marked `INFRASTRUCTURE_FAILURE` and `HARNESS_ARGUMENT_ERROR`.

The batch therefore says nothing about runtime execution surfaces, boundary
comparability, transformation judgment or synthesis. No fourth attempt was
launched because the instruction required exactly three runs followed by a stop.
The correct next action is a separately authorized batch whose immutable command
includes `--environment unknown-domain-v4`; it must not reinterpret these failures
as product evidence.

See the [machine-readable result](runs/independent-boundary-three.json), the
[requalified #234 report](correct-context-process-three.md#2026-09-25-correction-after-review-of-234),
and the [current delivery status](current-delivery-status.md).
