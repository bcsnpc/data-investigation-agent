# Private recording authority for newly computed content addresses

DECIDED WITHOUT REVIEW — 2026-10-13 UTC: apply the owner's existing permission
to write the tool's private recording containers through a code-owned,
one-object CAS binding. Rejected alternative: broad HTTP wildcard permission or
disabling the SDK gateway until future chunk hashes are known. No estate scope,
principal, role, credential or budget changes are made by this implementation.

The operator policy declares the fixed storage account and private container:

```json
{
  "role":"platform",
  "platform_cas":[
    {"account_url":"https://<account>.blob.core.windows.net","container":"snapshots"},
    {"account_url":"https://<account>.blob.core.windows.net","container":"tapes"}
  ]
}
```

Place this under the existing recording channel(s) in `identities`. Use the exact
approved account; only snapshots, tapes, captures and screenshots are accepted.
No wildcard is accepted. This declaration alone cannot issue an HTTP request.

The internal recorder validates a `chunks/<sha256>` or `files/<sha256>` key and
binds one exact URL immediately before invoking the SDK. A chunk PUT requires
bounded gzip expansion matching the content hash. A file manifest PUT must pass
the existing manifest identity, chunk and byte-total checks. Its serialized bytes
are separately hashed for transport binding. PUT is capped at 4 MiB, must carry
those identical bytes, `If-None-Match: *` and BlockBlob type. GET can address only
the currently bound object. The binding expires after that operation, including
error paths. Restoration retains the existing complete content-hash checks.

The final SDK transport still checks the kill switch, logical platform identity,
exact URL, method, headers and body before every physical request, then journals
dispatch and completion. Different account/container/key, query string, listing,
DELETE, HEAD, block upload control route or changed PUT content is refused. The
SDK has no automatic retry; archive code's separate explicit routes are unchanged.

This is internal platform persistence authority. No model or investigation tool
can call the binder, select a platform channel or request a CAS upload. The Python
application is the trusted boundary; this is not an OS sandbox against arbitrary
code already executing inside the worker. Existing exact HTTP grants remain
exact grants, independently of CAS authority.
