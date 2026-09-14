# Ownership-aware routing drafts

This first routing slice prepares and persists local review drafts. It has no GitHub
issue adapter, email transport, approval endpoint or delivery action. The provider
interfaces keep future issue creation and notification delivery separate from finding
classification. They are interfaces only, not operational integrations.

```powershell
python scripts/routing_drafts.py --run-id 3eaec492-8777-42fe-bce0-8ba468c75d63
```

The default source is `.local/defect-lab/evidence.sqlite`. For lab UI investigations,
pass its `.local/defect-lab/review/review.sqlite` database explicitly. Drafts are stored
in a separate `routing.sqlite` alongside the chosen evidence database.

`infra/routing/ownership.json` deliberately contains no owners. Add an operator-reviewed
entry with `kind`, `upstream`, `downstream` and `team`, for example the exact scope
`lab_record_reconciliation` / `silver` / `gold` and a real team name. No default team,
email address, GitHub assignee or recipient is inferred. Tests use fixture teams only.

Policies:

- EXPECTED_BEHAVIOR produces NO_BUG.
- Freshness, unresolved, source/data and business-review findings produce HUMAN_TRIAGE.
- A technical finding must have supported saved filter-cause proof, a matching evidence
  hash, and independently recomputed affected records/impact before draft preparation.
- Missing ownership produces NEEDS_OWNER; duplicate owner mappings are rejected.
- A qualified, owned finding produces DRAFT_REQUIRES_REVIEW with local scope, cause,
  impact, affected records, team, evidence reference and proposed notification text.

Severity stays UNASSESSED. No confidence percentage or full-estate first-boundary proof
is invented. Automatic delivery is always false. The evidence and policy hashes bind
the saved draft; unchanged repeated preparation returns the same draft, while changed
inputs produce a new one. This is draft idempotency, not external delivery idempotency.

Current cause validation supports the local filter finding only and trusts retained
operator-controlled evidence. Future cloud routing requires its own stronger supported
evidence policy, real ownership, severity/confidence configuration, review UX, approval
bound to fresh evidence/policy, provider adapters and durable delivery recovery.

The workflow ends at human triage after future delivery. No automatic remediation is
part of this implementation. No notifications or product-generated bugs were sent.
