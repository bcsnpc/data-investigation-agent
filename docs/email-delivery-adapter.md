# Email delivery adapter (not activated)

EmailAdapter accepts an injected SMTP session with send_message; it does not connect,
authenticate, discover credentials or run automatically. No live messages were sent.
The adapter requires a confirmed GitHub issue receipt for the exact approved draft before
producing its envelope preview. It revalidates current evidence, ownership and content.

preview returns sender, recipients, subject, body, issue receipt and a deterministic Message-ID,
plus an envelope hash. send requires explicit authorization of this exact envelope hash in
addition to the draft hash. Sender changes require new envelope authorization. The existing
UI approves the draft only: envelope review and permission enforcement must be integrated
before live activation. The caller contract is not a replacement for authentication.

The MIME message is plain text and uses the approved body unchanged apart from standard
line-ending encoding. No issue URL is inserted into the body after approval. Message-ID is
for traceability, not a server-enforced deduplication guarantee.

A durable email_delivery_attempts claim precedes the SMTP call. Repeated successful calls
return the saved receipt without resending. Concurrent callers share the same claim.
The response distinguishes ACCEPTED, PARTIAL, REFUSED and UNCERTAIN. SMTP acceptance never
sets delivery_confirmed=true. Partial, refused and uncertain attempts cannot automatically
resend to any recipient. Provider errors and response text are not copied into receipts.

SMTP has no generic receipt lookup facility. Timeouts/crashes therefore remain held; this
adapter deliberately offers no pretend reconciliation or force-retry method. Operational
provider logs and an explicit recovery decision are still required. Accepted receipts record
what the SMTP call reported even if policy subsequently changes; they are historical facts,
not permission for another send.

A real transport must enforce authenticated TLS, bounded timeouts, no debug logging of mail
or credentials and no automatic send retries. Sender ownership, recipients and provider
permissions remain unconfigured. Application startup, UI and worker do not instantiate a
live SMTP connection. The issue-to-email prerequisite is implemented, but hosted workflow
integration, explicit envelope review and live acceptance are pending.

The send_message response handling follows [Python's SMTP documentation](https://docs.python.org/3/library/smtplib.html#smtplib.SMTP.send_message).
Eight isolated tests cover exact message content, issue prerequisite, changed authorization,
header injection, timeouts, refusal, partial acceptance and concurrent attempts. SMTP
acceptance is tested through injected responses, not mailbox delivery.
