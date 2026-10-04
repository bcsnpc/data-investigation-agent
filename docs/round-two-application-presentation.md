# Isolated application-load presentation checkpoint

Recorded 2026-10-04 UTC. This continues Part B; no source scenario has run.

The corrected pipeline and audit agreement are recorded in
[audit verification](round-two-audit-verification.md). Its own copy output and
the reader's one same-run audit row both report 360 rows read and 360 written.
The high watermark is unavailable; matching counters do not establish snapshot
alignment or membership completeness.

## Publication and preserved verification failure

Using the existing publisher `admin@skynwhy.com`, one isolated semantic model
was created: `Application load fixture 20261003`, ID
`0c89889c-6fe6-49ab-91e9-4b00a51070e6`. It declares Direct Lake over
`dbo.stock_movements_round_two_20261003` in the isolated application-loaded
Bronze lakehouse, SQL endpoint `fbbccea4-d943-4f58-b91f-e6cbcb912620`.
Its measure is `Movement Units = SUM('Movements'[units])`.
No existing report, model, table, schedule or permission was changed.
This is separate from the older literal-seeded fixture's lineage.

Publication and definition retrieval used eight physical requests. The local
verification script ended `FAILED_OR_PARTIAL` with `StopIteration`: it expected
`model.bim`, while Fabric returned TMDL parts. That original receipt and ledger
row remain unchanged. No second publication occurred.

A separate offline verification of the retained TMDL confirms the exact source
table, schema, endpoint, Direct Lake mode, measure and expression link. The
verification has zero cloud requests and is recorded separately as
`SERVED_TMDL_DECLARATION_VERIFIED_OFFLINE`. It proves the served declaration,
not a successful reader value query or an investigation outcome.

## Reader permission before listing and pending decision

One read-only Power BI control-plane request returned HTTP200. The new model's
listing is:

```json
[
  {"datasetUserAccessRight":"ReadWriteReshareExplore","identifier":"admin@skynwhy.com","principalType":"User"},
  {"datasetUserAccessRight":"Read","identifier":"investigator-reader@skynwhy.com","principalType":"User"}
]
```

The reader currently has Read, not Read + Build. Under CLAUDE.md section 8,
the following exact one-model request is prepared and awaiting an explicit human
decision. It has not been applied; no workspace role or write permission is
requested.

```http
POST groups/149f8d99-1c66-4a0a-9624-759be002bb60/datasets/0c89889c-6fe6-49ab-91e9-4b00a51070e6/users
```

```json
{"identifier":"investigator-reader@skynwhy.com","datasetUserAccessRight":"ReadExplore","principalType":"User"}
```

The dedicated SQL reader and dia-reader are unchanged. Audit-source runtime
integration, load-latency and ingestion-gap producers, current discovery
recollection/approval, the four authored scenarios and unchanged family E remain
pending. No engine freeze or unfamiliar-domain acceptance is claimed.

## Accounting and receipts

Publication: eight physical requests, zero diagnostic reads, zero planner calls.
Permission listing: one physical metadata request, zero mutations. Offline TMDL
verification: zero requests. Cumulative Part B is **149/300**; rolling ordinary
usage at the permission check is **304/600**. Per-run diagnostic cap remains 12.

Private sealed receipts remain under `.local/round-two-20261003/`:
`application-presentation-publication.json`,
`application-presentation-served-verification.json`, and
`application-presentation-permissions-before.json`.
Each has a corresponding append-only ledger entry; the failed publication
verification is not rewritten as a clean success.


## Dated human-approved identity scope change

2026-10-04 UTC: the human explicitly approved Read + Build on this one model,
using the existing publisher, with no workspace role, write or other item.
The exact prepared request above was applied unchanged. Fresh before/after
listings both returned HTTP200; the POST returned HTTP200. The reader entry
changed from `Read` to `ReadExplore`; the publisher entry remained
`ReadWriteReshareExplore`. No other identity or item was changed.

The sealed `application-presentation-reader-grant-applied.json` records the
human decision, exact request and full before/after listings. The append-only
ledger records `IDENTITY_SCOPE_CHANGE_HUMAN_DECISION`. The reader manifest now
names this model and its scope. This supersedes the pending-decision checkpoint
above without erasing its historical evidence.

These three control-plane requests bring Part B to **152/300** and observed
rolling usage to **307/600**. Diagnostic cap remains 12. No investigation run
was performed as part of the grant.
