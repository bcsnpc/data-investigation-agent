# Cloud form demo: current admission requirements

This is an offline source and artifact audit, not a cloud execution or READY
claim. The implementation has no fixture ID, expected total, question answer or
outcome branch. The prepared form carries the original demo's submitted facts.

## Existing evidence and exact ticket

`scripts/fixtures/cloud-owner-demo-form.json` copies the questionnaire saved for
ticket `e573535d-041c-4cd9-bb7a-4f1c55b46046` in the isolated Round Fifteen
`owner-live-final/catalog.sqlite`. Only the request key changes to
`round-eighteen-cloud-family-a-1` for this single newly authorized attempt.
Report/page/visual, APPLICATION comparison, description and absent screenshot
are unchanged. The text asks about the current global Handled Quantity; it
does not supply or assert 7,661 or 8,765. Those are prior observed quantities,
not desired values injected into the new run.

The canonical `unknown-domain-v4` catalog imported into PostgreSQL has the
original fixture model `5b3eff46-631c-47b8-8211-049b5aa906ee` **disabled**, with
context `e1c6e5a0-fd5b-48e2-86bf-e4dae6e9e5ad`. Only billing is enabled in that
environment. The old owner-demo catalog is separate. An operator must publish
the specifically approved original model/context for the cloud demo; a worker
cannot enable it or choose an alternative model to obtain an answer.

`run_estate_investigation.py` uses the earlier text-only intake path. It does
not submit the saved questionnaire. `owner_demo.py` also retains its original
expired deadline and workstation storage preparation. Neither is silently
repurposed as the new cloud bootstrap.

## Operator sequence before the one attempt

1. Finalize the cloud manifest's fixed container paths, existing reader and
   model versioned Key Vault references, exact gateway policy and unchanged
   caps. Recompute the complete manifest/config hashes. No local DPAPI/CLI
   credential may substitute at execution. Definitions-only Contributor
   credentials cannot run diagnostic quantities.
2. Retain the approved metadata unchanged, recording its source context/hash;
   explicitly approve the new cloud configuration under the owner's migration
   decision. A manifest or authentication change is not covered by the old
   whole-config approval. Publish the selected model/context through the
   operator's shared-catalog path, not a worker-local enablement toggle.
3. Rebuild the six proof artifacts from their authoritative source receipts:
   discovery, discovery approval, transformation inventory, binding inventory,
   reader verification, publication. Keep original evidence immutable and use
   container-resolvable paths in new proofs. `assess_named_scope` verifies exact
   source fields, declaration conservation and all six stages; an index's
   supplied status is not authoritative.
4. Run only the necessary approved fresh verification controls. The preserved
   family-A named dependency scope has six transformation declarations,
   **18 binding proposals/verifications**, and one declared semantic/SQL route.
   The full binding set alone needs 36 value probes; the default three metadata
   slots produce a 39-probe bound under the approved 40 ceiling. The semantic
   DAX/SQL route needs its own accounted native witnesses. Guard/permission
   overhead still consumes physical requests from the shared pot. This is a
   sizing observation, not authorization to exceed any cap or omit a binding.
   A narrower scope must be genuinely compiled and conserved, not selected by
   dropping inconvenient witnesses.
5. Seal those controls and replay their captures offline. Publish a new proof
   only when the consumers validate it. Record partial attestation and
   SNAPSHOT_UNVERIFIED honestly. A role grant or HTTP 200 is not a value witness.
6. Build the pinned job artifact below. All readiness paths, including nested
   sources and publication captures, must resolve at their fixed container
   paths. An old certificate with Windows absolute paths is not portable just
   because its JSON file was uploaded. Changing all its pin fields is not
   evidence revalidation.
7. Start one worker. Any HELD/CLARIFYING result remains a result; the worker
   neither invents an answer nor replaces the ticket. Root records the attempt,
   controls, actual shared usage and capture/replay results.

## Fixed worker command and artifact contract

```text
python scripts/cloud_form_worker.py --bundle /inputs/job.json --sha256 <job-file-sha256> --job-root /work/one-attempt
```

`job.json` has version `cloud-form-attempt-v1`, hash-pinned `manifest`, `approval`,
`index`, `scope` and `form` references; `snapshots` maps `catalog` and `inventory`
to hash-pinned files; `model_pin` names `model_id`, `context_id`, `context_hash`.
Each file reference has exactly `path` (relative to the bundle) and `sha256`.
The approved manifest already names absolute catalog/inventory paths beneath
the new job root. The worker copies those pinned snapshots without rewriting
manifest paths or approvals. It refuses an existing job directory.

Deployment must provide PostgreSQL authority, explicit managed identity,
platform database allowlist, exact estate/model endpoint policy, model dollar
ceiling/margin, and `DIA_SLIM_RECORDING_CONFIG`. The latter uploads and verifies
sealed captures through the existing Blob gateway. This command does not obtain
an operator credential, fetch arbitrary startup code, issue grants or reset
accounting. Projected cloud persistence remains refused.

The worker re-evaluates six-stage scoped readiness offline, checks that the
shared catalog's enabled model/context equals its pin, and guards the actual
intake-derived preview against the verified whole-entity measure/scope before
start. It then calls the normal `forms.submit`, claims only that queued session
once, and calls normal `smart_intake.finish`. It does not close the ticket as
the user or retry interrupted/uncertain work. Results are private `result.json`
plus shared ticket state and governed captures; cloud logs show status only.

## Replay integration fix

Shared smart-ticket authority previously had no per-job mirror. Since each form,
read and finish operation snapshots SQLite for replay, a new PostgreSQL ticket
could be missing from the next capture's starting state. SharedTickets now
mirrors successful shared submit/read/update results into the private job
snapshot after the authority commits. Mirror failures raise and preserve the
already committed shared revision; they do not permit a SQLite authority
fallback or an automatic retry. Tests record and replay the actual ticket-state
events across separate snapshots, including failure, stale revision and request
links beyond the UI's first 40 rows.

Still to earn: actual container identity/token acquisition, new cloud approval
and route proofs, one full form investigation, Blob publication and offline
replay of its complete operation chain. Synthetic worker tests and ticket-state
replay tests do not substitute for these live results.
