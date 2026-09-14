# Isolated defect lab, first scenario

This local DuckDB lab uses a small, coherent partial-return/paid/unpaid lifecycle
fixture and the repository's actual Gold order-line transformation SQL. It is separate
from Azure SQL, Fabric and the 100,000-order baseline. Install the existing
`scripts/requirements-fabric-tests.txt` dependencies if DuckDB is unavailable.

From the repository root:

```powershell
python scripts/defect_lab.py initialize
python scripts/defect_lab.py validate
python scripts/defect_lab.py inject
python scripts/defect_lab.py evidence
python scripts/defect_lab.py reset
```

The CLI operates only on `.local/defect-lab/lab.duckdb`. Initialization refuses an
existing file. Use one operator process per lab. Each mutation is transactional.
The lab records table/schema fingerprints, the Gold SQL hash and an action timeline.
READY means every business-table fingerprint and the current transformation match
the recorded baseline. Injecting while already changed is rejected.

Scenario `LAB-GOLD-OMIT-PARTIAL` removes the partially returned order's materialized
Gold row. Its source capture is USD 198 and refund USD 99, leaving USD 99 net cash.
The paid order contributes USD 55; the unpaid order contributes zero. Injection lowers
Gold from USD 154 to USD 55 while Silver remains USD 154. This is a controlled output
omission, not an injected transformation-code change or a claimed existing cloud bug.

Reset rebuilds Gold with the shared transformation and checks the original fingerprints
before committing. It rejects source or transformation drift. A failed reset rolls back.
Do not overwrite stored fingerprints to declare changed data healthy.

Evaluation expectations live separately in `infra/lab/evaluation_expected.json`; only
tests read them. The evidence projection exports business observations and excludes
lab control, events, scenario labels and expected answers. This is separation by tool
contract, not filesystem access control: a future investigator must receive only that
projection and must not get unrestricted evaluator files or the whole lab database.

Validation: six lab tests cover exact independent impact, full reset, repeated operations,
source/code drift, reset rollback and evidence projection. A local CLI cycle verified
READY → NOT_READY → READY and left the lab reset. No cloud credentials or writes are used.

Pending: wire the evidence projection to the investigator, add affected-record/impact
verification, establish a business-grounded no-defect case, and expand to other layers.
The three-row fixture is a deterministic lab seed, not a replacement for the 100K data
or evidence of complete defect-suite acceptance.
