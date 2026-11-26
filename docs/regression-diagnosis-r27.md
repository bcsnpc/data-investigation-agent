# Round 27 regression diagnosis

Owner steer, 2026-11-21. Saved dev evidence only: **zero new model calls, zero estate queries, no injection, IAM or key change**. Calibration $14.34 and the $3 reserve remain protected. Pass 2 and calibration have not started.

## Main finding

**The clearest demonstrated regression is delivery, not a demonstrated loss of SQL/DAX ability.** The passing R26 guard runs already used `claude-opus-5-5` for investigation reasoning. Auxiliary vision routing did change, as recorded below. These forms bypass text-model extraction, so switching the default intake model cannot explain their regressions.

R27 inserts a structured conclusion contract and a separate evaluator. Correct native checks can now end unresolved because of a verdict-label mismatch, an uncited retained definition, or malformed evaluator output. Exploratory choices also differ, but saved observations cannot isolate which prompt sentence caused a stochastic query choice. This report distinguishes the first observed divergence from a directly demonstrated blocking code change.

The common code divergence occurs before the first investigation call: `Factory` adds `conclusion_contract=question-first-v1`; the finding schema adds direct answer, verdict class, calculation, undecided facts, routing and context gap; the prompt adds the R27 instructions. Relevant commits:

- `ce5e5249`: structured conclusion and reasoning-model intake default.
- `0f8b1a74`: unresolved candidate routing and bounded analysis tools.
- `0b12e9e5`: separate delivery evaluator.
- R26 `b6515585`: metadata reads and terminal per-layer findings.
- R26 `54891aea`: native operational route and source-history requirement.
- `be73c5ff`: mid-pass metadata transport/evaluator-output repair.
- `062a2bfb` and `f0d14fcd`: later offline repairs; **not used to rewrite or rerun these pass-1 outcomes**.

## Baseline and coverage

The owner-selected code baseline is **v0.24**, tag `02040ba5e360c96a376bf208739bb23781a021a1`. Round 25 records frozen merge `7f5d2b0d3a498485b03184384a9bac5e8ddbdf0`, with its nonbudget investigator runtime unchanged. The paired passing traces below are the R26 runs explicitly pinned when the regression guard was selected, all on image `1e0016e4` with Opus 5.5 investigation reasoning. They satisfy the requested “v0.24 or R26” passing-reference rule; they are not fresh v0.24 measurements. R25 held-out accuracy is not a denominator for this dev subset. No held-out set was opened.

Coverage: **11 reviewed failing guard tickets, four provisional secondary-only failures**, and the separate older-export pair. The harmful fixture-quantity ticket is included. Three guard tickets remain fully correct: application-baseline-v2, other-collected-definition-v2 and waiting-application-load-v2. Both access-export variants are unrun, so cannot be called regressions. All prior capture seals and downloaded audit-batch hashes were verified. The report/page/visual/measure/table, issue kind, figure, comparison, details, wording and screenshot fields are identical in all15 paired delivered intakes. The form input itself did not change. [The paired receipt](regression-diagnosis-r27.json) retains seals, action ordering, query counts and exact failed-query text; full captures remain private.

## Per-ticket first divergence and cause

Sequence numbers refer to each run's own native audit ordering. “Confirmed” describes an exercised code branch, not a proven causal effect of a prompt change. Provisional rows have no completed primary review yet.

