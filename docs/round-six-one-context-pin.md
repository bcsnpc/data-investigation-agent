# Round Six H: one fixture-context pin

Offline implementation, 2026-10-05 America/Chicago. #410 draft; no H cloud requests.

## Context consumers

| Module | Handle/read | Setter before H | Current owner |
| --- | --- | --- | --- |
| workspace | Workspace.store: catalog, preview, saved jobs and projections | Workspace constructor; G operator omitted replacement | pin_run_context |
| adaptive_runtime | AdaptiveRuntime.store: candidate admission, model context, procedure and synthesis | Constructor; G operator replacement | pin_run_context |
| runtime | Runtime.store / db(): worker admission, receipts and usage storage | Constructor; G operator replacement | pin_run_context |
| question_intake | Intake.store: retained intake; Intake.workspace.store: model/context catalog | Intake constructor captured original store | pin_run_context |
| screenshot_intake | Screenshots.store and Screenshots.workspace.store | Screenshots constructor captured original store | pin_run_context |
| usage_governance | UsageGovernor.runtime.store / runtime.db() | Governor constructor references runtime | pin_run_context, including alias |
| run_recording | agent.store: bootstrap databases, context pins and fixture state | Reads agent handle at operation start | Same pinned agent; pre-operation consistency check |
| adapters/microsoft_process | adapter.store and adapter.model context | Created per admitted procedure from agent store/current model | Inherits the pinned agent; no independent operator selector |
| adapters/code_lineage | current adapter.store/model context | Reads admitted adapter; manifest/ledger are evidence, not another model selector | Inherits pinned adapter |
| acceptance replay | bootstrap context_pins and copied database paths | Historical bootstrap constructor, not a live fixture selector | Preserved recording revision; all consumers constructed from one store |

The single entry point is investigator.acceptance_context.pin_run_context. It selects the latest explicitly approved context for the acceptance file's fixture state, then traverses the component graph and pins every captured store, including newly introduced consumers. It cannot move a consumer to another estate/database. The committed live runner and the new operator wrapper call this function; neither assigns a context handle. Historical operators/tapes stay untouched as evidence.

The run-start check reports every handle's database, inventory, environment, pins, resolved context ID/hash, revision and enablement. Any change or extra independent handle refuses before intake and before provider dispatch. The recorder calls it before every subsequent public operation too. It does not substitute a context ID into a preview. The engine admission check remains unchanged.

The sealed G A failure is the regression case: tape fbf26f10-038a-472c-b009-48933e4e42b2 is unchanged. A minimal hash-linked excerpt retains its selected841e425e context and previewd3b6e8e context. The test recreates that mismatch and refuses before Intake.resolve reaches its resolver. Tests also mutate each captured handle, check every value is named, discover a new consumer, refuse foreign-estate storage, and forbid individual setters in the live runner.

## DECIDED WITHOUT REVIEW

Used component-graph discovery instead of a second manually maintained setter list: another captured consumer must be pinned automatically, and a consumer added after pinning refuses. Rejected patching only Workspace.store, which would leave Intake.store and Screenshots.store stale and recreate the same class of failure. Retained the immutable G fixture-context approval and original binding proofs; no recollection, proof relabelling, identity, scope, fixture, cap or expectation change.

All fifteen inferred binding profiles were derived from retrieved code and verified on bounded values, not on snapshots; this is not global lineage equivalence. The independent declared application copy remains separately configuration-owned. Four observations: semantic true/false/false/true/true (17.0.93.25); Warehouse false/false/true/false/false (Latin1_General_100_BIN2_UTF8); application true/false/true/true/true (SQL_Latin1_General_CP1_CI_AS); Spark five false (3.5.5, no session collation setting). Observations apply only to their recorded surfaces; other containers retain owner declarations. Every binding remains SNAPSHOT_UNVERIFIED.

Targeted five pin tests and five state-selection tests passed with zero reads. Complete regression and the declared archived15-column regrade are next; no live or15x2 pass is claimed. Pot187/400,60reserved; rolling last observed237/1500, investigation cap12 unchanged. Engine bytes changed, prior freezes invalid.

## Dated H result ? 2026-10-05 America/Chicago

Section 1 completed before live execution: 2,016 runtime regression tests passed; the declared archived producer column passed15/15 locally with zero reads and on the hosted154b2c2 checkpoint (workflow37399565715, job112063467272). The six installed handles were pinned together. Historical G failure and every original tape remain unchanged. Engine changes invalidate prior freezes.

The list stopped at EMPTY's changed acceptance result. No numerical-16 or source control followed; no fixture was mutated, so no restoration was necessary. This is9 matching live projections,1 failed projection and5 unattempted cases of the15-case gate. Matching includes C's expected HELD refusal; it does not mean nine questions fully answered. No15x2 gate or unfamiliar-domain acceptance is earned. #410 remains draft and unmerged.

| Case | Run status / outcome | Acceptance projection | Diagnostic /12 | Physical | Guards | Pot before?after |
| --- | --- | --- | --- | --- | --- | --- |
| family-A | COMPLETED / TRANSFORMATION_LOGIC | PASSED | 4 | 12 | 6 | 187?199 |
| family-B | COMPLETED / NO_KNOWN_PATTERN | PASSED | 1 | 3 | 0 | 199?202 |
| family-C | HELD / no assessment | PASSED | 0 | 0 | 0 | 202?202 |
| family-D | COMPLETED / NO_COMPARABLE_PATH | PASSED | 6 | 8 | 0 | 202?210 |
| family-E | COMPLETED / TRANSFORMATION_LOGIC | PASSED | 4 | 12 | 6 | 210?222 |
| family-F | COMPLETED / CONSISTENT_TO_BOUNDARY | PASSED | 3 | 9 | 3 | 222?231 |
| family-G | COMPLETED / TRANSFORMATION_LOGIC | PASSED | 4 | 12 | 6 | 231?243 |
| family-H | COMPLETED / NO_KNOWN_PATTERN | PASSED | 1 | 3 | 0 | 243?246 |
| family-I | COMPLETED / TRANSFORMATION_LOGIC | PASSED | 4 | 12 | 6 | 246?258 |
| reproduction-empty | COMPLETED / NO_COMPARABLE_PATH | FAILED | 5 | 7 | 0 | 258?265 |

