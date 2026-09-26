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

## Live verification, 2026-09-26 22:40 UTC: a real masked failure, unmasked by the engine

The "Not established" section above is kept as written. This section records
what has since been established.

### What was installed and configured (authorised)

- **Package:** Microsoft's NuGet package `Microsoft.AnalysisServices.AdomdClient`
  **19.117.0**, the latest stable release, from nuget.org.
  - Authors: Microsoft.
  - `.nupkg` SHA-256: `94b2455d57447c72…`.
  - Extracted under `.local/adomd-client/19.117.0/`, which is not committed.
- **Assembly used:** `lib/net472/Microsoft.AnalysisServices.AdomdClient.dll`,
  because Windows PowerShell 5.1 runs on .NET Framework.
  - File version 17.0.91.17.
  - Authenticode signature valid, from Microsoft Corporation.
  - SHA-256: `1e75c2fd6b7a4f19…`.
- **Declared dependency not installed:** the package declares a dependency on
  `Microsoft.Identity.Client` (MSAL.NET). It is not needed for token
  authentication, and it was not installed.
- **Configuration:** `.local/unknown-domain-v4/config.json` gained
  `fabric.xmla_client.library`, pointing at that DLL. SHA-256 before
  `f45b3efa…`, after `4362a6c7…`; the prior file is kept locally.
- **Defect found and fixed during installation:** `Add-Type -Path` fails on this
  library with `ReflectionTypeLoadException`, because it eagerly resolves types
  that need MSAL. The script now loads the assembly lazily, and a client that
  cannot load is reported `UNAVAILABLE` at stage `client`, never as a captured
  surface error. This was fixed in #247 before it merged.

### The run

Session `specific-failure-verification-20260926T224029Z`, 22:40:29–22:40:47 UTC.
It ran as the reader, against the failing Direct Lake model (`3484a2bc…`, the
G presentation layer), through the engine's per-probe path: `evaluate()`, then
`attest()`, then `refine_failure()`, exactly as `vertical()` applies them. Two
metered reads, both settled as certain.

| | Result |
| --- | --- |
| Execute Queries | HTTP 400, `DatasetExecuteQueriesError`. Classified `GENERIC` by the adapter. |
| Sealed receipt `46cee4f7…` | `FAILED`, `error_type: NativeRejected`, `http_status: 400`, `service_error_code: DatasetExecuteQueriesError`. After #242, this is no longer `INTERRUPTED`/`TimeoutError`. |
| Refinement via XMLA | `OBTAINED`: `ERROR_CAPTURED`, codes **`AdalGrantHasExpiredDueToPasswordChangeErrorCode`, `AADSTS50173`** |
| Probe | Still `UNAVAILABLE`. Reason: "The presentation reader could not establish a baseline. Most specific failure via XMLA: AdalGrantHasExpiredDueToPasswordChangeErrorCode, AADSTS50173." |
| Output entry (`failures`) | Generic `DatasetExecuteQueriesError`; specific via XMLA: `AdalGrantHasExpiredDueToPasswordChangeErrorCode`, `AADSTS50173` |

The engine obtained the same error that the independent investigation had
found by hand, without a human in the loop.

### What is established, and what is not

- **Established:** a real failure that one interface masked was unmasked by the
  engine, through the adapter's second interface to the same surface. The
  specific codes reach the probe reason, the failure record and both outputs.
  Only codes were extracted; no message text was stored.
- **Not established: the specific error in a sealed receipt.** The sealed
  receipt is the Execute Queries one, and it carries only the generic error.
  The XMLA result is not itself sealed as a receipt. The specific codes live in
  the probe's failure record and outputs, which are derived evidence. Sealing
  the refinement as its own receipt would close this.
- **Not verified here:** the rest of `vertical()` beyond the per-probe path.
  That path was exercised through the same functions, not as a full
  investigation.
