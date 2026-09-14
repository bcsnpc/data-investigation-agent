# Live transport integration

The operator CLI now connects the existing durable adapters to HTTPS and SMTP transports.
It is never invoked by the review server or background investigator worker. No live delivery
has been tested or activated in this milestone. Real owners, recipients and provider access
remain unconfigured; fixture tests do not establish live permissions or deliverability.

GitHub transport pins api.github.com, restricts paths to the issue adapter's create/list
operations, validates certificates and uses a 20-second socket timeout. Responses are capped
at 2 MiB and request bodies at 128 KiB. It does not follow redirects or retry. Error response
content is discarded. See [Python HTTPSConnection](https://docs.python.org/3/library/http.client.html#http.client.HTTPSConnection).

SMTP transport connects lazily on send. Port 465 uses implicit TLS; port 587 requires
STARTTLS before authentication. Certificate/hostname validation is enabled and socket timeout
is 20 seconds. No plaintext fallback, debug output or automatic retry is provided. It uses
SMTP username/password authentication; the selected provider must support and authorize that
method. OAuth-only providers need an additional implementation. See [Python SMTP](https://docs.python.org/3/library/smtplib.html).

Credentials are read from process environment only, never command-line arguments:
INVESTIGATOR_GITHUB_TOKEN; INVESTIGATOR_SMTP_HOST; INVESTIGATOR_SMTP_PORT (default 465);
INVESTIGATOR_SMTP_USERNAME; INVESTIGATOR_SMTP_PASSWORD. Configure them locally without sharing
secrets in chat or committing them. Nothing automatically loads or logs credentials.

After independently authorizing the reviewed destinations and content, the operator may use:

```powershell
python scripts/run_delivery.py create-issue --workflow <workflow.sqlite> --evidence <evidence.sqlite> --ownership <ownership.json> --draft-id <id> --draft-hash <reviewed-hash> --confirm-external
```

Use reconcile-issue with the same arguments to look up a held GitHub attempt; this never
retries POST. After a confirmed issue receipt, prepare and approve the email envelope in the
review UI or envelope CLI. Sending requires its exact persisted approval:

```powershell
python scripts/run_delivery.py send-email --workflow <workflow.sqlite> --evidence <evidence.sqlite> --ownership <ownership.json> --envelope-hash <approved-envelope-hash> --confirm-external
```

The confirmation flag expresses the local operator's external-action decision. It is not a
hosted authorization boundary. Existing evidence/approval checks and durable attempt claims
still apply. Failure output is generic; inspect saved workflow/adapter state before acting.
SMTP acceptance is not delivery confirmation. Uncertain/partial/refused email is not retried.
The transports use per-socket timeouts, not a whole-operation wall-clock deadline.

Tests mock connection classes to check TLS ordering, fixed host, path restrictions, redirects,
timeouts, response limits, refusal propagation and confirmation gating. No network sends run
in these tests. Pending: real provider setup, mention/markup policy, hosted permissions,
provider recovery operations and explicitly authorized live acceptance.
