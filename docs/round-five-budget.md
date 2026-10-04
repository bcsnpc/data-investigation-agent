# Round Five authorised budget

2026-10-04. Human decision: `round-five-tapes-and-manifest.md` section 0.

The current local usage policy's rolling ordinary physical-request allowance was
changed from 1,000 to 1,500. Before and after control-plane reads both counted
641 charged requests and 2,293 usage rows. No counter reset, refund, reservation
or cloud request occurred. Diagnostic cap remains 12. The separate Round Five
pot is 400 physical requests, recorded in `infra/runtime/round-five-limits.json`;
Round Four remains 51/300 and Part B remains closed at 466/500.

Policy hashes:

- Before: `5b4f0f33321c430fe9ea41643c6cca9b363ce120169b9cc02064c69a9476e686`.
- After: `8bd0c6fc12edcedf3c908b1f4ae52de690271b50b561a8af0de75050823dce89`.

The policy file is local operator configuration, not the discovery configuration;
the discovery config and its approval hash were not changed. The raw before/after
record stays in `.local/round-five-20261004/budget-control-plane.json`; the ledger
contains a dated configuration decision. No run has started. Before live work,
the batch runner must enforce the separate pot, preserve failed requests, and
reserve restoration capacity; the limits file alone is not an admission gate.

No engine bytes changed in this budget record. Earlier freezes remain invalid.
