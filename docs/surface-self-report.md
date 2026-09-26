# Surface self-report (item 2a)

Updated 2026-09-26. This is item 2a: the invariant, the transport and a probe. No
lower-layer quantity is compiled, and `evaluate()` still has no path that reads
the Gold endpoint. That is item 2b.

**Engine bytes changed.** The fingerprint moved from `unfrozen-e3b2724a5c50` to
`unfrozen-a841e4860b0a`. No freeze exists, so none is invalidated, but any
earlier engine tag no longer describes this code.

## The invariant

An execution surface is established by the surface's own answer, not by the
client's belief about it. In the two near-misses of 2026-09-26, nothing lied and
nothing checked:
- a connection labelled `gold` opened Bronze because it named no database;
- receipts labelled `ISOLATED_METADATA` were made by the tenant administrator.

`process_debugging.attest()` is now applied to every probe `vertical()` receives.
A probe that claims a surface must carry a `surface_report`: the surface's own
answer, which must include `identity`. The rules:
- **Missing report:** a probe without one becomes `UNAVAILABLE` with
  `SURFACE_SELF_REPORT_MISSING`.
- **Contradiction:** any reported field that differs from the declared surface
  (case-insensitively) makes the probe `UNAVAILABLE` with
  `SURFACE_SELF_REPORT_CONTRADICTS_DECLARED`, and each contradiction is recorded.
  Such a probe is never `OBSERVED`, whatever its values.
- **No declared identity:** a probe that declares no identity cannot be attested
  and becomes `UNAVAILABLE` with `SURFACE_IDENTITY_NOT_DECLARED`.
- **Unattested fields:** declared fields the surface did not report are listed
  as `unattested_fields` in the receipt, never silently treated as confirmed.

The engine knows nothing about how a surface answers; the adapter supplies the
report. The admission path (`flexible_tools`) can request self-report columns.
It separates them from the values and seals them into the receipt as
`surface_report`. Values compared across layers therefore never include them.

## How each surface answers

| Surface | Self-report | Attested | Not attested |
| --- | --- | --- | --- |
| Power BI semantic model (DAX) | `USERPRINCIPALNAME()`, added as a column to the baseline query and admitted by the DAX compiler | identity | object: Power BI does not report which model served the query. Also engine and connection. |
| Fabric SQL analytics endpoint | `SUSER_SNAME()` and `DB_NAME()`, in the same connection | identity, object (database) | engine, connection |

## Transport

- **Parameterised auth.** `scripts/fabric_sql_auth.py` no longer hardcodes an
  account or profile. Both come from configuration: `fabric.sql_session` for the
  publisher session, and `fabric.sql_reader` for the least-privilege reader.
  - Profiles must be relative paths under `.local/`, and the two profiles must
    differ.
  - A profile holding another account, or another tenant, is refused before any
    token is requested. The tenant and audience checks are kept.
  - A missing or expired session raises `SignInRequired`, naming the account and
    profile. A reader session never falls back to the publisher session.
- **Self-report only.** `scripts/fabric_sql_surface.py` and
  `infra/scripts/Read-FabricSqlSurface.ps1` ask the endpoint who it is serving
  and which database. They accept no query text, and refuse any request field
  other than server, database and token. Data reads will go through the
  compile-and-admit path in 2b.
- **The database is always named.** It is required before a token is requested
  or a connection opened. For the probe it comes from the discovered binding:
  the resolved `declared_source` layer's `declared_connection_asset_id` is a
  `SQLEndpoint` asset, and its name is used. Configuration never supplies it. A
  test requires every repository SQL connection script to set `Initial Catalog`.
- **Honest capability.** The adapter declares `independent_lower_surface` only
  when a local, network-free session check reports the configured reader
  `READY`. Otherwise `capability_gaps()` states why, naming the sign-in required.
  No procedure step consumes this capability yet.
- **Existing callers.** The development configuration now carries the publisher
  session in `fabric.sql_session`. `connect_fabric_sql.py` takes
  `--session sql_session|sql_reader`, and the cross-layer worker passes the
  configured account and profile.

## Probe: 2026-09-26, 21:01:32–21:02:03 UTC

Run with `scripts/probe_fabric_sql_surface.py`: environment `unknown-domain-v4`,
model `5b3eff46…`, the G presentation measure. Two metered cloud reads.

