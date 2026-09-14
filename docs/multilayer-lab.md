# Three-layer local boundary investigation

Run `python scripts/multilayer_lab.py` to create a fresh isolated scenario under
.local/multilayer-evaluations. The report and evidence.sqlite persist the observations;
lab.duckdb is reset after the scenario. --output must name a new directory.

The fixture copies the existing local baseline into Bronze-named tables before changing
Silver. These are test inputs, not a cloud ingestion implementation. The scenario increases
ORD-000002's captured amount and its corresponding line total/unit price by USD 10, then
rebuilds Gold using the repository's real Gold query. Gold uses funded line totals, so a
capture-only mutation would not model the intended propagated discrepancy.

Expected observations:

| Boundary | Upstream net cash | Downstream net cash | Result |
| --- | ---: | ---: | --- |
| Bronze to Silver | USD 154 | USD 164 | One order differs by USD 10 |
| Silver to Gold | USD 164 | USD 164 | Matching records |

The investigator captures all three projections in one local read transaction. It reconciles
keys and amounts at each adjacent boundary, including missing/extra records, and reports the
first observed local mismatch. Agreement between downstream layers does not hide an earlier
mismatch. A separate test verifies an isolated Gold omission is first observed at Silver/Gold.

Classification remains UNRESOLVED, root_cause_verified=false and automatic routing disabled.
Observed divergence does not prove which transformation or business event caused it. The
investigator reads only business projections, not injection labels or expected answers.
Evidence is retained in the existing investigation_runs format; this new result shape is not
yet integrated into the review UI, routing or the existing nine-case evaluation matrix.

Reset verifies the Bronze copy against its stored fingerprint, refuses changed Gold code,
restores Silver from Bronze and rebuilds Gold. Existing baseline fingerprints must match
before commit. The live baseline and prior isolated lab are untouched.

Tests cover matching layers, a propagated upstream discrepancy, a downstream omission,
missing/duplicate projection data and refusal to reset changed Bronze. Remaining work includes
actual ingestion/Silver transformation proof, report/model scenarios, cloud snapshot contracts,
and user-facing multi-layer evidence integration. Product acceptance remains incomplete.
