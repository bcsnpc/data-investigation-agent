# Local routing delivery rehearsal

The routing rehearsal tests the handoff from an approved draft to issue creation and
then notification using durable **local simulated receipts**. It cannot send network
requests, create a real issue, or send a message. It is not wired into the UI or worker.
Real provider adapters, recipient approval, provider lookup/recovery and deployment
remain separate work.

The existing review approval is required before enqueue. Current evidence and ownership
are revalidated before each stage and receipt reconciliation. The approval hash binds the
rehearsal to the reviewed draft. The default real ownership policy remains empty.

Each stage gets a stable key derived from its draft ID, approved hash and stage. SQLite
claims one stage transactionally. Notification waits for the issue receipt and includes
that reference. Repeated enqueue and completed execution are idempotent. Simulated
receipts are committed separately from worker success, modeling a worker interruption
after a provider accepts an operation.

An attempted stage is marked UNCERTAIN before generating its receipt. Another worker
cannot automatically replay it. Explicit reconciliation requires a receipt with the
matching payload hash. Missing or conflicting receipts remain held; there is no force
retry, timeout retry or automatic uncertain-operation replay. Successful rehearsal status
means only the local simulation completed, never that a real recipient was notified.

Run against an existing locally approved draft and its matching evidence/policy files:

```powershell
python scripts/routing_delivery_rehearsal.py enqueue --draft-id <approved-draft-id> --workflow <review.sqlite> --evidence <evidence.sqlite> --ownership <ownership.json>
```

Use the same arguments with `advance` to run at most one stage, `status` to inspect it,
and `reconcile` to resolve a held operation using its saved local receipt. For recovery
verification, use `advance --interrupt-after-receipt`, then `reconcile`, then `advance`
to complete notification. The command requires existing files and never records approval
on the operator's behalf. All output includes LOCAL_REHEARSAL and external_delivery=false.

The workflow database contains routing_rehearsals, routing_rehearsal_steps and
routing_rehearsal_receipts. No production delivery table or provider credentials are used.
Database integrity and the local operator remain trusted; this does not solve atomic
policy changes across independent evidence/policy stores or individual reviewer identity.

Tests cover missing approval, stage order, idempotency, both stage interruptions,
restart, absent/conflicting receipts, changed evidence/ownership, concurrent workers,
and the command-line recovery sequence. All use fixture teams and isolated databases.

Before real delivery: bind the approved destination and exact provider payload, implement
provider-specific idempotency and receipt lookup, validate credentials/recipient ownership,
and obtain authorization for external issue/message delivery. Provider timeouts must remain
held when acceptance cannot be determined. Local simulated receipts prove the state machine;
they do not establish a third-party provider's delivery guarantees.
