# HealthNet hospital estate — build result

Owner date2026-10-30 (America/Chicago); native verification continued2026-10-31UTC. Build and native checks are complete except the explicitly unimplemented incremental-refresh option below. Release is pending the final CI and merge record. No DIA investigation or generalisation score is claimed.

## What was built

Two AzureSQL sources, hn_clinical and hn_billing, feed32raw Lakehouse tables. Native DataflowGen2 maintains reference mappings, a notebook performs MPI preparation, and19Warehouse projections/stored procedures feed three models and three reports. Revenue and Productivity are Import; Operations is DirectLake. Models use fixed existing owner connections, dynamic RLS and Doctor cost/margin OLS. Reports contain36visual containers,2filtered bookmarks,1doctor drill-through and masked patient detail.

| Synthetic population | Rows / count |
|---|---:|
| Facilities / departments / beds |3 /33 /880|
| Providers |360 (300physicians,60APC)|
| Patients |60000|
| Encounters |250000|
| Order lines |1500000|
| Results |2774006|
| Charges |505322|
| Claims / claim lines |289614 /579228|
| Payments / adjustments |256716 /268700|

Seed20261030 covers2025-10-01 through2026-10-29 (394days). Every person, facility, identifier and row is synthetic. Licensed CPT/CARC/NUBC content was not copied; synthetic alternatives and the small public diagnosis subset are documented in [realism and licensing](hospital-estate-realism.md).

## Realism checks

These are measured synthetic distributions, not clinical claims. Full target/actual tables and denominators are in the realism document.

| Metric | Target / assumption | Actual |
|---|---|---:|
| ED door-to-provider median |25minutes|25minutes|
| Nonadmitted ED LOS median |180minutes, censored at source end|179minutes|
| ED admission fraction |11.5%|11.467%|
| Readmission fraction |12%attempt; eligible preceding discharge required|11.790%|
| Orders per encounter |6|6|
| LAB / imaging / pharmacy mix |75% /12% /13%|75.040% /12.009% /12.950%|
| Initial adjudicated denial rate |12%assigned|12.067%|
| Final adjudicated denial rate |measured, not forced equal to initial|2.858%|
| Facility occupancy |measured; no forced target|68.218% /67.902% /68.863%|

Arrival weights were applied in UTC; ED display timestamps convert to America/Chicago. Account cash and claim adjudication are separate synthetic processes. No national productivity, clinical calibration or risk-adjustment claim is made.

## Reconciliation and reset

- All32native source row counts/canonical hashes match the generated sources; all13source invariant checks pass.
- All32raw row counts match source. All32same-run audit rows match Copy activity rowsRead/rowsCopied, with no recount replacing accounting.
- All19native Warehouse mart counts match independent local projections. Native finance conserves exactly:193599565928gross cents -112293602454adjustment cents -74799888773cash cents =6506074701balance cents.
- Native retained encounters249575, distinct MPI patients57764 and latest census565 agree with independent local checks. MPI retains60000rows/59400survivors; reference outputs14payer-history and396department-mapping rows.
- Full nightly integration40cd9dbc-ced8-4bee-985f-6c91e474a89e Completed; notebook,Dataflow and Warehouse activities all Succeeded. All three final model refreshes Completed.
- A second full seed rebuild matches all32source hashes,19local mart hashes and28independent baseline query results. Reset command: `python -m fixtures.hospital --output <new-directory> --seed 20261030`.

This is not a claim of full native row-content hashing at every downstream boundary. Native raw/mart counts, source hashes, finance and model/report values are distinct checks.

## Baselines and security

[Baseline record](hospital-estate-baseline.md) contains all64default/bookmark contexts:58native model queries and6static text contexts. Large tables use deterministic100-row windows with full cardinality; hashes label the returned window, not the full population. The final masked-name detail window was re-read separately. Native report rendering, bookmark activation and drill-through were also observed.

| Owner single-role simulation | Revenue visible charge rows | Productivity visible encounters | Operations visible encounters |
|---|---:|---:|---:|
| Executive |505322|249575|249575|
| HospitalManager |258476|127666|127666|
| DepartmentHead |39458|19475|19475|
| Doctor |0|3031|0(native COUNTROWSBlank)|

All12match independent slices. Native role membership lists remain0; existing owneradmin@skynwhy.com is represented in the mapping table and simulated through Test as role. No other user's authentication was impersonated or asserted. DepartmentHead's facility-only aggregates are denied. Doctor's combined cost/margin query is denied at synthetic_margin_cents; the identical query serves under Executive. This is one combined denial probe plus positive control, not two individual column probes. Temporary report-page restore matched original definition SHA-256a4c94e30d9527a3acf99f7a0b1dfb298ce91338d635367b157dc0fac811f3b31.

Commercial bookmark:Gross438933821.15 /113978charge rows. NorthEDbookmark:HealthNetNorth +ED, census294 /occupancy68.22%. Named-doctor drill-through preserves doctor10/NorthMedicine and1335visits. Masked patient names and MRNs are displayed. The A/R measure's per-context latest snapshot can retain an older aging bucket; its exact43654.18difference from a fixed-global-date query is documented rather than forced equal.

## Schedule, cost and limits

DailyUTCpipelines, read back enabled, beginNov1:clinical02:00,billing02:40,nightly03:30. Import refreshes are Revenue04:30 and Productivity05:00. Full refresh completed at this size. **Incremental model refresh is not enabled:** a rolling date window would age the fixed historical fixture out over time; this optional item remains unimplemented and is not described as a platform limitation.

Both SQL databases retain free-offer-only operation, mandatory pause at the free limit and60-minute inactivity auto-pause. Current OneLake files total805190370bytes (~0.8GB), illustrative ~$0.02/month at$0.023/GB-month. A20GBretention allowance would be$0.46/month, inside the approved$1incremental storage bound. These are estimates, not invoice measurements. Existing FTL4capacity is unchanged;9trial days remain at observation. Owner must decide future capacity if continued availability is needed; no paid fallback was provisioned. No new cost approval is pending for the built scope.

## Validation and remaining boundary

31focused generator tests pass. Native runtime verification found and fixed upsert key placement, audit conflicts, unsupported Warehouse SET, timestamp types, duplicate visual references and unapplied byName bookmarks; failed attempts remain recorded in the design history. Final CI/merge status is recorded below.

No engine files changed, no model API spend was used, and no hospital ticket, DIA scan or investigation ran. Future reader/scanner grants are documented in owner-actions.md and remain unapplied. XMLA/modern role-query client failures are retained; native owner Test as role supplied the security checks. Round25 remains paused untilNovember1UTC as instructed; this build does not spend its model budget.
