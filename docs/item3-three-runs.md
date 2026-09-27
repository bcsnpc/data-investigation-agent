# Item 3: three runs, 2026-09-27

Updated 2026-09-27. **All three runs failed before intake.** No investigation
ran, so the acceptance bar was not tested. It was neither met nor failed on
evidence. These are **infrastructure failures**.

## Conditions (the same as prior batches, set before the first run)

- **Code:** commit `a63bfa5`, engine `unfrozen-a9e32c819240` (the new
  fingerprint, which covers adapters and transports).
- **Inputs:** environment `unknown-domain-v4`, config SHA-256 `4362a6c7…`, G
  ticket (SHA-256 `e22ce27f…`), planner profile `quality-gpt54-reasoning`.
- **Mode:** known-domain regression, reviewed scope executed, synthesis on,
  planner recording on.
- **Limits:** read limit 6, input limit 384,000 characters, minimum model
  interval 65 s.
- **Runner:** `.local/item3-three-runs-20260927/run-three.py`, which is not
  committed. It asserts the commit, fingerprint, config and usage policy before
  each run.

## What happened

| Run | Started (UTC) | Wall | Exit | Session | Reads | Planner calls | Recordings |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | 02:51:46 | 2.8 s | 1 | none | 0 | 0 | 0 |
| R2 | 02:52:54 | 2.2 s | 1 | none | 0 | 0 | 0 |
| R3 | 02:54:01 | 1.8 s | 1 | none | 0 | 0 | 0 |

Each run stopped inside `run_ticket.py`, in `local_azure_key()`. That step
fetches the Azure OpenAI key with
`az cognitiveservices account keys list --subscription d5dd7d65…` through
Azure CLI's **default** profile, and the `az` command failed.

**The cause, confirmed afterwards with a read-only check:**
- The default profile holds the account that owns subscription `d5dd7d65…`, so
  it is the intended account.
- A token request for that subscription returns **`AADSTS50076`**: multi-factor
  authentication is required ("due to a configuration change made by your
  administrator …").
- The profile needs an interactive `az login` with MFA. That was not attempted:
  it is interactive, and it belongs to the account holder.

Usage was unchanged (4 cloud reservations for the day before and after; 0
planner calls). No model call, data read, probe or synthesis occurred.

## Per-run report requested

The same for all three runs, because none reached intake:
- **Execution surfaces and attestation:** none; no probe ran.
- **Boundaries compared or skipped:** none.
- **Genuine cross-surface comparison:** none.
- **Verified comparisons vs within-layer checks:** 0 and 0.
- **Reads by type and surface:** 0 SQL, 0 DAX, 0 Fabric SQL.
- **Investigation planner calls:** 0.
- **Synthesis:** not requested (the run never reached that step), so not
  validated.
- **Outcome and limits:** no outcome and no claim.

## Grading

The three ledger rows (`G-item3-R1/R2/R3-20260927`) were appended by the runner
as written, with its default `graded: PENDING_TRUTH_REVIEW` and
`stop_reason: PROCESS_FAILED`. They are left unchanged, as recorded run
evidence. **This document grades them `INFRASTRUCTURE_FAILURE`:** failure to
obtain the model provider key, caused by MFA enforcement (`AADSTS50076`) on the key-owning Azure CLI profile.

## What is needed

- **Sign-in:** the account holder signs in to Azure CLI's default profile
  interactively, with MFA:
  `az login --tenant aeb4d0a9-e637-4a7e-8efc-63cf0c3827df --scope https://management.core.windows.net//.default`,
  using `.local/azure-cli-env`.
- **Then:** a fresh, separately authorised three-run batch under the same
  conditions. These three failures do not count toward it and are not
  reinterpreted as product evidence.
