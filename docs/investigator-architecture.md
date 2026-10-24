# Investigator architecture

## Round22 reliability foundation (amended section1)

The default CLI runner dispatches `investigation` to cloud_investigator;
`legacy-baseline` is explicit. The trusted spec binds graph scope, hashes,
compiler ports and existing budgets. Ticket text cannot select a module,
query, identity or different permitted objects.

source_availability.py owns seven failure classes and value-free messages.
Only transient source reads retry, through unchanged guarded meters. Facts
retain observed reachability separately from unavailable run history. The
investigator renders blocked layers/times/owners alongside its supported
verdict; no outage becomes a successful negative observation.

Normal audit mode uses normal_audit.AuditContext: records are secret-checked,
copied and fsynced locally, uploaded in batches, and indexed by logical audit
ID. ACKNOWLEDGED, QUICK_FACTS and ANSWER progress events publish immediately.
Partial publication cannot replace the original failure. Test mode alone
enables native/provider byte-exact tapes. New cloud status questions use only
ledger/graph facts and skip model credentials and value/native setup.

ticket_catalog.materialize opens the pinned source catalog read-only and
copies only the selected model/current context and one approved current scan
into a fresh on-disk session. No historical scan/run or unrelated model is
loaded. Graph queries already use admitted path_records, never records().
The nine state patterns below remain gated by section1e; not implemented yet.


Status quick checks top up stale/missing facts through GraphAPI.refresh_facts on the admitted ticket subjects before selecting a status. The trusted cloud spec supplies a hash-pinned PathCollector; force propagates into the incremental collector so unchanged markers cannot suppress renewed observations. A failed top-up produces typed availability evidence and blocked output; successfully refreshed empty history is a distinct no-record observation. Observational timing includes UTC capture-clock start for correlation with Azure execution start; native tapes remain unchanged.


## 2a ? Code-owned case file
`investigator_case.CaseFile` owns one versioned record per ticket: code plan/current step, evidence summaries keyed by ID, decisions, blocked calls, errors, validated model action notes and final outcome. The investigator retains snapshots after recorded actions and returns its final case in the delivery bundle. The model reads a snapshot and proposes its action summary as an annotation; it cannot write steps, evidence or final outcome. `propose` rejects invalid fields or unknown citations and logs the rejection. Serialization round-trips all fields without loss. This is retained state; resumable checkpoint loading is still section2f.
Tests: CaseTests.test_round_trip_preserves_every_code_owned_field; CaseTests.test_model_cannot_rewrite_step_evidence_or_outcome_and_rejection_is_logged; IntegratedCaseTests.test_status_run_delivers_its_code_owned_case_and_retains_snapshots.


## 2b ? Recitation
Each AzureDecision bound to the investigator's code-owned case adds a transport-only recitation object to every model response, including native definition judgment calls. The request carries the current plan/step; the response restates both. CaseFile.recite compares the full value, logs mismatches with CODE_CASE_FILE_WINS, and never advances state from that restatement. Matching recitations are silent. Native decision and transformation validators receive their unchanged contracts after the observational envelope is removed. Injected decision seams undergo the same comparison in the engine.
Tests: RecitationTests.test_matching_recitation_is_silent_mismatch_is_logged_and_cannot_advance; Decisions.test_bound_case_recitation_is_required_on_wire_and_mismatch_cannot_change_state.


## 2c ? Just-in-time retrieval
Model requests carry the case's evidence summaries and a short action history; they no longer duplicate the evidence index or retain raw ordinary tool results. A requested raw result exists in fetched_evidence for one model call, then clears. get_evidence returns the original registry record; large records carry an explicit bounded model descriptor, and get_evidence_part retrieves exact canonical text slices (offset/limit, total length and SHA-256) from that same original. Checked design witnesses retain their labelled model projection plus a route to every original byte. Native evidence and consumer validation are unchanged. Case history retains all errors/blocked signatures without raw result bodies.
Tests: JustInTimeTests.test_ordinary_tool_context_contains_summary_and_id_not_raw_definition; test_explicit_raw_fetch_is_cleared_after_the_next_model_call; test_large_raw_result_is_retrievable_in_exact_hash_bound_parts_without_context_growth.