| Ticket | First observed divergence, old → new | Where delivery fails; responsible change | Recommendation |
|---|---|---|---|
| v2-application-baseline-v1 | Old first batch21 reads `get_definition` and values. New21 omits that definition read and adds row/distinct counts to DAX. | Both establish 7,661 across model, landing and source. New draft36 enters added evaluator41: incomplete output, then uncited-lineage rejection, finally UNRESOLVED. **Confirmed R27 evaluator/citation obstruction**; prompt causation of the omitted read is unproved. | **Fix** evaluator failure handling and citable retained definitions. |
| v2-billing-invoices-v2 | Initial layer checks are similar. Old later hits an unavailable object and recovers; new native diagnostics succeed. | Old repairs finding arguments and delivers. New draft65 enters evaluator70, which is incomplete; further analysis/read attempts hit the unchanged physical cap. **R27 evaluator, then extra tool spending.** | **Turn off** the blocking evaluator for a controlled ablation; retain code checks and independent grading. |
| v2-billing-mrr-v1 | Old first DAX recreates with SUMX/FILTER/RELATED as well as reading the measure. New first DAX reads the measure and recreates later. | Both have the same unsupported National SQL literal and graph/native-ID error, and recover. Only new then fails repeated incomplete evaluation. **Not a newly introduced SQL restriction.** | **Fix** evaluator and definition citations; keep read-only validation. |
| v2-failed-application-load-v1 | Old starts with three value reads. New21 reads job evidence first, then performs the value comparison28. | Both correct a graph/native-layer argument. New also cites a fetch wrapper, then the evaluator requires additional impact/support and rejects or truncates. **R27 structured delivery/evaluator**, not evidence that run-first reading is wrong. | **Keep** run-first; **fix** native job status versus numeric-impact delivery. |
| v2-failed-billing-transform-v1 | First batches are similar. New48 selects an unavailable object; the old corresponding diagnostics succeed. | Old repairs identifier/unsupported-number drafts and delivers. New cites a failed read, then evaluation demands causal attribution beyond the native failed run and reaches the tool limit. **Changed query choice plus R27 delivery loop**; no evidence the same valid old query became forbidden. | **Fix** query selection/citations and operational answer scope. |
| v2-fixture-quantity-v1, harmful | Old first DAX reads only `[Handled Quantity]`. New22 adds unresolved `[Activity Entries]`; existing member validation refuses it. | New corrects DAX44 and recovers 8,765 and the 7,661→8,765 duplicate-join evidence. Evaluation still fails; the terminal answer leads with the recovered DAX error. **Confirmed R27 evaluator × R26 terminal fallback interaction.** | **Fix** neutral fallback and definition references; keep the harmful flag and safety checks. |
| v2-latency-record-v1, provisional | Old first uses record_trace alone. New21 also requests job runs twice, then repeats current/history checks. | Old delivers after seven query results; new has ten and reaches physical closure before supported delivery. Source-history requirement already existed in the old R26 run. **Extra operational/history work**, not a demonstrated new syntax restriction. | **Fix** repeated work and comparison planning; retain source/history qualification. |
| v2-record-absent-everywhere-v1 | Both begin with empty key lookups. Old follows with counts/ranges; new adds `sys.tables`36. | Metadata compiles but reaches a transport business-object allowlist and terminates `SQL_OBJECT_NOT_ALLOWED`. **Confirmed R26 metadata compiler/gateway mismatch**, repaired by the R27 transport fix. | **Keep/fix** independently revalidated catalog reads; never widen business-object access. |
| v2-record-repeated-gold-v2 | Both trace keyed rows; new adds an early diagnostic and rereads more layers. | Old delivers after seven query results. New has nine, then malformed evaluation and uncited retained-definition claims block delivery. **R27 evaluator/citation gap.** | **Fix** retained-definition citations and evaluation failure handling. |
| v2-screenshot-record-01-v1 | Both start with scoped record_trace. New batch35 proposes DAX outside the single table-valued EVALUATE contract. | Old repairs draft ID/number errors and delivers. New later cites a failed read and repeats traces/evaluation until limit: 13 query results versus six. **Changed proposal plus R27 delivery loop**; grammar was already enforced. | **Fix** recovery and cite successful keyed checks. |
| v2-screenshot-record-02-v1, provisional | Old first uses DAX plus screenshot lookup. New first traces rows and delays direct DAX. | Old recovers from a failed screenshot lookup and one bad DAX. New has two bad DAX reads and 14 query results versus six, then failed-read citation/evaluation problems. **Tool/query choice and delivery loop**; old vision used Terra twice, while the new run never invoked the vision step. | **Fix** recovery and use the actual observed screenshot key. |
| v2-screenshot-record-03-v1, provisional | Shared first trace; new adds more SQL and later repeats the trace. | Old recovers from three query errors. New has only two, but fails source coverage and spends further reads on row_layer_diff after draft94. **R27 coverage/tool-allocation interaction**, not more syntax errors. Its vision role also changed from Terra to Opus; that is a confound, not an isolated cause. | **Fix** coverage planning; **keep** row diff optional. |
| v2-screenshot-record-04-v1 | Old uses CALCULATETABLE/SELECTCOLUMNS. New filters a projection with an unresolved member, then retries. | Old delivers after three successful reads. New draft42 lacks the implemented-rule verdict required by the new contract, then cites a fetch wrapper and misses source coverage. **Confirmed structured-contract rejection**, plus a different bad query proposal. | **Fix** contract/schema alignment and recovery. |
| v2-source-history-v2, provisional | Old follows record_trace with evidence, DAX and job history. New adds more current, lineage and temporal diagnostics. | Old passes despite one failed metadata query. New has **zero query failures**, obtains current/history rows, but after ten results hits physical closure and evaluator rejection of uncited SUM/DirectLake/copy statements. **R27 citation/evaluator and spending obstruction.** | **Fix** citing existing definitions and deliver the supported historical comparison before optional expansion. |
| v2-warehouse-scope-v1 | Both first reproduce two warehouse scopes. Old draft verdict is `different question`. New keeps that verdict but adds `verdict_class=AS DESIGNED`. | The new pair is rejected by the structured conclusion validator before legacy finding validation. Further retries hit definition, coverage and evaluator requirements despite reproducing 2,948/2,084 in all three layers. **Confirmed R27 contract/schema/prompt mismatch.** | **Fix** different-question versus AS DESIGNED mapping; do not invent an equivalent scope. |

