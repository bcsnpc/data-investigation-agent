# Verified local Gold filter cause

The lab now has a transformation-build variant in addition to output deletion:

```powershell
python scripts/defect_lab.py inject-filter
python scripts/lab_investigator.py --verify-filter
python scripts/defect_lab.py reset
```

Start from READY. The variant builds Gold using the shared transformation wrapped by
an exclusion of PARTIALLY_RETURNED records. In the same transaction it records the
executed SQL and source/output fingerprints in a build receipt. Reset rebuilds the
baseline and removes this receipt.

The verifier requires a mismatch, exactly one receipt, an exact supported SQL definition,
unchanged source/output fingerprints, and current investigation observations. It replays
only repository-owned SQL, never arbitrary captured text. The filtered replay must equal
every current Gold row; the unfiltered calculation must reconcile with Silver by order
and currency. The receipt contains operational build evidence, not evaluator answers or
scenario labels. Inspection and replay use one local read transaction.

When these gates pass the finding is TECHNICAL_DEFECT, with a verified local filter cause,
affected records, exact impact and retained SQL/fingerprints. The original output-deletion
scenario has no build proof and remains UNRESOLVED. Missing, stale, changed or unsupported
proof never promotes the classification. Automatic bug routing remains disabled.

This is one explicitly supported local transformation, not general SQL root-cause
inference. Local receipt files are trusted operator-controlled provenance, not signed
third-party attestations. The finding does not prove a full-estate first divergence,
production behavior or real-world event validity. No cloud baseline is modified.

Validation: four new tests cover verified filter replay/reset, deletion without proof,
source/output/query drift and stale observations. Local run
3eaec492-8777-42fe-bce0-8ba468c75d63 verified one omitted order and USD 99 understatement;
reset returned READY. Next: bring the lab findings into the reviewed ticket/UI workflow
and expand cause/freshness coverage before enabling routing.
