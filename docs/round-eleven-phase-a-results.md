# Round Eleven Phase A: complete evaluation, failed quality gate

Recorded 2026-10-09. All 68 unchanged tickets completed once on frozen `44490b4` using GPT-5.5 deployment `investigator-intake-f-55`. Development ran first, then the held-out partition; no source changes or tuning occurred during the pass. #423 remains draft. Prior freezes remain invalid.

This completes the prescribed text evaluation, not Round Eleven or the product. Scope adoption is distinct from starting an investigation. No estate reader ran, no quantities were evaluated, no synthesis or business/technical investigation outputs were produced. Screenshot Phase B and the rehearsal-nine/fifty live list remain gated. The two-report route is design only.

## Result

| Partition | Tickets | Adopted scopes | One-round settled | Full original-record matches | Questions | Mean questions | Consequential-admission flags |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| dev | 40 | 12 | 16/40 (40.0%) | 12/40 | 39 | 0.975 | 4 |
| held_out | 28 | 14 | 15/28 (53.6%) | 9/28 | 32 | 1.143 | 1 |

Held-out settlement is 15/28 (53.6%), below 85% (at least 24/28 required). Its family mean is 1.182 questions and refusal mean 2.000, above the 1.0 limit. One held-out consequential admission differs from the sealed record; the zero-harm requirement is not established. The gate fails independently on settlement and questioning, even if subsequent provenance review clears that flag. A paused ticket with unavailable user information is never counted as settled.

## Per class

| Partition | Class | Tickets | One-round settled | Full original matches | Questions | Mean | Flags |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| dev | family | 26 | 7 | 8 | 30 | 1.154 | 1 |
| dev | question | 3 | 2 | 1 | 1 | 0.333 | 1 |
| dev | refusal | 7 | 3 | 3 | 8 | 1.143 | 0 |
| dev | visual | 4 | 4 | 0 | 0 | 0.000 | 2 |
| held_out | family | 22 | 12 | 8 | 26 | 1.182 | 1 |
| held_out | question | 1 | 1 | 1 | 0 | 0.000 | 0 |
| held_out | refusal | 3 | 0 | 0 | 6 | 2.000 | 0 |
| held_out | visual | 2 | 2 | 0 | 0 | 0.000 | 0 |

## Before and after

The previous fresh development capture on `fda65b8`, re-scored conservatively from its retained finals under this same evaluator, has 14/40 one-round settlements, 11 adopted scopes, 48 questions (mean 1.200), 12/40 full original consumer matches, and 50 provider calls. The current fresh pass has 16/40 settlements, 12 adopted scopes, 39 questions (mean 0.975), 12/40 full matches, and 48 calls. These are separate stochastic samples; the full-record score did not improve. The retained-response dev-v9 audit's 37 questions and 13 matches remain separate historical results, not substituted for this fresh pass.

The earlier one-shot held-out 9/28 result measures full structured record agreement. The current interactive held-out full match is also 9/28; the 15/28 settlement metric includes appropriate semantic refusals and user-confirmed scope adoption, so it must not be presented as an increase from 9/28 to 15/28 accuracy. Goldens and split were not changed.

## Consequential differences: not silently cleared

| Ticket | Fields | Retained evidence and limitation |
| --- | --- | --- |
| Dev family-E-terse | model_id, measure_id | The named report and measure resolve and a no-figure freshness route is admitted without a visual. The sealed record instead expects TARGET_AMBIGUOUS and null identities. No visual, figure or timing evidence was invented; the admission/refusal discrepancy remains recorded. |
| Dev question-stale-no-sla | model_id, measure_id | Same no-target freshness admission versus sealed TARGET_AMBIGUOUS. A resolved measure is not evidence of currency. |
| Dev visual-3 | filters, selection_value | North / Component 1 survives as a VALUE_ONLY symbolic selection request, while the sealed record requires two concrete cell-key filters. No keyed quantity was executed. Exact scope is unresolved at this stage; this cannot be claimed as faithful completed cell intake. |
| Dev visual-5 | selection_value | A bookmark label was interpreted as a symbolic value request; the sealed record has no such selection. Saved bookmark invocation cannot be established by that nomination. |
| Held family-G-terse | model_id, measure_id | Source comparison was user-confirmed from the sealed text, and the named measure was resolved without a visual; the sealed record still expects TARGET_AMBIGUOUS. Comparison confirmation does not itself clear the target/admission discrepancy. |

Automatic flags are candidate harmful admissions, not a causal or wrong-value verdict. The checker explicitly returns REQUIRES_PROVENANCE_REVIEW. This report does not self-award harmful-error rate zero, change expected records, or clear a flag solely because new code permits the state. Held-out responses were not used to tune the candidate.

## Failures and unavailable replies

