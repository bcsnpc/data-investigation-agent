# Local replay API

Round 28A's narrowed API is local and replay-only. It is not deployed and cannot
fall back to live data or a model. The WSGI factory is
`investigator.investigation_api.create_app(service, auth, port=...)`.
Bind it to `127.0.0.1` using `wsgiref.simple_server.make_server`.

Every request, including health, requires `Authorization: Bearer <token>`.
`TokenAuth.from_secret_store` accepts an installed resolver plus vault/secret names;
the value stays in memory. Tests use a random ephemeral memory token. No API secret
was provisioned in this round. Authentication also declares the permitted estates
and requester; the submitted requester must match. No data identity is impersonated.

```http
POST /v1/investigations
Content-Type: application/json
Authorization: Bearer <token>

{"estate_id":"practice-fixture","requester":"reviewer","text":"Why is this number different?","report":"Example report","page":"Summary","visual":"Count"}
```

Returns `202` with `case_id` and `status_url`. Optional `screenshot` is base64 PNG/JPEG.
For replay, all ticket fields must match a preinstalled saved request exactly.

| Endpoint | Response |
| --- | --- |
| `POST /v1/investigations` | Case ID; exact saved replay runs locally. |
| `GET /v1/investigations/{id}` | `status`, `mode`, `result_url`. |
| `GET /v1/investigations/{id}/result` | Saved delivery result: verdict, explanation, evidence summary and handoff. |
| `GET /v1/health` | Health, `mode: REPLAY`, `live_enabled: false`. |

`ReplayEngine` takes explicitly installed `{request, result}` records. `Service`
validates the estate registry, persists private cases and writes each access to
`audit.jsonl` and a case/access file. It records no auth headers or query strings.
An unavailable saved request produces a recorded failure, not a generated answer.
Results are scoped to the authenticated requester and estate. Keep this private
case directory outside the repository. Schema and examples: `openapi.yaml`.

No public ingress, live execution endpoint, catalog/evidence endpoint or new connector
is included in the narrowed scope. Owner action: **approve API ingress on Azure**
and provision a named API secret before any future deployment; neither is done here.
