| Family | Prior outcome | New outcome | Reproduction result | Figure state | Diagnostic / physical reads | Planner / judge / synthesis calls | Both outputs produced |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | UNRESOLVED / BUDGET_LIMIT | UNRESOLVED / NO_PROGRESS | Not entered: horizontal route | UNSPECIFIED | 3 / 3 | 9 / 0 / 0 | No: BLOCKED |
| B | NO_COMPARABLE_PATH | NOT RUN: rolling window | Not measured | Not interpreted | 0 / 0 | 0 / 0 / 0 | No attempt |
| C | Resolver ValueError | NOT RUN: rolling window | Not measured | Not interpreted | 0 / 0 | 0 / 0 / 0 | No attempt |
| D | NO_COMPARABLE_PATH | NO_KNOWN_PATTERN / ENOUGH_DIAGNOSTICS | No figure; computed two cells | UNSPECIFIED | 4 / 4 | 0 / 0 / 1 | No: FAILED |
| E | TRANSFORMATION_LOGIC | UNRESOLVED / PROCESS_FAILED | No persisted finding | UNSPECIFIED | 4 / 4 | 0 / 0 / 0 | Yes |
| F | CONSISTENT_TO_BOUNDARY | NOT RUN: rolling window | Not measured | Not interpreted | 0 / 0 | 0 / 0 / 0 | No attempt |
| G | TRANSFORMATION_LOGIC | UNRESOLVED / PROCESS_FAILED | No persisted finding | UNSPECIFIED | 4 / 4 | 0 / 0 / 0 | Yes |
| H | H_COST_GUARD; later NO_PROGRESS | NO_KNOWN_PATTERN / ENOUGH_DIAGNOSTICS | No figure; computed two cells | UNSPECIFIED | 4 / 4 | 0 / 0 / 1 | No: FAILED |
| I | NO_COMPARABLE_PATH | NOT RUN: rolling window | Not measured | Not interpreted | 0 / 0 | 0 / 0 / 0 | No attempt |

