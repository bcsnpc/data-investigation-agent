# Frozen unfamiliar-domain challenge

2026-09-18. [Issue #199](https://github.com/bcsnpc/data-investigation-agent/issues/199)
under mission #193. Attempt v1 **failed end-to-end intake reliability**; general
intake corrections and a fresh freeze/variant are in progress. Acceptance has not passed.

## Freeze and separation

Stages 4–5 merged in [PR #198](https://github.com/bcsnpc/data-investigation-agent/pull/198)
at `5c79b517f98e0f09c6861b184506fb0a4138d808`, all six CI checks green.
Tag `unknown-domain-engine-v1` identifies commit
`6d001a4c6806bacdfcc34e7a0b1eb6a7cfeb93fc`. The local manifest hashes 372 existing
script/infrastructure/workspace files plus connection, usage and LLM configuration.
Manifest SHA-256: `cf1856a4be4d618fddbb21b3977689a58a834bd7ef95baa3d6a7771868ba9875`.
The engine was unchanged throughout attempt v1. It is now being corrected, so v1
cannot be resumed as a successful frozen acceptance attempt. Publisher/evaluator code is under
`acceptance/unknown_domain`, outside runtime imports. Generated expectations and
SQL readback files are private local acceptance artifacts, never planner inputs.

The baseline scan `beed2ba9-ab77-437e-a8a7-921be2272aa5` completed before publication
with nine operations. It contained the old fixture, not this domain.

## Publication and discovery evidence

A fresh related variant created six new suffixed SQL tables: warehouses, products,
product rates, stock movements, purchase orders and adjustments. Existing application
tables and SQL free-overage settings were untouched. SQL rows were read back and
loaded into three new Fabric lakehouses, then transformed by a new notebook.
The notebook job `7689f68d-2b8b-4ed9-ba2a-a6865f0ccf70` completed successfully.
This is a small controlled variant, not another 100,000-order regeneration.

A new Direct Lake model, `Warehouse Operations f28cf2`, and native reports
`Inventory Health f28cf2` and `Warehouse Performance f28cf2` were created.
The first report import failed because its themeCollection was missing. The
publisher corrected that definition after the remote operation reported terminal
failure; no engine change was made.

First post-publication discovery `7c98d2c9-1b01-4fba-8c1e-f25e4909c636` completed
with 24 operations and 117 changes. It automatically projected the new model and
the first report; a second scan collects publication completion. No model/report/
table IDs were registered in investigator configuration.

The dedicated reader initially received a permissions/not-found response. The user
explicitly approved Read + Build on model `c463921e-64b2-488e-b8b1-e0239980c79c`.
The grant returned HTTP 200, and a subsequent query using that reader returned
408 movement rows. Publisher credentials were not substituted for the reader.
This probe demonstrates access, not investigation success.

## Attempt v1 results

Second discovery `696b9a29-ec69-4957-b62c-acc8cec296d8` completed with 27 operations,
22 further changes and both reports visible. The graph contained 17 new lakehouse
tables and six new SQL tables. No per-asset registration occurred.

| Family | Recorded result |
| --- | --- |
| A Discrepancy | HELD twice at intake; second proposal altered an encoded measure ID and attached a quote without a corresponding filter |
| B Ratio | Completed: one native query, two planner calls; Received Units 6,333, Movement Units 8,595, Receipt Share 0.73682373472949392; cited component calculation and business-intent limit |
| C Derived | HELD at intake; no investigation queries |
| D Visual/filter | HELD at intake; no investigation queries |
| E Freshness | Asked the user to identify technical freshness context unnecessarily; no investigation queries |
| F Transformation | HELD at intake; no investigation queries |
| G Source/application | HELD at intake; no investigation queries |
| H Expected behavior | HELD at intake; no investigation queries |
| I Missing business context | Asked an intake clarification; did not yet investigate the unknown rule |

The ratio session was `c89e31f3-5962-4f57-a2a1-506a8c06e6a2`.
These results do not pass the challenge. The generic correction uses short
schema-enumerated catalog handles instead of having the LLM reproduce encoded URIs,
and attaches provenance quotes directly to filters. Freshness/history context is
made available through asset lookup. No domain names or expected answers enter
the engine. New behavior requires refreezing and a fresh variant.

## Acceptance still required

The nine business-ticket families, repeated/hidden variants, failed-hypothesis
revision, asset additions/changes/rename/removal and live permission/partial-scan
experiments still need their own recorded results. Do not infer that they passed
from publication or an access probe. Future engine corrections invalidate this
attempt and require a new freeze and fresh variant.

Publisher-only checks passed: two related-data/model tests, Python compilation and
PowerShell syntax parsing. The existing frozen engine's release evidence is 891
regression tests, 40 browser checks and the earlier live SQL/DAX smoke tests.

Artifacts are under `.local/unknown-domain`; see the
[publisher/evaluator runbook](../acceptance/unknown_domain/README.md).

## Attempt v2: fresh publication and reader access

The corrected engine is frozen at `3d958593cc1a9b2c0e987bdce60128055a463af6`,
tag `unknown-domain-engine-v2`. Manifest SHA-256:
`e43f3e37eed0a82ec164335d1c87b61a01209c24edba3ee43bbb575f972f3bcd`.
Correction validation recorded 894 regression tests and 40 browser checks; the
final intake schema caps also passed 29 focused intake tests.

The fresh e1b8e1 variant uses different data and semantic vocabulary. Its SQL
fixture includes primary/foreign keys. Publisher/evaluator artifacts remain
outside investigator inputs. Baseline discovery preceded publication; subsequent
scan `96dbb591-587a-43da-bdd0-f3ba5bd70593` completed with 45 operations and made
three models available in the catalog, including the new model and both reports.

The user explicitly approved Read + Build for investigator-reader@skynwhy.com on
model `3484a2bc-98c5-4cef-be5c-a6215484075e`. The grant returned HTTP 200 and a
native query succeeded using that dedicated reader. This is access evidence,
not a passed investigation. Artifacts: `.local/unknown-domain-v2/reader-grant.json`,
`reader-probe.json`, `discovered.json` and `freeze.json`.

The first discrepancy ticket resolved to the correct new model/measure with global
scope, then stopped HELD / TOOL_UNAVAILABLE after one planner and one query call.
Session: `70ea5018-cc35-4589-a295-9869b959484d`. Direct inspection of the native
response found a publisher defect: Activity Entries still uses
`COUNTROWS(Movements)` although the table was renamed Activity. The count-only
access probe succeeded because it queried Activity directly. This is not an
access failure or a passed investigation. Preserve the failed run; repair the
publisher/model, rescan and record a new attempt before continuing the matrix.
The engine freeze remains unchanged.

### Publisher repair before further v2 trials

Fabric operation `25a92dd0-4bd7-454e-8837-341e62ec8f70` succeeded. The publisher
now renames COUNTROWS table arguments as well as qualified column references;
three publisher tests and two required generator tests passed. A dedicated-reader
query returned Handled Quantity 8,765, Inbound Quantity 6,425, Outbound Quantity
2,340, Quantity Balance 4,085 and Activity Entries 406. This diagnostic repair
probe is separate from autonomous acceptance. The original failed run is retained.
Engine v2 files and prompts remain unchanged. Repair receipts are stored in
`.local/unknown-domain-v2/model-repair-{response,status,probe}.json`.

### First post-repair v2 matrix

Rescan `f5ab58db-0938-441f-baf0-bd3a4c25a9a6` completed with 45 operations and
seven changes. Engine freeze verification still passes.

| Family | Recorded behavior | Acceptance assessment |
| --- | --- | --- |
| A Discrepancy | Read five native values; three repeated hypothesis-contract rejections; stopped NO_PROGRESS | Failed to trace discrepancy |
| B Ratio | Read ratio 0.733029092983457; asked whether component explanation was wanted despite explicit request | Partial read; failed requested component investigation |
| C Derived | Read balance 4,085 and components 6,425 / 2,340; emitted EXPECTED_BEHAVIOR | Partial: arithmetic reproduced, but shallow explanation does not establish why value is low |
| D Visual/filter | Completed filtered native read, then contract rejection and RateLimitError | Blocked; filter-context explanation incomplete |
| E Freshness | Proposed nonexistent INFORMATION_SCHEMA.REFRESH_HISTORY; validator rejected it; then RateLimitError | Blocked with invalid-query finding; no freshness conclusion |
| F Transformation | One native read, then RateLimitError | Blocked; transformation investigation incomplete |
| G Source/application | One native read, then RateLimitError | Blocked; source investigation incomplete |
| H Expected behavior | Asked the user to confirm definitions already present in metadata | Failed to use available context |
| I Missing business context | Intake HELD / RESOLUTION_UNCERTAIN | No investigation; cause not established |

These results are not a pass. RateLimitError is recorded in D/E/F/G planner events;
no quota increase or automatic retry was made. An evaluator-only 65-second call
interval is available for fresh trials; existing deadlines still apply. The first
matrix receipts are `.local/unknown-domain-v2/runs/*-repaired.json`.

### Paced transformation repeat

Session `5b0e19c4-8027-4499-8695-53c89adc3876` used a 65-second evaluator-side
minimum LLM interval and finished UNRESOLVED / BUDGET_LIMIT: six planner calls,
five successful native queries and one rejected unqualified SQL proposal. No
RateLimitError occurred. Extended Value was observed as 57,043, but no notebook
context was retrieved and no upstream source query completed. Repeated overlapping
native aggregates consumed the budget. This is a failed transformation acceptance
case, not a provider blocker. Receipt: `runs/F-paced.json` under the v2 artifact folder.

Next engine work should address hypothesis-update schema reliability, material
clarification versus available metadata, context retrieval before unfamiliar source
queries, and detection of redundant diagnostics. These must remain domain-generic.
Any such engine change invalidates v2 for further unknown-domain grading and needs
a fresh freeze/variant. The change/permission experiments and broader roadmap remain
pending; issue #199 is not complete. No verified-cause or generality claim is made.
