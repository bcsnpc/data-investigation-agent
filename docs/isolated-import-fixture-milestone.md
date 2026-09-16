# Isolated Import fixture publication and content verification

Review: [PR #180](https://github.com/bcsnpc/data-investigation-agent/pull/180).

Tracking: [issue #179](https://github.com/bcsnpc/data-investigation-agent/issues/179).
PR #178 is merged at `95857895b6c0046c651ef9bcc9304d8daf493de1`.

## What this delivers

The acceptance lab now has a real isolated Import model whose data is compiled
from a reviewable artifact. It does not depend on a mutable external SQL or
OneLake source. This is operator publication tooling, not a new investigation
strategy or a metric-name branch in the adaptive runtime.

- `scripts/import_fixture.py` validates up to eight tables, 20 columns and 1,000
  rows per table. Supported cells are strings, booleans, exact bounded integers
  and nulls. Money can be represented in integer minor units. Dates, floating
  point and arbitrary external Power Query sources are intentionally unsupported.
- Active many-to-one relationships validate column types, unique non-null
  parent keys and absence of orphan child keys. Measures are operator-authored
  DAX definitions, not statements supplied by an untrusted business ticket.
- Canonical input, model and bundle hashes bind the generated TMSL and inline
  Power Query rows. Validation recompiles the specification before publication.
- `scripts/publish_import_fixture.py` creates a new workspace on an explicitly
  selected existing capacity, then creates a new model. It never updates an
  existing business model based on a matching display name.
- SQLite reservations commit before create/refresh dispatch. An uncertain
  request is held for inspection rather than automatically retried. Received
  responses replay without another mutation; completed LRO resolutions persist.
- Each invocation permits at most 40 HTTP calls, eight polls per operation and
  a 105-second subprocess limit per HTTP call. This is a per-invocation bound,
  not a tenant-wide quota. Service polling uses validated IDs, not arbitrary URLs.
- Refresh completion must match the submitted refresh ID. Standard refreshes
  may return `RequestId` without `Location`; unrelated completed history entries
  are not accepted as the publication's refresh.
- Complete bounded readback compares typed row multisets, preserving duplicates
  and explicit nulls. Partial-result errors and oversized responses fail closed.

## Validation

718 regression tests passed, including 24 focused fixture/publication tests.
Coverage includes artifact tampering, relationship/key errors, lossy values,
duplicate/missing rows, partial HTTP-200 query failures, uncertain dispatch,
changed-request replay, refresh correlation, bounded polling and persisted LRO
resolution integrity. The focused suite is included in CI.

## Live development evidence

The existing Central US FTL4 capacity was observed Active. No new paid capacity
was purchased and no Azure SQL reads, writes or quota settings were changed.

| Artifact | Value |
| --- | --- |
| Workspace | `ae4637b9-7d8b-4d7f-9f3e-28f3b3859080` |
| Semantic model | `6304045c-f80f-4e24-b905-b65522dff7ad` |
| Bundle hash | `b3eff25902ba9da368652ac35b0e8f98768168bb7590f301a6efacdbd5783545` |
| Input hash | `dd42fe0b162027edd286ad95e5288bac4cb72e7cdef8441a9ab74db5dba30b7e` |
| Submitted model hash | `2d2673c67004635ddfc9d95404061f556ce0c3f1f8f7711c4cf6de3b80f179a8` |
| Correlated refresh | `a6355ef5-e2bb-462b-8ff0-178e68b5b245`, Completed |
| Contents | 10 expected rows; 10 observed; exact multiset match |
| Native measures | Eligible events 10; refunded events 2; refund rate 0.2; total units 65 |

Removing one expected input row while retaining the saved live response produced
a mismatch. Publication replay reused the same workspace/model/refresh receipts.
Local artifacts and journals remain under `.local/import-fixture-*` and are not
committed. This tiny synthetic fixture is infrastructure smoke evidence, not a
hidden acceptance run or a business-data defect investigation.

## Runbook

Store a specification under `.local/` with `tables` and `relationships`. Each
table has `name`, `columns` (`name`, `type`), positional `rows` and `measures`
(`name`, `expression`). The compiler rejects unknown fields.

```powershell
python scripts/import_fixture.py --input .local/fixture-spec.json --output .local/fixture-bundle.json
python scripts/publish_import_fixture.py --bundle .local/fixture-bundle.json --journal .local/fixture-publication.sqlite --capacity <existing-capacity-id> --output .local/fixture-publication.json --verify
```

Use one journal per generation and retain it. Reusing a journal for different
inputs/capacity is rejected. Do not delete a journal to bypass an uncertain
dispatch. Inspect the saved request and remote resource/operation first; this
version deliberately provides no automatic uncertain-state recovery. Completed
refresh history may age out; absence of its exact ID results in a hold, not a
substitute refresh. Each verification captures data again; it is not an offline
replay of a prior content observation. Transport failures print no raw tokens or
service error bodies.

## Reader account and remaining proof boundary

The user approved creating a dedicated reader account. The current Fabric CLI
login cannot acquire a Microsoft Graph token, and Azure CLI is signed into the
personal Azure tenant. Therefore no enterprise account was silently created or
assumed. The user has been asked to create `investigator-reader@skynwhy.com` in
the enterprise tenant, with ordinary User directory role and a privately retained
temporary password. Account creation, license/sign-in readiness and access tests
are still pending.

After creation, grant only the isolated workspace Viewer access and required
model Read/Build permissions. Verify using that account's own token; never use
an admin token with a reader label. Check both successful bounded reads and
denied administrative capabilities. Do not add it to the business workspace.

**`generation_proven` and `live_acceptance_ready` remain false.** A successful
refresh, same model ID, exact readback or local journal cannot prove the model
was not changed and restored between observations. Enforceable remote write
controls, effective report/filter/identity context, approved semantic mappings
and a shared publication generation are still needed. This milestone does not
make a local lock into remote exclusivity or waive the Phase H gate.

The next grouped work is to establish that control boundary and separate reader,
bind the evidence into the catalog/runtime, then execute the frozen-runtime
acceptance families. The unified business/technical v2 UI and deployment follow
trustworthy investigation acceptance.

API references: [Fabric model creation](https://learn.microsoft.com/en-us/rest/api/fabric/semanticmodel/items/create-semantic-model),
[workspace creation](https://learn.microsoft.com/en-us/rest/api/fabric/core/workspaces/create-workspace),
[correlated refresh history](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/get-refresh-history-in-group),
[query response limits and partial errors](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/execute-queries-in-group).
