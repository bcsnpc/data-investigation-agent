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
