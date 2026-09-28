# Nine-family known-domain live map

2026-09-28 UTC. One attempt per family, on merged #286 (`8d5e000`). Six CI checks passed before merge. No engine changes, replacement runs, refills, permission changes or unfamiliar-domain claim.

All nine families were attempted between 03:50:24 and 04:10:13 UTC. Six reached validated synthesis; that is an execution result, not six fully answered tickets. A exhausted its diagnostic cap and synthesis blocked; C raised a resolver exception before reading; H stopped at the separately approved relative-cost guard.

## Actual cost and outcome

Model calls include intake, investigation (including definition judgment), and synthesis. Physical requests include guards and metadata. A runtime `COMPLETED` state does not imply a supported conclusion.

| Family | Intake route | Diagnostics / 4 | Physical / 16 | Guards | Model calls (intake + investigation + synthesis) | Recorded result |
| --- | --- | ---: | ---: | ---: | --- | --- |
| A | MISMATCH_COMPLAINT / HORIZONTAL | 4 | 4 | 0 | 8 (1 + 7 + 0) | UNRESOLVED; BUDGET_LIMIT; synthesis BLOCKED (KeyError) |
| B | MISMATCH_COMPLAINT / VERTICAL | 1 | 1 | 0 | 2 (1 + 0 + 1) | NO_COMPARABLE_PATH; synthesis validated |
| C | MISMATCH_COMPLAINT / VERTICAL | 0 | 0 | 0 | 1 (1 + 0 + 0) | Resolver ValueError before reading; session remained READY |
| D | MISMATCH_COMPLAINT / VERTICAL | 1 | 1 | 0 | 2 (1 + 0 + 1) | NO_COMPARABLE_PATH; synthesis validated |
| E | BUSINESS_QUESTION / NONE | 4 | 10 | 6 | 3 (1 + 1 + 1) | TRANSFORMATION_LOGIC; synthesis validated |
| F | MISMATCH_COMPLAINT / VERTICAL | 3 | 7 | 3 | 2 (1 + 0 + 1) | CONSISTENT_TO_BOUNDARY; synthesis validated |
| G | MISMATCH_COMPLAINT / VERTICAL | 4 | 10 | 6 | 3 (1 + 1 + 1) | TRANSFORMATION_LOGIC; synthesis validated |
| H | MISMATCH_COMPLAINT / HORIZONTAL | 1 | 1 | 0 | 3 (1 + 2 + 0) | HELD by H_COST_GUARD; runtime USAGE_LIMIT |
| I | BUSINESS_QUESTION / NONE | 2 | 2 | 0 | 2 (1 + 0 + 1) | NO_COMPARABLE_PATH; synthesis validated |
| **Total** | | **20 / 36** | **36 / 144** | **15** | **26 (9 + 11 + 6)** | **Six validated syntheses, not nine ticket passes** |

The eleven investigation calls were nine dynamic-planner calls (A seven, H two) and two definition-judge calls (E/G one each). All 26 calls have captured wire requests. The ledger's automatic `recording_phases.investigation` fallback includes standalone intake recordings with no phase field; the audited phase counts above and in the structured map distinguish them by recording session identity. No ledger history was rewritten.

Physical request breakdown: 12 DAX requests, five SQL quantity requests, 15 SQL identity/permission guards, two Fabric endpoint metadata requests, and two OneLake GETs. The latter two GETs form one ingestion diagnostic. Guard reuse was zero. All 36 initiated estate requests completed; no blocked admission was counted as a sent request.

## Family coverage and limits

