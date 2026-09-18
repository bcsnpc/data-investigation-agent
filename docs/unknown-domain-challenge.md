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
