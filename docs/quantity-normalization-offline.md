# Declared-report exclusion and shared quantity normalization

2026-09-27. Tracking #193. Offline saved-R2 check only.

The process adapter and synthesis now share scalar normalization. Only report
columns declared by the compiled request are excluded (both ordinary and DAX
bracketed labels). Receipt rows and attestation remain intact. Undeclared columns
are never stripped by name; multiple measurement columns remain non-scalar.
Synthesis derives comparable quantities only after verifying sealed query receipts,
request hashes and original result rows. Different numerical values still fail
an asserted-equal comparison. No planner context or directory coverage changed.

Correction to the proposed diagnosis: saved R2 already had its DAX identity column
removed by `flexible_tools.extract`. Its sealed measured rows contain only
`[baseline]`; SQL has `quantity`. The previous blocker was synthesis's raw-row
comparison, not a failure of the adapter to normalize that saved result. The new
shared projection also protects callers receiving unstripped declared report columns.

Read-only offline replay of session `54509912-5e30-4850-afd7-ed26b5bc56aa` verified
both seals and requests, then validated the equal normalized cross-surface
comparison. **Synthesis still does not complete:** full digest construction now
fails with `KeyError: metadata`. The ingestion context observation stores its
fields at the root, while synthesis expects a `metadata` object. This is a separate
contract gap, recorded without inventing metadata or editing the saved session.
No model or cloud call was made. Original runs and artifacts remain unchanged.
This check cannot establish successful model synthesis.

Validation: 17 independent-lower-read tests, 25 surface-self-report tests,
19 synthesis tests and two generator tests passed (63 total). New regressions
cover declared report exclusion, undeclared-column retention, immutable input,
non-scalar preservation, different aliases and genuinely different quantities.
[Offline receipt/diagnosis](runs/quantity-normalization-offline.json).
