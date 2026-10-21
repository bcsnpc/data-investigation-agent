# Fresh verification proof to a normal cloud demo

The original typed runner only checked the verification result's status strings. It did not consume the sealed witnesses or reproduce the old form worker's model/scope checks. It did not publish inferred binding profiles either. The current estate uses static declared paths: its code locations do not enable inference. A verifier's `profile_published=false` remains false throughout the handoff.

New combined demos and a standalone typed `investigation` use `cloud_verification_proof.validate`. It checks the hash-pinned source artifacts, sealed native tape, current image integrity, exact runtime engine/config/policy, current approval/context/model/spec pins, complete proposal/witness conservation, native value-query receipts and the independently recomputed Microsoft semantic-to-SQL declared route. Binding verdicts are recomputed by the existing `revalidate_verification` consumer; native attestation and compilation are recomputed by `validate_declared_route`. No provider or estate query is performed by this validator. A claimed VERIFIED string is insufficient.

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

## Content identity across replay utility changes

DECIDED WITHOUT REVIEW, 2026-10-21: the original handoff required the verification tape's Git commit to equal the demo image's commit. That was an internal conservative check, not the owner's rule that each live run must replay on its own image. It unnecessarily required repeating all verification reads after a change confined to a replay utility outside the runtime fingerprint. The rejected alternative was to repeat unchanged estate reads solely for that utility change.

The handoff now verifies current image provenance, requires the source tape revision to match its sealed state, and retains the exact runtime fingerprint, verifier and capture-program hashes, context, model, configuration, policy, spec, native receipts and complete witness checks. A changed runtime or producer still refuses. The proof records `source_engine_revision`, `current_image_revision` and `same_image_revision` separately; different revisions are never described as same-image verification. Each investigation's replay still requires its own exact image revision and fingerprint, with no drift override. Original tapes remain unchanged.

## Owner correction: independent verification is a label in BUILD_PHASE

2026-10-21 owner direction: C5's failed semantic query remains a failed verification, but does not gate the approved live demo. The standalone handoff accepts explicit `verification_handling: LABEL_ONLY_BUILD_PHASE` only when the manifest declares BUILD_PHASE. Strict proof gating remains the default elsewhere. The handoff records the original sealed native FINAL status/error as `verification_label`, attempts the existing proof checks, and records failed proof/model/scope handoff checks as warnings. It never calls those failed checks VERIFIED. The demo result is separate.

The normal `run_form` path still owns intake, declared read scope, read-only gateway, authoritative shared budgets, evidence/delivery and overclaim validation; their errors are not caught as handoff warnings. Shared authority remains mandatory. The proof-specific preview wrapper is not installed in label-only mode because it would reinstate the independent verification gate. No identity, permission, model, route or expectation is changed by selecting this mode.
