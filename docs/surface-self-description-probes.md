# Least-privilege surface self-description probes

2026-10-02, America/Chicago. Report and proposal only; no attestation wiring or
standard change. [Retrospective corrections](retrospective-surface-attestation.md)
merged in #300 as `d509e6f550c10fb2b12b97e8a9d12860436f9a4e` after all six checks
passed. The document is on project `main` and is also present, with matching
bytes, at `D:\data_investigation_agent\docs\retrospective-surface-attestation.md`.
The project checkout has existing user code edits; its branch and those edits
were not overwritten to materialize the report.

## Finding

**These routes can report more than the adapter asks for.** The SQL surface
reported its engine, version, session and network/protocol information. Both
REST/DAX and XMLA served semantic engine descriptors, server name and catalog
through properties accessible to the existing reader. My previous claim that
these reader routes cannot report engine/connection/object information was
too broad. The old receipts remain partial because they did not ask for it;
new knowledge does not retroactively complete them.

The shared account was `investigator-reader@skynwhy.com`. The SQL request used
its existing isolated Azure CLI profile; REST/DAX and XMLA used its existing
reader MSAL cache. Both token identities were checked against the configured
principal before querying. No interactive elevation, publisher identity, grant,
app registration, audience/scope addition, refresh, reframe or fixture change.

The [complete receipt set](runs/surface-self-description-probes.json) contains
every exact query, response, request/activity identifier and response/receipt
hash, including empty results and failures. All thirteen receipt hashes were
recomputed locally. These are audit receipt hashes, not a provider signature
and not existing investigation-store receipt seals.

## SQL analytics endpoint: three requests

Target: configured Gold endpoint and `warehouse_gold_e1b8e1`. Each request
opened an encrypted read-only-intent connection and dispatched one fixed SELECT.
No table data was read. Authentication/connection handshakes are excluded from
the existing query-request allowance, as elsewhere in its accounting.

### Engine

```sql
SELECT @@VERSION AS engine_version,
       SERVERPROPERTY('Edition') AS edition,
       SERVERPROPERTY('ProductVersion') AS product_version,
       SUSER_SNAME() AS reader_identity, DB_NAME() AS database_name
```

SERVED; one row:

```text
engine_version = Microsoft Azure SQL Data Warehouse (RTM) - 12.0.2000.8
                  Sep 16 2026 10:25:05
                  Copyright (C) 2026 Microsoft Corporation
edition = SQL Azure
product_version = 12.0.2000.8
reader_identity = investigator-reader@skynwhy.com
database_name = warehouse_gold_e1b8e1
```

Receipt: `sql-engine`.

### Connection/session

```sql
SELECT @@SPID AS session_spid,
       CONNECTIONPROPERTY('local_net_address') AS local_net_address,
       CONNECTIONPROPERTY('protocol_type') AS protocol_type,
       SUSER_SNAME() AS reader_identity, DB_NAME() AS database_name
```

SERVED; one row: session_spid **146**, local_net_address **10.0.0.9**,
protocol_type **TSQL**, reader_identity `investigator-reader@skynwhy.com`,
database_name `warehouse_gold_e1b8e1`. Receipt: `sql-connection`.

```sql
SELECT SESSION_ID() AS session_id
```

Refused as unsupported syntax/function, not permission: SQL error **195**,
exact inner message:

> 'SESSION_ID' is not a recognized built-in function name.

The outer exception is `MethodInvocationException`, wrapping ExecuteReader.
Receipt: `sql-session-id`. @@SPID succeeded; this alternative failed and was
not retried or replaced in the record.

## Semantic surface: REST/DAX and XMLA separately

Target model `3484a2bc-98c5-4cef-be5c-a6215484075e`; XMLA used the discovered
workspace/model names. These are metadata/self-description probes, not measure
comparisons, ticket investigations or synthesis runs.

### Initial engine-property queries: empty, not denied

REST Execute Queries:

```dax
EVALUATE SELECTCOLUMNS(
    FILTER(INFO.PROPERTIES(), [PropertyName] = "ProductName" || [PropertyName] = "ProductVersion"),
    "PropertyName", [PropertyName], "Value", [Value])
```

HTTP200, exact result `{"results":[{"tables":[{"rows":[]}]}]}`.
Receipt `rest-dax-properties`, RequestId `01befa00-8d1a-4100-b62a-5a13e2234b5b`.

