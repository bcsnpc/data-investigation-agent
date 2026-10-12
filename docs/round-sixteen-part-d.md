# Round Sixteen Part D: readiness blocks scoring

2026-10-12. The first Part D action was the offline readiness gate. **Both fixture and billing are BLOCKED / NOT_SCORED.** No estate or model calls were made.

The current engine fingerprint is `b2a0fb2ee3a341eba6acfff1f4cbab4f125163268e1e3560da7a998258085065`. The fixture's retained Part A index is pinned to its earlier engine; billing has no complete published index. All six current stages therefore return `ONBOARDING_EVIDENCE_INDEX_MISSING_OR_STALE`. Exact inputs, hashes, pins and results are retained in [the readiness record](round-sixteen-readiness.json).

This is not merely an index refresh task. A separately labelled retrospective evaluation of the fixture's unchanged original index under its original pins still returns:

- `DISCOVERY_NOT_COMPLETE`;
- `BOUNDARY_CONSERVATION_FAILED`;
- `PROPOSED_BINDING_CONSERVATION_FAILED`;
- `VERIFIED_BINDING_CONSERVATION_FAILED`.

That retrospective check cannot authorize current scoring. Part A's six-stage READY certificate applied only to the named unfiltered Handled Quantity route, not to the application branch, record projections, page/filter questions or the proposed whole-estate scenario set. No old scope certificate was broadened.

Billing's new metadata context `e2c81334-17c6-474f-957b-53ff5bf1565b`, hash `1c07c0c75098efe5b2ede369cd92498b7c8160405a0c6991c81ef91e54139c56`, remains PARTIAL and unapproved. The configured older approved context used by the current gate is `01c29e37-914a-4ec5-9a1c-23d3de0bfb71`; it was not silently replaced by the newer partial scan. Exact native identities resolved nine Warehouse partition routes and seven Copy edges, but the 35 direct Copy proposals remain UNVERIFIED. Seven row-version casts are unsupported. Warehouse views, stored-procedure execution, ordered DELETE/INSERT and UNION semantics prevent a faithful complete chain. No reader-verification request or profile publication was spent on a subset that could not make the required billing scope ready. [Onboarding evidence](round-sixteen-billing-onboarding.md).

## Scoring disposition

| Estate | Readiness | New scenarios seeded | Tester tickets | Scored attempts | Correct resolutions / questions / harmful findings |
|---|---|---:|---:|---:|---|
| Fixture | BLOCKED |0|0|0|NOT_SCORED|
| Billing | BLOCKED |0|0|0|NOT_SCORED|

No expectations were authored, no independent tester was asked to generate a cohort, and no development/held-out split or eight-worker scored run occurred. Reporting zero harmful findings as a scored success would be false: there is no scored sample. The Part C typed smoke remains separate evidence.

The readiness precondition is binding. Neither old successful tickets nor the three new smoke observations bypass it. Part D ends at this gate rather than changing the scenario set or weakening the readiness definition to obtain a score. Existing estate data, original runs, sealed oracles and acceptance expectations remain unchanged. #423 stays draft; no merge. Freeze remains invalid.
