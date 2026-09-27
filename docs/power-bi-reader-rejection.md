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

## Update 2026-09-26: model scope, identity mode, a permission grant and the revoked grant

The sections above are kept as written. Each finding below is dated, and marked
where it corrects an earlier one.

### What the three checks found (21:47–21:50 UTC)

- **Direct Lake refuses the reader; Import serves it.** At 21:47 UTC, the
  reader's constant `ROW("x",1)` failed with HTTP 400 `0xC1450012` on a second
  Direct Lake model (`f28cf2`), and succeeded with HTTP 200 on the Import model
  (`5f2afb96`). Same identity, same cached token, one minute apart.
- **The admin succeeds on the same model** (21:34–21:35 UTC, above).
- **This is model load, not table permissions.** The reader fails even on a
  constant expression that reads no data.
- **The warm-model theory is disproved.** The admin's queries at 21:34 UTC
  loaded the model, and the reader still failed at 21:36 and 21:47 UTC.
- **The models run as the caller.** Both Direct Lake models report a single
  `Sql` data source and **zero bound connections**
  (`GetBoundGatewayDataSources`). No shareable connection references the
  workspace. So the models use the caller's identity, not a fixed identity.
  This is inferred from the absence of a binding, not read from an explicit
  flag.
- **OneLake access on the Gold lakehouse.** Its `DefaultReader` role permits
  `Read` on path `*` for the item's `ReadAll` holders. The reader was not a
  member; its only workspace role is `Viewer`.
- **The timing stayed unexplained at the time of these checks.** Nothing
  readable showed a change between the 01:25 UTC success and the 21:01 UTC
  failures. The remaining evidence was in tenant audit and sign-in logs, which
  these identities cannot read.

### The authorised permission change (21:52:38–21:52:42 UTC)

One change, authorised explicitly: the reader
(`investigator-reader@skynwhy.com`, object `8a582d2a…`) was added as the only
Microsoft Entra member of the Gold lakehouse's (`b0ab76f7…`) `DefaultReader`
OneLake data access role. The role API replaces all roles, so the single
existing role was resent exactly as read, with `If-Match` on its ETag. A
`dryRun` returned 200 first.

| | Before | After |
| --- | --- | --- |
| Roles | `DefaultReader` only | `DefaultReader` only |
| Decision rules | Permit `Read` on `*` | unchanged |
| Item members | `ReadAll` holders of the lakehouse | unchanged |
| Entra members | none | the reader only |
| Workspace roles | admin `Admin`, reader `Viewer` | unchanged |

Before and after snapshots are kept locally, with SHA-256 `3e64209404b31e26…` and
`0a0a58e3a934e7d4…`. No workspace role, tenant setting or other identity was changed.

### The re-run did not test the grant (21:52:56 UTC)

The reader's constant query never reached Power BI. Token renewal failed first.
Its reservation was settled as uncertain, because no HTTP status came back.

### The reader's grant was revoked, which probably explains the whole failure

- **The cache:** the reader's MSAL cache (`.local/fixture-reader-auth`) holds
  one access token, cached at **20:32:26 UTC** and expiring at 21:55:22 UTC,
  plus one refresh token.
- **The renewal error:** a forced renewal returned `invalid_grant`,
  **`AADSTS50173`**: "The provided grant has expired due to it being revoked …
  The user might have changed or reset their password."
- **Correction:** the earlier conclusion that the token was valid and the
  session not revoked (reported in conversation, not committed) was wrong. The
  cached access token was still valid; the session behind it had been revoked.

The best-supported explanation, which is not verified against audit logs, is:
- The reader's password was changed or reset at about the 20:40 UTC interactive
  sign-in, revoking the reader's existing grants.
- Every reader query afterwards used the access token issued at 20:32, before
  that change. An Import query needs only that token, so it was served.
