# Browser envelope review

The isolated lab server exposes envelope preparation, status and approval under its existing
bearer authentication. In an approved routing review with destinations, enter the email
sender and choose Review email envelope. A confirmed issue receipt is required. The browser
shows sender, recipients, subject, exact body and issue reference before the review checkbox
and approval button. Existing attempt status is displayed with its envelope hash.

Endpoints:

- POST /api/routing/{draft_id}/envelope: confirm:true, draft_hash and sender.
- GET /api/envelopes/{envelope_hash}: saved preview, approval and attempt status.
- POST /api/envelopes/{envelope_hash}/approve: confirm:true.

JSON bodies are bounded to 1 KB and exact fields. IDs/hashes and methods are validated.
There is no send endpoint. The API rejects an enabled execution coordinator during setup,
and the lab server constructs the email adapter without an SMTP connection. Approval invokes
only the durable review workflow; no provider adapter sends are called.

Changes to evidence, policy or issue receipt block approval. Historical approval/status is
preserved and does not prove mailbox delivery. The existing shared-token reviewer assertion
is local, not enterprise identity. Live permission enforcement and deployment remain pending.

Browser checks use an isolated fixture repository, simulated issue receipt and example.invalid
sender/recipient. They prepare and approve the envelope without a live issue or email send.
The normal empty owner policy is unchanged. The full product still requires real provider
configuration, live authorized verification and hosted authentication/monitoring.
