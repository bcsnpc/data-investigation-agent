# Reviewed publication scope

The ten publisher/verifier gaps were caused by generic static analysis, rather than an unknown table-writing capability in the reviewed code. A narrow parser contract now proves their finite table scope without executing the notebooks or claiming which historical branch ran.

The contract accepts two exact normalized AST hashes: the current verifier body and the initial publisher body. Review confirmed their only difference is the informational `mode` field in the receipt. All five leading parameters must be literal, correctly typed values. The snapshot UUID, manifest hash, workspace, lakehouse and complete ten-table mapping must agree with the verified publication evidence. All mappings must share a Bronze proof hash. Modified code, extra statements, changed paths, missing mappings or unresolved parameters reject the contract and retain normal parser gaps.

For this code, the publisher's only possible Delta writes are the ten deterministic `Tables/snapshot_<id>/<table>` paths; the existing-receipt branch performs no table writes. Verification mode performs no table writes. Other conditional branches validate types, nullability, receipts and local/file operations. These do not introduce additional table destinations. The source manifest is hash-bound by the verified publication mappings.

The graph records ten `RESOLVED_BY_REVIEWED_CONTRACT` entries, each retaining the original notebook/line/reason, captured definition hash, reviewed AST hash and source/proof references. They are persisted with the lineage build and restored when loaded. Publisher `produces` links and non-data `verification_input` links record the finite scope. Historical blocked graphs are preserved. No caller-provided resolved flag is accepted by the eligibility gate.

Build `549f1a33-5b04-40c3-8b64-718d507e480c` uses metadata scan `4f443959-2657-4ca3-911a-0627441fa25f`: 403 links, zero remaining parser gaps, ten retained resolution records and 41 lineage-eligible data-bound visuals. The audit status is SUPPORTED_PATHS_RESOLVED. This is completeness within supported captured dependencies, not exhaustive runtime or column lineage. The earlier graph remains blocked under its original evidence.

Six new tests cover publisher/verifier modes, exact table scope, code changes, parameter changes, missing/duplicate mappings, wrong paths/proofs, preserved resolution records and automatic re-blocking. Existing lineage, gap-policy, audit and generator tests also pass. No cloud data or notebook definitions changed.

Model snapshot comparability remains false and automatic defect routing remains disabled. Investigation consumers must select this explicit build and still enforce metric, filter, currency and snapshot compatibility. Changes to the reviewed publisher require a new review and fingerprint; this is not general Python interpretation.
