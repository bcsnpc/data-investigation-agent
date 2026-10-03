# Value/descriptor reruns — preserved failures

Recorded 2026-10-02 America/Chicago (live execution 2026-10-03 UTC).

#311 merged at 71a3e2f; refusal registry #312 merged at 2578165; value/descriptor
#313 merged at cab41c6. Each had six green exact-head checks. The final #313 local
suite passed 1,580 tests in 420.438 seconds. All engine freezes remain invalid.

The three original tickets were attempted exactly once on that merged engine,
with planner recording enabled. No engine/adapter/fixture/config/policy/grant/cap
change, replacement run, batch credit, refund, reset or deadline extension.
Diagnostic cap remains four per run; rolling ordinary allowance remains 60.
Config/approval hash remains
`19e2ef0b0b5cb6bfd8df38c5fded6c1eaac40718b3926248ac62c61abf0cf8b6`.
Engine fingerprint:
`2cf2494bcca77d719b2a4774716dd949b00a92c0d5d609b5dd4c9f94d23c188f`.

**One delivered refusal; two HELD runs with BLOCKED synthesis. No reproduction
or acceptance pass.** R1 now produces both refusal narratives. R2/R3 expose a
report-scoped inventory sent to an unscoped synthesis consumer. Registered shape
coverage did not ensure that live producer/consumer payloads compose correctly.
The requirement that every refusal be delivered is still unmet on these paths.

Totals: nine physical DAX diagnostic requests (1 + 4 + 4), zero SQL/guard/other
requests, three intake calls, zero investigation-planner/judge/synthesis calls.
Ordinary rolling use 15 -> 24/60; earlier records naturally left the rolling
window, with no counter reset. Provider tokens: 43,184 input, 350 output;
4,500 output tokens reserved without refunds. Neither R2 nor R3 exceeded the
four-read cap; both stopped TOOL_UNAVAILABLE, not a cap increase or replacement.

## Batch map

| Run | Session | Physical / diagnostic / guards | Intake / investigation planner / synthesis | Terminal / synthesis | Delivered outputs |
| --- | --- | --- | --- | --- | --- |
| R1 | 1b64e3bb | 1 / 1 / 0 | 1 / 0 / 0 | COMPLETED / COMPLETED | Both refusal texts |
| R2 | fc2d3301 | 4 / 4 / 0 | 1 / 0 / 0 | HELD / BLOCKED | Neither |
| R3 | 5de14242 | 4 / 4 / 0 | 1 / 0 / 0 | HELD / BLOCKED | Neither |

All nine query receipts are SEALED; all three intake tapes captured request and
response with no recording exclusion. The ledger prefix and all original ticket
hashes were checked unchanged. These are recording/integrity checks, not surface
attestation or proof of reproduction.

## Original read counts: why 1, 0, 0

The original R1 had a scoped visual grouping on warehouse_name, so the whole
phrase `warehouse North` could be tested in one bounded existence lookup.
Original R2/R3 were cards without a grouping column and had no ACTIVE literal
matching that whole phrase, so they refused before reading. This was **not a
memo or cache**. The new North literal matches an ACTIVE declaration in the
fixture report, so R2/R3 resolve with zero existence reads; R1 still needs one.
The descriptor never chooses a column. Existing compiled-read memoization is
per adapter/run and fingerprinted by compiled scope and pinned context; it did
not account for the original zero-read refusals.

## Fixture authorship, independent arithmetic and honesty

R2's EMPTY and R3's exact 9 remain fixture-authored, not observed user figures.
The original independent arithmetic is preserved in the run-round derivation:
full active set RECEIPT + North + Component 1 + 2026-09-14. The seeded matching
warehouse/product movement 300 has nine units but type ISSUE, so RECEIPT excludes
it; no rows remain and SUM is BLANK, not zero. No engine compiled-query answer
was transcribed to author either ticket. The notebook seed hash remains
`3a980c4bd1920343202174c26b357be6233c6db267409d226d6a95fca4694273`.