## Older export movement 1: a nominal pass, not a reliable passing answer

The main-pass reviewer has all three match bits **true**, but its reason explicitly says the answer does **not** match the expectation and fails to explain the earliest retained-history boundary. Handoff quality is 1. The raw old outcome is BLOCKED, with rendered UNRESOLVED; it leads with an ambiguous DAX-member error and has no accepted `submit_finding`.

Thus the previous “before 1 correct / after 0” arithmetic reflects stored bits, **not proof that a genuinely correct answer regressed**. That interpretation is corrected here. No score or grader record is changed.

Step comparison:

1. Original intake: lookup3, resolve9, resolve15. Repair: lookup3, resolve9.
2. Original traces56 and lists candidates74. Repair traces/lists50 and reads lineage/evidence68.
3. **Both initially follow Warehouse Operations while the ticket names the ordersops application export.** Both try a source-layer ID that is not active on that chosen path. This shared source-root/candidate problem predates the two plumbing repairs.
4. Repair reaches additional temporal metadata/source reads and drafts not-found126. It nevertheless claims history has no time limit without establishing the earliest retained snapshot; temporal-column validation and final evaluation prevent delivery.

The first visible difference is the shorter intake repair sequence; there is no evidence that gateway repair or evaluator output length caused the shared wrong path. **Fix explicit-source routing and contradictory grading separately.** Do not treat the nominal old grade as technical truth or edit either expectation/trace.

## Harmful fixture quantity: recovered failure became the explanation

Old: `EVALUATE ROW("Handled Quantity", [Handled Quantity])`; seven query results, no query errors. It measures model/Gold 8,765 versus source/Silver 7,661, duplicate product-7 rate rows, and product-7 units 1,104→2,208, then delivers the retained join mechanism.

New: adding `[Activity Entries]` fails the same existing validator. Corrected DAX later returns 8,765 and the duplication evidence is recovered. Incomplete/rejected evaluations still downgrade delivery. The R26 terminal fallback selects the old read error as its lead explanation instead of recognizing its recovery.

The demonstrated chain is **R27 evaluator downgrade → R26 misleading terminal wording**. Prompt causation of the extra measure is not isolated. The reviewed harmful flag remains 1, including its separately recorded winner-label/prose inconsistency. The already-qualified neutral wording/definition-reference repair has no live recovery result; it is not retroactively applied here.