- **A discrepancy:** intake selected HORIZONTAL rather than the estimated vertical route. Four DAX reads reproduced and decomposed native quantities, but no source read or cross-surface comparison occurred. The run stopped BUDGET_LIMIT at four diagnostics after seven planner calls. Synthesis preparation recorded BLOCKED / KeyError before making a synthesis provider call. The saved error does not identify the missing key; this report does not invent it. No valid business/technical output was produced.
- **B ratio:** one DAX baseline returned 0.733029092983457. The vertical path did not decompose numerator/denominator and returned NO_COMPARABLE_PATH, with validated synthesis. The predicted limitation was reproduced by a real attempt. The recorded explanation describes a missing resolved lower binding; it does not prove the physical table is absent from discovery. The requested component explanation remains unanswered.
- **C derived:** intake selected Quantity Balance / VERTICAL. `resolve_path` raised `ValueError: Measure path exceeds bounded projection` at the existing 12,000-character bound. One intake call, zero reads or investigation calls, no synthesis. A session and its 16-credit grant existed; its persisted state stayed READY. This is a failed attempt, not a queued retry or a graceful supported limitation.
- **D visual/filter:** the North selection was read once through DAX. Lower-layer filter translation was NOT_COMPARABLE; no approximation, SQL read or cross-surface comparison occurred. NO_COMPARABLE_PATH synthesized successfully. The prediction was reproduced. The run did not read a separate global comparator or reconstruct all interactive report context.
- **E freshness:** BUSINESS_QUESTION / NONE entered the process walk. Power BI and Gold both returned 8,765; Gold versus Silver was 8,765 versus 7,661. One definition judge supported TRANSFORMATION_LOGIC and synthesis validated. Refresh timestamps were unavailable and skipped; the record carries no authoritative freshness SLA. The join mechanism is useful incidental evidence, but the freshness-specific request was not established by this outcome.
- **F transformation:** presentation and declared Gold source both returned 57,043. OneLake ingestion used two physical GETs; no deeper faithful quantity path or definition judgment was reached. CONSISTENT_TO_BOUNDARY synthesized successfully. This does not establish the total is correct, current, or free of an upstream transformation issue.
- **G source/application:** the same two attested cross-surface comparisons as E reached the Silver-to-Gold divergence and a definition judgment. TRANSFORMATION_LOGIC synthesized successfully. No Bronze/application or inventory-adjustment data was investigated; possible duplicate matches and intended rules remain unproved. The source/application question therefore remains partial.
- **H expected behavior:** HORIZONTAL selected Inbound Quantity. Its first DAX query read Inbound, Outbound, Handled Quantity and Quantity Balance together. The second planner proposed a movement-type breakdown. Admission of that second DAX read was stopped by the H guard; no synthesis followed. This is a bounded partial attempt, not an expected-behavior pass.
- **I unknown semantics:** intake selected Handled Quantity grouped by the discovered adjustment `reason_code` dimension, rather than asking what Q49 means. Two DAX reads yielded a within-layer check, correctly refused as an independent lower comparison. Grouped lower paths were also NOT_COMPARABLE. NO_COMPARABLE_PATH synthesized successfully, but neither the meaning of Q49 nor its intended effect was established. The actual route/cost differed from the estimated four-read process path.

Across E/F/G there were five genuinely cross-surface comparisons: three presentation/Gold agreements and two Gold/Silver divergences. All five remain SNAPSHOT_UNVERIFIED. I records one WITHIN_LAYER_CHECK, never upgraded to a boundary comparison. B/D/I have zero cross-surface comparisons. A/H stayed within the native model; C executed no probe. No comparison establishes currency or excludes update timing as a cause.

## H relative-cost stop

The evaluator interpreted “any two” conservatively and independently for physical requests and model calls. Before H, B+C were the cheapest pair: 1+0 physical requests and 2+1 model calls. H was therefore allowed at most one physical request and three model calls, including intake. This interpretation was communicated before the batch.

At 04:08:52 UTC, H had one physical request and three model calls. Its proposed movement-type breakdown required physical request two. The evaluator refused reservation `tool:2` before calling the existing governor, recording `H_COST_GUARD_REFUSED` with used=1, next=1, limit=1. Runtime retained HELD / USAGE_LIMIT; the ledger additionally identifies H_COST_GUARD. No extra request, reservation, retry or synthesis occurred. I still ran once afterwards. This evaluator-only guard changed no engine, provider payload, policy or per-run diagnostic cap.