There was no successful reproduction, so no first-attempt match to certify.
The arithmetic does not guarantee a native match: wrong seeded data, definition
retention, active-scope selection, compiler application, serving state or
attestation could all prevent it. Here all retained probes lack self-report,
and candidate reproduction never reaches its restricted probe.

The retained intake proposals do not include a page/visual definition_target;
the envelope carries report_binding and selection_request instead. This batch
therefore does not establish faithful addressing of the ticket's named card.
No authored numeric figure was substituted, no ambiguity was guessed away.

Artifacts remain under `.local/value-descriptor-reruns-20261002/`, with original
request/response recordings under `.local/planner-recordings/`, sealed receipts
in the existing catalog, and exactly one appended ledger row per run. Original
#311 runs and #312 offline counterfactuals remain unchanged. Read-only audits
inspect existing originals and admit no model or estate request.


## R1: 1b64e3bb-89dd-4ddc-af0a-9d2e80506431

Ticket (byte-identical to the original):

> In Inventory Health e1b8e1 I selected warehouse North. Handled Quantity differs from the global total. Check the North selection and explain what report context you can and cannot reproduce.

Intake 23d3072c-e235-4d89-bb6d-13287932f30f: PROPOSED, one call. Value `North`; separately quoted descriptor `warehouse`, never a binding source. Reported state: `UNSPECIFIED`. Original spans remain in the saved proposal.

Session: **COMPLETED**, stop `ENOUGH_DIAGNOSTICS`; recorded assessment: `NO_KNOWN_PATTERN`. Synthesis: **COMPLETED**, 0 provider calls. Investigation planner: 0; judge: zero. Physical/diagnostic reads: 1/1 against diagnostic cap 4; SQL/guards/other: zero. Ordinary rolling usage 15 -> 16/60. Intake tokens: 14379 input, 111 output; output reservation 1,500, not refunded.

### Inventory and resolution

Resolution stopped before an inventory marker was retained. No run-level inventory conservation or active set is claimed. R1 had a scoped grouping column, enabling a single existence lookup. `North` was measured as present, but the observation had no surface self-report and could not authorize resolution. The descriptor remained NOT_EVALUATED. R1 supplied no reported figure, but the earlier selection refusal prevented it from reaching the no-figure reproduction check.

### Every physical probe

All declared the same route: engine OLAP Server, workspace `149f8d99-1c66-4a0a-9624-759be002bb60`, model `3484a2bc-98c5-4cef-be5c-a6215484075e`, reader `investigator-reader@skynwhy.com`. Every retained probe had `surface_report: null`, MISSING / UNKNOWN consistency / NONE coverage, reason SURFACE_SELF_REPORT_MISSING; engine, connection, object and identity were unattested. Request/result seals and raw worker responses are preserved locally. No value is independently surface-attested.

| Receipt | Purpose | Retained result | Attestation |
| --- | --- | --- | --- |
| f4164fc3-ab60-4401-8abd-a45369403688 | value existence | `[{"[quantity]":{"type":"decimal","value":"1"}}]` | MISSING |



The three candidate values 8,765 in R2/R3 are undeclared-context evaluations, never unrestricted totals. The later scoped baseline is 3,359. Neither supplies the missing reproduced quantity. No cross-surface or within-layer COMPARISON was established; separate reads are not a comparison.

### Boundaries and limits

All four path boundaries stayed unchecked: model Activity -> declared movement_values source; that source -> its stock-movements input; that input -> its earlier stock-movements input; and the final unresolved application boundary. R1 stopped at selection resolution. R2/R3 refused filtered lower reads (`Declared source comparison does not yet translate filtered scope faithfully.`; deeper `Declared quantity trace supports only whole-entity scope without filters or grouping.`); the final upstream source is undeclared. The filtered-scope refusal is unchanged. No lower surface, snapshot alignment, refresh timing, intended semantics or explanation was established.

### Business output — verbatim

