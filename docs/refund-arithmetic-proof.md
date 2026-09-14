# Verified local double-refund arithmetic defect

The local lab supports inject-double-refund. It rebuilds Gold with a repository-owned wrapper
around the normal Gold query that subtracts refund_amount from net_cash_amount a second time.
The normal query already subtracts refunds. A build receipt captures the exact supported query
and current source/output fingerprints in the same transaction.

The cause verifier requires:

- A mismatch and exactly one supported arithmetic build receipt.
- Current source/output fingerprints matching the captured build.
- Current business observations matching the investigated payload.
- Replay of the repository-owned faulty query reproducing the complete Gold output.
- Replay of the correct query reconciling with Silver.

Receipt SQL is compared as text and never executed. Missing, altered, ambiguous or stale proof
does not establish a cause. The successful local finding is TECHNICAL_DEFECT with cause
Gold build subtracts refund amount twice: ORD-000001 is understated by USD 99. This proves
only the supported local build, not production provenance or a full-estate first boundary.

The normal lab verifier and reviewed two-layer worker use this additional verification path.
The existing deterministic UI displays its cause/impact without a new presentation branch.
The Silver/Gold evaluation matrix now contains ten cases including this arithmetic cause.
Reset rebuilds the original Gold query and removes the arithmetic receipt.

Routing now supports this arithmetic cause through its exact query/replay evidence contract.
Missing ownership yields NEEDS_OWNER; an explicit owner enables a review-only draft. Mixed or
stale proof remains HUMAN_TRIAGE. No automatic issue/notification or repair occurs.

Tests cover successful replay/impact/reset, missing or forged receipt text, source/output drift,
and routing hold. The existing reviewed lab workflow test includes the new case. All tests
and the evaluation use isolated local data; no live cloud/model/delivery operations occur.

To exercise the standard isolated lab manually, use the existing defect_lab.py commands:
inject-double-refund, then investigate through the local review server, then reset. The server
does not perform injection itself. Prefer evaluate_lab_matrix.py for fresh fixtures that reset
automatically. Full product/model evaluation and production proof remain pending.