| Probe | Result |
| --- | --- |
| Fabric SQL self-report | **`OBSERVED`, attestation `MATCHED`.** The declared surface was `FABRIC_SQL` on the `…-tggz6fdgdqfevfreown6aav3ma…` host, database `warehouse_gold_e1b8e1`, identity `investigator-reader@skynwhy.com`. The database came from the discovered endpoint asset `77c49180…`, whose binding is `DECLARED_BY_DEFINITION`. The endpoint reported identity `investigator-reader@skynwhy.com` and object `warehouse_gold_e1b8e1`. |
| DAX self-report | **`UNAVAILABLE`.** The read did not complete: sealed receipt `12761c25…` is `INTERRUPTED` with `TimeoutError`, so no self-report was obtained. |

The reader session was `READY`, and `independent_lower_surface` was declared.

**Why the DAX read failed.** Three further metered diagnostic reads, capturing
only HTTP status and error codes, showed the following:
- Power BI returned HTTP 400 `DatasetExecuteQueriesError`, with Analysis Services
  error `3242524690` (`0xC1450012`).
- It returned the same error for the unchanged baseline query **without**
  `USERPRINCIPALNAME()`, which completed at 01:25 UTC the same day.
- So the Power BI surface was failing the unchanged query at the time. The
  self-report change is not shown to be the cause.
- The adapter labelled the rejection "completion uncertain" (`TimeoutError`)
  because the native worker treats every `URLError`, including an HTTP 400, as
  uncertain. That labelling is left unchanged here, and recorded.

## What is established and what is not

**Established:**
- The engine refuses a probe whose surface does not report on itself, or whose
  report contradicts the declaration. Tests show this, and they fail when the
  invariant is removed.
- As the least-privilege reader, the Gold Fabric SQL endpoint reports the
  intended identity and database through the new transport.

**Not established:**
- **The live DAX self-report:** `USERPRINCIPALNAME()` in the baseline query has
  not returned a live answer through this path, because the Power BI surface
  failed during the run. It is verified only against the test fixture, together
  with the earlier reader check that used the same function.
- **The Power BI failure:** the cause of error `0xC1450012` is not established.
- **Surface independence:** the DAX surface's object is not attested, and no
  surface attests its engine or connection.
- **Data reads:** no table has been read through the Fabric SQL surface, and no
  explicit `DENY` has been checked.
- **Viewer scope:** Viewer remains broader than needed.

## Configuration change

`.local/unknown-domain-v4/config.json` gained `fabric.sql_reader`: the reader
account, `.local/azure-reader-sql`, and the `…-tggz6fdg…` host. Nothing else
changed. SHA-256 before `1476f125…`, after `f45b3efa…`. The prior file is kept
locally as `config.before-sql-reader-20260926.json`.

## Update 2026-09-26: attestation is consumed, not only recorded

Review of #240 found that `unattested_fields` was written into each receipt and
read by nothing. A probe could therefore be `MATCHED` on identity alone while its
database went unattested and unremarked. That is the Bronze-instead-of-Gold
failure with a green light on it. The sections above are kept as written.

What changed:
- **Reportable fields must be reported.** A probe declares which surface fields
  it is able to report (`Probe.surface_reportable`), and `attest()` requires
  every one of them. The Fabric SQL surface can report `identity` and `object`;
  the DAX surface can report only `identity`. So a lower surface that could name
  its database and did not is `UNAVAILABLE`, not `MATCHED`. `object` is not
  required globally, because Power BI cannot report which model served a query.
- **Unattested fields travel with the claim.** Every field of a compared surface
  that its surface did not report is named in the claim's limits and in both
  outputs as `unattested_surface_fields`.
- **Validation backstop.** Outcome validation refuses a boundary comparison
  without a `MATCHED` attestation on both sides. It also refuses a claim whose
  limits or outputs omit an unattested field.
- **Status history kept.** A failed attestation still turns a `NOT_COMPARABLE`
  probe into `UNAVAILABLE`, deliberately: untrusted outranks incomparable. The
  prior status is kept as `status_before_attestation`.
- **Gap report fixed.** `capability_gaps()` no longer raises `KeyError` on a
  sign-in-required status that lacks an account or profile.

Engine bytes changed: `unfrozen-a841e4860b0a` becomes `unfrozen-ba201bbc0cd9`.
No run was performed for this change.
