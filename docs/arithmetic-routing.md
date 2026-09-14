# Arithmetic routing evidence contract

Verified local double-refund findings can now prepare routing drafts through the existing
owner/review workflow. No real owners, recipients or delivery settings are changed.

Routing selects an exact supported contract by cause:

| Cause | Required query | Required replay flags |
| --- | --- | --- |
| Excluded partially returned records | filter_query | filtered replay matches, unfiltered replay reconciles |
| Refund subtracted twice | double_refund_query | faulty replay matches, corrected replay reconciles |

The saved result and proof must agree on cause and technical classification. The evidence
hash must match. Record reconciliation independently reproduces impact, affected records and
boundary. Unknown causes, mixed query/flag contracts, changed impact or stale evidence remain
HUMAN_TRIAGE. Evidence remains the trusted local operator-controlled store; this does not
re-run live query proof or establish production provenance.

A supported finding without an owner returns NEEDS_OWNER. With an explicit boundary owner,
it yields an idempotent DRAFT_REQUIRES_REVIEW record containing the correct arithmetic title,
USD 99 impact, affected order and scope limitation. Existing approval/rehearsal paths recompute
the same contract, so changed proof invalidates later actions. Review does not enable delivery.

Four tests cover owned draft/idempotency, mixed or rehashed invalid proof, changed impact,
and approval/rehearsal followed by stale-proof rejection. Existing filter behavior remains
covered by prior tests. All owners and operations in this step use isolated fixtures.
