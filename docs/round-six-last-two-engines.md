# Round Six G: last two engines and explicit normalization

Offline checkpoint, 2026-10-05 America/Chicago. Draft #410; no G estate request yet.

The failed application control requested one row against the worker minimum of two. SQL workers and control producers now consume `infra/scripts/WorkerResponseBounds.json`; record-budget validation precedes value execution. `process_tape.Tape` owns `finished`, not `finalized`. The shared finisher exercises the real recorder and a sweep checks all recorder self-attribute reads against declared attributes/methods. Original failed F artifacts remain unchanged.

The target's supported semantics apply explicitly to both profiles: UPPER only for case_fold, RTRIM only for trailing-space trim, then length-prefixed UTF16 binary keys for distinct and hash. Source operation semantics remain separate. Accent/kana/width folding without a faithful renderer is refused. Receipts carry the normalization and consumers recompute it from target semantics. No SQL padded equality is used for string distinctness. Synthetic compiled statements executed with ambient binary and case-insensitive collation both preserve two distinct strings under lakehouse semantics and collapse them to one under Warehouse semantics. Five control and seven observed-semantics tests passed. Full regression remains pending.

The Spark adapter builds one literal-only statement, with runtime version and session collation configuration, only behind explicit execution authorization. No identity is acquired or elevated by this producer. The human authorizes one Livy session/statement using existing investigator-code-reader Contributor scope; default clients cannot invoke it. [Microsoft's Livy route](https://learn.microsoft.com/en-us/fabric/data-engineering/get-started-api-livy-session) documents session creation, statements and deletion. Observations and any declared-default fallback remain pending; no outcome is claimed.

Next: one authorized application observation, one authorized Spark attempt, eight remaining verification pairs; seven earlier verified profiles remain preserved. No family resume until required bindings verify, and no15x2 gate or merge is claimed. Engine changes invalidate prior freezes.

## Live observations and corrections, 2026-10-05

Application control `round-six-g-application-20261006T005803` completed on ordersops as orderops_investigator, EngineEdition5/version12.0.2000.8, SQL_Latin1_General_CP1_CI_AS: case_fold=true, accent_fold=false, trim=true, kana=true, width=true. CI/AS names case-insensitive/accent-sensitive; absence of KS/WS accords with the observed kana/width equivalence. SQL padding, not the binary label, explains the observed trailing-space equality. Six physical requests, pot130->136, including separately recorded prewarm controls; one verification probe, zero investigation diagnostics. Original trim=false declaration conflicts and was refused. Dated configuration correction adopts the observed record; the old declaration/approval and original failure remain unchanged.

Spark session creation returned HTTP202 with GUID3a50005c-33a0-41d8-bc51-15ad7574e7a5. Local operator wrongly expected a numeric id and stopped; this own-code failure is preserved as round-six-g-spark-20261006T010032 (3physical, pot136->139). Corrected continuation used the SAME session, no replacement POST; exactly one statement completed and DELETE returned HTTP200. The continuation round-six-g-spark-continuation-20261006T010104 consumed6physical, pot139->145, no investigation diagnostics. Authenticated submitter is existing investigator-code-reader principal dc89155f-9a9a-4daa-9c20-7eff55818ccd, confirmed by token claims and session submitterId; engine current_user reports trusted-service-user, not the Entra principal. That is a runtime-identity limitation, not a matching principal attestation. No identity/scope/audience/grant changed. The human's narrow G execution decision supersedes the older code-only restriction for this one session only.

The Spark row reports case_fold=false, accent_fold=false, trim=false, kana=false, width=false; engine3.5.5 commit0677b6b57ece11fffdfa0353346b97d0cf6872fe, runtime spark.version3.5.5.5.4.20260807.1; objectwarehouse_bronze_e1b8e1. Session collation settings are empty. Resolution is OBSERVED_COMPARISON_PROBE, not a named observed BINARY collation. Only the exact original-landing layer adopts this observation; other layers retain their owner declarations. Five literals do not establish arbitrary Unicode equivalence or another object's observation.

The first full regression sweep ran2003 tests with2TAPE_UNCOMMITTED_ENGINE errors (started on uncommitted bytes) and1ADMISSION_CHANGED versus BUDGET_LIMIT failure in synthesis setup. All34 synthesis tests then passed. A complete committed-engine rerun is pending. Failures/logs retained locally. No8-binding rerun or family resume yet. New manifest approval pending; no15x2 claim.

## Eight remaining profiles, 2026-10-05

Run round-six-g-eight-bindings-20261006T010641 completed: landing->refined movement_id, warehouse_id, product_id, units, event_day, movement_type and refined->serving event_day, movement_type all VERIFIED. This is a bounded profile witness, not global equivalence; all comparisons remain SNAPSHOT_UNVERIFIED. Seven earlier numeric serving proofs remain unchanged, memoized under code hash313e90c9e25e1e1e844aac5383bfb3c01c4bd11684faeaabf48c207c623cf0c1. All needed-by bindings have witnesses now.

The pre-run estimate32 was low: actual42physical =16profile reads+3endpoint metadata+23SQL guard requests. Verification19/19; investigation0/12. Pot145->187/400,60reserved; rolling252/1500. No cap increased, no refunds/reset. Original tapes/proofs preserved. Sixteen statements first compiled offline with zero requests (round-six-g-eight-bindings-20261006T010617). The complete committed control/normalization engine passed2005 tests in373.956s.

Provisional runtime activation is explicit, requiring inference authorization, exact object/column/context and unchanged code hash. Original typed observations are revalidated; stale hashes, context/column changes, forged verdicts and later failed witnesses refuse. Cell-specific legacy proofs retain their previous scope checks. The investigation reads the original input, never the transformed verifier expression. The engine renders: lineage was verified on value, not on snapshot, and states that bounded agreement is not global equivalence. Code-source retrieval begins only after execution admission; its overhead is independently receipted. Six new activation tests pass; eleven planner projection goldens remain exact. Manifest context coverage test reports before/after2directory entries,1SQL entry,7563characters. No context coverage loss. Complete activation-engine regression and live family list remain pending.

## Resume approvals, 2026-10-05

DECIDED WITHOUT REVIEW under the authorized resume: the inferred manifest is hash908df87f1b066c11605b8381f3c7a5b3cdbd6482dde820f87c03bb3beed87f56; only authorized inference switches differ from the current observed-semantics manifest. The unchanged declared application-copy proof was consumer-revalidated and retained in a new immutable whole-manifest approval, without changing the original or claiming new currency. All15 bounded witnesses enter a new ledger; old ledgers remain untouched.

Whole-policy reapproval used exact retained metadata, zero cloud requests. Context8b6e9dfa-f209-4ca8-847b-dc07168e93fb, context hash5a771e9e60530cf261912d5ca31090c831e3b5a62de9ba893101043b2190f54e; pinned config hasha98dd72d3cc70972b0d82f2d686832a62d37f89ab7b45d810a232f20944ce414. Discovery creates new model-context identities even for unchanged source hashes. The runs retain the original explicitly approved fixture model contexts to which the proofs belong; their source hashes match the new projections. Proof context IDs are not relabelled. Current whole-policy approval still gates execution; this is retained-state approval, not a recollection or currency assertion.

## Resumed-list stop, 2026-10-05

The committed activation engine passed **2,011 regression tests** in348.267s. PowerShell reported exit1 for redirected ResourceWarnings; unittest itself reported OK, zero failures/errors.

Family A was attempted exactly once. Intake PROPOSED in one provider call; preview completed; create refused `Conflict: Dynamic context changed or disabled`. There was no session, no probe, no compared boundary, no investigation planner call, no judge, no synthesis and no narrative output. Pot187->187/400, reserve60; diagnostic0/12; guard0; rolling237/1500 after earlier charges expired naturally, not reset/refunded. The complete tape is sealed and validates.

Tape diagnosis: bootstrap pins841e425e-fe17-4bb0-9d06-b4623f49de5b, while OPERATION_START create carries preview contextd3b6e8e0-7911-4e62-b3f4-2d319c6ef131. The operator reassigned agent.store and runtime.store but omitted Workspace.store; preview therefore consulted the latest projection instead of the explicit retained pin. The gate correctly refused the mismatch. This is an operator integration failure, not evidence that provisional lineage succeeded or failed. A future correction must bind all three consumers to the same approved store; no context field may be hand-retargeted. No correction or replacement run was performed after the stop.

The original ledger row retained intake status PROPOSED despite the create error. An append-only dated correction records FAILED_BEFORE_EXECUTION; the original row, provider bodies, final tape and failure text remain untouched. The first changed result stops the entire list as instructed. No fixture mutation occurred, so no restoration was needed. No identity, permission, budget or expectation changed.

| Case | Current inferred column |
| --- | --- |
| family-A | FAILED_BEFORE_EXECUTION |
| family-B | NOT_ATTEMPTED_STOP_RULE |
| family-C | NOT_ATTEMPTED_STOP_RULE |
| family-D | NOT_ATTEMPTED_STOP_RULE |
| family-E | NOT_ATTEMPTED_STOP_RULE |
| family-F | NOT_ATTEMPTED_STOP_RULE |
| family-G | NOT_ATTEMPTED_STOP_RULE |
| family-H | NOT_ATTEMPTED_STOP_RULE |
| family-I | NOT_ATTEMPTED_STOP_RULE |
| reproduction-16 | NOT_ATTEMPTED_STOP_RULE |
| reproduction-empty | NOT_ATTEMPTED_STOP_RULE |
| source-consistent | NOT_ATTEMPTED_STOP_RULE |
| source-gap | NOT_ATTEMPTED_STOP_RULE |
| source-latency | NOT_ATTEMPTED_STOP_RULE |
| source-unreachable | NOT_ATTEMPTED_STOP_RULE |

The historical archived column remains separately earned15/15. The current inferred column is0/15 accepted,1failed attempt,14not attempted. **15x2 is not earned**; #410 stays draft/unmerged and no gate PR is promoted. Ordinary archived-tape CI cannot authorize that merge. Final round pot187/400 (340ordinary stop,60restoration reserve); rolling last read237/1500; investigation cap12 unchanged. No unfamiliar-domain acceptance claimed; prior freezes invalid.
