# HealthNet hospital estate — build result

Owner date: 2026-10-30 (America/Chicago). Native verification continued on October 31 UTC. The estate is deployed and its native checks are recorded below. Incremental model refresh remains unimplemented; daily full refresh is used instead. Release awaits the final CI and merge record.

## What was built

Two Azure SQL sources, `hn_clinical` and `hn_billing`, feed 32 raw Lakehouse tables. A Dataflow Gen2 maintains reference mappings, a notebook prepares patient identity matches, and 19 Warehouse projections and stored procedures feed three models and three reports. Revenue and Productivity use Import; Operations uses Direct Lake. Existing owner connections supply the data. Models define dynamic row security and Doctor restrictions on cost and margin columns.

The reports contain 36 visual containers, two filtered bookmarks, a doctor drill-through and masked patient detail.

| Synthetic population | Rows or count |
|---|---:|
| Facilities / departments / beds | 3 / 33 / 880 |
| Providers | 360: 300 physicians and 60 APCs |
| Patients | 60,000 |
| Encounters | 250,000 |
| Order lines | 1,500,000 |
| Results | 2,774,006 |
| Charges | 505,322 |
| Claims / claim lines | 289,614 / 579,228 |
| Payments / adjustments | 256,716 / 268,700 |

Seed `20261030` covers October 1, 2025 through October 29, 2026: 394 days. Every person, facility, identifier and row is synthetic. Licensed CPT, CARC and NUBC content was not copied. Synthetic alternatives and the small public diagnosis subset are documented in [realism and licensing](hospital-estate-realism.md).

## Realism checks

These are measured synthetic distributions, not clinical claims. The realism document contains the full target/actual tables and denominators.

| Metric | Target or assumption | Actual |
|---|---|---:|
| ED door-to-provider median | 25 minutes | 25 minutes |
| Nonadmitted ED LOS median | 180 minutes, censored at source end | 179 minutes |
| ED admission fraction | 11.5% | 11.467% |
| Readmission fraction | 12% attempted; eligible preceding discharge required | 11.790% |
| Orders per encounter | 6 | 6 |
| LAB / imaging / pharmacy mix | 75% / 12% / 13% | 75.040% / 12.009% / 12.950% |
| Initial adjudicated denial rate | 12% assigned | 12.067% |
| Final adjudicated denial rate | Measured; not forced equal to initial | 2.858% |
| Facility occupancy | Measured; no forced target | 68.218% / 67.902% / 68.863% |

Arrival weights apply in UTC; ED display timestamps convert to America/Chicago. Account cash and claim adjudication are separate synthetic processes. No national productivity, clinical calibration or risk-adjustment claim is made.

## Reconciliation and reset

- All 32 native source row counts and canonical hashes match the generated sources. All 13 source invariant checks pass.
- All 32 raw row counts match source. All 32 audit rows for the successful runs match the Copy activity's `rowsRead` and `rowsCopied`; recounts did not replace activity accounting.
- All 19 native Warehouse mart counts match independent local projections. Native finance conserves exactly: 193,599,565,928 gross cents - 112,293,602,454 adjustment cents - 74,799,888,773 cash cents = 6,506,074,701 balance cents.
- Native retained encounters (249,575), distinct MPI patients (57,764) and latest census (565) agree with independent local checks. MPI retains 60,000 rows and 59,400 survivors. Reference outputs contain 14 payer-history and 396 department-mapping rows.
- Nightly integration run `40cd9dbc-ced8-4bee-985f-6c91e474a89e` completed. Notebook, Dataflow and Warehouse activities succeeded. All three final model refreshes completed.
- A second full seed rebuild matches all 32 source hashes, 19 local mart hashes and 28 independent baseline query results. Reset command: `python -m fixtures.hospital --output <new-directory> --seed 20261030`.

This does not claim full native row-content hashing at every downstream boundary. Raw and mart counts, source hashes, finance and model/report values are separate checks.

## Baselines and security

The [baseline record](hospital-estate-baseline.md) contains all 64 default/bookmark contexts: 58 native model queries and six static text contexts. Large tables use deterministic 100-row windows with full cardinality. Hashes identify the returned window, not the full population. The final masked-name detail window was read separately. Report rendering, bookmark activation and drill-through were also observed in the browser.

| Single role simulated by owner | Revenue charge rows | Productivity encounters | Operations encounters |
|---|---:|---:|---:|
| Executive | 505,322 | 249,575 | 249,575 |
| HospitalManager | 258,476 | 127,666 | 127,666 |
| DepartmentHead | 39,458 | 19,475 | 19,475 |
| Doctor | 0 | 3,031 | 0; native COUNTROWS returns Blank |

All 12 agree with independent slices. Native role membership lists remain empty. Existing owner `admin@skynwhy.com` is represented in the mapping table and simulated through Test as role. Another user's authentication was not tested. DepartmentHead cannot see facility-only aggregates.

Doctor's combined cost/margin query is denied at `synthetic_margin_cents`; the identical query serves under Executive. This is one combined denial probe and a positive control, not two individual column probes. The temporary test page was removed. Original and restored definition SHA-256 both equal `a4c94e30d9527a3acf99f7a0b1dfb298ce91338d635367b157dc0fac811f3b31`.

The Commercial bookmark gives Gross Charges 438,933,821.15 and 113,978 charge rows. North ED sets HealthNet North and ED, giving census 294 and occupancy 68.22%. Doctor drill-through preserves doctor 10, North Medicine and 1,335 visits. Patient names and MRNs are masked.

The A/R measure selects the latest snapshot within each context. Its aging visual therefore retains an older bucket worth 43,654.18 that a fixed-global-date query excludes. This definition difference is documented rather than forced equal.

## Schedule, cost and remaining limits

Daily UTC pipeline schedules begin November 1: clinical 02:00, billing 02:40 and nightly 03:30. Import refreshes are Revenue 04:30 and Productivity 05:00. All schedules were read back enabled. The generated requirements retain a false native-verification flag because generation alone never proves deployment; the native results above are recorded separately.

**Incremental model refresh is not enabled.** A rolling date window would age rows out of this fixed historical fixture as time passes. Daily full refresh preserves stable reset and reconciliation across models, and completed at the current size. This optional item remains unimplemented; it is not described as a platform limitation.

Both SQL databases retain free-offer-only operation, mandatory pause at the free limit and a 60-minute inactivity pause. OneLake files currently total 805,190,370 bytes, about 0.8 GB: roughly $0.02/month at the illustrative $0.023/GB-month rate. A 20 GB retention allowance would cost $0.46/month, within the approved $1 incremental storage bound. These estimates are not invoice measurements.

The existing FTL4 capacity is unchanged and had nine trial days left at observation. The owner must choose future capacity if continued availability is needed. No paid fallback was provisioned. No new cost approval is pending for the built scope.

## Validation and release boundary

All 31 focused generator tests pass. Native verification found and fixed upsert key placement, audit conflicts, an unsupported Warehouse SET statement, timestamp types, duplicate visual references and bookmarks that did not apply. Failed attempts remain in the design history. Final CI and merge status are recorded below.

No engine files changed. No model API money was spent. No hospital ticket, DIA scan or investigation ran. Future reader/scanner grants are documented in `owner-actions.md` and remain unapplied. XMLA and modern role-query client failures are retained; the native owner Test as role feature supplied the security results.

Round 25 remains paused until November 1 UTC, as instructed. This build did not spend its model budget.
