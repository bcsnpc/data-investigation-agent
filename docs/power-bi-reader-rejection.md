# Power BI rejection of the reader: estate diagnosis

Updated 2026-09-26. Read-only diagnosis. No capacity, permission, identity or
model setting was changed. This is not a code change.

## The symptom

From 21:01 UTC, every DAX query the investigation engine sent as the reader
`investigator-reader@skynwhy.com` to model `3484a2bc…` (Warehouse Operations
e1b8e1) failed with:
- HTTP 400 `DatasetExecuteQueriesError`;
- Analysis Services error `3242524690` (`0xC1450012`).

The same unchanged baseline query succeeded as the reader at 01:25 UTC the same
day, in item 1's probe. See [surface self-report](surface-self-report.md).

## The hypothesis tested

The review suggested an estate cause on the trial Fabric capacity: the capacity
paused, throttled, or its trial expired. Direct Lake stops serving while the
metadata APIs keep answering.

## Evidence

**Capacity and workspace state** (read-only `GET`s as the administrator, about
21:33 UTC):

| Check | Result |
| --- | --- |
| Fabric capacities | `ec15bc07…` "Trial-20260725T002931Z-…", SKU `FTL4`, Central US, state **`Active`** |
| Power BI capacities | Same capacity, state **`Active`**, caller access `Admin` |
| Workspace `149f8d99…` | On capacity `ec15bc07…`, `capacityAssignmentProgress: Completed`, `isOnDedicatedCapacity: true` |
| Model `3484a2bc…` | Metadata returned: created 2026-09-18, `targetStorageMode: Abf`. Refresh history is empty (a Direct Lake model has no scheduled refresh in this estate). |

**Queries sent directly to `executeQueries`, outside the engine**, all metered:

| Time (UTC) | Identity | Model | Query | Result |
| --- | --- | --- | --- | --- |
| 21:34:49 | admin | e1b8e1 | `ROW("x", 1)` | **HTTP 200**, 1 row |
| 21:34:59 | admin | e1b8e1 | `ROW("n", COUNTROWS('Activity'))`, a Direct Lake data read | **HTTP 200**, 1 row |
| 21:35:30 | admin | f28cf2 (another model, same capacity) | `ROW("x", 1)` | **HTTP 200**, 1 row |
| 21:36:03 | reader | e1b8e1 | the unchanged baseline measure query, through the admission path | **HTTP 400**, `0xC1450012` |
| 21:36:49 | reader | e1b8e1 | `ROW("x", 1)`, which reads no data | **HTTP 400**, `0xC1450012` |

## What this establishes

- **Not the capacity.** It reports `Active`. Within the same three minutes, on
  the same model, the administrator's queries (including a Direct Lake data
  read) succeed. The capacity-paused/throttled/expired explanation is **not
  supported**. Throttling is not exposed by these APIs, but a throttled capacity
  would not serve one identity and refuse another in the same minute.
- **Not the data read.** The reader fails even on a constant expression that
  reads no data.
- **The rejection is specific to the reader identity** on this model. It began
  between 01:25 and 21:01 UTC on 2026-09-26.

## What this does not establish

**The cause is not established.** What changed for the reader in that window is
known only from this project's own actions:
- the account holder performed an interactive Azure CLI sign-in into
  `.local/azure-reader-sql` at about 20:40 UTC;
- the reader connected to the Gold SQL endpoint at 20:43 UTC.

Whether the reader's password was reset, or its sessions revoked, before that
sign-in is not known here. Candidates worth checking, none verified:
- **Reset or revoked sessions.** A reset or revocation could invalidate the
  identity Power BI uses on the reader's behalf for Direct Lake, while a freshly
  issued Power BI token is still accepted.
- **A changed model permission or setting** for the reader.

Checking needs Entra sign-in and audit logs, or the model's permission list,
viewed by the tenant administrator. Neither was read, because reading them would
require a Graph scope this session's identities do not hold.

**Trial expiry.** The trial capacity's name encodes its creation date,
2026-07-25. A standard 60-day trial would end about 2026-09-23. The capacity
reports `Active`, and the administrator's queries succeed, so expiry is not
indicated. The trial end date itself is not exposed by these APIs.

## Consequence for the engine

Until the reader can query this model again, every live DAX baseline as the
reader is `UNAVAILABLE`, and investigations stop at step 2. That is the correct
behaviour: the engine does not fall back to the administrator.
