# Published report fixture: retained predicates

Date: 2026-10-01. Tracking: [#193](https://github.com/bcsnpc/data-investigation-agent/issues/193).
[Fidelity precondition and approved fixture plan](freshness-context-and-filter-fixture-plan.md).

The served definition retains real predicates in both slicer selections, the page
filter, the visual filter and the Data-enabled bookmark. It did not reduce them
to field references. This settles retention for this fixture and API route; it
does not prove that every report encoding is retained or that the investigator
can already reproduce it.

## Authorization, publication and baseline

#291 merged as `d93cebbdb4f63fbffc8241bf355d1b9146c712fd` after all six checks passed.
The user authorized only a separate report bound to the existing model. The one
create request returned HTTP202 and its operation completed successfully. No
publication failure or mutation retry occurred.

- Report: **Declared predicate fixture 20261001**, ID
  `2bc1cb2d-9230-4b8f-b7dc-c9f6b2151995`.
- Workspace: `149f8d99-1c66-4a0a-9624-759be002bb60`.
- Existing model: `3484a2bc-98c5-4cef-be5c-a6215484075e`.
- Publisher: **admin@skynwhy.com**, principal
  `23de217f-6e14-49cf-9acd-47dcd83cb82f`, verified from the actual Fabric access
  token's identity claims. Token/credentials are not retained in this report.
- Both baseline queries ran as **investigator-reader@skynwhy.com** and returned
  that identity with **Handled Quantity = 8,765 before and 8,765 after**.

The native before-read also established the selected existing values: North and
Coastal locations, Component 1, RECEIPT and event day 2026-09-14. Predicate values
were not guessed. No request edited an existing report, model, data, permission
or schedule; none refreshed/reframed the model. Baseline equality does not attest
served snapshots or prove currency.

The new report has an unfiltered control page and a selected page with two
slicers, a page-filtered companion card and an additionally visual-filtered card.
Four explicit DataFilter interactions connect both slicers to both selected-page
cards. There is no report-level filter or predicate on the control page/card.

## Served definition: exact predicate fragments

The first operation after create resolution was getDefinition. It returned
HTTP202; its completed operation supplied 16 parts. Fourteen submitted JSON
report parts are structurally identical to the returned parts. The service
rewrote definition.pbir to its own model connection format and added .platform.
The rewritten connection explicitly retains
`semanticmodelid=3484a2bc-98c5-4cef-be5c-a6215484075e`; it did not create a model.

These are actual served `filter` subtrees, not reconstructed predicates. `From`
binds source alias `s` to the named model entity; `Where.Condition.In` contains
the property and literal tuples. This is different from a `field` projection
with no `Where`/`Values`.

### Saved location slicer

`definition/pages/8b067ecb975e5af7a39b/visuals/f330a73cbbdf5467ae5c/visual.json`

```json
{"Version":2,"From":[{"Name":"s","Entity":"Locations","Type":0}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"warehouse_name"}}],"Values":[[{"Literal":{"Value":"'North'"}}]]}}}]}
```

### Saved product slicer

`definition/pages/8b067ecb975e5af7a39b/visuals/d93c45218e8d5014b475/visual.json`

```json
{"Version":2,"From":[{"Name":"s","Entity":"Items","Type":0}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"product_name"}}],"Values":[[{"Literal":{"Value":"'Component 1'"}}]]}}}]}
```

### Page filter

`definition/pages/8b067ecb975e5af7a39b/page.json`

```json
{"Version":2,"From":[{"Name":"s","Entity":"Activity","Type":0}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"movement_type"}}],"Values":[[{"Literal":{"Value":"'RECEIPT'"}}]]}}}]}
```

### Visual filter

`definition/pages/8b067ecb975e5af7a39b/visuals/a32b6a48db655ac8a4f2/visual.json`

```json
{"Version":2,"From":[{"Name":"s","Entity":"Activity","Type":0}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"event_day"}}],"Values":[[{"Literal":{"Value":"'2026-09-14'"}}]]}}}]}
```

### Bookmark location selection

`definition/bookmarks/3ea29d97240757cdb0d6.bookmark.json`

```json
{"Version":2,"From":[{"Name":"s","Entity":"Locations","Type":0}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":"warehouse_name"}}],"Values":[[{"Literal":{"Value":"'Coastal'"}}]]}}}]}
```

The bookmark retains the same product selection, page filter and target visual
filter, and changes the location selection from North to Coastal. Its exact
served options are:

```json
{
  "applyOnlyToTargetVisuals": false,
  "suppressData": false,
  "suppressDisplay": true,
  "suppressActiveSection": false
}
```

`suppressData: false` enables saved data/filter state. The bookmark identifies
the selected page and the actual slicer visual in explorationState; it is not
just a bookmark title. The control page has no filterConfig, and its card has no
filterConfig or slicer selection.

## Reads, validation and stopping point

Seven physical reads were metered: two reader DAX baseline/value reads, two
publisher operation GETs resolving creation, and three metadata requests fetching
and resolving the served definition. One separate create mutation makes eight
estate HTTP requests total. Ordinary rolling allowance stayed 60; usage moved
0 to 7, with no credits or policy increases and no model calls. Authentication
and Microsoft schema downloads are not estate value/metadata requests.

All 14 submitted JSON report parts validated against their Microsoft schemas and
referenced schemas before publication. A legacy RefResolver validation attempt
failed locally; modern reference resolution completed without schema alteration.
No failed local validation sent a publication request. The required two generator
tests passed; no engine code changed, so the previous 1,327-test run is historical
engine validation, not a suite rerun for this documentation receipt.

[Structured identity, HTTP receipts, served fragments and hashes](runs/report-filter-fixture-receipt.json)
retain the evidence. Full submitted/served parts and the durable create journal
remain in `.local/report-filter-fixture-20261001/`. The ledger appends one
ESTATE_FIXTURE_VERIFICATION row, not an investigation/acceptance pass.

No browser rendering, bookmark activation or contextual measure reproduction was
tested. Predicate retention is established; actual display behavior remains to
be evaluated. No rescan, approval change, intake, filter capability, filtered lower
comparison, fresh freeze or unfamiliar-domain claim was made. Discovery and
re-approval intentionally wait for the user's next decision.

Platform references: [Create Report](https://learn.microsoft.com/en-us/rest/api/fabric/report/items/create-report),
[PBIR files](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report),
[Microsoft bookmark schema](https://github.com/microsoft/json-schemas/blob/main/fabric/item/report/definition/bookmark/1.0.0/schema.json).