- A Direct Lake model runs as the caller and must obtain further tokens from
  the caller's session to read storage. That session was revoked, so the model
  could not load for the reader (`0xC1450012`).
- The admin's session was unaffected.
- This fits the 01:25 success, the 21:01 onset, the Direct Lake-only failure,
  and the constant-query failure.

### What remains open

- **The grant's effect is untested.** The reader needs a fresh interactive
  sign-in (`scripts/connect_fixture_reader.py --sign-in`) before any reader
  query can run. That is an action for the account holder.
- **The grant may be unnecessary.** If the revoked session was the whole cause,
  the `DefaultReader` membership was not needed. Removing it would be a separate
  permission change, requiring separate authorisation.
- **The password change is not confirmed.** Only the tenant audit log can
  confirm it; these identities cannot read that log.

## Correction 2026-09-26 (21:58 UTC): the revoked grant does not explain the refusal

The update above says the revoked grant "probably explains the whole failure".
**That explanation is withdrawn.** The observations it rests on are kept.

- **21:57:54 UTC:** the account holder signed the reader in again, through
  `connect_fixture_reader.py --sign-in`. Its built-in check passed on the Import
  model: HTTP 200, identity matched, and refresh history refused with 403, as
  intended.
- **21:58:39 UTC:** with that fresh session **and** the `DefaultReader` OneLake
  grant in place, the reader's constant `ROW("x",1)` against the Direct Lake
  model still failed: HTTP 400 `DatasetExecuteQueriesError`, Analysis Services
  `0xC1450012`.

So neither a revoked session nor missing OneLake read access explains why Direct
Lake refuses the reader. `AADSTS50173` did occur: the reader's earlier grant was
revoked. But it is not the cause of this failure.

- **Password change:** whether the 21:57 sign-in prompted a password change was
  not observable from here. The account holder can confirm.
- **Propagation delay:** OneLake data access role changes can take time to
  propagate, so a delay is not excluded. It was not tested further.

Per the instruction, the experiment stopped at this failure. No further
permission was added, and the `DefaultReader` grant **remains in place**:
removing it was authorised only if this query succeeded. The cause of the
Direct Lake refusal is **not established**. The change between 01:25 and 21:01
UTC is unexplained.

## Update 2026-09-26 (22:06 UTC): the OneLake grant was reverted

The reader's `DefaultReader` OneLake membership was tried at 21:52 UTC. It did
not resolve the Direct Lake refusal (21:58 UTC, above), and it has been
reverted. The sections above are kept as written.

**The revert** was the single change authorised for it:
- **22:06:06–22:06:10 UTC:** the reader was removed from the Gold lakehouse's
  `DefaultReader` role.
- **Guard:** the role's state immediately before the revert was confirmed to be
  exactly the post-grant state (snapshot SHA-256 `0a0a58e3a934e7d4…`,
  identical to the post-grant snapshot). A `dryRun` returned 200. The update
  carried `If-Match` on the ETag just read.
- **Result:** the role is again exactly as it was before the grant. Rules
  (permit `Read` on `*`) and item members (lakehouse `ReadAll` holders) are
  unchanged, and there are no Entra members. Post-revert snapshot SHA-256 is
  `1f21444d2e027462…`; it differs from the original snapshot only
  by ETag.
- **Unchanged:** no workspace role, tenant setting or other identity was
  changed.

The Direct Lake refusal of the reader remains, and its cause is not
established.

## Root cause, 2026-09-26: a stored service-side grant invalidated by a password reset

**Provenance.** This section records the findings of an independent
investigation reported by the account holder, which used XMLA against the same
model. This session did not perform that investigation and has not re-verified
its findings. It records them as reported. The sections above are kept as
written.

**Reported cause:**
- **The reset:** the reader's password was reset at **2026-09-26T20:42:20Z**,
  which advanced the account's `TokensValidFrom`.
