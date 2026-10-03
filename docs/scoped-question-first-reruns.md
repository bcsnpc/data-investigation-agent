# Scoped, question-first live reruns

Recorded 2026-10-03 UTC (2026-10-02 America/Chicago). Three KNOWN_DOMAIN_REGRESSION attempts, one per unchanged saved ticket. This report records failed delivery; it is not frozen or unfamiliar-domain acceptance.

## Merged implementation and validation

- PR C [#318](https://github.com/bcsnpc/data-investigation-agent/pull/318) merged as `dad5ba73e7c9236ed8b08c0c8655a0a54df07363` after all six checks passed. Successful identical compiled native probes reuse the original sealed receipt within the run; declared evaluations precede baselines; cap-stopped probes retain names and purposes.
- PR D [#319](https://github.com/bcsnpc/data-investigation-agent/pull/319) merged as `e8c33a02b38f53fe9c8bcc374b131d23f7ebe315` after all six checks passed. The final local suite passed **1,607 tests**. Earlier suite and CI failures remain recorded. The unscoped inventory validator was deleted; twelve call sites in seven modules use the scoped validator, guarded by an AST test. Business refusal rendering now uses the shared identifier-form guard; unavailable checks, ambiguous targets and completed value absence retain distinct categories.
- #312 supplied receipt recognition/dispatch vocabulary, not inventory content validation. Synthesis still called an obsolete content validator. Inventory content stays under one scoped validator rather than a second schema inside the registry. See [implementation audit](scoped-inventory-and-refusals.md).
- Engine changes invalidate prior freezes. No engine or adapter change occurred during this batch.

## Conditions and preservation

The three ticket files match their original saved bytes. No configuration, approval, policy, permission, fixture, schedule, credit, cap or counter change; no rescan, replacement run or deadline extension. The model profile remains GPT-5.4 medium reasoning, 8,000 output tokens, 120-second timeout and 48,000 input characters per call. Dynamic limits remain four diagnostic reads and 384,000 cumulative input characters.

Context: `3ae7607b-5a5e-46c6-8e1b-195dbabc9cae`. Approved configuration hash: `19e2ef0b0b5cb6bfd8df38c5fded6c1eaac40718b3926248ac62c61abf0cf8b6`. Engine hash: `ecb59a0186d954dc4f9763f5ba8370c62e25f05131ddf1b895b8421b4dbff1df`.

One initial R1 application launch used the worker virtual environment and failed to import jsonschema before intake, session creation, admission, model calls or reads. Its startup log is preserved. The actual application then launched with the existing application Python and configured native worker, without dependency changes. This was not a replacement investigation.

Artifacts remain under `.local/scoped-question-reruns-20261003/`: original ticket bytes, intake proposals, session JSON, before/after usage snapshots, logs, ledger rows, read-only receipt audits and synthesis failure audits. Recording was enabled. All three intake tapes captured both request and response, with no exclusion and no provider error. Recording directories: R1 `8dbaff69-659a-49a4-b6bd-d02aff2d7c0b`, R2 `ba6769d7-c1ad-46af-bc52-edd8b2700732`, R3 `4a94e35a-34a1-4dad-a0c9-7e5999dd6ff6`. There was no later provider call to record. Three ledger rows were appended to [the ledger](runs/ledger.jsonl); historical rows remain untouched.

## Budget and delivery summary

| Run | Session | Physical / diagnostic / cap | Guard / SQL / other | Intake / investigation planner / judge / synthesis calls | Zero-cost reuse events | Result |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | `f04a8af5-37df-4e64-aa80-a4f576956f6a` | 4 / 4 / 4 | 0 / 0 / 0 | 1 / 0 / 0 / 0 | 4 | HELD / TOOL_UNAVAILABLE; no assessment |
| R2 | `d831c404-ea07-4d0b-bd7b-1f9b9c2cbe36` | 4 / 4 / 4 | 0 / 0 / 0 | 1 / 0 / 0 / 0 | 3 | COMPLETED / NO_COMPARABLE_PATH; synthesis BLOCKED |
| R3 | `6875ffa2-cece-49e4-8338-05197ea69f32` | 4 / 4 / 4 | 0 / 0 / 0 | 1 / 0 / 0 / 0 | 3 | COMPLETED / NO_COMPARABLE_PATH; synthesis BLOCKED |

Rolling physical usage: **26 ? 30 ? 34 ? 38 of 60**. Total: twelve physical DAX diagnostic requests, no overhead requests, three intake calls, zero investigation-planner/judge/synthesis-provider calls. Actual model usage: 43,184 input and 363 output tokens; 4,500 output tokens reserved, with no refunds. All selected declared evaluations and shared baselines were obtained. No additional selected declared probe was blocked by the read cap.

**No business or technical narrative was generated for any run.** The saved assessments in R2/R3 are structured process findings, not validated narrative outputs. There are six absent outputs, so there is no verbatim narrative to quote. No offline substitute was generated.

## Every physical probe: execution surface and attestation

Every row below is a DAX value-query probe against the same model. The original receipt for every row self-reports exactly **engine `OLAP Server`, identity `investigator-reader@skynwhy.com`, object `3484a2bc-98c5-4cef-be5c-a6215484075e`** in the value statement. These are quoted from each receipt, not inferred from the execution profile. Each attestation has consistency `MATCHED` but coverage **`PARTIAL`**: engine, identity and object attested; connection `149f8d99-1c66-4a0a-9624-759be002bb60` remains **`UNATTESTED`**. Required three-field self-report is present. This is not full surface attestation or snapshot verification.

| Run | Probe / role | Original receipt | Value | Engine / identity / object self-report | Attestation |
| --- | --- | --- | --- | --- | --- |
| R1 | North value existence | `7bd40167-1c55-46af-affd-ee3e2c8d63dd` | 1 (exists) | `OLAP Server` / `investigator-reader@skynwhy.com` / `3484a2bc-98c5-4cef-be5c-a6215484075e` | PARTIAL; connection unattested |
| R1 | Ungrouped declared; shared undeclared/TOTAL | `e1250b5b-9103-4248-8c72-9cd44f6b9ae4` | 8765 | `OLAP Server` / `investigator-reader@skynwhy.com` / `3484a2bc-98c5-4cef-be5c-a6215484075e` | PARTIAL; connection unattested |
| R1 | North KEYED declared | `ecc5a1fa-d451-45e3-9c28-1f17f10b06fa` | 3359 | `OLAP Server` / `investigator-reader@skynwhy.com` / `3484a2bc-98c5-4cef-be5c-a6215484075e` | PARTIAL; connection unattested |
| R1 | Normal vertical North baseline | `aa53f7d0-d0f6-4124-ba86-bc8c78f9b927` | 3359 | `OLAP Server` / `investigator-reader@skynwhy.com` / `3484a2bc-98c5-4cef-be5c-a6215484075e` | PARTIAL; connection unattested |
| R2 | Control declared; shared undeclared | `481b8698-9461-4d25-a2e1-af1e1e7a7d6c` | 8765 | `OLAP Server` / `investigator-reader@skynwhy.com` / `3484a2bc-98c5-4cef-be5c-a6215484075e` | PARTIAL; connection unattested |
| R2 | Page-and-slicer declared | `4c11d5b9-32cd-497c-9620-55d8a1c8aa61` | 92 | `OLAP Server` / `investigator-reader@skynwhy.com` / `3484a2bc-98c5-4cef-be5c-a6215484075e` | PARTIAL; connection unattested |
| R2 | Full page/visual/slicer declared | `84f553bd-5200-4724-bf76-3744f1b06ab2` | BLANK | `OLAP Server` / `investigator-reader@skynwhy.com` / `3484a2bc-98c5-4cef-be5c-a6215484075e` | PARTIAL; connection unattested |
| R2 | Normal vertical North baseline | `086de50b-c61f-4b86-ae05-c23fe3504b64` | 3359 | `OLAP Server` / `investigator-reader@skynwhy.com` / `3484a2bc-98c5-4cef-be5c-a6215484075e` | PARTIAL; connection unattested |
| R3 | Control declared; shared undeclared | `a32e71eb-e2e4-4216-93e8-2b0b1b2ceb62` | 8765 | `OLAP Server` / `investigator-reader@skynwhy.com` / `3484a2bc-98c5-4cef-be5c-a6215484075e` | PARTIAL; connection unattested |
| R3 | Page-and-slicer declared | `2dd4e8f9-6329-49ca-8811-dd28f7d7aa64` | 92 | `OLAP Server` / `investigator-reader@skynwhy.com` / `3484a2bc-98c5-4cef-be5c-a6215484075e` | PARTIAL; connection unattested |
| R3 | Full page/visual/slicer declared | `ba04e8f3-7aac-406c-934e-7ea1d106c56c` | BLANK | `OLAP Server` / `investigator-reader@skynwhy.com` / `3484a2bc-98c5-4cef-be5c-a6215484075e` | PARTIAL; connection unattested |
| R3 | Normal vertical North baseline | `29ff57ce-c9d6-4de4-86a9-649674eaaeaf` | 3359 | `OLAP Server` / `investigator-reader@skynwhy.com` / `3484a2bc-98c5-4cef-be5c-a6215484075e` | PARTIAL; connection unattested |

Reused probes retain these original receipts and distinct COMPILED_DUPLICATE_REFUSED events, with no extra read or budget charge. All comparisons here are **WITHIN_LAYER_CHECK**, with zero cross-surface comparisons and zero verified lower boundaries. Neither surface reports a served snapshot version. The undeclared-context value remains subject to RLS and other native restrictions; it is not an unrestricted or true total.

## R1 ? no reported figure, observed North

Ticket SHA-256: `af4602acdd2a6c8bdb74892a86c4346ac957ba2ed158aeb108412f1952959e84`. Report resolves **STATED** from the exact ticket quote `Inventory Health e1b8e1` (span 3?26), report `692f3ead-d1d1-4f7f-984b-51e54f3e7497`. `North` (span 48?53) resolves **OBSERVED** through the attested existence receipt, against `Locations.warehouse_name`, a grouping column in that report. The separate descriptor `warehouse` is a nonbinding hint; it does not choose the column.

Two report-scoped candidate inventories each contain **1 discovered = 1 ACTIVE + 0 CONDITIONAL + 0 UNSUPPORTED**, independently accepted by engine validation against original retained evidence. They refer to the same single declaration, not two distinct declarations. The ACTIVE saved unselected slicer is FULL_DOMAIN, VIEWER_CHANGEABLE, SAVED_DEFAULT; it creates no enumerated value restriction. The North KEYED cell adds its resolved cell key.

| Cell | Undeclared-context value | Declared/cell value | Reported state | Comparison |
| --- | --- | --- | --- | --- |
| Ungrouped visual 25189fcc5fe05539b3b6 | 8,765 | 8,765 | UNSPECIFIED | Unavailable: No reported figure supplied. |
| North KEYED row, visual d21708a8bc35561c81f5 | 8,765 | 3,359 | UNSPECIFIED | Unavailable: No reported figure supplied. |
| TOTAL row, same table visual | 8,765 | 8,765 | UNSPECIFIED | Unavailable: No reported figure supplied. |

Precision is inapplicable: no figure was supplied. The no-reported-figure reason is retained for every cell, rather than an inventory complaint. The session nevertheless ended **HELD / TOOL_UNAVAILABLE** with a retained process `ValueError`, no final assessment and fallback UNRESOLVED. This is not the requested delivered refusal.

Synthesis independently failed before provider dispatch with **`ValueError: Cell identity differs from original definition/read receipts`**. The KEYED and TOTAL markers both point to definition receipt `declared-context-0002be0e-e896-4a4d-b1bc-09d0da1f8db1`; the retained definition carries the KEYED cell, while the TOTAL marker carries a different TOTAL cell identity. The original validator correctly rejects this mismatch. The separate underlying process ValueError retains only its category; this report does not invent a more specific live cause.

Business output: **NOT_GENERATED**. Technical output: **NOT_GENERATED**.

## R2 ? fixture-authored EMPTY

Ticket SHA-256: `c85cf7e9c521e40738855c70558f4b5d397e88df3a808bc932ef4f57a62275be`. Report resolves **STATED** from `Declared predicate fixture 20261001` (span 3?38), report `2bc1cb2d-9230-4b8f-b7dc-c9f6b2151995`. North resolves **EVIDENCE** from ACTIVE inventory entry `cac9aa35a4dcb793f149c5becc22516d005b2935d46e003475e9533f9f5d1ab0`, not a new existence read. Its ticket quote is `North` (span 201?206).

Reported state **EMPTY**, sourced from span 71?157: `the card Handled Quantity - extra visual predicate shows nothing (the visual is empty)`. EMPTY is not zero and has no numeric precision.

## Shared R2/R3 inventory and active restrictions

Three candidate-scoped inventories each conserve **9 discovered** declarations; these are views of the same nine original declarations, not 27 distinct declarations. Engine inventory and resolution validation against original retained observations succeeds.

| Candidate | ACTIVE | CONDITIONAL | UNSUPPORTED | Declared value |
| --- | --- | --- | --- | --- |
| Control c35f95e493de5d258b64 | 0 | 9 | 0 | 8,765 |
| Page card 7b8db703ca845710aca9 | 3 | 6 | 0 | 92 |
| Full visual a32b6a48db655ac8a4f2 | 4 | 5 | 0 | BLANK |

| Restriction | Applicability | Volatility / assumption |
| --- | --- | --- |
| Activity.movement_type IN RECEIPT | ACTIVE on page and full visual | FIXED / NONE |
| Items.product_name IN Component 1 | ACTIVE on page and full visual, saved slicer | VIEWER_CHANGEABLE / SAVED_DEFAULT |
| Locations.warehouse_name IN North | ACTIVE on page and full visual, saved slicer | VIEWER_CHANGEABLE / SAVED_DEFAULT |
| Activity.event_day IN 2026-09-14 | ACTIVE on full visual only | FIXED / NONE |
| Stored bookmark predicates and declarations outside each candidate scope | CONDITIONAL; retained and excluded | Invocation/applicability not established |

The shared undeclared-context value is **8,765**, never labelled the total/unrestricted value. In R2 the full visual returns native **BLANK**, yielding a retained **REPRODUCED EMPTY** marker; the other two candidates do not reproduce EMPTY. The normal North baseline is 3,359. Overall process classification is **NO_COMPARABLE_PATH**, because lower filtered-scope comparisons remain unsupported; the reproduction is a within-layer side finding, not a presentation verdict.

Evidence validation passes, but synthesis admission blocks the **90,146-character** digest against the unchanged **48,000-character** per-call bound (42,146 over). The evidence field alone is 83,228 characters. No synthesis provider call occurred.

The retained qualifier says: **?The check assumes saved default positions for viewer-changeable selections; their current positions were not established.?** It was not delivered in either output, because neither output exists. The requested weaker-claim rendering and business non-confirmation are therefore not demonstrated by this run.

Business output: **NOT_GENERATED**. Technical output: **NOT_GENERATED**.

## R3 ? fixture-authored exact 9

Ticket SHA-256: `a49412fa60ec95d487b225cb28bf710a288ab6448fd1a094390e2fddadfd8bc4`. Same report and target provenance as R2, with North source span 173?178. Reported state **NUMBER**, value **9**, precision **EXACT**, source span 122?150: `shows 9 for Handled Quantity`.

The candidate values are 8,765, 92 and BLANK against exact 9; all three markers are **NOT_REPRODUCED**. BLANK is a completed legitimate result, not unavailable and not zero. Undeclared-context value 8,765; normal North baseline 3,359. Overall process classification **NO_COMPARABLE_PATH** for the unchanged filtered lower-boundary refusal. It does not explain the authored figure or establish PRESENTATION_LOGIC.

The retained open set explicitly names: **?A moved slicer or other saved-default selection remains an explicit possibility; its current position was not established.?** Invoked bookmark, user selection, RLS and genuine deeper divergence remain unexcluded. This is retained evidence, not a delivered narrative.

Evidence validation passes, but the **90,082-character** digest exceeds **48,000** by 42,082; its evidence field is 83,191 characters. Synthesis blocks before provider dispatch. Business output: **NOT_GENERATED**. Technical output: **NOT_GENERATED**.

## Lower boundaries and limits

No lower layer was read and no actual cross-surface boundary was compared. R2/R3 retain all four unchecked boundaries:

1. Presentation Activity ? declared movement_values: filtered source comparison cannot be translated faithfully.
2. movement_values ? middle stock_movements: quantity trace supports whole-entity scope only; filtered scope refused.
3. Middle stock_movements ? earlier stock_movements: same filtered-scope limitation.
4. Earlier stock_movements ? application: no resolvable declared upstream connection for literal initialisation/unsupported derived column; application source remains unresolved.

R1 retains the first three NOT_COMPARABLE results, then the walk refuses; the fourth was not reached. Snapshot, RLS/current selection and cross-filtering remain unknown. No freshness, ingestion, job-history or definition-judge read/call occurred. Neither business correctness nor currency is established.

## Honesty check and remaining findings

The existing independent derivation used seeded Bronze rows rather than transcribing an engine query. Seed hash `3a980c4bd1920343202174c26b357be6233c6db267409d226d6a95fca4694273`. Under North, Component 1 and 2026-09-14, the candidate seed row is movement 300, warehouse 1, product 1, units 9, type ISSUE. The additional ACTIVE RECEIPT page filter excludes it, leaving no rows; SUM should return BLANK. Both EMPTY and exact 9 were fixture-authored, not observed from a user. The derivation stays outside runtime context.

- R1 could have differed if North were absent, multiple report-scoped grouping columns matched, the existence probe were unavailable, or cell/measure context yielded different values. The implementation did not guarantee observed resolution. Its retained no-figure result matches the expected absence, but delivery failed.
- R2 could have failed reproduction if served data differed from the seeded rows, predicates were lost/misclassified, compiled intersections or relationships differed, the measure coalesced BLANK to zero, or attestation failed. Arithmetic predicts the fixture result; it does not force the live native result. The full-set BLANK comparison executed, but end-to-end qualification delivery did not.
- R3 could have reproduced 9 if the served data, applied context or measure differed so that the full native result was 9. No branch forced non-reproduction. The observed BLANK supports a non-reproduction marker, but the required open-set output did not deliver.

The successful memoisation, full active-set native evaluation and scoped conservation do not amount to a completed capability. New defects/limits are recorded without an engine fix or cap increase: R1 per-cell definition identity reuse, and R2/R3 oversized original-evidence synthesis digests. A bounded, validation-preserving digest design requires separate work; silent evidence loss is not an acceptable remedy. All three failed deliveries remain unchanged. Stop after this report; fixture change and further runs remain deferred.