## 2d ? Visible errors and blocked failed repeats
The code-owned case retains failed tool names, exact arguments, error type/reason and evidence IDs. Before admission, the engine derives failed-call identity from those retained errors using canonical arguments; an identical failure returns a short retained-evidence note and logs INVES?TIGATOR_CALL_BLOCKED without dispatch. Different arguments remain eligible. Non-hard exceptions produce a retained GAP; gateway/budget/state hard stops still propagate. The case's model view retains compact error and blocked-call signatures while raw failure records remain in the capture.
Test: FailedRepeatTests.test_same_failed_signature_is_blocked_different_arguments_are_allowed (one identical retry blocked, changed node dispatched, original error/gap retained).


## 2e ? Code-owned playbook tool scoping
`investigator_playbook` declares the recreate, quick_facts, investigate and deliver tool sets. Only engine code advances the case phase. Tools.invoke checks that phase before schema validation, cache access or dispatch; the model's decision schema exposes only the current phase's set. Native fact top-up belongs to quick_facts; comparisons and definition checks belong to investigate; delivery permits only reading retained evidence. Pure ledger fact inspection remains available during investigation. Internal recreate/quick-check operations are already code driven and remain guarded at their native ports.
Test: PlaybookTests.test_forbidden_tool_never_dispatches_and_code_advance_changes_tools proves compare is refused before reader dispatch in quick_facts, becomes available after code advance, refresh is excluded in investigate, and delivery cannot perform another comparison. Existing status/fact regressions remain green.


## 2f ? Checkpoint completed operations
`investigator_checkpoint` retains a hash-sealed, ticket/path/context/source/spec-pinned operation checkpoint in existing shared PostgreSQL state (no new resource or grant). It records write-ahead pending intent, completed results, the code-owned case, original evidence IDs/receipts, tool read caches and native Probe objects. Restart reconstructs the completed logical prefix locally from those records, without redispatching completed model or estate calls, then continues at the first unfinished operation. It does not restart native work. A finished checkpoint returns its original as-of result only on explicit same-case resume; new run IDs create fresh cases. Changed pins or revisions refuse reuse.
The native value port restores original probes so a later definition check can consume the same measured boundary. Prior physical owners are retained before dispatch; on cloud resume the worker reads their actual charged rows from the shared usage ledger (including interrupted requests), and carries those counts forward. No reservation is released, reset or estimated. Current-execution reads and prior charged reads are reported separately. Active elapsed time of completed steps is carried forward; interruption time is not advertised as measured investigation time. Shared checkpoint I/O has a TEST replay boundary; native/provider tapes are unchanged. FileStore is the atomic/fsynced offline test backend, not the live authority.
Tests: CheckpointTests.test_killed_investigation_resumes_completed_steps_and_identical_case_without_re_reads uses an actual child-process exit17 mid-investigation, then restarts and compares the preserved case byte-for-byte structurally while proving no completed read repeats. Corrupt/binding-mismatch and optimistic-revision tests refuse reuse; Values.test_checkpoint_restores_original_native_probes_for_later_design_checks preserves the original query/value/surface without a reread.


## 2g ? Stable system/tool prefix
For each code phase, AzureDecision now keeps instructions and tool definitions byte-stable across tickets. Admitted IDs and exact context/key are supplied in the dynamic payload. The wire uses fixed admitted_context/admitted_key references; code expands them and applies the original ticket-specific consumer schema, so invented IDs or altered scope still fail before execution. The vocabulary is generated from the stable wire schema; native child judgment schemas stay unchanged apart from the case recitation envelope.
Each usage receipt records prefix SHA-256/length and the provider's cache details. cache_metrics reports known cached/input token ratios and call hits separately from unknown usage; it does not infer missing cache counts. Checkpoints retain those observations. The first retained pre-pattern NORMAL smoke baseline is65.36% cached input tokens (52,096/79,705); it is explicitly not a measurement of this pattern. New-image live measurement is pending2j.
Tests: Decisions.test_two_tickets_have_identical_prefix_and_scope_references_expand_before_validation compares exact prefix bytes with different IDs, scope shapes and keys; test_scope_reference_transport_does_not_admit_invented_ids_or_scope preserves strict admission. Existing filtered-lower refusal test passes unchanged.


