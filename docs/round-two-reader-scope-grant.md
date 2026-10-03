# Round Two: explicitly approved reader scope change

2026-10-03, America/Chicago. The user's explicit decision authorized SELECT only
on `app.stock_movements_round_two_20261003` for `orderops_investigator`, required
the prepared script unchanged, and prohibited schema-wide, write and other-object
grants. This satisfies CLAUDE.md's identity-scope decision rule.

The script executed was exactly:

```sql
-- Prepared only. Requires the user's explicit permission decision.
-- No write, DDL, administrator, schema-wide or database-wide permission.
GRANT SELECT ON OBJECT::[app].[stock_movements_round_two_20261003]
TO [orderops_investigator];
```

Prepared/executed script SHA-256:
`e5c283cd5dec4f1c863887d479e6c26d6a3df6e78ac172d8421a4beadd79aa61`.
The existing database-owner credential executed it; the diagnostic credential
did not elevate itself. No other mutation statement was sent.

The before and after permission control-plane reads were served by Azure SQL
as `orderops_investigator` in `ordersops`, using `HAS_PERMS_BY_NAME` with the
exact object name and each named permission. They were performed immediately
around the successful execution and retained in the separately sealed local
`reader-grant-execution-protocol-corrected.json` receipt.
Receipt seal: `48d05cc3160fd0a0e5cf9b45fbbaaea01f4393c8da54dd28f7530d4c22d7de0a`.
File SHA-256: `434c5a806efbd9b16619db56b5ea2602221305e0218b6748c94bc10981dd7295`.
Successful action recorded at `2026-10-03T23:31:59.525491+00:00` through
`2026-10-03T23:32:06.629582+00:00` (18:31–18:32 America/Chicago).

| Effective object permission | Before | After |
| --- | --- | --- |
| SELECT | 0 | 1 |
| INSERT | 0 | 0 |
| UPDATE | 0 | 0 |
| DELETE | 0 | 0 |
| ALTER | 0 | 0 |
| CONTROL | 0 | 0 |

The grant makes this isolated fixture's application source readable for Part B.
It does not establish a source-to-Bronze binding, a load, faithful comparison or
ingestion completeness. No schema-wide grant, write permission, other-object
grant, app registration, audience, firewall, SQL free-limit setting or live
configuration was changed.

## Preserved failures and accounting

1. Initial permission preflight failed at connect with SqlException 40613; no
   SQL statement or grant was dispatched. Its admission stays charged.
2. A read-only Azure database control-plane request observed Online and a resume
   at `2026-10-03T23:28:30.157000+00:00`. Free-limit/AutoPause settings were unchanged.
3. The resumed reader check returned strings (`"0"`), but the local helper
   compared one with integer zero. Its assertion failed before grant execution.
   The recorded "Unexpected existing access" assertion is a helper defect, not
   evidence of an existing permission: the retained response says zero.
4. The corrected permission assertion passed, but a local wrapper used the
   metered-reader stdin protocol for an ordinary mutation script. That script
   waits for EOF; the metered caller leaves stdin open. The bounded operation
   timed out before opening SQL. The conservatively reserved slot is retained;
   it is not a served SQL request or an executed grant.
5. The final wrapper used the proper ordinary subprocess protocol for the
   single mutation, within its durable admission. Before check, unchanged grant
   and after check all succeeded. SELECT became one and all tested write/control
   permissions stayed zero.

Each failed attempt and the successful action have their own appended ledger
row. No artifact, counter or prior row was edited or refunded. Eight admissions
were added by this sequence: six completed estate requests and two unsuccessful
preparations. This includes one SQL permission mutation; it is recorded separately
from metadata reads and is not a diagnostic quantity. Part B's preceding nine
admissions remain, making **17 of 120** at this checkpoint. The ordinary rolling
allowance remains 300; no policy increase or credit grant occurred.

## Carry-forward scenarios and platform finding

B3 now has four authored scenarios (gap, latency, absent at the declared source,
and source declared but configured unreachable), followed by unchanged family E.
The fourth must stop at the deepest reachable declared layer, name the inaccessible
source boundary, quote the load's successful completion and its own rows-read and
rows-written accounting, and send the remaining question to the application owner.
It cannot establish LOAD_LATENCY or INGESTION_GAP without reading the application.
Matching job accounting alone is not independent evidence that all expected
application rows arrived or that the source has not changed since.

The previously recorded Copy Job history request served HTTP 200 to the reader;
this is now recorded as a positive capability in CLAUDE.md's platform table.
It establishes listing access on the tested job. Its empty list does not establish
that completed-run details or row accounting are served; those must still be tested.
No new investigation ran in this grant checkpoint; no scenario outcome is claimed.
README and delivery status record this scope change. Engine bytes are unchanged
by this evidence PR; prior freezes already remain invalidated.