XMLA:

```sql
SELECT [PropertyName], [Value] FROM $SYSTEM.DISCOVER_PROPERTIES
WHERE [PropertyName] = 'ProductName' OR [PropertyName] = 'ProductVersion'
```

SERVED, zero rows, no truncation. Receipt `xmla-properties`.
The same DAX query above through XMLA also returned zero rows, no truncation:
receipt `xmla-dax-properties`. Three empty results were retained. They did not
establish missing permission or missing engine metadata; those property names
were absent from the subsequently enumerated rowset.

### Identity control via REST/DAX

```dax
EVALUATE ROW("reader_identity", USERPRINCIPALNAME())
```

HTTP200: `[reader_identity] = investigator-reader@skynwhy.com`.
Receipt `rest-dax-identity`, RequestId `1f9512f0-b082-410c-bcb5-fe20de3d0919`.

### XMLA sessions: permission refusal

```sql
SELECT TOP 10 [SESSION_ID], [SESSION_SPID], [SESSION_CONNECTION_ID],
              [SESSION_USER_NAME], [SESSION_CURRENT_DATABASE]
FROM $SYSTEM.DISCOVER_SESSIONS
```

Receipt `xmla-sessions`, stage query, `MethodInvocationException` while reading.
Exact server exception:

```text
The '<euii>investigator-reader@skynwhy.com</euii>' user does not have permission to call the Discover method.

Technical Details:
RootActivityId: 664a981f-746e-439b-bbb4-22599e3b9a2f
Date (UTC): 10/2/2026 5:46:23 AM
```

### XMLA connections: permission refusal

```sql
SELECT TOP 10 [CONNECTION_ID], [CONNECTION_HOST_NAME], [CONNECTION_USER_NAME]
FROM $SYSTEM.DISCOVER_CONNECTIONS
```

Receipt `xmla-connections`, stage query, `MethodInvocationException` at ExecuteReader.
Exact server exception:

```text
The '<euii>investigator-reader@skynwhy.com</euii>' user does not have permission to call the Discover method.

Technical Details:
RootActivityId: 8505d086-c37b-41c6-ba1d-5a7155bb6bcb
Date (UTC): 10/2/2026 5:46:28 AM
```

