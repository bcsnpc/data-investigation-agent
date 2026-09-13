# Saved investigation evidence API

The local WSGI backend exposes retained investigation runs from SQLite. It does not execute SQL/DAX, start an investigation, refresh Fabric, submit tickets or route defects. Its purpose is to give the future investigation interface a stable way to read saved evidence.

| Endpoint | Result |
|---|---|
| `GET /api/investigations?limit=20&offset=0` | Newest runs first, ordered by creation time and ID; summary records plus `next_offset` |
| `GET /api/investigations/<canonical UUID>` | Saved request and result, graph ID, classification and explicit read-only capabilities |

All requests require `Authorization: Bearer <token>`. The server token comes from `INVESTIGATOR_API_TOKEN`, must be at least 32 ASCII characters, and should be generated randomly. It is not a cloud credential. No token is committed or written by the API. Responses use `Cache-Control: no-store`; the server does not log request URLs. There is no CORS allowance.

```powershell
$env:INVESTIGATOR_API_TOKEN = python -c "import secrets; print(secrets.token_urlsafe(32))"
python scripts/serve_investigations.py --port 8765
```

The launcher binds only to `127.0.0.1`. An authorized local client must use the same token. This is a single-operator development service, not a public deployment or production identity system. The process runs in the foreground until stopped. The API module implements WSGI so a hosted server/authentication adapter can be introduced later.

SQLite is opened with `mode=ro` and `query_only`; a missing database is not created. Pagination accepts limits 1–100 and offsets 0–100000. Offset pagination is stable within a query, but inserts between requests can shift subsequent pages. The client should deduplicate run IDs when browsing a changing store. Invalid pagination/IDs return 400, missing records 404, unauthorized requests 401, mutation methods 405, and unavailable/corrupt evidence returns a sanitized 503.

Detail responses preserve historical statuses and evidence. NOT_COMPARABLE, INSUFFICIENT_EVIDENCE and UNRESOLVED are not upgraded to success or root cause. Stored request/result data is intended for the authenticated operator; do not expose this local service publicly. Evidence browsing does not imply current cloud freshness or exact snapshot comparability.

Six tests cover authentication, real HTTP delivery, read-only SQLite, bounded pagination, invalid IDs, missing stores, sanitized errors and preserved statuses. A local HTTP smoke check retrieved run `203157aa-0ccd-4bca-9188-1111191c8cc1` from the actual evidence store: all five totals and graph references were preserved, with NOT_COMPARABLE intact and zero cloud queries. The temporary verification server was stopped. Ticket intake and asynchronous investigation execution remain separate next steps.
