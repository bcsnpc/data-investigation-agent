# Local categorical replay UI

serve_categorical_replay.py exposes a dedicated loopback-only page for one configured lab,
retained definition bundle and native page. Start it with a local operator token (at least 32
ASCII characters) already in INVESTIGATOR_API_TOKEN:

```powershell
python scripts/serve_categorical_replay.py --database .local/replay-ui.sqlite --lab .local/defect-lab/lab.duckdb --definitions .local/report-bundle.json --page definition/pages/PAGE_ID/page.json --port 8782
```

Each slicer starts without a selection. Choose All values or enter specific strings, one per
line. Prepare captures the local lab snapshot and saves exact selections. Review the scope,
check the confirmation box and approve. Run is a separate explicit action available only after
approval. The backend verifies hashes/snapshots and preserves the existing one-attempt behavior.

The review ID is retained in the URL fragment. Reopening that URL and authenticating restores
the saved review; refresh retrieves current state after an uncertain response. Completed runs
show selected-record count, comparison and currency totals. Failed attempts remain held; the
page does not automatically retry. Preparing again creates a separate unapproved draft.

API routes require the operator bearer token. Definition/lab/page are server configuration,
not request parameters. The review database is bound to that configuration and cannot silently
switch scope. Static resources contain no token. Token stays in browser memory. This is local
operator authentication, not enterprise identity, and production workers remain unchanged.

Four API tests cover authentication, preview/approval/run/replay, confirmation/hash validation
and server-scope binding. Browser verification uses an injected local lab and fixture definitions;
no Power BI query, cloud, LLM or delivery call is made. It verifies explicit choices, approval
confirmation, saved review restoration and the local mismatch result. No production deployment.

Verification result: 355 script tests passed and JavaScript syntax passed. Browser restored
review 70b1f9b4-0063-4883-b973-facb361992c1, required confirmation, approved and ran the
fixture comparison: one selected record, Silver 99, Gold 0, difference -99 USD. Browser errors
were empty. The isolated lab reset READY and its server/token were removed. Retained test
artifacts: .local/replay-ui-check/b11322f9-02b0-41f3-a8fb-f6a4686e55e3.