All 68 operations returned without an uncaught operation exception. All 82 provider requests have retained responses and the tapes have no recording exclusions. Source-level extraction validation and adoption refusals remain on the tapes. Twenty-one dev and ten held-out tickets received at least one unavailable simulated answer; they remain paused/held. Other failed adoptions retain their exact history and consumer error. The complete per-ticket map below distinguishes those cases from settlement.

## Budget and evidence

82 provider calls; 1,027,504 transmitted input characters, mean 12,530.54 per call. This is below the stated phase bound of 136 calls / 2,720,000 characters. Zero estate physical requests, diagnostic reads, guard requests, investigation planner calls and synthesis calls. Tapes contain 82 PROVIDER_REQUEST and 82 PROVIDER_RESPONSE events, 68 finals and all clarification/state events. These model requests are not estate reads.

All 82 provider responses carry measured usage: 209,566 input tokens, 14,090 output tokens, 223,656 total. These token counts come from retained provider bodies; they are separate from the governor's larger output-token reservation.

Daily reservations before/after: model calls 350 -> 432 against 600; input characters 5,299,181 -> 6,326,685 against 8,000,000; output-token reservation 525,000 -> 648,000 against 1,500,000. Output figures are reservations, not measured billed tokens. Ordinary rolling estate usage 0 -> 0 against 3,000 at these snapshots; Round Ten pot 1,013/1,500 with 95 restoration reserve unchanged. No ceiling, counter, credit, deployment quota, identity, permission, secret or fixture changed.

Engine hash `9468dd2d974a98fb116e02d4216a81811e9fd490fe3d3c69c971c5b37562ee48`; sealed split SHA-256 `d2c330ff5144b9f05c69c5571bb5c89a17b157d781cabc8d86c56346ded96795`; private runner SHA-256 `f073243355a66dc2bf55704b7e33a3e5ed59cb1238b2294a67db59fcbac5bcff`. Each of the 68 case hashes was checked against its unchanged split record before running, and each final tape SHA-256 was checked afterward. Raw model bodies and local databases remain under `.local/`; no raw tape is committed or newly published. One append-only ledger row per ticket carries counts and tape identity.

## Validation and lifecycle limits

Frozen 44490b4 full suite ran 2,665 tests and failed two adoption tests because their manually submitted request fixture omitted the required request_key. The public controller already requires and persists it. The test fixture now supplies the closed request envelope and asserts its retained key; production validation was not relaxed. All 36 focused adoption/input/reference/evaluator tests pass. The corrected full-suite result is recorded separately when complete; the initial failed log remains preserved. An intermediate focused command mistyped two module names; its import failures remain in tool history and were corrected by running the actual modules.

Exact-byte audit: the evaluation worktree hash remains 9468dd2d974a98fb116e02d4216a81811e9fd490fe3d3c69c971c5b37562ee48. The regression worktree hash is 88469fdc5519b46d307d141d771c9c377ec28feb9ebd275bec6cb42ccfb724e7; input_reference.py has LF there versus CRLF in the frozen checkout. All engine/transport files are equal after newline normalization. This newline-only difference is explicitly recorded rather than pretending their byte fingerprints match; no tape is relabelled or replayed under the other hash.

The lifecycle has offline tests for restart/resume, stale revisions, changed-question history, evidence reuse only under the same context/scope/cell, findings sharing, configured business/technical handoffs, and human-only closure. Synthetic read/synthesis stages replay separately. Those do not establish an autonomous live ticket lifecycle: scope adoption currently requires the existing review/start flow and attachment of its governed run. Browser presentation has not been visually exercised; link support currently takes the labelled optional report_link field, and link predicates/bookmarks refuse explicitly rather than lose context. Interactive privacy-projected tickets remain refused before raw persistence.

DECIDED WITHOUT REVIEW: corrected the invalid test fixture instead of making request_key optional in the consumer. Rejected alternative: weakening the input contract to satisfy a manually constructed pre-envelope test. No engine behavior or scored response changed after the freeze. Also retained model/measure/selection differences as consequential audit flags rather than hiding them behind target equality.

## What remains

Phase A needs faithful multi-key cell confirmation, a clear supported route for explicit within-report comparators, fewer redundant questions, and automatic governed execution after settled intake. Genuine target ambiguity and unavailable sealed replies stay unresolved. Their expectation records were not edited. Screenshot/vision Phase B cannot begin under this failed quality gate. The [one-page OTHER_REPORT design](round-eleven-other-report-design.md) is available for review; it is not implemented and requires approval of the paired-scope contract. No unfamiliar-domain or general-capability claim is earned.

## Complete 68-ticket map

Scope adoption is an intake result, not an investigation completion. Q counts individual questions; an unavailable answer is not a successful clarification. Original match covers every sealed structured field.