```text

You asked: In Inventory Health e1b8e1 I selected warehouse North. Handled Quantity differs from the global total. Check the North selection and explain what report context you can and cannot reproduce.
Answer to your question: Not answered.

The investigation stopped during selection resolution.
Reason: Target ambiguity: value-existence observation unavailable for fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name.
No explanation of the reported difference was established.
Recommended action: Resolve the stated blocker before a new investigation.
You described the selected value as "warehouse"; that description was a hint, not a reason to choose a column.

```

### Technical output — verbatim

```text

You asked: In Inventory Health e1b8e1 I selected warehouse North. Handled Quantity differs from the global total. Check the North selection and explain what report context you can and cannot reproduce.
Answer to your question: Not answered.

The investigation stopped during selection resolution.
Reason: Target ambiguity: value-existence observation unavailable for fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name.
No explanation of the reported difference was established.
Recommended action: Resolve the stated blocker before a new investigation.
You described the selected value as "warehouse"; that description was a hint, not a reason to choose a column.

```

## R2: fc2d3301-ee27-464f-83cd-892ee40604fe

Ticket (byte-identical to the original):

> In Declared predicate fixture 20261001, on Saved predicate selections, the card Handled Quantity - extra visual predicate shows nothing (the visual is empty) for Handled Quantity. I selected warehouse North. Check whether the saved declared report context reproduces what the visual shows and explain what remains unknown about my selections.

Intake becdb96b-e43a-4a8e-8237-00f74dbb19ab: PROPOSED, one call. Value `North`; separately quoted descriptor `warehouse`, never a binding source. Reported state: `EMPTY`. Original spans remain in the saved proposal.

Session: **HELD**, stop `TOOL_UNAVAILABLE`; recorded assessment: `None`. Synthesis: **BLOCKED**, 0 provider calls. Investigation planner: 0; judge: zero. Physical/diagnostic reads: 4/4 against diagnostic cap 4; SQL/guards/other: zero. Ordinary rolling usage 16 -> 20/60. Intake tokens: 14405 input, 118 output; output reservation 1,500, not refunded.

### Retained inventory and active restrictions

Resolution validated these report-scoped inventories in the engine; the read-only audit revalidated the original resolution against original observations. Nine DISTINCT declarations appear in each candidate inventory, not 27 distinct declarations. Synthesis did NOT validate the inventory.

| Candidate | Discovered | ACTIVE | CONDITIONAL | UNSUPPORTED |
| --- | ---: | ---: | ---: | ---: |
| 1 | 9 | 0 | 9 | 0 |
| 2 | 9 | 3 | 6 | 0 |
| 3 | 9 | 4 | 5 | 0 |



Candidate 1 is the unfiltered control (0 active). Candidate 2 uses the page RECEIPT predicate plus saved Component 1 and North slicer defaults (3 active). Candidate 3 adds the 2026-09-14 visual predicate (4 active). Slicer defaults are ACTIVE / VIEWER_CHANGEABLE / SAVED_DEFAULT; page and visual predicates are fixed. Bookmark alternatives are CONDITIONAL and excluded. North binds by an exact ACTIVE literal, not by the descriptor. The hint records textual agreement only after resolution.

No restricted evaluation or reproduced value was established. The procedure tried an undeclared-context probe for each candidate, found the probe unavailable for attestation, and never admitted the restricted partner. It later retained `DECLARED_CONTEXT_REPRODUCTION_UNAVAILABLE`: **No addressable candidate visual.** Authored figure: EMPTY for R2, exact 9 for R3. These runs cannot be graded reproduction or non-reproduction.

### Every physical probe

All declared the same route: engine OLAP Server, workspace `149f8d99-1c66-4a0a-9624-759be002bb60`, model `3484a2bc-98c5-4cef-be5c-a6215484075e`, reader `investigator-reader@skynwhy.com`. Every retained probe had `surface_report: null`, MISSING / UNKNOWN consistency / NONE coverage, reason SURFACE_SELF_REPORT_MISSING; engine, connection, object and identity were unattested. Request/result seals and raw worker responses are preserved locally. No value is independently surface-attested.

