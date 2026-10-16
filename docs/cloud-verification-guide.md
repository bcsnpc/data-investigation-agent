# One cloud approval session and one form attempt

These are operator commands, not startup hooks. They do not create credentials,
roles, or limits. Use the same deployed image for preparation, verification,
replay, readiness and the form. Its code-only source manifest must be version 2
and pass `source_revision.committed_revision()` before capture.

Mount immutable inputs at `/inputs`: `estate.json`, `endpoints.json`,
`verification-spec.json`, `form.json`, `retained-facts.json`, and the read-only
canonical `catalog.sqlite` / `inventory.sqlite` snapshots. `/work` is private
writable job storage. Gateway policy, shared PostgreSQL configuration and slim
recording configuration are injected by the operator; they are not artifacts.
The manifest's private catalog/inventory paths are `/work/one-attempt/...`.
Do not create that directory until the form worker starts. The endpoint receipt
path is `/inputs/endpoints.json`; it remains byte-pinned in the manifest.

1. Prepare in image-local **offline state mode** (unset
   `INVESTIGATOR_STATE_BACKEND` for this command only), with the source model and
   enterprise context IDs/hashes explicitly selected by the operator:

   ```sh
   python scripts/cloud_context_prepare.py --manifest /inputs/estate.json \
     --source-catalog /inputs/catalog.sqlite --source-inventory /inputs/inventory.sqlite \
     --folder /work/verification --model-id MODEL_ID --context-id RETAINED_SCAN_ID \
     --context-hash RETAINED_SCAN_HASH --actor owner \
     --decision 'Round Eighteen cloud migration: retained definitions, fresh verification, one original A demo'
   ```

   Copy `/inputs/endpoints.json` into `/work/verification/endpoints.json`
   unchanged. No estate collection occurs. The original databases stay untouched.
   The candidate re-enables only the selected model; it does not claim READY.

2. Inspect the generated `publication-candidate.json`, then publish its exact
   SHA-256 with PostgreSQL/managed identity restored. This compares the original
   model against authoritative PostgreSQL, preserves its prior revision, and
   updates that model only. A concurrent change refuses; never bypass it.

   ```sh
   python scripts/cloud_context_publish.py --candidate /work/verification/publication-candidate.json --sha256 CANDIDATE_SHA256
   ```

3. Confirm the plan offline. Full inventory includes 18 bindings, two batched
   same-database metadata reads, and the two-read native boundary: 40 approval
   probes in one session. Guards/transport requests remain separately charged
   by the shared governor; 40 is not a physical-request estimate.

   ```sh
   python scripts/cloud_binding_verifier.py --plan /inputs/verification-spec.json
   python scripts/cloud_verification_run.py --manifest /inputs/estate.json \
     --prepared /work/verification --spec /inputs/verification-spec.json \
     --spec-sha256 SPEC_SHA256 --session UNIQUE_SESSION --deadline UNIX_DEADLINE \
     --capture /work/verification-capture
   ```

   No language model is used. Any refused witness stops the verifier, with
   partial progress and exact error retained. Do not repeat, omit a binding, or
   increase the cap to manufacture completion. The caller must archive the
   capture and settle/report the actual shared counters, including failures.

4. Only after completion, replay and build readiness from this fresh capture.
   The retained facts file supplies declaration inventory and scope only; every
   retained asset hash must still match. Historical witnesses are discarded.
   Exact native queries, attestation, quantity and source bindings are rechecked.

   ```sh
   python scripts/cloud_readiness_build.py --manifest /inputs/estate.json \
     --prepared /work/verification --retained-facts /inputs/retained-facts.json \
     --capture /work/verification-capture --output /work/readiness
   ```

   Stop if the result is BLOCKED. READY is derived by the six-stage consumer,
   never supplied by the operator. The replay itself performs zero network reads.
   Keep paths stable for its source-bound receipt references.

5. Build a `cloud-form-attempt-v1` JSON bundle in `/work`. Every file reference
   is `{path: RELATIVE_PATH, sha256: FILE_SHA256}`: `manifest` points to a
   byte-identical copy of `/inputs/estate.json`, `approval` to the generated
   approval, `index` and `scope` to `/work/readiness/{index,scope}.json`, and
   `form` to the unchanged saved form. `snapshots` has `catalog` and `inventory`
   referencing `/work/verification` snapshots. `model_pin` contains the generated
   model's `model_id`, `context_id`, and SHA-256 digest of its context object.
   Paths must be within `/work` (copy inputs there unchanged); no `..` escapes.
   The bundle has no READY flag, credentials, answers or expectations.

   ```sh
   python scripts/cloud_form_worker.py --bundle /work/form-bundle.json \
     --sha256 BUNDLE_SHA256 --job-root /work/one-attempt
   ```

   The standard form path runs once. Intake questions/refusals remain results;
   the worker does not answer them. It rechecks readiness and authoritative PG
   model pins before model/estate admission. Existing dollar, physical, rolling,
   reserve and investigation guards apply. Retain the result and durable tapes.

No actual cloud verification or demo success is established by this guide or its
offline tests. Windows-generated engine fingerprints are not cloud approvals;
image-local preparation is required. The source application remains unreachable
until an explicitly supported credential route exists; no fallback identity is
allowed.
