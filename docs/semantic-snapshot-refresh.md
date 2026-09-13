# Semantic refresh against registered Gold

`refresh_powerbi.py` resolves the configured Gold run through the SQLite publication registry, revalidates its hash and Silver/Bronze dependency evidence, and requires the current Gold receipt to match. It synchronizes SQL endpoint metadata and requests a transactional full semantic refresh. It no longer depends on the superseded separate dimension receipt.

After completion, one DAX query checks all six model tables for the expected Gold run, exact publication row counts and missing run markers. The current Gold receipt is checked again. The refresh response, query, observed rows and Gold reference are saved locally.

`validate_powerbi.py` consumes that refresh reference and reconciles fifteen business totals, order count, eight filter cases and a refund drillthrough case. A final marker/count query and Gold receipt check bracket the validation. Combined evidence is stored in SQLite `semantic_snapshot_verifications`, keyed by refresh ID with an evidence hash. A different verification cannot replace an existing record; use a new refresh for a new registered verification.

```powershell
python scripts/refresh_powerbi.py
python scripts/validate_powerbi.py
```

The resulting status is SEMANTIC_RUN_ALIGNED. It proves observed run/count alignment and the separately recorded metric checks. It does not expose or prove the Direct Lake engine's exact Delta version selection, prevent concurrent writers, or freeze future automatic framing. Therefore `snapshot_comparable` remains false. Missing or mixed markers fail; no technical defect is automatically classified. No report layouts or measure definitions are changed.

Four new tests cover aligned observations without overclaiming version proof, mixed/stale runs, null markers, wrong counts and missing dimension evidence. Existing model/report contract and generator tests remain required. Metadata recollection and lineage updates are a separate next step.

Live refresh `63e0ebc6-d4e3-4544-8e9b-92c07778819e` completed successfully against Gold run `e6559c75-d1ba-49bc-a87e-61cc47ecaf99`. All six model tables aligned: 365 dates, 20,000 customers, 150 products, 100,000 orders, 286,652 lines and 7,270 refunds. Fifteen totals, order count, eight filter cases and refund drillthrough passed. Combined evidence is stored in SQLite and `.local/semantic-snapshot-verified.json`. The status remains observed SEMANTIC_RUN_ALIGNED, with snapshot comparability false.