| Receipt | Purpose | Retained result | Attestation |
| --- | --- | --- | --- |
| d7c5ae17-94fb-4cbd-a043-3f417737dc54 | declared_context_read | `[{"[quantity]":{"type":"decimal","value":"8765"}}]` | MISSING |
| 37764631-4126-4c94-9a51-e97b75ee47ec | declared_context_read | `[{"[quantity]":{"type":"decimal","value":"8765"}}]` | MISSING |
| 4e608d41-e4fc-4086-88a2-bd6944018c50 | declared_context_read | `[{"[quantity]":{"type":"decimal","value":"8765"}}]` | MISSING |
| 602e065a-ed55-439c-a38f-62a27b0d9f3f | baseline, established | `[{"[m0]":{"type":"decimal","value":"3359"}}]` | MISSING |



The three candidate values 8,765 in R2/R3 are undeclared-context evaluations, never unrestricted totals. The later scoped baseline is 3,359. Neither supplies the missing reproduced quantity. No cross-surface or within-layer COMPARISON was established; separate reads are not a comparison.

### Boundaries and limits

All four path boundaries stayed unchecked: model Activity -> declared movement_values source; that source -> its stock-movements input; that input -> its earlier stock-movements input; and the final unresolved application boundary. R1 stopped at selection resolution. R2/R3 refused filtered lower reads (`Declared source comparison does not yet translate filtered scope faithfully.`; deeper `Declared quantity trace supports only whole-entity scope without filters or grouping.`); the final upstream source is undeclared. The filtered-scope refusal is unchanged. No lower surface, snapshot alignment, refresh timing, intended semantics or explanation was established.

### Synthesis failure

Original saved failure category: `ValueError` before any provider call. Read-only validation of the ORIGINAL state identifies: **Declaration inventory is malformed**. The report-scoped inventory has `discovered`, `entries`, `report_id`; `_context_evidence()` passes it to the unscoped `declaration_inventory.validate()`, which permits exactly `discovered`, `entries`. This is a consumer-contract mismatch, not an unsupported native form. The original failure and lack of outputs remain unchanged. No synthesis rerun, fixture change or mid-batch engine fix was performed.

### Business output — verbatim

**NOT GENERATED.** Synthesis was BLOCKED; there is no output text to quote. No retrospective text is substituted for it.

### Technical output — verbatim

**NOT GENERATED.** Synthesis was BLOCKED; there is no output text to quote. No retrospective text is substituted for it.

## R3: 5de14242-4f27-43e8-8b3a-b548df56fea9

Ticket (byte-identical to the original):

> In Declared predicate fixture 20261001, on Saved predicate selections, the card Handled Quantity - extra visual predicate shows 9 for Handled Quantity. I selected warehouse North. Check whether the saved declared report context reproduces what the visual shows and explain what remains unknown about my selections.

Intake 1b2d1967-f2aa-4eb9-bcd6-3799ac3b63bd: PROPOSED, one call. Value `North`; separately quoted descriptor `warehouse`, never a binding source. Reported state: `NUMBER`. Original spans remain in the saved proposal.

Session: **HELD**, stop `TOOL_UNAVAILABLE`; recorded assessment: `None`. Synthesis: **BLOCKED**, 0 provider calls. Investigation planner: 0; judge: zero. Physical/diagnostic reads: 4/4 against diagnostic cap 4; SQL/guards/other: zero. Ordinary rolling usage 20 -> 24/60. Intake tokens: 14400 input, 121 output; output reservation 1,500, not refunded.

### Retained inventory and active restrictions

Resolution validated these report-scoped inventories in the engine; the read-only audit revalidated the original resolution against original observations. Nine DISTINCT declarations appear in each candidate inventory, not 27 distinct declarations. Synthesis did NOT validate the inventory.

| Candidate | Discovered | ACTIVE | CONDITIONAL | UNSUPPORTED |
| --- | ---: | ---: | ---: | ---: |
| 1 | 9 | 0 | 9 | 0 |
| 2 | 9 | 3 | 6 | 0 |
| 3 | 9 | 4 | 5 | 0 |



