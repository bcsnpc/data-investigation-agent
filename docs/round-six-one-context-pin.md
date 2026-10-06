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
