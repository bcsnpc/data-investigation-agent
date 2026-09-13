# Ticket intake and deterministic execution

The local evidence service can now accept tickets when started with `--enable-tickets`. It uses a separate `workflow.sqlite` beside the metadata database. Existing investigation evidence endpoints remain read-only; intake writes only local workflow records. Authentication uses the same local bearer token.

| Endpoint | Behavior |
|---|---|
| `POST /api/tickets` | Accept JSON and a UUID `Idempotency-Key`; return ticket ID/status URL |
| `GET /api/tickets/<UUID>` | Return ticket, pinned graph, status, timeline, outcome and evidence-run link |
| `GET /api/investigations/<UUID>` | Retrieve linked saved investigation evidence |

Required fields are `title` (200 characters), `report` (200) and `description` (10,000). Optional fields are `metric`, `currency` and `order_id`. Unknown fields are rejected and request bodies are limited to 16 KiB. Attachments and editing existing tickets are not implemented. Duplicate submission keys return the existing ticket; different content with the same key returns 409. Corrections currently require a new submission/key.

```powershell
# Set INVESTIGATOR_API_TOKEN as described in investigation-evidence-api.md.
python scripts/serve_investigations.py --enable-tickets
# In the worker's local environment, process one pending ticket:
python scripts/ticket_worker.py
```

The API enqueues and returns promptly; it does not execute cloud reads in the HTTP request. A separate worker atomically claims one ticket. States are QUEUED, RUNNING, NEEDS_INPUT, COMPLETED and FAILED. Each transition appends a timeline event in the same transaction. No always-running worker or public service is installed by this change.

The first worker supports only explicit `Order Count` or `Net Cash`, an uppercase three-letter currency, and optionally an `ORD-######` order filter. It resolves the report and metric against the pinned graph. Missing/unsupported scope or a changed configured graph becomes NEEDS_INPUT without a cloud query. The worker does not interpret descriptions, dates, visuals or implied filters; that requires the future LLM/planning layer. Its outcome explicitly states the narrow executed scope.

COMPLETED means bounded evidence acquisition finished. It can include NOT_COMPARABLE, INSUFFICIENT_EVIDENCE or UNAVAILABLE boundaries and retains classification UNRESOLVED. It does not mean the ticket is resolved, all reads succeeded or a defect exists. Exception bodies are not retained in FAILED outcomes. No external issue creation, notification, LLM call or business-data mutation occurs.

Claims use a 30-minute lease. A later worker invocation may reclaim an expired RUNNING ticket; the old claim cannot finalize after expiry or replacement. Recovery can repeat read-only acquisition and leave an unlinked evidence run if a process crashed between acquisition and ticket completion. This is at-least-once execution with fenced finalization, not exactly-once cloud reads. The bounded current worker is expected to finish within its lease; heartbeats and a hosted worker are future work.

Six workflow tests cover durable idempotency/conflicts, concurrent claims, expired-claim fencing, missing scope without execution, sanitized failures, HTTP intake and status/evidence linkage. Six evidence API tests and generator tests also pass. Live verification is recorded in the tracker.

Live HTTP ticket `f2fa6c29-7080-4d54-a882-3d99772b5b0b` completed and links to investigation `d8cab0ab-c823-4171-a98a-6f20497e63b7`. Both status and linked evidence were retrieved through authenticated HTTP. The four downstream layers matched baseline totals; source SQL was unavailable, and the ticket outcome preserves UNAVAILABLE/NOT_COMPARABLE and UNRESOLVED. This verifies handling of partial evidence rather than claiming complete source connectivity. The temporary server stopped after the check.
