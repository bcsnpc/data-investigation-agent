# Federated SQL expected-principal wiring defect

Offline diagnosis of the preserved `cloud-stage-verify-01/output.zip`; no second live verification was admitted by this fix.

The capture remains FAILED. Capture SHA-256: `4bfd291c509bfca89872ea97076994b2f877035896993f9d75e8ab6dae896e73`.
It consumed four physical requests, one verification read and zero model calls. All four requests completed before target-catalog admission refused.

Tape event ordinal 59 is the successful SQL worker response: `read_only_verified=true`, database `warehouse_gold_e1b8e1`, engine `Microsoft Azure SQL Data Warehouse`. Its query-bound `surface_report.identity` is `531419ef-1610-415a-b8bf-01a4b6aad751@dff91047-ebc2-4657-8dbe-5af328d57780`. The configured federated SQL reader's `account` is the display label `dia-investigator-round19`. `binding_catalog.read_many` compared that label with the self-reported SQL principal, producing `ValueError: Target types lack reader-owned guarded surface evidence`.

The adapter now derives the expected SQL principal from the validated federated credential's exact client ID and tenant ID. User and legacy modes retain their declared account. This helper is shared by catalog and graph checks and SQL execution-surface declarations. The observed response is never rewritten. The display label, object ID alone, a different application's ID and a different tenant do not count as aliases. Missing principal configuration refuses. Engine, database and read-only permission evidence remain mandatory; existing token binding still validates tenant, object ID, client ID and audience.

This is a code correction, not evidence that a new live verification passed. Original captures, expected outcomes and approvals are unchanged. A future live verification requires current-code approval under the existing workflow.
