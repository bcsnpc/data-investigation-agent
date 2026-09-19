# Evidence-qualified conclusions and discriminating tests

2026-09-19. Current implementation status belongs in [delivery status](current-delivery-status.md).

## Research and implementation choice

[OpenAI trace grading](https://developers.openai.com/api/docs/guides/trace-grading)
recommends examining execution traces to locate failures, not only scoring final
answers. [Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
separates tool selection, argument precision and functional correctness; it also
recommends that evaluation evidence drive architectural expansion. We apply these
ideas to the existing runtime rather than migrating frameworks or adding agents.

The previous transformation run completed but assigned a likely defect to an
unestablished business interpretation. Completion and valid citations alone did
not make the diagnosis correct. The existing instructions already mentioned
uncertainty, but the final decision did not explicitly identify that dependency.

Current provider STOP decisions require a bounded support object: observed
mechanism, mechanism receipts, dependency on intended business rules, cited intent
basis, and the best remaining test or reason none is useful. The runtime rejects
assertive defect, source/application, freshness and expected-behavior labels when the planner explicitly marks
the essential intended rule UNKNOWN. ESTABLISHED needs cited successful evidence;
mechanism support for those labels needs a complete live read. Historical saved
assessments remain readable and injected legacy adapters retain compatibility.

These checks validate references and explicit contradictions. They cannot verify
that a citation semantically supports a claim, certify intent authority, or stop
a model from incorrectly declaring NOT_REQUIRED. Support remains LLM_INFERRED.
No TEAM_CONFIRMED provenance or verified cause is synthesized. Metadata availability
and the support object grant no execution permissions.

Planner guidance now favors tests separating competing explanations and targeted
source search using observed identifiers. It does not require SQL, a fixed layer
sequence, a join check, or any scenario-specific test for every ticket. Bounded
reads, cancellation, replay, read-only identity and cost policies remain.

## Evaluation criteria

Evaluate these independently; no weighted completion score hides a failed claim:

- Does a read or retrieved definition actually discriminate the proposed mechanism,
  rather than merely reproduce the reported value?
- Is a plausible competing explanation tested, or is its omission explained by
  missing capability, scope, evidence or budget?
- Does the label require business intent that the available evidence cannot establish?
- Are successful, partial, rejected and unavailable observations distinguished?
- Does the final response answer what can be established and preserve what cannot?

An adequate uncertainty answer can pass a ticket without a defect label. A plausible
but unsupported defect label does not pass because it includes caveats. Independent
review of observations remains necessary; the planner does not grade its own success.

Current
fixtures remain known-domain regressions; changed engine bytes require a fresh
freeze and newly introduced variant for unfamiliar-domain acceptance.


## First live transformation trial

Known-domain session `e8b3d11a-08af-47f7-82a5-816405cf3b4b` completed in 11 planner
calls with six context lookups and four successful reads (three SQL, one DAX).
It measured 360 source movements becoming 409 joined rows, 49 extra matches,
and no unmatched movements. Source units were 7,568 versus 8,580 joined units.
A native query and the source valuation calculation both returned 53,145. A
further source test localized fanout to one product with two rate versions.
No expected values or scenario-specific route were supplied to the planner.

This is substantially stronger mechanism evidence than the prior sign-based
interpretation. The final support object correctly marked intended rate selection
UNKNOWN and withheld a corrected valuation. However, it selected
SOURCE_OR_APPLICATION_ISSUE despite that essential unknown premise. The original
check only covered likely-defect and expected-behavior labels, so this exposed a
classification consistency gap. The check now also covers source/application and
freshness issue labels. This does not erase the successful observations or turn
that first run into a final-engine acceptance result. A repeat evaluates the change.

Provider decision decoding now also requires the support object instead of relying
only on the strict provider schema. Legacy injected adapters and old saved results
remain compatible. A generic clarification distinguishes catalog search for an
object's schema from literal search inside source text.

Validation: 949 local regression tests passed on the corrected engine, including
unknown-intent labels, failed/partial citations and missing provider support.


## Corrected-engine repeat

Session `dd1b3de5-2c6e-47f8-adc5-73eda6f05b87` completed with
BUSINESS_CONTEXT_REQUIRED in 11 planner calls and three successful reads (one
DAX, two SQL), with five context lookups. It measured the current 53,145 and a
50,109 latest-version-only counterfactual, with 409 versus 360 rows. The conclusion
explicitly withheld business correctness and a corrected total until the intended
rate-version rule is supplied. It recovered from one SQL complexity rejection
and one support-citation consistency rejection; neither caused a remote retry.

The repeat is useful known-domain mechanism investigation and uncertainty handling,
not proof of general reliability. Retrieval still consumes a substantial fraction
of the call budget. The next acceptance step is a new engine freeze and fresh
variant, with all nine families and repeated trials; no unfamiliar-domain pass is
claimed. Original daily allowances were restored without resetting usage. No SQL
limits, identities, permissions, deployments or source data changed in this work.
