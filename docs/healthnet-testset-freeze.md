# HealthNet test-set engine freeze

Recorded 2026-11-26T19:16:01.460221+00:00, before test authoring or new estate reads.

- Commit: `9fb0190b11a5e2a83579de4ed5bdb58c5ac73300`.
- Engine/runtime SHA-256: `2a70673c449cc9a4abaf767f3c80cbdf105c32558a44a2483a6953320d4d2c39` (833 files).
- Prompt-bearing source SHA-256: `46fa11ec2c4205f23ba3788f3c874147637db45064ba526ae73143818119b5a2` (69 files).

Hashes cover the canonical sorted JSON list of `path`, byte length and file SHA-256
(sort_keys=True, compact separators). Engine scope: tracked non-test Python/JSON/
PowerShell/web source under scripts/, apps/investigator-workspace/, infra/scripts/
and infra/cloud-worker/, plus acceptance/model_steps/intake-resolution-policy.json.
Prompt scope is the complete engine files containing `prompt`, `system_message` or
`instructions` (case-insensitive), including embedded prompts; no prompt fragments
are omitted within those files. The complete member list is local at
`.local/healthnet-authoring/engine-freeze-members.json`.

Owner approved this session to author the HealthNet test set, read the estate as
owner (including waking its separate free-offer SQL databases), define reversible
faults without injecting them, and create only the `healthnet-answers-key` Key Vault
secret. No DIA access grant, DIA execution, engine change, merge or tag is authorized.
The author/operator sees the answers: this set is **owner-authored, not operator-blind**.
Future scoring must disclose that exposure and use independent grading. Fault
expectations are conditional on fresh injection admission; an uninjected case cannot
be scored against a fault outcome.