Every run has its original sealed tape, pinned databases, immutable result and one live ledger row; grading is recorded separately with zero reads. All ten used one intake call and zero investigation planner calls. Nine completed provider synthesis; C used deterministic refusal rendering. Every successful cross-surface comparison remains SNAPSHOT_UNVERIFIED. Verbatim outputs are retained under docs/runs/round-six-h-<case>-business_output.txt and technical_output.txt. Reproduction is within-layer, not a cross-surface validation.

Round pot187?265/400:78 physical requests,32 diagnostic reads and27 guards for the ten attempts. Last recorded rolling335/1500. Investigation cap12 unchanged; largest observed diagnostic count6. Sixty requests remain reserved; ordinary work still stops at340. No refund, counter reset, policy increase, new secret, identity or permission change.

### EMPTY: the first genuine changed result

Run1f96ab15-e18c-4d5d-9732-0f79a15d072e completed NO_COMPARABLE_PATH and synthesis validated. The answering cell68005673? returned BLANK under the14 September predicates. Expected: REPRODUCED EMPTY. Actual: no reproduction verdict, because intake omitted the reported state.

The original ticket says "shows nothing (the visual is empty)". The sealed intake response explicitly recognized VISUAL_CONTENT and quoted that sentence, yet emitted `reported_candidates: []`. `question_intake.FIGURE_INSTRUCTIONS` already tells the model to include an explicitly empty visual as FIGURE. The wire schema nevertheless accepts an empty candidate array; extraction produces `{state: UNSPECIFIED}` and the procedure records "No reported figure supplied." The response satisfied that shape while omitting an explicitly reported state. No span retry was triggered because no candidate existed to validate.

The business output starts "Answer to your question: No verdict: no figure supplied" and later asks the user to supply the empty state already present. This is a model interpretation/completeness failure, not a wrong BLANK value, parser refusal, context-pin mismatch or read-budget exhaustion. The reproduced BLANK was preserved without promoting it to a match. Original response, refusal and outputs are untouched; no expectation change, engine repair, replacement run or further live read followed. The tape and evidence hashes are in the separately saved reproduction-empty-diagnosis.json.

### Offline replay installation

The inferred A tape initially blocked at CLOCK:BOUNDED_REQUEST because the historical replay harness constructed AdaptiveRuntime without the installed lineage service. The sealed manifest supplies the missing installation input; it does not supply answers. The harness requires its existing sealed digest and exact adapter configuration to match before installing the archived producer's own service. Approval, ledger and code retrieval then pass through the original bounded tape events with sockets blocked.

Three blocked offline attempts are preserved: missing service; configuration mismatch from archive-root path normalization; root derivation initially attempted from an already absolute inventory path. The cause was established as recorded-versus-temporary installation root, then corrected by deriving the root from the sealed interpreter path and its manifest-relative suffix and demanding the complete projected configuration match. The fourth replay passed exact runtime decisions and outputs for A, zero reads. No tape, bootstrap, saved observation or producer implementation was changed. Seven hostile-input/factory tests, four private-delivery tests and ten acceptance-harness tests pass. The new helper test is included in the hosted workflow.

The partial second-column replay sweep is still recorded separately; live projection grades are never presented as completed byte-exact replays. Current status is reported below once that sweep ends. An archived15/15 check is not the requested15x2 check.

### Dated operator corrections

C was initially described in commentary as changed based on a fallback replay outcome name. Reading its actual acceptance file established HELD/null with PATH_CONTEXT_LIMIT as the expected result; its sealed observation retains14,813 characters against12,000. The original failed/held run was not changed or repeated; its final grade is PASSED. This correction supersedes that commentary, not the case expectation.

D's first offline output grade was invoked while synthesis was still pending and failed for absent outputs. That premature grade remains saved; the FINISHED sealed result's separate final grade passed. The local grader now refuses active runs. No D replacement occurred. An A output-printing helper also failed after printing its first output; the iteration was corrected without a live repeat. Replay-ledger writing first failed before any append on log encoding; BOM-aware reading preserved the original logs and appended four zero-read replay records once.

### DECIDED WITHOUT REVIEW ? H continuation

Registered report-15sep's preservede920dda4 context/hash as an explicit approval record for the requested fixture state, with zero recollection or reads. Rejected silently selecting a hand context in the operator; every actual run uses the single pin. Numeric16 was not subsequently attempted because EMPTY stopped the list.

Supplied the immutable whole-manifest sidecar to offline replay instead of reconstructing code-source declarations from requests or injecting stored qualifications. Rejected dropping the sealed configuration check to get a replay pass. The sidecar is selected by the already sealed manifest hash. No new private bundle, release asset or Actions secret was published because the second column is not earned.

Kept the source-copy binding separately configuration-declared. The fifteen bounded code-derived profiles and four observed semantics recorded above remain true, but they do not establish global equivalence, snapshot alignment or current source controls. Proposed prewarm was prepared only, never executed after the stop. A complete current-engine15x2 gate and its merge remain pending.

Closing local control-plane read: pot265/400 unchanged, rolling310/1500;25 earlier requests expired naturally from the rolling window after the last live335 observation. No counter reset or refund. Controls and source prewarm were not executed.