## 2h ? Optional clean-context heavy reader
Trusted spec heavy_reader.enabled_steps is empty by default and can enable only investigate. Code invokes the reader only for a large explicitly fetched record; the model cannot activate it. Each stateless child request sees one raw chunk, its source ID/hash and the prior short reading summary, not the parent transcript/ticket/tool history. It has no native execution tools. The same metered AzureDecision, deadline admission, recitation and monthly guards apply; no identity or scope is delegated. Original evidence stays in the registry and checkpoint. The parent receives a <=1000-character summary with verified source references, labelled NOT a finding, then uses the unchanged evidence checker for any verdict. Child calls and provider cache usage stay in the same case accounting.
Tests: HeavyReaderTests prove default off, explicit step enablement, clean context, bounded parent summary and refusal of invented IDs. ParentContextTests.test_enabled_reader_returns_summary_to_real_parent_loop_without_raw_growth exercises the real engine loop and confirms the raw definition is absent from the parent request while original evidence remains retained.


## 2i ? Submit/poll/outcome run harness
`run_investigator_harness.py` uses AzureCLIUser to submit a declared investigation through the existing `dia run ? --runtime azure` entry point, poll that returned execution, and fetch the exact hash-sealed final result. It does not infer delivery or correctness from Azure Succeeded. Legacy baseline requires an explicit flag and legacy-baseline target. The append-only CaseLog is hash chained and fsynced; it retains submission attempts, polling, blocks, final engine case/outcome and platform capture controls separately from estate reads. Existing logs resume polling the same submitted run; an uncertain submission cannot silently start a second one. Active-run timeout retains the execution and forbids following admissions until reconciled. Owner CLI tokens stay in memory and never enter logs. No new API/UI, identity, grant or secret is created.
The harness executes admitted/typed targets as the current CLI supports. Raw wording must pass the existing essentials intake and be mapped from its catalog/graph admission, without expectations; the harness itself does not invent missing report/measure/scope fields. This distinction will be explicit in the scored set and its clarification results.
Tests: HarnessTests.test_fixture_ticket_submits_polls_and_receives_real_engine_case_log; test_azure_adapter_submits_through_dia_cli_and_polls_the_returned_execution; uncertain-submission and corrupted-seal regressions. These are offline fixture tests; live harness exercise is pending2j.

Harness validation follow-up: each fresh submission must use per_execution binding, and a delivered ticket's text must byte-match the submitted text before an OUTCOME is logged. A wrong ticket echo is a retained BLOCK, never a score. This protects the adapter mapping without teaching the harness expectations. Two regressions cover fixed capture reuse and mismatched ticket text.

## Independent scored-set writer and grader
`evaluation_job` stores evaluation batches separately from runtime evidence and graph enrichment. It uses the existing enrichment dollar account and existing provider/Key Vault reference through `enrichment-batch`, with explicit evaluation-submit/evaluation-resume operations. The writer schema accepts only scenario description, visible labels and requested variations; the grader accepts sealed expected and delivered answers. No expected field is accepted on a writer request. The gateway re-compiles every provider request and refuses changed model, system, token bound or endpoint; investigator identities cannot use this channel. Every request/response and uncertain submission remains captured. No graph fact or runtime proof is produced by evaluation prose. A batch submitted without a receipt cannot be silently resubmitted.

