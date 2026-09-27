# Enforced dual outputs

2026-09-27. Known-domain regression only. Engine bytes changed; all earlier
freezes remain invalidated. No new freeze or variant.

The business explanation is a closed, outcome-specific statement enforced by a
single-value enum in the response schema. It accepts no free-text substitution,
asset label, query description or numeric interpolation. The provider still cites
the evidence; the wording is marked DETERMINISTIC_OUTCOME_RENDERING. This trades
free-form business detail for an enforceable plain-language guarantee. The full
technical evidence remains available separately; original observations are not
redacted or reconstructed for validation.

Both returned outputs carry recommended_action derived from the existing ACTIONS
taxonomy. Its plain-language text is also present in each explanation. The model
cannot choose an incompatible action. Deterministic pre-synthesis outputs also
carry their taxonomy action. Technical narrative assembly appends every recorded
unattested surface field with layer and receipt identity, so provider omissions
cannot remove those qualifications.

Tests reject injected assets, query text, jargon and extra numbers for every
outcome; all actions match the taxonomy; all five attestation fields survive a
provider narrative that omits them. The existing whole-response and original-
evidence validation remains intact. No planner context is added: initial directory
coverage and synthesis input payload are unchanged; the wire response schema is
more restrictive.

Live evidence and final validation follow below. No success is claimed before the
single requested live run.

## One live run

Run `cbb9c17f-b720-436a-b72a-474a10e94aee` completed with validated synthesis. Intake classified
the unchanged ticket as BUSINESS_QUESTION, a different valid interpretation from
c2658c88; no retry or claim that schema closure removes interpretation variance.
One equal independent boundary, one DAX read, one Fabric SQL read, one OneLake
metadata invocation; one intake and one synthesis call, zero investigation
planner calls. Stopped at Gold; deeper capability and freshness unavailable.
Five surface fields remain unattested. No permission, config or policy change.
One ledger row appended; historical rows untouched.

## Business explanation ? verbatim

The checked information agrees. The remaining question requires business knowledge that this investigation cannot establish. Recommended action: Ask a business specialist to explain the intended rule.

## Technical explanation ? verbatim

The measure returned 8765 on the Activity surface, and a direct SQL aggregation of movement_values.units also returned 8765. The process comparison recorded those aggregates as equal across the two execution surfaces. Ingestion metadata shows movement_values was written once with 406 output rows. The investigation did not reach deeper stock-movement or adjustment sources, so it cannot determine whether any source entries reflect the intended business rule.

Surface attestation limits:
- Unattested connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity (receipt 1d288186-c597-46ff-ade0-0e44420d019d).
- Unattested engine on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity (receipt 1d288186-c597-46ff-ade0-0e44420d019d).
- Unattested object on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity (receipt 1d288186-c597-46ff-ade0-0e44420d019d).
- Unattested connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values (receipt ee8c50df-af1b-4951-8117-94a2bee78d79).
- Unattested engine on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values (receipt ee8c50df-af1b-4951-8117-94a2bee78d79).

Recommended action: Ask a business specialist to explain the intended rule.

The original structured conclusions and limits remain attached.
[Full output records](runs/enforced-dual-outputs.json), [per-run metrics](runs/enforced-dual-outputs-live.json).

Validation: seven output-contract tests passed. Full suite ran 1,210 tests with
one failure: an injected synthesis response still used free business prose. The
fixture was updated to the enforced wire contract; no production code changed
after the live run. Focused synthesis tests are rerun; CI checks the final head.
Initial full-suite failure remains in the local validation log.
