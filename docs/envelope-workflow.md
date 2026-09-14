# Durable envelope review workflow

EnvelopeWorkflow persists the email adapter's exact envelope preview and a separate local
operator approval. It requires the existing approved routing draft and a confirmed issue
receipt. Sender, recipients, subject/body, draft hash and issue receipt are bound into the
saved envelope hash. Any difference at approval/execution requires a new preview.

The prepare, approve and detail methods are exposed through a local CLI. Review the full
prepare output before approving its envelope hash. Example placeholders:

```powershell
python scripts/envelope_workflow.py prepare --workflow <workflow.sqlite> --evidence <evidence.sqlite> --ownership <ownership.json> --draft-id <id> --draft-hash <hash> --sender <sender-address>
python scripts/envelope_workflow.py approve --workflow <workflow.sqlite> --evidence <evidence.sqlite> --ownership <ownership.json> --envelope-hash <reviewed-hash> --confirm
python scripts/envelope_workflow.py status --workflow <workflow.sqlite> --evidence <evidence.sqlite> --ownership <ownership.json> --envelope-hash <reviewed-hash>
```

The CLI has no send action, supplies no SMTP transport and keeps delivery disabled. Approval
stores a timestamp and local-envelope-operator assertion, not an enterprise identity or
external authorization. Repeated/concurrent approval preserves the original timestamp.
Historical status includes any adapter attempt, with its envelope hash so a different
previous attempt is distinguishable from the selected review.

The coordinator execute method is disabled by default. A trusted application must explicitly
enable delivery and supply an SMTP adapter after independently enforcing external permission.
Execution requires saved approval and revalidates the current envelope before delegating to
the existing durable adapter. It does not create an issue automatically or retry held mail.
Acceptance remains distinct from mailbox delivery; delivery_confirmed is always false here.

Tests exercise CLI approval/status, idempotent/concurrent approval, default-disabled execution,
missing approval, exact approved execution, receipt/policy changes and timeout state across
restart. Enabled execution uses simulated SMTP only. No live delivery was performed.

Browser envelope review, authenticated hosted execution, live transports/credentials, real
owners/recipients, provider recovery operations and authorized live acceptance remain pending.
No UI or web API send endpoint is introduced by this step.