## Owner frontier steer, 2026-10-23
New `ledger-case-v2` records retain successful tool results keyed by canonical tool+arguments. Exact repeats return a copy from that case and a short evidence-ID note, with a blocked-call event; the native tool is not dispatched. Model context exposes only references, not the full stored results. Old v1 serialized cases remain readable without rewriting the originals.
After a rejected verdict, code walks the first unmeasured admitted boundary, then unchecked evidence-contract hypotheses. Each selected frontier action exposes only its single tool in the retained phase record; no further model lookup occurs while this deterministic continuation executes. The key/context, native guards and verdict validator are unchanged. Three exploratory model steps without quantity/proof progress also enter this continuation. A frontier phase with no progress advances once to the next action; exhaustion returns not found with the measured furthest point. These are owner-approved progress limits, not additional spend allowances.


## Raw operational admission, Round22
NORMAL cloud runs may now receive an untyped id/text ticket. The trusted entry reads only names from its explicitly admitted graphIDs (max200; no full/historical catalog scan), admits one explicitly named job/model operational question, and writes the derived typed ticket inside the normal audit before invoking the same investigator port. It preserves original text and exact source spans. Missing or ambiguous target/time essentials yield one code-rendered question with real names, never internal IDs in display labels. Business-decision/filter-effect/quantity primary asks cannot be redirected into a job-status finding. Raw calculation admission remains explicitly UNIMPLEMENTED; it does not fall back to a prepared visual or expected answer. Typed/native paths remain unchanged. Raw TEST-mode replay is not claimed; this new path requiresNORMAL recording.

An optional run_selector lives inside the consumer FACTrequest. It selects only a uniquely matching run from the currently retained recent history, at the ticket-stated timestamp precision. An explicit date/time without the selector cannot silently become latest. Missing history, insufficient stored precision, conflicting records and same-second ambiguity refuse. The selected view drops the original hash/id and records source_fact_id plus source span; the actual ledger fact and all receipts remain unchanged. Both outputs state selection precision. Native adapter retains seventh-to-ninth fractional digits so it does not erase an exact run referent. No model/capability result is manufactured by name admission.

Tests cover raw wording through actual status consumer with an older failed run while latest succeeded; no model/quantity reads; source-span tampering; time precision and ambiguity; bounded graph candidates; grounded display names; wrong primary-ask routing; and cloud assembly forwarding the derived typed record through the existing port. Scored set and broad raw calculation admission remain pending.


## Round22 dev fixes, 2026-10-24
Raw calculation tickets now use `calculation_intake.py`: governed extraction returns token references; code resolves ranked admitted graph names, current-definition enrichment synonyms/meanings and container edges. A unique high-confidence target carries an explicit assumption; genuine ties yield one grounded question. Primary quantities and comparator quantities stay distinct, exact precision is preserved, and unresolved scope cannot fall back to a broader read. Missing comparison still allows recreation and relevant quick facts. Existing native measure profiles are selected only by exact connected asset identity. Saved visual inventory conservation and ACTIVE coverage are validated by the consumer before scope composition. Unknown declarations block rather than disappear. Periods without a faithful column binding and grouped visuals without a cell address remain explicit gaps; this is not a general route-coverage claim.

For failed-job, waiting and latency answers, the verdict consumer retains the exact supporting operational fact and same-producer current schedule. `operational_delivery.py` renders its catalog name, run ID, status, start/end, observation, error and scheduled next run in both outputs, before optional model prose could omit them. Missing fields are explicitly unavailable. Due time is distinct from an estimated update based on measured median duration. An overdue schedule never invents an unstarted run ID. Conflicting schedules are unavailable; unrelated/stale schedules cannot supply a next run. A requested historical run keeps its own error and times even if a newer run exists. Operational-only answers continue to disclaim a numerical cause.


### Round22 resumed comparison and definition wiring
Pending comparison tickets now enter the existing code-owned unresolved frontier, measuring declared layers before requesting a missing external number. The existing evidence validator checks native findings independently and qualifies external-comparison coverage. ProcessValues layer maps distinguish an absent route from a failed native query. Approved retained contexts can supply compiler-declared paths when current owner collection is unavailable, with the original context hash/as-of warnings. MicrosoftProcessAdapter.retained_measure_definition supplies the exact saved measure expression and provenance for the already-bound target; the graph journal retains it and the definition consumer renders it without a value read or business-correctness claim.
