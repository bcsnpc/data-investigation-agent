# Storage SDK dispatch boundary correction

2026-10-13 UTC / 2026-10-12 America/Chicago. Offline audit, zero cloud calls.

The installed Azure Storage SDK's `StorageAccountHostsMixin._create_pipeline`
builds an explicit policy list; it does not consume `per_call_policies`.
Consequently that argument in the owner-local `archive-next-eight.py` and
`publish-pilot-cas.py`, and in the initial repository Blob adapters, did not
establish the intended gateway boundary. Absence of `controls.jsonl` was a real
defect, not proof of zero requests. Prior actual calls must be recorded as lacking
that dispatch journal; expected operation counts cannot replace physical counts.

The supported `transport=` argument is now a `GuardedTransport` wrapper. At every
SDK physical send (including retries/redirect attempts), it checks the exact
method and URL against the explicit channel, fsyncs a DISPATCHED control record,
then delegates to RequestsTransport. The latter disables automatic redirects.
Responses and exceptions get a second record sharing the attempt ID. Only
DISPATCHED records count requests; an unresolved attempt remains conservatively
charged. Authentication headers, bodies and exception messages are never logged.
The query-free URL and SHA-256 of the full requested URL permit route correlation
without writing a query credential. Failure to write the initial record prevents
send. MSI token acquisition remains the already documented authentication-plane
exception, not a Blob artifact request.

Owner operator scripts must replace the ignored hook explicitly, for example:

```python
from investigator.adapters.guarded_transport import GuardedTransport
transport = GuardedTransport(gateway, 'owner-archive', receipts=controls_path)
client = ContainerClient(account_url, 'archive', credential=existing_key_in_memory,
                         transport=transport, retry_total=0)
```

No local operator script was changed or executed by this helper. The same wrapper
works for BlobClient.from_blob_url. The default journal is the explicit
DIA_PLATFORM_CONTROL_RECEIPTS path or `.local/platform-control-requests.jsonl`;
operators should supply the round-specific path. Regression uses the real Blob
SDK with a fake transport: successful dispatch, retried 503, gateway denial,
receipt disk failure, changed redirect target and ConnectionResetError. No live
endpoint is contacted.

The archive adapter retains overwrite=False. If the SDK reports an existing
object, that only skips upload: publication still requires a Hot object, complete
download/decompression matching original SHA and size, an unchanged ETag, and a
conditional Archive transition. Existing corrupt or already-Archive objects are
refused. An existing Archive object requires its earlier verified receipt; this
change does not auto-rehydrate or pretend that its bytes were checked anew.
Each fully verified Archive object can now be checkpointed. The CLI fsyncs these
to `<output>.progress.jsonl` before attempting the next object. These rows preserve
completed work on a later failure; they are not automatically trusted resume
instructions, nor permission to overwrite, delete or accept an incomplete file.

The engine identity-producer ratchet now explicitly admits only
`adapters/guarded_transport.py` as another private correlation namespace. It is
not disguised through an alternate randomness API. A regression runs an SDK
request while an engine tape is active: the platform journal identifier consumes
no engine identity, emits no tape event and is absent from the SDK result. This
keeps control receipt IDs independent without weakening deterministic result IDs.
