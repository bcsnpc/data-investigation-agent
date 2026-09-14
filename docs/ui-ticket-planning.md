# Ticket submission and live planning from the UI

Issue #63 follows PR #62, merged at `1923b5654b18b7c823260bc91404561efb760c54`.
The user authorized bounded live SQL and LLM testing; SQL must still retain
`useFreeLimit=true` and `freeLimitExhaustionBehavior=AutoPause`.

```powershell
python scripts/serve_investigations.py --enable-tickets --enable-plan-review --enable-planning
```

After connecting, expand **Start a new investigation**, enter title, report and
description, and submit. Then select **Generate draft**. The UI displays the
inferred scope and requires review before **Approve and queue**. The existing
worker still runs separately; refresh displays its saved evidence. Submission
alone and status refreshes do not call the model.

POST `/api/tickets/{id}/plan` requires the shared operator bearer token, a UUID
`Idempotency-Key`, and exactly `{"confirm":true}`. The endpoint is disabled
unless explicitly enabled. It verifies ticket existence/current lineage, stores
RUNNING in `planning_requests`, and starts the existing Azure planner in a child
process. The child loads keys in memory through personal Azure CLI authentication
and uses the same configured workflow database. It has a 130-second timeout.
The HTTP request is synchronous: the local single-thread WSGI server waits during
planning. This is a local development workflow, not a production job service.

The same ticket/key returns the retained result without another provider call.
FAILED requests are also retained. A process crash can leave RUNNING with an
uncertain provider outcome; repeating that key returns 202 without re-execution.
Inspect saved drafts before issuing a new key. There is no automatic retry or
lease recovery for paid model calls. The browser reuses its key in the current
page session; reloading and deliberately requesting planning can create a new
paid call. Each accepted draft remains non-executable until reviewed approval.

The original narrative ticket may become NEEDS_INPUT if the deterministic worker
claims it without explicit metric/currency fields. The approved child contains
validated explicit scope and is the ticket used for evidence acquisition. UI
approval navigates to that child. Intake/workflow status unification is later work.

## Verification

Four request tests cover completed/failed replay, in-progress replay and a missing
persisted plan. Seven review API tests cover explicit request/key/opt-in behavior
and existing review flows. Six workflow and two generator tests passed.

The live browser opened the existing baseline ticket and its saved evidence,
then submitted ticket `548e4cef-8116-47ce-8fe6-b54f2475c11c` for ORD-000002.
Live model planning produced `1c002541-0fe2-49f1-89ed-ed0cfb814225` with Executive
Sales / Net Cash / USD / ORD-000002. The operator reviewed and approved that
scope into child ticket `e0270880-bf1c-44fa-bea9-b435aca35a3f`.
Two model calls were made in this browser verification: baseline re-planning
(550 tokens) and the new single-order draft (554 tokens), 1,104 tokens total.
No source business writes were authorized or performed.

The approved worker completed run `9ef75410-0b9e-433b-b648-6b20b806c73a`.
SQL, Bronze, Silver, Gold and semantic each returned one order and USD 1,529.64.
The browser refreshed and displayed all ten observations with AVAILABLE status.
Classification remains UNRESOLVED with NOT_COMPARABLE boundaries because exact
snapshot comparability is still unproven. No browser errors were reported.
Browser and local server stopped; the temporary operator token was removed.

This run also exercised actual SQL wake-up recovery: attempt one failed with
40613 at connection, a 10-second delay followed, and attempt two succeeded.
The saved observations retain both attempt timestamps and outcomes. This is live
recovery evidence in addition to the earlier simulated retry tests.