## Credits, expiry and unchanged controls

The user approved 16 credits per session, 144 total, with one common six-hour expiry. Nine grants were persisted before each session's first estate request; grant and before/after control-plane readbacks are retained locally. **36 charged, 108 unused, all expiring 2026-09-28 09:50:24.348615 UTC.** Unused credits are not transferable and do not authorize another attempt. They were still unexpired when this report was written; expiration is enforced at admission.

| Family | Session | Granted | Charged | Unused until expiry |
| --- | --- | ---: | ---: | ---: |
| A | `c7dcc655-f2f9-4ae2-9b6c-5bd2a045e8b0` | 16 | 4 | 12 |
| B | `9a0eb374-247f-4380-8453-b3b77c63a1e3` | 16 | 1 | 15 |
| C | `e8dcb0d9-0fcd-400b-8bb8-788597667c40` | 16 | 0 | 16 |
| D | `c2e2e7c9-0cdc-482c-abc3-c3cdab729dee` | 16 | 1 | 15 |
| E | `c274890f-e041-4261-b364-c4c3d6c2bcc8` | 16 | 10 | 6 |
| F | `6860ae26-d855-4bb2-ac03-8e10c1e01cf1` | 16 | 7 | 9 |
| G | `cd2ffbff-f75b-4999-a0fe-a5fee18ee5f9` | 16 | 10 | 6 |
| H | `e68af7b8-4a7c-47a8-8303-8116278a15be` | 16 | 1 | 15 |
| I | `0d049414-87b8-4a7a-a034-9649f6840f53` | 16 | 2 | 14 |

The diagnostic cap stayed four. Ordinary allowance stayed 60 and had zero available both before and after; its rolling charged count aged from 77 to 74 as old usage left the window. Every new read used its named batch allocation. No counters were reset, no credits refunded/refilled, and no global ceiling or deadline changed. Model reservations increased by 26 calls; existing model limits were unchanged.

Engine fingerprint before/after: `58df502e8f157a314ea05c533209fad1124516a8d6d25071fa5732e79a6adbbe`. Config, policy, model profile and all nine ticket hashes also match before/after; the [structured map](runs/nine-family-map.json) records them. No frozen-acceptance validity is asserted.

## Receipts and verbatim outputs

Local immutable run results, logs, grant/readback snapshots, H refusal and operator scripts are under `.local/nine-family-20260928/`. All 26 provider tapes remain under `.local/planner-recordings/`; tape identifiers are in the append-only [ledger](runs/ledger.jsonl) and structured map. Exactly nine ledger rows were appended. No existing run or ledger row was changed.

| Family with validated synthesis | Business output | Technical output |
| --- | --- | --- |
| B | [Verbatim](runs/nine-family-B-business.txt) | [Verbatim](runs/nine-family-B-technical.txt) |
| D | [Verbatim](runs/nine-family-D-business.txt) | [Verbatim](runs/nine-family-D-technical.txt) |
| E | [Verbatim](runs/nine-family-E-business.txt) | [Verbatim](runs/nine-family-E-technical.txt) |
| F | [Verbatim](runs/nine-family-F-business.txt) | [Verbatim](runs/nine-family-F-technical.txt) |
| G | [Verbatim](runs/nine-family-G-business.txt) | [Verbatim](runs/nine-family-G-technical.txt) |
| I | [Verbatim](runs/nine-family-I-business.txt) | [Verbatim](runs/nine-family-I-technical.txt) |

A/C/H have no validated pair to publish. No replacement output was generated. The new mechanism-only and discovered-container rendering validated on the six synthesis paths exercised, including E/G; that does not repair the investigation coverage gaps above.

Validation for this evidence-only PR: local map checks reconcile nine unique session rows, 26 captured requests, 36 charged credits/receipts, unchanged controls, and exact output-text copies. The prior #286 engine passed 1,316 local regressions and all six CI checks before merge; those are prior engine-validation results, not tests rerun for this report.