## Auxiliary model routing is a separate change

R27 cloud routing hardcoded SCREENSHOT, SUMMARY and EVALUATOR to the investigator model, ignoring their configured step selections. This is separate from intake. Saved step-cost records show:

| Screenshot ticket | Old vision calls | New vision calls |
|---|---|---|
| record01 | None | None |
| record02 | Terra,2 | None |
| record03 | Terra,2 | Opus,2 |
| record04 | None | None |

Thus screenshot03 is not a same-model vision comparison. No evidence establishes that the model change caused its failure; both query selection and delivery also differ. Three new independent routing switches retain the current investigator-model default but allow each role to use its own configured step. The routing test checks each role separately and confirms the other roles and credentials/configuration are unchanged. No model was called. Recommendation: **FIX role selectability and measure separately**, rather than crediting or blaming Opus vision from this single pair.

## Why query errors became the top backtrack group

| Matched 15 guard pairs | Query results | Failed query results | Failure rate |
|---|---:|---:|---:|
| Old passing R26 | 96 | 9 | 9.4% |
| New R27 | 129 | 9 | 7.0% |

Both contain seven wrong-column/object failures and two validator failures. These are recorded query results, not all tool errors or unique statements. Cached repeats do not produce a fresh native query.

The prior backtrack classified the **first relevant mistake**, including mistakes later recovered. Nine query-first labels did not prove worsening query construction or that syntax caused all nine final failures. The paired sample has equal error counts and more overall reads in the new runs. This is an observational comparison, not a new quality score.

Concrete comparisons:

- Fixture quantity adds an unknown measure in new DAX; the validator correctly refuses it, and a correction succeeds.
- MRR uses the unsupported National literal in **both** old and new passing/failing traces.
- Screenshot03 has **three** old errors and **two** new errors; the new failure is subsequent coverage/spending.
- Source-history-v2 has **one** old error and **zero** new errors; new delivery still fails.
- `query_dax.compile_query` is AST-identical between v0.24 and the pre-steer current engine. SQL added bounded temporal BETWEEN/Spark VERSION support; that does not explain the existing National-literal refusal.

The metadata compiler/gateway mismatch is real and separately attributable. It is not a reason to remove independent read-only/object checks. A controlled flag ablation is needed to isolate prompt effects; **none was run in this task**.

## Grouped recommendations

| Change | Recommendation |
|---|---|
| Opus intake | **Keep.** The old passing reasoning model was already Opus. The form subset does not test text extraction. |
| Candidate routing/native containment | **Fix** explicit-source rooting. Keep exact addresses, retained filters and unique-match requirements. The old/new older-export path issue is shared. |
| Structured conclusion | **Fix** label/schema alignment and operational-status versus numeric-impact distinctions. Keep a direct answer, findings and routing. |
| Blocking evaluator | **Turn off for a controlled diagnostic ablation**, not as a default change here. Retain deterministic evidence/overclaim checks and independent grading. Malformed evaluation is not technical disproof. |
| Evaluator output repair | **Keep** 3,200-token limit and incomplete-versus-rejected diagnostics. They do not fix a valid but overbroad rejection. |
| Metadata gateway repair | **Keep** exact independent catalog-payload revalidation; off restores refusal, never more data access. |
| Query validator | **Keep** safety and correct dialect/member/object restrictions; **fix** feedback and recovery. Old passing runs also hit these rules. |
| Question-first/operational prompts | **Fix**, then ablate independently. Added requirements and repeated operational/history work correlate with spending, but exact prompt causality is unproved. |
| Contribution/row-diff tools | **Keep optional**; avoid rereading established results or expanding after the read phase closes. |
| Terminal report | **Fix wording, keep findings.** A recovered error must not become the discrepancy cause. |
| Definition references, source-label deferral, identifier-role hints | **Keep** the qualified offline fixes; measure later. Do not rewrite pass-1 outputs. |
| Grader consistency | **Fix separately.** Older-export all-true bits contradict its reason and raw answer. Original scores remain unchanged. |