- **The stale grant:** Power BI's service-side Direct Lake path still presents a
  grant for the reader issued on **2026-09-16**. It now fails with
  **`AADSTS50173`** (`AdalGrantHasExpiredDueToPasswordChangeErrorCode`).
- **Why re-signing did not help:** a fresh client-side sign-in does not replace
  that stored service-side grant. That is why the reader's re-sign-in at
  21:57:54 UTC did not help.
- **Why it looked generic:** XMLA exposes this real error. `executeQueries`
  masks it as the generic `DatasetExecuteQueriesError`, Analysis Services
  `0xC1450012`.

**Consistent with the observations above:**
- The admin succeeds on the same model; that grant is unaffected.
- The Import model serves the same reader; it needs no stored downstream grant.
- The reader's SQL endpoint reads succeed.
- The onset lies between the 01:25 UTC success and the 21:01 UTC failures; the
  reset was at 20:42:20 UTC.
- A constant query fails, because the model cannot load for that principal.
- Neither OneLake role membership nor the workspace role is involved. Both were
  tested; the OneLake grant was added and then reverted.

### Corrections, dated 2026-09-26

Each earlier hypothesis is corrected here. The original text is kept above.
- **Capacity (paused, throttled or expired): wrong.** The capacity was
  `Active`, and it served the admin in the same minute.
- **Session: wrong as framed, and wrongly dismissed.**
  - This session recorded that the reader's revoked client session "probably
    explains the whole failure". It then withdrew that explanation when a fresh
    sign-in did not help.
  - The password reset and `AADSTS50173` were in fact the cause. The failing
    grant is the stored service-side one, not the client's session.
  - So the original claim wrongly located the grant, and the withdrawal wrongly
    concluded that `AADSTS50173` "is not the cause of this failure".
- **OneLake read access: wrong.** Adding `DefaultReader` membership did not
  help, and it was reverted.
- **"Cause not established": superseded** by the reported cause above.
- **Timing "unexplained": superseded.** The reset at 20:42:20 UTC explains it.

**Still not done:** nothing has been changed to renew the service-side grant.
Live DAX baselines as the reader remain `UNAVAILABLE` until it is renewed.

## Remedy, 2026-09-27 00:32 UTC: an interactive portal sign-in cleared the stale grant

The sections above are kept as written.

**The action:** the account holder signed in to app.powerbi.com as
`investigator-reader@skynwhy.com`, in a private window, and opened a report on
the Direct Lake model. This should make Power BI mint a fresh delegated grant
for that user.

Afterwards, as the reader:
- **00:32:37 UTC, constant query:** `ROW("x",1)` on the Direct Lake model
  (`3484a2bc…`) returned **HTTP 200**, 1 row. Before, it failed with
  `0xC1450012`.
- **00:33:02–00:33:29 UTC, baseline measure query:** run through the engine's
  per-probe path (`evaluate()`, then `attest()`, then `refine_failure()`). It
  returned **`OBSERVED`**, `COMPLETE_RESPONSE`, sealed receipt `058ea31a…`.
  - The value's fingerprint equals item 1's reader baseline from 01:25 UTC on
    2026-09-26, so it is the same value.
  - **The first live DAX self-report:** Power BI answered
    `USERPRINCIPALNAME()` with `investigator-reader@skynwhy.com`. Attestation is
    `MATCHED`, with `object`, `engine` and `connection` unattested. The
    self-report is sealed inside the receipt.

**What this establishes:**
- **The remedy:** an interactive portal sign-in cleared the stale service-side
  grant (`AADSTS50173`).
- **Not an API remedy:** nothing in the APIs exposed this. A fresh client-side
  MSAL sign-in did not clear it at 21:57 UTC, and neither did OneLake role
  membership.
- **Recovery:** a live DAX baseline as the reader can be established again.

**Not established:** why the portal sign-in, and not the client sign-in,
refreshed the grant. The account holder did not renew the data source
credential separately, so the portal sign-in is the only recorded action.
