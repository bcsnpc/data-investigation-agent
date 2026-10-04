# Declared load audit source

2026-10-04 UTC. Part B implementation checkpoint; no new investigation run.

An estate may declare `load_audits`, with delivery, producer and audit asset
identities. The declaration contains no query, metric, expected value or
platform-specific route. There is one source per delivery; duplicates refuse.

The Microsoft adapter reads the configured audit first for that delivery. It
requires current discovered assets and column types, the independent reader
endpoint, compiler-governed SQL, existing read-only guards and query-bound
identity/engine/object attestation. It records the row's own run ID, start/end,
rows read/written and high watermark without recounting. A missing watermark
stays missing. Matching counters do not establish current source completeness.

Failed, running, ambiguous or malformed runs, missing counters and unobserved
copy-output accounting return unavailable. They never produce CURRENT. When an
audit is declared, a missing/unsupported/unreadable audit does not silently
substitute monitoring or retained history. Without an audit declaration, the
existing retained run-history path remains. An empty monitoring result is not
positive completion evidence.

This does not yet implement the source-delivery divergence outcome producers.
LOAD_LATENCY still needs the source-change comparison; INGESTION_GAP needs
independent membership/version evidence and successful delivery accounting.
Neither is certified by 360/360 alone. Source-boundary runs and the configured
unreachable-source narrative remain pending.

Six new audit tests cover hostile completion/counter states, ambiguous runs,
unique identity-only declarations, no silent fallback, missing physical schema
and mismatched reader attestation. Together with retained job history, source
connection, application quantity, flexible investigation and runtime tests,
**81 tests passed**. The previous failed-job regression now supplies the adapter
configuration dependency explicitly; its failed-job refusal assertion remains.

No planner payload content is added by this consumer. The source connection
golden-view regression still requires byte-identical directory coverage and
payload (28 entries, 11 SQL objects, 5,543 characters). New audit observations
will remain original receipts, not reconstructed summaries. Prior engine freezes
are invalidated. No cloud request, fixture change or ledger run in this
implementation checkpoint. Current configuration/recollection remains separate.