| Partition | Ticket | Intake result | One-round settled | Original match | Q | Calls | Input chars | Unavailable |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| dev | original:family-B-noisy | SCOPE_ADOPTED | True | True | 1 | 2 | 25,816 | 0 |
| dev | original:family-B-terse | HELD | False | False | 1 | 1 | 12,527 | 0 |
| dev | original:family-B-typo | HELD | False | False | 1 | 1 | 12,562 | 0 |
| dev | original:family-D-noisy | HELD / TARGET_AMBIGUOUS | False | True | 2 | 1 | 12,822 | 2 |
| dev | original:family-D-terse | HELD / TARGET_AMBIGUOUS | False | True | 2 | 1 | 12,536 | 2 |
| dev | original:family-D-typo | HELD / INTAKE_EXTRACTION_INVALID | False | False | 2 | 2 | 25,327 | 2 |
| dev | original:family-E-mention | SCOPE_ADOPTED | True | True | 0 | 1 | 12,714 | 0 |
| dev | original:family-E-noisy | HELD | False | False | 1 | 1 | 12,818 | 1 |
| dev | original:family-E-terse | SCOPE_ADOPTED | True | False | 0 | 1 | 12,532 | 0 |
| dev | original:family-E-typo | HELD / INTAKE_EXTRACTION_INVALID | False | False | 1 | 2 | 25,307 | 1 |
| dev | original:family-H-noisy | HELD / TARGET_UNRESOLVED | False | False | 2 | 1 | 12,837 | 2 |
| dev | original:family-H-terse | HELD / TARGET_AMBIGUOUS | False | False | 2 | 1 | 12,551 | 2 |
| dev | original:family-H-typo | HELD / INTAKE_EXTRACTION_INVALID | False | False | 2 | 2 | 25,357 | 2 |
| dev | original:family-I-noisy | HELD | False | False | 2 | 1 | 12,821 | 2 |
| dev | original:family-I-terse | HELD | False | False | 2 | 1 | 12,535 | 2 |
| dev | original:family-I-typo | HELD / INTAKE_EXTRACTION_INVALID | False | False | 2 | 2 | 25,317 | 2 |
| dev | original:question-change-days | HELD / UNIMPLEMENTED_ROUTE | True | True | 0 | 1 | 12,562 | 0 |
| dev | original:question-hiding-rows | HELD / INTAKE_EXTRACTION_INVALID | False | False | 1 | 2 | 25,340 | 1 |
| dev | original:question-stale-no-sla | SCOPE_ADOPTED | True | False | 0 | 1 | 12,538 | 0 |
| dev | original:refusal-business-benchmark | HELD / UNIMPLEMENTED_ROUTE | True | True | 0 | 1 | 12,505 | 0 |
| dev | original:refusal-business-intent | HELD / UNIMPLEMENTED_ROUTE | True | True | 0 | 1 | 12,525 | 0 |
| dev | original:refusal-business-q49 | HELD / UNIMPLEMENTED_ROUTE | True | True | 0 | 1 | 12,483 | 0 |
| dev | original:refusal-two-figures | HELD | False | False | 2 | 1 | 12,574 | 2 |
| dev | original:refusal-unidentified-visual | HELD / INTAKE_EXTRACTION_INVALID | False | False | 2 | 2 | 25,223 | 2 |
| dev | original:refusal-unsupported-filter | HELD / TARGET_AMBIGUOUS | False | False | 2 | 1 | 12,550 | 2 |
| dev | original:refusal-unsupported-relative | HELD / TARGET_AMBIGUOUS | False | False | 2 | 1 | 12,573 | 2 |
| dev | original:visual-1 | SCOPE_ADOPTED | True | False | 0 | 1 | 12,544 | 0 |
| dev | original:visual-3 | SCOPE_ADOPTED | True | False | 0 | 1 | 12,585 | 0 |
| dev | original:visual-4 | SCOPE_ADOPTED | True | False | 0 | 1 | 12,552 | 0 |
| dev | original:visual-5 | SCOPE_ADOPTED | True | False | 0 | 1 | 12,667 | 0 |
| dev | original:family-B | SCOPE_ADOPTED | True | True | 0 | 1 | 12,575 | 0 |
| dev | original:family-D | HELD | False | False | 1 | 1 | 12,634 | 1 |
| dev | original:family-E | SCOPE_ADOPTED | True | True | 0 | 1 | 12,630 | 0 |
| dev | original:family-H | HELD / UNIMPLEMENTED_ROUTE | False | False | 0 | 1 | 12,642 | 0 |
| dev | original:family-I | HELD | False | False | 2 | 2 | 25,470 | 1 |
| dev | rebuilt:family-B | SCOPE_ADOPTED | True | True | 0 | 1 | 11,542 | 0 |
| dev | rebuilt:family-D | HELD | False | False | 1 | 1 | 11,601 | 1 |
| dev | rebuilt:family-E | SCOPE_ADOPTED | True | True | 0 | 1 | 11,597 | 0 |
| dev | rebuilt:family-H | HELD | False | False | 1 | 1 | 11,609 | 1 |
| dev | rebuilt:family-I | HELD | False | False | 2 | 1 | 11,535 | 1 |
| held_out | original:family-A-mention | SCOPE_ADOPTED | True | True | 1 | 1 | 12,693 | 0 |
| held_out | original:family-A-noisy | SCOPE_ADOPTED | True | True | 1 | 1 | 12,797 | 0 |
| held_out | original:family-A-terse | SCOPE_ADOPTED | True | True | 1 | 1 | 12,511 | 0 |
| held_out | original:family-A-typo | HELD / INTAKE_EXTRACTION_INVALID | False | False | 2 | 2 | 25,265 | 0 |
| held_out | original:family-C-noisy | SCOPE_ADOPTED | True | False | 1 | 2 | 25,774 | 0 |
| held_out | original:family-C-terse | HELD | False | False | 1 | 1 | 12,505 | 0 |
| held_out | original:family-C-typo | HELD / INTAKE_EXTRACTION_INVALID | False | False | 1 | 2 | 25,267 | 0 |
| held_out | original:family-F-noisy | HELD | False | False | 2 | 1 | 12,811 | 1 |
| held_out | original:family-F-terse | HELD | False | False | 2 | 1 | 12,525 | 1 |
| held_out | original:family-F-typo | HELD / TARGET_UNRESOLVED | False | False | 2 | 1 | 12,560 | 1 |
| held_out | original:family-G-mention | SCOPE_ADOPTED | True | True | 1 | 1 | 12,763 | 0 |
| held_out | original:family-G-noisy | HELD / TARGET_UNRESOLVED | False | False | 2 | 2 | 25,924 | 1 |
| held_out | original:family-G-terse | SCOPE_ADOPTED | True | False | 1 | 1 | 12,581 | 0 |
| held_out | original:family-G-typo | HELD / INTAKE_EXTRACTION_INVALID | False | False | 2 | 2 | 25,405 | 1 |
| held_out | original:question-change-week | HELD / UNIMPLEMENTED_ROUTE | True | True | 0 | 1 | 12,553 | 0 |
| held_out | original:refusal-nonexistent-column | HELD / TARGET_AMBIGUOUS | False | False | 2 | 1 | 12,528 | 2 |
| held_out | original:refusal-two-figures-total | HELD | False | False | 2 | 1 | 12,538 | 2 |
| held_out | original:refusal-unidentified-measure | HELD / INTAKE_EXTRACTION_INVALID | False | False | 2 | 2 | 25,229 | 2 |
| held_out | original:visual-2 | SCOPE_ADOPTED | True | False | 0 | 1 | 12,565 | 0 |
| held_out | original:visual-6 | SCOPE_ADOPTED | True | False | 0 | 1 | 12,563 | 0 |
| held_out | original:family-A | SCOPE_ADOPTED | True | True | 1 | 1 | 12,580 | 0 |
| held_out | original:family-C | SCOPE_ADOPTED | True | False | 0 | 1 | 12,560 | 0 |
| held_out | original:family-F | HELD | False | False | 1 | 1 | 12,613 | 1 |
| held_out | original:family-G | SCOPE_ADOPTED | True | True | 1 | 1 | 12,669 | 0 |
| held_out | rebuilt:family-A | SCOPE_ADOPTED | True | True | 1 | 1 | 11,547 | 0 |
| held_out | rebuilt:family-C | SCOPE_ADOPTED | True | False | 0 | 1 | 11,527 | 0 |
| held_out | rebuilt:family-F | HELD | False | False | 1 | 1 | 11,580 | 1 |
| held_out | rebuilt:family-G | SCOPE_ADOPTED | True | True | 1 | 1 | 11,636 | 0 |

Machine-readable counts, per-field differences and all 68 tape hashes are in [the result record](round-eleven-phase-a-results.json). Original raw responses, failures and superseded exploratory results are retained locally, unchanged.

Dated final regression result, 2026-10-09: the corrected request-fixture suite completed all 2,665 tests in 543.092 seconds, OK. Initial failed 44490b4 log and ResourceWarnings remain retained. A separate 110-test lifecycle/safety pass completed in 24.599 seconds, OK, including wrong-cell, comparison-span and both sealed competing-figure cases. Together with the 36 focused input/adoption checks, this establishes offline regression behavior, not the failed intake quality gate or live lifecycle readiness.

Dated command-wrapper audit: the full-suite tool returned exit1 while its unittest log reports2,665 OK. A zero-exit Python process writing only to stderr reproduces tool exit1 under the same PowerShell redirection; explicitly printing LASTEXITCODE reports0. This supports a wrapper/redirection artifact, not an additional unittest failure. The original command status is retained rather than relabelled.