These calls establish refusal for this reader, not the precise minimum role
that would grant access. No elevation was pursued. There is no documented
DAX INFO.SESSIONS/INFO.CONNECTIONS counterpart in Microsoft's current
[INFO function inventory](https://learn.microsoft.com/en-us/dax/info-functions-dax).
I did not fabricate functions or send SQL DMV syntax as a DAX query and call
the resulting grammar error a permission finding.

### Discover the actual property names

Two additional queries, retaining all original empty results:

```sql
SELECT [PropertyName] FROM $SYSTEM.DISCOVER_PROPERTIES
```

```dax
EVALUATE SELECTCOLUMNS(INFO.PROPERTIES(), "PropertyName", [PropertyName])
```

Both served the property-name inventory. The complete returned inventories
are in receipts `xmla-property-names` and `rest-dax-property-names`; REST
RequestId `58ee263e-22cb-4a63-a0ec-b294b81a1adc`. Relevant returned names were
Catalog, ProviderName, ProviderVersion, DBMSVersion and ServerName.
ProductName/ProductVersion were not listed. Only names were requested here;
password/authentication property values were neither requested nor collected.

### Ask for those descriptors: both interfaces succeed

```sql
SELECT [PropertyName], [Value] FROM $SYSTEM.DISCOVER_PROPERTIES
WHERE [PropertyName] = 'Catalog' OR [PropertyName] = 'ProviderName'
   OR [PropertyName] = 'ProviderVersion' OR [PropertyName] = 'DBMSVersion'
   OR [PropertyName] = 'ServerName'
```

```dax
EVALUATE SELECTCOLUMNS(
    FILTER(INFO.PROPERTIES(), [PropertyName] = "Catalog" || [PropertyName] = "ProviderName"
        || [PropertyName] = "ProviderVersion" || [PropertyName] = "DBMSVersion"
        || [PropertyName] = "ServerName"),
    "PropertyName", [PropertyName], "Value", [Value])
```

| Property | REST/DAX returned | XMLA returned |
| --- | --- | --- |
| Catalog | `3484a2bc-98c5-4cef-be5c-a6215484075e` | `Warehouse Operations e1b8e1` |
| ProviderName | `OLAP Server` | `OLAP Server` |
| ProviderVersion | `17.0.91.20` | `17.0.91.20` |
| DBMSVersion | `17.0.91.20` | `17.0.91.20` |
| ServerName | `host002_datasets-023` | `host002_datasets-023` |

Receipts `xmla-engine-descriptors` and `rest-dax-engine-descriptors`.
REST HTTP200, RequestId `b5dc4ee8-c625-4c5e-bc07-f98beeb35ac8`; XMLA SERVED,
five rows, no truncation. These are values in server query results, not a
client-library ProductVersion getter or a client-selected URL relabelled as
server attestation. Catalog's different representation across interfaces
must remain explicit; a model name is not silently treated as a GUID.

Microsoft documents [INFO.PROPERTIES as a property rowset](https://learn.microsoft.com/en-us/dax/info-properties-function-dax)
and [DMV interfaces and their permission limits](https://learn.microsoft.com/en-us/analysis-services/instances/use-dynamic-management-views-dmvs-to-monitor-analysis-services).
The live accepted properties and refused session calls establish this reader's
actual access here; neither broad documentation nor earlier timestamp-DMV
refusals prove that all metadata is administrator-only.

## Proposed standard; not implemented

**My proposal is demonstrated difference on comparable self-reported fields,
with honest coverage, rather than requiring FULL coverage of every declaration.**
The evidence now provides a credible engine-product distinction: the SQL
server describes Microsoft Azure SQL Data Warehouse; the semantic server
describes OLAP Server. Those are different engine product categories, both
reported by their own query responses. The shared identity establishes no
difference. SQL's local IP and semantic ServerName are different descriptor
types; mere unequal strings would not prove different connections. Session
numbers from unrelated namespaces would not prove difference either.

For SQL-to-SQL Gold/Silver, the retained DB_NAME self-reports already distinguish
the database objects on both sides. The same engine/server does not make two
distinct self-reported databases the same engine/connection/object triple.
That existing evidence remains partial under #299, whose FULL gate is unchanged.

Before adopting the proposal, define adapter-owned, comparable engine-product
descriptors, preserve their original forms and provenance, and specify what
assertions make them incompatible. Do not treat version inequality alone,
client-supplied labels, host aliases or unrelated ID namespaces as proof.
The engine should consume that neutral difference evidence, not interpret
product strings or assume a Microsoft route.

Require the distinguishing descriptor to accompany each **actual quantity
probe**, preferably in the same response/query, along with identity, declared
binding and all omissions. Today's separate metadata probes do not attest
the value-serving surface of old receipts or automatically certify future
ones. INFO.PROPERTIES being a DAX table makes composing a descriptor with a
value query plausible, but that combined query was not executed in this audit.
Same product descriptors alone also do not prove two surfaces are the same.

FULL can remain a coverage grade, useful where attainable, independently of
the difference predicate. Missing engine/connection/object facts must remain
visible and limit the claim. Difference verification does not establish
faithful equivalence, snapshot alignment, current data or business correctness;
those separate gates remain. If no comparable field establishes difference,
verified boundary eligibility stays refused. No standard, validator, outcome
or adapter was changed here, and no old run was upgraded.

## Accounting and preservation

Thirteen query-request reservations: **3 SQL, 4 REST/DAX, 6 XMLA**. All attempts
are charged, including one unsupported SQL function, two XMLA permission
refusals and three initially empty property queries. There were zero ticket
diagnostic reads, guards, intake/planner/judge/synthesis calls or retries.
Rolling ordinary use increased **8 to 21 of 60**; no batch credits or limit
changes. The governed count bounds initiated query requests, not XMLA protocol
frames, authentication handshakes or an externally measured provider bill.
Per-investigation caps were not exercised by these operator metadata probes.

One appended ledger row per probe; no prior ledger line, Family D receipt,
output, run or draft #297 was changed. Config and usage-policy byte hashes
are unchanged. This PR changes documentation/evidence only; it introduces
no engine bytes or additional freeze invalidation. Intake evidence-resolution
and definition-target/reported-figure wiring remain queued.

Local validation: both required generator tests passed; all thirteen audit
receipt hashes recomputed; prior document and ledger byte prefixes preserved;
report links resolved; `git diff --check` passed. No runtime code changed.
