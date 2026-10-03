# Autonomous round: final review report

2026-10-03. Parts A and B completed as a bounded engineering and known-domain measurement round. No formal freeze, fresh variant, unfamiliar-domain acceptance, permission change or business-correctness claim. Original evidence, tapes and failures remain unchanged.

## Ordered PRs, invariants and contracts

| PR | Part / purpose | Invariant and permanent test | Contract change |
|---|---|---|---|
| [330](https://github.com/bcsnpc/data-investigation-agent/pull/330) | A0: merge prior partial batch | Preserve five failures and four NOT_RUN rows; append-only evidence | None |
| [331](https://github.com/bcsnpc/data-investigation-agent/pull/331) | A1: authorised 300 physical / 12 diagnostic configuration | `test_autonomous_round_limits`: old charged window survives; next over-ceiling request refuses | Scoped new-round configuration; existing envelopes untouched |
| [332](https://github.com/bcsnpc/data-investigation-agent/pull/332) | A2–A4: subject gating, disjoint budgets, retained holds, implemented routes | `test_question_kind_budgets`: freshness zero reproduction, visual applicable, cap-four separation, unknown kind/unimplemented route refused, two prehold originals and pending names retained | Required wire question-kind quote; strict BUDGET_STOP accounting |
| [333](https://github.com/bcsnpc/data-investigation-agent/pull/333) | A5: provider preflight and citation namespace | `test_synthesis_wire_preflight`: unsupported schema/dangling original references fail before dispatch; unknown handle rejected | Technical-only provider response and enumerated citation handles; internal full evidence contract unchanged |
| [334](https://github.com/bcsnpc/data-investigation-agent/pull/334) | Own judgment in A: repair reviewed-evidence handoff | `test_question_intake`: full reviewed proposal, deep copy and future shared evidence declaration survive into preview/procedure | Shared procedure evidence declaration; no evidence passed alongside it |
| [335](https://github.com/bcsnpc/data-investigation-agent/pull/335) | A7: all nine unchanged tickets | Original receipts, engine inventory revalidation, one row per run and append-only C correction; six CI checks | None |
| [336](https://github.com/bcsnpc/data-investigation-agent/pull/336) | B: complete mechanism evidence into synthesis | `test_synthesis_spine`: whole future fields/provenance survive, deep copy, named whole elision, unchanged coverage; wire test checks consumer vocabulary reaches instructions | Provider view adds opaque `mechanism_evidence`; validation still uses originals |
| [337](https://github.com/bcsnpc/data-investigation-agent/pull/337) | B measurement and complete round report | Original output extraction, artifact hashes and append-only ledger-prefix audit | None |

Implementation and A7 PRs merged only after all six checks passed. Latest stable local suite reports 1,665 tests OK; 17 focused synthesis tests passed. The full-suite PowerShell redirection reported shell status 1 because existing ResourceWarnings went through its error stream; the unittest summary and raw log are preserved, and CI independently passed. No dedicated live browser session was rerun.

## A7: all nine unchanged tickets

| Family | Procedure outcome / stop | Diagnostic / physical / guards | Synthesis / both outputs |
|---|---|---|---|
| A | TRANSFORMATION_LOGIC | 4 / 10 / 6 | FAILED / NOT_GENERATED |
| B | NO_KNOWN_PATTERN | 1 / 1 / 0 | COMPLETED / GENERATED |
| C | PATH_CONTEXT_LIMIT | 0 / 0 / 0 | COMPLETED / GENERATED |
| D | NO_COMPARABLE_PATH | 6 / 6 / 0 | COMPLETED / GENERATED |
| E | TRANSFORMATION_LOGIC | 4 / 10 / 6 | COMPLETED / GENERATED |
| F | CONSISTENT_TO_BOUNDARY | 3 / 7 / 3 | COMPLETED / GENERATED |
| G | TRANSFORMATION_LOGIC | 4 / 10 / 6 | FAILED / NOT_GENERATED |
| H | NO_KNOWN_PATTERN | 1 / 1 / 0 | COMPLETED / GENERATED |
| I | TRANSFORMATION_LOGIC | 4 / 10 / 6 | FAILED / NOT_GENERATED |

E and G recovered TRANSFORMATION_LOGIC with zero reproduction reads. E delivered both outputs; G still failed synthesis, as did A and I. Their completed responses copied a digit-bearing object name, violating the unchanged mechanism-only contract. C refused PATH_CONTEXT_LIMIT before any read and delivered refusal outputs. D retained three no-reported-figure cells with engine-validated declaration conservation; filtered-lower comparison remains refused. B did not explain components. H established no verified business handoff. Six pairs are generated, not six fully answered tickets.

The [full A7 record](autonomous-round-nine-families.md) quotes every produced output and reports original quantity surfaces/self-reports/attestations, physical receipts, boundaries, snapshot status, skipped checks, limits and inventory/restrictions. Both preliminary runs and their outputs are in [the handoff finding](reviewed-evidence-handoff.md).

### Dated display correction to A7 report, 2026-10-03

The earlier per-family prose requested `mode` rather than the actual `comparison_mode` field, so it displayed None. The original report is preserved. The actual recorded intake pairs are:

| Family | Shape | Comparison mode |
|---|---|---|
| A | MISMATCH_COMPLAINT | VERTICAL |
| B | BUSINESS_QUESTION | NONE |
| C | BUSINESS_QUESTION | NONE |
| D | MISMATCH_COMPLAINT | VERTICAL |
| E | BUSINESS_QUESTION | NONE |
| F | MISMATCH_COMPLAINT | VERTICAL |
| G | BUSINESS_QUESTION | NONE |
| H | BUSINESS_QUESTION | NONE |
| I | BUSINESS_QUESTION | NONE |

D inventory: each of its three original cells discovers one declaration, classified ACTIVE 1 / CONDITIONAL 0 / UNSUPPORTED 0. Engine validation confirms conservation and ACTIVE coverage against each original definition observation. No reproduction verdict exists because the reported figure is UNSPECIFIED. Other families have no completed reproduction inventory; none is manufactured for reporting.

## Part B: committed design and before/after

The [ranked design](autonomous-round-part-b-design.md) was committed as f3523ba before implementation. After A7, I ranked evidence continuity above ratio decomposition: the common delivery seam was withholding the very mechanism it asked the model to explain. This is a display-copy contract addition, not a new calculation engine or inferred binding. The complete definition-evidence entry now survives, with its retained operations, original judgment, provenance and limits. Oversized units are explicitly elided whole; originals govern validation. Consumer-owned forbidden prose terms reach instructions, and local refusal remains unchanged.

On four retained cases, wire payloads grew from 3.6–3.8k to 7.4–7.6k characters; eight evidence entries and two boundaries each remained. Directory and SQL-object directory counts are zero at this seam before/after. No elision; permanent tests guard coverage and future definition fields.

Before: A/G A7 produced transformation evidence but no narrative pair. After: two unchanged-ticket attempts on merged #336 both validate synthesis and explain the retained left join and possible row multiplication. A is PARTLY_ANSWERED; G remains NOT_ANSWERED about source correctness/intended rules. There is no newly reachable taxonomy outcome or new ratio/filtered-lower capability. What improved is delivery of supported mechanism evidence; two successful samples do not establish general reliability.

The [repeat record](mechanism-evidence-repeats.md) contains both output pairs verbatim, every original quantity surface/attestation, compared and unchecked boundaries, skipped checks and all limits. All boundary snapshots remain SNAPSHOT_UNVERIFIED.

## Every run in this round

| Stage / family | Session | DAX / SQL / metadata physical | Diagnostic / physical / guards | Intake / exploration / judge / synthesis | Outcome | Both outputs |
|---|---|---|---|---|---|---|
| Preliminary A7 E | 44d222b3-0743-47ce-b903-f8865aa16e2f | 1 / 8 / 1 | 4 / 10 / 6 | 1 / 0 / 1 / 1 | TRANSFORMATION_LOGIC | GENERATED |
| Preliminary A7 G | 542e6507-b7dc-4de3-8209-5713b98c12ac | 1 / 8 / 1 | 4 / 10 / 6 | 1 / 0 / 1 / 1 | TRANSFORMATION_LOGIC | GENERATED |
| A7 A | beb6b607-cb98-47f8-b1e2-9e7b2dfe8ac7 | 1 / 8 / 1 | 4 / 10 / 6 | 1 / 0 / 1 / 1 | TRANSFORMATION_LOGIC | NOT_GENERATED |
| A7 B | 42febae9-4d3e-4ec3-97bb-306769d96233 | 1 / 0 / 0 | 1 / 1 / 0 | 1 / 0 / 0 / 1 | NO_KNOWN_PATTERN | GENERATED |
| A7 C | b5f4ff47-dd16-49f5-89af-df8d2c46ceaa | 0 / 0 / 0 | 0 / 0 / 0 | 1 / 0 / 0 / 0 | PATH_CONTEXT_LIMIT | GENERATED |
| A7 D | 96edf2e6-5ae0-467e-a420-69c4b717da17 | 6 / 0 / 0 | 6 / 6 / 0 | 1 / 0 / 0 / 1 | NO_COMPARABLE_PATH | GENERATED |
| A7 E | 057ff2ca-fa5d-42e4-87ca-6c4736068b13 | 1 / 8 / 1 | 4 / 10 / 6 | 1 / 0 / 1 / 1 | TRANSFORMATION_LOGIC | GENERATED |
| A7 F | e1fce96a-9e9c-458e-9101-983fc977281b | 1 / 4 / 2 | 3 / 7 / 3 | 1 / 0 / 0 / 1 | CONSISTENT_TO_BOUNDARY | GENERATED |
| A7 G | 02a4372d-3722-4a12-b70f-66f96a76557e | 1 / 8 / 1 | 4 / 10 / 6 | 1 / 0 / 1 / 1 | TRANSFORMATION_LOGIC | NOT_GENERATED |
| A7 H | 467e416f-8200-4b1d-a034-8a03aeba4cd1 | 1 / 0 / 0 | 1 / 1 / 0 | 1 / 0 / 0 / 1 | NO_KNOWN_PATTERN | GENERATED |
| A7 I | a1dbfe60-a2fe-43af-999c-12e1170d4ee2 | 1 / 8 / 1 | 4 / 10 / 6 | 1 / 0 / 1 / 1 | TRANSFORMATION_LOGIC | NOT_GENERATED |
| Part B G | 6640a85f-c54e-4aef-a2a5-96df6194d2d0 | 1 / 8 / 1 | 4 / 10 / 6 | 1 / 0 / 1 / 1 | TRANSFORMATION_LOGIC | GENERATED |
| Part B A | a9466911-69be-4252-96f2-0afb84b4f468 | 1 / 8 / 1 | 4 / 10 / 6 | 1 / 0 / 1 / 1 | TRANSFORMATION_LOGIC | GENERATED |

Totals: {'reads_dax': 17, 'reads_sql': 68, 'reads_other': 10, 'diagnostic_reads': 43, 'physical_requests': 95, 'guard_requests': 51, 'intake_calls': 13, 'investigation_planner_calls': 0, 'judge_calls': 8, 'synthesis_calls': 12}. Thirteen run rows, ten generated output pairs. Ledger corrections do not count as replacement runs. Old preliminary judge counts and C null diagnostic accounting are annotated, never edited. Physical metadata may exceed diagnostic metadata operations: F ingestion issued two GET requests for one diagnostic operation.

## Own judgment, disagreements and open findings

- Paused measurement after two preliminary runs to repair the lost question-kind handoff structurally (#334). Both runs remain recorded; I did not use them as proof that subject wiring worked. The corrected full batch is separately named.
- Corrected the A5 H premise: its supplied spine references resolved; the model response invented a receipt ID. Enumerated handles prevent that response state, while pre-call original-reference validation independently guards hostile/missing spine references. No false producer finding was reported.
- Picked mechanism evidence continuity after inspecting A7 provider views, rather than adding component reads while delivery lacked evidence. No rule was relaxed to obtain completion.
- Appended three ledger corrections for reporting defects: two preliminary judge-count annotations, and C diagnostic zero. No refunds, resets or original-row edits.
- The unrelated reproduction-unavailability sentence still appears in business prose for non-presentation tickets (for example G). Reads are correctly gated, but rendering makes an irrelevant capability sound relevant. Recorded as an open presentation finding, not silently repaired during the batch.
- Ratio/component decomposition remains unimplemented; C still hits a bounded context refusal; D still lacks faithful filtered lower quantities. These require their own capability arguments and tests.
- Intended source semantics, authoritative timing expectations, current served snapshots and a real application ingestion path remain unavailable/unestablished. No result here proves original source correctness, actual duplicated keys, currency or intended grain.
- The optional metadata identity does not attest the version served by a quantity query. The permission findings are unchanged; no elevation was attempted.
- Provider preflight currently covers synthesis. Intake/judge wire auditing remains a separate open item; their historical schema usage is not certified by this PR.
- The shrinking literal-debt ratchet remains binding; horizontal comparison, recurrence, business-context and known-issues work remain proposal-only.

## Final budgets

- Before A1: ordinary rolling use 60/60. A1 changed the scoped ceiling to 300 without resetting charged use; diagnostic cap twelve applies only to new runs.
- Preliminary E/G: 20 physical requests, 60 → 80/300. A7: 55, 80 → 135/300. Part B: 20, 135 → 155/300. Overall round: 95 physical requests, no new credits.
- Part B independent ceiling: 20/150 used; no extra attempts/refills. Ordinary window: 155/300 used, 145 available. Diagnostic cap remains twelve; maximum observed per run was six.
- Final model reservation window: 59/240 calls, 1,455,266/8,000,000 input characters and 303,000/1,500,000 output tokens reserved. These are reservations, not billed token usage. Counters and uncertain reservations were not reset.

The chosen Part B intervention and its bounded measurement are complete. Remaining capability work is ranked in the committed design; no budget was spent merely to exhaust the allowance.