Dated measurement: 2026-10-03, America/Chicago. Known-domain regression, engine `4db619d` (#329). This is a partial map, not acceptance. [Original nine-family map](nine-family-live-map.md) is historical evidence, with later H full-allowance NO_PROGRESS recorded separately. Existing tickets were read unchanged from the retained A–I ticket files; no reported figure was authored.

The initial rolling allowance was 41/60, leaving 19 physical requests. Order: D, H, E, A, G, F, I, B, C. All attempted runs retained the four-diagnostic-read cap, same quality profile and configured three-boundary ceiling. No credits, allowance/cap changes, fixture edits, engine/adapter changes or replacement attempts. Every intake used one model call, separate from the table’s investigation planner count.

Of nine families: zero received a reproduction verdict; two (D/H) retained no-figure findings with computed values; two (E/G) aborted without retaining reproduction markers; one (A) never entered reproduction because intake chose the horizontal route; four were not attempted. None newly received a validated answer to its original question. This is not a count of five undeclared capabilities: non-entry, an aborted evidence chain, no figure, and an adapter refusal are different states. No retained completed inventory contains UNSUPPORTED.

Outcome comparison must keep route and completion separate. D is the one directly comparable completed vertical classification change. E/G have no completed current vertical classification, rather than a replacement explanation for their previous transformation findings. H changed from the historical horizontal route to vertical through intake judgment. A remains UNRESOLVED with a different stopping reason. No outcome change is attributed to an unspecified vertical-path fix.


## Family D — `b71dd887-1c27-4965-8091-1bed680847ca`

The filtered lower-scope refusal is unchanged. Selection existence and two cell evaluations plus their baseline consume four reads before a vertical presentation baseline. The #329 zero-comparison producer now returns NO_KNOWN_PATTERN when that baseline is absent, rather than violating NO_COMPARABLE_PATH’s baseline contract. This is a budget-allocation consequence, not a newly answered discrepancy.

Intake: MISMATCH_COMPLAINT / VERTICAL; metric quote `Handled Quantity`. Report resolution STATED, quote `Inventory Health e1b8e1` at 3–26. These are ticket-span provenance, not runtime selection evidence. Figure UNSPECIFIED: no figure quote/precision inferred. Context `35461b1d-b5a4-48ef-a61d-aa539403a188`. Diagnostic reads 4/4, physical requests 4, guard requests 0, SQL 0, DAX 4, other 0; no batch credits. Synthesis FAILED.

Cell UNGROUPED: declared-context value 8765; undeclared-context value 8765; No reported figure supplied. Inventory discovered 1 = ACTIVE 1 + CONDITIONAL 0 + UNSUPPORTED 0. The engine validator passes on original saved observations; conservation is not merely asserted. Evidence `declared-reproduction-b2d055eb7ea3ee4125d4b3d59cb6dce26e722852a63f5a5063484faafeefdd2d`.
Declaration `f263f4e936e9ca1c8fc3c5b0185b607f5402888c2bb67cd3010138153d155dfd`: ACTIVE, FULL_DOMAIN, volatility VIEWER_CHANGEABLE, assumption SAVED_DEFAULT; restrictions []. It is a saved full-domain slicer, not a predicate selecting North. The keyed D cell independently adds North through its cell address; no restriction was invented.
Cell KEYED: declared-context value 3359; undeclared-context value 8765; No reported figure supplied. Inventory discovered 1 = ACTIVE 1 + CONDITIONAL 0 + UNSUPPORTED 0. The engine validator passes on original saved observations; conservation is not merely asserted. Evidence `declared-reproduction-d8964b006f1897843e4ab8efa01a1c351f1ed77cc6ac20c25467b12f6edbec3a`.
Declaration `f263f4e936e9ca1c8fc3c5b0185b607f5402888c2bb67cd3010138153d155dfd`: ACTIVE, FULL_DOMAIN, volatility VIEWER_CHANGEABLE, assumption SAVED_DEFAULT; restrictions []. It is a saved full-domain slicer, not a predicate selecting North. The keyed D cell independently adds North through its cell address; no restriction was invented.

Every physical probe, in receipt order:

| Receipt | Tool | Address / purpose | Value | Self-report | Attestation |
| --- | --- | --- | --- | --- | --- |
| `0d8e4925-3f9f-4aed-acb3-1e2176258c28` | bounded_dax | BASELINE  | [{"[quantity]": {"type": "decimal", "value": "1"}}] | engine=OLAP Server; identity=investigator-reader@skynwhy.com; object=3484a2bc-98c5-4cef-be5c-a6215484075e | PARTIAL; MATCHED; unattested connection |
| `3c9933ed-e07f-4055-95b8-3d293e0578c0` | bounded_dax | CELL UNGROUPED | [{"[quantity]": {"type": "decimal", "value": "8765"}}] | engine=OLAP Server; identity=investigator-reader@skynwhy.com; object=3484a2bc-98c5-4cef-be5c-a6215484075e | PARTIAL; MATCHED; unattested connection |
| `e16020e5-74ce-4a5d-bb05-e564613f9ddd` | bounded_dax | BASELINE  | [{"[quantity]": {"type": "decimal", "value": "8765"}}] | engine=OLAP Server; identity=investigator-reader@skynwhy.com; object=3484a2bc-98c5-4cef-be5c-a6215484075e | PARTIAL; MATCHED; unattested connection |
| `977d4754-8f7b-4eb2-893d-44ac96e14e7c` | bounded_dax | CELL KEYED | [{"[quantity]": {"type": "decimal", "value": "3359"}}] | engine=OLAP Server; identity=investigator-reader@skynwhy.com; object=3484a2bc-98c5-4cef-be5c-a6215484075e | PARTIAL; MATCHED; unattested connection |

All completed reproduction pairs above are WITHIN_LAYER_CHECK, never a verified boundary. Where a surface self-report is missing, no attestation grade is inferred. Snapshot currency is not established.
Skipped `boundary-1-not-comparable`: Declared source comparison does not yet translate filtered scope faithfully.
Skipped `boundary-2-not-comparable`: Declared quantity trace supports only whole-entity scope without filters or grouping.
Skipped `boundary-3-not-comparable`: Declared quantity trace supports only whole-entity scope without filters or grouping.

The provider refused the wire schema: `Invalid schema for function 'evidence_narrative': In context=('properties', 'business_output', 'properties', 'text'), " is not allowed in string literals for structured outputs (strict=true).` Code: invalid_function_parameters. No response pair exists.

Both final outputs, verbatim:

No validated output pair was produced. Question/answer alignment, identifier exclusion and once-only hedge checks cannot pass on absent outputs. The raw rejected provider proposal is not substituted for the final output.

## Family H — `115898f8-fc74-4bba-b7ba-07664b8d7cf9`

Intake selected BUSINESS_QUESTION / NONE and Inbound Quantity only. The vertical route ran instead of the historical horizontal planner/relative-cost guard; the old guard was absent. No rejected investigation planner steps: zero planner calls. This route variation means its stop reason is not evidence that the previous horizontal NO_PROGRESS was fixed. The requested inbound/outbound interpretation has no validated answer.

The declared partition binding is RESOLVED, but the selected definition is `CALCULATE([Handled Quantity],'Activity'[movement_type]="RECEIPT")`. The adapter's `resolve_path()` adds an executable declared-source quantity only inside its simple `SUM(column)` branch (microsoft_process.py:411–424); this definition does not enter it. The resulting single-layer path reaches the `unverified_business_flow()` branch (process_debugging.py:428–440), yielding NO_KNOWN_PATTERN. Its retained metadata nevertheless still carries UNRESOLVED_PARTITION_IDENTITY: a stale/generic gap description despite the successful binding is another finding, not proof that the source identity was unresolved. No lower-layer comparison, job-history evaluation or definition judge occurred.

Intake: BUSINESS_QUESTION / NONE; metric quote `Inbound Quantity`. Report resolution STATED, quote `Warehouse Performance e1b8e1` at 0–28. These are ticket-span provenance, not runtime selection evidence. Figure UNSPECIFIED: no figure quote/precision inferred. Context `35461b1d-b5a4-48ef-a61d-aa539403a188`. Diagnostic reads 4/4, physical requests 4, guard requests 0, SQL 0, DAX 4, other 0; no batch credits. Synthesis FAILED.

Cell UNGROUPED: declared-context value 6425; undeclared-context value 6425; No reported figure supplied. Inventory discovered 1 = ACTIVE 1 + CONDITIONAL 0 + UNSUPPORTED 0. The engine validator passes on original saved observations; conservation is not merely asserted. Evidence `declared-reproduction-dcd6f666a136689e8c90975572fe2752db68392b00e94aebeb2406fcb75cc233`.
Declaration `af413e5d592dc37796bc98b9b61677f8efb7eefe573ff4fc42c54506328e9174`: ACTIVE, FULL_DOMAIN, volatility VIEWER_CHANGEABLE, assumption SAVED_DEFAULT; restrictions []. It is a saved full-domain slicer, not a predicate selecting North. The keyed D cell independently adds North through its cell address; no restriction was invented.
Cell TOTAL: declared-context value 6425; undeclared-context value 6425; No reported figure supplied. Inventory discovered 1 = ACTIVE 1 + CONDITIONAL 0 + UNSUPPORTED 0. The engine validator passes on original saved observations; conservation is not merely asserted. Evidence `declared-reproduction-73cdd676348201c86467c74dbad36f65dfc5b34ca1703ce2ef6c3c155fb114a7`.
Declaration `af413e5d592dc37796bc98b9b61677f8efb7eefe573ff4fc42c54506328e9174`: ACTIVE, FULL_DOMAIN, volatility VIEWER_CHANGEABLE, assumption SAVED_DEFAULT; restrictions []. It is a saved full-domain slicer, not a predicate selecting North. The keyed D cell independently adds North through its cell address; no restriction was invented.

Every physical probe, in receipt order:

| Receipt | Tool | Address / purpose | Value | Self-report | Attestation |
| --- | --- | --- | --- | --- | --- |
| `0ad0e211-fcd4-44f5-9ddc-46837a333936` | bounded_dax | CELL UNGROUPED | [{"[quantity]": {"type": "decimal", "value": "6425"}}] | engine=OLAP Server; identity=investigator-reader@skynwhy.com; object=3484a2bc-98c5-4cef-be5c-a6215484075e | PARTIAL; MATCHED; unattested connection |
| `00aaaf06-761e-4960-abd5-9ca8aa450bae` | bounded_dax | BASELINE  | [{"[quantity]": {"type": "decimal", "value": "6425"}}] | engine=OLAP Server; identity=investigator-reader@skynwhy.com; object=3484a2bc-98c5-4cef-be5c-a6215484075e | PARTIAL; MATCHED; unattested connection |
| `302ef605-88b7-4e30-91ce-f4143d767d93` | bounded_dax | CELL TOTAL | [{"[quantity]": {"type": "decimal", "value": "6425"}}] | engine=OLAP Server; identity=investigator-reader@skynwhy.com; object=3484a2bc-98c5-4cef-be5c-a6215484075e | PARTIAL; MATCHED; unattested connection |
| `779f6e76-582e-4740-99e3-92e69584e940` | bounded_dax | BASELINE  | [{"[baseline]": {"type": "decimal", "value": "6425"}}] | engine=OLAP Server; identity=investigator-reader@skynwhy.com; object=3484a2bc-98c5-4cef-be5c-a6215484075e | PARTIAL; MATCHED; unattested connection |

All completed reproduction pairs above are WITHIN_LAYER_CHECK, never a verified boundary. Where a surface self-report is missing, no attestation grade is inferred. Snapshot currency is not established.

The recorded response cites `00aaaf06-761e-4960-abd5-9ddc-46837a333936` in technical_output.evidence_ids; the actual receipt is `00aaaf06-761e-4960-abd5-9ca8aa450bae`. Offline validation against the recorded wire schema reproduces ValidationError. No validated output pair exists.

Both final outputs, verbatim:

No validated output pair was produced. Question/answer alignment, identifier exclusion and once-only hedge checks cannot pass on absent outputs. The raw rejected provider proposal is not substituted for the final output.

## Family E — `e90751ab-33b3-463f-b345-a7774b6f80ea`

Reproduction precedes the vertical walk and spends the four diagnostic slots on report cells and baseline. A subsequent requested baseline hits UsageHold. The broad process exception handler labels that admission refusal PROCESS_FAILED; it also loses the in-memory walk observations, while sealed physical receipts survive. This is a newly exposed defect, not evidence of a failed estate job. No TRANSFORMATION_LOGIC conclusion or freshness answer was reached.

Intake: BUSINESS_QUESTION / NONE; metric quote `Handled Quantity`. Report resolution STATED, quote `Inventory Health e1b8e1` at 0–23. These are ticket-span provenance, not runtime selection evidence. Figure UNSPECIFIED: no figure quote/precision inferred. Context `35461b1d-b5a4-48ef-a61d-aa539403a188`. Diagnostic reads 4/4, physical requests 4, guard requests 0, SQL 0, DAX 4, other 0; no batch credits. Synthesis COMPLETED.

No original completed reproduction marker/inventory validation persisted. The process aborted before returning its in-memory observations. Sealed query results below are preserved evidence, not backfilled walk findings.

Every physical probe, in receipt order:

| Receipt | Tool | Address / purpose | Value | Self-report | Attestation |
| --- | --- | --- | --- | --- | --- |
| `62dbd1b1-d85f-43b3-8067-bc8ae24b1009` | bounded_dax | CELL UNGROUPED | [{"[quantity]": {"type": "decimal", "value": "8765"}}] | engine=OLAP Server; identity=investigator-reader@skynwhy.com; object=3484a2bc-98c5-4cef-be5c-a6215484075e | not retained; sealed result self-report only |
| `596db4b1-f106-40ce-a238-52d678f35b5d` | bounded_dax | BASELINE  | [{"[quantity]": {"type": "decimal", "value": "8765"}}] | engine=OLAP Server; identity=investigator-reader@skynwhy.com; object=3484a2bc-98c5-4cef-be5c-a6215484075e | not retained; sealed result self-report only |
| `1efd563a-2fa1-4663-9d89-bb901224f760` | bounded_dax | CELL TOTAL | [{"[quantity]": {"type": "decimal", "value": "8765"}}] | engine=OLAP Server; identity=investigator-reader@skynwhy.com; object=3484a2bc-98c5-4cef-be5c-a6215484075e | not retained; sealed result self-report only |
| `bcfc6b76-3080-45f8-8d30-65ac65501020` | bounded_dax | BASELINE  | [{"[baseline]": {"type": "decimal", "value": "8765"}}] | engine=OLAP Server; identity=investigator-reader@skynwhy.com; object=3484a2bc-98c5-4cef-be5c-a6215484075e | not retained; sealed result self-report only |

All completed reproduction pairs above are WITHIN_LAYER_CHECK, never a verified boundary. Where a surface self-report is missing, no attestation grade is inferred. Snapshot currency is not established.

Retained failure: {"error_type": "UsageHold", "line": 485, "message": "Investigation diagnostic-read limit", "message_redacted": false, "module": "adaptive_runtime.py"}

Both final outputs, verbatim:

**Business**

```text
You asked: Inventory Health e1b8e1 Handled Quantity may be stale. Inspect the available refresh and processing history and explain whether freshness can be established. I have not supplied a freshness SLA.
Answer to your question: Not answered.

The investigation stopped during process failure.
Reason: Investigation diagnostic-read limit
No explanation of the reported difference was established.
Recommended action: Resolve the stated blocker before a new investigation.
Process failure: Investigation diagnostic-read limit
```

**Technical**

```text
You asked: Inventory Health e1b8e1 Handled Quantity may be stale. Inspect the available refresh and processing history and explain whether freshness can be established. I have not supplied a freshness SLA.
Answer to your question: Not answered.

The investigation stopped during process failure.
Reason: Investigation diagnostic-read limit
No explanation of the reported difference was established.
Recommended action: Resolve the stated blocker before a new investigation.
Process failure: Investigation diagnostic-read limit (UsageHold at adaptive_runtime.py:485).
```

Output checks: question subject and Not answered are rendered. Failure message is explicit, not an unavailability. The fixture tag `e1b8e1` leaks through the verbatim ticket header; no asset URI/query/receipt ID is in the business body. The blocker is repeated in Reason and Process failure: the once-only requirement is not satisfied. These are recorded defects, not edited away.

## Family A — `c4fc651a-cd62-4c55-ad5f-36450bb6b478`

Four rejected proposals are preserved: `90ceb737-c29f-4fd0-bebe-9029add0bc5e`, “Contribution query must read the declared upstream object”; `9418c974-20d1-486e-9f75-62a2a5ec9c0d`, `4e3360e7-75a4-4b2c-bff8-ed578eb24a9a` and `476a4280-b0d2-488f-a0de-6668e229cb24`, each “Unknown or ambiguous DAX member”. Synthesis is BLOCKED / SYNTHESIS_ASSESSMENT_UNAVAILABLE, with no provider call. Typed native observations carry transport identity provenance for the isolated reader/model/workspace, not quantity-bound self-report; no surface attestation grade is inferred. Their physical receipts have null query IDs; the table names the corresponding saved observations in request order, not backfilled receipt IDs.

Intake selected MISMATCH_COMPLAINT / HORIZONTAL, as in its old run. Declared-context reproduction belongs to the vertical procedure and was not entered. This run’s NO_PROGRESS is an observed planner/test-selection outcome, not attributable to a vertical-path fix.

Intake: MISMATCH_COMPLAINT / HORIZONTAL; metric quote `Handled Quantity`. Report resolution STATED, quote `Inventory Health e1b8e1` at 3–26. These are ticket-span provenance, not runtime selection evidence. Figure UNSPECIFIED: no figure quote/precision inferred. Context `35461b1d-b5a4-48ef-a61d-aa539403a188`. Diagnostic reads 3/4, physical requests 3, guard requests 0, SQL 0, DAX 3, other 0; no batch credits. Synthesis BLOCKED.

No original completed reproduction marker/inventory validation persisted. The horizontal route did not invoke extraction; this is not an unsupported-declaration result.

Every physical probe, in receipt order:

| Receipt | Tool | Address / purpose | Value | Self-report | Attestation |
| --- | --- | --- | --- | --- | --- |
| `101b7a16-f5b2-4369-8dc0-64df31092008` | bounded_dax | not retained  | [{"[Activity Entries]": {"type": "decimal", "value": "406"}, "[Handled Quantity]": {"type": "decimal", "value": "8765"}, "[Inbound Quantity]": {"type": "decimal", "value": "6425"}, "[Outbound Quantity]": {"type": "decimal", "value": "2340"}, "[Quantity Balance]": {"type": "decimal", "value": "4085"}}] | not retained | not retained; sealed result self-report only |
| `754646e1-3c83-4f82-b2dd-17b5c04a19eb` | bounded_dax | not retained  | [{"Activity[movement_type]": {"type": "string", "value": "RECEIPT"}, "[Activity Entries]": {"type": "decimal", "value": "298"}, "[Handled Quantity]": {"type": "decimal", "value": "6425"}, "[Units Max]": {"type": "decimal", "value": "40"}, "[Units Min]": {"type": "decimal", "value": "2"}, "[Units Sum]": {"type": "decimal", "value": "6425"}}, {"Activity[movement_type]": {"type": "string", "value": "ISSUE"}, "[Activity Entries]": {"type": "decimal", "value": "108"}, "[Handled Quantity]": {"type": "decimal", "value": "2340"}, "[Units Max]": {"type": "decimal", "value": "40"}, "[Units Min]": {"type": "decimal", "value": "2"}, "[Units Sum]": {"type": "decimal", "value": "2340"}}] | not retained | not retained; sealed result self-report only |
| `4c57c170-0892-45f7-b907-62ac8a44dacf` | bounded_dax | not retained  | [{"Activity[movement_type]": {"type": "string", "value": "RECEIPT"}, "[Activity Rows]": {"type": "decimal", "value": "298"}, "[Distinct Movement IDs]": {"type": "decimal", "value": "270"}, "[Handled Quantity]": {"type": "decimal", "value": "6425"}, "[Units Sum]": {"type": "decimal", "value": "6425"}}, {"Activity[movement_type]": {"type": "string", "value": "ISSUE"}, "[Activity Rows]": {"type": "decimal", "value": "108"}, "[Distinct Movement IDs]": {"type": "decimal", "value": "90"}, "[Handled Quantity]": {"type": "decimal", "value": "2340"}, "[Units Sum]": {"type": "decimal", "value": "2340"}}] | not retained | not retained; sealed result self-report only |

All completed reproduction pairs above are WITHIN_LAYER_CHECK, never a verified boundary. Where a surface self-report is missing, no attestation grade is inferred. Snapshot currency is not established.

Both final outputs, verbatim:

No validated output pair was produced. Question/answer alignment, identifier exclusion and once-only hedge checks cannot pass on absent outputs. The raw rejected provider proposal is not substituted for the final output.

## Family G — `3f6de6ff-adbf-4e8c-996b-b58a2d709974`

Like E, the unchanged ticket entered BUSINESS_QUESTION / NONE, consumed four DAX diagnostic slots and then hit UsageHold at adaptive_runtime.py:485. The broad process exception handler discarded walk observations while physical receipts and sealed query results survived. No SQL/guard read, judge, successful boundary comparison or source/application answer occurred. This lost finding traces to reproduction's additional budget use plus exception persistence, not to a changed source mechanism.

See the recorded stop and receipts below. A change caused by admission/evidence failure is not a new source/application conclusion.

Intake: BUSINESS_QUESTION / NONE; metric quote `Handled Quantity`. Report resolution STATED, quote `Inventory Health e1b8e1` at 0–23. These are ticket-span provenance, not runtime selection evidence. Figure UNSPECIFIED: no figure quote/precision inferred. Context `35461b1d-b5a4-48ef-a61d-aa539403a188`. Diagnostic reads 4/4, physical requests 4, guard requests 0, SQL 0, DAX 4, other 0; no batch credits. Synthesis COMPLETED.

No original completed reproduction marker/inventory validation persisted. The process aborted before returning its in-memory observations. Sealed query results below are preserved evidence, not backfilled walk findings.

Every physical probe, in receipt order:

| Receipt | Tool | Address / purpose | Value | Self-report | Attestation |
| --- | --- | --- | --- | --- | --- |
| `57d0d590-ea82-4c0f-bc99-2b8362401310` | bounded_dax | CELL UNGROUPED | [{"[quantity]": {"type": "decimal", "value": "8765"}}] | engine=OLAP Server; identity=investigator-reader@skynwhy.com; object=3484a2bc-98c5-4cef-be5c-a6215484075e | not retained; sealed result self-report only |
| `b9627c2b-1d0b-4324-a821-9ed8b67b4f89` | bounded_dax | BASELINE  | [{"[quantity]": {"type": "decimal", "value": "8765"}}] | engine=OLAP Server; identity=investigator-reader@skynwhy.com; object=3484a2bc-98c5-4cef-be5c-a6215484075e | not retained; sealed result self-report only |
| `01e83c1b-4a8a-43cf-9e23-e7cf216cb5c6` | bounded_dax | CELL TOTAL | [{"[quantity]": {"type": "decimal", "value": "8765"}}] | engine=OLAP Server; identity=investigator-reader@skynwhy.com; object=3484a2bc-98c5-4cef-be5c-a6215484075e | not retained; sealed result self-report only |
| `daca4540-cc73-48b3-9d84-dfd0110fb7d4` | bounded_dax | BASELINE  | [{"[baseline]": {"type": "decimal", "value": "8765"}}] | engine=OLAP Server; identity=investigator-reader@skynwhy.com; object=3484a2bc-98c5-4cef-be5c-a6215484075e | not retained; sealed result self-report only |

All completed reproduction pairs above are WITHIN_LAYER_CHECK, never a verified boundary. Where a surface self-report is missing, no attestation grade is inferred. Snapshot currency is not established.

Retained failure: {"error_type": "UsageHold", "line": 485, "message": "Investigation diagnostic-read limit", "message_redacted": false, "module": "adaptive_runtime.py"}

Both final outputs, verbatim:

**Business**

```text
You asked: Inventory Health e1b8e1 Handled Quantity may include incorrect source entries. Inspect source stock movements and related inventory adjustments for evidence. Do not assume an adjustment record alone proves the intended business rule.
Answer to your question: Not answered.

The investigation stopped during process failure.
Reason: Investigation diagnostic-read limit
No explanation of the reported difference was established.
Recommended action: Resolve the stated blocker before a new investigation.
Process failure: Investigation diagnostic-read limit
```

**Technical**

```text
You asked: Inventory Health e1b8e1 Handled Quantity may include incorrect source entries. Inspect source stock movements and related inventory adjustments for evidence. Do not assume an adjustment record alone proves the intended business rule.
Answer to your question: Not answered.

The investigation stopped during process failure.
Reason: Investigation diagnostic-read limit
No explanation of the reported difference was established.
Recommended action: Resolve the stated blocker before a new investigation.
Process failure: Investigation diagnostic-read limit (UsageHold at adaptive_runtime.py:485).
```

Output checks: question subject and Not answered are rendered. Failure message is explicit, not an unavailability. The fixture tag `e1b8e1` leaks through the verbatim ticket header; no asset URI/query/receipt ID is in the business body. The blocker is repeated in Reason and Process failure: the once-only requirement is not satisfied. These are recorded defects, not edited away.

## Stop and remaining work

Five of nine families ran: D, H, E, A, G. F, I, B, C did not enter intake and have distinct NOT_RUN ledger rows; their reproduction/vertical capabilities are unmeasured. The batch consumed 19 physical requests, all diagnostic DAX reads, zero guards/SQL/metadata. Ordinary use 41 to 60 of 60; diagnostic cap four unchanged. Nine investigation planner calls (A), zero judges, two attempted synthesis model calls (D/H), five intake calls; E/G used deterministic refusal rendering. No replacement/refill. The first slot releases 2026-10-03 22:48:17 UTC (17:48:17 CDT); four slots are available cumulatively at 2026-10-04 00:11:38 UTC (2026-10-03 19:11:38 CDT), absent intervening use. This is a rolling window, not a midnight reset. The engine/config/policy/profile and all nine ticket hashes match the initial manifest.

No B ratio decomposition, C bound change, filtered lower-scope translation or provider/adapter repair was attempted. Unrun families are unmeasured, not predicted failures. Existing failures, historical outputs and receipts remain unchanged. Prior freezes remain invalid; this evidence-only change creates no new freeze or unfamiliar-domain claim.
