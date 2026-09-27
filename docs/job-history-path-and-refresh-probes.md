# Retained job completion, fixed path narrative and refresh-access probes

2026-09-27. PR #272 merged after all six checks passed at `1dde6cc`.
This change invalidates earlier engine freezes. No new freeze, variant or live
investigation was run. Only the two explicitly requested metadata probes ran.

## Retained job history

The prior adapter treated any truthy detail as CURRENT, including an error object
or failed job. It now requires an AVAILABLE list response, selects the latest run
by its UTC start, and requires Completed, a valid completion timestamp not before
start, and no failureReason. An older success cannot hide a newer failure.
Ambiguous latest runs, malformed/error responses and missing timestamps remain
UNAVAILABLE. Distinct run_state values are SUCCEEDED, FAILED, IN_PROGRESS,
NOT_RUN and UNKNOWN. No retained runs means NOT_RUN within that retained response,
not proof that the job never ran historically. A missing transformation binding
remains NOT_APPLICABLE. Raw retained history and context version stay attached.

CURRENT now means only successful retained completion, explicitly not freshness.
No timestamp-to-SLA comparison, LATENT branch or ingestion-gap detector was added.
Tests include adapter-level Failed -> UNAVAILABLE, old-success/new-failure,
progress/empty/unsupported states and invalid completion evidence.

## Fixed technical path account

The technical narrative can no longer invent a factual paragraph about path
ordering. Its bounded text is an exact schema enum rendered from procedure facts
and supported operation vocabulary. The engine appends a fixed boundary account:
upstream input -> downstream output, the verified quantities and comparison result,
plus a mapping from short L terms to the original layer identities. The same
original comparison fields and receipt references drive this account; the model
cannot choose or exchange upper/lower labels. Business wording remains unchanged.

Additional limitation wording is also fixed; all original mandatory limitations
and the judge's interpretation remain separately preserved in the evidence/output
record. This deliberately avoids a synonym blacklist pretending to detect every
possible reversal in free prose. Contradictory text, including the recorded
"higher upstream total", fails the wire schema. No prose is silently rewritten.
The independently model-authored technical paragraph is replaced by the fixed
account; this is an explicit contract change, not a claim that free prose has
become semantically reliable. No new live narrative evaluation was requested.

## Context and validation

Focused tests: 24 passed. All 1,260 local regression tests passed in 403.575 seconds.
The saved R2 synthesis digest remains 14,386 characters, directory entries0 ->0
and SQL objects0 ->0 (this digest has no directory). Schema characters increase
2,782 ->3,234. A separate28-entry directory fixture remains byte-equivalent after
schema construction. Output facts are appended deterministically, like surface
attestation, rather than consuming directory capacity. Tests reject reversed
ordering, changed quantities and inverted additional limitations.

## XMLA probe: one query

Identity investigator-reader@skynwhy.com was checked against the configured token
account, tenant, audience and principal. The existing isolated MSAL session and
ADOMD client were used. No grant, consent, fallback identity or retry was used.
The connection succeeded; ExecuteReader was refused at query stage.

The [documented partition rowset](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/a1c6e9bb-9422-4f12-95a0-2fad880f61cd)
contains TableID, ModifiedTime and RefreshedTime. This one query asks for timing
per partition with its parent TableID; no partition/table timing was returned:

```sql
SELECT [TableID], [Name], [ModifiedTime], [RefreshedTime], [State] FROM $SYSTEM.TMSCHEMA_PARTITIONS
```

Exact service exception (inner message):

```text
User '<euii>investigator-reader@skynwhy.com</euii>' needs to be an administrator to read the metadata of the database '3484a2bc-98c5-4cef-be5c-a6215484075e'.



Technical Details:

RootActivityId: cb7aaeeb-1ee3-424c-b04f-92e7074f1a50

Date (UTC): 9/27/2026 6:36:40 PM
```

This demonstrates refusal of the tested TMSCHEMA metadata route on this model.
It does not say XMLA data queries are inaccessible or enumerate every DMV.

## REST probe: one request

GET `https://api.powerbi.com/v1.0/myorg/groups/149f8d99-1c66-4a0a-9624-759be002bb60/datasets/3484a2bc-98c5-4cef-be5c-a6215484075e/refreshes?$top=1`

HTTP403. Exact response:

```json
{"error":{"code":"Unauthorized","message":"Api accessed by user <eupi>8a582d2a-ecb4-4320-bf72-75a529a0d382</eupi> with insufficient privileges. request is unauthorized, identity None."}}
```

RequestId: `18fefbfc-e00b-48dd-b9a1-231bad466158`.
Microsoft's [refresh-history endpoint documentation](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/get-refresh-history-in-group)
requires dataset Write permission, separately from the accepted delegated OAuth
scopes. The reader's refusal is consistent with that requirement.

Neither route supplied timestamps. There is therefore no newly demonstrated
reader refresh-timing capability and no REFRESH_LATENCY implementation. Even
successful timestamps would still need an evidence-backed comparison before
establishing lateness.

Both calls are separately authorized CAPABILITY_AUDIT ledger entries (two metadata
reads, zero investigation calls). The standing policy remains60; no standing or
batch increase was applied. Original runs and receipts remain unchanged.
[Full probe receipts and offline context measurement](runs/job-history-path-refresh-audit.json).

Offline assembly of saved R2 also validated without modifying the original session or calling a provider. The rendered second boundary is L2 (upstream input), 7,661 -> L1 (downstream output), 8,765. This is a renderer check, not a new investigation or live acceptance result.
