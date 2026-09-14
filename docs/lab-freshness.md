# Local Gold source-version lag

From a READY lab:

```powershell
python scripts/defect_lab.py inject-stale
python scripts/lab_investigator.py --verify-cause
python scripts/defect_lab.py reset
```

The fixture builds Gold using the unchanged shared transformation against a controlled
prior source view with no refund rows. Current Silver retains the refund. A transactional
receipt binds the supported prior-source contract, transformation hash and current
source/output fingerprints. This models a stale publication; it does not modify cloud
data or a scheduler.

The verifier requires current receipt/observation agreement, newer refund evidence,
exact reproduction of Gold from the prior source view, and reconciliation of the current
transformation replay with Silver. Only repository-owned queries execute. Missing proof
or drift stays UNRESOLVED. The existing filter-build verifier still reports
TECHNICAL_DEFECT for its distinct case.

For this fixture, Silver is USD 154 and Gold USD 253: one order is overstated by USD 99.
Classification is REFRESH_FRESHNESS, not a logic defect. The local review server supports
this through its existing approval/worker path. Reset restores all baseline fingerprints
and removes the source-version receipt. Routing remains disabled.

This is proof within one synthetic prior-source contract. It does not establish actual
cloud snapshot comparability, expected refresh frequency, lateness, elapsed lag or why
a real scheduler failed. Receipt provenance is local/operator-controlled. Those remain
separate live freshness requirements.

Validation includes classification/reset, distinction from filter defects, missing proof,
source/output/code drift and the reviewed API path. Local run
eb5ccabd-f6b5-43dc-86d7-a27bc93c367f returned REFRESH_FRESHNESS and the lab was reset READY.