## Configuration switches

Trusted `guided-investigation/1` specifications now accept `regression_flags`: **33 independent booleans, each defaulting to its current behavior (true)**. Unknown names/nonbooleans are rejected. Flags are request-local, reset after exceptions, and logged as `REGRESSION_FEATURE_CONFIGURATION`. Ticket text/intake cannot set them.

Example only; not deployed or run:

```json
{"regression_flags":{"r27_delivery_evaluator":false,"r27_structured_delivery":true}}
```

The complete switch list and behavior descriptions follow. Turning all switches off does **not** promise byte-identical v0.24 emulation: estate snapshots, provider libraries and safety hardening remain current.

| Flag | Default | Independent behavior | Recommendation |
|---|---|---|---|
| `r26_native_containment` | true | Resolve loose table names through declared native container membership. | KEEP |
| `r26_named_page_lookup` | true | Use named-page lookup during intake prefill. | KEEP |
| `r26_source_history_requirement` | true | Require matched source-history evidence before a latency claim. | FIX |
| `r26_metadata_reads` | true | Admit bounded catalog/INFO/Delta metadata reads through independent validation. | KEEP |
| `r26_temporal_extensions` | true | Permit newly supported BETWEEN temporal / Spark VERSION syntax. | KEEP |
| `r26_operational_fastpath` | true | Route report-free named job questions through native status facts. | KEEP |
| `r26_access_priming` | true | Read access definitions before other access-question tools. | KEEP |
| `r26_operational_priming` | true | Read native run evidence first for operational question kinds. | KEEP |
| `r26_final_action_reserve` | true | Reserve the final tool slot for delivery. | KEEP |
| `r26_terminal_report` | true | Append per-layer findings and honest unresolved handoff. | FIX |
| `r27_reasoning_model_intake` | true | Default extraction to the configured investigator model; off uses configured INTAKE. | KEEP |
| `r27_candidate_routing` | true | Pass bounded unresolved target alternatives into investigation. | KEEP |
| `r27_structured_delivery` | true | Require/render question-first structured conclusion fields. | FIX |
| `r27_question_first_prompt` | true | Append the Round27 question-first/candidate/as-designed reasoning guidance. | FIX |
| `r27_delivery_evaluator` | true | Run the separate model delivery evaluator after code evidence checks. | TURN OFF for controlled ablation only |
| `r27_evaluator_format_repair` | true | Use3200 output tokens and distinguish malformed/truncated evaluation from rejection. | KEEP |
| `r27_contribution_tool` | true | Expose bounded contribution analysis. | KEEP |
| `r27_row_diff_tool` | true | Expose bounded row-level layer comparison. | KEEP |
| `r27_metadata_gateway_revalidation` | true | Revalidate pure catalog SQL payloads at transport; off restores refusal. | KEEP |
| `r27_retained_definition_references` | true | Give existing retained definitions independently citable case evidence IDs. | KEEP |
| `r27_identifier_role_descriptions` | true | Explain graph/native/evidence identifier roles in tool descriptions. | KEEP |
| `r27_selected_target_restore` | true | Restore a reversible selected_target alias before local validation. | KEEP |
| `r27_source_label_deferral` | true | Retain loose unbound source labels for investigation without selecting a source. | KEEP |
| `r27_neutral_unresolved_wording` | true | Do not turn the first failed query into a discrepancy cause. | FIX |
| `r27_candidate_refusal_handling` | true | Represent id-less query-limit refusal as unavailable candidate, never a match. | KEEP |
| `r26_investigation_prompt` | true | Use the current investigation prompt; off uses the exact v0.24 literal, with safety still enforced in code. | FIX |
| `r26_extraction_prompt` | true | Use the current extraction prompt; off uses the exact v0.24 literal. | FIX |
| `r26_metadata_prompt` | true | Show newly added metadata examples in query-dialect guidance. | FIX |
| `r26_current_fault_consistency` | true | Require current native faults to be explained before an as-designed conclusion. | FIX |
| `r26_native_candidate_scope` | true | Enable retained native candidate-scope compilation; off refuses the optional probe, never drops its filters. | KEEP |
| `r27_reasoning_model_screenshot` | true | Use investigator model for screenshot; off restores that role's configured ai_routing selection. | FIX |
| `r27_reasoning_model_summary` | true | Use investigator model for summary; off restores that role's configured ai_routing selection. | FIX |
| `r27_reasoning_model_evaluator` | true | Use investigator model for evaluator; off restores that role's configured ai_routing selection. | FIX |

