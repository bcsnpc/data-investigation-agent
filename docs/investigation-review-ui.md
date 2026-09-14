# Local investigation review UI

Issue #61 adds a responsive, same-origin UI to the local Python review API.
PR #56 merged at `0009b362df1a8be5e6d378db8c9a710ab8e22bb5` and PR #60
merged at `8ff356603331dd56d7d1f80e13464c3755692381`.

Start the existing server with an operator token set in its environment:

```powershell
python scripts/serve_investigations.py --enable-tickets --enable-plan-review
```

Open `http://127.0.0.1:8765/`, enter that access token, and open a ticket reference.
An optional `?ticket=<uuid>` link prefills the reference. The screen displays
ticket text, status history, drafts, human-readable report names, metric/currency/
order scope, clarification questions and prior approval links. Approval requires
a checkbox and sends the displayed draft hash. It opens the resulting child
ticket; refresh retrieves status and any saved evidence.

Evidence displays exact values, availability and comparison statuses, preserving
UNRESOLVED and NOT_COMPARABLE. These are deterministic summaries, not new LLM
root-cause claims. Worker execution remains separate. Ticket creation, model
planning, background workers, hosted authentication and LLM narrative explanation
are not exposed by this UI release.

The fixed HTML/CSS/JS assets are public only when plan review is enabled; all
data routes still require bearer authentication. The access token stays in
JavaScript memory, is cleared from its input, and is discarded on disconnect or
reload. No browser storage or third-party scripts are used. Text renders through
DOM textContent. CSP restricts scripts/styles/connections to same origin and
disallows framing; route mapping cannot read arbitrary local files.

## Verification

Agent-browser verified a temporary fixture workspace: access-token rejection
and successful connection, ticket opening, draft scope, report name, explicit
approval, queued child ticket, partial-evidence display and disconnect. Desktop
and 390px mobile screenshots were visually checked; mobile had no horizontal
overflow, and no browser errors were reported. The browser and fixture server
were stopped. Fixture records were isolated from the real workflow database.

Two static-route/auth tests, five review API tests, six evidence API tests and
two generator tests passed; JavaScript syntax checked. No SQL queries or model
calls were made, preserving the SQL free-allowance constraint.
