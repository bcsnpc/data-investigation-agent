# HealthNet realism and licensing

All rows, people, staff, identifiers, facilities, addresses and payer names are synthetic. Seed 20261030 fixes the source population. Benchmarks guide distributions; they are not copied patient records. The generation period is 2025-10-01 through 2026-10-29 (394 days), allowing a partial October-to-October comparison. It does not establish two complete calendar years.

| Distribution | Generator target / range | Basis |
|---|---|---|
| Completed inpatient length of stay | service means Medicine 6.3, Cardiology 5.0, Orthopedics 3.6, Surgery 4.7, Obstetrics 2.4, Pediatrics 2.8, ICU 8.0 days; gamma shape 2, 0.5?45 days | Assumptions; context: Medicare FFS mean 5.6 days in 2022 ([MedPAC](https://www.medpac.gov/wp-content/uploads/2024/07/July2024_MedPAC_DataBook_SEC-1.pdf)); not an all-payer population estimate |
| Occupancy | 880 beds (450/280/150); no overlapping assignments; report measured occupancy rather than force a target | Fictional capacity assumption; [AHA hospital context](https://www.aha.org/statistics/fast-facts-us-hospitals) |
| Season / weekday | winter arrival weight 1.14; weekend 0.92 | Explicit assumptions |
| ED arrival hour | overnight 0.35; morning 0.8; daytime/evening 1.35; late evening 0.7 | Explicit assumptions, weighted per hour |
| ED door to provider | lognormal median 25 minutes, sigma 0.8; missing for LWBS | Assumption; CDC reports 40.6% seen within 15 minutes, so this synthetic wait profile is intentionally slower ([CDC](https://www.cdc.gov/nchs/fastats/emergency-department.htm)) |
| ED length of stay | nonadmitted lognormal median 180 minutes, sigma 0.55, 25?1500 min; admitted includes actual bed wait | Assumption; ED boarding is not forced into the nonadmitted distribution |
| LWBS | 2.5% of nonadmitted ED arrivals, not all arrivals | Assumption; actual denominator reported |
| ED admissions | 11.5% | CDC 2022 all-ED context, same public source above |
| Readmissions | 12% attempt among new IP admissions; only actual preceding same-service discharges qualify within 30 days | Assumption; actual eligible rate can be lower; not a CMS risk-adjusted metric |
| Transfers | 2.4% attempted ED interfacility, requiring a real preceding different-facility discharge within one day | CDC transfer context; actual linked transfer rate may be lower |
| Orders / encounter | 6 at full size, LAB75% / imaging12% / pharmacy13% | Assumptions |
| Turnaround | median LAB55, imaging90, pharmacy35 minutes; lognormal sigma0.5; STAT half routine | Assumptions, completed only |
| Cancel / void / unfinished | 4% cancel, 1.5% void, 2% in-progress/ordered, plus explicit reentries | Assumptions |
| STAT | 40% for ED; 12% other encounters | Assumptions |
| Charges | lognormal IP median $28,000; other encounters $1,800; two component charges, occasional zero/bundle | Fictional gross charges, not payment or cost benchmarks |
| Payer mix | Medicare37%, Medicaid24%, commercial31%, self-pay8%, before reference remapping | Assumptions; remapped plans alter historical/current-reference groupings |
| Initial denial | 12% assigned; report adjudicated claims only, unresolved final subset | Assumption near 11.81% cited in [HFMA chapter February2026](https://www.hfma.org/wp-content/uploads/2026/02/february2026-speaksnewsletter-firstillinois.pdf); not an HFMA national causal standard |
| Denial categories | seven synthetic categories, approximately balanced by account index | Assumption; no X12 CARC copied |
| Days to bill / pay | generated service-to-bill delay; payment 14?39 days after bill; late charges4?34 days; disclose right censoring | Assumptions; compare measured outputs, not asserted benchmarks |
| A/R | exact posted charges + signed adjustments ? signed payments, daily aging by facility/payer | Definition choice aligned with [HFMA MAP definitions](https://www.hfma.org/data-and-insights/map-initiative/map-keys/); no target fabricated |
| Adjustments / writeoff | total58% gross: usually contractual; qualifying older accounts split10% gross to bad debt at90days; small charity offsets refunds | Assumptions; not cost accounting |
| Late charges | 5% selected, capped at source as-of date | Assumption; distinguish late and cross-month counts |
| Providers | 300 physicians +60 APC; 25% at0.5FTE; specialty-linked attendance; 36 transfers April16 | Assumptions; actual daily visits and workload reported, not national productivity norms |
| Procedure workload | uniform2?12 fictional workload units; never described as licensed RVU | Assumption |

## Code sets

- ICD-10-CM: four diagnosis identifiers (I10, E11.9, J18.9, R10.9), with our own generic descriptions. ICD-10-PCS: 0WQF0ZZ, documented in the [CMS public v38 code reference](https://www.cms.gov/icd10m/version38-fullcode-cms/fullcode_cms/P0764.html). This is a pinned demonstration subset, not a claim of current-year coding compliance. [ONC identifies ICD-10-CM/PCS as publicly available without a license](https://healthit.gov/resources/cartos-oncs-terminology-service/); [CMS code hub](https://www.cms.gov/medicare/coding-billing/icd-10-codes).
- CPT is licensed by AMA ([license FAQ](https://www.ama-assn.org/practice-management/cpt/cpt-licensing-frequently-asked-questions-faqs)); use PRC synthetic identifiers only. No CPT descriptors.
- NUBC is licensed ([NUBC licensing](https://www.nubc.org/license)); use synthetic revenue centre identifiers only.
- CARC/RARC: use DN-SYN and SYN-RMK identifiers/categories only; no redistribution of [X12 code lists](https://x12.org/codes).
- Drug identifiers SYN-DRUG, DRGs SYN-DRG and workload weights are synthetic. No HCPCS/CDT, real MS-DRG weights or RxNorm release imported. [RxNorm terms](https://www.nlm.nih.gov/research/umls/rxnorm/docs/termsofservice.html) distinguish public NLM normalized content from proprietary source vocabularies; avoid that ambiguity entirely here.

Actual distributions and checks are emitted in verification.json for each generated volume. A tiny test sample proves invariants, not population-rate conformance. Native source/raw/model/report reconciliation remains a separate requirement.


## Full-population measurements, seed 20261030

All actuals below are measured from the seeded local source tables and independent local marts. They do not establish native report values. The original targets above remain assumptions; neither the generator nor the targets were retuned to these measurements.

| Metric | Target / definition | Measured actual |
|---|---|---|
| ED door-to-provider median | 25 minutes, nonblank ED visits | 25 |
| Nonadmitted ED LOS median | 180 minutes before source-end censoring | 179 |
| Completed Cardiology ALOS | service-specific mean above; only completed admissions | 4.941 days |
| Completed ICU ALOS | service-specific mean above; only completed admissions | 8.077 days |
| Completed Medicine ALOS | service-specific mean above; only completed admissions | 6.229 days |
| Completed Obstetrics ALOS | service-specific mean above; only completed admissions | 2.335 days |
| Completed Orthopedics ALOS | service-specific mean above; only completed admissions | 3.553 days |
| Completed Pediatrics ALOS | service-specific mean above; only completed admissions | 2.849 days |
| Completed Surgery ALOS | service-specific mean above; only completed admissions | 4.671 days |
| Original Commercial payer mix | before mid-year remapping | 77,464 / 250,000 (30.986%) |
| Original Medicaid payer mix | before mid-year remapping | 60,096 / 250,000 (24.038%) |
| Original Medicare payer mix | before mid-year remapping | 92,440 / 250,000 (36.976%) |
| Original SelfPay payer mix | before mid-year remapping | 20,000 / 250,000 (8.000%) |
| AdvancedPractice staffing | 300 physicians / 60 APC; 25% half-time overall | 60 people, 52.5 FTE |
| Physician staffing | 300 physicians / 60 APC; 25% half-time overall | 300 people, 262.5 FTE |
| IMAGING order mix | LAB75%, imaging12%, pharmacy13% | 180,142 (12.009%) |
| LAB order mix | LAB75%, imaging12%, pharmacy13% | 1,125,607 (75.040%) |
| PHARMACY order mix | LAB75%, imaging12%, pharmacy13% | 194,251 (12.950%) |
| CANCELLED final order status | includes explicit void/reentry changes | 59,994 |
| IN_PROGRESS final order status | includes explicit void/reentry changes | 22,409 |
| ORDERED final order status | includes explicit void/reentry changes | 7,513 |
| RESULTED final order status | includes explicit void/reentry changes | 1,382,383 |
| VOIDED final order status | includes explicit void/reentry changes | 27,701 |
| IMAGING ROUTINE turnaround | routine medians55/90/35; STAT half; resulted only | 90.000 minutes |
| IMAGING STAT turnaround | routine medians55/90/35; STAT half; resulted only | 45.000 minutes |
| LAB ROUTINE turnaround | routine medians55/90/35; STAT half; resulted only | 55.000 minutes |
| LAB STAT turnaround | routine medians55/90/35; STAT half; resulted only | 27.500 minutes |
| PHARMACY ROUTINE turnaround | routine medians55/90/35; STAT half; resulted only | 35.000 minutes |
| PHARMACY STAT turnaround | routine medians55/90/35; STAT half; resulted only | 17.500 minutes |
| Facility 1 occupancy | measured, no forced occupancy target | 68.218% |
| Facility 2 occupancy | measured, no forced occupancy target | 67.902% |
| Facility 3 occupancy | measured, no forced occupancy target | 68.863% |
| Original service-to-bill mean | service-to-post plus1-5 days; right-censored | 5.314 days |
| Original-bill-to-cash mean | 14-39 days before date rounding / censoring | 24.591 days |
| ed_admission_fraction | denominator in verification SQL | 0.114667 |
| ed_lwbs_fraction | denominator in verification SQL | 0.022113 |
| ed_transfer_fraction | denominator in verification SQL | 0.023248 |
| inpatient_completed_alos_days | denominator in verification SQL | 5.054303 |
| readmission_fraction_admissions | denominator in verification SQL | 0.117896 |
| orders_per_encounter | denominator in verification SQL | 6.000000 |
| stat_fraction | denominator in verification SQL | 0.237713 |
| cancellation_fraction | denominator in verification SQL | 0.039996 |
| initial_adjudicated_denial_fraction | denominator in verification SQL | 0.120667 |
| final_adjudicated_denial_fraction | denominator in verification SQL | 0.028582 |
| part_time_provider_fraction | denominator in verification SQL | 0.250000 |
| Initial denial: authorization | original remittance lines; synthetic codes | 7,906 lines; 1,267,019,110 cents denied |
| Initial denial: coding | original remittance lines; synthetic codes | 7,820 lines; 1,345,897,282 cents denied |
| Initial denial: duplicate | original remittance lines; synthetic codes | 8,162 lines; 1,373,186,902 cents denied |
| Initial denial: eligibility | original remittance lines; synthetic codes | 7,804 lines; 1,338,992,515 cents denied |
| Initial denial: medical necessity | original remittance lines; synthetic codes | 7,830 lines; 1,272,482,323 cents denied |
| Initial denial: missing information | original remittance lines; synthetic codes | 8,116 lines; 1,383,918,126 cents denied |
| Initial denial: timely filing | original remittance lines; synthetic codes | 8,004 lines; 1,312,714,210 cents denied |
| BAD_DEBT adjustments | signed cents; synthetic financial assumptions | 18,026 rows; -1,406,818,801 cents |
| CHARITY adjustments | signed cents; synthetic financial assumptions | 1,171 rows; -5,855,000 cents |
| CONTRACTUAL adjustments | signed cents; synthetic financial assumptions | 249,503 rows; -110,880,928,653 cents |
| A/R 0-30 | 2026-10-29 posted balance snapshot | 4,279,283,153 cents |
| A/R 31-60 | 2026-10-29 posted balance snapshot | 2,226,791,548 cents |

The original arrival-hour weights are applied in UTC; only ED display timestamps are converted to America/Chicago. Posting after service includes ordinary billing lag: 383,820 rows post after service, while 25,016 post at least four days later. Do not interpret the larger count as the special 5% late cohort.

Payments are a separate synthetic account-level process, not inferred from final adjudication. An unresolved denied claim can therefore coexist with account cash. Claim-line remittance rounding and account-level adjustments are separate definitions; the exact account balance conservation check is the financial invariant. No claim of clinically calibrated collections behavior is made.
