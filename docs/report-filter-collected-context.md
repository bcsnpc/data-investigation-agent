# Report predicates in the engine's collected context

Date: 2026-10-01. Tracking: [#193](https://github.com/bcsnpc/data-investigation-agent/issues/193).
[Publication evidence](report-filter-fixture-publication.md).

**All fixture predicates reach the engine.** This audit reads the newly published
model context and current enterprise assets, rather than the publisher output.
All 16 report parts are present, parseable and retrievable through the engine's
existing content accessor. Nothing retained by publication was lost or changed
in collection. This establishes input availability, not filter reproduction.

## Rescan, approval and preserved failure

#292 merged as `bfda35b7348e5055a1c0818106c5f9e6638cfed6` after six green checks.
The environment is unknown-domain-v4; the inspected existing model is e1b8e1.
Metadata calls used admin@skynwhy.com, principal
23de217f-6e14-49cf-9acd-47dcd83cb82f, verified for Fabric, Power BI and OneLake.
The diagnostic reader was not elevated.

Collection completed with **89 collector operations: 88 HTTP metadata requests
and one SQL catalog invocation executing seven read commands, 95 physical estate
reads total**. Definition status/result polls are included. SQL commands were
objects, columns, keys, foreign keys, definitions, checks and permissions.
No business quantity reads or model calls. Discovery kept its original
160-operation, 32 MiB and 600-second collection limits; separate scan budgets
apply. Ordinary investigation allowance and credits stayed unchanged.

First local publication failed after collection: my local audit file inspect.py
shadowed Python's standard-library inspect during a dataclasses import. Failed
scan `de043485-a70b-48fc-a121-521f4fa187c1` remains FAILED / KeyError in history.
Renaming the local file fixed the harness error without changing the engine.
Recovery published from the exact captured responses, replayed in original
request order with target/method/audience and response hashes checked. Recovery
made **zero additional cloud requests**; its replayed 89 operations are not
another 95 physical reads. Collection timestamps remain the original live
interval, not the later context-publication time.

- Complete enterprise scan/version: `a786eef2-d4fc-43a9-b5e3-2a6a1ee0774a`.
- Raw inventory scan: `c5f429a5-2924-4185-af2d-53265aed6742`.
- Catalog model: `5b3eff46-631c-47b8-8211-049b5aa906ee`.
- Model context: `3ae7607b-5a5e-46c6-8e1b-195dbabc9cae`, revision **4**, enabled.
- Discovery-model approval and context both pin the whole-config digest:
  `19e2ef0b0b5cb6bfd8df38c5fded6c1eaac40718b3926248ac62c61abf0cf8b6`.

Configuration and engine fingerprints are unchanged. Prior run files, provider
tapes, existing docs/run artifacts and persisted v2_runs, v2_run_events and
adaptive_sessions were hashed before/after and stayed unchanged. Two appended
ledger rows distinguish failed live publication from zero-read captured-metadata
publication; earlier rows are not rewritten. Old previews remain historical.

## What collection contains

Report: `2bc1cb2d-9230-4b8f-b7dc-c9f6b2151995`. Definition coverage is COMPLETE.
Its projected model context contains all **16 DefinitionParts**, explicitly bound
to the existing model. The enterprise assets also include **two ReportPage assets
and seven ReportVisual assets**, retaining native metadata.

| Content | Collected representation | Result |
| --- | --- | --- |
| Pages | Two page.json parts plus ReportPage assets | Page predicate and slicer interactions intact; control unfiltered |
| Visuals | Seven visual.json parts plus ReportVisual assets | Both saved slicer selections and card visual filter intact |
| Filter config | Embedded filterConfig in native page/visual metadata and parts | Present; no separate FilterConfig entity |
| Bookmark index | definition/bookmarks/bookmarks.json part | Present; points to saved bookmark |
| Bookmark data/state | definition/bookmarks/3ea29d97240757cdb0d6.bookmark.json part | Both saved selections, page/visual predicates and Data-enabled options intact |
| Other parts | .platform, definition.pbir, report.json, version.json, pages.json | Present |

There is no normalized ReportBookmark entity. The bookmark is a CURRENT
DefinitionPart child, retrievable through get_asset/read_content. All 16 parts
were reconstructed through that engine route in **17 local content reads**, with
next_offset followed and text checked against storage. The 8,609-character
bookmark uses offsets 0 and 6,000; its second page is available. No cloud reads
or planner calls were needed for this check.

## Exact predicate fragments from the new context

All parts parsed as JSON. Each predicate's From alias resolved to the semantic
entity and actual model column; literal tuples match that column's string type.
Parseability does not claim an implemented filter-to-query compiler: capability
work is still pending authorization.

### Bookmark Slicer Selection: Locations.warehouse_name

`definition/bookmarks/3ea29d97240757cdb0d6.bookmark.json`

```json
{"Version":2,"From":[{"Name":"s","Entity":"Locations","Type":0}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"warehouse_name"}}],"Values":[[{"Literal":{"Value":"'Coastal'"}}]]}}}]}
```

### Bookmark Slicer Selection: Items.product_name

`definition/bookmarks/3ea29d97240757cdb0d6.bookmark.json`

```json
{"Version":2,"From":[{"Name":"s","Entity":"Items","Type":0}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"product_name"}}],"Values":[[{"Literal":{"Value":"'Component 1'"}}]]}}}]}
```

### Page Filter: Activity.movement_type

`definition/pages/8b067ecb975e5af7a39b/page.json`

```json
{"Version":2,"From":[{"Name":"s","Entity":"Activity","Type":0}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"movement_type"}}],"Values":[[{"Literal":{"Value":"'RECEIPT'"}}]]}}}]}
```

### Visual Filter: Activity.event_day

`definition/pages/8b067ecb975e5af7a39b/visuals/a32b6a48db655ac8a4f2/visual.json`

```json
{"Version":2,"From":[{"Name":"s","Entity":"Activity","Type":0}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"event_day"}}],"Values":[[{"Literal":{"Value":"'2026-09-14'"}}]]}}}]}
```

### Slicer Selection: Items.product_name

`definition/pages/8b067ecb975e5af7a39b/visuals/d93c45218e8d5014b475/visual.json`

```json
{"Version":2,"From":[{"Name":"s","Entity":"Items","Type":0}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"product_name"}}],"Values":[[{"Literal":{"Value":"'Component 1'"}}]]}}}]}
```

### Slicer Selection: Locations.warehouse_name

`definition/pages/8b067ecb975e5af7a39b/visuals/f330a73cbbdf5467ae5c/visual.json`

```json
{"Version":2,"From":[{"Name":"s","Entity":"Locations","Type":0}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"warehouse_name"}}],"Values":[[{"Literal":{"Value":"'North'"}}]]}}}]}
```

The bookmark options in the collected context are:

```json
{
  "applyOnlyToTargetVisuals": false,
  "suppressData": false,
  "suppressDisplay": true,
  "suppressActiveSection": false
}
```

The default location is North; the bookmark switches to Coastal and retains
Component 1, page and visual predicates. suppressData is false: Data is enabled.

## Gaps, validation and stopping point

No missing or changed parts relative to the served publication definition.
**No collector gap for this fixture's predicates or bookmark.** Existing code
retains every returned definition part without a bookmark allowlist. This is
proven for this native fixture, not every report format or platform.

Validation: current context integrity and approval hashes checked; 17 engine
content calls reconstructed all 16 parts; six selection/filter ASTs resolved to
typed model columns; all collected parts structurally match publication; prior
records unchanged; required two generator tests passed. No full engine suite
was rerun for this evidence-only work.

[Structured receipts and fragments](runs/report-filter-discovery-receipt.json)
record IDs, hashes, physical reads, preservation and the failed attempt. Full
raw responses and model context remain in .local/report-filter-discovery-20261001/.

The reproduction test now has evidence to read. No filter capability, composition,
bookmark activation, browser rendering, reported-number comparison or lower-scope
translation was built or run. D's refusal remains unchanged. Stopped before
capability work; no new freeze, domain or acceptance claim.
