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

## Second batch, 2026-09-27 03:38 UTC: stopped at the discovery-policy check

The first batch above is kept as written. After the account holder's MFA
sign-in restored the model key, a fresh batch ran under the same conditions at
`main` `24a23be`, engine `unfrozen-a9e32c819240`.
**All three runs failed before any investigation read.**

| Run | Started (UTC) | Wall | Exit | Intake model calls | Planner calls | Reads | Reference cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | 03:38:27 | 10.7 s | 1 | 1 (recorded) | 0 | 0 | $0.035 |
| R2 | 03:39:44 | 7.4 s | 1 | 1 (recorded) | 0 | 0 | $0.005 |
| R3 | 03:40:57 | 7.6 s | 1 | 1 (recorded) | 0 | 0 | $0.005 |

### What stopped them

Each run completed intake (one recorded model call), then failed at preview:
`adaptive_candidates.catalog` raised `Conflict: Dynamic investigation needs
current approved discovery policy`.

**The cause is this session's own configuration changes.**
- **What discovery pins:** the approved discovery for the model records
  `policy_hash` `1f1616d4…`. That is the digest of the **whole** config file at
  discovery time.
- **Exactly the old config:** it equals the digest of the config **before**
  `fabric.sql_reader` was added (2026-09-26, item 2a).
- **What changed it:** the config has since gained `fabric.sql_reader` and
  `fabric.xmla_client`, and now digests to `19e2ef0b…`.
- **The effect:** from the moment `fabric.sql_reader` was added, every
  catalog-mediated investigation in this environment was refused. The engine
  correctly treats the discovery approval as stale.
- **Why it went unnoticed:** the later transport and verification checks (#248,
  #250) called the adapter directly and bypassed the catalog gate.

The before and after config hashes were recorded for each change, but the
effect on discovery approval was not checked. That was a mistake.

### Per-run report requested

The same for all three runs:
- **Execution surfaces and attestation:** none; no probe ran.
- **Boundaries compared or skipped:** none.
- **Genuine cross-surface comparison:** none.
- **Verified comparisons vs within-layer checks:** 0 and 0.
- **Reads:** 0 of any type.
- **Investigation planner calls:** 0; only the intake model call ran.
- **Synthesis:** none.
- **Outcome:** no outcome and no claim.

Usage for the day went from 0 to 3 planner-kind reservations: the three intake
calls, 127,437 input characters in total, 4,500 output tokens reserved. Cloud
reads are unchanged at 4.

### Grading

The runner's ledger rows `G-item3b-R1/R2/R3-20260927` are kept as written, with
`graded: PENDING_TRUTH_REVIEW`. This document grades them
`INFRASTRUCTURE_FAILURE`: the discovery-policy approval was invalidated by
configuration changes.

### Options (a decision for the account holder, none taken)

1. **Re-approve discovery under the current config.** This re-runs discovery for
   `unknown-domain-v4` with the metadata identity. It makes cloud metadata
   reads, and it creates a new current context. It keeps the independent-read
   configuration in place.
2. **Narrow the policy hash (engine change).** Make the discovery policy digest
   cover only the configuration that affects discovery, so adding a reader or
   transport section does not invalidate approval. This needs its own PR and
   argument, because it changes what "approved discovery" certifies.
3. **Not recommended: revert `fabric.sql_reader` and `fabric.xmla_client`.**
   This would restore the pinned digest, but it would disable the independent
   lower read, so the runs could not test the acceptance bar.
