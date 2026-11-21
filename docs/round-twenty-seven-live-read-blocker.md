# Round 27 model-read diagnosis

Observed 2026-11-21 after the confirmed model-credit update. No identity, credential, connection or permission was changed.

The fresh fixture control verifies the original 360 business rows and schema hashes, and `SYSTEM_VERSIONED_TEMPORAL_TABLE`. Its Power BI measure read fails with HTTP400, `DatasetExecuteQueriesError`, Analysis Services code `3242524690`. No fresh model total is established.

Two additional bounded read-only probes on Application load fixture 20261003 give the same error: `EVALUATE ROW("probe", 1)` and the `[Movement Units]` measure. Therefore this is not demonstrated to be a misspelled measure or a numerical discrepancy. The generic response does not prove its underlying cause. Microsoft documents HTTP400 for ExecuteQueries query failures; it does not identify this numeric error code here. [Execute Queries documentation](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/execute-queries).

Read-only Azure application metadata confirms the existing investigator application `531419ef-1610-415a-b8bf-01a4b6aad751` has one client credential, `0b4b4562-5df3-44b1-98c4-6fb28e80df6e`, whose expiration is **2026-11-21T18:40:00.660887Z**. This is expired at the time of the failed probes. Earlier baseline checks passed before expiration. Expiration is established; causation of the generic DAX response remains to be verified after an authorized renewal.

The existing [owner action](owner-actions.md) requires an owner decision for another fixed-connection credential rotation. A scoped approval request is pending: rotate this same application's secret for 30 days, store it only in the existing Key Vault, and update only the existing fixture/billing connections, with no new identity or permissions. Never print the secret. Key Vault replacement alone does not update Fabric's encrypted connection credentials.

The proof input cohort is prepared but unadmitted. Do not score a failed baseline as an engine failure or claim a model value from the old receipt. Offline qualification and documentation continue while this decision is pending; no fixture has been injected in this continuation.

Private source/model checks: `.local/round-twenty-seven/admission/20261121-210841/`. The two follow-up responses are retained under `.local/round-twenty-seven/connection-diagnosis/`; no raw credentials are in these responses.
