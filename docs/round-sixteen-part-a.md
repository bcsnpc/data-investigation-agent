# Round Sixteen Part A

Work in progress, 2026-10-12. The fixture readiness rebuild and billing binding work are still in progress; neither estate is claimed READY by this checkpoint. The Part A deadline is 07:50:24 UTC.

## Changes and evidence

The continuation controller now re-resolves retained targets against the current catalog, preserves old pins and evidence, and asks a visible-name question only when the target cannot be established. An actual user reply starts a fresh hybrid step phase; the prior phase is recorded. Wall-time and diagnostic limits remain cumulative.

Billing's approved connection User grant and seven table-level VIEW DEFINITION grants are recorded with before/after controls in [the grant record](round-sixteen-billing-grants.md). Native collection recovered seven source objects with 42 columns, seven Bronze tables with 42 columns, and 12 Warehouse tables with 54 columns. Operator definition evidence remains distinct from reader execution evidence. Exact metadata replay matched all 27 logical calls and 51 physical admissions without network or model calls.

The adapter retains no-mapping Copy activities as column-name mapping hypotheses, including explicit casts. Metadata visibility is not whole-schema visibility. Inferred mappings do not become verified bindings merely because both columns exist. See [the onboarding record](round-sixteen-billing-onboarding.md).

The later billing integration resolves nine Warehouse semantic partitions and seven embedded Copy links. It produces 35 unverified direct-column proposals; seven casts remain explicitly unsupported by the neutral contract. Full billing still depends on ordered procedure execution, DELETE/INSERT, views and UNION semantics. Partial verification would not close that dependency set, so no reads were spent on a misleading partial profile. The billing focused suite passed 117 tests.

For the fixture, static extraction successfully decoded all 17 notebook writers. The original quantity has a six-asset, six-declaration closure, including the auxiliary rates branch and two explicitly named Bronze ceilings. That exposes a genuine reader-evidence gap: the retained 15 verifications do not cover the Silver-to-Bronze rates step. The additional three-column verification is being prepared under the existing verification class; no fixture binding or data is changed. The native semantic-model/source boundary is declaration-backed, so its original query-bound receipts are being checked as declared-boundary evidence rather than relabelled as an inferred proposal.

## The single smoke batch

The batch window was 06:16:45 to 06:31:45 UTC. Three historical pre-reply catalogs were isolated, while all live accounting pointed at the original shared ledgers. Original tickets and tapes were unchanged. All three operations returned before the deadline, using zero physical requests and zero model calls; these were continuation-path checks, not successful investigations or accuracy scores.

| Saved continuation | Result | What it establishes |
|---|---|---|
| PIPELINE 037 | CLARIFYING, visual question | A business-question route refusal was incorrectly treated as a changed target. |
| PIPELINE 042 | CLARIFYING, visual question | Same route-refusal defect. |
| HYBRID 021 | HELD, AGENT_WALL_LIMIT | The reply received 12 fresh available steps, but its cumulative wall budget was already exhausted. No wall limit was raised. |

The route-refusal defect was fixed after the smoke and covered by an offline controller regression. A missing procedure now remains an explicit route refusal rather than generating a visual question. No replacement smoke was admitted; the original results remain the recorded results.

Before ticket admission, the three setups failed on a shared SQLite lock held by the metadata snapshot audit. A subsequent setup-only validation failed because the private helper expected an ID field inside the tape rather than validating its directory identity and sealed hash. Both errors and their corrections are preserved. They made no provider or estate requests and are not counted as ticket attempts. Future private metadata captures audit a consistent in-memory snapshot after releasing the shared source handle; a rejected snapshot is not written to disk.

## Accounting at the post-smoke checkpoint

Part A has charged 71 physical slots: 10 grant/resume controls, five authentication controls from the failed collection wrapper, and 51 metadata requests plus five authentication controls in the successful collection. Investigation diagnostics and model calls are both zero. Pot 2,712/4,000; reserve 95 untouched. Rolling usage was 685/3,000 at the captured checkpoint. Conservative model total remains $94.704272 against the $119.704272 policy ceiling, with the existing $10 margin retained.

The final readiness result, tests, replay housekeeping and Part A commit will be appended before the part closes. Draft #423 is not merged; the previous freeze is invalid.

## Additional offline review

The root's combined manifest, scoped-readiness, continuation and Copy/Warehouse regression run passed 101 tests. A separate transformation/verifier selection passed 42 tests; its tape test refused `TAPE_UNCOMMITTED_ENGINE` while source edits were in progress. That refusal is retained, and the tape check will be repeated after the source is committed. These counts overlap the agent's focused suites and are not added into a new unique-test total.

Recompilation also found that the current compiler types the Gold product identifier as a key, whereas its historical record has a numeric profile. The old record remains unchanged. The bounded A0 verification therefore plans four bindings: three rate columns and the key. Eight value probes and two target catalogs use 10 of the existing verification class's 11 slots; the investigation cap remains 12. The physical estimate is 27 SQL requests, bounded at 32, plus at most four separately recorded authentication controls. No new model call, identity, permission or fixture mutation is required.
