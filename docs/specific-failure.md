# Prefer the most specific failure the surface can give

Updated 2026-09-26. Engine change: the fingerprint moves to
`unfrozen-789b25653c0c`. No freeze existed.

## Why

On 2026-09-26, Power BI refused the reader on Direct Lake models. Execute
Queries reported only the generic `DatasetExecuteQueriesError`, with Analysis
Services `0xC1450012`. Working from that generic error, a full day went into
hypotheses: capacity, client session, OneLake access. Each was wrong.

The real error, `AADSTS50173` on a stored service-side grant, was available all
along from the XMLA interface to the same model. See
[Power BI reader rejection](power-bi-reader-rejection.md). Any estate can mask a
failure this way.

## The rule (engine, domain-generic)

When a read fails with an error the surface reports only generically, the
adapter should try to obtain a more specific failure from another interface to
the same surface before the probe is reported `UNAVAILABLE`. The specific error
is then carried into the evidence.

`process_debugging.refine_failure()` is applied centrally, after `attest()`, to
every probe that `vertical()` receives:
- **When it applies:** only to an `UNAVAILABLE` probe whose adapter-supplied
  `failure` is marked `GENERIC`. A `SPECIFIC` failure, or an `UNCERTAIN` one
  (completion unknown), is left alone.
- **When the adapter declares `failure_detail`:** the engine calls
  `adapter.failure_detail(layer, probe)`. If that returns a `SPECIFIC` failure
  with codes, the probe's reason is extended with the most specific failure,
  its interface and codes. The generic failure is kept alongside it.
- **Never upgraded:** the status never changes. An `UNAVAILABLE` probe stays
  `UNAVAILABLE`.
- **When it does not work:** an undeclared capability, a second interface that
  itself fails, or one that returns no codes are each recorded on the failure
  (`NOT_DECLARED`, `FAILED` with the error type, `NO_SPECIFIC_FAILURE`). They
  never replace the generic failure.
- **Where it appears:** every `UNAVAILABLE` probe's failure is listed in both
  outputs as `failures`, with generic and specific codes. The baseline reason
  carries the specific failure.

The engine knows nothing about which interfaces exist; that is the adapter's
business.

## The Microsoft adapter

- **Classification:** Execute Queries failures are classified by the adapter.
  - `GENERIC`: `DatasetExecuteQueriesError`.
  - `UNCERTAIN`: an interrupted read.
  - `SPECIFIC`: anything else.

  The failure carries the failed receipt's ID, its HTTP status and its service
  error code.
- **The second interface:** `failure_detail()` re-issues the same
  already-admitted query through **XMLA** to the same model. The workspace and
  model are addressed by their discovered names, never by configured names.
- **Codes only:** `scripts/read_xmla_failure.py` and
  `infra/scripts/Read-XmlaFailure.ps1` run as the configured reader. They reduce
  the XMLA error to codes (`AADSTS…`, `…ErrorCode` names, `0x…` engine codes).
  The message text crosses the process pipe only; it is never returned or
  stored.
- **Honest capability:** `failure_detail` is declared only when
  `fabric.xmla_client.library` names an ADOMD.NET client library under
  `.local/` and a native reader is configured. Otherwise
  `capability_gaps()` says why.

## Not established

- **Not verified live.** No ADOMD.NET client library is installed on this
  machine, so the XMLA path has not run end to end here. It is covered by tests
  with a simulated transport. Two things are therefore unconfirmed:
  - Whether the token-in-password connection string authenticates as intended.
  - Whether the reader's XMLA error carries the codes as the independent
    investigation reported.
- **Metering:** the XMLA re-issue is metered as a cloud read.
