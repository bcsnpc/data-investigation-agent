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

## Post-authoring verification

All 833 engine/runtime files and all 69 prompt-bearing files still match the
pre-authoring hashes. No engine, model prompt or runtime rule was changed.
The requested CLAUDE.md authoring constraint is the sole new operating instruction.
See healthnet-testset-verification.json. At this historical checkpoint owner/reviewer approval was pending; the final
APPROVED_SEALED approval below supersedes that status.

Revision 2 reviewer changes, 2026-11-26: test inputs, encrypted expectations and
review material only. All833 runtime and69 prompt-bearing files still match the
original freeze. Static definition defects remain plans only, never live changes.
See the revised hash manifest and healthnet-testset-verification.json.

## APPROVED_SEALED - 2026-11-26 (revision 3, final)

Owner confirmed reviewer approval on 2026-11-26, subject to the final HN-005 and
HN-020 wording edits and dollar-spacing corrections. Those edits are applied; the
HN-005 form comparison uses the same neutral payment-app wording. All 27 expected
answer records are unchanged from revision 2, verified by decrypt-and-compare.
AES-256-GCM re-encryption uses the existing pinned Key Vault key version, a fresh
nonce and authenticated final ticket hash. The key was used only in memory.

Final SHA-256 hashes:

- `tests/tickets/healthnet/tickets.json`: `29480e4fd567c27a08f89f7a1aeb49407b3899bf81aa14f30164af2e254dcfbf`.
- `tests/tickets/healthnet/expected-answers.enc.json`: `60812b96949df8f9a0ac9e246279f5a0778da04d088e791aa3c6053288f92a52`.
- `tests/tickets/healthnet/screens/hn-026-revenue-baseline.png`: `3d590a4b1814b372562bb05ca15494f1f8a231f37468b3642f1af97684ccee9e`.
- `tests/tickets/healthnet/screens/hn-027-productivity-baseline.png`: `d46ccb8a1327a8e7d324477dce69a7826cf56b9dfcee11317936f33758887869`.

All 833 engine/runtime files and 69 prompt-bearing files match the original freeze.
The existing CLAUDE.md engine freeze rule remains in force. The set is owner-authored,
reviewed and sealed before any DIA run; the author/operator has seen the answers
and future scoring must disclose that exposure and use independent grading.
No DIA runs, model calls, access grants or injections were performed.

After authenticating the final seal, both the active local plaintext review packet
and its superseded revision-1 copy were deleted. Local ticket and screenshot inputs
remain uncommitted; only encrypted answers, hashes and documentation are pushed.
Earlier pending-approval statements are historical and superseded by this final seal.


## Later authorized smoke-plumbing exceptions ? 2026-11-26

The authoring seal above is unchanged. The owner subsequently authorized generic
config/connector/gateway smoke plumbing only. Of the833 frozen engine/runtime
files, exactly3 differ: scripts/investigator/adapters/estate_config_schema.py,
scripts/investigator/estate_config.py (disabled SMOKE_ONLY/READY_SEALED_TEST
states), and scripts/managed_sql_worker.py (literal SELECT1 connectivity reads,
with existing gateway and read-only controls). The other830 engine files and
all69 prompt-bearing files retain their original hashes. No HealthNet-specific
intake, reasoning, verdict or prompt change. Generic config/worker regressions,
full suite,8image shards and123unchanged replay classifications are recorded in
docs/healthnet-smoke.md. The engine-freeze rule still applies.

Owner access decisions changed only approved estate permissions: source reader
roles, Viewer/Build and the HealthNet-only unfiltered Investigator RLS role/group
experiment. No test injection or DIA/AI run was made. This is an access smoke,
not a scored HealthNet run. No sealed ticket/answer body was read in the task;
no ticket, answer, seal or expectation was changed. Author/operator exposure
from test authorship remains disclosed; future grading must remain independent.


2026-11-26 owner-authorized connector exception: default REST remains unchanged; HealthNet native bundle selects read-only gateway XMLA for the three verified models. Only transport/configuration and synthetic practice-fixture tests changed, not reasoning/prompts/expectations. One trivial actual-engine-port DAX read passed, with no ticket or AI run. Approved sealed files remain unchanged. See docs/healthnet-engine-dax.md.


2026-11-26 Linux extension complete
Only the generic pinned ADOMD 19.117.0 .NET 8 reader, native transport and image packaging changed. The actual Azure engine port passed the trivial read and the execution Succeeded; no HealthNet ticket or AI call ran. The build-context file changed solely to admit the two native client source files; no prompt text or HealthNet-specific reasoning changed. The other 68 prompt-bearing file hashes and all approved sealed test files remain unchanged. See docs/healthnet-engine-dax.md and its evidence JSON.