Existing independent R26 settings remain: `ai_routing` step/provider/model selection, `intake_strategy`, `intake_cascade`, `investigator_cascade`, and `diagnostic_prompt_cache`. These remain explicit installation choices. Authentication, IAM, secrets, read-only enforcement, budgets/reserve, evidence identity and held-out sealing are **not disableable flags**. A routing flag does not approve a new provider purpose or spend; existing provider/purpose gates still apply. PostgreSQL hardening and budget-accounting corrections are not rolled back as quality ablations.

Disabled metadata/candidate features refuse or report unavailable; they never remove filters or widen scope. The selected-target/candidate-refusal repair switches can reproduce historical strict behavior for offline diagnosis; shipping those defects is not recommended. Evaluator-off still invokes deterministic finding validation. Optional v0.24 prompt literals are retained as data with their original code provenance.

## Exact saved AWS error

Both `form-batch14` and `form-batch15` end with:

```text
investigator.adapters.reasoning_bedrock.BedrockError: BEDROCK_AccessDeniedException
```

API: **Bedrock Runtime Converse**, region `us-east-1`, model `amazon.nova-pro-v1:0`, existing user `dia-bedrock`. Configured endpoint: `https://bedrock-runtime.us-east-1.amazonaws.com/model/amazon.nova-pro-v1%3A0/converse`.

The adapter converts `botocore.ClientError` into `BedrockError` and suppresses the original AWS message to avoid credential/header identifiers. The full `Error.Message`, request ID and HTTP status are **not persisted in these failed grading logs**. I cannot recover or quote a more specific denial from saved evidence, or establish IAM versus account/billing/model access as the cause. Existing STS identity verification passed; the saved read-only policy simulation and model-availability checks were themselves denied. **No AWS request, retry, IAM or key change was made for this diagnosis.**

## Validation and stop

Focused checks pass: 18 flag tests, 31 Round27 tests, seven evaluator tests and three candidate-investigation tests. The first image qualification (44940760620) failed because the strict source stager excluded the two new public JSON files. The repair admits only those exact code/configuration files; private JSON remains excluded. The superseded intermediate qualification44941359410 was cancelled. Final full-suite/eight-shard qualification passed as workflow `44943235321`, source `3934ef5d`, with publication disabled. The hook-coverage test initially rejected dynamic auxiliary flag names; the final code uses explicit dependencies and all18 focused flag tests pass. The final counts and receipt are below.

No scores, expectations or captures changed. **Stop after this report under the owner steer. Do not resume pass 2 or calibration.**

Final qualification: source `3934ef5d84ffc3221679e58f0912f40d0b782638`, workflow `44943235321`: **5944 passed, 53 skipped, zero failures/errors; all eight image shards passed**. Publication and deployment were not requested. [Hash-pinned receipt](regression-diagnosis-r27-qualification.json). No model run or live estate query was made. Diagnosis complete; stopped under the owner instruction.

## Evaluator advisory proof setting

The owner-selected single ablation is `r27_evaluator_advisory=true`. It defaults to false. The evaluator remains enabled and logs its original approval, hard and soft findings, and `would_reject`. Advisory delivery preserves the deterministically validated result rather than requesting evaluator rewrites or downgrading it. Intake explicit-target and unique-match checks, cited-evidence validation, the structured delivery contract and its saved-evidence format repair stay enabled. New independent saved-evidence reviews assess whether each would-be rejection was justified; those decisions are reported separately from official correctness grades.
