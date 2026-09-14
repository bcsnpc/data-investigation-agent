# Local plan review API

Issue #59 depends on the reviewed handoff in PR #56. SQL retry PR #58 was
merged separately at `3522f9a23852a12b53129c97905989e8b7de381a`.

Start the local server with the existing bearer token in the environment:

```powershell
python scripts/serve_investigations.py --enable-tickets --enable-plan-review
```

The additional flag is opt-in and requires ticket support. All routes retain
bearer authentication, no-store headers, loopback binding and quiet logging.
This is a single local operator interface, not multi-user production auth.

| Request | Behavior |
|---|---|
| GET /api/tickets/{ticket-id}/plans?offset=0 | Up to 20 drafts, stable UUID ordering, next_offset when more exist |
| GET /api/plans/{plan-id} | Draft, SHA-256 plan_hash and existing approval/child link if present |
| POST /api/plans/{plan-id}/approve | Explicit approval of the reviewed hash; creates one linked queued ticket |

Approval requires JSON with exactly these fields:

```json
{"confirm": true, "plan_hash": "<hash returned when viewing the draft>"}
```

The hash binds approval to the displayed record. Draft and current estate
lineage are rechecked, and the existing transactional handoff prevents duplicate
work. The estate file is reloaded on each approval. A changed hash, stale lineage
or non-approvable draft returns 409. Bad input returns 400, missing records 404,
wrong content type 415, and approval bodies over 4 KiB 413. First approval
returns 201; repeat approval of the unchanged draft returns 200 and the same
ticket/status URL. Authentication is checked before request parsing.

`local-api-operator` is the recorded reviewer for this shared-token interface.
It does not establish a named person's identity. The operator must review the
meaning of the full scope; matching hashes cannot detect a model's missed filter.
The HTTP request only queues work. It does not run SQL, call the model, send a
notification or route a defect. A worker is still run separately.

Five API tests include real local HTTP viewing/approval, duplicate approval,
missing/false confirmation, stale hashes, changed lineage and invalid inputs.
Six handoff tests, six existing evidence API tests, six workflow tests and two
generator tests also pass. Temporary test databases and servers are cleaned up.
No Azure SQL or model calls were needed for this change. SQL must retain its
free limit and AutoPause-on-exhaustion settings; no paid overage is authorized.

Next: a user-facing review UI and validated LLM narrative explanations.
