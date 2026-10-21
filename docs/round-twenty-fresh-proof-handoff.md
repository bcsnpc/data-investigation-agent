# Fresh verification proof to a normal cloud demo

The original typed runner only checked the verification result's status strings. It did not consume the sealed witnesses or reproduce the old form worker's model/scope checks. It did not publish inferred binding profiles either. The current estate uses static declared paths: its code locations do not enable inference. A verifier's `profile_published=false` remains false throughout the handoff.

New combined demos and a standalone typed `investigation` use `cloud_verification_proof.validate`. It checks the hash-pinned source artifacts, sealed native tape, current image engine/revision/config/policy, current approval/context/model/spec pins, complete proposal/witness conservation, native value-query receipts and the independently recomputed Microsoft semantic-to-SQL declared route. Binding verdicts are recomputed by the existing `revalidate_verification` consumer; native attestation and compilation are recomputed by `validate_declared_route`. No provider or estate query is performed by this validator. A claimed VERIFIED string is insufficient.

After that, normal workspace construction must expose shared authority and the exact same published model record. The existing form resolver binds explicit picks to retained definitions. The current handoff supports only the independently verified ungrouped, unfiltered whole-entity measure; a different measure, filtered/grouped or incomplete visual scope refuses before model admission. Normal form submission and its own validation still run, with the existing preview guard retained. This is not a new ticket interpretation or a route inferred from matching an expected figure.

The proof result says `PROOF_REVALIDATED`, `readiness=NOT_ASSESSED`, `profile_published=false`, the bounded sample count and snapshot limitation. It never manufactures READY or publishes profiles. No `retained-facts.json` or exact replay is required before live work. Replay remains a separate step after the live run on the same image.

## Separate jobs under the existing overall deadline

Run a typed verification-only check with no `demo_ticket`. Retain its prepared snapshots and complete native capture through existing CAS manifests. For the subsequent typed investigation, restore those same immutable artifacts into a new job input directory; keep the original approved manifest and spec unchanged. Do not re-prepare a different context between the jobs.

The standalone investigation options are exactly:

```json
{
  "ticket": "/inputs/form.json",
  "verification_proof": {
    "version": "fresh-cloud-reader-proof-v1",
    "prepared": "/inputs/prepared",
    "capture": "/inputs/capture",
    "spec": "/inputs/verification-spec.json",
    "capture_sha256": "<sha256 of capture/tape.json>",
    "approval_sha256": "<sha256 of prepared/approval.json>",
    "spec_sha256": "<sha256 of the original verification spec>"
  }
}
```

`cloud_verification_proof.reference` creates this local reference without network calls. The new input bundle is distinct from the existing seven-member verification bundle. It contains the original manifest/spec/form, retained prepared catalog/inventory/approval/context/model/endpoints, and the complete capture tape and its seven hash-pinned baseline dependencies. Restore from existing CAS; never fabricate or rewrite a baseline. The normal runner pins the image. Both jobs keep the existing 1,800-second hard runtime and monthly accounting; separating them does not admit a different identity or bypass budget guards.

Regressions cover actual witness/native consumers, missing or forged evidence, source/context/spec/image changes, changed current authority, filtered form refusal before model calls, and the standalone typed path reaching normal `run_form`. Original tapes and acceptance expectations are untouched.
