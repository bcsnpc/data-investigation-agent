# Round Twenty: fresh cloud verification and family A input plan

Prepared offline 2026-10-21. No Azure, model, estate or permission operation was performed while preparing this plan.

The fixed `verification` runner handler accepts `options.inputs`. It invokes the existing retained-context preparation inside the selected runtime image, deriving a fresh approval from the explicit BUILD_PHASE manifest and current engine fingerprint. It then uses the existing selected-model compare-and-swap publication. Retained metadata is not recollected, and publication does not declare readiness. A concurrent catalog change refuses publication rather than replacing it.

The source is the complete preserved third-attempt catalog-after snapshot, whose selected-model revision is 83. Its canonical model body equals the last retained published model, SHA-256 `982019b45a48cbd45282bd218fbdca7716d5273b15564c6875f729589aaf7257`. The earlier input catalog has revision82 and is stale. This comparison is between saved evidence, not a new observation of the current PostgreSQL row; live normal CAS remains authoritative.

A fixed allowlist retains the verifier's programs, context, endpoints, model, SQLite baselines and journal through the existing platform snapshot CAS before any verification read. Completed/failure artifacts are retained again afterward, with one immutable per-file reference as each succeeds. A killed process therefore leaves the initial dependencies and completed native events in Blob. Unknown files or credential directories cannot enter this retention route. The runner never scans an arbitrary whole working directory for publication.

After the verification completes with its own `VERIFIED` result, `options.demo_ticket` starts the normal form path as a separately recorded step. The selected-model private catalog and inventory are copied from the just-prepared snapshots, so a separate stale private row cannot contradict the freshly published model. The fresh verification and family A share one job. The plan gives verification900seconds within the existing1800-second job. A refused/failed verification records why the demo was not admitted. Exact replay is a separate later command on the same image; no readiness builder or replay prerequisite is called by this route.

## Locally prepared input

- ZIP: `.local/round-twenty/part-c-inputs-01/inputs.zip`
- SHA-256: `a71a6444e2fe44c5ae7ae8557cc58c6c1ad3fbd4606a1fb67f48a46e705b7e85`
- Compressed:54,532,599bytes; expanded:482,966,499bytes.
- Per-member reconstruction sources and hashes: `input-receipt.json` beside the ZIP.
- Runner configuration: `runner-template.json` beside the ZIP.
- Intended existing-platform Blob: `captures/round-twenty/inputs/part-c-01.zip`.

The manifest and verification spec both declare BUILD_PHASE. Historical budget numbers remain informational. The form retains the same report/page/visual/comparison and wording; only its request key is fresh. Definitions, seeded data, scopes and the expected7,661?8,765 observation were not rewritten.

Root applies the current image digest and fresh platform-cost observation, uploads this ZIP using the existing platform authority, then uses the single launch command:

```powershell
python scripts/dia.py run family-a --estate .local/round-twenty/part-c-inputs-01/runner-template.json --runtime azure
```

No old inline launcher, exclusive writer lease, at-most-one-attempt condition, strict six-stage readiness gate or exact-replay-before-live gate is used. Source hashes, identity/read-only enforcement, monthly budgets, actual result validation and secret checks remain enforced.
