# Frozen unfamiliar-domain challenge

## v4 attempt: published and discovered; reader approval pending

Engine `981bec80b53ec17d01dfa7f02c3fc470257dbfe0`, tag `unknown-domain-v4-engine`.
Manifest SHA-256: `6540c4976b181b4481f1f7116066433cee5cbbf54b43e9c302e2084d60e1b46e`.
The freeze covers 382 engine files plus the v4 connection and usage policy.
The isolated working catalog retains 313 prior usage records. No publisher truth
was copied into investigator context. The baseline scan precedes generation and
publication. The baseline completed with 66 operations and zero matching assets
for fresh suffix `23619e`. Six SQL tables, three lakehouses and a notebook were
created; notebook execution completed. Model `163ce520-ec47-4824-975c-96f5c749205f`
and reports `ce379e11-9a02-43df-9ddd-14be119ec0ee` and
`e74fae1b-aab8-4058-9ae1-4038b7eec18a` are published. Nine business tickets are
prepared using the fresh published vocabulary. Rescan
`ffbc0be4-225a-47d9-a280-4c0a456646d6` completed with 81 operations, discovering
the model and both reports as CURRENT. The model was automatically projected
into the enabled catalog without runtime ID registration (five available models).
Exact reader grants are prepared and pending user approval; none has been applied.
This starts an attempt; it is not a challenge pass.


## Historical attempts (recorded 2026-09-18)

[Issue #199](https://github.com/bcsnpc/data-investigation-agent/issues/199)
under mission #193. Attempts v1/v2 are historical failed/partial attempts.
**Attempt v3 exposed a profile-projection defect after discovery. The engine
correction requires a fresh freeze; live acceptance has not passed.**
Sections below the v3 record preserve their original release evidence.

## Attempt v3: structural discovery and fresh publication

Engine tag `unknown-domain-v3-engine` freezes
`05348d0bc37eb03409f2f6d3726c62b92b6390e2` before variant generation.
The manifest covers 378 engine/infrastructure/workspace files plus connection and
usage policies. Manifest SHA-256:
`8d7eaf79210f9aadd6f916a243c97944f9e32cde08ea3e68cfcefe3b5b21a258`.
GPT-5.4 evaluation settings are included in the frozen infrastructure files.

Baseline `3e59c4d8-b4f4-4ba1-96d0-bd4b71c0d325` completed with 47 metadata
operations, complete listing coverage and zero changes before generation. Variant
`0fd86f` was absent. Publication created six new suffixed SQL tables, three
lakehouses, a notebook, one semantic model and two reports. Notebook job
`7d62256b-0507-47ba-b995-04778187cad8` completed successfully. Existing application
tables were not modified. Display vocabulary is publisher-owned and appears only
as ordinary generated model metadata, never investigator configuration or mappings.

The user explicitly approved Read + Build for investigator-reader on model
`8e434350-7100-47b7-a0de-2c5732385dbb`, and table-level SELECT for the SQL reader
on the six `_0fd86f` tables. Both grants were applied and read back. The initial
Power BI add request failed; access was read back and the documented
[update-user API](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/put-dataset-user-in-group)
set only ReadExplore. No write/admin grants were added. The first failed request
remains in the publisher journal.

Historical catalog, inventory and usage rows were copied using SQLite backup;
183 usage rows were retained. The challenge allowance is 150 planner calls,
4,800,000 input characters and 225,000 output-token reservations per UTC day;
cloud-call limit remains 60. This uses the user's existing authorization for
needed LLM budget increases, not a reset of consumption. Previous-folder trials
are stopped while this acceptance copy is active.

Post-publication scan `94dca95d-2e45-47eb-a225-13f38004ba0c` completed with
63 operations and complete coverage. It discovered the model and both reports
without manual model/table ID registration. The stored profile was 5,130
characters, but long scoped member IDs caused the 2,500-character planner
projection to discard every table. This was found before any v3 ticket trial.

The generic correction trims member lists with explicit truncation/counts before
dropping the selected table. The same discovered context now yields 1,997
characters, two table hints and selected-table numeric/measure references. The
original profile and freeze manifest remain unchanged. Engine edits invalidate v3
for further frozen grading; subsequent runs are explicitly known-domain regressions.
A new freeze and fresh variant are required. Nine-family results, hypothesis
revision, change/permission experiments and repeated hidden variants remain pending.


Known-domain transformation session `2337130f-66f5-4014-95a3-b601d2d338a3`
ended HELD / PLANNER_FAILED / UNRESOLVED with `APITimeoutError`, after ten
planner calls, five successful native reads, four metadata lookups and 230,746
cumulative input characters. It reproduced 53,145 and inspected notebook join
logic, but performed no SQL read or measured key/join-cardinality experiment.
Several native checks overlapped. This is partial observation evidence and a
failed completed investigation, not acceptance or a supported cause. The original
daily policy was restored after the run without resetting usage. The next quality
work must evaluate test selection and provider timeout behavior before another
freeze; merely publishing another variant would not resolve these findings.

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