Candidate 1 is the unfiltered control (0 active). Candidate 2 uses the page RECEIPT predicate plus saved Component 1 and North slicer defaults (3 active). Candidate 3 adds the 2026-09-14 visual predicate (4 active). Slicer defaults are ACTIVE / VIEWER_CHANGEABLE / SAVED_DEFAULT; page and visual predicates are fixed. Bookmark alternatives are CONDITIONAL and excluded. North binds by an exact ACTIVE literal, not by the descriptor. The hint records textual agreement only after resolution.

No restricted evaluation or reproduced value was established. The procedure tried an undeclared-context probe for each candidate, found the probe unavailable for attestation, and never admitted the restricted partner. It later retained `DECLARED_CONTEXT_REPRODUCTION_UNAVAILABLE`: **No addressable candidate visual.** Authored figure: EMPTY for R2, exact 9 for R3. These runs cannot be graded reproduction or non-reproduction.

### Every physical probe

All declared the same route: engine OLAP Server, workspace `149f8d99-1c66-4a0a-9624-759be002bb60`, model `3484a2bc-98c5-4cef-be5c-a6215484075e`, reader `investigator-reader@skynwhy.com`. Every retained probe had `surface_report: null`, MISSING / UNKNOWN consistency / NONE coverage, reason SURFACE_SELF_REPORT_MISSING; engine, connection, object and identity were unattested. Request/result seals and raw worker responses are preserved locally. No value is independently surface-attested.

| Receipt | Purpose | Retained result | Attestation |
| --- | --- | --- | --- |
| 941741bd-2648-4479-835f-401e86a7ee96 | declared_context_read | `[{"[quantity]":{"type":"decimal","value":"8765"}}]` | MISSING |
| a458d8d9-e9c8-4163-83a4-d7da1b3f5e64 | declared_context_read | `[{"[quantity]":{"type":"decimal","value":"8765"}}]` | MISSING |
| 083412d1-0f99-4ff2-a2ea-62bfb1ed09e1 | declared_context_read | `[{"[quantity]":{"type":"decimal","value":"8765"}}]` | MISSING |
| 37bf51c0-743f-4777-9fb8-202052ad638f | baseline, established | `[{"[m0]":{"type":"decimal","value":"3359"}}]` | MISSING |



The three candidate values 8,765 in R2/R3 are undeclared-context evaluations, never unrestricted totals. The later scoped baseline is 3,359. Neither supplies the missing reproduced quantity. No cross-surface or within-layer COMPARISON was established; separate reads are not a comparison.

### Boundaries and limits

All four path boundaries stayed unchecked: model Activity -> declared movement_values source; that source -> its stock-movements input; that input -> its earlier stock-movements input; and the final unresolved application boundary. R1 stopped at selection resolution. R2/R3 refused filtered lower reads (`Declared source comparison does not yet translate filtered scope faithfully.`; deeper `Declared quantity trace supports only whole-entity scope without filters or grouping.`); the final upstream source is undeclared. The filtered-scope refusal is unchanged. No lower surface, snapshot alignment, refresh timing, intended semantics or explanation was established.

### Synthesis failure

Original saved failure category: `ValueError` before any provider call. Read-only validation of the ORIGINAL state identifies: **Declaration inventory is malformed**. The report-scoped inventory has `discovered`, `entries`, `report_id`; `_context_evidence()` passes it to the unscoped `declaration_inventory.validate()`, which permits exactly `discovered`, `entries`. This is a consumer-contract mismatch, not an unsupported native form. The original failure and lack of outputs remain unchanged. No synthesis rerun, fixture change or mid-batch engine fix was performed.

### Business output — verbatim

**NOT GENERATED.** Synthesis was BLOCKED; there is no output text to quote. No retrospective text is substituted for it.

### Technical output — verbatim

**NOT GENERATED.** Synthesis was BLOCKED; there is no output text to quote. No retrospective text is substituted for it.
