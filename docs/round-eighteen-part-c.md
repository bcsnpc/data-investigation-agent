# Round Eighteen ? Part C

Checkpoint 2026-10-13 04:50 UTC. Draft #424; neither PR merges.

The approved platform is deployed through parameterized Bicep and a code-only GHCR image. PostgreSQL and Container Apps are in South Central US; storage, Key Vault and the worker identity remain East US. The worker uses managed identity for platform state/Blob/Key Vault, and the explicitly approved existing delegated reader for the cross-tenant test estate. It never substitutes the Contributor code reader for quantity reads.

Eight historical tapes were replayed as parallel Container Apps jobs. The initial cohort was **7/8**, about68seconds from first start to last finish, versus **8/8 in198.253seconds** locally. Retained diagnostics found Linux mishandling absolute Windows configuration paths. Corrected shard4 `job-dia-worker-mftupru` passed1/1 in55seconds. All eight now have passing cloud receipts, but this is not a single all-green parallel timing result and no speedup is claimed. Offline child network, estate and model counts are zero; platform artifact controls are separate.

The approved reader's Power BI and SQL authentication worked in the cloud with the same tenant/object/audiences. Fresh context preparation conserved825 discovered asset IDs/content hashes. Its reviewed hash was required before a compare-and-swap publication of one model, preserving old context history.

The first live verification, `job-dia-worker-974nsjk`, completed18/18 witnesses using40/40 verification probes and89 physical requests, all settled. The native boundary also agreed on distinct surfaces. Connection remains unattested and every comparison remains SNAPSHOT_UNVERIFIED. No diagnostic investigation or model call occurred. This is bounded reader verification, not the requested7,661-to-8,765 demo finding.

Its exact replay failed: the shared PostgreSQL reservation implementation uses a different clock sequence from the legacy SQLite implementation selected by replay. A later finalization error masked that first cause. Both original errors and the immutable tape remain. The correction versions the budget implementation at capture and re-executes that algorithm against an in-memory repository during replay. It does not copy admission answers or relax comparisons. First-error propagation also prevents a second FINAL mismatch from replacing a failed replay. New engine bytes require fresh approval and verification; the old proof is not transferred.

Retained-control preflight remains fixture8 PASS/0 FAIL/24 MISSING and billing8 PASS/0 FAIL/13 MISSING; neither establishes whole-estate readiness. The requested one cloud demo is still unadmitted at this checkpoint. Its outcome and final replay status will be appended below.

At04:39:32 UTC: new physical requests89; new model spend$0; pot2,928/4,000, rolling287/3,000, restoration95remaining. No limit or estate permission changed during these checks. The full frozen334c3ac regression passed4,047 tests; the newer shared-budget correction passed39 focused tests with26 inherited opt-in backend tests skipped and4 subtests. Full60c741a regression is pending. The earlier freeze is invalid.


## Part C close, 2026-10-13 05:30 UTC

Verify02 `job-dia-worker-ybvd8u6` ran05:08:29--05:24:53 UTC (984seconds). Live verification again completed18/18 witnesses,40/40 probes and89 physical requests, all settled, with zero investigation diagnostics/model calls. Its immutable tape SHA256 is `c6cad49ae8ab08f066157e3c349513daa5e5857a426c40db74abad6fc0d3998d`. Output ZIP301,321,267 bytes, SHA256 `30edf2399ce391b608f6ffaa8e61e5d5376fc665b8c4f4fc9018cdffc5c55243`, was read back and retained. Native-route limits remain unchanged.

Exact replay failed `TapeError: TAPE_EVENT_DIFFERS:BUDGET_INPUT:WORKER_READ`. Readiness was not published; the one family A cloud demo was NOT_RUN. The first mismatching request is now identified: live gateway normalization adds `require_read_only:true` to SQL worker payloads, while replay skips that live-only gateway branch and omits the field. A later wait/finalization masks the initial byte mismatch. This is a producer/replay payload asymmetry; it establishes neither a wrong value nor a successful replay. Offline correction is underway; neither original tape is amended or relabelled. No third verification/live attempt is admitted in this part.

Full corrected enginee646f7e:4,057 PASS,46 skipped,1,416 subtests in464.88seconds. Later native-pointer export correction has19 focused tests: new capture pointers are copied byte-identically under the stage output, missing/unsealed/unpublished captures listed explicitly, and primary failures retained. No database copy or estate/model request is added. It does not retroactively change either executed image.

Closing read-only repeatable-read PostgreSQL report at05:29:12 UTC:10,200 usage rows, two new sessions of89 SETTLED requests each, shared model opening/charge107,957,725 microdollars with no new monetary reservations. New model spend$0; pot3,017/4,000, restoration95 remaining, rolling376/3,000. The ordinary SharedState status helper stalled and was stopped as a read-only control; the direct consistent SELECT report made no mutations and avoids that advisory-lock path. The earlier connection-loss receipt is retained. All new verification reservations are settled. Part D documentation/audit continues offline.
